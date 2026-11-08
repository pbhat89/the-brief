# The Brief: subscription-backed agent pipeline

This is an opt-in comparison runner. It does not replace the existing morning job or overwrite today's edition. Never claim a live research run from fixture tests.

## Architecture

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
