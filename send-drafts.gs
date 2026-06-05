/**
 * autoSendBriefDrafts — Google Apps Script for The Brief.
 *
 * Why this exists:
 *   The claude.ai Gmail connector only exposes create_draft, not send.
 *   The daily routine therefore leaves a draft in your Drafts folder
 *   instead of sending the email. This script picks up those drafts
 *   and sends them automatically.
 *
 * How it works:
 *   Walks your Drafts folder, finds any draft whose subject starts with
 *   the SUBJECT_PREFIX, sends each one, and logs the send. Idempotent —
 *   once a draft is sent, it's gone from Drafts and won't be touched.
 *
 * Install:
 *   1. Open https://script.google.com → New project.
 *   2. Paste this file's contents into the editor; save (Ctrl+S).
 *   3. Run autoSendBriefDrafts once manually to grant the Gmail
 *      "Send email as you" scope. Google will prompt for authorization.
 *   4. In the left rail click "Triggers" (the clock icon) → Add Trigger:
 *        Function:        autoSendBriefDrafts
 *        Deployment:      Head
 *        Event source:    Time-driven
 *        Type:            Minutes timer
 *        Interval:        Every 15 minutes
 *      Save.
 *   5. Done. From now on, any draft created by the routine with subject
 *      starting "☕ The Brief" will be sent within 15 minutes.
 *
 * Safety:
 *   - Only touches drafts whose subject starts with SUBJECT_PREFIX.
 *   - Will not touch any other draft you write by hand.
 *   - Logs every send to the Apps Script execution log (View → Executions).
 */

const SUBJECT_PREFIX = '☕ The Brief';

function autoSendBriefDrafts() {
  const drafts = GmailApp.getDrafts();
  let sent = 0;
  let skipped = 0;

  for (const draft of drafts) {
    const msg = draft.getMessage();
    const subject = msg.getSubject() || '';

    if (!subject.startsWith(SUBJECT_PREFIX)) {
      skipped++;
      continue;
    }

    try {
      draft.send();
      console.log(`Sent: "${subject}"`);
      sent++;
    } catch (err) {
      console.error(`Failed to send "${subject}": ${err}`);
    }
  }

  console.log(`Run complete. Sent: ${sent}. Skipped (other drafts): ${skipped}.`);
}
