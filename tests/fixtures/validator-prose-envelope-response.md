Synthetic framing outside the bounded payload appears before the marker. It is harmless narrative text and must not become part of the parsed decision body.

<<<ORA-VALIDATION-BEGIN:validation-synthetic-prose-envelope-001>>>
## sample-alpha — ACCEPT

### BEHAVIOR
In this fictional scenario, the alpha root receives three invented records labelled Amber, Birch, and Cedar. The described result keeps their supplied spelling, punctuation, and sequence intact while normalizing only the deliberately irregular spaces between fields. A repeated display label remains repeated because labels are ordinary data, not an implied instruction to merge two records. The expected outcome is therefore a stable three-record sequence whose visible content can be compared without relying on any unstated environment.

### MECHANISM
The hypothetical mechanism reads each sample record into a temporary in-memory list, trims the declared separator padding, and emits the list in its original order. It never treats prose before or after the supplied boundary as input. It also keeps record identity separate from display text, so two records may share a label without becoming the same record. This account is intentionally self-contained: names, values, and transformations exist only to make the fixture long enough to exercise realistic multi-paragraph parsing.

### EVIDENCE
The synthetic evidence table contains input pairs A-01/Amber, A-02/Birch, and A-03/Cedar and an invented expected-output table containing those same pairs in the same order. A fictional comparison reports three matches, zero omissions, and zero additions. These statements describe fixture data only; no repository, command, service, person, or actual execution is represented, and no external result is being offered as proof of a real implementation.

### LIMITATIONS
The example does not claim that a real parser performed normalization, that any storage layer retained the records, or that the invented comparison was executed. It covers ordering, preservation, and duplicate display labels but says nothing about scale, concurrency, localization, or recovery after interruption. Those omissions are deliberate because this root exists solely as neutral structured prose inside the parser envelope.

## sample-bravo — REJECT

### BEHAVIOR
The bravo root describes a made-up reconciliation rule for four colored cards. The promised behavior is to retain both cards when their colors match but their serial tokens differ. In the fictional observed table, cards Blue-B7 and Blue-B8 are incorrectly collapsed into one row. The decision is REJECT because the described output loses a distinct sample item, even though the total color count still looks plausible at a glance.

### MECHANISM
The imaginary implementation groups cards by color alone before assigning output rows. That grouping key is too broad for the stated example because color is a presentation property and the serial token is the actual identity. A safe fictional correction would group by serial token and carry color as an attribute. This explanation is detailed enough to resemble a substantive root decision while remaining unrelated to any actual application, codebase, organization, or event.

### EVIDENCE
Synthetic input rows B-01/Blue-B7, B-02/Blue-B8, B-03/Gold-G2, and B-04/Green-G4 are paired with an invented result containing only three rows. The fixture narrative declares that the second blue card is absent and that the other three records are unchanged. No files were opened and no checks were run; the mismatch is part of the authored example and exists only to give the parser a negative decision among positive ones.

### LIMITATIONS
Because the reconciliation is fictional, the rejection does not diagnose an actual defect or recommend work on a real product. It does not explore malformed serial tokens, empty colors, partial updates, or retry behavior. The only intended semantic signal is that one exact root heading carries REJECT while its four required fields remain ordinary non-empty prose and stay within the supplied markers.

## sample-charlie — ACCEPT

### BEHAVIOR
The charlie root uses an invented timetable with Morning, Midday, and Evening entries. The sample result orders them by the explicit numeric position attached to each entry rather than alphabetically by the display name. When two descriptions contain the word Morning, both remain present and their numeric positions decide placement. The accepted behavior demonstrates that readable prose can include repeated ordinary words without creating extra structural sections.

### MECHANISM
In the hypothetical flow, each entry is paired with a small integer, the pairs are sorted by that integer, and the descriptions are copied without reinterpretation. Only exact level-two root headings and the four exact level-three field headings have structural meaning. Words such as result, decision, evidence, or status appear within sentences as plain content and do not become separate verdicts. The imagined flow has no dependencies and names no concrete software.

### EVIDENCE
The fabricated source list places Evening at position 3, Morning at position 1, and Midday at position 2. Its fabricated expected list is Morning, Midday, Evening, and the stated comparison finds that order exactly. A second invented row uses Morning notes at positions 4 and 5 to show that repeated prose survives. This is illustrative fixture material, not an account of a test run, inspection, release, or customer record.

### LIMITATIONS
The example assumes unique numeric positions and does not define what would happen if two entries shared a position or omitted it. It also avoids dates, time zones, calendars, and locale-specific sorting because those details would add domain meaning without improving the parser boundary case. Acceptance applies only to the coherent fictional facts stated in this root and conveys nothing about a real system.

