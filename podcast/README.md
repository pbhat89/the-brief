# Morning podcast companion

This bounded companion extends The Brief without replacing the existing Claude routine, general-news archive, templates, watchdog, recipients or Gmail draft sender. No new scheduler is installed here. The existing external ChatGPT companion automation has been updated for 07:00 Asia/Singapore with a 07:30 delivery target; the original Claude schedule and Gmail workflow are unchanged.

## Operator sequence and deadline

Use the existing external automation: 07:00 Asia/Singapore start; 07:30 target, not a guaranteed SLA. At 07:00 record a run ID and timestamped status. Read prior delivery ledgers and the entire existing archive index before choosing stories. Research concurrently with checking for today's Claude HTML/JSON.

**07:12 SGT is the intake cutoff.** Use today's Claude payload only if it is available and verified by then. A 07:20–07:30 arrival must not hold up audio. At cutoff, independently verify a smaller general-news selection; if verification is unavailable omit that segment and say so. Never relabel yesterday's brief as today. Freeze script by 07:17, aim for synthesis by 07:24 and verify playback/download by 07:28. At 07:30 deliver a truthful partial-status notice if audio is blocked; never claim delivery because a script exists. Late source material goes to the next run after freshness and dedup checks.

Editing a repository prompt does **not** reconfigure the existing Claude routine or an external automation. A human/operator must update its saved instructions separately. Do not add a GitHub cron that pretends it can research or synthesize without the necessary tools.

## Research and evidence

- Refresh the roster from https://xstarterpack.com/; last observed count 211 is a reference, never proof of today's coverage. Inspect public profiles/posts within the runtime budget; record every attempted handle, timestamp, outcome and direct post URLs. Preserve actual post timestamps separately from retrieval time. Inaccessible profiles are blocked, not checked-empty. Do not bypass access controls. State attempted/accessed/blocked/total counts and the unvisited remainder.
- Check https://www.youtube.com/@EverydayAI_/videos and /streams, then publisher episode/newsletter pages at https://www.youreverydayai.com/. Summarize an actual accessible transcript with segment references, never infer the episode from a title/description. Preserve original episode date and upload date separately. Exclude Start Here, replay and re-upload material even without a replay label. Episode 841 (August 14, 2026) was the last verified original at handoff; it is a checkpoint, not a claim that nothing newer exists.
- Use primary announcement/research/product sources to verify AI news. Add an original-source spotlight for Andrej Karpathy, Andrew Ng, Naval Ravikant and Yann LeCun only when genuinely new material is verified. No invented quotes; no news quota or padding.
- Retain the existing general-news breadth and link its published HTML when available. Combine duplicate underlying events across X, YouTube, newsletters, news and every prior delivery. An update needs a named material new fact and a link to the prior event. Keep a stable human-reviewed event ID: URL normalization alone cannot detect semantic duplicates.
- Weather/air quality comes from NEA/MSS/data.gov.sg. Record observation time, retrieval time, region, units and source link. Label forecasts as forecasts; distinguish PSI and PM2.5. Do not assume haze or infer a health warning from missing/stale data. State unavailable observations plainly.

## Editorial and audio contract

Target 10–12 minutes (roughly 1,300–1,650 spoken words; measure actual MP3 duration). Warm, concise, credible: brief grounded confidence/leadership opening; timestamped Singapore weather/air quality; general and AI headlines with implications; fresh thinker spotlight; transcript-based Everyday AI insight; one practical mindset/healthy-day tip; one sourced interesting fact; short actionable close. No puzzles. Clearly mark commentary versus sourced claims. Keep factual links in the transcript/report.

The separate private-audio stage uses a verified available voice and private pronunciation configuration. Never publish that configuration. No paid API, enrollment or credentials without approval. Browser speech synthesis is not a downloadable MP3. If synthesis is unavailable, report the blocker privately.

## Publication and mobile access

Public UI: [news hub](index.html), [report archive](archive.html), [tracker](tracker.html). Pin the news hub to a phone home screen. The public HTML contains news only: remove personal openings and encouragement.

Audio is private and delivered separately as native ChatGPT attachments, including an MP3 with an ordinary download control and a private transcript. This public repository contains no audio, personalized scripts, transcripts, pronunciation preferences, personal configuration or private attachment URLs. An authenticated private player may be considered later. Public GitHub Pages has no per-listener authentication; a hidden URL is not access control.

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
- **Narrative:** the private 10–12-minute podcast uses grounded, warm encouragement and leadership/AI-transformation context, a practical mindset or healthy-day tip, concise news and implications, NEA/MSS weather and haze observations with timestamps, and a sourced interesting fact. No puzzles in the companion. Quotes must be real; commentary is distinguished from reporting.
- **Timing:** the existing external companion automation is configured for **07:00 Asia/Singapore**, accepting the same-day Claude brief only through **07:12**, with a **07:30 delivery target**, not a guaranteed SLA. If the upstream brief arrives later, independently verify a smaller selection and disclose availability; never present yesterday's brief as today's.
- **Privacy and phone access:** public HTML contains news only. Personalized audio and its transcript are **private**, delivered as native ChatGPT attachments accessible on the phone. No personal greeting, private script, voice configuration, media or private attachment URL is published here. An authenticated private player can be considered later.

The existing Claude routine's schedule, general-news template, archive and Gmail workflow remain unchanged. The ChatGPT companion automation has been updated separately. Editing repo instructions does not automatically reconfigure either runtime.

**Open:** [mobile news hub](https://pbhat89.github.io/the-brief/podcast/) · [live progress tracker](https://pbhat89.github.io/the-brief/podcast/tracker.html) · [report archive](https://pbhat89.github.io/the-brief/podcast/archive.html) · [root overview](../README.md).

