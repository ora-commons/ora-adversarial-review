---
name: ora-gear-3
description: Run standalone Ora Gear 3 on an exact request or complete current answer, using Claude Code by default or an explicitly selected native engine.
---

# Ora Gear 3

Use the installed `ora-gear-3` command. Do not reproduce its reviewer,
reviser, recovery, or recording logic here.

Invoke it only when the exact original request is available in a caller-supplied
local file or through standard input supplied directly by the caller. Never
reconstruct, tidy, summarize, or retype chat text and call that “verbatim.” If
no exact machine-readable source exists, explain that limitation.

- One-pass is the default; add `--consensus` only when the user asks.
- Supply `--native claude` for the compatible Claude default. Pass the caller's
  explicit engine choice through unchanged — `--native codex`, or
  `--native zcode`/`hermes`/`qwen`/`minimax` for a fresh analytical route through
  Agent Bridge. Add `--model fable` or `--model claude-fable-5` only when the
  caller selects that Claude Fable model; otherwise let the CLI use its
  configured model, and never choose or switch an engine or model silently. The
  command verifies and records the exact effective model for every successful
  native role.
- Add `--peer TARGET` only for the exact Agent Bridge target the user selected.
  Bridge is optional and owns target validation; do not discover or substitute.
- Add `--repository PATH` with the absolute path of the repository or task
  worktree the request works on — the real candidate worktree, not the
  document folder, primary checkout, or temporary launch directory. Omit it
  for non-repository work; never guess a repository from the request text.
- Add `--assigned-path PATH` once per path the assignment actually works on
  inside that repository — repository-relative or absolute, taken from the
  assignment itself, never guessed from request text. Omit it for
  whole-repository work.
- Add `--turn-instructions-file FILE` when the current user message carries
  instructions for this turn — for example an override naming a core rule
  with its condition and scope. The file must hold the exact original
  message, never a retyped or tidied copy. Omit the option when no current
  user instruction exists.
- Use `--current-answer FILE` for an existing complete answer. Supply later user
  messages, assistant turns, and governing context only through their matching
  repeated file options and in the caller's order.
- Run in the foreground. Preserve standard output exactly as the answer and
  separately report standard-error status, route/readiness disclosures,
  verified effective model when present, warnings, and `RUN.md` path. A substantive
  `NOT PASSED` result is not a technical command failure.
