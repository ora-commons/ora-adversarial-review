from __future__ import annotations

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
from ora_review.adapters import (
    _ProcessResult,
    BridgeAdapter,
    ClaudeAdapter,
    CodexAdapter,
)
from ora_review.errors import CallFailure, MalformedResponse, OraReviewError
from ora_review.models import StageMaterial, UserMaterial
from ora_review.packet import NO_MASTER_NOTICE, PacketBuilder, extract_answer
from ora_review.runner import ReviewRunner, RunRequest


def _answer(
    packet: str,
    body: str,
    *,
    revision: bool = False,
    revision_disposition: str = "SETTLED",
    revision_items: str = "- R1 — ACCEPTED — corrected.",
) -> str:
    begins = re.findall(r"<<<ORA-ANSWER-BEGIN:[^\n>]+>>>", packet)
    ends = re.findall(r"<<<ORA-ANSWER-END:[^\n>]+>>>", packet)
    if not begins or not ends:
        raise AssertionError("scripted answer did not receive an output boundary pair")
    disposition = (
        f"## REVIEW DISPOSITION\n\n{revision_items}\n\n" if revision else ""
    )
    text = f"{disposition}{begins[-1]}\n{body}\n{ends[-1]}"
    if revision:
        text += f"\n\nReview disposition: {revision_disposition}"
    return text


