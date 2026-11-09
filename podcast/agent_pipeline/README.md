# The Brief: subscription-backed agent pipeline

This is an opt-in comparison runner. It does not replace the existing morning job or overwrite today's edition. Never claim a live research run from fixture tests.

## Architecture

See the [root README diagrams](../../README.md#multi-agent-revamp-workflow-and-architecture) for the seven individual agent roles, workflow, components, technology stack and implemented-versus-pending release checkpoints. The independent checker is called again for script fidelity; the LangGraph orchestrator is deterministic code.

`readiness → four research roles → editor → independent checker → (bounded repair) → canonical edition → HTML + podcast script → approved audio hook → audit/export`

The LangGraph coordinator is code, not another conversational worker. Research roles are India, Singapore/weather, UK-US-world, and AI/learning. The editor, checker and podcast producer are distinct model calls. Maximum research concurrency is three by default, at most four. All work uses Codex's supported ChatGPT subscription sign-in; there is no API-key or paid fallback. This does not inherit a dot's memory or connector permissions.

## Installation and private runner

Python 3.11+ and official Codex CLI are required. In a virtual environment:

```
pip install -r podcast/agent_pipeline/requirements.txt
codex login
codex login status
python -m podcast.agent_pipeline.pipeline --repo "$PWD" --output "$HOME/.local/state/the-brief" --date 2026-11-08 --run-id comparison-20261108-1
```

Sign in using ChatGPT, not an API key. The runner needs a writable Codex home and normal supported authentication. Do not copy credentials from managed environments, commit auth files, or put subscription credentials on this public repository's CI runner. Local private output must be outside the checkout. A trusted always-available runner is required for unattended operation; repository code is not such a runner.

## Resume and reproducibility

Use the exact same command plus `--resume`. The run ID, edition date and loaded context hash must match. SQLite checkpoints resume completed graph nodes. Failed runs retain an audit/export. Use a new run ID for changed inputs. Runtime output, raw evidence, personal scripts, audio and checkpoints stay private. Public code and sanitized examples do not contain actual personal data.

## Audio and publishing

The approved narrator assets and voice contracts remain private. `--hooks /private/path/hooks.json` accepts an `audio` argument-vector command. It receives the run state on stdin and must return JSON containing `path`, `sha256`, `qa_passed: true`, and `approved_voice: true`, after running the existing approved voice contract and complete-file audio checks. No shell interpolation is used. Missing configuration produces a written-only result with an explicit audio blocker, never an unapproved voice.

Comparison mode intentionally does not publish into the production daily index. The verified comparison HTML, transcript, audio (if configured) and Excel audit can be delivered privately. Promotion requires verified runner authentication, live research, audio hook and publication tests. Production publishing should use existing PUBLISHING.md receipt/idempotency/readback checks, with a separate comparison edition identity.

## Schedule and deadlines

Proposed production schedule: 05:45 Asia/Singapore readiness; research and review until 06:18; audio/HTML until 06:45; QA/upload by 06:55; delivery by 07:00. No schedule has been changed by this code. If audio is blocked, deliver verified written output by the deadline with precise status. Do not bypass quality gates to meet a target.

## Audit

The private append-only SQLite event store is the source of truth; Excel is an export. It links run, agent attempts, sources, claims, evidence, checkpoints and artifacts. Unknown usage stays unknown. Durations are measured, not guessed. Never log auth tokens, credentials, arbitrary stderr or sensitive personal data to public GitHub.

## Validation

```
python -m unittest discover -s podcast/agent_pipeline/tests -v
node --test podcast/*.test.mjs
```

Unit/integration tests use deterministic fixtures; they do not establish real source access, subscription quota, authentication continuity or subjective audio quality. The initial managed-cloud live probe was blocked by a read-only Codex home before model invocation. Complete the live comparison on a supported writable signed-in runner before promoting this pipeline.

## Windows runner verification (9 November 2026)

A normal ChatGPT-subscription Codex invocation and a hosted live-search call have now succeeded on the connected Windows runner. This resolves the earlier managed-cloud execution blocker, not the remaining full-edition/audio release gates. No production cutover or schedule change is implied.

Use the installed native `codex.exe` with `--codex-executable PATH`; npm `.cmd` shims are deliberately rejected by the Python adapter. Python text I/O is UTF-8. Windows calls run without a shell or visible console window, and timeouts terminate only the launched process tree. Audit handles are explicitly closed before cleanup. CI covers Windows and Linux with deterministic fixtures, not live login or subjective audio quality.

Windows privacy is checked using NTFS owner/DACL evidence, not POSIX mode bits. The audit writer fails closed when additional principals are present or inspection fails. It does not silently change permissions or whitelist an account solely because its name resembles an application. Provision a verified owner-only output directory through an approved workflow before private audio or narrator assets are used. Synthetic test ACLs do not prove the real runner is private.

### First live comparison and trace repair

The 9 November research trial executed all four roles and stopped at the research-evidence gate, before editing, narration or publishing. Candidate stories are not a verified edition. Missing measured attempt timestamps and missing mandatory source-category rows were exposed; the gate was not bypassed.

The adapter now timestamps streamed tool events as they arrive. These are **locally observed event times**, not claims about the remote server's exact execution time. A separate live probe verified both search and exact open-page URL capture. Only a completed, unambiguous open attempt can bind a web source to its trace; search discovery alone does not prove the page was opened or read. The model's unsupported timestamps are discarded. Local upstream and expert-ledger reads use their own measured path/hash evidence and never pretend to be web visits. Reading a file is not proof of complete editorial reconciliation.

Blocked CLI results return a nonzero exit status. The original blocked trial remains immutable; repairs require a new run identity, not retroactively invented evidence. Private-output permissions and full audio/release validation remain required before promotion.

## Native assistant cloud handoff proof

`native_bridge.py` is a private durable job queue, not a Python API for spawning
ChatGPT agents. `native_proof.py` owns a real LangGraph research → independent
checker flow with SQLite checkpoints and `interrupt`/`Command(resume=...)`.
An external assistant driver must read each queued request, actually spawn the
worker, claim the job using the returned agent ID, submit its schema-valid JSON,
and resume the graph. Code-owned state survives between those handoffs.

```
python -m podcast.agent_pipeline.native_proof --directory PRIVATE_DIR --run-id UNIQUE_ID
python -m podcast.agent_pipeline.native_bridge --directory PRIVATE_DIR request --job-id JOB_ID
python -m podcast.agent_pipeline.native_bridge --directory PRIVATE_DIR claim --job-id JOB_ID --request-hash HASH --agent-id ACTUAL_ID
python -m podcast.agent_pipeline.native_bridge --directory PRIVATE_DIR complete --job-id JOB_ID --request-hash HASH --agent-id ACTUAL_ID --output-file RESULT.json
python -m podcast.agent_pipeline.native_proof --directory PRIVATE_DIR --run-id UNIQUE_ID --resume
```

Create and verify a private directory first. Raw requests/results stay in its
handoff database, separate from AuditStore's metadata-only log. Duplicate matching
requests are idempotent; conflicting identities, invalid output, and unclaimed
completion fail closed. Retries require an explicit failed previous attempt.
Queued/start/completion times measure bridge events, not hidden model inference.
Usage remains unknown (`null`). Agent IDs and tool references supplied by the
driver require actual collaboration/tool evidence; the bridge cannot authenticate
an arbitrary caller's claim that an agent was spawned or a page read.

Provider is `native_assistant_subagent`; transport is `assistant_tool_handoff`.
No Codex subprocess, API key, subscription attribution, or metered-token claim is
made. This small NEA-page proof is not a briefing edition, unattended scheduler,
production switch, or evidence of daily delivery reliability. The production
pipeline and schedules remain unchanged. Windows unit tests use synthetic ACL
snapshots while retaining ACL validation; they do not establish real directory
privacy on a deployed runner.

### Live proof result, 9 November 2026

Two actual managed assistant workers independently opened the official NEA weather
page while the laptop was offline. Research and checker results passed the queued
JSON schemas and LangGraph resumed to END; the private audit chain verified. The
checker initially returned the wrong evidence JSON shape; validation rejected it
until corrected. The proof checks page scope, not current weather readings.
Bridge-observed claim-to-completion durations were 55.46 s and 237.98 s; the latter
includes driver/formatting delay. These are not model inference measurements.

120 Python regression tests passed locally, including eight native bridge/proof
tests. Raw run state and tool references remain private, not in this repository.
The full seven-role native pipeline, automatic connector provenance, scheduled
recovery and end-to-end audio/delivery remain unverified. No daily-runtime cutover
has occurred.
