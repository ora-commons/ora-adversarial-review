# Ora Adversarial Review — Specification and Implementation Plan

**Status:** Authoritative product contract and bounded implementation plan.

**Authority:** This is the product contract for the standalone Ora Adversarial
Review package and its three separately invoked commands. It consolidates the
product owner's current decisions and the portable parts of Ora's live review
contracts. A later direct owner instruction replaces conflicting text here.

**Purpose:** Define what the product must do, what it must not become, and the
smallest implementation sequence that proves it works. It is not a conversation
log, construction diary, or description of live Ora.

---

## 1. Product purpose

This is the basic reliability unit for nontrivial AI interaction:

    exact request → complete answer → fresh adversarial review → reasoned revision

It is intended to be ordinary infrastructure behind general AI use, not a
special-purpose audit invoked only for programming or formal analysis. It must
work for advice, decisions, planning, explanation, writing, transformation,
creative work, interpretation, and strict-form outputs as well as analytical
questions.

It does not make an answer perfect or independently prove every fact. It creates
one or more disciplined opportunities to find material errors, expose
consequential omissions, and improve the complete answer without changing the
user's goal.

The design test for every component is:

> If this component disappeared, which core failure of answer accuracy,
> completeness, user-intent fidelity, bounded correction, or data integrity
> would become unavoidable?

If the answer is none, the component does not belong.

---

## 2. One product, three separate commands

Ora Adversarial Review is one standalone package with shared fidelity
mechanics and three distinct user-invoked commands. This prevents the common laws,
packet handling, run record, and review primitive from drifting while keeping
the two Gear methods and the external validator unmistakably separate.

Gear 4 is not a profile or switch inside Gear 3. The tools have separate public
commands, role instructions, and fixed execution paths. Neither command chooses
or invokes the other except for the prominently labelled Gear 3 technical
fallback defined in section 18.

### Ora Gear 3

One complete current answer receives a fresh adversarial review and, when
needed, a reasoned revision.

Public command name: **ora-gear-3**.

Termination configurations:

- **one-pass** — default; one review and, on FAIL, one revision;
- **consensus** — fresh whole-answer review and revision repeat to a fixed cap.

### Ora Gear 4

Two blind, complementary analyses are produced from the same exact request:

- **Depth** uses White and Black Hat disciplines to form, support, and
  stress-test the best answer.
- **Breadth** uses Green and Yellow Hat disciplines to search the plausible
  answer space, compare tradeoffs, and surface non-obvious value.

The lanes undergo reciprocal posture-aware review and revision, then one
consolidator produces the complete answer. That answer receives its own
independent Gear-3-style review because consolidation is the most consequential
stage.

Public command name: **ora-gear-4**.

Breadth stance configurations:

- **analytical** — default; map plausible answers, tradeoffs, conditions, and
  overlooked value;
- **committed** — for a user-requested thesis, conviction, argument, or embodied
  voice; hold that commitment while reaching it through a genuinely different
  route.

Termination configurations:

- **one-pass** — one review and at most one revision for each lane and for the
  consolidated answer;
- **consensus** — the same bounded whole-answer consensus primitive applies
  independently to each lane and to the consolidated answer.

Gear 4 has no duplicate-answer vote, majority rule, or “double-check” profile.
Its value is deliberately different Depth and Breadth work.

### Ora Validator

One exact request file and an explicit list of opaque safe root IDs go to one
explicit Agent Bridge peer in one protected packet. The selected peer directly
authors one `ACCEPT` or `REJECT` decision for every root, with nonempty
`BEHAVIOR`, `MECHANISM`, `EVIDENCE`, and `LIMITATIONS` fields.

Public command name: **ora-validator**.

Validator has no internal route, native adapter, retry, fallback, aggregate
PASS/FAIL, inferred root, or configurable workflow. A valid root `REJECT` is a
completed substantive result. Unavailable transport, uncertain publication,
missing or extra roots, duplicate roots or fields, malformed content, and
unverified provenance are technical failures and produce no certifying result.

---

## 3. Product boundaries

All three commands are:

- standalone outside the live Ora application;
- invokable from any initiating host that can run the installed command and
  supply its exact inputs;
- usable without programming knowledge;
- independent of any Programming Loop;
- governed by editable Markdown instructions and a human-readable Markdown run
  record;
- executed by a small fixed-flow runner for mechanical fidelity.

Gear 3 and Gear 4 are capable of external review through Agent Bridge or
internal review through fresh Codex or Claude Code calls. Codex is the compatible
default; Claude Code is an explicit native-engine selection. Validator is
deliberately external-only and completes exactly one peer call. The application
that invokes a command is an initiating host, not necessarily the native engine
that performs Gear roles.

The word “Ora” in their names identifies the method and its source lineage. It
does not create a dependency on the live Ora application or its mode library.

A programming task, specification, plan, or code answer can be submitted as
ordinary content. These tools do not specify, authorize, execute, test, commit,
publish, merge, or govern programming work.

---

## 4. Universal laws

These laws apply to every producer, reviewer, reviser, and consolidator call.

### 4.1 User sovereignty

- Serve the user's stated goal.
- Never silently substitute a safer, more conventional, more analytical, or
  more interesting goal.
- Preserve the user's values, circumstances, commitment, voice, and requested
  form when they are part of the request.
- A reviewer may challenge a flawed premise, but may not replace the user's
  objective merely because it prefers another one.

### 4.2 Honesty over agreement

- Accuracy is more important than agreement or reassurance.
- Do not validate an unsupported conclusion.
- Do not manufacture objections, alternatives, or caveats merely to appear
  independent.
- Pushback must address something central, consequential, factually important,
  internally contradictory, or capable of changing the outcome.

### 4.3 Anti-confabulation

- Never invent facts, citations, quotations, user circumstances, source
  contents, tool results, searches, tests, or verification.
- Distinguish supplied facts, actually checked facts, general knowledge,
  interpretation, and inference whenever the distinction matters.
- A checkable factual error, an unestablished claim, and a disputed
  interpretation are different findings.
- If support is unavailable, state what is uncertain and what evidence or user
  information could resolve it.
- A common view does not by itself make a defensible contested conclusion a
  factual error.

### 4.4 Materiality

- Review only defects or omissions capable of materially changing truth,
  usefulness, safety, the user's decision or action, compliance with the
  request, or the requested form.
- Optional polish, reviewer taste, preferred abstractions, and merely
  interesting tangents cannot cause FAIL.
- There is no minimum number of findings.
- A strong answer may pass unchanged.

### 4.5 Consequential omissions are in scope

“Do not expand scope” does not prohibit material needed to answer the original
request well. A reviewer must ask what the first response failed to investigate
or consider.

New material is justified when it fills a consequential omission tied to the
original request. It is prohibited when it creates an unrelated goal,
deliverable, feature, process, or machinery.

### 4.6 Reasoned recommendations

- Review findings are suggestions, not commands.
- Every suggested change must identify the affected passage or precise absence,
  state the suggested correction or investigation, and explain why it matters.
