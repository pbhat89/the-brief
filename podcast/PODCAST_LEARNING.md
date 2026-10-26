# Podcast learning ledger and pure helpers

The initial 19 October 2026 seed contains the three most recent original Big Technology episodes verified that day. At initialization all were pending: transcript access was observed, but full archive/story dedup review still needed completion. Consult the evolving ledger for current state. Podscripts is recorded as third-party transcription, not publisher-approved text; source discovery alone never marks an episode covered.

Run from the repository root:

    node podcast/validate-podcast-learning.mjs
    node --test podcast/validate-podcast-learning.test.mjs

The behavior tests use an immutable synthetic fixture. Only structural validation reads the evolving production ledger.

## Exports

- validatePodcastLearningLedger(ledger): error strings; an empty array means structural/state checks passed, not that editorial/source truth has been verified.
- selectPodcastLearning(ledger, context): read-only selection returning episode_id (or null), reason, and the selected episode record when applicable.
- recordPodcastState(ledger, {episode_id, status, reason, recorded_at}): returns a new ledger. Status is pending, deferred, or skip. Deferred/skip require a reason. Published state cannot be set here.
- recordPodcastPublication(ledger, context, evidence): reselects under current facts and returns a new ledger only if the verified live publication matches the selected episode. A second recap on the same SGT date, even through another show or revision, is rejected. Exact retries are idempotent.
- canonicalPodcastIdentity(value): canonicalizes known YouTube and Apple URL variants to episode IDs, and removes generic tracking parameters.
- sgtDate(ISO timestamp): returns the calendar date in Asia/Singapore.

No helper fetches, publishes, or writes files. The caller must persist the returned ledger atomically and serialize concurrent runs around load/select/publish/record; a pure helper cannot prevent two separate processes from publishing against the same old snapshot. Never publish until the daily slot is reserved by the single publication workflow. Do not assume passing validation authorizes publication.

## Selection context

Provide date_sgt (YYYY-MM-DD), as_of (ISO timestamp with timezone), primary_check, fallback_check, and candidates (complete episode-shaped records of newly discovered episodes or fresh evidence for known records).

primary_check must have status complete or inaccessible, plus checked_at on the current SGT date. inaccessible also needs a reason. A source check must represent the actual newest publisher-feed review, not a search-index timestamp. fallback_check has status complete and current checked_at; it is needed before choosing Big Technology. Missing fallback evidence safely yields no recap.

The current feed snapshot must include the latest qualifying original, including already-covered ones, so latest-only selection cannot mistake an older unseen candidate for latest. Candidate aliases resolve against the ledger; a known episode preserves its canonical RSS publication date/title/source and existing state. Do not supply title strings alone as identity aliases. Provide RSS, Apple, YouTube and exact episode/transcript URLs as appropriate.

Before selecting, refresh the chosen candidates' transcript.checked_at, actual body_retrieved and provenance. Transcript status retrieved requires a real body, HTTPS source_url, and provenance publisher-transcript, official-channel-captions, or third-party-transcription. Caption metadata, descriptions and snippets do not suffice.

Complete dedup_review with status clear or distinct_contribution, nonempty story_keys, and reviewed_at on the current SGT date. distinct_contribution also needs a concrete contribution. pending or duplicate reviews cannot be selected. This judgment must reconcile existing report/podcast history and today's stories. Automated structure checks cannot determine semantic duplication.

Everyday AI has precedence: choose the newest unseen qualifying original among those with readable transcripts and reviewed distinct value. An inaccessible newest upload does not displace another eligible unseen primary episode. Its Start Here/Get Started Here beginner series, replays, promotions and non-substantive content are excluded. Substantive technical/how-to Big Technology learning remains eligible.

Catch-up uses the frozen three-episode seed newest first on fallback days; blocked candidates stay pending/deferred and the next seed may be selected. After all seeds are published or explicitly skipped, latest-only considers the most recent qualifying original before coverage/readability checks. It never backfills older unseen episodes. Record deferred/skip reasons explicitly; discovery/drafting never marks coverage.

## Publication evidence

Require publication_id, canonical episode_id, status verified_published, output_url (a public pbhat89.github.io/the-brief/archive or podcast/reports HTML page matching the edition date, without query or fragment), revision, content_sha256 (64 lowercase hexadecimal characters), verified_at, and confirmation describing the actual live-output check. verified_at must follow the selection time. Candidate and publication writes use explicit public-field allowlists; raw receipts, private listener URLs and transcript bodies are discarded rather than persisted. Existing public ledger records reject unknown fields. The helper adds date_sgt/show and links the episode state to this evidence. Failed delivery, drafts, commits and upload acknowledgments alone do not qualify.

One SGT date refers to the brief edition date, not UTC date or a new revision ID. Revisions reuse the same selected episode; they must not record another recap. This helper allows an exact retry of the same evidence, but intentionally does not update a published entry to different evidence. Any future publication-evidence revision workflow must preserve the date and canonical episode lock.

