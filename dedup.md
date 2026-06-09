# Deduplication Specification

This document defines how the daily routine reads `/archive` and excludes repeats from the last 2-3 days. It is referenced by `routine-prompt.md` (Stage 0) and enforced by `verifier-checklist.md`.

## 1. Goal

Every day's brief contains only genuinely new developments. If a topic was already covered in the last 2-3 days, it must not appear again unless there is a material new fact — in which case the item leads with that new fact and is prefixed `Update:`. The reader must never feel they are reading yesterday's brief again.

## 2. Inputs Read at Stage 0

The routine loads the following from `/archive`, in this order of preference:

1. **`archive/INDEX.md`** — primary fast-path. A tab-separated running log. Parse all rows whose date falls within the last 3 calendar days (Asia/Singapore).
2. **`archive/YYYY-MM-DD.json`** — for each of the last 2-3 days, read the structured items. Provides the richer fields (`key-entities`, `fun-fact-id`, `puzzle-type`) needed for fuzzy matching.
3. **`archive/USED.json`** — the rolling fun-fact / puzzle ledger. This is the LONG-window memory: `funfact_topics` (last 60 days) and `puzzle_log` (last 30 days). The per-day JSON files only cover the last 2-3 days, which is far too short for topic-based fun-fact dedup — `USED.json` is what makes the 30-day fun-fact rule and the 30-day puzzle-title rule actually work. Read it at Stage 0; write it at Stage 4b every run. Schema and write rules: §7, §8, §9.
4. **`archive/YYYY-MM-DD.html`** — not read by the routine. Rendered artifact only.

Fallback rules:
- If `INDEX.md` is missing or malformed, fall back to reading the JSON files directly and rebuilding the in-memory index.
- If both `INDEX.md` and the JSON files are missing for the relevant window, treat the EXCLUDE set as empty and proceed (this is normal on first run).
- If a single JSON file is malformed, skip it and continue with the remaining days; log a warning.

## 3. The EXCLUDE Set

The EXCLUDE set is the union of signals from the last 2-3 days, partitioned by item kind:

- **Stories** — union of all `short-hash` values, plus a "soft" set of `(key-entities, event)` tuples for entity-based matching when hashes don't match but the story is clearly the same. Window: last 2-3 days (from `INDEX.md` / per-day JSON).
- **Fun facts** — set of `topic_key` values from `USED.json.funfact_topics` dated within the last **30 days** (see §7).
- **Puzzles** — set of `type` values from the last **4 days** plus `title_key` values from the last **30 days**, both from `USED.json.puzzle_log` (see §8).

The STORY window is 2-3 days: always include yesterday and the day before; include 3 days back when the topical density warrants it (e.g., a multi-day rolling story like an election or trial). Default story window is 3 days. The fun-fact and puzzle windows are the longer 30/4-day windows above, which is why they are tracked in `USED.json` rather than only the per-day files.

## 4. The `short-hash` Algorithm

Deterministic across runs. The procedure:

1. Lowercase the headline.
2. Strip punctuation (anything not `[a-z0-9 ]`).
3. Collapse runs of whitespace to a single space; trim leading/trailing whitespace.
4. Remove common stop-words at the START only: `a`, `an`, `the`.
5. Compute SHA-1 hex of the resulting string.
6. Take the first 8 hex characters.

```text
Input:    "India's Budget Passes 5-3"
Step 1:   "india's budget passes 5-3"
Step 2:   "indias budget passes 53"
Step 3:   "indias budget passes 53"
Step 4:   "indias budget passes 53"   (no leading stop-word)
Step 5:   sha1("indias budget passes 53") = "a3f9c2e8b1d7..."
Step 6:   "a3f9c2e8"
```

Notes:
- Stop-word stripping is START-only. "The" inside a headline (e.g., "Senate blocks the bill") is preserved so distinct headlines don't collide.
- Numerals are preserved (the `5-3` becomes `53` after punctuation strip — they remain part of the signal).
- The 8-character prefix gives ~4 billion buckets; collision risk over a 3-day window with ~30 items is negligible.

## 5. The `key-entities` Field

A comma-separated list of the 2-4 most salient named entities in the story. Entities are people, organizations, places, or named events (bills, treaties, summits).

```text
Headline: "India's Lok Sabha passes data protection bill 287-152"
key-entities: ["Lok Sabha", "India", "data protection bill"]
```

