# Expert learning log

This is a growing, source-backed bank of useful ideas from Andrej Karpathy, Andrew Ng, Yann LeCun and Naval Ravikant. It supports practical learning about technical coding, the transition to AI, and management. A valuable older idea is eligible even when an expert has no new post. Do not fill this segment with repeated “nothing new” notices or treat it as a breaking-news quota.

## Files and authority

- `expert-learning-log.json`: concepts, original sources and sanitized coverage history.
- `expert-learning-log.schema.json`: portable structural contract.
- `validate-expert-learning.mjs`: dependency-free structural, chronology and usage checks.
- The approved private delivery ledger remains the authority for final script/audio and delivery evidence. This public log contains no personal details, private transcripts, listener URLs, delivery receipts, credentials or sensitive work examples.

The external scheduled assistant must load the log before choosing a lesson and update it after confirmed use. Repository edits do not update a saved automation, and this repository contains no research or narration engine.

## Selection and no-repeat rules

1. Read all existing concepts and aliases, prior public reports and the available private delivery ledger. The initial seed covers only the reports listed in `history.reviewed_reports`; it is not a complete import of past learning.
2. Research the four experts' original essays, letters, talks, research, interviews or posts. Prefer the most useful supported idea, recent or evergreen. Keep the actual original date. A repost, re-upload, newly discovered old link or different expert does not make the idea new.
3. Assign one stable, author-neutral `concept_id` to the underlying lesson. Compare the takeaway and application across every expert, title, source and alias. Add another source/expert to an existing concept rather than creating a new ID for the same lesson. Check near-duplicates manually; URL or string matching cannot establish semantic novelty.
4. A `researched_candidate` has no recorded use. It is not automatically eligible: `pending_full_history` means its comparison with available history is still needed. Change to `reviewed_no_match` only after that check. Keep global history gaps visible; never claim exhaustive deduplication when history is missing. If uncertain whether a concept was used, choose a clearly different concept while resolving the gap.
5. Never select a concept with any prior use as a new lesson. Report coverage conservatively blocks reuse even if audio coverage is unknown. There is no rolling expiry, cooldown, new-expert exemption or new-wording exemption. A related concept is acceptable only when the actual principle and learning outcome are distinct, not because it has a different example. Do not disguise a repeat as a follow-up.
6. In narration, briefly name the expert, give an honest date/era label where relevant, explain the idea, and give one practical takeaway. Clearly separate what the source says from the briefing's application. Avoid fabricated quotes, unsupported performance promises or treating a research hypothesis as established fact. Do not repurpose dated model/optimizer advice as current technical recommendations.
7. Check the whole episode, including the opening and management segment, for a repeated concept. An expert lesson used in the opening still counts as used. Do not force all four experts or a fixed number of concepts into every episode.

## Recording use without false delivery claims

- `researched_candidate`: source was directly checked; `uses` is empty and both last-used fields are null. Researching, selecting or drafting a lesson does not mean it was narrated.
- `covered_in_report`: a published report contains the concept, but narration is unconfirmed. Record a `report` use and leave `last_narrated` null.
- `narrated`: the final delivered podcast is confirmed to contain the concept. Record its Singapore edition date, a `podcast` use and a brief confirmation statement. Source audits establish provenance; they do not by themselves establish audio delivery. Keep detailed private evidence in the approved private ledger.

`last_used` is the most recent confirmed use in either channel. `last_narrated` is the date of confirmed podcast use. Update only after checking the final artifact and delivery outcome; an optional source item, abandoned draft, failed render or unpublished audio does not justify a podcast use. If a public report was published but audio failed, keep the report use and do not invent narration. Keep covered concepts and their uses permanently; never reset them to candidate or delete coverage to make them eligible again. Refresh the latest repository version before writing so concurrent updates are not lost.

Use dates exactly as the publisher provides them. `original_date_basis` records whether the date was read directly or preserved from archived evidence; `checked_on` is separate. `sources[].locator` identifies the relevant section, page or transcript timestamps. For video, verify the original recording/publication identity and the actual accessible transcript rather than relying on a title. Undated or unverifiable new research is not an eligible candidate; resolve the evidence first.

## Seed state on 19 October 2026

Six source-verified evergreen candidates are included: inspect real data; prove a tiny pipeline; build AI capability through pilots/training; understand self-supervision; develop domain knowledge; and own outcomes including failure. They have not been marked narrated, and each still needs a complete available-history comparison before selection.

Two historical concepts are conservatively blocked:

- Naval's long-term-work principle, original post dated 30 September 2026: confirmed narrated on 19 October. The leadership application was editorial interpretation.
- Ng's automatically verifiable tasks versus human judgment, source date recorded as 16 October 2026: present in the 18 October revised report. Narration remains unconfirmed. The original letter returned 403 during this seed pass, so the record preserves the archived evidence and does not imply a fresh primary read.

## Checks

Run from the repository root:

```sh
node podcast/validate-expert-learning.mjs
node --test podcast/validate-expert-learning.test.mjs
```

These checks reject duplicate concept IDs and normalized aliases, missing original-source provenance, contradictory candidate/coverage states, inconsistent dates, repeat podcast uses and obvious private URL patterns. They cannot prove source accuracy, actual narration, absence of personal data, semantic novelty or full historical coverage. Review those editorially. Validate again after every update.

## Source review, 21 October 2026