## sample-delta — ACCEPT

### BEHAVIOR
The delta root describes a pretend round trip for a small bundle of text fragments. The expected result preserves blank lines inside each fragment, keeps a literal em dash as text, and leaves a harmless sentence containing the words accept and reject in lowercase unchanged. The bundle returns with the same fragment count and order. The decision is positive because every invented comparison in this section agrees with the explicitly stated expectation.

### MECHANISM
The synthetic mechanism assigns each fragment an opaque token, carries its text as an uninterpreted value, and reconstructs the ordered bundle from those tokens. It recognizes structure only at the outer marker and exact heading lines, so punctuation embedded in a paragraph remains data. The design is described abstractly and intentionally omits language names, libraries, storage locations, and machine details; none are needed to exercise extraction of a long decision body.

### EVIDENCE
Fixture fragment D-01 contains two paragraphs, D-02 contains the sentence “the words accept and reject are examples,” and D-03 contains an em dash between two invented labels. A fictional before-and-after table lists equal character sequences for all three fragments and an unchanged order D-01, D-02, D-03. The table is authored sample content and does not claim that any operation occurred.

### LIMITATIONS
The round trip does not cover binary input, mixed newline conventions, extremely large values, or invalid character sequences. It does not establish durability or error recovery. Those are outside the fixture’s neutral purpose. The accepted decision simply supplies another complete root with prose rich enough to guard against accidental truncation while using only invented labels and facts.

## sample-echo — REJECT

### BEHAVIOR
The echo root presents a fictional summary made from five numbered tokens. The stated requirement is to report every token exactly once and to place an explicit neutral placeholder beside any token whose description is absent. The invented output skips token E-04 instead of showing its placeholder. The section is rejected because omission changes the visible set and prevents a reader from distinguishing missing sample data from an accidentally dropped record.

### MECHANISM
The imagined summarizer filters out entries with empty descriptions before rendering, so the renderer never receives E-04. That sequence contradicts the fictional requirement, which calls for rendering first and substituting a placeholder only for the absent description. The mechanism description uses no real identifiers or implementation details. It exists to ensure a later negative decision remains separate from the earlier bravo rejection and is returned in the authored root order.

### EVIDENCE
The synthetic input enumerates E-01 through E-05 and marks only E-04 as lacking a description. The synthetic output enumeration contains E-01, E-02, E-03, and E-05. The fixture therefore supplies an explicit, internally consistent reason for the negative heading without asserting that any program produced those rows. No actual output, external call, or historical observation is embedded here.

### LIMITATIONS
The example does not say how a placeholder should be localized, styled, or exported, and it does not address multiple absent descriptions. It cannot support conclusions about production data loss because there is no production data. Its sole regression role is to keep a second REJECT decision, with complete required fields, inside a long mixed-decision response whose surrounding prose is excluded.

## sample-foxtrot — ACCEPT

### BEHAVIOR
The foxtrot root closes the fictional set with a digest of the five earlier sample outcomes plus one independent checksum label. The described digest preserves the requested root sequence, records each decision word exactly as authored in its heading, and does not manufacture an aggregate verdict. A reader can recover six separate root decisions without treating this final section as a summary that overrides them. That behavior matches the fixture’s intended ordered extraction contract.

### MECHANISM
The hypothetical collector appends one structured item whenever it encounters a complete root section, then returns the items in encounter order. It verifies membership against the supplied neutral root list and refuses to infer missing items from surrounding narrative. The final checksum label is ordinary prose with no certification meaning. Although the paragraph resembles a design explanation, every element is invented specifically for this fixture and names no actual component or provider.

### EVIDENCE
An authored sample list gives the ordered pairs sample-alpha/ACCEPT, sample-bravo/REJECT, sample-charlie/ACCEPT, sample-delta/ACCEPT, sample-echo/REJECT, and sample-foxtrot/ACCEPT. The expected extraction repeats those six pairs exactly. This list is the fixture’s own synthetic reference; it is not a report from a model, reviewer, command, repository, or release process, and every described observation is invented.

### LIMITATIONS
The final sample does not prove behavior for duplicate roots, unexpected roots, missing fields, foreign markers, or verdict-like text outside the boundary; separate cases may cover such malformed inputs. It intentionally exercises only a well-formed, long, multi-root response with mixed decisions and harmless outer prose. The neutral examples should be read as parser data and nothing more.
<<<ORA-VALIDATION-END:validation-synthetic-prose-envelope-001>>>

Synthetic framing outside the bounded payload appears after the marker. It remains harmless narrative text and must also stay outside the parsed decision body.