Matching rules:
- Case-insensitive.
- Whitespace-normalized.
- Common-sense aliasing: `"PM Modi"` matches `"Narendra Modi"`, `"US"` matches `"United States"`, `"SCOTUS"` matches `"Supreme Court"`. The routine maintains an inline alias map for the top ~50 recurring entities.
- Entities are compared as a set, not a sequence.

## 6. The Repeat Decision

Given a candidate item from today's research, apply this decision tree:

```text
a) Compute short-hash of candidate headline.
   If hash is in EXCLUDE set                   -> REPEAT (go to material-new-fact check)

b) Else compute key-entities set of candidate.
   For each prior item in the last 2-3 days:
     If shared_entities >= 2
        AND same event (same outcome / same action)
        -> REPEAT (go to material-new-fact check)

c) Else                                         -> NEW. Include as-is.
```

When an item is flagged REPEAT, check for a **material new development**:

- **New named outcome** — e.g., yesterday a bill passed the lower house; today the President signed it.
- **New named actor** — e.g., yesterday a Minister responded; today the PM responded.
- **Significant new number** — e.g., death toll up by 10+; vote count finalized; revised GDP figure.
- **Reversal** — yesterday's "approved" became today's "blocked"; yesterday's "ceasefire" became today's "collapsed".

Decision:
- If a material new development exists -> **INCLUDE**, but the summary leads with the new fact, the headline reflects the new development (not the original story), and the item is prefixed `Update:` in the rendered brief.
- If no material new development -> **DROP**.

The `≥2 shared entities` threshold is intentionally moderate. Lower (≥1) would over-suppress unrelated stories that happen to share a country or a politician. Higher (≥3) would let near-duplicates slip through when stories naturally surface only 2 strong entities. When in doubt, the verifier prefers DROP over duplicate.

## 7. Fun Fact Dedup — TOPIC-based over 30 days

The old rule (exact `fun-fact-id` text-hash over 2-3 days) was too weak: the same fact reworded, or a different fact about the same subject, slipped through within days. Dedup is now **topic-based over a 30-day window**, backed by `archive/USED.json`.

**`topic_key`.** The normalized main SUBJECT of the fact: lowercase, singular, articles (`a`/`an`/`the`) stripped. Examples:
- "octopuses have three hearts" → `octopus`
- "the Eiffel Tower grows taller in summer" → `eiffel tower`
- "honey never spoils" → `honey`

**Rules:**
- **HARD RULE:** do NOT use a fun fact whose `topic_key` appears in `USED.json.funfact_topics` within the last **30 days**, even if the wording is entirely different. The subject is the dedup unit, not the sentence.
- If the first candidate collides, generate another and retry — up to **10 times**.
- If 10 candidates still collide, deliberately switch to a different category and draw from it. Rotate categories across: `space`, `biology`, `history`, `language`, `food`, `math`, `geography`, `human body`, `tech`.
- Still require the fact to be verifiable against at least two reputable sources (see `verifier-checklist.md`); listicle / "amazing facts" sites are not acceptable.
- A coarse one-word `topic` is also recorded in the per-day JSON for a soft secondary rotation signal, but the 30-day `topic_key` check in `USED.json` is the binding constraint.

## 8. Puzzle Dedup

Puzzle TYPE rotates across: `visual`, `logic`, `quantitative`, `lateral`. Backed by `archive/USED.json.puzzle_log`.

**`title_key`.** The puzzle title normalized: lowercase, kebab-case, articles stripped (e.g. "Two Trains and a Bird" → `two-trains-and-a-bird`).

**Rules:**
- **Type:** today's `type` must NOT equal any `type` used in the last **4 days** (`USED.json.puzzle_log`). This guarantees a rotation tighter than "not two-in-a-row".
- **Title:** today's `title_key` must NOT appear in `USED.json.puzzle_log` within the last **30 days**, regardless of type. If it collides, pick a different puzzle.
- Beyond those hard rules, prefer types not seen recently when a free choice exists.

## 9. Writing the Archive After the Run

At the end of the daily routine, write three artifacts under `/archive`:

