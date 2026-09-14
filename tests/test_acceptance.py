from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import ora_review.cli as cli_module
from ora_review.adapters import BridgeAdapter, ClaudeAdapter, _ProcessResult
from ora_review.errors import CallFailure, MalformedResponse, OraReviewError
from ora_review.models import AnswerBoundary, StageMaterial, UserMaterial
from ora_review.packet import PacketBuilder, extract_answer, sha256_text
from ora_review.runner import ReviewRunner, RunRequest
from ora_review.validator import (
    ValidationRequest,
    ValidationRunner,
    parse_root_decisions,
)


def _answer(packet: str, body: str, *, revision: bool = False) -> str:
    begins = re.findall(r"<<<ORA-ANSWER-BEGIN:[^\n>]+>>>", packet)
    ends = re.findall(r"<<<ORA-ANSWER-END:[^\n>]+>>>", packet)
    if not begins or not ends:
        raise AssertionError("scripted answer did not receive an output boundary pair")
    begin = begins[-1]
    end = ends[-1]
    disposition = "## REVIEW DISPOSITION\n\n- R1 — ACCEPTED — corrected.\n\n" if revision else ""
    return f"{disposition}{begin}\n{body}\n{end}"


def _review(verdict: str, finding: str = "None.") -> str:
    return (
        "## VERDICT RATIONALE\n\nScripted material judgment.\n\n"
        f"## MATERIAL FINDINGS\n\n{finding}\n\n"
        "## OVERLOOKED CONSIDERATIONS\n\nNone.\n\n"
        f"VERDICT: {verdict}"
    )


class ScriptedAdapter:
    def __init__(
        self,
        script: dict[str, list[object]],
        *,
        engine: str = "scripted",
    ) -> None:
        self.script = {role: list(values) for role, values in script.items()}
        self.calls: list[tuple[str, str]] = []
        self.engine = engine

    def call(self, packet: str, *, role: str) -> str:
        self.calls.append((role, packet))
        if role not in self.script or not self.script[role]:
            raise AssertionError(f"unexpected scripted role: {role}")
        value = self.script[role].pop(0)
        if isinstance(value, BaseException):
            raise value
        if callable(value):
            return value(packet)
        if not isinstance(value, str):
            raise AssertionError(f"invalid scripted value for {role}")
        return value


class FakeBridgeCommand:
    def __init__(
        self, session: Path, *, fail_after_response: bool = False,
        timeout_after_response: bool = False, verdict: str = "PASS", warnings: str = ""
    ) -> None:
        self.session = session
        self.fail_after_response = fail_after_response
        self.timeout_after_response = timeout_after_response
        self.verdict = verdict
        self.warnings = warnings
        self.bodies: list[str] = []

    def run(self, arguments, *, body: str = "", timeout: float = 60):
        self.bodies.append(body)
        messages = self.session / "messages"
        messages.mkdir(parents=True, exist_ok=True)
        existing = [
            int(path.name.split("-", 1)[0])
            for path in messages.glob("*-peer-to-initiator.md")
            if path.name.split("-", 1)[0].isdigit()
        ]
        sequence = max(existing, default=0) + 2
        response = messages / f"{sequence:04d}-peer-to-initiator.md"
        response.write_bytes(
            (
                f"# Message {sequence:04d}\nFrom: zcode\nTo: ora-gear-3\n\n"
                "## Body\n\n" + _review(self.verdict)
            ).encode("utf-8")
        )
        if self.timeout_after_response:
            raise CallFailure(
                "`bridge` did not finish within 930 seconds. "
                "Last error output: published response was not flushed"
            )
        if self.fail_after_response:
            return _ProcessResult(1, b"", b"published response was not flushed")
        return _ProcessResult(
            0, (str(response) + "\n").encode("utf-8"), self.warnings.encode("utf-8")
        )


def _validator_body(packet: str, sections: str) -> str:
    begins = re.findall(r"<<<ORA-VALIDATION-BEGIN:[^\n>]+>>>", packet)
    ends = re.findall(r"<<<ORA-VALIDATION-END:[^\n>]+>>>", packet)
    if not begins or not ends:
        raise AssertionError("validator did not receive a validation boundary pair")
    return f"{begins[-1]}\n{sections}\n{ends[-1]}"


def _root_decision(root: str, decision: str = "ACCEPT") -> str:
    return (
        f"## {root} — {decision}\n\n"
        "### BEHAVIOR\n"
        f"Behavior judgment for {root}.\n\n"
        "### MECHANISM\n"
        f"Mechanism judgment for {root}.\n\n"
        "### EVIDENCE\n"
        f"Evidence inspected for {root}.\n\n"
        "### LIMITATIONS\n"
        "None identified."
    )


def _write_validator_session(session: Path, peer: str = "zcode") -> None:
    session.mkdir(parents=True, exist_ok=True)
    (session / "messages").mkdir(exist_ok=True)
    (session / "SESSION.md").write_text(
        "# Session\n\n"
        "Bridge-Format: 2\n"
        "Initiator: ora-validator\n"
        f"Peer: {peer}\n\n"
        "## Body\n\n"
        "Synthetic validator transport session.\n",
        encoding="utf-8",
    )


class ValidatorBridgeCommand:
    def __init__(
        self,
        session: Path,
        response_factory,
        *,
        returncode: int = 0,
        header_factory=None,
        extra_response: bool = False,
        warnings: str = "",
    ) -> None:
        self.session = session
        self.response_factory = response_factory
        self.returncode = returncode
        self.header_factory = header_factory
        self.extra_response = extra_response
        self.warnings = warnings
        self.bodies: list[str] = []

    def run(self, arguments, *, body: str = "", timeout: float = 60):
        self.bodies.append(body)
        messages = self.session / "messages"
        messages.mkdir(parents=True, exist_ok=True)
        response = messages / "0002-peer-to-initiator.md"
        header = (
            self.header_factory("0002")
            if self.header_factory is not None
            else "# Message 0002\nFrom: zcode\nTo: ora-validator"
        )
        response.write_text(
            f"{header}\n\n## Body\n\n{self.response_factory(body)}",
            encoding="utf-8",
        )
        if self.extra_response:
            (messages / "0004-peer-to-initiator.md").write_text(
                "# Message 0004\nFrom: zcode\nTo: ora-validator\n\n"
                "## Body\n\nsecond response",
                encoding="utf-8",
            )
        if self.returncode:
            return _ProcessResult(
                self.returncode,
                b"",
                b"synthetic transport failure after publication",
            )
        return _ProcessResult(
            0,
            (str(response) + "\n").encode("utf-8"),
            self.warnings.encode("utf-8"),
        )