## Initial source evidence and transcription limits

The [initial source review](big-technology-source-review.json) records publisher RSS GUIDs, exact UTC publication dates, Apple and YouTube identities, transcript access and aliases. The canonical publisher feed is https://feeds.megaphone.fm/LI3617121267. Seed dates are 16, 15 and 9 October 2026, newest first. The Kevin Roose interview's alternate video/transcript title is the same conversation; preserve it as an alias, never a fourth episode. Refresh the live feed and original dates on each run; index crawl or reupload dates are not publication dates.

The public Podscripts bodies were retrievable from intro through sign-off during initialization. They contain automatic-transcription errors and are not publisher-approved or verbatim-perfect. Official-channel caption metadata was present for two aliases, but caption downloads returned empty bodies; do not claim those captions were read. Prefer readable publisher transcripts or official captions when available. Verify consequential names, numbers and factual claims against original sources, distinguishing a speaker's opinion or allegation from established fact. Omit ads and unsupported claims. Describe old catch-up episodes by their real release date. Never infer recap content from titles/descriptions or copy raw transcripts into this public repository.

The required prepublication command is `node podcast/validate-editorial.mjs --audit /absolute/private/audit.json`. A recap's private audit must include `podcast_selection_context` with the fields above, and canonical `episode_key`, display `show`, `transcript_source_url` and `transcript_provenance` in `podcast_recaps`. The CLI checks selection against the current ledger, then verifies the exact transcript source/provenance. Perform semantic and source review before setting readiness fields; these checks do not certify source truth. Record successful public coverage only after verified publication and final delivery reconciliation, then persist the sanitized ledger using a fresh repository revision.

## Coverage reconciliation, 21 October 2026

The fixed catch-up queue’s second episode, Kevin Roose’s original 15 October conversation, was published and included in the accepted combined delivery for 21 October. The distinct recap concerns shared conviction and organisational alignment, explicitly treating Roose’s view as interpretation and separating an illustrative business application. The third-party transcript provenance and limitations remain recorded. The newer Sundar Pichai original, published 20 October at 17:18 UTC, remains pending and unsummarized; the fixed three-episode seed has not been changed. Publication evidence is in the sanitized ledger, without private playback or delivery references.


## Coverage reconciliation, 22 October 2026

The fixed catch-up queue's third original, published 9 October at 16:51 UTC, was included in the accepted combined edition. The selected actual transcript at 30:01–32:54 concerns general-purpose assistants versus workflow specialization; the business example was explicitly editorial. Third-party transcription caveats remain. The three-item seed is unchanged and now completed. The newer Pichai original remains pending and unsummarized; subsequent selection must check for newly released unseen qualifying originals, not re-seed the catch-up queue.


## Coverage reconciliation, 23 October 2026

After the unchanged three-episode seed was completed, the latest-only check selected Sundar Pichai's original 20 October episode (17:18 UTC). The actual third-party transcript at 16:54–22:52 supports the recap on compute allocation, capacity lead times and demand uncertainty. The document-processing capacity example is editorial, not a Pichai claim; transcription limitations remain. Everyday AI's current qualifying original and transcript could not be established, so Big Technology was used without claiming exhaustive source coverage. The recap was included in the verified, accepted combined edition: [public report](https://pbhat89.github.io/the-brief/podcast/reports/2026-10-23.html). Earlier episodes and the fixed seed are preserved.


## Coverage reconciliation, 25 October 2026

The latest qualifying Big Technology original, published 23 October at 22:12 UTC, now had an accessible actual third-party transcript. The distinct 56:39–57:39 recap covers forgotten event websites, retained data and digital-asset lifecycle responsibility; the webinar application is editorial and CIS asset-inventory guidance independently supports the principle. No previous PHP incident statistics or Pichai compute-allocation lesson were repeated. The recap was included in the verified, accepted [combined edition](https://pbhat89.github.io/the-brief/podcast/reports/2026-10-25.html). The fixed three-episode seed, older published episodes and historical gaps remain unchanged.

### Required learning-source discovery surfaces

Before selecting a recap, attempt both the Big Technology publisher RSS and its official YouTube page at https://www.youtube.com/@Alex.kantrowitz as separate source-checklist rows, alongside all six Everyday AI surfaces. RSS is not a substitute for the channel-page attempt. Preserve actual attempt times, access gaps, original/upload dates and transcript provenance; do not mark listing-only or inaccessible episodes covered. See `SOURCE_COVERAGE.md` for the post-delivery inventory correction.

## 27 October 2026 · Confirmed use

The new Big Technology original of 26 October at 17:09 UTC was selected after separately attempting publisher RSS and the official YouTube page. The actual third-party transcript at 13:57–15:44 supports the distinct explanation of customer concentration versus distribution-channel dependence, not a repeat of the IPO headline. Automatic-transcription limitations remain; uncertain names and numbers were omitted. Verified publication and accepted combined delivery establish this use. All previous coverage and the completed, fixed three-episode seed remain unchanged.