Re-read LeCun and Misra’s original 4 March 2021 self-supervised-learning article. The hidden-input-prediction concept was compared semantically with available delivered history through 20 October, companion reports and upstream archives. No matching underlying lesson was found; the existing concept is now `reviewed_no_match`, not a new concept or a recorded use. Its source date remains evergreen. Separate the authors’ explanation from the editorial business application, and do not equate general pretraining with validated task performance. Global historical-import gaps remain unchanged. No publication or narration is established by this review.

### Confirmed use, 21 October 2026

Following verified report publication and accepted combined delivery, `self-supervision-from-data-structure` is recorded as narrated on 21 October. The lesson explains hidden-input prediction, separately applying the distinction between broad pretraining and actual-workflow validation. It is no longer an unused candidate. Earlier source review above records the prepublication state; all other concepts and uses remain unchanged.


## Coverage reconciliation, 22 October 2026

Naval Ravikant's evergreen 21 June 2019 accountability lesson was included in the verified, accepted combined edition. The application to outcome ownership and review was explicitly separated from his original claim. The concept is now narrated, not an unused candidate; private delivery references are retained outside this repository.


## Coverage reconciliation, 23 October 2026

Andrej Karpathy's evergreen 25 April 2019 tiny-batch debugging lesson was included in the verified, accepted combined edition: [public report](https://pbhat89.github.io/the-brief/podcast/reports/2026-10-23.html). The lesson distinguishes checking pipeline wiring from proving generalization; the invented-document business application is explicitly editorial. Semantic review found this distinct from the earlier input-inspection lesson, despite sharing an original source. The concept is now narrated, not an unused candidate. All previous concepts, uses and historical coverage gaps remain preserved.


## Research reconciliation, 24 October 2026

At the initial research checkpoint, the specific-knowledge-through-curiosity candidate was checked against the available daily and personal-topic history and retained as a researched candidate, not yet narrated. The confirmed-use entry below supersedes that provisional status. The source's career-interest principle is distinct from prior accountability, long-term habits, and evaluating the reliability of expertise. The AI Transformation Playbook candidate is conservatively blocked: an earlier coverage record references that playbook, and exact lesson-level reconciliation is still pending. No new delivery status or date is asserted by this research update.


## Confirmed use, 24 October 2026

Naval Ravikant's evergreen 25 March 2019 specific-knowledge-through-curiosity lesson was included in the verified, accepted combined edition: [public report](https://pbhat89.github.io/the-brief/podcast/reports/2026-10-24.html). The lesson connects distinctive expertise with genuine curiosity; the operations-analyst example and AI application are explicitly editorial. Only this concept is now recorded as narrated. All earlier concepts, source reviews and history gaps are preserved. No podcast recap was delivered, and no podcast coverage state or fixed catch-up seed is changed by this reconciliation.


## Confirmed use, 25 October 2026

Karpathy’s evergreen 25 April 2019 explanation of random versus grid search was included in the verified, accepted combined edition: [public report](https://pbhat89.github.io/the-brief/podcast/reports/2026-10-25.html). The lesson concerns unequal importance of model settings and a limited experiment budget, not the previously covered input-inspection or tiny-pipeline checks. The nine-trial example and business application are editorial; no universal superiority claim is made. Only this new concept gains a narrated use; prior concepts and history gaps are preserved.

### 26 October 2026 · Confirmed use

Andrew Ng’s evergreen workflow trace-localisation lesson (source dated 22 October 2025; `agent-trace-failure-localisation`) was narrated and delivered after verified publication. The document-assistant application is editorial. Direct page access failed; indexed primary publisher text supplied the evidence. The machine ledger now records confirmed use, not a pending candidate.

## 27 October 2026 · Confirmed use

Naval’s evergreen 31 March 2019 complementary building-and-communication lesson was included in the verified, accepted combined edition. The AI-prototype explanation is explicitly editorial. Only this concept gains a narrated use; all previous entries and history gaps remain preserved.

## 28 October 2026 · Confirmed use

Karpathy’s evergreen 25 April 2019 human-baseline and annotation-consistency lesson was included in the verified, accepted combined edition. The customer-message classification exercise is an editorial application, not a quotation or a performance ceiling. Only this concept gains a narrated use; all prior concepts and historical gaps remain preserved.


## 29 October 2026 · Confirmed use after late notification

The existing verified morning edition containing Naval’s evergreen judgment-and-leverage lesson received an accepted combined notification later the same Singapore date. The concept is now narrated; the AI safeguards remain an explicitly editorial application. No audio was regenerated and no source window or earlier use was changed.

## 30 October 2026 · Confirmed use

Karpathy’s evergreen 25 April 2019 input-independent baseline lesson was included in the verified, accepted combined edition. The support-message class-imbalance example and minority-case review are editorial applications. This is distinct from previously covered human-label calibration, tiny-batch wiring and raw-input inspection. Only this confirmed concept advances; earlier coverage and history gaps remain preserved.


## 31 October 2026 · Confirmed use

Yann LeCun and coauthors’ evergreen 2023 I-JEPA representation-target lesson was included in the verified, accepted combined edition: [public report](https://pbhat89.github.io/the-brief/podcast/reports/2026-10-31.html). The lesson explains predicting learned image representations rather than exact pixels; the dog-behind-a-fence analogy and downstream-task question are explicitly editorial. This is distinct from the earlier lesson on where self-supervised training signals come from. Only this concept gains a narrated use. No inaccessible podcast original is marked delivered; all earlier uses and historical coverage gaps remain preserved.
