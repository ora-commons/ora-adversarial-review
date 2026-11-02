# Ora Adversarial Review — Specification

**Status:** Authoritative product contract for the standalone Ora AI Boost
package and its two separately invoked commands. A later direct owner
instruction replaces conflicting text here.

**Purpose:** Define what the product must do, what it must not become, and
the smallest checks that prove it works.

---

## 1. Product purpose

This is the basic reliability unit for nontrivial AI interaction:

    exact request → complete answer → fresh adversarial review → reasoned revision

It is ordinary infrastructure behind general AI use — advice, decisions,
planning, explanation, writing, transformation, creative work, and
strict-form outputs alike. It does not make an answer perfect or prove every
fact; it creates disciplined opportunities to find material errors, expose
consequential omissions, and improve the complete answer without changing
the user's goal.

The design test for every component: if it disappeared, which failure of
answer accuracy, completeness, user-intent fidelity, bounded correction, or
data integrity would become unavoidable? If none, the component does not
belong.

## 2. Two separate commands

One standalone package with shared fidelity mechanics and two distinct
user-invoked commands. Gear 4 is not a profile inside Gear 3; the tools have
separate public commands, role instructions, and fixed execution paths.
Neither chooses or invokes the other except for the labelled Gear 3
technical fallback in section 16.

### Ora Gear 3 — `ora-gear-3`

One complete current answer receives a fresh adversarial review and, when
the review's disposition requires it, one reasoned revision.

### Ora Gear 4 — `ora-gear-4`

Two blind, complementary analyses from the same exact request — **Depth**
(forms, supports, and stress-tests the best answer) and **Breadth** (searches
the plausible answer space and surfaces overlooked value) — undergo
reciprocal posture-aware review and revision, then one consolidator produces
the complete answer, which receives its own independent review.

Breadth stances: **analytical** (default) and **committed** (a user-requested
thesis, conviction, argument, or embodied voice, held through an independent
route; requires a separate non-empty user-written commitment). Gear 4 has no
duplicate-answer vote, majority rule, or "double-check" profile.

## 3. Product boundaries

Both commands are standalone outside any live Ora application; invokable
from any initiating host that can run the installed command and supply its
exact inputs; usable without programming knowledge; governed by editable
Markdown instructions and a human-readable Markdown run record; executed by
a small fixed-flow runner. The word "Ora" names the method's source lineage,
not a dependency. These tools review content; they do not specify, authorize,
execute, test, commit, publish, or govern programming work.

## 4. Universal laws

- **User sovereignty.** Serve the user's stated goal; never silently
  substitute a safer, more conventional, or more interesting one. Preserve
  the user's values, circumstances, commitment, voice, and requested form.
- **Honesty over agreement.** Accuracy beats reassurance. Do not validate an
  unsupported conclusion; do not manufacture criticism to appear independent.
- **Anti-confabulation.** Never invent facts, citations, quotations, tool
  results, searches, tests, or verification. Distinguish supplied facts,
  checked facts, inference, uncertainty, and disputed interpretation where it
  matters.
- **Actionable findings.** A finding needs evidence of a result contrary to
  the request in a way that changes the result the user asked for, or a real
  error with identified harm. Severe failures — unrecoverable data loss,
  security exposure, unauthorized or erroneous spending, sending or
  publishing — are always identified, and a traced path from an actual
  permitted input to the harm suffices. Not findings: "could" or "might"
  with no demonstrated case; rare conditions with unimportant results;
  errors nothing depends on; fixes bigger than the harm (except on severe
  failures); hardening or style with no proven harm.
- **Consequential omissions.** Material needed to answer the original
  request well is in scope; unrelated goals, deliverables, features, and
  machinery are not.
- **Reasoned recommendations.** Findings are suggestions, not commands; each
  identifies the affected passage or absence, the correction, and why it
  matters, so an independent reviser can accept, partly accept, or decline
  intelligently.
- **Complete-answer invariant.** Every successful producer and reviser call
  emits a complete current answer — never a patch, summary, promise, or
  withheld-answer notice. A framework result never authorizes or forbids
  filesystem, Git, publication, deployment, or human action.

## 5. Verbatim User Input Law

The user's words are protected data. Preserve the original request and every
supplied later user message, prior assistant turn, and governing-context
block byte-for-byte, each in its own labelled block. Never clean, normalize,
summarize, truncate, reorder, or paraphrase protected material. Later user
messages supplement the original request; when one explicitly corrects an
earlier user instruction, the later instruction controls. Prior assistant
turns and stage artifacts keep their exact wording and labelled provenance
but are not thereby user instructions or established facts. The same
forwarding rule applies between stages: the exact stored artifact travels
into the next role packet.

