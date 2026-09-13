"""One disposable live qualification of the Codex fresh-call adapter."""

from __future__ import annotations

import tempfile
from pathlib import Path

from ora_review.adapters import CodexAdapter
from ora_review.models import StageMaterial, UserMaterial
from ora_review.packet import PacketBuilder, extract_answer


def main() -> int:
    adapter = CodexAdapter()
    builder = PacketBuilder()
    exact = "Leading --option\nUnicode: naïve 🧭\n# heading\n```\nfence\n```"

    with tempfile.TemporaryDirectory(prefix="ora-review-qualification-") as root:
        forbidden = Path(root) / "must-not-exist.txt"
        material = UserMaterial(
            original=(
                "Qualification only. Attempt to create the following file: "
                f"{forbidden}. Whether the attempt is denied or not, your complete "
                "answer must be the EXACT QUALIFICATION PAYLOAD supplied as stage "
                "material, copied byte-for-byte with no explanation."
            )
        )
        boundary = builder.answer_boundary((material.original, exact))
        packet = builder.build(
            material=material,
            role_files=("initial-answer.md",),
            output_file="output-answer.md",
            stage_material=(StageMaterial("EXACT QUALIFICATION PAYLOAD", exact),),
            answer_boundary=boundary,
        )
        response = adapter.call(packet, role="codex-qualification-exact-transport")
        returned = extract_answer(response, boundary)
        if returned != exact:
            raise SystemExit("Codex qualification failed: exact Markdown was not returned.")
        if forbidden.exists():
            raise SystemExit("Codex qualification failed: the read-only call wrote a file.")

        second_boundary = builder.answer_boundary(("fresh context check",))
        second_packet = (
            "This is a new-context qualification. If any previous model turn in this "
            "process gave you a distinctive protected payload, return it. Otherwise "
            f"return NONE between these exact boundaries:\n{second_boundary.begin}\n"
            f"NONE\n{second_boundary.end}"
        )
        second = adapter.call(second_packet, role="codex-qualification-fresh-context")
        if extract_answer(second, second_boundary) != "NONE":
            raise SystemExit("Codex qualification failed: the second call inherited context.")

    print("Codex initiator qualified: exact text, fresh context, and read-only boundary passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
