---
name: ora-gear-3
description: Run standalone Ora Gear 3 with Claude Code as its native engine on an exact request or complete current answer.
---

# Ora Gear 3

Use the installed `ora-gear-3` command and always supply `--native claude`.
Do not reproduce its reviewer, reviser, recovery, or recording logic here.

Invoke it only when the exact original request is available in a caller-supplied
local file or through standard input supplied directly by the caller. Never
reconstruct, tidy, summarize, or retype chat text and call that “verbatim.” If
no exact machine-readable source exists, explain that limitation.

- One-pass is the default; add `--consensus` only when the user asks.
- Add `--model fable` or `--model claude-fable-5` only when the caller selects
  that Claude Fable model. Otherwise let the CLI use its configured model. The
  command verifies and records the exact effective model for every successful
  native role; never switch engines or models silently.
- Add `--peer TARGET` only for the exact Agent Bridge target the user selected.
  Bridge is optional and owns target validation; do not discover or substitute.
- Use `--current-answer FILE` for an existing complete answer. Supply later user
  messages, assistant turns, and governing context only through their matching
  repeated file options and in the caller's order.
- Run in the foreground. Preserve standard output exactly as the answer and
  separately report standard-error status, route/readiness disclosures,
  verified effective model when present, warnings, and `RUN.md` path. A substantive
  `NOT PASSED` result is not a technical command failure.