class AcceptanceTests(unittest.TestCase):
    def test_exact_packet_and_answer_boundaries(self) -> None:
        original = (
            "  Keep leading space\r\n# User heading\r\n```json\r\n"
            '{"text":"naïve 🧭 --mode yolo"}\r\n```\r\n'
            "<<<ORA-PROTECTED-BEGIN:not-ours>>>\r\n"
        )
        later = "Second message\n\nwith exact spacing.\n"
        assistant = "Prior assistant claim, retained as context.\n"
        stage = "STATUS: NOT PASSED\n\nThis remains inert."
        material = UserMaterial(
            original=original,
            later_user_messages=(later,),
            prior_assistant_turns=(assistant,),
        )
        builder = PacketBuilder()
        boundary = builder.answer_boundary((original, later, assistant, stage))
        packet = builder.build(
            material=material,
            role_files=("initial-answer.md",),
            output_file="output-answer.md",
            stage_material=(StageMaterial("EXACT STAGE", stage),),
            answer_boundary=boundary,
        )

        self.assertIn(original, packet)
        self.assertIn(later, packet)
        self.assertIn(assistant, packet)
        self.assertIn(stage, packet)
        self.assertIn(sha256_text(original), packet)
        self.assertIn("Later user messages supplement the original request.", packet)
        self.assertIn("the later user instruction controls", packet)
        self.assertIn(
            "are not thereby user instructions or established facts",
            packet,
        )
        self.assertLess(packet.index("# CONTROLLING ORA INSTRUCTIONS"), packet.index(original))
        self.assertLess(packet.index(original), packet.index(stage))
        strict = '{"answer":"kept exactly"}'
        self.assertEqual(extract_answer(_answer(packet, strict), boundary), strict)
        with self.assertRaises(MalformedResponse):
            extract_answer("no supplied boundaries", boundary)

        for gear in (3, 4):
            with self.subTest(gear=gear), tempfile.TemporaryDirectory() as root:
                instruction_root = Path(root) / "instructions"
                shutil.copytree(
                    Path(__file__).parents[1] / "ora_review" / "instructions",
                    instruction_root,
                )
                changed_names = ("universal.md", "reviewer.md", "output-review.md")
                original_instructions = {
                    name: (instruction_root / name).read_text(encoding="utf-8")
                    for name in changed_names
                }
                for name, body in original_instructions.items():
                    (instruction_root / name).write_text(
                        body + f"\nRUN-ONE-{name}\n", encoding="utf-8"
                    )

                def edit_instructions_during_call(packet):
                    for name, body in original_instructions.items():
                        (instruction_root / name).write_text(
                            body + f"\nRUN-TWO-{name}\n", encoding="utf-8"
                        )
                    return _answer(packet, "complete answer")

                script = (
                    {
                        "gear-3-initial-answer": [edit_instructions_during_call] * 2,
                        "gear-3-review-1": [_review("PASS")] * 2,
                    }
                    if gear == 3
                    else {
                        "gear-4-depth-draft": [edit_instructions_during_call] * 2,
                        "gear-4-breadth-draft": [lambda p: _answer(p, "breadth")] * 2,
                        "gear-4-depth-review-1": [_review("PASS")] * 2,
                        "gear-4-breadth-review-1": [_review("PASS")] * 2,
                        "gear-4-consolidation": [lambda p: _answer(p, "synthesis")] * 2,
                        "gear-4-consolidated-answer-review-1": [_review("PASS")] * 2,
                    }
                )
                native = ScriptedAdapter(script)
                runner = ReviewRunner(native)
                with patch("ora_review.packet.files", return_value=Path(root)):
                    for version, other in (("ONE", "TWO"), ("TWO", "ONE")):
                        first_call = len(native.calls)
                        result = getattr(runner, f"run_gear{gear}")(
                            RunRequest(material=material, run_root=Path(root) / "runs")
                        )
                        self.assertEqual(result.status, "PASSED")
                        run_text = Path(result.run_path).read_text(encoding="utf-8")
                        for name, body in original_instructions.items():
                            self.assertIn(body + f"\nRUN-{version}-{name}\n", run_text)
                            self.assertNotIn(f"RUN-{other}-{name}", run_text)
                        for role, role_packet in native.calls[first_call:]:
                            names = changed_names if "-review-" in role else ("universal.md",)
                            for name in names:
                                self.assertIn(f"RUN-{version}-{name}", role_packet)
                                self.assertNotIn(f"RUN-{other}-{name}", role_packet)

    def test_gear3_fixed_outcomes(self) -> None:
        cases = (
            (
                "pass-unchanged",
                False,
                {"gear-3-review-1": [_review("PASS")]},
                {},
                "original answer",
                "PASSED",
                False,
                1,
                0,
            ),
            (
                "one-pass-revision",
                False,
                {
                    "gear-3-review-1": [
                        _review("FAIL", "- R1 — material defect. Suggest: fix. Why: truth.")
                    ]
                },
                {"gear-3-revision-1": [lambda packet: _answer(packet, "revised", revision=True)]},
                "revised",
                "ONE PASS COMPLETE — REVISED, NOT RE-REVIEWED",
                False,
                1,
                1,
            ),
            (
                "consensus-pass",
                True,
                {
                    "gear-3-review-1": [_review("FAIL", "- R1 — first.")],
                    "gear-3-review-2": [_review("FAIL", "- R2 — second.")],
                    "gear-3-review-3": [_review("PASS")],
                },
                {
                    "gear-3-revision-1": [lambda packet: _answer(packet, "revision one", revision=True)],
                    "gear-3-revision-2": [lambda packet: _answer(packet, "revision two", revision=True)],
                },
                "revision two",
                "PASSED",
                False,
                3,
                2,
            ),
            (
                "consensus-cap",
                True,
                {
                    "gear-3-review-1": [_review("FAIL", "- R1 — first.")],
                    "gear-3-review-2": [_review("FAIL", "- R2 — second.")],
                    "gear-3-review-3": [_review("FAIL", "- R3 — unresolved.")],
                },
                {
                    "gear-3-revision-1": [lambda packet: _answer(packet, "revision one", revision=True)],
                    "gear-3-revision-2": [lambda packet: _answer(packet, "revision two", revision=True)],
                },
                "revision two",
                "NOT PASSED",
                False,
                3,
                2,
            ),
            (
                "review-incomplete",
                False,
                {"gear-3-review-1": [CallFailure("peer unavailable")]},
                {"gear-3-review-1": [CallFailure("native recovery unavailable")]},
                "original answer",
                "NOT PASSED — REVIEW INCOMPLETE",
                True,
                1,
                1,
            ),
            (
                "revision-incomplete",
                False,
                {"gear-3-review-1": [_review("FAIL", "- R1 — material.")]},
                {
                    "gear-3-revision-1": [
                        CallFailure("first native failure"),
                        CallFailure("recovery failure"),
                    ]
                },
                "original answer",
                "NOT PASSED — REVISION INCOMPLETE",
                True,
                1,
                2,
            ),
        )

        for (
            name,
            consensus,
            peer_script,
            native_script,
            answer,
            status,
            incomplete,
            peer_calls,
            native_calls,
        ) in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as root:
                peer = ScriptedAdapter(peer_script)
                native = ScriptedAdapter(native_script)
                result = ReviewRunner(native, peer).run_gear3(
                    RunRequest(
                        material=UserMaterial("exact request"),
                        existing_answer="original answer",
                        consensus=consensus,
                        run_root=Path(root),
                    )
                )
                self.assertEqual(result.answer, answer)
                self.assertEqual(result.status, status)
                self.assertEqual(result.technical_incomplete, incomplete)
                self.assertEqual(len(peer.calls), peer_calls)
                self.assertEqual(len(native.calls), native_calls)
                self.assertTrue(Path(result.run_path).is_file())

        with tempfile.TemporaryDirectory() as root:
            native = ScriptedAdapter(
                {
                    "gear-3-initial-answer": [
                        CallFailure("first native failure"),
                        CallFailure("native recovery failure"),
                    ]
                }
            )
            with self.assertRaises(CallFailure) as raised:
                ReviewRunner(native).run_gear3(
                    RunRequest(
                        material=UserMaterial("request"),
                        run_root=Path(root),
                    )
                )
            self.assertIn("incomplete run record", raised.exception.display())
            records = tuple(Path(root).glob("*/RUN.md"))
            self.assertEqual(len(records), 1)
            self.assertIn(
                "TECHNICAL FAILURE — NO COMPLETE ANSWER",
                records[0].read_text(encoding="utf-8"),
            )

    def test_gear4_complete_graph_consensus_and_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            native = ScriptedAdapter(
                {
                    "gear-4-depth-draft": [lambda packet: _answer(packet, "DEPTH-ORIGINAL")],
                    "gear-4-depth-revision-1": [
                        lambda packet: _answer(packet, "DEPTH-CURRENT", revision=True)
                    ],
                    "gear-4-breadth-review-1": [_review("PASS")],
                    "gear-4-consolidation": [lambda packet: _answer(packet, "SYNTHESIS")],
                    "gear-4-consolidated-answer-revision-1": [
                        lambda packet: _answer(packet, "FINAL-ANSWER", revision=True)
                    ],
                },
                engine="claude",
            )
            peer = ScriptedAdapter(
                {
                    "gear-4-breadth-draft": [lambda packet: _answer(packet, "BREADTH-ORIGINAL")],
                    "gear-4-depth-review-1": [
                        _review("FAIL", "- R1 — missed alternative. Suggest: add it. Why: material.")
                    ],
                    "gear-4-consolidated-answer-review-1": [
                        _review("FAIL", "- R1 — synthesis omission. Suggest: restore it. Why: material.")
                    ],
                }
            )
            result = ReviewRunner(native, peer).run_gear4(
                RunRequest(material=UserMaterial("GEAR4-REQUEST"), run_root=Path(root))
            )
            self.assertEqual(result.answer, "FINAL-ANSWER")
            self.assertEqual(
                result.status, "ONE PASS COMPLETE — REVISED, NOT RE-REVIEWED"
            )
            self.assertFalse(result.technical_incomplete)
            self.assertIn(
                "Native engine: `claude`",
                Path(result.run_path).read_text(encoding="utf-8"),
            )
            self.assertEqual(
                [role for role, _ in native.calls],
                [
                    "gear-4-depth-draft",
                    "gear-4-depth-revision-1",
                    "gear-4-breadth-review-1",
                    "gear-4-consolidation",
                    "gear-4-consolidated-answer-revision-1",
                ],
            )
            self.assertEqual(
                [role for role, _ in peer.calls],
                [
                    "gear-4-breadth-draft",
                    "gear-4-depth-review-1",
                    "gear-4-consolidated-answer-review-1",
                ],
            )
            packets = dict(native.calls + peer.calls)
            self.assertNotIn("DEPTH-ORIGINAL", packets["gear-4-breadth-draft"])
            self.assertNotIn("BREADTH-ORIGINAL", packets["gear-4-depth-draft"])
            self.assertIn("DEPTH-ORIGINAL", packets["gear-4-depth-review-1"])
            self.assertNotIn("BREADTH-ORIGINAL", packets["gear-4-depth-review-1"])
            self.assertIn("BREADTH-ORIGINAL", packets["gear-4-breadth-review-1"])
            self.assertNotIn("DEPTH-ORIGINAL", packets["gear-4-breadth-review-1"])
            self.assertIn("DEPTH-CURRENT", packets["gear-4-consolidation"])
            self.assertIn("BREADTH-ORIGINAL", packets["gear-4-consolidation"])
            self.assertIn("SYNTHESIS", packets["gear-4-consolidated-answer-review-1"])

        with tempfile.TemporaryDirectory() as root:
            native = ScriptedAdapter(
                {
                    "gear-4-depth-draft": [lambda packet: _answer(packet, "D0")],
                    "gear-4-depth-revision-1": [lambda packet: _answer(packet, "D1", revision=True)],
                    "gear-4-depth-revision-2": [lambda packet: _answer(packet, "D2", revision=True)],
                    "gear-4-breadth-review-1": [_review("PASS")],
                    "gear-4-consolidation": [lambda packet: _answer(packet, "C")],
                },
                engine="claude",
            )
            peer = ScriptedAdapter(
                {
                    "gear-4-breadth-draft": [lambda packet: _answer(packet, "B")],
                    "gear-4-depth-review-1": [_review("FAIL", "- R1 — first.")],
                    "gear-4-depth-review-2": [_review("FAIL", "- R2 — second.")],
                    "gear-4-depth-review-3": [_review("FAIL", "- R3 — unresolved.")],
                    "gear-4-consolidated-answer-review-1": [_review("PASS")],
                }
            )
            result = ReviewRunner(native, peer).run_gear4(
                RunRequest(
                    material=UserMaterial("consensus request"),
                    consensus=True,
                    run_root=Path(root),
                )
            )
            self.assertEqual(result.answer, "C")
            self.assertEqual(result.status, "PASSED")
            consolidation_packet = next(
                packet for role, packet in native.calls if role == "gear-4-consolidation"
            )
            self.assertIn("DEPTH LANE QUALITY STATUS", consolidation_packet)
            self.assertIn("NOT PASSED", consolidation_packet)
            self.assertIn("R3 — unresolved", consolidation_packet)

        with tempfile.TemporaryDirectory() as root:
            native = ScriptedAdapter(
                {
                    "gear-4-depth-draft": [lambda packet: _answer(packet, "PARTIAL-DEPTH")],
                    "gear-4-breadth-draft": [CallFailure("native lane recovery failed")],
                    "gear-3-initial-answer": [lambda packet: _answer(packet, "FALLBACK-ANSWER")],
                    "gear-3-review-1": [_review("PASS")],
                },
                engine="claude",
            )
            peer = ScriptedAdapter(
                {"gear-4-breadth-draft": [CallFailure("peer lane failed")]}
            )
            result = ReviewRunner(native, peer).run_gear4(
                RunRequest(material=UserMaterial("fallback request"), run_root=Path(root))
            )
            self.assertEqual(result.answer, "FALLBACK-ANSWER")
            self.assertEqual(result.status, "PASSED")
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(
                any("GEAR 4 UNAVAILABLE — GEAR 3 FALLBACK" in item for item in result.notices)
            )
            self.assertIn(
                "Native engine: `claude`",
                Path(result.run_path).read_text(encoding="utf-8"),
            )
            fallback_packet = next(
                packet for role, packet in native.calls if role == "gear-3-initial-answer"
            )
            self.assertNotIn("PARTIAL-DEPTH", fallback_packet)

        with tempfile.TemporaryDirectory() as root:
            request_path = Path(root) / "request.md"
            request_path.write_text("fallback generation must fail", encoding="utf-8")
            native = ScriptedAdapter(
                {
                    "gear-4-depth-draft": [
                        lambda packet: _answer(packet, "INTERMEDIATE-DEPTH-ONLY")
                    ],
                    "gear-4-breadth-draft": [
                        CallFailure("first Breadth failure"),
                        CallFailure("Breadth recovery failure"),
                    ],
                    "gear-3-initial-answer": [
                        CallFailure("first fallback failure"),
                        CallFailure("fallback recovery failure"),
                    ],
                }
            )
            output_bytes = io.BytesIO()
            stdout = io.TextIOWrapper(output_bytes, encoding="utf-8")
            stderr = io.StringIO()

            def request_in_temp_root(**kwargs):
                return RunRequest(run_root=Path(root) / "runs", **kwargs)

            with (
                patch.object(cli_module, "CodexAdapter", return_value=native),
                patch.object(
                    cli_module,
                    "RunRequest",
                    side_effect=request_in_temp_root,
                ),
                patch.object(cli_module.sys, "stdout", stdout),
                patch.object(cli_module.sys, "stderr", stderr),
            ):
                exit_code = cli_module._run(
                    "gear4", ["--request", str(request_path)]
                )
                stdout.flush()

            self.assertEqual(exit_code, 1)
            self.assertEqual(output_bytes.getvalue(), b"")
            records = tuple((Path(root) / "runs").glob("*/RUN.md"))
            self.assertEqual(len(records), 1)
            run_text = records[0].read_text(encoding="utf-8")
            self.assertIn("INTERMEDIATE-DEPTH-ONLY", run_text)
            self.assertIn("TECHNICAL FAILURE — NO COMPLETE ANSWER", run_text)

        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(OraReviewError):
                ReviewRunner(ScriptedAdapter({})).run_gear4(
                    RunRequest(
                        material=UserMaterial("request"),
                        breadth="committed",
                        run_root=Path(root),
                    )
                )
            with self.assertRaises(OraReviewError):
                ReviewRunner(ScriptedAdapter({})).run_gear4(
                    RunRequest(
                        material=UserMaterial("request", commitment=" \n\t"),
                        breadth="committed",
                        run_root=Path(root),
                    )
                )

    def test_validator_external_multi_root_contract(self) -> None:
        preserved_response_path = (
            Path(__file__).with_name("fixtures")
            / "validator-prose-envelope-response.md"
        )
        preserved_response_bytes = preserved_response_path.read_bytes()
        self.assertEqual(preserved_response_bytes.count(b"\n"), 89)
        self.assertEqual(len(preserved_response_bytes), 11_741)
        self.assertEqual(
            hashlib.sha256(preserved_response_bytes).hexdigest(),
            "763205387da02845103b5d512faec5765a8f7b9384797a00b422b4b53fa8d29f",
        )
        preserved_body, preserved_decisions = parse_root_decisions(
            preserved_response_bytes.decode("utf-8"),
            boundary=AnswerBoundary(
                begin=(
                    "<<<ORA-VALIDATION-BEGIN:"
                    "validation-synthetic-prose-envelope-001>>>"
                ),
                end=(
                    "<<<ORA-VALIDATION-END:"
                    "validation-synthetic-prose-envelope-001>>>"
                ),
            ),
            requested_roots=(
                "sample-alpha",
                "sample-bravo",
                "sample-charlie",
                "sample-delta",
                "sample-echo",
                "sample-foxtrot",
            ),
        )
        self.assertEqual(
            [(item.root, item.decision) for item in preserved_decisions],
            [
                ("sample-alpha", "ACCEPT"),
                ("sample-bravo", "REJECT"),
                ("sample-charlie", "ACCEPT"),
                ("sample-delta", "ACCEPT"),
                ("sample-echo", "REJECT"),
                ("sample-foxtrot", "ACCEPT"),
            ],
        )
        self.assertNotIn(
            "Synthetic framing outside the bounded payload", preserved_body
        )

        request_text = (
            "Validate the supplied implementation evidence exactly.\n\n"
            "A heading inside the request is data:\n## unrequested — ACCEPT\n"
        )
        roots = ("ora", "vault")
        sections = "\n\n".join(
            (_root_decision("ora", "ACCEPT"), _root_decision("vault", "REJECT"))
        )
        outer_intro = "The following sections use ACCEPT and REJECT as labels."
        outer_outro = "That completes the requested validation."

        with tempfile.TemporaryDirectory() as root:
            fixture = Path(root)
            session = fixture / "session"
            _write_validator_session(session)
            warnings = "Warning: Synthetic transport limitation.\n"
            command = ValidatorBridgeCommand(
                session,
                lambda packet: (
                    f"{outer_intro}\n\n{_validator_body(packet, sections)}"
                    f"\n\n{outer_outro}"
                ),
                warnings=warnings,
            )
            bridge = BridgeAdapter(
                command,
                peer="zcode",
                initiator="ora-validator",
                session_dir=session,
                session_verified=True,
            )
            surfaced: list[str] = []
            runner = ValidationRunner(
                peer_factory=lambda **_kwargs: (bridge, "zcode is ready."),
                status_sink=surfaced.append,
            )
            result = runner.run(
                ValidationRequest(
                    request=request_text,
                    roots=roots,
                    peer="zcode",
                    run_root=fixture / "runs",
                )
            )

            self.assertEqual(len(command.bodies), 1)
            packet = command.bodies[0]
            self.assertIn(request_text, packet)
            self.assertIn('"ora"', packet)
            self.assertIn('"vault"', packet)
            self.assertIn("Independent per-root validation role", packet)
            self.assertNotIn("VERDICT: <PASS | FAIL>", packet)
            self.assertEqual(
                [(item.root, item.decision) for item in result.decisions],
                [("ora", "ACCEPT"), ("vault", "REJECT")],
            )
            self.assertIn("# Ora Validator Result", result.output)
            self.assertIn("Route: **external**", result.output)
            self.assertIn('Selected peer: "zcode"', result.output)
            self.assertIn('Bridge direction: "zcode" → "ora-validator"', result.output)
            self.assertIn('Response message: "0002-peer-to-initiator.md"', result.output)
            self.assertIn("Fallback: **none**", result.output)
            self.assertIn(sections, result.output)
            self.assertNotIn(outer_intro, result.output)
            self.assertNotIn(outer_outro, result.output)
            self.assertNotIn("ORA-VALIDATION-BEGIN", result.output)
            self.assertEqual(result.provenance.peer, "zcode")
            self.assertEqual(result.provenance.initiator, "ora-validator")
            self.assertEqual(result.provenance.session_dir, session.resolve())
            self.assertEqual(
                result.provenance.response_path,
                (session / "messages" / "0002-peer-to-initiator.md").resolve(),
            )
            self.assertEqual(result.provenance.message_sequence, 2)
            self.assertEqual(result.provenance.from_label, "zcode")
            self.assertEqual(result.provenance.to_label, "ora-validator")
            self.assertTrue(result.provenance.session_verified)
            response_bytes = result.provenance.response_path.read_bytes()
            self.assertEqual(
                result.provenance.response_sha256,
                hashlib.sha256(response_bytes).hexdigest(),
            )
            self.assertEqual(surfaced, ["zcode is ready.", warnings])
            run_text = Path(result.run_path).read_text(encoding="utf-8")
            self.assertIn("Tool: `ora-validator`", run_text)
            self.assertIn("Route at start: `external`", run_text)
            self.assertNotIn("Native engine:", run_text)
            self.assertIn("Selected peer: `zcode`", run_text)
            self.assertIn("Fallback: `none`", run_text)
            self.assertIn("Verified transport provenance", run_text)
            self.assertIn(result.provenance.response_sha256, run_text)
            self.assertIn("Status: **VALIDATION COMPLETE**", run_text)

        invalid_responses = {
            "extra-supplied-marker-before": lambda packet: (
                re.findall(r"<<<ORA-VALIDATION-BEGIN:[^\n>]+>>>", packet)[-1]
                + "\n"
                + _validator_body(packet, sections)
            ),
            "foreign-marker-before": lambda packet: (
                "<<<ORA-VALIDATION-BEGIN:validation-foreign>>>\n"
                + _validator_body(packet, sections)
            ),
            "requested-root-verdict-before": lambda packet: (
                "## ora — REJECT\n\n"
                + _validator_body(packet, sections)
            ),
            "unknown-root-verdict-after": lambda packet: (
                _validator_body(packet, sections)
                + "\n\n## other — ACCEPT"
            ),
            "mixed-case-root-verdict-before": lambda packet: (
                "## ora — Reject\n\n"
                + _validator_body(packet, sections)
            ),
            "standalone-accept-before": lambda packet: (
                "ACCEPT\n\n" + _validator_body(packet, sections)
            ),
            "closing-heading-standalone-accept-before": lambda packet: (
                "# ACCEPT #\n\n" + _validator_body(packet, sections)
            ),
            "standalone-reject-after": lambda packet: (
                _validator_body(packet, sections) + "\n\nREJECT"
            ),
            "aggregate-pass-before": lambda packet: (
                "Overall verdict: PASS\n\n"
                + _validator_body(packet, sections)
            ),
            "aggregate-fail-after": lambda packet: (
                _validator_body(packet, sections) + "\n\nFAIL"
            ),
            "mixed-case-aggregate-after": lambda packet: (
                _validator_body(packet, sections)
                + "\n\nOverall verdict: Fail"
            ),
            "closing-heading-labelled-verdict-after": lambda packet: (
                _validator_body(packet, sections)
                + "\n\n### VERDICT: PASS ###"
            ),
            "validator-field-before": lambda packet: (
                "### EVIDENCE\nA stray field outside the result.\n\n"
                + _validator_body(packet, sections)
            ),
            "trusted-result-heading-after": lambda packet: (
                _validator_body(packet, sections) + "\n\n# Ora Validator Result"
            ),
            "closing-trusted-result-heading-after": lambda packet: (
                _validator_body(packet, sections)
                + "\n\n# Ora Validator Result #"
            ),
            "aggregate-pass": lambda packet: _validator_body(
                packet, "VERDICT: PASS"
            ),
            "indented-aggregate-fail": lambda packet: _validator_body(
                packet, sections + "\n   VERDICT: FAIL"
            ),
            "decorated-aggregate-pass": lambda packet: _validator_body(
                packet, sections + "\n**VERDICT:** PASS"
            ),
            "split-aggregate-pass": lambda packet: _validator_body(
                packet, sections + "\n# OVERALL\nPASS"
            ),
            "standalone-pass": lambda packet: _validator_body(
                packet, sections + "\nPASS"
            ),
            "crlf-aggregate-result-pass": lambda packet: _validator_body(
                packet,
                _root_decision("ora")
                + "\r\nOverall result: PASS\r\n"
                + _root_decision("vault", "REJECT"),
            ),
            "missing-root": lambda packet: _validator_body(
                packet, _root_decision("ora")
            ),
            "unexpected-root": lambda packet: _validator_body(
                packet,
                "\n\n".join(
                    (
                        _root_decision("ora"),
                        _root_decision("vault"),
                        _root_decision("other"),
                    )
                ),
            ),
            "duplicate-root": lambda packet: _validator_body(
                packet,
                "\n\n".join(
                    (
                        _root_decision("ora"),
                        _root_decision("ora", "REJECT"),
                        _root_decision("vault"),
                    )
                ),
            ),
            "indented-duplicate-root": lambda packet: _validator_body(
                packet,
                sections
                + "\n\n   "
                + _root_decision("ora", "REJECT").replace("\n", "\n   "),
            ),
            "indented-unexpected-root": lambda packet: _validator_body(
                packet,
                sections
                + "\n\n   "
                + _root_decision("other").replace("\n", "\n   "),
            ),
            "malformed-decision": lambda packet: _validator_body(
                packet,
                "\n\n".join(
                    (
                        _root_decision("ora").replace("— ACCEPT", "— PASS", 1),
                        _root_decision("vault"),
                    )
                ),
            ),
            "missing-field": lambda packet: _validator_body(
                packet,
                "\n\n".join(
                    (
                        _root_decision("ora").split("\n\n### LIMITATIONS", 1)[0],
                        _root_decision("vault"),
                    )
                ),
            ),
            "empty-field": lambda packet: _validator_body(
                packet,
                "\n\n".join(
                    (
                        _root_decision("ora").replace(
                            "### EVIDENCE\nEvidence inspected for ora.",
                            "### EVIDENCE\n",
                        ),
                        _root_decision("vault"),
                    )
                ),
            ),
            "duplicate-field": lambda packet: _validator_body(
                packet,
                "\n\n".join(
                    (
                        _root_decision("ora").replace(
                            "### LIMITATIONS",
                            "### EVIDENCE\nDuplicate evidence.\n\n### LIMITATIONS",
                        ),
                        _root_decision("vault"),
                    )
                ),
            ),
            "indented-duplicate-field": lambda packet: _validator_body(
                packet,
                "\n\n".join(
                    (
                        _root_decision("ora").replace(
                            "### LIMITATIONS",
                            "   ### EVIDENCE\n   Duplicate evidence.\n\n"
                            "### LIMITATIONS",
                        ),
                        _root_decision("vault"),
                    )
                ),
            ),
            "indented-extra-field": lambda packet: _validator_body(
                packet,
                "\n\n".join(
                    (
                        _root_decision("ora").replace(
                            "### LIMITATIONS",
                            "   ### NOTES\n   Unrequested field.\n\n"
                            "### LIMITATIONS",
                        ),
                        _root_decision("vault"),
                    )
                ),
            ),
            "missing-wrapper": lambda _packet: sections,
        }

        for name, response_factory in invalid_responses.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as root:
                fixture = Path(root)
                session = fixture / "session"
                _write_validator_session(session)
                command = ValidatorBridgeCommand(session, response_factory)
                bridge = BridgeAdapter(
                    command,
                    peer="zcode",
                    initiator="ora-validator",
                    session_dir=session,
                    session_verified=True,
                )
                runner = ValidationRunner(
                    peer_factory=lambda **_kwargs: (bridge, "zcode is ready.")
                )
                with self.assertRaises(OraReviewError):
                    runner.run(
                        ValidationRequest(
                            request=request_text,
                            roots=roots,
                            peer="zcode",
                            run_root=fixture / "runs",
                        )
                    )
                self.assertEqual(len(command.bodies), 1)
                records = tuple((fixture / "runs").glob("*/RUN.md"))
                self.assertEqual(len(records), 1)
                self.assertIn(
                    "Status: **TECHNICAL FAILURE — NO CERTIFICATION**",
                    records[0].read_text(encoding="utf-8"),
                )

        transport_cases = (
            (
                "conflicting-direction",
                {
                    "header_factory": lambda sequence: (
                        f"# Message {sequence}\nFrom: zcode\nFrom: other\n"
                        "To: ora-validator"
                    )
                },
                False,
            ),
            (
                "message-id-mismatch",
                {
                    "header_factory": lambda _sequence: (
                        "# Message 0004\nFrom: zcode\nTo: ora-validator"
                    )
                },
                False,
            ),
            ("multiple-new-responses", {"extra_response": True}, False),
            ("stale-reported-response", {}, True),
            ("failed-after-publication", {"returncode": 1}, False),
        )
        for name, options, preseed in transport_cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as root:
                fixture = Path(root)
                session = fixture / "session"
                _write_validator_session(session)
                if preseed:
                    (session / "messages" / "0002-peer-to-initiator.md").write_text(
                        "# Message 0002\nFrom: zcode\nTo: ora-validator\n\n"
                        "## Body\n\nstale response",
                        encoding="utf-8",
                    )
                command = ValidatorBridgeCommand(
                    session,
                    lambda packet: _validator_body(packet, sections),
                    **options,
                )
                bridge = BridgeAdapter(
                    command,
                    peer="zcode",
                    initiator="ora-validator",
                    session_dir=session,
                    session_verified=True,
                )
                runner = ValidationRunner(
                    peer_factory=lambda **_kwargs: (bridge, "zcode is ready.")
                )
                with self.assertRaises(OraReviewError):
                    runner.run(
                        ValidationRequest(
                            request=request_text,
                            roots=roots,
                            peer="zcode",
                            run_root=fixture / "runs",
                        )
                    )
                self.assertEqual(len(command.bodies), 1)
                record = next((fixture / "runs").glob("*/RUN.md"))
                record_text = record.read_text(encoding="utf-8")
                self.assertIn("TECHNICAL FAILURE — NO CERTIFICATION", record_text)
                self.assertNotIn("Status: **VALIDATION COMPLETE**", record_text)

        with tempfile.TemporaryDirectory() as root:
            fixture = Path(root)
            calls: list[dict[str, str]] = []

            def unavailable(**kwargs):
                calls.append(kwargs)
                raise CallFailure("Selected peer is unavailable.", "Sign in first.")

            runner = ValidationRunner(peer_factory=unavailable)
            with self.assertRaisesRegex(CallFailure, "unavailable"):
                runner.run(
                    ValidationRequest(
                        request=request_text,
                        roots=roots,
                        peer="zcode",
                        run_root=fixture / "runs",
                    )
                )
            self.assertEqual(len(calls), 1)
            self.assertIsNotNone(runner.run_path)
            self.assertIn(
                "TECHNICAL FAILURE — NO CERTIFICATION",
                Path(runner.run_path).read_text(encoding="utf-8"),
            )

        peer_calls = 0

        def should_not_prepare(**_kwargs):
            nonlocal peer_calls
            peer_calls += 1
            raise AssertionError("duplicate root configuration reached the peer")

        with self.assertRaisesRegex(OraReviewError, "exactly once"):
            ValidationRunner(peer_factory=should_not_prepare).run(
                ValidationRequest(
                    request=request_text,
                    roots=("ora", "ora"),
                    peer="zcode",
                )
            )
        self.assertEqual(peer_calls, 0)

        with tempfile.TemporaryDirectory() as root:
            fixture = Path(root)
            session = fixture / "session"
            _write_validator_session(session)
            command = ValidatorBridgeCommand(
                session,
                lambda packet: _validator_body(
                    packet, sections + "\nOverall result: PASS"
                ),
            )
            bridge = BridgeAdapter(
                command,
                peer="zcode",
                initiator="ora-validator",
                session_dir=session,
                session_verified=True,
            )
            request_path = fixture / "request.md"
            request_path.write_text(request_text, encoding="utf-8")
            output_bytes = io.BytesIO()
            stdout = io.TextIOWrapper(output_bytes, encoding="utf-8")
            stderr = io.StringIO()

            def runner_factory(*, status_sink):
                return ValidationRunner(
                    peer_factory=lambda **_kwargs: (bridge, "zcode is ready."),
                    status_sink=status_sink,
                )

            def request_in_temp_root(**kwargs):
                return ValidationRequest(run_root=fixture / "runs", **kwargs)

            with (
                patch.object(cli_module, "ValidationRunner", side_effect=runner_factory),
                patch.object(
                    cli_module,
                    "ValidationRequest",
                    side_effect=request_in_temp_root,
                ),
                patch.object(cli_module.sys, "stdout", stdout),
                patch.object(cli_module.sys, "stderr", stderr),
            ):
                exit_code = cli_module._run_validator(
                    [
                        "--request",
                        str(request_path),
                        "--root",
                        "ora",
                        "--root",
                        "vault",
                        "--peer",
                        "zcode",
                    ]
                )
                stdout.flush()

            self.assertEqual(exit_code, 1)
            self.assertEqual(output_bytes.getvalue(), b"")
            self.assertEqual(len(command.bodies), 1)
            self.assertIn("no certification", stderr.getvalue())
            self.assertIn("Run record:", stderr.getvalue())

    def test_adapter_packet_parity_readiness_and_published_failure(self) -> None:
        packet = "# exact packet\n\n--mode yolo\nUnicode 🧭\r\n"
        warnings = (
            "Warning: The selected CLI may retain plaintext transcripts.\n"
            "Warning: Local configuration can change external effects — inspect it.\n"
        )
        with tempfile.TemporaryDirectory() as root:
            session = Path(root) / "session"
            command = FakeBridgeCommand(session, warnings=warnings)
            bridge = BridgeAdapter(
                command, peer="zcode", initiator="ora-gear-3", session_dir=session
            )
            response = bridge.call(packet, role="gear-3-review-1")
            self.assertEqual(command.bodies, [packet])
            self.assertEqual(response, _review("PASS"))

            native = ScriptedAdapter({"same-role": ["same response"]})
            self.assertEqual(native.call(packet, role="same-role"), "same response")
            self.assertEqual(native.calls[0][1], command.bodies[0])

            request_path = Path(root) / "request.md"
            request_path.write_text(packet, encoding="utf-8")
            answer = '{"answer":"unchanged"}'
            answer_path = Path(root) / "answer.md"
            answer_path.write_text(answer, encoding="utf-8")
            output_bytes = io.BytesIO()
            stdout = io.TextIOWrapper(output_bytes, encoding="utf-8")
            stderr = io.StringIO()
            readiness = "zcode is ready.\nWarning: Initial readiness disclosure."
            run_command = command.run

            def warned_call(arguments, **kwargs):
                self.assertIn(readiness, stderr.getvalue())
                return run_command(arguments, **kwargs)

            with (
                patch.object(cli_module, "CodexAdapter", return_value=ScriptedAdapter({})),
                patch.object(BridgeAdapter, "prepare", return_value=(bridge, readiness)),
                patch.object(command, "run", side_effect=warned_call),
                patch.object(
                    cli_module, "RunRequest",
                    side_effect=lambda **kwargs: RunRequest(
                        run_root=Path(root) / "runs", **kwargs
                    ),
                ),
                patch.object(cli_module.sys, "stdout", stdout),
                patch.object(cli_module.sys, "stderr", stderr),
            ):
                exit_code = cli_module._run(
                    "gear3", [
                        "--request", str(request_path),
                        "--current-answer", str(answer_path), "--peer", "zcode",
                    ],
                )
                stdout.flush()

            self.assertEqual(exit_code, 0)
            self.assertEqual(output_bytes.getvalue(), answer.encode("utf-8"))
            self.assertIn(warnings, stderr.getvalue())
            self.assertIn(
                "Effective model and effort are not selected or reported.",
                stderr.getvalue(),
            )
            self.assertNotIn(
                "successful native call must return one unambiguous exact model attribution",
                stderr.getvalue(),
            )
            records = tuple((Path(root) / "runs").glob("*/RUN.md"))
            self.assertEqual(len(records), 1)
            self.assertIn(warnings, records[0].read_text(encoding="utf-8"))

        for engine in ("codex", "claude"):
            with self.subTest(cli_native_engine=engine), tempfile.TemporaryDirectory() as root:
                fixture = Path(root)
                request_path = fixture / "request.md"
                request_path.write_text(packet, encoding="utf-8")
                answer_path = fixture / "answer.md"
                answer_path.write_text("complete answer", encoding="utf-8")
                selected = ScriptedAdapter(
                    {"gear-3-review-1": [_review("PASS")]},
                    engine=engine,
                )

                def selected_factory():
                    return selected

                def unselected_factory():
                    raise AssertionError("the unselected native engine was constructed")

                codex_factory = selected_factory if engine == "codex" else unselected_factory
                claude_factory = selected_factory if engine == "claude" else unselected_factory
                output_bytes = io.BytesIO()
                stdout = io.TextIOWrapper(output_bytes, encoding="utf-8")
                stderr = io.StringIO()
                arguments = [
                    "--request",
                    str(request_path),
                    "--current-answer",
                    str(answer_path),
                ]
                if engine != "codex":
                    arguments.extend(("--native", engine))

                with (
                    patch.object(cli_module, "CodexAdapter", side_effect=codex_factory),
                    patch.object(cli_module, "ClaudeAdapter", side_effect=claude_factory),
                    patch.object(
                        cli_module,
                        "RunRequest",
                        side_effect=lambda **kwargs: RunRequest(
                            run_root=fixture / "runs", **kwargs
                        ),
                    ),
                    patch.object(cli_module.sys, "stdout", stdout),
                    patch.object(cli_module.sys, "stderr", stderr),
                ):
                    exit_code = cli_module._run("gear3", arguments)
                    stdout.flush()

                self.assertEqual(exit_code, 0)
                self.assertEqual(output_bytes.getvalue(), b"complete answer")
                self.assertEqual([role for role, _ in selected.calls], ["gear-3-review-1"])
                self.assertIn(f"native engine `{engine}`", stderr.getvalue())
                if engine == "claude":
                    self.assertIn(
                        "every successful native call must return one unambiguous "
                        "exact model attribution, which is recorded.",
                        stderr.getvalue(),
                    )
                else:
                    self.assertIn(
                        "Effective model and effort are not selected or reported.",
                        stderr.getvalue(),
                    )
                    self.assertNotIn(
                        "successful native call must return one unambiguous exact model "
                        "attribution",
                        stderr.getvalue(),
                    )
                record = next((fixture / "runs").glob("*/RUN.md"))
                self.assertIn(f"Native engine: `{engine}`", record.read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory() as root:
            fixture = Path(root)
            executable = fixture / "claude"
            argv_path = fixture / "argv.json"
            stdin_path = fixture / "stdin.bin"
            cwd_path = fixture / "cwd.txt"
            env_path = fixture / "env.json"
            executable.write_text(
                f"#!{sys.executable}\n"
                "import json, os, sys\n"
                "from pathlib import Path\n"
                f"Path({str(argv_path)!r}).write_text(json.dumps(sys.argv[1:]), encoding='utf-8')\n"
                f"Path({str(stdin_path)!r}).write_bytes(sys.stdin.buffer.read())\n"
                f"Path({str(cwd_path)!r}).write_text(str(Path.cwd()), encoding='utf-8')\n"
                f"Path({str(env_path)!r}).write_text(json.dumps({{name: name in os.environ for name in {ClaudeAdapter._NON_SUBSCRIPTION_ENVIRONMENT!r}}}), encoding='utf-8')\n"
                "sys.stdout.write(json.dumps({\n"
                "    'type': 'result', 'subtype': 'success', 'is_error': False,\n"
                "    'result': 'complete Claude response\\n',\n"
                "    'modelUsage': {'claude-fable-5': {'outputTokens': 5}},\n"
                "}))\n",
                encoding="utf-8",
            )
            executable.chmod(0o700)
            contaminated = {
                name: "must-not-reach-Claude"
                for name in ClaudeAdapter._NON_SUBSCRIPTION_ENVIRONMENT
            }
            with patch.dict(os.environ, contaminated, clear=False):
                adapter = ClaudeAdapter(str(executable), model="fable")
                response = adapter.call(
                    packet,
                    role="claude-exact-packet",
                )

            self.assertEqual(response, "complete Claude response\n")
            self.assertEqual(adapter.effective_model, "claude-fable-5")
            self.assertEqual(stdin_path.read_bytes(), packet.encode("utf-8"))
            self.assertEqual(
                json.loads(argv_path.read_text(encoding="utf-8")),
                [
                    "--print",
                    "--input-format",
                    "text",
                    "--output-format",
                    "json",
                    "--model",
                    "fable",
                    "--no-session-persistence",
                    "--safe-mode",
                    "--restricted",
                    "--permission-mode",
                    "dontAsk",
                    "--tools",
                    "",
                    "--strict-mcp-config",
                    "--mcp-config",
                    "{}",
                    "--no-chrome",
                    "--disable-slash-commands",
                    "--prompt-suggestions",
                    "false",
                ],
            )
            native_directory = Path(cwd_path.read_text(encoding="utf-8"))
            self.assertNotEqual(native_directory, fixture)
            self.assertFalse(native_directory.exists())
            self.assertTrue(
                all(
                    present is False
                    for present in json.loads(env_path.read_text(encoding="utf-8")).values()
                )
            )

        with tempfile.TemporaryDirectory() as root:
            fixture = Path(root)
            executable = fixture / "claude"
            calls_path = fixture / "calls.json"
            request_path = fixture / "request.md"
            answer_path = fixture / "answer.md"
            request_path.write_text(packet, encoding="utf-8")
            answer_path.write_text("complete answer", encoding="utf-8")
            executable.write_text(
                f"#!{sys.executable}\n"
                "import json, sys\n"
                "from pathlib import Path\n"
                f"calls_path = Path({str(calls_path)!r})\n"
                "calls = json.loads(calls_path.read_text(encoding='utf-8')) if calls_path.exists() else []\n"
                "calls.append(sys.argv[1:])\n"
                "calls_path.write_text(json.dumps(calls), encoding='utf-8')\n"
                "model = 'claude-sonnet-4-5' if len(calls) == 1 else 'claude-fable-5'\n"
                "sys.stdout.write(json.dumps({\n"
                "    'type': 'result', 'subtype': 'success', 'is_error': False,\n"
                f"    'result': {_review('PASS')!r},\n"
                "    'modelUsage': {model: {'outputTokens': 5}},\n"
                "}))\n",
                encoding="utf-8",
            )
            executable.chmod(0o700)
            output_bytes = io.BytesIO()
            stdout = io.TextIOWrapper(output_bytes, encoding="utf-8")
            stderr = io.StringIO()
            with (
                patch.object(
                    cli_module,
                    "ClaudeAdapter",
                    side_effect=lambda **kwargs: ClaudeAdapter(
                        str(executable), **kwargs
                    ),
                ),
                patch.object(
                    cli_module,
                    "RunRequest",
                    side_effect=lambda **kwargs: RunRequest(
                        run_root=fixture / "runs", **kwargs
                    ),
                ),
                patch.object(cli_module.sys, "stdout", stdout),
                patch.object(cli_module.sys, "stderr", stderr),
            ):
                exit_code = cli_module._run(
                    "gear3",
                    [
                        "--request",
                        str(request_path),
                        "--current-answer",
                        str(answer_path),
                        "--native",
                        "claude",
                        "--model",
                        "fable",
                    ],
                )
                stdout.flush()

            self.assertEqual(exit_code, 0)
            self.assertEqual(output_bytes.getvalue(), b"complete answer")
            calls = json.loads(calls_path.read_text(encoding="utf-8"))
            self.assertEqual(len(calls), 2)
            for arguments in calls:
                self.assertEqual(
                    arguments[arguments.index("--model") + 1],
                    "fable",
                )
                self.assertEqual(
                    arguments[arguments.index("--output-format") + 1],
                    "json",
                )
            status = stderr.getvalue()
            self.assertIn("Requested native model selector `fable`", status)
            self.assertIn(
                "Verified effective native model: `claude-fable-5`", status
            )
            record = next((fixture / "runs").glob("*/RUN.md"))
            record_text = record.read_text(encoding="utf-8")
            self.assertIn("Requested native model selector: `fable`", record_text)
            self.assertIn("reported effective model `claude-sonnet-4-5`", record_text)
            self.assertIn(
                "Returned effective native model: `claude-fable-5`", record_text
            )

        class NotReady:
            def run(self, arguments, *, body: str = "", timeout: float = 60):
                return _ProcessResult(
                    1,
                    b"",
                    b"ZCode is not signed in. Next action: Run zcode login.",
                )

        with patch("ora_review.adapters._BridgeCommand.locate", return_value=NotReady()):
            with self.assertRaisesRegex(CallFailure, "ZCode is not signed in") as raised:
                BridgeAdapter.prepare(peer="zcode", initiator="ora-gear-3")
            self.assertIn("Run zcode login", raised.exception.display())

        for verdict, timeout_after_response in (("PASS", False), ("FAIL", False), ("FAIL", True)):
            with self.subTest(
                verdict=verdict, timeout_after_response=timeout_after_response
            ), tempfile.TemporaryDirectory() as root:
                session = Path(root) / "session"
                command = FakeBridgeCommand(
                    session, fail_after_response=True,
                    timeout_after_response=timeout_after_response, verdict=verdict
                )
                bridge = BridgeAdapter(
                    command, peer="zcode", initiator="ora-gear-3", session_dir=session
                )
                script = {} if verdict == "PASS" else {
                    "gear-3-revision-1": [lambda p: _answer(p, "revised", revision=True)],
                    "gear-3-review-2": [_review("PASS")],
                }
                native = ScriptedAdapter(script)
                result = ReviewRunner(native, bridge).run_gear3(
                    RunRequest(
                        material=UserMaterial("request"),
                        existing_answer="answer",
                        consensus=verdict == "FAIL",
                        run_root=Path(root) / "runs",
                    )
                )
                self.assertEqual(result.answer, "answer" if verdict == "PASS" else "revised")
                self.assertEqual(result.status, "PASSED")
                self.assertTrue(result.technical_incomplete)
                self.assertEqual(result.exit_code, 1)
                self.assertEqual(len(command.bodies), 1)
                self.assertEqual(
                    [role for role, _ in native.calls],
                    [] if verdict == "PASS" else ["gear-3-revision-1", "gear-3-review-2"],
                )
                run_text = Path(result.run_path).read_text(encoding="utf-8")
                self.assertIn(_review(verdict), run_text)
                self.assertIn("transport failure", run_text)
                if timeout_after_response:
                    detail = (
                        "`bridge` did not finish within 930 seconds. "
                        "Last error output: published response was not flushed"
                    )
                    self.assertIn(detail, run_text)
                    self.assertTrue(any(detail in notice for notice in result.notices))
                self.assertTrue(any(
                    "Remaining peer-owned roles will use fresh internal" in notice
                    for notice in result.notices
                ))

        with tempfile.TemporaryDirectory() as root:
            fixture = Path(root)
            request_path = fixture / "request.md"
            request_path.write_text("Answer without taking any action.", encoding="utf-8")
            calls = fixture / "calls.txt"
            executable = fixture / "codex"
            executable.write_text(
                f"#!{sys.executable}\n"
                "import os, time\n"
                "from pathlib import Path\n"
                "with Path(__file__).with_name('calls.txt').open('a') as calls:\n"
                "    calls.write(f'{os.getpid()}\\t{Path.cwd()}\\n')\n"
                "time.sleep(30)\n",
                encoding="utf-8",
            )
            executable.chmod(0o700)
            launcher = (
                "import sys\n"
                "from pathlib import Path\n"
                "from unittest.mock import patch\n"
                "from ora_review.adapters import CodexAdapter\n"
                "from ora_review.cli import main_gear3\n"
                "fixture = Path(sys.argv.pop(1))\n"
                "native = CodexAdapter(str(fixture / 'codex'))\n"
                "with patch('ora_review.cli.CodexAdapter', return_value=native), "
                "patch.object(Path, 'home', return_value=fixture), "
                "patch('tempfile.tempdir', str(fixture)):\n"
                "    sys.exit(main_gear3())\n"
            )
            process = subprocess.Popen(
                [sys.executable, "-c", launcher, root, "--request", str(request_path)],
                cwd=Path(__file__).resolve().parents[1],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
            )
            try:
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline:
                    if calls.exists() and calls.read_text(encoding="utf-8").endswith("\n"):
                        break
                    if process.poll() is not None:
                        break
                    time.sleep(0.01)
                self.assertTrue(calls.exists(), "fake native call did not start")
                first_call = calls.read_text(encoding="utf-8").splitlines()[0]
                pid, native_directory = first_call.split("\t")
                process.send_signal(signal.SIGTERM)
                stdout, stderr = process.communicate(timeout=15)
                self.assertEqual(process.returncode, 128 + signal.SIGTERM, stderr)
                self.assertEqual(stdout, b"")
                self.assertEqual(calls.read_text(encoding="utf-8").splitlines(), [first_call])
                with self.assertRaises(ProcessLookupError):
                    os.kill(int(pid), 0)
                self.assertFalse(Path(native_directory).exists())
            finally:
                if process.poll() is None:
                    process.kill()
                process.communicate(timeout=5)
                if calls.exists():
                    for call in calls.read_text(encoding="utf-8").splitlines():
                        try:
                            os.killpg(int(call.split("\t")[0]), signal.SIGKILL)
                        except ProcessLookupError:
                            pass


if __name__ == "__main__":
    unittest.main()