def _review(
    disposition: str = "SETTLED",
    finding: str = "None.",
    *,
    severe: str = "None.",
) -> str:
    return (
        "## REVIEW RATIONALE\n\nScripted material judgment.\n\n"
        f"## SEVERE FINDINGS\n\n{severe}\n\n"
        f"## MATERIAL FINDINGS\n\n{finding}\n\n"
        "## OVERLOOKED CONSIDERATIONS\n\nNone.\n\n"
        f"Review disposition: {disposition}"
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


TEST_CORE = (
    "CORE — applies to every call this core is sent to.\n\n"
    "C0 Only the user may authorize an override."
)
TEST_OVERRIDE = (
    "Override C5 for this turn only: answer directly without manufactured "
    "pushback; applies while the draft stays under review."
)

# Every runner launch resolves the global instruction master through the real
# chain: this module points ORA_INSTRUCTION_MASTER at a fixture master file,
# so no test depends on (or writes into) anything outside its own fixtures.
_MASTER_FIXTURE: dict[str, object] = {}
_PRIOR_MASTER_ENV: dict[str, str] = {}


def _write_master_file(path: Path, core: str) -> None:
    path.write_text(
        f"<!-- ORA-CORE-BEGIN -->\n{core}\n<!-- ORA-CORE-END -->\n",
        encoding="utf-8",
    )


def setUpModule() -> None:
    directory = Path(tempfile.mkdtemp(prefix="ora-master-fixture-"))
    master = directory / "global-instructions.md"
    _write_master_file(master, TEST_CORE)
    _MASTER_FIXTURE["directory"] = directory
    _MASTER_FIXTURE["master"] = master
    if "ORA_INSTRUCTION_MASTER" in os.environ:
        _PRIOR_MASTER_ENV["ORA_INSTRUCTION_MASTER"] = os.environ[
            "ORA_INSTRUCTION_MASTER"
        ]
    os.environ["ORA_INSTRUCTION_MASTER"] = str(master)


def tearDownModule() -> None:
    if "ORA_INSTRUCTION_MASTER" in _PRIOR_MASTER_ENV:
        os.environ["ORA_INSTRUCTION_MASTER"] = _PRIOR_MASTER_ENV[
            "ORA_INSTRUCTION_MASTER"
        ]
    else:
        os.environ.pop("ORA_INSTRUCTION_MASTER", None)
    shutil.rmtree(str(_MASTER_FIXTURE["directory"]), ignore_errors=True)


class Gear3EndingTests(unittest.TestCase):
    """One simple check per Gear 3 ending, on the shared scripted adapter."""

    def test_each_ending(self) -> None:
        severe_finding = (
            "- S1 — traced path from a permitted input to data loss."
        )
        cases = (
            (
                "settled-review-passes",
                {"gear-3-review-1": [_review("SETTLED")]},
                "original answer",
                "PASSED",
                False,
                1,
            ),
            (
                "settled-correction",
                {
                    "gear-3-review-1": [_review("CORRECTION", "- R1 — material defect.")],
                    "gear-3-revision-1": [
                        lambda packet: _answer(packet, "revised", revision=True)
                    ],
                },
                "revised",
                "SETTLED AFTER CORRECTION — REVISED, NOT RE-REVIEWED",
                False,
                2,
            ),
            (
                "settled-rejection-keeps-answer",
                {
                    "gear-3-review-1": [_review("CORRECTION", "- R1 — not a defect.")],
                    "gear-3-revision-1": [
                        lambda packet: _answer(
                            packet,
                            "original answer",
                            revision=True,
                            revision_items=(
                                "- R1 — DECLINED — the claim lacks support; no change."
                            ),
                        )
                    ],
                },
                "original answer",
                "SETTLED AFTER CORRECTION — REVISED, NOT RE-REVIEWED",
                False,
                2,
            ),
            (
                "severe-fix-settles",
                {
                    "gear-3-review-1": [
                        _review("CORRECTION", "- R1 — material.", severe=severe_finding)
                    ],
                    "gear-3-revision-1": [
                        lambda packet: _answer(
                            packet,
                            "revised",
                            revision=True,
                            revision_items=(
                                "- R1 — ACCEPTED — corrected.\n"
                                "- S1 — ACCEPTED — removed the harmful path; "
                                "the traced input no longer reaches it."
                            ),
                        )
                    ],
                },
                "revised",
                "SETTLED AFTER CORRECTION — REVISED, NOT RE-REVIEWED",
                False,
                2,
            ),
            (
                "severe-review-goes-to-owner",
                {
                    "gear-3-review-1": [
                        _review("SEVERE", "- R1 — adjacent.", severe=severe_finding)
                    ]
                },
                "original answer",
                "SEVERE — UNRESOLVED, OWNER DECISION REQUIRED",
                False,
                1,
            ),
            (
                "severe-revision-never-succeeds",
                {
                    "gear-3-review-1": [
                        _review("CORRECTION", "- R1 — material.", severe=severe_finding)
                    ],
                    "gear-3-revision-1": [
                        lambda packet: _answer(
                            packet, "revised", revision=True, revision_disposition="SEVERE"
                        )
                    ],
                },
                "revised",
                "SEVERE — UNRESOLVED, OWNER DECISION REQUIRED",
                False,
                2,
            ),
            (
                "ask-user-review",
                {
                    "gear-3-review-1": [
                        _review("ASK USER", "- R1 — needs a product choice.")
                    ]
                },
                "original answer",
                "ASK USER — OWNER DECISION REQUIRED",
                False,
                1,
            ),
            (
                "review-incomplete",
                {
                    "gear-3-review-1": [
                        CallFailure("native failure"),
                        CallFailure("native recovery failure"),
                    ]
                },
                "original answer",
                "NOT PASSED — REVIEW INCOMPLETE",
                True,
                2,
            ),
            (
                "review-missing-disposition-is-incomplete",
                {
                    "gear-3-review-1": [
                        "## REVIEW RATIONALE\n\nIncomplete scripted review.",
                        CallFailure("native recovery failure"),
                    ]
                },
                "original answer",
                "NOT PASSED — REVIEW INCOMPLETE",
                True,
                2,
            ),
            (
                "duplicate-disposition-is-incomplete",
                {
                    "gear-3-review-1": [
                        "## REVIEW RATIONALE\n\nTwo declaration lines.\n\n"
                        "Review disposition: SETTLED\n\n"
                        "Review disposition: MAYBE",
                        CallFailure("native recovery failure"),
                    ]
                },
                "original answer",
                "NOT PASSED — REVIEW INCOMPLETE",
                True,
                2,
            ),
            (
                "revision-incomplete",
                {
                    "gear-3-review-1": [_review("CORRECTION", "- R1 — material.")],
                    "gear-3-revision-1": [
                        CallFailure("first native failure"),
                        CallFailure("recovery failure"),
                    ],
                },
                "original answer",
                "NOT PASSED — REVISION INCOMPLETE",
                True,
                3,
            ),
            (
                "settled-without-the-severe-fix-is-incomplete",
                {
                    "gear-3-review-1": [
                        _review("CORRECTION", "- R1 — material.", severe=severe_finding)
                    ],
                    "gear-3-revision-1": [
                        lambda packet: _answer(
                            packet, "revised", revision=True, revision_items="None."
                        ),
                        CallFailure("recovery failure"),
                    ],
                },
                "original answer",
                "NOT PASSED — REVISION INCOMPLETE",
                True,
                3,
            ),
            (
                "answer-text-severe-line-does-not-settle",
                # An S-label line inside the answer body is answer content,
                # not the severe finding's own recorded fix in the
                # correction's REVIEW DISPOSITION section.
                {
                    "gear-3-review-1": [
                        _review("CORRECTION", "- R1 — material.", severe=severe_finding)
                    ],
                    "gear-3-revision-1": [
                        lambda packet: (
                            "## REVIEW DISPOSITION\n\nNone.\n\n"
                            "## COMPLETE CURRENT ANSWER\n"
                            + _answer(
                                packet,
                                "- S1 — the unresolved issue in the original review.",
                            )
                            + "\n\nReview disposition: SETTLED"
                        ),
                        CallFailure("recovery failure"),
                    ],
                },
                "original answer",
                "NOT PASSED — REVISION INCOMPLETE",
                True,
                3,
            ),
        )
        for name, script, answer, status, incomplete, calls in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as root:
                native = ScriptedAdapter(script)
                result = ReviewRunner(native).run_gear3(
                    RunRequest(
                        material=UserMaterial("exact request"),
                        existing_answer="original answer",
                        run_root=Path(root),
                    )
                )
                self.assertEqual(result.answer, answer)
                self.assertEqual(result.status, status)
                self.assertEqual(result.technical_incomplete, incomplete)
                self.assertEqual(
                    result.exit_code,
                    1 if incomplete or result.status.startswith("SEVERE") else 0,
                )
                self.assertEqual(len(native.calls), calls)
                run_text = Path(result.run_path).read_text(encoding="utf-8")
                self.assertIn(f"Status: **{status}**", run_text)
                if name == "settled-without-the-severe-fix-is-incomplete":
                    # The reviewer's severe finding survives the failed
                    # correction in the record.
                    self.assertIn("S1 — traced path", run_text)

    def test_initial_answer_failure_leaves_record_only(self) -> None:
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
                    RunRequest(material=UserMaterial("request"), run_root=Path(root))
                )
            self.assertIn("incomplete run record", raised.exception.display())
            records = tuple(Path(root).glob("*/RUN.md"))
            self.assertEqual(len(records), 1)
            self.assertIn(
                "TECHNICAL FAILURE — NO COMPLETE ANSWER",
                records[0].read_text(encoding="utf-8"),
            )

    def test_peer_failure_switches_to_internal(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            native = ScriptedAdapter(
                {
                    "gear-3-initial-answer": [lambda p: _answer(p, "first answer")],
                    "gear-3-review-1": [_review("SETTLED")],
                }
            )
            peer = ScriptedAdapter(
                {"gear-3-review-1": [CallFailure("peer unavailable")]}
            )
            result = ReviewRunner(native, peer).run_gear3(
                RunRequest(material=UserMaterial("request"), run_root=Path(root))
            )
            self.assertEqual(result.status, "PASSED")
            self.assertEqual(len(peer.calls), 1)
            self.assertEqual([role for role, _ in native.calls], ["gear-3-initial-answer", "gear-3-review-1"])
            self.assertTrue(any(
                "Route changed to internal".lower() in notice.lower()
                or "Remaining peer-owned roles" in notice
                for notice in result.notices
            ))


class Gear4GraphTests(unittest.TestCase):
    def test_complete_graph_blindness_and_ownership(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            native = ScriptedAdapter(
                {
                    "gear-4-depth-draft": [lambda p: _answer(p, "DEPTH-ORIGINAL")],
                    "gear-4-depth-revision-1": [
                        lambda p: _answer(p, "DEPTH-CURRENT", revision=True)
                    ],
                    "gear-4-breadth-review-1": [_review("SETTLED")],
                    "gear-4-consolidation": [lambda p: _answer(p, "SYNTHESIS")],
                    "gear-4-consolidated-answer-revision-1": [
                        lambda p: _answer(p, "FINAL-ANSWER", revision=True)
                    ],
                },
                engine="claude",
            )
            peer = ScriptedAdapter(
                {
                    "gear-4-breadth-draft": [lambda p: _answer(p, "BREADTH-ORIGINAL")],
                    "gear-4-depth-review-1": [
                        _review("CORRECTION", "- R1 — missed alternative.")
                    ],
                    "gear-4-consolidated-answer-review-1": [
                        _review("CORRECTION", "- R1 — synthesis omission.")
                    ],
                }
            )
            result = ReviewRunner(native, peer).run_gear4(
                RunRequest(material=UserMaterial("GEAR4-REQUEST"), run_root=Path(root))
            )
            self.assertEqual(result.answer, "FINAL-ANSWER")
            self.assertEqual(
                result.status, "SETTLED AFTER CORRECTION — REVISED, NOT RE-REVIEWED"
            )
            self.assertFalse(result.technical_incomplete)
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
            # Blind lanes: neither draft sees the other lane.
            self.assertNotIn("DEPTH-ORIGINAL", packets["gear-4-breadth-draft"])
            self.assertNotIn("BREADTH-ORIGINAL", packets["gear-4-depth-draft"])
            # Reciprocal review sees only its own lane.
            self.assertIn("DEPTH-ORIGINAL", packets["gear-4-depth-review-1"])
            self.assertNotIn("BREADTH-ORIGINAL", packets["gear-4-depth-review-1"])
            self.assertIn("BREADTH-ORIGINAL", packets["gear-4-breadth-review-1"])
            self.assertNotIn("DEPTH-ORIGINAL", packets["gear-4-breadth-review-1"])
            # Consolidation sees both current lanes, and the final review
            # sees the synthesis and the lane record.
            self.assertIn("DEPTH-CURRENT", packets["gear-4-consolidation"])
            self.assertIn("BREADTH-ORIGINAL", packets["gear-4-consolidation"])
            self.assertIn("SYNTHESIS", packets["gear-4-consolidated-answer-review-1"])
            self.assertIn("DEPTH LANE QUALITY STATUS", packets["gear-4-consolidation"])
            self.assertIn(
                "REVISED — SETTLED, NOT RE-REVIEWED", packets["gear-4-consolidation"]
            )

    def test_severe_lane_never_reports_success(self) -> None:
        # A lane that ended severe never had a revision, so nothing recorded
        # a fix for its severe finding: even a passing consolidated review
        # cannot settle it.
        with tempfile.TemporaryDirectory() as root:
            native = ScriptedAdapter(
                {
                    "gear-4-depth-draft": [lambda p: _answer(p, "D")],
                    "gear-4-breadth-review-1": [_review("SETTLED")],
                    "gear-4-consolidation": [lambda p: _answer(p, "C")],
                },
                engine="claude",
            )
            peer = ScriptedAdapter(
                {
                    "gear-4-breadth-draft": [lambda p: _answer(p, "B")],
                    "gear-4-depth-review-1": [
                        _review(
                            "SEVERE",
                            "- R1 — adjacent defect.",
                            severe="- S1 — traced path from a permitted input to data loss.",
                        )
                    ],
                    "gear-4-consolidated-answer-review-1": [_review("SETTLED")],
                }
            )
            result = ReviewRunner(native, peer).run_gear4(
                RunRequest(material=UserMaterial("severe lane request"), run_root=Path(root))
            )
            self.assertEqual(
                result.status, "SEVERE — UNRESOLVED, OWNER DECISION REQUIRED"
            )
            self.assertEqual(result.exit_code, 1)

    def test_lane_failure_uses_labelled_gear3_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            native = ScriptedAdapter(
                {
                    "gear-4-depth-draft": [lambda p: _answer(p, "PARTIAL-DEPTH")],
                    "gear-4-breadth-draft": [CallFailure("native lane recovery failed")],
                    "gear-3-initial-answer": [lambda p: _answer(p, "FALLBACK-ANSWER")],
                    "gear-3-review-1": [_review("SETTLED")],
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
            fallback_packet = next(
                packet for role, packet in native.calls if role == "gear-3-initial-answer"
            )
            self.assertNotIn("PARTIAL-DEPTH", fallback_packet)

    def test_consolidation_failure_carries_lane_findings_to_fallback(self) -> None:
        # A consolidation failure must not drop the completed lanes'
        # findings: the fallback reviewer receives them, including an
        # unresolved severe lane review.
        with tempfile.TemporaryDirectory() as root:
            native = ScriptedAdapter(
                {
                    "gear-4-depth-draft": [lambda p: _answer(p, "DEPTH-ORIGINAL")],
                    "gear-4-breadth-review-1": [_review("SETTLED")],
                    "gear-4-consolidation": [
                        CallFailure("consolidation native failure"),
                        CallFailure("consolidation native recovery failure"),
                    ],
                    "gear-3-initial-answer": [lambda p: _answer(p, "FALLBACK-ANSWER")],
                },
                engine="claude",
            )
            peer = ScriptedAdapter(
                {
                    "gear-4-breadth-draft": [lambda p: _answer(p, "BREADTH-ORIGINAL")],
                    "gear-4-depth-review-1": [
                        _review(
                            "SEVERE",
                            "- R1 — lane defect.",
                            severe="- S1 — traced path from a permitted input to data loss.",
                        )
                    ],
                    "gear-3-review-1": [_review("SETTLED")],
                }
            )
            result = ReviewRunner(native, peer).run_gear4(
                RunRequest(material=UserMaterial("severe lane request"), run_root=Path(root))
            )
            self.assertEqual(result.answer, "FALLBACK-ANSWER")
            fallback_review = next(
                packet for role, packet in peer.calls if role == "gear-3-review-1"
            )
            self.assertIn("DEPTH COMPLETE REVIEW 1", fallback_review)
            self.assertIn(
                "S1 — traced path from a permitted input to data loss", fallback_review
            )
            self.assertIn("BREADTH COMPLETE REVIEW 1", fallback_review)

    def test_committed_breadth_requires_user_commitment(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            runner = ReviewRunner(ScriptedAdapter({}))
            with self.assertRaises(OraReviewError):
                runner.run_gear4(
                    RunRequest(
                        material=UserMaterial("request"),
                        breadth="committed",
                        run_root=Path(root),
                    )
                )
            with self.assertRaises(OraReviewError):
                runner.run_gear4(
                    RunRequest(
                        material=UserMaterial("request", commitment=" \n\t"),
                        breadth="committed",
                        run_root=Path(root),
                    )
                )
            with self.assertRaises(OraReviewError):
                runner.run_gear4(
                    RunRequest(
                        material=UserMaterial("request"),
                        existing_answer="seed",
                        run_root=Path(root),
                    )
                )


class PacketAndRecordTests(unittest.TestCase):
    def test_exact_text_boundaries_and_prefix(self) -> None:
        original = (
            "  Keep leading space\r\n# User heading\r\n```json\r\n"
            '{"text":"naïve 🧭 --mode yolo"}\r\n```\r\n'
            "<<<ORA-PROTECTED-BEGIN:not-ours>>>\r\n"
        )
        later = "Second message\n\nwith exact spacing.\n"
        material = UserMaterial(original=original, later_user_messages=(later,))
        builder = PacketBuilder()
        boundary = builder.answer_boundary()
        packet = builder.build(
            material=material,
            role_files=("initial-answer.md",),
            output_file="output-answer.md",
            stage_material=(StageMaterial("EXACT STAGE", "STATUS: NOT PASSED"),),
            answer_boundary=boundary,
        )
        self.assertIn(original, packet)
        self.assertIn(later, packet)
        self.assertIn("STATUS: NOT PASSED", packet)
        self.assertLess(packet.index("# CONTROLLING ORA INSTRUCTIONS"), packet.index(original))
        strict = '{"answer":"kept exactly"}'
        self.assertEqual(extract_answer(_answer(packet, strict), boundary), strict)
        with self.assertRaises(MalformedResponse):
            extract_answer("no supplied boundaries", boundary)

    def test_instruction_prefix_core_turn_repository(self) -> None:
        # The resolved core, the verbatim turn body, and the repository's
        # root AGENTS.md lead every packet of the run, and the binding
        # expires with it.
        native = ScriptedAdapter({
            "gear-3-initial-answer": [lambda p: _answer(p, "first answer")],
            "gear-3-review-1": [_review("SETTLED")],
        })
        with tempfile.TemporaryDirectory() as root:
            repo = Path(root) / "repo"
            repo.mkdir()
            (repo / "AGENTS.md").write_text(
                "Rule: one file per change.", encoding="utf-8"
            )
            runner = ReviewRunner(native=native)
            result = runner.run_gear3(RunRequest(
                material=UserMaterial("Review this exact answer."),
                current_turn_instructions=TEST_OVERRIDE,
                repository_path=repo,
                run_root=Path(root) / "runs",
            ))
            run_text = Path(result.run_path).read_text(encoding="utf-8")
        self.assertEqual(result.status, "PASSED")
        for role, packet in native.calls:
            self.assertLess(
                packet.index("## CORE RULES — UNIVERSAL"),
                packet.index("## UNIVERSAL LAWS"), role)
            self.assertEqual(packet.count(TEST_CORE), 1, role)
            self.assertIn(TEST_OVERRIDE, packet, role)
            self.assertIn("Rule: one file per change.", packet, role)
            self.assertIn("## REPOSITORY INSTRUCTIONS", packet, role)
        self.assertIsNone(runner.packet_builder.instruction_prefix)
        self.assertIn("RESOLVED INSTRUCTION PREFIX — VERBATIM", run_text)

    def test_master_fail_open_with_loud_warning(self) -> None:
        # A selected master that is missing or malformed never stops the
        # run: it proceeds without the core and carries a loud warning.
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            broken = root_path / "broken-master.md"
            broken.write_text("no core markers here", encoding="utf-8")
            for name, selected in (
                ("missing", str(root_path / "missing.md")),
                ("malformed", str(broken)),
            ):
                with self.subTest(master=name):
                    native = ScriptedAdapter({
                        "gear-3-initial-answer": [
                            lambda p: _answer(p, f"answer {name}")],
                        "gear-3-review-1": [_review("SETTLED")],
                    })
                    with patch.dict(
                        os.environ, {"ORA_INSTRUCTION_MASTER": selected}
                    ):
                        result = ReviewRunner(native).run_gear3(
                            RunRequest(
                                material=UserMaterial("m"),
                                run_root=root_path / f"runs-{name}",
                            )
                        )
                    self.assertEqual(result.status, "PASSED")
                    self.assertTrue(any(
                        "WARNING" in notice and selected in notice
                        for notice in result.notices
                    ))
                    self.assertNotIn("## CORE RULES — UNIVERSAL", native.calls[0][1])

    def test_unconfigured_master_notice(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            home = Path(root) / "home"
            home.mkdir()
            native = ScriptedAdapter({
                "gear-3-initial-answer": [lambda p: _answer(p, "no core")],
                "gear-3-review-1": [_review("SETTLED")],
            })
            with (
                patch.dict(os.environ, {"ORA_INSTRUCTION_MASTER": ""}),
                patch.object(Path, "home", return_value=home),
            ):
                result = ReviewRunner(native).run_gear3(
                    RunRequest(
                        material=UserMaterial("m"), run_root=Path(root) / "runs"
                    )
                )
            self.assertEqual(result.status, "PASSED")
            self.assertIn(NO_MASTER_NOTICE, result.notices)
            self.assertNotIn("## CORE RULES — UNIVERSAL", native.calls[0][1])

    def test_repository_refusals_happen_before_any_call(self) -> None:
        native = ScriptedAdapter({})
        runner = ReviewRunner(native=native)
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(OraReviewError):
                runner.run_gear3(RunRequest(
                    material=UserMaterial("m"),
                    repository_path=Path(root) / "nope",
                    run_root=Path(root) / "runs",
                ))
        self.assertEqual(native.calls, [])


class CliSurfaceTests(unittest.TestCase):
    def test_run_status_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            request_path = root_path / "request.md"
            request_path.write_text("Review this exact answer.", encoding="utf-8")
            answer_path = root_path / "answer.md"
            answer_path.write_text("complete answer", encoding="utf-8")
            native = ScriptedAdapter({"gear-3-review-1": [_review("SETTLED")]})
            output_bytes = io.BytesIO()
            stdout = io.TextIOWrapper(output_bytes, encoding="utf-8")
            stderr = io.StringIO()
            with (
                patch.object(cli_module, "CodexAdapter", return_value=native),
                patch.object(
                    cli_module,
                    "RunRequest",
                    side_effect=lambda **kwargs: RunRequest(
                        **{**kwargs, "run_root": root_path / "runs"}
                    ),
                ),
                patch.object(cli_module.sys, "stdout", stdout),
                patch.object(cli_module.sys, "stderr", stderr),
            ):
                exit_code = cli_module._run(
                    "gear3",
                    ["--request", str(request_path), "--current-answer", str(answer_path)],
                )
                stdout.flush()
            self.assertEqual(exit_code, 0)
            self.assertEqual(output_bytes.getvalue(), b"complete answer")
            status = stderr.getvalue()
            self.assertIn("Ora Gear 3; native engine `codex`.", status)
            self.assertIn("Status: PASSED", status)
            self.assertIn("Run record:", status)
            # The long manufactured route prose is gone: one configuration
            # line only.
            self.assertNotIn("Fresh context is guaranteed", status)
            self.assertNotIn("plaintext transcripts", status)
            records = tuple((root_path / "runs").glob("*/RUN.md"))
            self.assertEqual(len(records), 1)

    def test_removed_options_are_rejected(self) -> None:
        for option in ("--consensus", "--assigned-path", "--assigned-path=x"):
            with self.subTest(option=option), self.assertRaises(SystemExit):
                cli_module._run("gear3", ["--request", "x", option])
        with self.assertRaises(SystemExit):
            cli_module._run("gear4", ["--request", "x", "--consensus"])


class ReadOnlyEngineTests(unittest.TestCase):
    """The two native adapters start fresh, restricted, read-only calls."""

    def test_codex_adapter_arguments_and_reporting(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            fixture = Path(root)
            argv_path = fixture / "codex-argv.json"
            stdin_path = fixture / "stdin.bin"
            executable = fixture / "codex"
            executable.write_text(
                f"#!{sys.executable}\n"
                "import json, sys\n"
                "from pathlib import Path\n"
                f"Path({str(argv_path)!r}).write_text(json.dumps(sys.argv[1:]), encoding='utf-8')\n"
                f"Path({str(stdin_path)!r}).write_bytes(sys.stdin.buffer.read())\n"
                "sys.stderr.write(\n"
                "    'OpenAI Codex v0.162.1\\n'\n"
                "    'model: gpt-5.3\\n'\n"
                "    'reasoning effort: high\\n'\n"
                ")\n"
                "out = sys.argv[sys.argv.index('--output-last-message') + 1]\n"
                f"Path(out).write_text({_review('SETTLED')!r}, encoding='utf-8')\n",
                encoding="utf-8",
            )
            executable.chmod(0o700)
            adapter = CodexAdapter(str(executable), model="gpt-5.3", effort="high")
            response = adapter.call("# exact packet", role="codex-read-only")
            self.assertEqual(response, _review("SETTLED"))
            self.assertEqual(adapter.reported_model, "gpt-5.3")
            self.assertEqual(adapter.reported_effort, "high")
            self.assertEqual(stdin_path.read_bytes(), b"# exact packet")
            arguments = json.loads(argv_path.read_text(encoding="utf-8"))
            for required in (
                "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules",
                "--skip-git-repo-check",
            ):
                self.assertIn(required, arguments)
            self.assertEqual(
                arguments[arguments.index("--sandbox") + 1], "read-only"
            )
            self.assertEqual(arguments[arguments.index("-m") + 1], "gpt-5.3")
            self.assertEqual(
                arguments[arguments.index("-c") + 1], "model_reasoning_effort=high"
            )

    def test_claude_adapter_restrictions_and_attribution(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            fixture = Path(root)
            argv_path = fixture / "claude-argv.json"
            cwd_path = fixture / "cwd.txt"
            env_path = fixture / "env.json"
            executable = fixture / "claude"
            executable.write_text(
                f"#!{sys.executable}\n"
                "import json, os, sys\n"
                "from pathlib import Path\n"
                f"Path({str(argv_path)!r}).write_text(json.dumps(sys.argv[1:]), encoding='utf-8')\n"
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
                response = adapter.call("# exact packet", role="claude-read-only")
            self.assertEqual(response, "complete Claude response\n")
            self.assertEqual(adapter.effective_model, "claude-fable-5")
            arguments = json.loads(argv_path.read_text(encoding="utf-8"))
            for required in (
                "--print", "--no-session-persistence", "--safe-mode",
                "--restricted", "--strict-mcp-config", "--no-chrome",
                "--disable-slash-commands",
            ):
                self.assertIn(required, arguments)
            self.assertEqual(
                arguments[arguments.index("--permission-mode") + 1], "dontAsk"
            )
            self.assertEqual(arguments[arguments.index("--tools") + 1], "")
            native_directory = Path(cwd_path.read_text(encoding="utf-8"))
            self.assertNotEqual(native_directory, fixture)
            self.assertFalse(native_directory.exists())
            self.assertTrue(
                all(
                    present is False
                    for present in json.loads(env_path.read_text(encoding="utf-8")).values()
                )
            )

    def test_claude_ambiguous_attribution_is_not_a_failure(self) -> None:
        # The reported model is recorded only where unambiguous; an
        # ambiguous report never fails the call.
        with tempfile.TemporaryDirectory() as root:
            executable = Path(root) / "claude"
            executable.write_text(
                f"#!{sys.executable}\n"
                "import json, sys\n"
                "sys.stdout.write(json.dumps({\n"
                "    'type': 'result', 'subtype': 'success', 'is_error': False,\n"
                "    'result': 'answer text',\n"
                "    'modelUsage': {'a': 1, 'b': 2},\n"
                "}))\n",
                encoding="utf-8",
            )
            executable.chmod(0o700)
            adapter = ClaudeAdapter(str(executable))
            self.assertEqual(adapter.call("# packet", role="r"), "answer text")
            self.assertIsNone(adapter.effective_model)


class BridgeAdapterTests(unittest.TestCase):
    def test_lenient_response_reading_and_choices(self) -> None:
        packet = "# exact packet"

        class FakeBridgeCommand:
            def __init__(self, session: Path) -> None:
                self.session = session
                self.bodies: list[str] = []
                self.arguments: list[tuple[str, ...]] = []

            def run(self, arguments, *, body: str = "", timeout: float | None = 60):
                self.bodies.append(body)
                self.arguments.append(tuple(arguments))
                messages = self.session / "messages"
                messages.mkdir(parents=True, exist_ok=True)
                response = messages / "0002-peer-to-initiator.md"
                response.write_text(
                    "# Message 0002\nFrom: zcode\nTo: ora-gear-3\n"
                    "An unrecognized header line\n"
                    "Model: glm-5.3\nEffort: high\n\n"
                    "## Body\n\n" + _review("SETTLED"),
                    encoding="utf-8",
                )
                return _ProcessResult(
                    0, (str(response) + "\n").encode("utf-8"), b"warning text"
                )

        with tempfile.TemporaryDirectory() as root:
            session = Path(root) / "session"
            command = FakeBridgeCommand(session)
            bridge = BridgeAdapter(command, peer="zcode", session_dir=session)
            response = bridge.call(packet, role="gear-3-review-1")
            self.assertEqual(response, _review("SETTLED"))
            self.assertEqual(command.bodies, [packet])
            self.assertEqual(
                command.arguments, [("run", "--session", str(session))]
            )
            self.assertEqual(bridge.last_call_notice, "warning text")
            self.assertIsNotNone(bridge.last_call_choices)
            self.assertEqual(bridge.last_call_choices.model, "glm-5.3")
            self.assertEqual(bridge.last_call_choices.effort, "high")

    def test_failure_and_foreign_path_are_refused(self) -> None:
        class FailingCommand:
            def run(self, arguments, *, body: str = "", timeout: float | None = 60):
                if "run" in arguments:
                    return _ProcessResult(1, b"", b"transport broke")
                return _ProcessResult(0, b"ready\n", b"")

        class OutsideCommand:
            def run(self, arguments, *, body: str = "", timeout: float | None = 60):
                if "run" in arguments:
                    return _ProcessResult(0, b"/etc/passwd\n", b"")
                raise AssertionError(arguments)

        with tempfile.TemporaryDirectory() as root:
            session = Path(root) / "session"
            failing = BridgeAdapter(
                FailingCommand(), peer="zcode", session_dir=session
            )
            with self.assertRaisesRegex(CallFailure, "transport broke"):
                failing.call("# packet", role="r")
            outside = BridgeAdapter(
                OutsideCommand(), peer="zcode", session_dir=session
            )
            with self.assertRaisesRegex(CallFailure, "outside its session"):
                outside.call("# packet", role="r")


class ProcessBoundaryTests(unittest.TestCase):
    def test_cancellation_cleans_up_the_child_group(self) -> None:
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
                self.assertEqual(
                    calls.read_text(encoding="utf-8").splitlines(), [first_call]
                )
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
