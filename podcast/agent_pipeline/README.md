# The Brief: subscription-backed agent pipeline

This is an opt-in comparison runner. It does not replace the existing morning job or automatically overwrite today's edition. Any separately authorized promotion must still pass the existing editorial, voice, measured-audio and publication gates. Never claim a live research run from fixture tests.

## Architecture

See the [root README diagrams](../../README.md#multi-agent-revamp-workflow-and-architecture) for the seven individual agent roles, workflow, components, technology stack and implemented-versus-pending release checkpoints. The independent checker is called again for script fidelity; the LangGraph orchestrator is deterministic code.

`readiness → four research roles → editor → independent checker → (bounded repair) → canonical edition → HTML + podcast script → approved audio hook → audit/export`

The LangGraph coordinator is code, not another conversational worker. Research roles are India, Singapore/weather, UK-US-world, and AI/learning. The editor, checker and podcast producer are distinct model calls. Maximum research concurrency is three by default, at most four. The standalone adapter uses Codex's supported ChatGPT subscription sign-in; the native alternative uses an external managed assistant driver with separately attributed connector receipts. Neither has an API-key or paid fallback. Native execution does not prove Codex subscription attribution, and the standalone adapter does not inherit a dot's memory or connector permissions.

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

Proposed production schedule: 04:00 Asia/Singapore readiness; research and review until 06:18; audio/HTML until 06:45; QA/upload by 06:55; delivery target 07:00, latest 07:15. No schedule has been changed by this code. If audio is blocked, deliver independently verified written output by 07:15 with precise status; if written quality/delivery is blocked too, report the blocker by then. Do not bypass quality gates to meet a target.

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

### Full native comparison runner (opt-in, live validation ongoing)

`native_pipeline.py` reuses the full research/editor/checker/script/release gates.
Four research jobs queue before a durable interrupt; the external assistant driver
executes actual native workers, records original tool receipts with
[`NATIVE_TOOL_CAPTURE.md`](NATIVE_TOOL_CAPTURE.md), and resumes the graph.
Runtime, context and private baseline hashes are immutable across resume. No
Python worker spawning, automatic retries, publication or schedule cutover occurs.

Rejected schema/identity/state submissions now produce deduplicated metadata-only
audit events. Evidence manifests retain actual wrapper timing, source references
and original-result hashes, with a separately attributed capture-driver identity.
Receipt validation is not cryptographic connector attestation. Declared evidence
without captured timing/hash cannot satisfy measured-source gates.

The full native four-role comparison completed through independently checked
written edition and script. Audio/publication remains source-release blocked.
Private baseline inputs and review artifacts remain outside this public repository.

### Versioned recovery and source-attempt semantics

An optional `--parent-manifest` binds an immutable prior same-edition/context
manifest to a distinct new run. Four actual worker revalidation turns are still
required; old tool calls keep their original times/hashes, never become new
fetches. The original run is not silently migrated. Failed and unclear opens
retain measured attempt provenance (`open_failed`/`open_unknown`) separately
from readable access. Credential-bearing URLs remain rejected; exact public
YouTube handles and ordinary news slugs are supported.

Cross-stage source identity is normalized deterministically before editing: a
research source ID must resolve to one unique HTTPS source-row URL supported by
that story's exact evidence URL. Raw outputs remain immutable, mappings are
audited separately, and ambiguity fails closed. Snapshot context is recursively
canonicalized before the first prompt, so fresh-process resume cannot alter
request identity just by changing JSON key order.

### Carried research and integrated audit workbook

`--seed-research PRIVATE_RESULT.json` may accompany a parent manifest to carry
only verified `research_ready` state into a distinct same-context run. Its file
hash and origin run are bound in the new manifest. Carried source/claim/evidence
rows are labelled, no new researcher calls are invented, and actual editor/checker
turns still run. Exceptions now record error type and failed status without raw
validation payloads. A complete synthetic graph test covers every model stage
through the unchanged release-blocked boundary.

`python -m podcast.agent_pipeline.native_report --directory PRIVATE_RUN --output PRIVATE_REPORT.xlsx`
creates a separate nine-tab report from read-only SQLite inputs, joining pipeline
and native-job/evidence/rejection state. Hash chains, request/output/evidence
hashes and completed schemas are checked. Unknown token metrics remain blank;
bridge wall time is not model inference time. Raw prompts and captured page
content are excluded. Pending or failed runs are never labelled complete.

Script fidelity now has an explicit bounded repair path: at most two separately
identified producer/checker repair pairs, always against the same locked edition.
Failed checks do not mutate completed jobs; exhaustion records failure and emits
no script artifact. Full native graph regressions cover success, repair success
and exhaustion. This does not waive the independent source-release gate.


### Native driver exit status

The JSON `status` is authoritative: a draft is not a successful delivery.
Native CLI exit 0 means either a nonempty `__interrupt__` pending an external
worker handoff, or terminal `comparison_ready`. Drivers must distinguish those
cases in JSON. All other terminal states, including
`comparison_draft_release_blocked`, audio/coverage blocks, failures and unknown
states, exit 2. A pending exit 0 never means the episode was published.

### Verified comparison outcome (9 November 2026)

All actual native model stages completed. The reviewed draft contains 12 selected
items and an 11-section, 692-word spoken body; it was not padded. The source gate
remains blocked, so no new audio or production publication occurred. A cloud
executor interruption recovered from persisted state without repeating source
fetches. The combined private workbook retains five versioned attempts and their
22 native jobs, with source rebindings distinguished from new fetches. This is
not evidence of unattended daily delivery or a production cutover.

### Explicit supplemental research

`--research-supplement PRIVATE_JSON` requires `--seed-research` and a matching
`--parent-manifest`. The bundle contains `edition_date`, `context_hash`,
`parent_run_id`, actual `researcher_id`, a `research` array conforming to the
research schema, and `receipts` entries `{path, sha256, tool_ref}` pointing at
retained native_capture receipt files. All supplement source IDs, story IDs and
event IDs must be new. Receipt hashes, request URLs, times, references and exact
evidence quotations are checked; declared model timestamps are not trusted.
Raw-file and canonical bundle hashes are bound to the new run manifest.

A real `supplemental_review` native job must return
`{passed, accepted_story_ids, issues}` before any additions reach the editor.
Unknown/duplicate accepted IDs or failed review block the run. An explicit
accepted-ID subset records rejections by omission in the retained review output;
accepted objects are not rewritten. This is a manual assistant-driver handoff,
not an autonomous API. Researcher identity and tool execution remain explicit
caller attestations, not automatically authenticated facts. Original capture
times stay historical; no fake new research invocations are recorded.

Updated coverage/gap evidence must stay separately traceable; this feature does
not alter historical coverage cursors, replace the locked content context or
waive the existing release gate. Existing completed runs remain immutable.

Optional supplement `coverage_artifact: {path, sha256}` binds a new private
coverage evidence JSON and copies it immutably into the new run output. It is
visible to the supplement reviewer, but is explicitly not a release-gate pass
or a change to the inherited content-context hash. A complete final-edition
editorial audit is still required by `hooks['editorial_audit']` and the existing
`validate-editorial.mjs` gate after script generation. Fresh condition readings
may use new story/event IDs; the editor must explicitly exclude superseded
readings rather than mutating historical candidates.

For additions collected by several actual workers, each receipt may declare its
original `researcher_id`; `research_provenance` may list the actual candidate
file hashes and researcher identities. These are retained caller attestations,
not fabricated bridge invocations or proof of automatic tool authentication.

The present graph can finish with a written draft and
`comparison_draft_release_blocked`. A subsequent explicit release phase may
run approved offline narration, measured audio QA and the full final editorial
and voice gates, then the authorized private publication driver. Such a later
phase must have separate audit evidence; it must not rewrite the completed
comparison status as `comparison_ready` or waive any final gate. Full graph
release-stage decomposition remains future work.

Story supplement receipt rows now require `tool_name: "chat_search_web_run"`
and a genuine native web source extract with matching source reference and exact
`Source: open` request URL. Browser receipts are not supported as story evidence
by this importer and must not be relabelled. X coverage remains a separate
coverage artifact preserving its actual browser provenance. This format check
is not automatic authentication of a remote tool. Every accepted or rejected
story ID receives an explicit supplemental disposition audit event.

### Updated comparison and rendering blocker

The later same-day comparison completed a real receipt-bound supplemental review,
editor, independent fact checker, script producer and one bounded script repair
with an independent recheck. It contains 14 selected items and a 659-word body.
No padding was added to meet the 10–12-minute target; that target is not met by
this written comparison. Source-attempt validation passes as PARTIAL, not full
historical-window coverage. The original edition remains available.

The graph correctly retains `comparison_draft_release_blocked`. A separately
authorized private render phase passed script/voice preflight and content
readiness, but two renderer attempts exited with signal 9 during model startup
before any audio chunks. The second attempt ran without concurrent ASR. Low
available memory was observed, but no accessible OOM counter proved the cause.
No new audio was uploaded, no approved voice setting was weakened, and final
measured editorial/audio/publication gates remain unsatisfied. A supported cloud
runner with sufficient available capacity is the next requirement. Existing
schedules and the original publishing workflow are unchanged.

A first supplemental-review queue attempt also failed safely because a large
coverage artifact exceeded the bounded prompt limit. The repair passes only its
path, hash and bounded summary to the reviewer, retaining the full private
artifact separately. The failed run remains immutable; a distinct run completed
the review. Realistic large-artifact regression and Windows/Linux CI pass.

### Evidence-backed editorial depth and narration lock

The research prompt no longer asks for a headline and one short sentence. Audio
length constrains selection after research, never the breadth of mandatory source
attempts or the evidence retained. Researchers must read beyond discovery snippets
and retain useful background, concrete developments, affected people/mechanisms
and limitations with exact source passages. Partial text or blocked X access stays
explicitly partial. Another publisher cannot prove X coverage.

The editor accounts for every supplied candidate in `selection`, with a reason for
including or excluding it. Every news story has an explicit `treatment` and materiality-based
`treatment_reason`: developed stories need distinct `narrative` units for
development, context and stakes, plus any material caveat. Justified brief updates
need only a complete development and any material caveat, not padded stakes. Each unit
contains natural spoken `text` and `evidence_indexes` into the story's retained
quotes. The summary is those units joined by spaces, so HTML cannot quietly lose
the context. Evidence-poor stories need further research or exclusion, not padding.
Weather, learning and fact retain their existing specialized rules and may have
an empty narrative array. No minimum word count or number of agents proves depth.

Both editorial and script checkers judge selection and edition-level depth in
`edition_review`, with a specific rationale. All-brief editions require a justified
quiet-day/evidence explanation; there is no numerical story or length quota. They
must also return a specific `editorial_reviews` row
for each news story, identifying all supported unit indexes and judging useful
context and preservation of caveats. The editor's candidate set is visible to the
editorial checker for selection/coverage review. Missing reviews, unsupported
units or failed depth/caveat findings block approval even with `passed: true`.

Narration preserves each locked news unit verbatim exactly once, in original
order, in a section referencing that story. The producer can add natural transitions, not compress away the unit's
meaning. Awkward prose requires an editor revision and a new lock, not a silent
producer rewrite. Existing bounded repair, voice, audio and source-release gates
remain in force. The new contract requires a distinct run with new runtime/schema
identity; do not rewrite old completed outputs to make them appear compliant.

These deterministic checks prove structure, retained evidence identity and text
fidelity, **not** source entailment or editorial judgment. The independent checker
must actually compare the evidence, including any omitted limitations. A dishonest
or mistaken model can still misjudge an apparently well-formed unit. The adversarial
fixtures explicitly exercise rejection of an unsupported expansion with a supplied
independent finding; they do not pretend a Python gate understands the claim.
Before promotion, run a real-source comparison through independent review and
listen to the rendered sentences. Fixture passes are not live research, improved
coverage, a pronunciation assessment or a delivery claim. No schedules, published
editions or external instructions are changed by this implementation.


### Retention contract (11 November update)

Audio now targets around 15 minutes with no padding. The written edition may be
richer. Specialist evidence packets survive summarization intact; the editor
preserves selected news evidence arrays in their original order and accounts for
every passage in `retention`. Each row has `evidence_index`, `disposition`
(`narrated`, `written_only`, `omitted`), `unit_indexes`, and a concrete `reason`.
Indexes point into `narrative` or `written_context` according to disposition;
omitted rows have no unit indexes. Important caveats to a spoken claim must stay
in the spoken narrative. `written_context` uses the same evidence-indexed unit
format as `narrative` and is rendered after the spoken core in HTML. Non-news
stories use empty arrays for these two fields. Independent review indexes cover
`narrative + written_context`, in that order. Old cached editions missing these
fields require re-editing and independent review, not fabricated migration rows.

This accounts for passages, not automatically for every fact within a passage.
The independent checker must judge all distinct facts, omissions and materiality
against original candidate evidence. Neither a complete ledger nor a 15-minute
recording proves quality. All research gaps remain visible in the edition.
