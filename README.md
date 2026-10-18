# The Brief

## Combined morning briefing and private podcast

The companion combines the existing general-news brief with fresh AI coverage and a warm, concise private podcast. **The runtime is the external scheduled ChatGPT assistant**; this repo provides instructions, evidence formats and public UI, not a bundled autonomous collector or synthesis engine.

- **X research:** refresh the source roster dynamically from [X Starter Pack](https://xstarterpack.com/) (currently 211 profiles, rather than a fixed claim of 200). Read accessible public profiles and original posts; record attempted, accessible, blocked and unvisited counts. Access limits are explicit. Preserve actual post timestamps in Asia/Singapore and distinguish edited, uploaded and retrieved times. Verify claims against primary sources.
- **Selection and dedup:** include up to 20 fresh AI items, with no padding. Group the underlying event across X, news, videos and newsletters, and compare against all available prior deliveries and the existing brief archive. A material update needs a concrete new fact; report missing history rather than claim complete dedup.
- **Everyday AI:** check YouTube Videos and Live plus publisher episode pages, blog, AI News and newsletter. Summarize actual accessible transcripts with references. Exclude Start Here, replays and re-uploads even when they are not labelled as replays; preserve original publication date separately from upload date.
- **Original-source spotlight:** look for genuinely fresh contributions from **Andrej Karpathy, Andrew Ng, Naval Ravikant and Yann LeCun**. When nothing fresh is verified, say so. Any evergreen perspective is clearly labelled and never counted as fresh news.
- **Narrative:** the private 10–12-minute podcast follows one coherent order: brief welcome and mindset tip; Singapore weather and air quality; main news grouped by Singapore, India, world, business and sports; AI and Everyday AI with relevant thinkers; then a short sourced interesting fact and close. Keep encouragement in the opening rather than interleaving it with news. Use one soothing female stock voice throughout, at a moderately faster pace and consistent volume. Retire mixed-voice openings. Test names privately and do not claim pronunciation is correct without listener review. No puzzles; distinguish sourced reporting from commentary.
- **Timing:** the companion's requested daily start is **07:45 Asia/Singapore**, after the upstream HTML is expected. The external automation is managed separately; repo edits do not change its schedule. Inspect and verify the same-day upstream HTML/JSON at start, with a bounded five-minute intake window. If unavailable, disclose the gap and use independently verified current news; never relabel yesterday's edition. The 18 October refreshed edition is requested around **08:00 SGT**, a target rather than a guaranteed SLA.
- **Privacy and phone access:** public HTML contains news only. Personalized audio and transcript stay private. Native ChatGPT attachments remain an available delivery route. Owner-only private streaming is available with seven-day playback expiry; upload integrity, range seeking and anonymous-access denial were verified. Owner-browser playback still needs a signed-in check. **Permanent storage deletion after seven days remains pending approval/setup**; playback expiry is not deletion. No personal greeting, private script, voice configuration, media or private URL is published here.

The owner-private player includes a speech-reactive blue/purple liquid animation, with pause and reduced-motion handling, and still requires ChatGPT sign-in. Shared PIN listening is requested but **not implemented**: audience confirmation, secure user-entered PIN setup and a verified authorization design are pending. No access or credentials are changed by this documentation.

The existing Claude routine's schedule, general-news template, archive and Gmail workflow remain unchanged. The external ChatGPT companion automation is managed separately; its requested start is now 07:45 SGT, with configuration confirmation tracked independently. Editing repo instructions does not automatically reconfigure either runtime.

**Open:** [mobile news hub](https://pbhat89.github.io/the-brief/podcast/) · [live progress tracker](https://pbhat89.github.io/the-brief/podcast/tracker.html) · [report archive](https://pbhat89.github.io/the-brief/podcast/archive.html) · [full companion operations](podcast/README.md).

A self-contained daily news brief that runs every morning at 07:00 Asia/Singapore
on Anthropic's cloud as a Claude Code Routine. The routine fetches real news,
fact-checks it, deduplicates stories against the last 2-3 days of archived
headlines (and fun facts / puzzles against a longer 30-day rolling ledger),
renders an interactive HTML brief from `template.html`, publishes it via
GitHub Pages, and emails a clean, styled one-line HTML digest (with the Pages
link) to the recipient list via the Gmail connector. It runs on the user's Max
plan, so there is no API cost as long as overage and credits stay disabled in
billing.

## How it runs

Each morning the routine executes five stages in order:

- Stage 0 — Load history. Read the last 2-3 days from `archive/INDEX.md` to
  build an EXCLUDE set of recently-covered stories, and read `archive/USED.json`
  for the 30-day fun-fact / puzzle dedup ledger.
- Stage 1 — Research. Pull from the source lists in `routine-prompt.md`,
  skipping anything in the EXCLUDE set, and expand searches (widening 48h→72h)
  until each news section has at least 4 candidates.
- Stage 2 — Draft. Substitute today's data into `template.html` (date
  placeholders + the `SECTIONS` / `FUN_FACT` / `PUZZLE` / `WORD_PUZZLE` JS arrays) to produce
  the day's rich HTML brief.
- Stage 3 — Verify. Run every item past `verifier-checklist.md` (sourcing,
  dates, named entities, claims). Re-do anything that fails, backfilling to keep
  each section at 4-5 items.
- Stage 4 — Publish & Archive. Create a Gmail draft: a styled one-line HTML
  digest (`htmlBody`, built from `email-digest-sample.html`) of the eight news
  sections, with a plain-text fallback, sent to every address in the recipient
  list. Write today's HTML + JSON to `archive/`, append story rows to
  `archive/INDEX.md`, and update `archive/USED.json`. Push to `main`; GitHub
  Pages auto-serves the new HTML within ~60s.

The full brief lives at
`https://pbhat89.github.io/the-brief/archive/YYYY-MM-DD.html` and uses the
interactive tabbed UI from `template.html` (anchor chips, spectrum framing
blocks on political items, fun-fact, puzzle, and word-puzzle cards). The email
is a clean, scannable HTML digest — one line per headline, four to five per
section, no fun fact or puzzles — opened by a prominent full-width button that
links to that URL.

The email subject line uses a ☕ prefix. The Pages-hosted brief is split
across labelled tabs: 🇸🇬 Singapore, 🇮🇳 India, 🇬🇧 UK News,
🌍 Global / Geopolitics, 💻 Tech & AI, 📈 Business & Markets,
🎾🏏🏎️ Sports, 🔬 Other Miscellaneous News, ✦ Fun Fact, 🧩 Puzzle, and
🔤 Word Puzzles, as defined in the template.

## Repo layout

```
the-brief/
  README.md               This file.
  routine-prompt.md       The full prompt the routine runs each morning.
  template.html           The full rich brief template (served via Pages).
  email-digest-sample.html Reference layout for the clean one-line email digest.
  verifier-checklist.md   Per-item fact-check rules used in Stage 3.
  dedup.md                Rules for matching today's stories against history.
  send-drafts.gs          Google Apps Script that auto-sends drafts the routine creates.
  .gitignore
  archive/
    INDEX.md              Append-only log of past headlines (the story dedup source).
    USED.json             Rolling fun-fact / puzzle / word-puzzle ledger (30-day dedup memory).
    .gitkeep
```

## How to edit

- Change what the daily routine does — edit `routine-prompt.md`. This is the
  prompt that runs on the schedule; everything else is referenced from it.
- Change what the email looks like — edit `template.html`. Layout, typography,
  tab labels and colors all live there.
- Change which outlets and topics get pulled — edit the source lists inside
  `routine-prompt.md`.
- Tighten or loosen fact-checking — edit `verifier-checklist.md`.
- Change how aggressively stories are deduplicated — edit `dedup.md`.

After editing, paste the updated `routine-prompt.md` back into the routine on
claude.ai/code/routines. Template and checklist files are read by the prompt
at runtime from this repo, so re-pasting the prompt is only required when the
prompt itself changes.

## Deploy

1. Go to claude.ai/code/routines and create a new routine named
   "The Brief — daily".
2. Paste the contents of `routine-prompt.md` as the routine prompt.
3. Set the schedule to Daily, 07:00, timezone Asia/Singapore.
4. Enable only the Gmail connector. Leave all other connectors off.
5. Set the model to Claude Opus.

In billing, keep both overage and credit top-ups OFF. The routine is sized to
fit inside Max-plan usage; leaving overage off prevents any accidental charge
if usage spikes.

## Environment network allowlist (why India/UK can go dark)

The routine's cloud environment enforces a network egress policy: requests to
hosts outside its allowlist are rejected at the proxy with a 403 before they
reach the site. In July 2026 this blocked every primary India and UK outlet
(plus Reuters, AP, The Guardian, NYT, and even `pbhat89.github.io`), so those
sections ran on placeholders or fallback sources for days.

`routine-prompt.md` mitigates this in-run (FIX 6 retries, then the India/UK
**fallback source tiers** — SCMP, Al Jazeera, CNN, Bloomberg, CNBC, The
Guardian), but the real fix is widening the environment's network access
where the routine is configured (claude.ai → Code → the routine's environment
settings; see code.claude.com/docs/en/claude-code-on-the-web for network
policy details). Domains to allow:

```
# India (primary outlets)
thehindu.com  indianexpress.com  hindustantimes.com
timesofindia.indiatimes.com  ndtv.com  economictimes.indiatimes.com
# UK (primary outlets)
bbc.com  bbc.co.uk  news.sky.com
# Also on allowed lists but currently blocked
reuters.com  apnews.com  theguardian.com  nytimes.com
# Self-verification of the published brief
pbhat89.github.io
```

Until those are allowed, expect India/UK to run on the fallback tier and the
`PAGES CHECK BLOCKED` marker in run logs (the GitHub Actions watchdog covers
the Pages check from outside the environment).

## Auto-send the Gmail draft

The claude.ai Gmail connector only exposes `create_draft` — there's no `send`
tool. By default the routine therefore leaves a draft in your Drafts folder
every morning, which you'd have to open and click Send manually.

`send-drafts.gs` is a small Google Apps Script that closes this gap. It
walks your Drafts folder on a schedule, finds any draft whose subject starts
with `☕ The Brief`, and sends it. Drafts you write by hand are untouched.

One-time setup (about 3 minutes):

1. Open https://script.google.com and click **New project**.
2. Paste the contents of `send-drafts.gs` into the editor. Save.
3. Click **Run** once on `autoSendBriefDrafts` — Google will ask for the
   "Send email as you" Gmail scope. Authorize it.
4. In the left rail click the clock icon (**Triggers**) → **Add Trigger**:
   - Function: `autoSendBriefDrafts`
   - Event source: Time-driven
   - Type: Minutes timer
   - Interval: Every 15 minutes
   - Save.

That's it. From the next routine run forward, the daily brief will be in
your inbox within 15 minutes of the routine creating the draft.

The repo also publishes each day's HTML at
`https://pbhat89.github.io/the-brief/archive/YYYY-MM-DD.html` via GitHub
Pages, so even if the email path fails the brief is always live at that URL.

## Recipient

The recipient list is **not committed** to this public repo. `routine-prompt.md`
uses `<<RECIPIENT_EMAILS>>` as a placeholder — a JSON array of one or more plain
addresses. The actual list lives in `recipient.local.txt` (gitignored).

To paste the prompt into the claude.ai routine "Instructions" field:

1. Open `routine-prompt.md` and copy its full contents.
2. Open `recipient.local.txt` and copy the address array.
3. In the Instructions box on claude.ai, find-and-replace every `<<RECIPIENT_EMAILS>>`
   with the array before saving the routine.

The addresses are also visible in the routine's bound Gmail connector, so they're
not "secret" — but keeping them out of git means they never show up in the public
commit history, GitHub search, or repo clones.

## Morning companion

The existing Claude brief and Gmail workflow remain unchanged. The companion adds an operational specification for verified X/Everyday AI/AI coverage, source evidence contracts and a public news hub. See [instructions](podcast/README.md), [news hub](https://pbhat89.github.io/the-brief/podcast/), [reports](https://pbhat89.github.io/the-brief/podcast/archive.html) and [live tracker](https://pbhat89.github.io/the-brief/podcast/tracker.html).

The companion's requested start is now 07:45 Singapore time, with a bounded five-minute upstream intake; the refreshed 18 October edition is targeted around 08:00. The external ChatGPT companion automation is configured separately; no autonomous research collector or synthesis service is bundled in this repository. Editing a prompt does not update the saved Claude routine automatically. Public HTML is news only. Audio and its transcript are delivered privately as ChatGPT attachments; no private media URLs or personal configuration belong in this repo.
