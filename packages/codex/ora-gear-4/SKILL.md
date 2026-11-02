---
name: ora-gear-4
description: Run standalone Ora Gear 4 on an exact request, using Codex by default or an explicitly selected native engine, with analytical or committed Breadth.
---

# Ora Gear 4

Use the installed `ora-gear-4` command. Do not reproduce its analyst,
reciprocal-review, consolidation, or final-review instructions in this skill.

The command's verbatim-input law is load-bearing. Invoke it only when the exact
original request is available through a caller-supplied local file or through
standard input that the caller supplied directly. Never reconstruct, tidy,
summarize, or retype the current chat message into a temporary file and call
that "verbatim." If there is no exact machine-readable source, explain this
host limitation plainly instead of pretending the fidelity guarantee holds.

- Analytical Breadth is the default. Add `--breadth committed` only when the
  user explicitly selects it, and supply the separate exact user-written
  commitment with `--commitment FILE`.
- Omit `--native` or use `--native codex` for the compatible Codex default. Pass
  the caller's explicit engine choice through unchanged — `--native claude`, or
  `--native zcode`/`hermes`/`qwen`/`minimax` for a fresh analytical route through
  Agent Bridge. Add
  `--model fable` or `--model claude-fable-5` only when the caller also selects
  that Claude Fable model; never choose or switch an engine or model silently.
- Add `--peer TARGET` only for the Agent Bridge target the user selected. Pass
  that ID unchanged; Bridge owns target validation. Never discover, rotate, or
  silently substitute another target.
- Add `--repository PATH` with the absolute path of the repository or task
  worktree the request works on — the real candidate worktree, not the
  document folder, primary checkout, or temporary launch directory. Omit it
  for non-repository work; never guess a repository from the request text.
- Add `--turn-instructions-file FILE` when the current user message carries
  instructions for this turn — for example an override naming a core rule
  with its condition and scope. The file must hold the exact original
  message, never a retyped or tidied copy. Omit the option when no current
  user instruction exists.
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
