# Morning podcast companion

This bounded companion extends The Brief without replacing the existing Claude routine, general-news archive, templates, watchdog, recipients or Gmail draft sender. No new scheduler is installed here. The requested external companion start is now 07:45 Asia/Singapore; configuration is handled outside this repo. The original Claude schedule and Gmail workflow are unchanged.

## Operator sequence and deadline

The requested daily start is **07:45 Asia/Singapore**, after the same-day Claude HTML is expected. At start, record a new run ID and timestamped status; read prior delivery ledgers and the archive index, and verify the same-day upstream HTML/JSON before selecting stories. Keep upstream claims subject to freshness, primary-source and repeat checks.

Use a bounded five-minute intake window, through 07:50 SGT on a normal run. If the same-day upstream is unavailable, disclose availability and independently verify current headlines; never present yesterday's brief as today's. Do not wait indefinitely. The refreshed 18 October edition is requested around 08:00 SGT, a target rather than a guaranteed SLA. Freeze the script and reserve time for complete rendering, technical checks and delivery; if that target cannot be met, give a truthful progress update rather than claim success.

Editing a repository prompt does **not** reconfigure the existing Claude routine or an external automation. A human/operator must update its saved instructions separately. Do not add a GitHub cron that pretends it can research or synthesize without the necessary tools.

## Research and evidence

- Refresh the roster from https://xstarterpack.com/; last observed count 211 is a reference, never proof of today's coverage. Inspect public profiles/posts within the runtime budget; record every attempted handle, timestamp, outcome and direct post URLs. Preserve actual post timestamps separately from retrieval time. Inaccessible profiles are blocked, not checked-empty. Do not bypass access controls. State attempted/accessed/blocked/total counts and the unvisited remainder.
- Check https://www.youtube.com/@EverydayAI_/videos and /streams, then publisher episode/newsletter pages at https://www.youreverydayai.com/. Summarize an actual accessible transcript with segment references, never infer the episode from a title/description. Preserve original episode date and upload date separately. Exclude Start Here, replay and re-upload material even without a replay label. Episode 841 (August 14, 2026) was the last verified original at handoff; it is a checkpoint, not a claim that nothing newer exists.
- Use primary announcement/research/product sources to verify AI news. Add an original-source spotlight for Andrej Karpathy, Andrew Ng, Naval Ravikant and Yann LeCun only when genuinely new material is verified. No invented quotes; no news quota or padding.
- Retain the existing general-news breadth and link its published HTML when available. Combine duplicate underlying events across X, YouTube, newsletters, news and every prior delivery. An update needs a named material new fact and a link to the prior event. Keep a stable human-reviewed event ID: URL normalization alone cannot detect semantic duplicates.
- Weather/air quality comes from NEA/MSS/data.gov.sg. Record observation time, retrieval time, region, units and source link. Label forecasts as forecasts; distinguish PSI and PM2.5. Do not assume haze or infer a health warning from missing/stale data. State unavailable observations plainly.

## Editorial and audio contract

Target 10–12 minutes; measure the actual audio duration. Use this section order consistently:

1. Brief welcome and one grounded mindset tip.
2. Singapore conditions: timestamped NEA/MSS weather and air quality.
3. Main news grouped by Singapore, India, world, business and sports.
4. AI and Everyday AI, with relevant fresh thinker contributions or clearly labelled context.
5. Short sourced interesting fact and close.

Keep encouragement in its opening segment; do not interrupt news with random personal encouragement. No puzzles. Mark commentary versus sourced claims and keep factual references in the private transcript/public report.

Use **one soothing female stock voice throughout**, at a moderately faster pace with consistent volume. Retire mixed-voice openings. Keep names and pronunciation tests in the private runtime; audition them and obtain listener review before claiming correctness. Check completeness, duration, clipping and chapter-to-chapter loudness. If the selected voice fails, report the issue rather than silently splice in a different voice. No paid API, enrollment or credentials without approval. Browser speech synthesis is not a downloadable audio file.

## Publication and mobile access

Public UI: [news hub](index.html), [report archive](archive.html), [tracker](tracker.html). Pin the news hub to a phone home screen. The public HTML contains news only: remove personal openings and encouragement.

Audio is private and delivered separately as native ChatGPT attachments, including an MP3 with an ordinary download control and a private transcript. This public repository contains no audio, personalized scripts, transcripts, pronunciation preferences, personal configuration or private attachment URLs. The preferred private streaming URL and automatic seven-day audio deletion are pending authenticated-hosting implementation. Neither access control nor deletion is a working guarantee yet. Public GitHub Pages has no per-listener authentication; a hidden URL is not access control.