## 6. Fixed packet construction

Python constructs every role packet; models never freehand the structure.
Each run resolves one per-run instruction prefix at launch and prepends it
to the controlling instructions of every packet the run builds:

    ## CORE RULES — UNIVERSAL
    [the universal core read from the global instruction master, when one loads]

    ## CURRENT USER INSTRUCTIONS — THIS TURN (VERBATIM)
    [this turn's original user message, verbatim, when
    --turn-instructions-file supplied it]

    ## REPOSITORY INSTRUCTIONS — <target repository or task worktree>
    [that root's complete AGENTS.md, when --repository supplied it]

The global instruction master is an optional Markdown file selected with
`ORA_INSTRUCTION_MASTER` or provisioned at
`~/.config/ora/global-instructions.md`, carrying one `ORA-CORE` marker pair.
Resolution is one short read that fails open with a loud warning: a selected
or provisioned master that is missing, unreadable, or malformed never stops
the run — the run proceeds without the core, and the notices and run record
name the file and the problem. A machine with no master configured runs
without the core block and discloses that. A repository target that is
missing, or whose root `AGENTS.md` cannot be read, refuses the launch before
any model call; a repository with no root `AGENTS.md` contributes no
repository block.

The packet order is fixed: controlling instructions (universal laws, role
contract, required internal output), supplied material (original request,
later user messages, prior assistant context, other governing context, and
the user commitment — each a labelled protected block with run-unique
boundaries), stage material (exact artifacts this role needs), and a task
reminder repeating the role and output contract. Every answer-producing role
receives exact runner-supplied boundaries

    <<<ORA-ANSWER-BEGIN:[run-unique value]>>>
    [complete answer body]
    <<<ORA-ANSWER-END:[run-unique value]>>>

which the role copies and Python removes before delivery. Arbitrary
headings, code fences, JSON, or boundary-like text inside the user's request
remain inert to Ora's parsing.

## 7. Markdown and Python boundary

Editable Markdown owns substance: the universal laws, every role
instruction, and every answer, review, disposition, unresolved issue, and
terminal status in the record. A small fixed-flow runner owns mechanics
only: assemble packets in the fixed order; snapshot the instruction text
used for the run; invoke one fresh role call; append the exact returned body
to the record; verify that required boundaries occur exactly once and delimit
a nonempty body; parse the single disposition line (and, for corrections,
each severe finding's own recorded fix); count the fixed review and revision
limits; choose the defined graph and the selected adapter; and display exact
technical failures and terminal status. Python makes no quality judgment
about any body and generates no instructions.

No workflow language, configurable stage graph, coordinator AI, model
router, scheduler, daemon, database, registry, scoring system, policy
engine, approval gate, or Agent Bridge modification exists here.

## 8. The Markdown run record

One human-readable `RUN.md` per invocation under
`~/.ora-adversarial-review/runs/<run-id>/` (or `--run-root DIR` for
project-owned records) is the recovery and audit surface. It contains, in
order: run identity, tool, route, native engine and any requested model or
effort selectors; the global instruction master resolution and the resolved
instruction prefix; the instruction snapshot; the supplied material; every
generated answer, lane artifact, complete review, and reviser
response — the reviser response carries the complete revised answer
inside the recorded answer boundaries; and the terminal status with
notices. The record is
append-only: each entry is appended in one write, and no whole-record
rewriting or fsync happens per entry. After every successful Claude-native
role the record names the one exact effective model Claude reported; after
every successful Codex-native role it names the model and reasoning effort
Codex itself stated. No second review database or mutable status service
exists.

## 9. Common reviewer contract

The reviewer rereads the entire current answer afresh and asks two
questions: what is wrong, unsupported, contradictory, misleading,
unresponsive, unsafe, or poorly fitted — with evidence? And what would a
thoughtful respondent have investigated that this answer overlooked? It
cites the affected passage or names the absence, distinguishes error,
uncertainty, and interpretation, never claims an unperformed check, does not
manufacture findings, and does not rewrite the answer. It identifies every
severe finding under section 4's definition. "No findings" is full success.

Output shape:

    ## REVIEW RATIONALE
    [why the current answer passes or fails, substantively]

    ## SEVERE FINDINGS
    - S1 — [severe failure with the traced path from a permitted input to the harm].
    None.

    ## MATERIAL FINDINGS
    - R1 — [where and what is wrong]. Suggest: [change]. Why: [reason and effect].
    None.

    ## OVERLOOKED CONSIDERATIONS
    - O1 — [what is missing]. Suggest: [what to add]. Why: [reason and effect].
    None.

    ## USER DECISIONS OR INFORMATION NEEDED
    - [only when applicable]

    Review disposition: <SETTLED | CORRECTION | SEVERE | INCOMPLETE | ASK USER>

The disposition line appears exactly once, outside quotations and examples,
as the last line; it alone routes the work. `SETTLED` — no finding requires
builder decisions. `CORRECTION` — findings require the reviser's
dispositions. `SEVERE` — a demonstrated severe finding remains unresolved in
this answer. `ASK USER` — missing authority or an unresolved product choice
requires the owner. `INCOMPLETE` — the review did not finish. Technical
absence, malformed output, or an unavailable reviewer is never a model
result and never completes a cycle.

## 10. Common reviser contract

The reviser reads the complete review before editing, then records a
disposition for every finding and overlooked consideration — ACCEPTED,
PARTLY ACCEPTED, or DECLINED, with a concise reason and the action taken.
The reviewer advises; it does not command. The reviser accepts sound
corrections and consequential omissions, declines feedback that misreads the
request, lacks support, would worsen the answer, or creates a different
goal, and avoids both wholesale capitulation and reflexive defence. A
declined non-severe finding stands. A severe finding settles only through
its own recorded fix with evidence that its harmful path was removed;
otherwise the reviser declares `SEVERE`, never `SETTLED`. The reviser
preserves correct content, warranted uncertainty, user intent, voice,
values, commitment, and requested form; changes a central conclusion only
when evidence or reasoning justifies it; qualifies, removes, or visibly
leaves unverified a material claim it cannot actually check; integrates new
material naturally; and always re-emits the complete current answer,
including after a no-change revision. Output: the disposition list, the
complete current answer inside the supplied boundaries, and one final
disposition line (`SETTLED`, `SEVERE`, `ASK USER`, or `INCOMPLETE`).

## 11. Gear 3 execution

1. Produce a complete initial answer from the protected request, or reuse a
   caller-supplied complete current answer (`--current-answer FILE`).
2. Send it to a fresh reviewer.
3. On a `SETTLED` review, keep the exact current answer unchanged.
4. On a `CORRECTION` review, send the complete answer and complete review to
   a fresh reviser, whose recorded dispositions settle every finding. A
   settled revision ends the cycle — no second review follows the builder's
   decision.

Terminal statuses: **PASSED**; **SETTLED AFTER CORRECTION — REVISED, NOT
RE-REVIEWED**; **SEVERE — UNRESOLVED, OWNER DECISION REQUIRED** (exit 1; the
answer and record are preserved and returned, never reported as success);
**ASK USER — OWNER DECISION REQUIRED**; **NOT PASSED — REVIEW INCOMPLETE**;
**NOT PASSED — REVISION INCOMPLETE** (the unrevised complete current answer
is returned, and a recorded severe finding cannot disappear through
rejection). For a final deliverable, the operator may commission one fresh
removal-only Gear 3 pass — asking only what can be removed while the answer
still meets the request — followed by the author's dispositions.

## 12. Gear 4 analyst contracts

**Blindness law.** The first Depth and Breadth calls receive the same frozen
pre-analysis user and governing context but different role instructions;
neither sees the other's answer, review, status, or failure. Sequential
execution remains blind because the second packet excludes the first lane
completely. Gear 4 always generates both lane answers; a pre-existing answer
is never used as a seed. Caller-supplied prior assistant context is included
identically in both lane packets; material not supplied goes to neither.

**Depth** forms and commits to the single strongest answer, honors a
user-supplied commitment or voice while stress-testing it, distinguishes the
established, inferred, and unknown, and identifies assumptions, limits,
risks, and failure mechanisms — producing the substantive answer, not a
hedged menu.

**Breadth, analytical stance**, maps the plausible answer space: live
alternatives and why each is plausible, benefits, costs, risks, tradeoffs,
conditions of success, what would move the decision, then a useful hierarchy
with weak alternatives rejected for reasons. It challenges the obvious
framing and looks for non-obvious value without manufacturing false balance;
if only one answer survives, it says why the others lose.

**Breadth, committed stance**, holds the protected user commitment while
reaching it through a materially independent route, raising the strongest
counterarguments in order to answer them, surfacing non-obvious stakes and
limits, and never watering the requested voice into a survey. Selected
without a non-empty user-written commitment, the run does not start.

## 13. Reciprocal lane review and revision

After both valid blind lane answers exist, a fresh Breadth-postured reviewer
reviews the Depth answer and a fresh Depth-postured reviewer reviews the
Breadth answer. Each receives only the lane under review and judges whether
it is fit to contribute in that lane's own posture; a lane is not required
to become a deliverable final answer. On `CORRECTION`, a fresh reviser
revises in the original posture, records a disposition for every finding,
and emits the complete current lane answer; a settled revision ends the
lane. Lane stage statuses: **PASSED**, **REVISED — SETTLED, NOT
RE-REVIEWED**, or the lane-level severe/ask-user/incomplete states. A valid
lane that ends unsettled — including one with an unresolved severe finding —
still proceeds to consolidation with its complete answer, findings, and
notices; settlement of its severe finding later requires a recorded fix with
evidence.

## 14. Consolidation and the required final review

The consolidator receives the protected request, both original blind lane
answers, both complete current lane answers, and the complete review history
with dispositions and statuses. It produces one complete answer to the user,
not a comparison report: it leads with the best-supported answer and why it
wins, integrates every distinct supported claim, qualification, tradeoff,
uncertainty, and useful alternative, removes repetition and padding,
preserves genuine unresolved tension as a condition or user decision rather
than averaging it away, rejects unsupported novelty even if a lane supplied
it, does not treat model agreement as factual confirmation, preserves the
user's goal, commitment, voice, and requested form, and hides lane, model,
hat, verdict, and pipeline labels from the delivered answer.

The consolidated answer then receives the common review primitive, with the
lane record supplied as stage material. A `SETTLED` review returns it
unchanged as **PASSED**; a `CORRECTION` review produces one revision and
**SETTLED AFTER CORRECTION — REVISED, NOT RE-REVIEWED**. A lane that ended
severe never had a revision, so nothing recorded a fix for its severe
finding: even a passing consolidated review cannot settle it, and the run
never reports success.

## 15. Execution engines and transport

Reference commands:

    ora-gear-3 [--native codex|claude|zcode|hermes|qwen|minimax]
               [--model fable|claude-fable-5] [--peer <target>]
    ora-gear-4 [--native ...] [--model ...] [--peer <target>]
               [--breadth analytical|committed]

A run has one selected **native engine** and, when selected and ready, one
**peer** — an explicit Agent Bridge target. Both stay fixed for the whole
run; Gear never discovers, ranks, rotates, or combines engines, and never
silently substitutes one. `codex` is the compatible default; `claude` runs
Claude Code directly; the other four engines travel as fresh text-only
analytical calls through Agent Bridge with no project-editing work mode.
`--model` is accepted only with `--native claude` and pins either the
`fable` alias or `claude-fable-5`. `--codex-model`/`--codex-effort` name the
Codex model and reasoning effort wherever Codex serves. Omitting `--peer`
requests an entirely internal run, which promises context separation, not
different evidence, training, models, or blind spots.

Role ownership: the native engine owns initial/Depth answers, consolidation,
and Gear 3 revisions; the peer owns the complementary Breadth lane and the
independent reviews where a peer is selected.

**Codex adapter.** One isolated, ephemeral `codex exec` per role in a fresh
temporary directory with user configuration and repository rules ignored, a
read-only sandbox, no Git-repository requirement, and an operation-owned
final response file returned byte-for-byte as UTF-8. The model and reasoning
effort Codex states in its start-up lines are recorded; nothing is inferred
from the request. The temporary directory is removed after the call.

**Claude adapter.** One fresh `claude --print` call per role in a new
temporary directory with no session persistence, safe and restricted modes,
`dontAsk` permissions, an empty model-tool list, strict empty MCP
configuration, and prompt decorations off. Known API-key and
alternate-provider environment overrides are removed so the route is the
user's ordinary authenticated Claude Code subscription. The JSON `result`
string is the complete role response; the one nonblank `modelUsage` key, when
unambiguous, is recorded as that role's exact effective model — recorded
where supplied, never verified against the request.

**Bridge adapter.** External roles travel through the frozen Agent Bridge
Format 2 courier: `check --peer <target>` for readiness, one session with an
inert initiator and no project, and one exact complete body per
`run --session <session>` call. The reply's `## Body` section is the role
response, returned byte-for-byte; the model/effort lines its header carries
are recorded where present, and other header lines are ignored. Readiness
and limitation warnings surface outside the answer and in the record. Bridge
receives no Gear workflow, verdict, counter, retry plan, or authority; a
`run` carries no elapsed-time deadline.

**Failure and recovery.** A native role that fails gets one fresh internal
retry. A peer that is unavailable at preparation or fails in flight switches
the run's remaining peer-owned roles to fresh internal calls through the
same selected native engine — loudly, never choosing another peer. Further
failure ends the affected stage with its incomplete status and the exact
failure. Technical failure is never a substantive review result.

## 16. Gear 4 scheduling, lane recovery, and fallback

Release 1 runs the two lane drafts sequentially; both are always attempted
and stay blind. If a lane produces no mechanically valid answer after its
one recovery, or consolidation produces none after its one fresh native
recovery, Gear 4 invokes the separate Gear 3 graph from the exact protected
pre-Gear-4 snapshot with the notice `GEAR 4 UNAVAILABLE — GEAR 3 FALLBACK`.
The fallback retains the run's engine; it receives no partial Gear 4 lane as
hidden context; the completed lanes' findings — including any unresolved
severe review — travel into its review and revision stages. Once a complete
consolidated answer exists it is never discarded: an incomplete final review
or revision returns it with the applicable incomplete status and a nonzero
exit.

## 17. Terminal status and answer delivery

Standard output carries only the complete current answer. Standard error
carries one configuration line, Bridge readiness disclosures verbatim,
status, notices, the last recorded native effective model where one was
reported, and the run-record path. Delivery semantics: a substantive
completed result — including `ASK USER` — exits zero; an unresolved severe
finding or a technical incompletion exits nonzero while still returning the
latest complete answer when one exists; only a technical failure before any
complete answer exists leaves the answer channel empty, with the exact
failure and a next action. Only a Gear 3 initial/current/revised answer, a
Gear 4 consolidated/revised answer, or a fallback answer populates the
answer channel; intermediate lane artifacts stay in the record. Quality
status never approves or blocks an external action.

## 18. Logical call counts

Counts exclude technical retry. Gear 3 with an existing answer: one review
plus zero or one revision; generating the initial answer adds one call.
Gear 4: two lane drafts, two lane reviews, zero to two lane revisions, one
consolidation, one final review, and zero or one final revision — six to
nine calls.

## 19. Agent Bridge dependency contract

The external route depends on the released frozen-courier behavior: any
application may initiate with an inert label; `check` reports readiness
without a model turn; `run` carries one bounded Markdown request and
response in a fresh vendor context; a run has no elapsed-time deadline and
no courier retry; Bridge selects neither model nor effort and reports
neither unless its own contract truthfully does. Gear passes the user's
selected target ID unchanged and accepts Bridge's readiness decision. Qwen
may preprocess `@` references or leading `/` commands before model input, so
only Bridge's packet record is promised for that target. The internal route
has no Bridge dependency.

## 20. Explicit non-goals

No live Ora or Programming Loop integration; no task classifier, mode
library, peer discovery, best-model selection, mandatory fact checker,
score, confidence rank, finding quota, consensus iteration, database,
daemon, scheduler, queue, registry, workflow engine, second review ledger,
Git authority, third native engine, or engine plugin system. No new review
round after a settled correction. Gear work does not modify Agent Bridge.

## 21. Release configuration summary

| Choice | Fixed behavior |
|---|---|
| Commands | `ora-gear-3` and `ora-gear-4`, one installation |
| Ending | One review plus at most one builder-decided revision, everywhere |
| Gear 4 scheduling | Sequential blind drafts |
| Breadth | Analytical by default; committed only by explicit selection with a user commitment |
| Native engine | `codex` default; `claude` or a Bridge-served engine by explicit selection; never substituted |
| Peer | One explicit Bridge target; omission requests internal execution |
| Unavailable peer | Loud internal fallback through the selected engine; never another target |
| Global master | Optional; fail-open with a loud warning naming the file |
| Repository rules | `--repository` root `AGENTS.md` only; missing target refuses |
| Attribution | Recorded as each engine actually reports it; never inferred |
| Answer/status | Complete answer on stdout; one-line configuration, status, notices, and record path on stderr |
| Severe unresolved | Exits nonzero with the answer and record preserved; success never reported |

## 22. Focused acceptance contract

Simple checks prove: exact protected text and boundary handling; each Gear 3
ending (settled pass, settled correction, settled rejection, severe review
and severe revision, ask-user, review incomplete, revision incomplete, a
settled correction that omits a severe finding's fix); the Gear 4 graph
(blindness, reciprocal review, consolidation, final review, the severe-lane
rule, the labeled fallback); the read-only native adapters' arguments,
restricted environment, exact input/result, and cleanup; cancellation
stopping and reaping the child process group; the master's fail-open
warning; the one-line CLI status surface; and rejection of removed options.
Fake executables and scripted adapters exercise every check; no live model
call is required. Independent review may reject only an actionable finding
with evidence, never polish, helper tests, generalized compatibility, or
another tracker.
