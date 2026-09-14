# Ora Adversarial Review

Ora Adversarial Review is a lean, standalone reliability layer for nontrivial
AI requests. It provides three separate commands:

- `ora-gear-3` produces or accepts one complete answer, gives it a fresh
  adversarial review, and revises it when the review finds a material defect.
- `ora-gear-4` creates blind Depth and Breadth answers, cross-reviews them,
  consolidates both, and independently reviews the complete synthesis.
- `ora-validator` sends one exact validation request to one explicit external
  peer and accepts the result only when that peer directly supplies one strict
  `ACCEPT` or `REJECT` decision for every explicitly named root.

Gear one-pass is the default; `--consensus` is capped at three reviews and two
revisions. A run returns the latest complete deliverable when one exists while
keeping status and its human-readable `RUN.md` path outside the answer. The
editable Markdown method and small standard-library Python runner are standalone
from live Ora and programming workflows; Validator has one strict external-call
result contract instead.

## Setup and native engine

Python 3.10 or later is required. Gear 3 and Gear 4 also require one supported,
authenticated native command on `PATH`:

- `codex` is the compatible default. Ora starts a fresh ephemeral read-only
  `codex exec` call for every native role. This route does not select or report
  an effective model or effort.
- `claude` is selected with `--native claude`. Ora calls Claude Code directly
  through its ordinary subscription route; Agent Bridge is not involved in
  native roles. Each call is fresh, non-persistent, restricted to no model
  tools, and run in a temporary neutral directory.

Select Claude and, when requested, pin either accepted Fable selector:

```text
ora-gear-3 --request /absolute/path/request.md \
  --native claude --model fable
```

`--model` is valid only with `--native claude`. The same selected native
adapter and model selector are retained for every native producer, reviewer,
reviser, lane, consolidation, technical retry, peer-failure recovery, and the
labelled Gear 4-to-Gear 3 fallback. Ora never changes engine or model silently.

Every successful Claude call must return one unambiguous effective model in its
JSON `modelUsage`; a selected Fable alias must match it. Ora records every exact
model in `RUN.md`, reports the last after successful completion, and uses the
JSON `result` text unchanged. Missing, ambiguous, or mismatched attribution is a bounded
technical failure. A fake executable checked exact input/result, model mismatch
recovery, selector retention, restricted flags, subscription-environment
isolation, and cleanup. No live Claude or Fable model call was made, so the
route is implemented but not live qualified.

To install from this checkout, use a virtual environment. In a POSIX shell,
from the checkout directory:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
```

Pip installs all three commands and their role Markdown as a copy. Repeat
`python -m pip install .` to update it; an in-progress invocation keeps its
starting instruction snapshot.

Optional thin host entries are under `packages/codex/` and `packages/claude/`.
They invoke the installed commands without copying the method or runner. Claude
entries always select `--native claude`; Codex entries preserve the default
unless the caller deliberately selects Claude. A host installer may place the
chosen entry in its normal skill directory. The initiating host remains
distinct from the engine named by `--native`.

To remove it, run `python -m pip uninstall ora-adversarial-review` in the same
environment and remove only Gear skill directories copied from `packages/`.
User-owned run records are preserved.

## Exact input

The original request is protected data. Read it from a UTF-8 file:

```text
ora-gear-3 --request /absolute/path/request.md
ora-gear-4 --request /absolute/path/request.md
```

Or pipe exact bytes on standard input. Gear never cleans, summarizes, or
reconstructs protected material. Repeated `--later-user`,
`--assistant-context`, and `--context` files remain separate exact blocks;
later user corrections control conflicts without turning assistant or stage
artifacts into user instructions or established facts.

Gear 3 accepts `--current-answer FILE` for “review this answer.” Gear 4 uses
analytical Breadth unless `--breadth committed --commitment FILE` is explicitly
selected. The commitment file must contain the user's own nonempty words.

Validator requires a file, explicit safe root IDs, and a peer; it neither reads
standard input nor infers roots:

```text
ora-validator --request /absolute/path/validation.md \
  --root ora --root vault --peer zcode
```

Validator never accepts `--native` or `--model`. It remains an external-only
Agent Bridge operation with no native role, retry, or fallback.

## Internal and optional external review

Without `--peer`, every Gear role is a fresh selected-engine call. This proves
context separation, not different evidence, training, models, or blind spots.

`--peer TARGET` passes one user-selected ID unchanged to Agent Bridge for
peer-owned roles. Bridge owns readiness. Failure is shown exactly, then Gear
uses the already selected native engine/model; it never chooses another peer or
provider. Diversity is claimed only when independently established.

Only Gear falls back. Validator ends without certification on readiness,
transport, shape, root-set, or provenance failure; a well-formed root `REJECT`
is a completed substantive result. It certifies only the one bounded decision
body and rejects ambiguous certification material outside it.

Ora surfaces all Bridge readiness/limitation warnings outside the answer.
Bridge neither chooses nor reports Gear's native engine/model. Qwen alone may
preprocess `@` references or leading `/` commands before model input, so only
Bridge's packet record—not exact Qwen model input—is promised for that target.

External operation requires the frozen Bridge Format 2 checkout at
`AGENT_BRIDGE_HOME` or `~/agent-bridge`. Ora invokes `-m bridge` through its own
Python, omits `Project:`, and has no Format 1 path.

## Records, output, and tested scope

For Gear 3 and Gear 4, standard output contains only the complete current answer
bytes. Standard error contains configuration, selected native engine and model
selector where applicable, route/readiness, status, notices, verified final
Claude model attribution after success, and the run-record path. Every
successful Claude-native role has its own exact attribution in the record.

Validator failure leaves stdout empty; success contains its trusted wrapper and exact peer decisions. Runs are under
`~/.ora-adversarial-review/runs/<run-id>/RUN.md`.

The Codex native route was qualified on macOS 26 arm64. External Gear runs used
ZCode through Agent Bridge commit `9a6195d31b691993187c1fb7334870c3ad7a8a98`,
including loud missing-peer fallback. Other combinations are not thereby
qualified; Claude was fake-tested without a live Claude/Fable call.

[`SPECIFICATION.md`](SPECIFICATION.md) is the product contract and bounded plan.
First-party files use CC0 1.0 Universal; see [`LICENSE`](LICENSE) and
[`NOTICE`](NOTICE). Unbundled CLIs and Bridge retain their own terms.