1. **`archive/INDEX.md`** — append one tab-separated row per included item:

   ```text
   YYYY-MM-DD<TAB>headline<TAB>short-hash<TAB>comma,separated,entities
   ```

   Example row:

   ```text
   2026-06-05	Lok Sabha passes data protection bill 287-152	a3f9c2e8	Lok Sabha,India,data protection bill
   ```

   Rules:
   - One row per story item. Fun facts and puzzles are not written to `INDEX.md`; they live in the JSON.
   - The file is append-only. Never rewrite prior rows.
   - Headlines containing literal tabs must have them replaced with a single space before writing.

2. **`archive/YYYY-MM-DD.json`** — the full structured payload for today. One file per day. The canonical schema is defined in `routine-prompt.md` Stage 4b; the abbreviated shape below shows only the fields dedup actually reads:

   ```json
   {
     "date": "YYYY-MM-DD",
     "items": [
       {
         "tab": "Singapore | India | Global | Tech & AI | Business & Markets | Sports",
         "headline": "...",
         "short_hash": "a3f9c2e8",
         "key_entities": ["..."],
         "is_update": false
       }
     ],
     "fun_fact": { "fun_fact_id": "funfact-b7e1d4c0", "topic": "space" },
     "puzzle": { "type": "logic", "puzzle_hash": "c2d3e4f5" }
   }
   ```

   Key naming uses snake_case throughout the JSON, matching `routine-prompt.md`. Tab names match the rendered template exactly.

3. **`archive/YYYY-MM-DD.html`** — the rendered brief, produced from `template.html`.

4. **`archive/USED.json`** — the rolling fun-fact / puzzle ledger. Load the existing file (or start `{ "funfact_topics": [], "puzzle_log": [] }`), then:

   ```json
   {
     "funfact_topics": [ { "date": "YYYY-MM-DD", "topic_key": "octopus", "text": "Octopuses have three hearts." } ],
     "puzzle_log":     [ { "date": "YYYY-MM-DD", "type": "logic", "title_key": "two-trains-and-a-bird" } ]
   }
   ```

   Rules:
   - Append today's fun-fact entry to `funfact_topics` and today's puzzle entry to `puzzle_log`.
   - Prune `funfact_topics` to the last **60 days** and `puzzle_log` to the last **30 days** (relative to today's SGT date). The 60-day fun-fact retention gives headroom above the 30-day enforcement window so an edge-of-window topic is never lost early.
   - This file IS committed (it is the dedup memory; do not gitignore it).
   - On a skipped day, write no fun-fact/puzzle entries (none were chosen) but still prune.

All four writes happen atomically at the end of the routine. If any write fails, none are committed (so a partial archive never poisons tomorrow's EXCLUDE set).

## 10. Edge Cases

- **First run (empty archive)** — EXCLUDE set is empty; nothing is a repeat. All items pass through as NEW.
- **Missed days** — if the routine didn't run yesterday, use the most recent 2-3 days available, even if not strictly contiguous. The window is "last 2-3 archive days," not "last 2-3 calendar days." If only one prior day exists, use that one.
- **Time zone** — all "yesterday" / "today" comparisons use **Asia/Singapore** (UTC+8). The date string in filenames and INDEX rows is the Asia/Singapore calendar date at routine start.
- **Routine runs twice in one day** — the second run sees today's own archive file. It must exclude today's date from the EXCLUDE-window computation when reading prior items, or it will treat itself as a repeat. Practically: window = "the N most recent archive days strictly earlier than today's Asia/Singapore date."
- **Malformed entity list** — if `key-entities` is empty or missing for a prior item, that item participates in hash-based matching only; it never contributes to the soft entity-tuple set.
- **Hash collision** — extremely unlikely at 8 hex chars over a 3-day window, but if a candidate's hash matches a prior item's hash AND shares zero entities, treat it as NEW (the hash collision is spurious). This protects against the rare case where two unrelated headlines normalize to the same string.
- **Long-running stories** — for stories that genuinely span many days (elections, trials, wars), the `Update:` prefix is the correct pattern. The headline must change day-over-day to reflect the actual new development; otherwise the verifier (`verifier-checklist.md`) will reject the brief.

## References

- `routine-prompt.md` — Stage 0 invokes this spec to build the EXCLUDE set.
- `verifier-checklist.md` — verifier checks that no included item's `short-hash` is in the prior 2-3 days' set, and that any `Update:`-prefixed item names a concrete new fact in its first sentence.