For public news updates, atomically update `reports.json` with `latest_id` and `reports`. Each report needs `id`, `title`, ISO `published_at` and a relative same-origin or HTTPS `report_url`. Verify the news-only HTML is accessible before moving the latest pointer. Do not place private media URLs in this manifest.

Update `status.json` only after actual work, using pending/running/completed/blocked and a timestamp/detail per step. Report ingestion, source coverage, verification/dedup, script, audio, publication and delivery separately. No fake percentages or simulated timers. This page polls every 30 seconds and labels updates older than 15 minutes stale. Persist pending work across failures. Only mark delivery completed after checking the actual approved destination.

## Contracts and validation

`evidence.schema.json` describes source evidence, including timestamps, transcript basis and original/replay identity. `ledger.example.json` is an empty format, not research results. Keep the real append-only delivery ledger and coverage runs in the approved private store. Import all prior brief archive rows and previous podcast deliveries, review aliases and event clusters, and record history gaps; do not claim all-history dedup when history is missing.

Run dependency-free checks with:

```sh
node podcast/validate.mjs
node --test podcast/validate.test.mjs
```

The validator checks the shipped manifests and operational invariants; it is not a full JSON Schema engine or a substitute for editorial verification. No collector, synthesis engine, credentials, autonomous runner or schedule is bundled.

## Publicly documented narrative and research approach

The companion combines the existing general-news brief with fresh AI coverage and a warm, concise private podcast. **The runtime is the external scheduled ChatGPT assistant**; this repo provides instructions, evidence formats and public UI, not a bundled autonomous collector or synthesis engine.

- **X research:** refresh the source roster dynamically from [X Starter Pack](https://xstarterpack.com/) (currently 211 profiles, rather than a fixed claim of 200). Read accessible public profiles and original posts; record attempted, accessible, blocked and unvisited counts. Access limits are explicit. Preserve actual post timestamps in Asia/Singapore and distinguish edited, uploaded and retrieved times. Verify claims against primary sources.
- **Selection and dedup:** include up to 20 fresh AI items, with no padding. Group the underlying event across X, news, videos and newsletters, and compare against all available prior deliveries and the existing brief archive. A material update needs a concrete new fact; report missing history rather than claim complete dedup.
- **Everyday AI:** check YouTube Videos and Live plus publisher episode pages, blog, AI News and newsletter. Summarize actual accessible transcripts with references. Exclude Start Here, replays and re-uploads even when they are not labelled as replays; preserve original publication date separately from upload date.
- **Original-source spotlight:** look for genuinely fresh contributions from **Andrej Karpathy, Andrew Ng, Naval Ravikant and Yann LeCun**. When nothing fresh is verified, say so. Any evergreen perspective is clearly labelled and never counted as fresh news.
- **Narrative:** the private 10–12-minute podcast follows one coherent order: brief welcome and mindset tip; Singapore weather and air quality; main news grouped by Singapore, India, world, business and sports; AI and Everyday AI with relevant thinkers; then a short sourced interesting fact and close. Keep encouragement in the opening rather than interleaving it with news. Use one soothing female stock voice throughout, at a moderately faster pace and consistent volume. Retire mixed-voice openings. Test names privately and do not claim pronunciation is correct without listener review. No puzzles; distinguish sourced reporting from commentary.
- **Timing:** the companion's requested daily start is **07:45 Asia/Singapore**, after the upstream HTML is expected. The external automation is managed separately; repo edits do not change its schedule. Inspect and verify the same-day upstream HTML/JSON at start, with a bounded five-minute intake window. If unavailable, disclose the gap and use independently verified current news; never relabel yesterday's edition. The 18 October refreshed edition is requested around **08:00 SGT**, a target rather than a guaranteed SLA.
- **Privacy and phone access:** public HTML contains news only. Personalized audio and transcript stay private. Native ChatGPT attachments are the available delivery route. A private streaming URL with automatic **seven-day audio deletion** is a requested preference **pending authenticated-hosting implementation**; it is not a working feature or a verified deletion guarantee. No personal greeting, private script, voice configuration, media or private URL is published here.

The existing Claude routine's schedule, general-news template, archive and Gmail workflow remain unchanged. The external ChatGPT companion automation is managed separately; its requested start is now 07:45 SGT, with configuration confirmation tracked independently. Editing repo instructions does not automatically reconfigure either runtime.

**Open:** [mobile news hub](https://pbhat89.github.io/the-brief/podcast/) · [live progress tracker](https://pbhat89.github.io/the-brief/podcast/tracker.html) · [report archive](https://pbhat89.github.io/the-brief/podcast/archive.html) · [root overview](../README.md).

