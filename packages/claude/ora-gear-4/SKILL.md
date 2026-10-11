---
name: ora-gear-4
description: Run standalone Ora Gear 4 on an exact request, using Claude Code by default or an explicitly selected native engine, with analytical or committed Breadth and optional consensus.
---

# Ora Gear 4

Use the installed `ora-gear-4` command. Do not reproduce its blind lanes,
review, consolidation, recovery, or recording logic here.

Invoke it only when the exact original request is available in a caller-supplied
local file or through standard input supplied directly by the caller. Never
reconstruct, tidy, summarize, or retype chat text and call that “verbatim.” If
no exact machine-readable source exists, explain that limitation.

- Analytical Breadth and one-pass are defaults. Select committed Breadth only
  when the user explicitly asks, with their exact nonempty `--commitment FILE`;
  add `--consensus` only when requested.
- Supply `--native claude` for the compatible Claude default. Pass the caller's
  explicit engine choice through unchanged — `--native codex`, or
  `--native zcode`/`hermes`/`qwen`/`minimax` for a fresh analytical route through
  Agent Bridge. Add `--model fable` or `--model claude-fable-5` only when the
  caller selects that Claude Fable model; otherwise let the CLI use its
  configured model, and never choose or switch an engine or model silently. The
  command verifies and records the exact effective model for every successful
  native role, retry, and fallback.
- Add `--peer TARGET` only for the exact Agent Bridge target the user selected.
  Bridge is optional and owns target validation; do not discover or substitute.
- Supply later user messages, assistant turns, and governing context only
  through their matching repeated file options and in the caller's order.
- Run in the foreground. Preserve standard output exactly as the answer and
  separately report standard-error status, route/readiness disclosures,
  verified effective model when present, warnings, fallback notice, and `RUN.md` path.
