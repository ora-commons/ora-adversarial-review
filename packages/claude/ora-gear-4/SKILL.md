---
name: ora-gear-4
description: Run standalone Ora Gear 4 with Claude Code as its native engine on an exact request, with analytical or committed Breadth and optional consensus.
---

# Ora Gear 4

Use the installed `ora-gear-4` command and always supply `--native claude`.
Do not reproduce its blind lanes, review, consolidation, recovery, or recording
logic here.

Invoke it only when the exact original request is available in a caller-supplied
local file or through standard input supplied directly by the caller. Never
reconstruct, tidy, summarize, or retype chat text and call that “verbatim.” If
no exact machine-readable source exists, explain that limitation.

- Analytical Breadth and one-pass are defaults. Select committed Breadth only
  when the user explicitly asks, with their exact nonempty `--commitment FILE`;
  add `--consensus` only when requested.
- Add `--model fable` or `--model claude-fable-5` only when the caller selects
  that Claude Fable model. Otherwise let the CLI use its configured model. The
  command verifies and records the exact effective model for every successful
  native role, retry, and fallback; never switch engines or models silently.
- Add `--peer TARGET` only for the exact Agent Bridge target the user selected.
  Bridge is optional and owns target validation; do not discover or substitute.
- Supply later user messages, assistant turns, and governing context only
  through their matching repeated file options and in the caller's order.
- Run in the foreground. Preserve standard output exactly as the answer and
  separately report standard-error status, route/readiness disclosures,
  verified effective model when present, warnings, fallback notice, and `RUN.md` path.
