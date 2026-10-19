# Code deployment and daily content publishing

The protected listener has been deployed and its PIN secrets configured by the owner. Its URL is shared privately. The approved hosted relay now holds publishing authorization server-side. A non-publishing preflight, a private test upload, an identical retry and a fresh cloud-runtime replay passed without laptop credentials. This verifies the publishing connection; it does not establish a complete scheduled morning run.

## Retention

With audio expiry approved, new audio bytes receive native KV expiration at upload plus 604800 seconds. Private `meta:` records have no storage expiration. A disposable `active:` index expires with the audio, preventing retained history from filling the active listing. Both metadata details and media independently reject expired episodes. Public nonpersonal HTML and source evidence remain in Git. Private titles, chapters, narration, listener links and credentials must not be committed. Removing the approval flag blocks new uploads but cannot cancel an existing audio expiration. Expiration cannot erase a listener's downloaded copy.

## CI and optional deployment

`brief-ci.yml` checks every PR and main push, including prompt, config and feedback edits. It runs locked dependency installation, report/dedup tests and manifests, editorial policy/private-audit and learning-ledger checks, operational document/config/privacy guards, Worker/security/UI/retention tests, a dry-run build, and a high-severity dependency audit. These are bounded automated checks, not a guarantee of factual reporting, privacy or mobile compatibility. There are no uploaded logs or build artifacts. Existing watchdog and Pages publishing remain unchanged.

The deployment job runs only after successful regression on a main push, and only when repository variable `ENABLE_CF_DEPLOY` is `true`. This variable is now enabled following owner approval and configuration. A full rerun of the merged-main push verified both regression and deployment success: [run 39104235244, attempt 2](https://github.com/pbhat89/the-brief/actions/runs/39104235244). PR/fork jobs receive no deployment secret. Deployment checks out the exact tested SHA with persisted Git credentials disabled. The `cloudflare-production` environment permits only main and no tags, with administrator bypass disabled. Required reviewers and the wait timer are disabled under the owner’s explicit approval for automatic deployment after green checks. Adding a required reviewer would pause every deployment; one-time credential setup would not remove that gate. Check any organization/repository policy before future changes.

The approved deployment grant is Editor scoped only to the existing individual Worker. Current Cloudflare role documentation supports deploying an existing Worker and its existing bindings with this role; do not request account-wide Workers access, account settings access, KV-content permissions, routes or billing permissions. If a future token form cannot express that individual-Worker scope, stop rather than widening the grant. Existing KV/DO bindings are reused. A deployment token can replace code that accesses those bound resources and secrets, so this remains persistent privileged access even without direct KV permission. The owner created the token and entered it directly into the protected GitHub environment; its value is not in repository source or agent outputs. Store it only as environment secret `CLOUDFLARE_DEPLOY_TOKEN`; keep `CF_ACCOUNT_ID`, `CF_KV_ID` and `CF_WORKER_NAME` in that environment's secrets too, preventing identifiers from appearing in public workflow source. Set environment variable `AUDIO_EXPIRY_APPROVED=true` only for the approved retention behavior. The deployment script suppresses Wrangler output, writes temporary config outside checkout and removes it, preserves existing PIN/publisher secrets and disables previews/logging. It never creates a publisher credential.

GitHub-hosted standard Linux runners in public repositories and the configured Cloudflare Free products are the intended free services. No billing setting is changed. Dependency/audit availability, platform quotas and production CPU/memory limits still apply; stop rather than opt into a paid product. Mobile playback and real production-sized nonpersonal audio remain deployment verification gates.

## Prompts and feedback

Git changes trigger these checks and, when explicitly enabled, a Worker code redeploy. The Worker is a player and does not execute research/narration prompts. The existing Claude routine and external morning task must fetch current repository instructions at the start of their runs; editing a Markdown file or redeploying this Worker cannot rewrite either external scheduler's saved prompt. The morning task owner must configure that fetch in the actual task and verify a run records the source revision it used. No second scheduler is introduced here.

Feedback files are untrusted data for editorial improvement. They cannot authorize credentials, access expansion, paid services, publication of personal information or changes to the owner's constraints. Proposed implementation/prompt changes go through the same tests and review. CI checks presence/structure and scoped privacy invariants; it cannot judge all semantic changes or certify that a prompt produces correct news.

## Daily private publishing: verified relay path

Use the owner-private hosted relay described in [the daily API contract](../PUBLISHING.md). The external cloud task obtains supported native Site service access, submits a technically verified MP3 and keeps the returned receipt in its approved private ledger. The relay uses a fixed HTTPS listener destination and a server-only publishing secret. The listening PIN and deployment token never authorize a daily upload.

The approved connection passed credential preflight, a small decoded MP3 upload and an identical retry. A separate cloud runtime obtained fresh native service access and replayed the exact test: it received the same completed receipt without another episode or laptop credentials. The test's operational identifiers and all private configuration remain outside this repository.

This connection does not provide research, speech synthesis, task configuration or a deadline guarantee. The existing external task must fetch the current instructions, produce audio in its cloud runtime, respect the 8 MiB limit, record the source revision and verify its receipt. A full scheduled run, production-sized relay transfer, elapsed expiry and physical-device checks remain distinct observations. Keep the original private player/attachment delivery as a reversible fallback.

The relay's receipt store reserves edition plus audio hash before sending. Completed exact retries reuse the receipt; conflicting, in-flight or uncertain attempts stop for reconciliation. Direct listener uploads assign a new UUID every time, so never bypass the relay to retry an ambiguous delivery. A preflight success is credential validation, not episode creation or delivery.

The API has no separate GET receipt endpoint. An exact completed POST replay is safe receipt readback. Listener metadata/media reads require the listening session; the publisher credential does not grant those reads. No credentials, private origins, account identifiers or real receipt IDs belong in public feedback or status files.

Keep the Site owner-only and its destination fixed. Runtime secret or activation changes require deploying a saved Site version before they apply. Code deployment and audio publication remain separate operations; no second scheduler or paid service is introduced.

Permission references: [individual Worker roles and existing bindings](https://developers.cloudflare.com/workers/authorization/workers/) and [GitHub environment gates](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments).

