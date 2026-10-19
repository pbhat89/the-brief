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
