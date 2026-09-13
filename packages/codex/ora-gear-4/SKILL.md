---
name: ora-gear-4
description: Run standalone Ora Gear 4 on an exact request, using Codex by default or an explicitly selected Claude native engine, analytical or committed Breadth, and optional consensus.
---

# Ora Gear 4

Use the installed `ora-gear-4` command. Do not reproduce its analyst,
reciprocal-review, consolidation, or final-review instructions in this skill.

The command's verbatim-input law is load-bearing. Invoke it only when the exact
original request is available through a caller-supplied local file or through
standard input that the caller supplied directly. Never reconstruct, tidy,
summarize, or retype the current chat message into a temporary file and call
that “verbatim.” If there is no exact machine-readable source, explain this
host limitation plainly instead of pretending the fidelity guarantee holds.

- Analytical Breadth and one-pass are the defaults. Add `--breadth committed`
  only when the user explicitly selects it, and supply the separate exact
  user-written commitment with `--commitment FILE`.
- Add `--consensus` only when the user asks for it.
- Omit `--native` or use `--native codex` for the compatible Codex default. If
  the caller explicitly selects Claude Code, use `--native claude`. Add
  `--model fable` or `--model claude-fable-5` only when the caller also selects
  that Claude Fable model; never choose or switch an engine or model silently.
- Add `--peer TARGET` only for the Agent Bridge target the user selected. Pass
  that ID unchanged; Bridge owns target validation. Never discover, rotate, or
  silently substitute another target.
- Supply later user messages, assistant turns, or governing context only
  through their matching repeated file options and in the caller's order.
- Run the command in the foreground. The command owns both blind lanes, their
  review, consolidation, final review, recovery, status, and `RUN.md`; this
  skill must not reproduce the graph manually.
- Keep the command's standard output as the answer and report its separate
  standard-error status, all Bridge readiness and limitation disclosures,
  selected native engine/model disclosures, verified Claude effective model
  when present, fallback notice when present, and run-record path. Never
  suppress warnings from successful readiness checks.
