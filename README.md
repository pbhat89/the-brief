# The Brief

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