- The explanation must be persuasive enough for an independent reviser to
  accept, partly accept, or decline it intelligently.
- The reviewer outputs conclusions, supporting arguments, and relevant
  evidence or uncertainty. It does not expose private chain-of-thought or
  narrate the act of reviewing.

### 4.7 Complete-answer invariant

- Every successful producer and reviser call emits a complete current answer.
- Never substitute a patch, diff, summary, “unchanged” note, promise to answer,
  process narration, or withheld-answer notice for that answer.
- A framework verdict never authorizes or forbids filesystem, Git, publication,
  deployment, or human action.
- On every terminal quality status, the complete current answer is returned.

---

## 5. Verbatim User Input Law

The user's words are protected data, not material the runner or another model
may improve.

This law governs Ora's recording, packet construction, and intact handoff to its
adapter. It is not an exact-model-input guarantee for a Bridge target with the
declared limitation in section 22.

- Preserve the original request byte-for-byte: spelling, punctuation,
  capitalization, whitespace, Markdown, examples, order, and emphasis.
- Preserve each later user message in its own chronological verbatim block.
- Preserve each prior assistant turn the caller explicitly supplies in a
  separate block clearly labelled as assistant output. The runner does not
  infer which earlier turns matter.
- Later user messages supplement the original request. When a later user
  message explicitly corrects or conflicts with an earlier user instruction,
  the later user instruction controls.
- Never clean, normalize, correct, summarize, truncate, silently split,
  reorder, or paraphrase protected material.
- Prior assistant turns and stage artifacts retain their exact wording and
  labelled provenance, but are not thereby user instructions or established
  facts.
- Any model-derived interpretation is additional and clearly distinguishable
  from protected material.
- If exact protected material cannot fit or Ora cannot hand it off intact,
  report a technical failure. Never retry with an abbreviated version.

The same forwarding rule applies to model artifacts between stages. Ora places
the exact stored artifact in the next role packet, not a paraphrase of it.

---

## 6. Fixed packet construction

Python constructs every role packet. Models never freehand the packet structure.

