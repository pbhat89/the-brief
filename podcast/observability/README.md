# Runtime metalog

Download [runtime-metalog.xlsx](runtime-metalog.xlsx) to inspect or record pipeline runs.

- **Runs:** one row per complete run. Record the edition date, stable run ID, start/end UTC timestamps, final run/output statuses, failed agent names and a sanitized evidence link.
- **Agent attempts:** one row per agent or code-node attempt. Reuse the run ID and increment the attempt number for retries. Record status, timestamps, error category and recovery action.
- Runtime formulas use elapsed wall-clock seconds. Overall runtime comes from the run start/end, not the sum of parallel agent runtimes.
- Blank timestamps mean unknown, not zero. Keep unsuccessful attempts even if a retry succeeds. Final run status and individual attempt outcomes are separate.

## Current state

This is an empty, manual template created on 8 November 2026. It does **not** automatically collect runtime events. No past runtimes or failures have been invented. Wiring real run events into the workbook belongs to the future framework implementation, after architecture approval. No runtime, schedule or existing application has been changed by adding this workbook.

## Privacy

This repository is public. Commit only sanitized operational metadata. Never add secrets, tokens, personal logs, recordings, private transcripts, full request/response payloads or confidential evidence URLs. Keep detailed diagnostics in approved private storage. Evidence links in this workbook should be public-safe or omitted.
