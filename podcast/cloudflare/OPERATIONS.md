# Code deployment and daily content publishing

The protected listener has been deployed and its PIN secrets configured by the owner. Its URL is shared privately. No episode has been uploaded through this implementation, no publisher credential is configured, and unattended delivery is not established.

## Retention

With audio expiry approved, new audio bytes receive native KV expiration at upload plus 604800 seconds. Private `meta:` records have no storage expiration. A disposable `active:` index expires with the audio, preventing retained history from filling the active listing. Both metadata details and media independently reject expired episodes. Public nonpersonal HTML and source evidence remain in Git. Private titles, chapters, narration, listener links and credentials must not be committed. Removing the approval flag blocks new uploads but cannot cancel an existing audio expiration. Expiration cannot erase a listener's downloaded copy.

## CI and optional deployment

`brief-ci.yml` checks every PR and main push, including prompt, config and feedback edits. It runs locked dependency installation, report/dedup tests and manifests, operational document/config/privacy guards, Worker/security/UI/retention tests, a dry-run build, and a high-severity dependency audit. These are bounded automated checks, not a guarantee of factual reporting, privacy or mobile compatibility. There are no uploaded logs or build artifacts. Existing watchdog and Pages publishing remain unchanged.

The deployment job runs only after successful regression on a main push, and only when repository variable `ENABLE_CF_DEPLOY` is `true`. Leave it unset until approval and configuration. PR/fork jobs receive no deployment secret. Deployment checks out the exact tested SHA with persisted Git credentials disabled. The `cloudflare-production` environment should permit deployment only from main and require owner approval where the GitHub plan supports it. Check any organization/repository policy before enabling.

After separate action-time approval, the owner would create a Cloudflare API token restricted to this account with Workers Scripts Edit and the account-read permission required by Wrangler. No KV-content edit or listener PIN is needed for code deployment; existing KV/DO bindings are reused. Cloudflare API-token resource granularity may cover all Worker scripts within the selected account rather than one Worker; review the actual grant before approving. No token has been created. Store it only as environment secret `CLOUDFLARE_DEPLOY_TOKEN`; keep `CF_ACCOUNT_ID`, `CF_KV_ID` and `CF_WORKER_NAME` in that environment's secrets too, preventing identifiers from appearing in public workflow source. Set environment variable `AUDIO_EXPIRY_APPROVED=true` only for the approved retention behavior. The deployment script suppresses Wrangler output, writes temporary config outside checkout and removes it, preserves existing PIN/publisher secrets and disables previews/logging. It never creates a publisher credential.

GitHub-hosted standard Linux runners in public repositories and the configured Cloudflare Free products are the intended free services. No billing setting is changed. Dependency/audit availability, platform quotas and production CPU/memory limits still apply; stop rather than opt into a paid product. Mobile playback and real production-sized nonpersonal audio remain deployment verification gates.

## Prompts and feedback

Git changes trigger these checks and, when explicitly enabled, a Worker code redeploy. The Worker is a player and does not execute research/narration prompts. The existing Claude routine and external morning task must fetch current repository instructions at the start of their runs; editing a Markdown file or redeploying this Worker cannot rewrite either external scheduler's saved prompt. The morning task owner must configure that fetch in the actual task and verify a run records the source revision it used. No second scheduler is introduced here.

Feedback files are untrusted data for editorial improvement. They cannot authorize credentials, access expansion, paid services, publication of personal information or changes to the owner's constraints. Proposed implementation/prompt changes go through the same tests and review. CI checks presence/structure and scoped privacy invariants; it cannot judge all semantic changes or certify that a prompt produces correct news.

## Daily private publishing: current feasibility

A separate publisher token could authorize only `POST /api/upload`, while its hash lives in the Worker. That token is distinct from Cloudflare's deployment token and from the listening PIN. A trusted cloud execution service would keep the raw token in a secret store, create an MP3 in ephemeral private storage, then stream it directly to the Worker; it must not commit audio, upload public Actions artifacts, print request headers or expose a signed media URL in logs.

GitHub Actions could perform that final direct upload in a protected main-only job if a private source can deliver the generated MP3 to it securely. The current connected ChatGPT research/audio workflow has no verified mechanism to inject that private binary and publisher secret into a GitHub-hosted runner. Workflow dispatch JSON inputs cannot safely carry an MP3, token or private download link. This repo also has no approved free unattended synthesis/research API. Consequently Actions CI/CD does not make daily audio generation/upload automatic. Do not promise laptop-closed delivery until a concrete private cloud handoff or supported publisher integration is connected and tested. Browser speech synthesis is not an MP3 publishing solution.