The order is fixed:

    # CONTROLLING ORA INSTRUCTIONS

    ## UNIVERSAL LAWS
    [common editable Markdown]

    ## ROLE FOR THIS CALL
    [one editable role contract]

    ## REQUIRED INTERNAL OUTPUT
    [the role's output contract]

    ---

    # SUPPLIED MATERIAL — VERBATIM WITH LABELLED PROVENANCE

    ## ORIGINAL USER REQUEST — VERBATIM
    [run-unique protected block]

    ## LATER USER MESSAGES — VERBATIM, CHRONOLOGICAL
    [zero or more protected blocks]

    ## PRIOR ASSISTANT CONTEXT — VERBATIM
    [zero or more turns explicitly supplied by the caller]

    ## OTHER GOVERNING CONTEXT — VERBATIM
    [only context actually supplied and available to the initiating harness]

    ---

    # STAGE MATERIAL — VERBATIM
    [the exact artifacts required by this role]

    ---

    # TASK REMINDER — CONTROLLING
    [the role's task, generated from the same source as the opening role]

    ## OUTPUT ORDER — REQUIRED
    [the exact internal response shape and the run-unique answer boundaries]

The controlling instructions, user messages, assistant context, governing
context, and stage artifacts must be visually unmistakable from one another.
The original request must never be buried inside prose written by the runner.
Exact preservation proves wording and provenance; it does not turn an assistant
or stage claim into a user instruction or an established fact.

Each protected block uses a run-unique boundary that does not occur in any
stored body. Python records a digest for each protected block.
Arbitrary headings, code fences, JSON, XML, or boundary-like text inside the
user's request remain inert to Ora's parsing and packet construction. This does
not override a selected target's declared model-input limitation.

Every answer-producing role receives exact runner-supplied boundaries such as:

    <<<ORA-ANSWER-BEGIN:[run-unique value]>>>
    [complete answer body]
    <<<ORA-ANSWER-END:[run-unique value]>>>

The actual unique value is generated only after Python confirms that neither
boundary occurs in any stored artifact. The role copies the supplied boundaries;
it does not invent them. Python removes them before delivery. Initial-answer,
lane-answer, reviser, and consolidator calls all use this same mechanism.

When the host exposes separate system and user channels, controlling
instructions use the controlling channel and Ora places protected material in
the data channel. Agent Bridge carries one ordered Markdown body, so the same
boundaries and order remain explicit inside that body.

---

## 7. Markdown and Python boundary

### Markdown owns substance

Editable Markdown contains:

- the universal laws;
- Gear 3 reviewer and reviser instructions;
- Gear 4 Depth, Breadth, reciprocal-review, lane-revision, consolidation, and
  final-review instructions;
- validator per-root judgment and strict output instructions;
- the complete evolving run context;
- every answer, review, disposition, verdict, unresolved issue, and terminal
  status.

### Python owns mechanics

A small fixed-flow runner performs only work models do unreliably:

- create and atomically update one shared Markdown run file;
- create collision-safe protected blocks and verify their bytes;
- snapshot the instruction text used for the run;
- assemble packets in the fixed order;
- invoke one fresh role call;
- append the exact returned body to the appropriate block;
- verify that each required boundary occurs exactly once and that it delimits a
  non-empty body; any other result is malformed and takes the defined recovery
  path; Python makes no quality judgment about the body;
- extract only runner-owned wrappers using the run-unique boundaries;
- parse only a line-anchored final PASS or FAIL verdict;
- parse validator output only when every explicit root has one strict ACCEPT or
  REJECT section with all four required nonempty fields;
- count the fixed review and revision limits;
- select the already-defined Gear 3 or Gear 4 graph;
- choose the external peer or selected native call adapter, keeping that native
  engine and any Claude model selector for the complete run;
- validate Claude Code's JSON result and exact effective-model attribution
  before accepting its unchanged result text;
- display exact technical failures and terminal status.

Python does not judge the review, interpret whether two models substantively
agree, score an answer, generate instructions, or infer new workflow stages.

### What must not be built

No workflow language, configurable stage graph, coordinator AI, model router,
peer-discovery service, scheduler, daemon, database, registry, ledger, scoring
system, policy engine, approval gate, Git gate, or Agent Bridge modification.

The control flow is fixed in ordinary Python. The wording remains forkable
Markdown.

---

## 8. Shared Markdown run record

One human-readable Markdown file is canonical for the review method's current
run. Agent Bridge's own session messages remain transport records; they do not
become workflow state.

The run file contains, in order:

1. run identity, selected tool, native engine, any requested Claude model
   selector, and other configuration;
2. instruction snapshot;
3. protected user and governing-context blocks;
4. any pre-existing complete current answer;
5. each generated answer or Gear 4 lane artifact;
6. each complete review;
7. each reviser disposition and complete revised answer;
8. Gear 4 consolidation inputs and complete consolidated answer;
9. terminal quality status, unresolved findings, and technical notices.

After every successful Claude-native role, the record also names that role, the
requested selector or lack of one, and the one exact effective model returned by
the official CLI. Codex records the selected engine but makes no effective-model
or effort claim.

Python owns the headings, boundaries, ordering, and atomic writes. Models supply
only the body of their assigned output block.

The file is the recovery and audit surface. No second review database or mutable
status service exists.

A validator run uses the same protected instruction/material blocks and atomic
write. Its record additionally names the selected peer, explicit root list,
external-only route, verified Format 2 session and response-message identity,
response digests, and the fact that no fallback occurred. Untrusted readiness,
warning, failure, and peer-response text that Ora writes to `RUN.md` stays
inside protected record blocks. Envelope, count, or direction failures can
leave candidate response text inspectable only in Agent Bridge's session files;
the validator does not copy those unverified candidates into `RUN.md`.

---

## 9. Common reviewer contract

The reviewer receives the exact request, available governing context, and the
complete current answer. In later consensus rounds it also receives prior
findings and the reviser's reasons, but must reread the entire current answer
afresh.

The reviewer asks:

1. What is materially wrong, unsupported, contradictory, misleading,
   unresponsive, unsafe, or poorly fitted to the user's actual purpose?
2. What would a thoughtful, well-informed respondent have investigated or
   considered that this answer overlooked, and could that omission materially
   improve or change the response?

Relevant overlooked considerations may include facts, ambiguity, assumptions,
alternative interpretations, user circumstances, values, emotional reality,
stakeholders, tradeoffs, practical obstacles, consequences, boundary
conditions, risks, opportunities, or challenges to the framing. This is a
search lens, not a quota.

The reviewer:

- judges only by standards relevant to this request;
- protects the user's goal, values, commitment, voice, words, and requested
  form;
- cites the affected passage or names precisely what is absent;
- distinguishes error, uncertainty, and interpretation;
- never claims an unperformed check;
- makes each recommendation concrete and explains its reasoning and material
  effect;
- does not manufacture criticism;
- does not rewrite the answer.

Minimal internal output:

    ## VERDICT RATIONALE
    [Briefly explain why the current answer passes or fails the materiality
    standard. State the controlling strengths or defects; do not narrate the
    review process.]

    ## MATERIAL FINDINGS
    - R1 — [where and what is wrong]. Suggest: [specific change].
      Why: [reason and material effect].
    None.

    ## OVERLOOKED CONSIDERATIONS
    - O1 — [what is missing]. Suggest: [what to investigate or add].
      Why: [reason and what it could change].
    None.

    ## USER DECISIONS OR INFORMATION NEEDED
    - [only when the answer responsibly requires user input or evidence]

    VERDICT: <PASS | FAIL>

The optional user-decision section is omitted when not applicable. The other
two sections use “None.” when empty.

PASS means no material defect or consequential omission remains in the exact
current answer for the information available.

FAIL means at least one finding could materially change accuracy, usefulness,
safety, the user's decision or action, adherence to the request, or the
requested form.

An answer may PASS when its correct conclusion is that evidence is insufficient,
the matter cannot presently be resolved, or the user must make a stated choice.
It must explain why and identify the exact information or decision needed.

Technical absence, malformed output, or an unavailable reviewer is not a model
FAIL and never becomes PASS.

---

## 10. Common reviser contract

The reviser reads the complete review before changing the answer.

For every material finding and overlooked consideration, it:

- **accepts**, **partly accepts**, or **declines** the suggestion;
- states a concise reason;
- states the action taken when accepted or partly accepted.

The reviewer advises; it does not command. The reviser must avoid both wholesale
capitulation and reflexive defence.

The reviser:

- accepts sound corrections and consequential omissions even when they require
  material not present in the first answer;
- declines feedback that misreads the request, lacks support, would worsen the
  answer, or creates a different goal;
- preserves correct content, warranted uncertainty, useful nuance, user intent,
  voice, values, commitment, and requested form;
- changes a central conclusion only when evidence or reasoning justifies it;
- verifies a material checkable claim when real evidence access exists;
- otherwise qualifies, removes, or visibly leaves the claim unverified;
- integrates new material naturally rather than pasting the review into the
  answer;
- always re-emits the complete current answer, including on a no-op revision.

Minimal internal output:

    ## REVIEW DISPOSITION
    - R1 — ACCEPTED | PARTLY ACCEPTED | DECLINED — [action and reason].
    - O1 — ACCEPTED | PARTLY ACCEPTED | DECLINED — [action and reason].
    None.

    ## COMPLETE CURRENT ANSWER
    <<<ORA-ANSWER-BEGIN:[runner-supplied unique value]>>>
    [the entire answer in the user's requested form]
    <<<ORA-ANSWER-END:[runner-supplied unique value]>>>

The runner uses unique boundaries rather than Markdown headings alone to extract
the complete answer. It removes the internal wrapper before delivery.
“None.” is used only when the disposition section has no items.

---

## 11. Ora Gear 3 execution

### 11.1 Starting answer

Gear 3 may:

- produce a complete initial answer from the protected request; or
- reuse an already existing complete current answer.

Reuse is necessary for requests such as “review what you just told me.”

### 11.2 Default one-pass

1. Obtain the complete current answer.
2. Send it to a fresh reviewer.
3. On PASS, keep the exact current answer unchanged.
4. On FAIL, send the complete answer and complete review to a fresh reviser.
5. Return the complete revised answer and stop. Do not seek agreement.

Terminal quality status:

- reviewer PASS: **PASSED**;
- revision after FAIL: **ONE PASS COMPLETE — REVISED, NOT RE-REVIEWED**;
- unavailable or malformed review after a complete current answer exists:
  **NOT PASSED — REVIEW INCOMPLETE**, plus the exact technical failure;
- unavailable or malformed revision after reviewer FAIL and one internal
  recovery attempt: **NOT PASSED — REVISION INCOMPLETE**, plus the exact
  technical failure.

REVIEW INCOMPLETE is neither a substantive PASS nor a completed substantive
NOT PASSED review: no reviewer completed an inspection of the current answer.
REVISION INCOMPLETE preserves the reviewer FAIL and returns the unrevised
complete current answer rather than pretending that correction occurred.

### 11.3 Optional bounded consensus

The same first review and revision occur. After a revision:

1. A new fresh reviewer receives the whole current answer, protected request,
   prior findings, and reviser dispositions.
2. It reviews the whole answer again and may identify new material defects or
   omissions.
3. PASS freezes the current answer.
4. FAIL permits another full revision while the fixed budget remains.
5. A final fresh review examines the whole answer.

Fixed ceiling:

- at most three review calls;
- at most two revision calls;
- stop immediately on PASS.

Terminal quality status:

- latest reviewer PASS: **PASSED**;
- latest reviewer FAIL when the cap is spent: **NOT PASSED**;
- technically incomplete review with a complete answer available:
  **NOT PASSED — REVIEW INCOMPLETE**, plus the exact failure;
- technically incomplete revision after reviewer FAIL:
  **NOT PASSED — REVISION INCOMPLETE**, plus the exact failure.

NOT PASSED is useful information, not withheld work. The run record preserves:

- the unresolved reviewer objection;
- the reviser's accept/partial/decline reason;
- why the final reviewer still considers the issue material;
- any user information or decision that could resolve it.

The complete current answer is always returned.

---

## 12. Ora Gear 4 analyst contracts

### 12.1 Blindness law

The first Depth and Breadth calls receive the same frozen pre-analysis user and
governing context but different role instructions.

- Neither sees the other's answer, review, status, or failure.
- Each runs in a fresh context.
- Sequential execution remains blind when the second packet excludes the first
  lane completely.
- Parallelism is only a latency optimization.

Gear 4 always generates both lane answers from the protected request. A
pre-existing answer is never used as an asymmetric seed. Any prior assistant
context explicitly supplied by the caller is protected and included identically
in both lane packets; material not supplied goes to neither lane. The runner
does not interpret the request to decide what earlier context it needs.

### 12.2 Depth — White and Black Hats

Depth produces the single strongest answer the user should receive.

- Honor an explicit user-supplied commitment, thesis, stance, voice, or requested
  form. Stress-test it rather than replacing it.
- When the request leaves the conclusion open, choose the best-supported answer
  and commit to it.
- Use the grounds appropriate to the task: supplied facts, genuinely checked
  evidence, explicit inference, practical reasoning, user-stated values,
  circumstances, or craft judgment.
- Distinguish what is established, what is inferred, and what remains unknown.
- Explain the reasoning supporting the answer.
- Identify assumptions, limits, boundary conditions, missing information, and
  what evidence or changed circumstances would alter the conclusion.
- Stress-test the commitment with specific risks and failure mechanisms rather
  than generic caution.
- For advice, identify likely human and practical consequences. For creative
  work, commit to the strongest execution without pretending taste is objective
  fact.
- Produce the substantive answer, not a hedged menu, risk catalogue, or process
  narration.

### 12.3 Breadth — Green and Yellow Hats, analytical default

Breadth searches for the plausible answer space and overlooked value.

- Independently examine plausible answers, interpretations, approaches, or ways
  of serving the request.
- Explain why each live alternative is plausible.
- Identify benefits, costs, risks, tradeoffs, consequences, opportunities, and
  conditions of success when relevant.
- Explain why rejected alternatives lose.
- Challenge the obvious framing and look for non-obvious possibilities,
  stakeholders, circumstances, or adjacent value.
- For advice, consider materially different values, circumstances, emotional
  realities, and practical consequences.
- For creative work, consider materially different executions without turning
  the final product into a survey.
- Breadth is search effort, not an alternative quota. If only one answer
  survives, say so and explain what was considered and rejected.
- Do not manufacture ambiguity around a settled fact.
- Produce substantive analysis independently; do not anticipate Depth or create
  difference for its own sake.

### 12.4 Breadth committed stance

Committed stance is valid only when the initiating adapter supplies a separate,
non-empty protected commitment block in the user's own words. The runner checks
only whether that block exists; it never derives or interprets a commitment.
The tool never invents one.

Breadth then:

- holds the requested thesis, conviction, opinion, or embodied voice;
- reaches it through an independent evidence route, framing, or angle;
- uses Green Hat creativity and Yellow Hat value in service of that commitment;
- raises the strongest counterarguments in order to answer them rather than
  preserving them as a neutral menu;
- surfaces non-obvious stakes, opportunities, and limits;
- never waters the requested voice into an analytical survey.

If committed stance is selected without that block, the run does not start.
The tool reports the missing input plainly so the user may supply it.

---

## 13. Ora Gear 4 reciprocal review and revision

After both valid blind lane answers exist:

- A fresh Breadth-postured reviewer reviews the Depth answer.
- A fresh Depth-postured reviewer reviews the Breadth answer.

Both use the common reviewer contract.

Each first reciprocal reviewer receives the protected request, governing
context, and only the lane answer under review. A later consensus reviewer also
receives that same lane's prior findings and reviser dispositions. Neither sees
the sibling lane. Its posture comes from its role instructions, not from the
sibling lane.

A lane review judges whether the answer is fit to contribute in that lane's own
posture. It does not judge whether a Breadth lane is already a deliverable final
answer or require it to become a second Depth answer.

### Breadth reviewing Depth

It asks especially:

- Which plausible alternatives, interpretations, user circumstances, values,
  stakeholders, opportunities, consequences, or frames did the commitment
  foreclose?
- Where do the answer's limits or boundary conditions need to be clearer?
- What non-obvious value could materially enrich the response?

It does not penalize Depth merely for committing.

### Depth reviewing Breadth

It asks especially:

- Which alternatives are unsupported, implausible, or false balance?
- Which answer is best supported, and has Breadth provided a usable hierarchy?
- Which assumptions, risks, failure mechanisms, or bad eliminations did the
  expansion neglect?

In committed stance it does not penalize Breadth for holding the user's thesis.
It tests the independent route, support, counterarguments, and limits.

### Lane revision

A FAIL lane reviser receives the protected request and governing context, its
own complete current lane answer, its complete review, and—in a later consensus
round—only that lane's prior findings and dispositions. It receives no sibling-
lane artifact. It revises in the original posture. A PASS lane remains
unchanged.

Every lane revision:

- accepts, partly accepts, or declines each recommendation with reasons;
- preserves the lane's Depth or Breadth job;
- preserves user intent, form, and warranted nuance;
- may add consequentially omitted material;
- explains material changes;
- emits the complete current lane answer.

---

## 14. Ora Gear 4 ending configurations

### 14.1 One-pass lanes

Each lane receives:

- one fresh review;
- at most one conditional full revision.

A PASS lane receives the stage status **PASSED**. A revised lane receives the
stage status **NOT RE-REVIEWED**. These are lane-stage records, not the terminal
run status. Two complete current lane answers then proceed to consolidation.

### 14.2 Consensus lanes

Each lane independently uses the Gear 3 consensus primitive:

- later reviewers reread the complete current lane answer;
- at most three reviews and two revisions;
- the lane freezes on PASS;
- Depth and Breadth do not have to agree with one another.

Consensus means the current lane answer is fit to contribute. It may PASS by
truthfully concluding that evidence is insufficient or a user decision is
needed.

If a valid lane remains NOT PASSED when its budget ends, its
complete current answer, unresolved objection, and reviser reasoning still
proceed to consolidation. The overall run remains truthfully NOT PASSED unless
the consolidated answer's later review resolves the defect.

This protects the complete-answer invariant and lets the consolidator use the
other lane to resolve a real weakness.

---

## 15. Ora Gear 4 consolidation

The consolidator receives:

- the protected request and governing context;
- both original blind lane answers;
- both complete current lane answers;
- the complete review history needed to understand each current lane, including
  the latest review and any still-relevant earlier finding;
- each lane's dispositions, unresolved findings, and quality status.

It produces one complete answer to the user, not a comparison report.

The consolidator:

- leads with the best-supported answer and explains why it wins;
- includes the strongest live alternatives, conditions, or limits only when
  they materially matter;
- integrates every distinct supported claim, qualification, tradeoff,
  uncertainty, user circumstance, and useful alternative;
- deduplicates repeated substance and removes padding;
- distinguishes agreement already present in the blind originals from
  convergence caused by cross-review;
- does not treat model agreement as independent factual confirmation;
- preserves genuine unresolved tension as a condition, uncertainty, or user
  decision rather than averaging it away;
- rejects unsupported novelty even when only one lane supplied it;
- introduces no unsupported claim;
- preserves the user's goal, commitment, voice, and requested form;
- hides lane, model, hat, verdict, and pipeline labels from the delivered
  answer;
- emits the complete user-facing answer inside the runner-supplied answer
  boundaries, which Python removes before delivery.

There is no separate formatter call. Formatting is part of producing the
consolidated answer, and that exact answer is reviewed afterward.

---

## 16. Required review of the consolidated answer

The consolidated answer receives the common Gear 3 review primitive.

### One-pass

1. A fresh reviewer reads the complete consolidated answer, protected request,
   both lanes, reviews, and dispositions.
2. It applies the common material-defect and overlooked-consideration questions.
3. It also checks whether consolidation lost distinct supported material,
   injected a claim, created false compromise, hid material uncertainty, or
   damaged the user's requested form.
4. PASS returns the answer unchanged as **PASSED**.
5. FAIL sends the complete consolidated answer and complete review to a fresh
   reviser. The reviser receives the same protected request, lanes, reviews,
   dispositions, and current answer as the consolidated-answer reviewer. It
   follows the common reviser contract while remaining bound by the
   consolidation rules in Section 15.
6. The reviser returns the complete answer and the run records
   **ONE PASS COMPLETE — REVISED, NOT RE-REVIEWED**.

### Consensus

The consolidated answer receives the same fixed ceiling of three
fresh whole-answer reviews and two revisions.

- PASS returns the complete answer as **PASSED**.
- Exhaustion on FAIL returns the complete answer as **NOT PASSED** with the
  unresolved objection and reasons.
- A responsible answer that says user input or evidence is required may PASS.

Consensus applies both per lane and to the consolidated answer. It never means
forcing Depth and Breadth to share a substantive conclusion.

---

## 17. Execution engines and transport

A Gear run has one selected **native engine** and, when selected and ready, one
**peer side**—the explicit Agent Bridge target. The application that launches
the command is only the initiating host: it may invoke either supported native
engine. The native engine and same peer remain fixed throughout the run. Gear
never discovers, ranks, rotates, or combines them. Every role call starts fresh;
Ora supplies only its exact packet, subject to the target's declared model-input
limitation in section 22.

Reference commands:

    ora-gear-3 [--native codex|claude] [--model fable|claude-fable-5]
               [--peer <target>] [--consensus]
    ora-gear-4 [--native codex|claude] [--model fable|claude-fable-5]
               [--peer <target>] [--consensus]
               [--breadth analytical|committed]

Codex is the compatible native default. `--native claude` selects Claude Code;
`--model` is accepted only with that engine and pins either the `fable` alias or
the full `claude-fable-5` selector. Omitting Claude's model selector permits the
official CLI's configured model, but Ora still requires and records one
unambiguous effective-model attribution for each successful role. Omitting
`--peer` requests an entirely internal run. Committed Breadth must be selected
explicitly and requires a user-supplied commitment. A native UI may present the
same choices, but cannot add hidden routing.

### 17.1 Fixed role ownership

| Role | Gear 3 external | Gear 3 internal |
|---|---|---|
| Initial answer, when needed | Fresh native call | Fresh native call |
| Reviewer | Fresh peer call | Separate fresh native call |
| Reviser | Fresh native call | Separate fresh native call |

| Role | Gear 4 external | Gear 4 internal |
|---|---|---|
| Depth draft/revision | Fresh native call | Fresh native Depth call |
| Breadth draft/revision | Fresh peer call | Separate fresh native Breadth call |
| Breadth review of Depth | Fresh peer call | Separate fresh native reviewer |
| Depth review of Breadth | Fresh native call | Separate fresh native reviewer |
| Consolidation/revision | Fresh native call | Fresh native call |
| Consolidated-answer review | Fresh peer call | Separate fresh native reviewer |

The native engine thus owns the committed answer and synthesis; the peer
supplies the complementary lane and independent challenge. An internal run
preserves separate calls and blindness but claims only context separation, not
different evidence, training, models, or blind spots.

### 17.2 Agent Bridge adapter

Ora Adversarial Review is an application above the frozen Bridge Format 2
courier. Its adapter:

1. runs `python3 -m bridge check --peer <target>` from the Bridge checkout;
2. creates one session with inert initiator `ora-gear-3` or
   `ora-gear-4` and no `Project:`;
3. sends each peer role as one exact complete body to
   `python3 -m bridge run --session <session>` from that checkout;
4. records the returned body byte-for-byte in `RUN.md`.

The adapter uses Ora's own Python interpreter for these module calls, not an
`agent-bridge` executable.

Every required fact and artifact travels in the protected packet. Omitting
`Project:` avoids project-scoped repository instructions and gives every
accepted target the same session and courier shape, not an identical
model-input guarantee. Section 22 defines the narrow declared exception. One
Bridge session may carry the run because every call starts a fresh vendor
context. Bridge receives no Gear workflow, verdict, counter, retry, plan, or
authority.

The Gear adapter uses only Format 2, with no Format 1 compatibility layer.

### 17.3 Fresh native adapters

A native adapter has one model-facing operation: start an isolated native
context with the exact UTF-8 packet and return one final text body unchanged.
It may not inherit the live conversation, sibling lane, other role context, or
content not present in the packet; nor may it summarize, trim, repair, or
reconstruct either direction.

The Codex adapter starts `codex exec` in a new temporary directory with
ephemeral execution, user configuration and repository rules ignored, a
read-only sandbox, no Git-repository requirement, and an operation-owned final
response file. It reads and returns that file as UTF-8 without selecting or
claiming an effective model or effort. The temporary directory and response
file are removed after the foreground call finishes or fails.

The Claude adapter starts the official `claude` command in a new temporary
directory with print mode, no session persistence, safe and restricted modes,
`dontAsk` permission mode, an empty model-tool list, strict empty MCP
configuration, no Chrome, disabled slash commands, and prompt suggestions off.
The exact packet is standard input. Known API-key and alternate-provider
environment overrides are removed so the supported route is the user's
ordinary authenticated Claude Code subscription, not a hidden API, Bedrock,
Vertex, Foundry, or Bridge call. Ora neither signs in nor purchases access.

Claude Code must return one successful JSON result with a string `result` and
exactly one nonblank `modelUsage` key. Ora treats the decoded `result` string as
the complete role response and hands it unchanged to the fixed response parser;
only runner-owned answer boundaries are removed. It records the returned
`modelUsage` key as that role's exact effective-model attribution. With selector
`fable`, the attribution must begin `claude-fable-`; with `claude-fable-5`, it
must equal that selector or identify one of its more specific versions. Missing,
ambiguous, or mismatched attribution is a technical failure and never usable.

The command creates exactly one native adapter for the run. Every native role,
its one technical retry, recovery after peer failure, and the complete Gear
4-to-Gear 3 fallback uses that same adapter and therefore the same engine and
Claude selector. Partial Gear 4 work never changes the selector or enters the
fallback packet. No failure may silently choose Codex, another Claude model, a
provider, or Bridge.

An initiating host lacking either supported native command may still be a
Bridge target, but it cannot claim to supply Gear's native roles on that basis.
Host-global instructions may still apply. Gear grants no filesystem mutation,
Git, publication, deployment, credential, or unrelated external-action
authority.

### 17.4 Disclosure and failure

Before work begins, status outside the answer identifies the tool, ending,
selected native engine, any requested Claude model selector, selected peer and
readiness—or internal route—and says that:

- review roles use fresh contexts;
- Codex does not select or report an effective model or effort;
- Claude requires one exact returned effective model for every successful
  native role, records each attribution, and verifies it against a requested
  Fable selector when one was supplied;
- Bridge does not select or report effective model or effort unless its own
  future contract truthfully does so; and
- an external CLI runs under the user's account and local or vendor tooling may
  retain plaintext transcripts.

Before any peer work, surface all Bridge readiness and limitation disclosures
verbatim outside the answer, including warnings returned by a successful check.
Do not suppress them because the selected target is ready.
Retain warnings from successful peer calls as separate status notices and in
`RUN.md`; never put them in the answer.

Fresh context is guaranteed. A peer result is provider- or model-diverse only
when that separation has been established independently; otherwise it is simply
a fresh second reading. Neither kind of second reading is independent factual
verification.

An initial readiness failure is shown verbatim with its next action, then the
run becomes internal through the already selected native engine and model;
Gear never chooses another peer. After a later peer failure, preserve valid
artifacts, inspect an uncertain response path, recover only the unfinished role
once through that selected native adapter, and run remaining peer-owned roles
internally. Do not retry a peer already shown unavailable.

A required internal role that returns no valid artifact gets one fresh internal
recovery. Further failure returns the latest complete answer with the applicable
incomplete status. Section 18 defines the narrower Gear 4 fallback before a
consolidated answer exists. Technical failure is never reviewer PASS or FAIL.

### 17.5 External-only validator transport

Validator requires all three input classes explicitly: `--request FILE`, one or
more repeated `--root ID` values, and `--peer TARGET`. It accepts no standard
input, inferred roots, internal route, or fallback. Root IDs are opaque to the
runner but must be safe nonempty CLI tokens, and duplicate requested IDs are
rejected before transport.

The adapter checks the selected peer, creates one Format 2 session as
`ora-validator` with no project, and sends exactly one protected packet. A
successful response is usable only when its printed path is the sole new
peer-to-initiator message for that call; its exact header has one matching
message number, one `From: <selected peer>`, and one `To: ora-validator`; and
the session, response identity, and response digests verify mechanically.

Inside runner-supplied validation boundaries, the peer must return exactly one
section for every requested root and no other root:

    ## <ROOT> — ACCEPT|REJECT
    ### BEHAVIOR
    [nonempty]
    ### MECHANISM
    [nonempty]
    ### EVIDENCE
    [nonempty]
    ### LIMITATIONS
    [nonempty]

Duplicate, missing, unexpected, empty, or malformed sections and
fields are technical failures. So is aggregate PASS/FAIL inside the bounded
body. Exactly one supplied boundary pair is required. Harmless ordinary prose
before or after that pair is ignored and excluded from the certified output,
but any additional validation marker (including one with a different token) or
certification-shaped material outside it is a technical failure. That includes
requested-root or unknown-root verdict material, standalone `ACCEPT` or
`REJECT`, aggregate `PASS` or `FAIL`, and validator-field structure. Validator
never recovers a response from an uncertain Bridge failure and never invokes
Codex. On success, its trusted wrapper and `RUN.md` identify the external route,
selected peer, exact Format 2 direction, verified session/message, response
digests, and no-fallback fact; the peer-authored root decisions remain exact
inside that wrapper.

## 18. Gear 4 scheduling, lane recovery, and Gear 3 fallback

### 18.1 Sequential execution is the Release 1 default

Release 1 runs Depth and Breadth sequentially. This avoids concurrency machinery
without changing the method:

- both lane calls are always attempted;
- Breadth receives the same frozen pre-analysis user and governing context as
  Depth;
- Breadth receives no Depth artifact, status, or failure;
- both lanes therefore remain blind and independent at first draft;
- the later reciprocal review, revision, and consolidation graph is unchanged.

A future adapter may run the first two calls concurrently only if it preserves
those exact properties. Parallelism is a latency optimization, not a third
configuration or a semantic distinction.

### 18.2 Required lane outputs

Both lanes must produce complete, mechanically valid answers before
consolidation. Mechanically valid means the supplied answer boundaries occur
exactly once and delimit a nonempty body. Python makes no judgment about the
answer's quality.

A valid lane that reaches the end of its consensus budget with
`NOT PASSED` still proceeds to consolidation. Its complete current answer,
unresolved reviewer findings, and reviser reasoning travel with it. This avoids
discarding usable work and gives the consolidator and the mandatory final review
one last opportunity to resolve the defect. The terminal Gear 4 answer cannot
be `PASSED` unless a fresh reviewer passes that exact consolidated answer.

A lane may truthfully pass while concluding that evidence or a user decision is
needed. Consensus asks whether the lane responsibly handles the available
information, not whether it can force a substantive conclusion.

### 18.3 Missing or malformed lane recovery

If either lane produces no mechanically valid answer:

1. preserve the other valid lane;
2. rerun only the missing lane once in a fresh native context;
3. use the identical protected pre-analysis packet and original posture;
4. exclude the sibling lane and the failed attempt from the recovery packet.

Once both valid lane answers exist, the result is a full Gear 4 run. No
degraded label or Gear 3 label applies.

### 18.4 Incomplete lane review or revision

When both complete lane answers exist, a later technical failure does not erase
either one. If a lane review or revision still cannot complete after its one
recovery:

- keep that lane's latest complete answer;
- record **REVIEW INCOMPLETE** or **REVISION INCOMPLETE** as a lane execution
  notice with the exact failure;
- carry the lane answer, any completed review, and the notice to consolidation;
- complete the mandatory consolidated-answer review; and
- display the lane notice beside the terminal quality status.

The final reviewer decides the quality status of the complete synthesized
answer. The process exits nonzero because a required lane stage was technically
incomplete, even if that answer receives **PASSED**. Do not invoke Gear 3 merely
because a review or revision failed after both lane answers existed.

### 18.5 Labelled Gear 3 fallback

If a required lane still has no valid answer after that one recovery, Gear 4
cannot produce its defining two-lane input. Invoke the separate Gear 3 graph
from the exact protected pre-Gear-4 snapshot and show:

    GEAR 4 UNAVAILABLE — GEAR 3 FALLBACK

The fallback:

- inherits the requested one-pass or consensus ending;
- retains the run's selected native engine and any Claude model selector for
  every fallback role and technical retry;
- receives no partial Gear 4 lane as hidden analysis context;
- produces and returns a complete Gear 3 answer;
- keeps the execution notice outside the answer bytes.

Use the same fallback if both valid lanes exist but consolidation itself cannot
produce any complete answer after one fresh native recovery.

Once a complete consolidated Gear 4 answer exists, never discard it and restart
as Gear 3. If its required review or revision cannot complete, return that
consolidated answer with the appropriate `REVIEW INCOMPLETE` or
`REVISION INCOMPLETE` status.

## 19. Terminal quality status and answer delivery

The complete answer and framework status are separate outputs.

For delivery and technical recovery, a complete user-deliverable answer is a
Gear 3 initial, current, or revised answer; a Gear 4 consolidated or revised
answer; or a successful Gear 3 fallback answer. Depth and Breadth answers and
all other intermediate stage artifacts remain in the run record and never
populate the answer channel.

Terminal quality statuses are:

- **PASSED** — a fresh reviewer passed the exact current answer;
- **ONE PASS COMPLETE — REVISED, NOT RE-REVIEWED** — the default one-pass
  answer changed after its only review;
- **NOT PASSED** — the latest reviewer still found a material defect when the
  consensus budget ended;
- **NOT PASSED — REVIEW INCOMPLETE** — a complete answer exists but its required
  review could not be completed;
- **NOT PASSED — REVISION INCOMPLETE** — a reviewer found a material defect but
  the required revision could not be completed, so the prior complete answer is
  returned.

Gear 4 may add the separate execution notice:

    GEAR 4 UNAVAILABLE — GEAR 3 FALLBACK

A Gear 4 lane may also record the stage-local quality states `PASSED`,
`NOT RE-REVIEWED`, or `NOT PASSED`, and the execution notices
`REVIEW INCOMPLETE` or `REVISION INCOMPLETE`. A lane state never substitutes
for the status of the complete delivered answer. An incomplete lane notice
remains visible and makes the process exit nonzero even when final-answer review
passes.

For the reference command:

- standard output contains only the complete current answer;
- standard error contains the selected native engine, any requested Claude
  selector, route disclosures, one short status line, any route or fallback
  notice, the last verified Claude effective model after a successful run, and
  the path to the Markdown run record;
- the run record contains the full reviewer analysis, reasoning, dispositions,
  unresolved issues, technical notices, and every successful Claude-native
  role's exact effective-model attribution.

A graphical harness adapter uses equivalent separate answer and status
surfaces. Status text never enters JSON-only, XML-only, code-only,
translation-only, fixed-length, or other strict-form output.

A substantive `NOT PASSED` result is a completed review run and exits
successfully. It may identify genuine disagreement, missing evidence, or
decisions the user must make. A technical incompletion exits nonzero while
still returning the latest complete answer when one exists. A successful
labelled Gear 3 fallback exits successfully with both its execution notice and
its own final quality status.

Only a technical failure before any complete answer exists permits an empty
answer channel. The user then receives the exact failure and one useful next
action.

Quality status never approves or blocks an external action. It reports what the
review method established.

Validator has a separate result contract. Success writes one trusted Markdown
wrapper and the exact validated peer-authored root sections to standard output;
status, warnings, and `RUN.md` path remain on standard error. `ACCEPT` and
`REJECT` are both successful substantive root decisions. Any transport,
provenance, boundary, root-set, or field-shape failure exits nonzero with empty
standard output and a clear error plus the run-record path.

## 20. Logical call counts

Counts exclude technical recovery.

| Tool and ending | Logical calls |
|---|---|
| Gear 3 one-pass, existing answer | 1 review + 0–1 revision |
| Gear 3 consensus, existing answer | 1–3 reviews + 0–2 revisions |
| Gear 4 one-pass | 6–9 total |
| Gear 4 consensus | 6–18 total |
| Validator | exactly 1 external call |

Generating Gear 3's initial answer adds one call. Gear 4 one-pass comprises two
lane drafts, two reviews, zero to two revisions, consolidation, final review,
and zero or one final revision. Consensus permits one to three reviews and zero
to two revisions independently for each lane and the consolidated answer.

The fixed cost is intentional: consensus replaces manual relay rather than
becoming an unbounded pursuit of agreement.

---

## 21. Source adaptation decisions

The portable method is the contract in this document: user sovereignty,
anti-sycophancy and anti-confabulation, complementary Depth/Breadth work,
reasoned dispositions, whole-answer review, lossless consolidation, and review
of the deliverable. It neither imports live Ora modes or machinery nor limits a
fresh reviewer from finding a consequential omission.

## 22. Agent Bridge dependency contract

The external route depends on the released behavior of the frozen
`Agent Bridge — Frozen Courier Interface`, not on construction behavior or a
native package from another harness.

The required Bridge contract is:

- any application may initiate with an inert label;
- callable targets are the installed Bridge release's connector set;
- one session binds one initiator and one target;
- `check` reports target readiness without a model turn;
- `run` carries one bounded Markdown request and response in a fresh vendor
  context;
- Bridge records the exact supplied body; target model-input behavior is
  declared separately;
- a run has a deadline and no courier retry;
- the application owns every Gear stage, counter, verdict, fallback, and status;
- Bridge selects neither model nor effort and reports neither unless its own
  future contract changes truthfully.

The Gear product passes the user's one selected target ID unchanged to Bridge
and accepts Bridge's readiness decision. It does not copy or independently
validate Bridge's target list. Adding a future target is Bridge work, not a Gear
prompt or application release. Gear does not copy connector recipes,
credentials, model catalogs, version tables, or qualification facts.

Qwen is included with a narrow limitation: Bridge records the exact role packet,
but Qwen may interpret `@` references and leading `/` commands before the model
sees it. Ora therefore promises exact recording and handoff, not exact Qwen
model input. This disclosed limitation is accepted; it is not grounds to reject
Qwen or rewrite user input. Other Bridge targets retain their exact-body
promise. Ora adds no Qwen-specific Python branch.

The Bridge implementation must conform to Format 2 before the external Gear
adapter is released. The Gear implementation must not emulate obsolete Format 1
workflow fields, `PLAN.md`, review headers, or application-specific record
kinds.

The internal route has no Bridge dependency.

Validator uses the same frozen Format 2 courier but has a stricter application
contract: readiness must succeed, one and only one peer response must be
published for its single call, provenance must verify, and no fallback or
uncertain-publication recovery is allowed.

## 23. Explicit non-goals

Release 1 has no live Ora or Programming Loop integration; task classifier,
mode library, peer discovery, best-model selection, mandatory fact checker,
score, confidence rank, finding quota, unbounded consensus, database, daemon,
scheduler, queue, registry, workflow engine, second review ledger, Git
authority, third native engine, engine plugin system, or speculative
compatibility layer. Gear work does not modify Agent Bridge; a connector change
remains a separate Bridge project. Native Claude support is a direct adapter at
the existing call boundary, not a router or general engine abstraction.

## 24. Release 1 configuration summary

| Choice | Fixed behavior |
|---|---|
| Product | One Ora Adversarial Review installation, three separate commands |
| Default ending | One-pass |
| Optional ending | `--consensus`, fixed at three reviews and two revisions |
| Gear 4 scheduling | Sequential blind drafts |
| Breadth | Analytical by default; committed only by explicit selection |
| Lane exhaustion | A valid `NOT PASSED` lane proceeds with its unresolved material |
| Native engine | `codex` by default; `claude` only by explicit selection |
| Claude model | CLI-configured model by default; `fable` or `claude-fable-5` only when explicitly selected |
| Native retry/fallback | Keep the same selected engine and Claude selector throughout |
| Peer | One explicit Bridge target; omission requests internal execution |
| Unavailable peer | Loud internal fallback; never another automatic target |
| Bridge project | Always omitted |
| Attribution | Codex model/effort not selected or reported; every successful Claude role records one exact effective model |
| Answer/status | Complete answer on the answer channel; status and record path separately |
| Substantive `NOT PASSED` | Completed run, not a technical process failure |
| Validator input | Exact request file, repeated explicit root IDs, and explicit peer |
| Validator route | Exactly one external call; no native route, retry, or fallback |
| Validator result | One strict ACCEPT/REJECT section per root with trusted transport wrapper |

These are not stored preferences or a configurable workflow. Each invocation
states the non-default choices it uses.

## 25. Minimal product architecture

Release 1 is one standalone repository and installation containing:

| Component | Failure it prevents |
|---|---|
| Editable role Markdown | Hidden or uneditable method wording |
| One standard-library fixed runner | Reordered prompts, stage drift, bad counters, and unreliable extraction |
| One canonical `RUN.md` per invocation | Lost answers, review reasoning, or recovery point |
| One Format 2 Bridge adapter | Vendor-CLI transport rebuilt inside Gear |
| Codex and Claude native adapters | Reuse of the live conversation, hidden engine switching, or altered role text |
| Thin Codex and Claude skill entries | Host-specific invocation without copying the review method or runner |
| Three public entries | Gear 3, Gear 4, and validator accidentally blended or auto-selected |
| Validator role and output Markdown | Hidden validation standard or model-chosen result shape |

The data flow is fixed:

    initiating host → installed command + selected native engine
      → exact user material
      → runner + RUN.md
      → one fresh native or Bridge role call
      → exact stage artifact recorded
      → next hard-coded stage
      → complete answer + separate status

The Gear runner has exactly two graphs. Validator has one separate fixed
external-call path, not a third review graph. Neither loads a workflow
definition, stage graph, plugin registry, policy table, or routing
configuration.

A run directory contains `RUN.md` and only temporary files required for atomic
replacement. One writer holds the run. The record snapshots instructions,
protects block digests, and never overwrites a valid completed stage. Corrupt or
ambiguous state is reported, not guessed. Release 1 does not reconstruct and
resume an interrupted graph; the durable record preserves the work for a new
run. Temporary files are removed when the run ends.

A host skill only captures exact input, presents the supported engine choices,
invokes the installed command in the foreground, and keeps standard output
separate from status. It does not copy role text, own counters, interpret
verdicts, or keep another state file. The Claude skill explicitly supplies
`--native claude`; a caller selects Fable rather than the skill choosing it.

A target-only harness needs no Gear skill. A Bridge connector proves only that
the harness can receive a peer packet; it does not make that harness a native
Gear engine.

## 26. Maintained release sequence

Release and update work preserves the exact-input, fixed-graph, record, and
answer/status contracts; exercises both native adapters and Bridge with bounded
fake executables; independently reviews implementation, Markdown, entries,
documentation, and legal/package contents; and discloses which live engines,
models, peers, and platforms were actually exercised. The released package
contains only the three commands, two Gear graphs, external-only Validator,
thin host entries, CC0 legal text, and required runtime files.

An engine addition uses the one-call adapter boundary without changing role
ownership or Validator; a target addition remains Bridge work. Rollback restores
the prior Git/package version while preserving user-owned run records.

## 27. Focused acceptance and release contract

The complete product test budget is eight material checks:

1. **Exact text:** whitespace, Unicode, Markdown, boundary-shaped text, and
   strict-form fixtures prove byte preservation, collision/malformed-boundary
   handling, and answer/status separation.
2. **Gear 3:** scripted PASS, one-pass revision, consensus/cap, role ownership,
   call ceilings, and complete-answer recovery.
3. **Gear 4:** blind lanes, reciprocal posture, conditional revision, valid
   two-lane consolidation, final review, lane recovery, valid `NOT PASSED`
   propagation, and labelled Gear 3 fallback.
4. **Adapter parity:** one exact packet crosses Codex, Claude, and Format 2;
   readiness failure, next action, selected-native recovery, and uncertain
   publication are preserved.
5. **Native mechanics:** fake executables prove fresh temporary context, exact
   input/result, restricted effects, cleanup, no unselected launch, retained
   engine/model, and Claude subscription arguments plus exact attribution.
6. **Representative live behavior:** Gear 3 and Gear 4 together show reasoned
   findings, overlooked considerations, Depth/Breadth complementarity,
   revision, consolidation, and clean delivery; rare failures remain fixtures.
7. **Boundary inspection:** confirm Markdown substance, mechanical Python, two
   fixed graphs, two native engines, and no router, configurable workflow,
   persistence service, Git authority, live Ora/Loop dependency, or Bridge edit.
8. **Validator:** prove strict multi-root decisions, fields, provenance/digests,
   one protected external call, no native fallback, empty failure stdout, and a
   run record. One live ZCode multi-root qualification is sufficient.

Do not rerun Bridge's connector suite; one representative external Gear
integration is enough. Report live provider/model checks separately.

Independent review may reject only a material defect: wrong or missing output,
protected-content loss or misattribution, broken blindness, a false PASS or
hidden failure, loss of an available complete answer, execution beyond the cap,
an unauthorized external effect, or contradiction with this contract. It may
not demand polish, helper tests, generalized compatibility, broader model
coverage, or another tracker.

Release only the reviewed implementation and instruction snapshot. State which
native engines, models, initiating hosts, platforms, and Bridge release were
actually qualified; portability is not a claim of universal installed support.
Fake executables exercised Claude exact input/result, restrictions, subscription
environment, Fable retention, attribution, recovery, and cleanup. No live Claude
or Fable model call was made. Rollback restores Git/package state without
deleting user-owned run records.

Completion requires both Gear graphs, Validator's one-call external contract,
both native adapters' focused checks, semantic review of exact role Markdown,
truthful route/status/attribution, and cleanup. First-party release files use
CC0 1.0 Universal; separately installed CLIs and Bridge keep their own terms.
