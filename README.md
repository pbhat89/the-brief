# The Brief

A self-contained daily news brief that runs every morning at 07:00 Asia/Singapore
on Anthropic's cloud as a Claude Code Routine. The routine fetches real news,
fact-checks it, deduplicates against the last 2-3 days of archived headlines,
renders a styled HTML email from `template.html`, and sends it via the Gmail
connector to a recipient address you configure locally (see "Recipient"
below). It runs on the user's Max plan, so
there is no API cost as long as overage and credits stay disabled in billing.

## How it runs

Each morning the routine executes five stages in order:

- Stage 0 — Load history. Read the last 2-3 days from `archive/INDEX.md` to
  build an EXCLUDE set of recently-covered stories.
- Stage 1 — Research. Pull from the source lists in `routine-prompt.md`,
  skipping anything in the EXCLUDE set.
- Stage 2 — Draft. Compose the brief sections and render the HTML email using
  `template.html`.
- Stage 3 — Verify. Run every item past `verifier-checklist.md` (sourcing,
  dates, named entities, claims). Re-do anything that fails.
- Stage 4 — Publish & Archive. Send the email through the Gmail connector,
  then append today's headlines to `archive/INDEX.md` so tomorrow's run can
  see them. Dedup rules live in `dedup.md`.

The email subject line uses a ☕ prefix. The brief is split across labelled
tabs: Singapore, India, Global / Geopolitics, Tech & AI, Business & Markets,
Sports, ✦ Fun Fact, and 🧩 Puzzle, as defined in the template.

## Repo layout

```
the-brief/
  README.md               This file.
  routine-prompt.md       The full prompt the routine runs each morning.
  template.html           HTML email template the routine fills in.
  verifier-checklist.md   Per-item fact-check rules used in Stage 3.
  dedup.md                Rules for matching today's stories against history.
  send-drafts.gs          Google Apps Script that auto-sends drafts the routine creates.
  .gitignore
  archive/
    INDEX.md              Append-only log of past headlines (the dedup source).
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

The recipient email is **not committed** to this public repo. `routine-prompt.md`
uses `<<RECIPIENT_EMAIL>>` as a placeholder. The actual address lives in
`recipient.local.txt` (gitignored).

To paste the prompt into the claude.ai routine "Instructions" field:

1. Open `routine-prompt.md` and copy its full contents.
2. Open `recipient.local.txt` and copy the address.
3. In the Instructions box on claude.ai, find-and-replace `<<RECIPIENT_EMAIL>>`
   with the address before saving the routine.

The address is also visible in the routine's bound Gmail connector, so it's
not "secret" — but keeping it out of git means the address never shows up in
the public commit history, GitHub search, or repo clones.
