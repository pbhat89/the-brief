# Private Cloudflare player

This directory is isolated from the existing hosted player. It contains no episodes, transcripts, PINs, publisher tokens or account identifiers. The PIN listener is deployed; its URL is shared privately. The approved private hosted relay now publishes episodes with server-held authorization and durable retry receipts; a fresh cloud-runtime replay passed. The first complete scheduled morning run remains to be observed. See the [daily relay API contract](../PUBLISHING.md). See [current operations and CI/CD](OPERATIONS.md). Only Workers Free, a new private Workers KV namespace, and a SQLite Durable Object are required. No R2, paid plan or public audio assets.

## Owner handoff and deployment configuration

These bootstrap steps describe a fresh installation. The existing deployed listener reuses its approved bindings; do not recreate namespaces, reset the PIN or replace credentials during daily runs. Current daily publishing uses the [private relay contract](../PUBLISHING.md).

1. In this directory run `npm ci`, `npm test`, and `npm run check`. Use a current supported Node release. Authenticate Wrangler yourself in the intended Cloudflare account; this change does not switch accounts or create account credentials.
2. Run `npx wrangler kv namespace create EPISODES`. Create a **new, empty** namespace; copy its ID into `wrangler.jsonc`. Never bind an existing live namespace. The placeholder deliberately prevents production deployment.
3. With account access approved, run `node scripts/configure-pin.mjs` in an interactive local terminal. It asks for a user-chosen 12–32 digit PIN twice without echo, derives a salted PBKDF2-SHA256 verifier (100,000 iterations), and submits `PIN_SALT` and `PIN_HASH` through Wrangler's secret stdin. No plaintext PIN enters a file, shell history, URL or source code. Do not paste a PIN into chat. Choose a long unpredictable PIN; short numeric codes are susceptible to offline guessing if the verifier is compromised. Changing the verifier invalidates old sessions. A failed partial update fails authentication closed; rerun the helper to finish.
4. Publisher authorization is separate from the shared listening PIN. **Creating or provisioning a persistent publishing credential requires separate explicit approval.** Until then leave `PUBLISHER_TOKEN_HASH` absent. After approval, the owner supplies a high-entropy 32–256 character base64url token through their own secret manager, computes its SHA-256 hash locally and sets only the hexadecimal hash via `npx wrangler secret put PUBLISHER_TOKEN_HASH`. Never store the raw token here. There is no public setup endpoint and a listener cannot publish.
5. **Seven-day actual deletion requires separate explicit confirmation.** Leave `EXPIRY_APPROVED` set to `"false"` until that confirmation. Uploads are rejected while false. After approval set it to `"true"`; newly uploaded audio and its disposable active-list index receive absolute KV expiration at upload + 604800 seconds. Private playback metadata is retained without storage expiration; authenticated reads reject expired episodes. This uses native KV expiry, not a cleanup job. Reverting the flag prevents new uploads but does not cancel already scheduled expiry. No existing live files have been touched or scheduled for deletion.
6. Run `npm run deploy` after those owner steps. Wrangler creates the SQLite Durable Object migration and returns the `https://brief-private-player.<subdomain>.workers.dev` URL. Open that URL over HTTPS, set no Cloudflare cache rules for `/api/*`, and complete the deployed checks below before sharing the URL and PIN separately.

## Publishing contract

`POST /api/upload` requires exact same-origin `Origin`, `Authorization: Bearer <owner token>`, `X-Brief-Publish: 1`, `Content-Type: audio/mpeg`, exact `Content-Length` and raw MP3 bytes. Do not use multipart. Size is capped at 8 MiB (suitable for approximately 7.36 MB episodes), below KV's 25 MiB limit. The streaming read enforces the cap even when a length is spoofed. The endpoint requires two consecutive MPEG Layer III frames after an optional ID3 header; this is a format sanity check, not a malware scanner or full decoder. Source files should come from the trusted publisher pipeline.

Optional `X-Episode-Title` is at most 120 characters. Optional `X-Episode-Chapters` is a JSON array of at most 30 `{ "title": "Introduction", "start": 0 }` entries (title up to 80 characters, start in seconds). The server generates the UUID and expiry; callers cannot choose KV keys or an expiration. Audio is written before metadata; a partial write is invisible and expires automatically. UUID writes avoid KV's one-write-per-key-per-second constraint. No update endpoint exists; personal audio has a separately confirmed, authenticated deletion endpoint described below. KV is eventually consistent: allow propagation before playback. The player lists up to 100 unexpired active-index keys per collection. Retained private metadata is not scanned for the current listing.

## Security and behavior

- A single SQLite Durable Object serializes a shared global limit of 10 PIN attempts per 15 minutes, including successful attempts, before expensive hashing. It cannot be bypassed with IP rotation; an attacker can temporarily lock out everyone. This deliberately conservative tradeoff suits a small shared player. No IP addresses are retained.
- Opaque random sessions are hashed in Durable Object storage, expire after 12 hours and use a `__Host-` Secure/HttpOnly/SameSite=Strict cookie. Logout deletes the session server-side. Session rows are periodically removed by an alarm. The DO is accessible only via its binding, not a public route. A single origin-wide PIN is shared access: anyone with the URL and PIN can listen and save authorized audio.
- Metadata, episode details, audio, and audio Range GET/HEAD all authenticate first. Single byte ranges, open-ended and suffix ranges are supported; malformed/multiple/unsatisfiable ranges receive 416. HEAD has the corresponding GET length without the body. All responses use private/no-store, no CORS, restrictive CSP and same-origin resource policy. No CDN Cache API is used. Responses check metadata expiry independently of KV propagation. An already downloaded or actively served audio response cannot be remotely revoked.
- Every write checks exact Origin. Cookie-authenticated writes also require the session CSRF token; publishing uses a distinct bearer token and required custom header, never the listener cookie. Browser secrets remain in memory only. Logging is disabled in the configuration; do not enable request-body/header logging.
- The mobile UI includes play/pause, progress seek, ±15 seconds, chapters and speed. Its blue/purple orb reacts only to audio-element frequencies through Web Audio, with paused and reduced-motion states. There is no microphone permission or recording.

## Validation and free-plan limits

`npm test` uses Node's built-in test runner and mocks KV/DO bindings. It covers anonymous/forged-session bypass, GET/HEAD protection, global guessing limit, salted PIN login and cookie flags, logout/CSRF, ranges and response bytes, cache/CSP, expiry, publishing authorization/setup gate, malformed media and upload size guards. These are unit/route tests, not proof of Cloudflare runtime or globally distributed behavior.

`node scripts/runtime-check.mjs` additionally launches Wrangler locally on port 9878 with isolated synthetic values and a fresh local `.wrangler/runtime-*` SQLite/KV store. It checks real workerd PIN verification, cookie sessions, a synthetic 7.36 MB upload and full/range/HEAD responses, and 11 concurrent login attempts. This script enables expiry only in that local synthetic store. It never contacts production storage. The runtime check and route/security/UI/retention tests pass locally. `npm run check` bundles successfully (about 20 KiB), and the locked Wrangler 4.151.1 dependency install reports zero npm audit vulnerabilities at preparation time. Local compatibility does not certify deployed CPU, memory or browser playback.

The 100,000 PBKDF2 iteration setting respects the production runtime cap; it is below modern password-hashing work-factor recommendations. The 12-digit minimum and global online limiter mitigate this for shared listening, but owner-chosen weak or reused PINs remain unsafe. Prefer a long unpredictable code. See the [Cloudflare runtime issue](https://github.com/cloudflare/workerd/issues/1346); explicitly verify the chosen work factor on deployment.

Workers Free documents 100,000 requests/day, 10 ms CPU per request and 128 MB isolate memory. KV Free provides 1 GB storage, 100,000 reads/day, 1,000 writes/day, 1,000 deletes/day and 1,000 lists/day; values cap at 25 MiB. Three KV writes per episode and list + one metadata read per listed episode apply. About seven 7.36 MB episodes occupy about 52 MB; do not treat the storage allowance as unlimited. SQLite Durable Objects are available on Free with their own request/storage quotas. There is no automatic paid-plan upgrade configured.

PIN PBKDF2 executes inside the Durable Object rather than the outer Worker's 10 ms path. Media buffering is capped at 8 MiB; a response slice and upload chunk assembly can temporarily duplicate buffers, so expected single-request data stays well below 128 MB. Multiple simultaneous requests share an isolate and can exceed that memory budget. Reading/slicing a ~7.36 MB KV value and upload validation/assembly may exceed 10 ms CPU: local tests cannot certify the production CPU cap. **Free-plan feasibility remains conditional on deployed measurement.** If it fails, reduce episode size/bitrate or redesign streamed bounded range delivery; do not silently enable paid features.

Before live use, measure Worker and DO CPU/memory in Cloudflare metrics with a synthetic ~7.36 MB MP3; test concurrent full/range playback, iOS Safari/Android seeking, expiry at the seven-day boundary, server-observed HEAD/Range headers, cross-origin attacks, 11 concurrent PIN requests, session revocation, KV propagation and cold starts. Confirm no Cloudflare cache rule overrides private responses. Use a separate test namespace for expiry experiments and obtain deletion approval first. Do not upload personal production episodes until these checks pass. Expiring keys and already served content cannot provide client-side erasure.

Official references: [Worker limits](https://developers.cloudflare.com/workers/platform/limits/), [KV limits](https://developers.cloudflare.com/kv/platform/limits/), [KV expiration and consistency](https://developers.cloudflare.com/kv/api/write-key-value-pairs/), [SQLite Durable Object storage](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/), [Durable Object limits](https://developers.cloudflare.com/durable-objects/platform/limits/), [pricing](https://developers.cloudflare.com/workers/platform/pricing/).

## Historical review follow-up validation

The staged counts below record earlier review milestones; current CI is authoritative for the present source.

The current test suite has 12 passing tests, including browser-script tests with a minimal DOM harness. A centralized reset clears the PIN, CSRF state, audio source, episode/chapter content and playback controls, then shows and focuses the PIN form on API 401 or expired-session logout. Media errors recheck the session because audio elements do not expose HTTP status. A generation guard prevents an older in-flight episode request from reopening a player after reset. Actual mobile/browser behavior still requires verification.

Authenticated HEAD ignores Range entirely and returns 200 with the full media Content-Length and no response body (RFC 9110 section 14.2). Unit and local runtime checks cover valid, malformed and unsatisfiable Range headers on HEAD.

Full GET now passes the existing KV ArrayBuffer directly to Response instead of making an additional full-size slice. Partial GET still buffers the whole KV value and copies the requested portion. Response construction and runtime transport may also allocate memory internally. Concurrent requests share the 128 MB isolate, and production 10 ms CPU/memory measurements remain deployment gates. The 7.36 MB synthetic runtime fixture verifies upload and byte transport only; it does not establish MP3 decoding, audible playback or mobile compatibility. A real nonpersonal MP3 and mobile checks remain required.

Playback review: pause now runs synchronously with no session request, including when offline. AudioContext resume and initial audio play are both invoked in the click handler before any await, preserving the mobile user gesture. Media access remains server-authenticated and audio errors use the existing session recheck/401 reset. All 14 tests pass, including regression tests for offline pause and gesture-timed play initiation; actual mobile autoplay behavior remains a browser verification gate.


The current regression suite includes audio-only expiry and retained-metadata isolation. Public HTML/news history remains independent. Feedback and prompt edits trigger CI, but player deployment does not execute or synchronize the external morning task; see [OPERATIONS.md](OPERATIONS.md) for the verified relay connection and remaining scheduled-run checks.


## Personal Podcasts

The authenticated player includes Today, Previous and Personal Podcasts. Topic
recordings show their title, upload date, measured duration when provided, chapter
count and seven-day expiry. Selecting a personal recording opens its chapters and
playback controls in that tab. Returning to Today selects the remembered daily
recording; personal uploads never become the daily latest. Selection/progress are
kept only in browser memory and cleared when the player is locked.

For direct listener uploads, set `X-Episode-Collection: personal`, required
`X-Episode-Key` matching `^[a-z0-9][a-z0-9-]{0,79}$`, and optional
`X-Episode-Duration` (finite seconds, greater than zero, at most 86400). Production
publishing must use the [relay contract](../PUBLISHING.md), whose stable personal
receipt prevents duplicate delivery; direct Worker uploads still create a new UUID
every time. Daily uploads omit the collection and key. Existing metadata and daily
active indexes need no migration.

Personal audio and its `active-personal:` index use the same approved seven-day
expiry. Private metadata, including any later deletion tombstone, stays retained.
The Delete button explains permanent hosted deletion and shared-PIN permissions
before its final confirmation. Deletion checks Origin, session, CSRF and explicit
ID; removes actual audio and active-index storage; preserves the metadata tombstone;
and supports safe retries. Daily recordings cannot be deleted through this feature.
Changes can take time to propagate across Cloudflare. No deletion is performed
merely by deploying this code.

Storage information is an authenticated estimate of listed active audio, not an
account-wide quota meter. It identifies partial counts and warns near 1 GB while
explaining excluded storage and independent request/compute limits. No billing or
permission change is needed. The collection/deletion/UI tests and local workerd
smoke test cover isolation, legacy defaults, authentication, cross-origin/CSRF
rejection, interrupted cleanup, repeated deletion, expiry, storage counts, keyboard
tabs, cancelled confirmation and stale-list handling. Physical-device playback and
global KV propagation remain separate production observations.

## Log book

Log book is the fourth authenticated tab. It uses the server's Asia/Singapore
calendar day, starts on the first authenticated Log book visit, and never creates
pre-start history. Today is the default view. Unfinished days from the preceding
five calendar days appear as optional catch-up choices; completed days do not
return just because one or more habits were missed. There is no end-of-day prompt,
notification, streak pressure or reminder schedule.

The five weekday habits are No smoke, No sugar, One way public transport, Fitness,
and Meditation. Saturday and Sunday omit public transport. Fitness is a single
habit, with optional walk, tennis, cycle and yoga activity labels. Checking a circle
animates a strike-through and removes that habit from the remaining list. The
checked tray offers Undo. Reduced-motion mode skips the animation and keyboard
focus moves to the next habit or Done.

Only Done stores a habit record. Each applicable habit is explicitly true or false,
so saved missed habits are distinct from an unlogged day. Unsaved selections are
kept in memory only and cleared by Lock, expiry or page reload. An uncertain save
freezes its original payload for an idempotent retry; a conflicting finalized day
shows the saved record rather than overwriting it. Finalized days are read-only.
The collapsed Week in view section shows saved Did / Didn't do summaries and
labels absent records Not logged. Weekend transport is not applicable.

Private records live in the already-bound Auth SQLite Durable Object, separately
from session keys and seven-day audio. No new service, binding, credential,
migration, repository-data write or paid plan is required. The first read stores
only schema/timezone/start-date configuration. A record has date, version, completed
status, exact applicable habit booleans, optional fitness activities and savedAt.
Habit records have no expiration; session cleanup does not delete them. Anyone
with the existing shared PIN can view and finalize these shared records. This is
shared access, not an owner-only identity system.

GET /api/logbook optionally accepts a Monday week date and returns the requested
week plus today/recent saved records, with server date and pending dates. PUT
/api/logbook/YYYY-MM-DD requires exact Origin, valid session, CSRF, JSON under
2 KiB and an expected version. The Durable Object rechecks session and CSRF inside
its serialized transaction. It refuses future/pre-start/out-of-window dates,
incomplete/mistyped booleans, weekend transport, unknown activities and conflicting
finalization. Exact retry receipts remain available after the entry window closes.
All responses retain private/no-store headers and the existing restrictive CSP.
Request-body logging remains disabled. No real habits or private identifiers are
included in source, fixtures, CI logs, screenshots or public reports.

Synthetic Node tests cover date rollover, catch-up boundaries, explicit false
values, authentication/CSRF, invalid inputs, concurrent writes, save retries,
read-only history, reset races, focus and reduced motion. The isolated local
workerd runtime check exercises SQLite persistence across a local process restart,
plus normal player regressions. These checks do not write production habit records.

Browser-model build note: after editing src/logbook-model.js, run
`node scripts/build-logbook-model.mjs` to refresh the checked-in browser source
literal. A test enforces exact parity. Do not serialize a build-transformed
function at Worker runtime: bundlers can inject helper references that do not
exist in the separate browser script. The workerd smoke test also executes the
exact served /app.js in an isolated synthetic DOM before testing authenticated
storage, so browser-bundle initialization is a deployment gate.

## Original and verified written views

Written editions default to **Original brief** when a same-date upstream archive exists. This retains the original dark/gold design, typography and section tabs, without executing upstream JavaScript. On narrow screens the section tabs use a horizontal touch-scroll strip so headlines remain visible. Written-edition dates are explicitly displayed in Asia/Singapore. **Verified companion** stays separate and contains checked coverage and the podcast-matching fact. Original text may include repeated or subsequently corrected claims; the view labels and source links make that distinction explicit. When there is no original for that date, the app says so and shows the companion; it never substitutes another date.

After every public report/manifest or upstream archive update, run the existing repository-root command `node podcast/cloudflare/scripts/build-reports.mjs`. It now generates both `src/reports.js` and `src/originals.js`; include both in the validated change set. No separate per-day viewer edits are needed. Archived upstream files are not modified.

Original snapshots are public-only static pages. The build parses literal data with Acorn, escapes text, filters source links and rejects unsupported CSS. It does not evaluate archive scripts. The viewer uses an opaque-origin sandbox with no scripts, forms or same-origin privileges, and a restrictive response CSP. Original fonts are locally embedded under their OFL licenses (see ORIGINAL-FONTS.md), with no third-party requests. Private audio, session, PIN and retention behavior are unchanged.

`node scripts/original-browser-check.mjs` (from this directory, after `npx playwright install --with-deps chromium`) checks 390px and 1280px rendering, locally loaded fonts, section controls, both facts, view switching, unavailable originals and Back/Lock cleanup using synthetic session responses. CI retains only public-content screenshots for seven days; it never uses production PINs, private episodes or playback metadata. Local socket restrictions may prevent browser/workerd startup; hosted CI remains the required deployment gate.

## Focused Today view and daily reflection (22 October 2026)

Today selects only the current Asia/Singapore edition (explicit edition date,
falling back to Singapore upload date for legacy metadata). Older audio stays in
Previous, including when selected for playback. Missing same-day audio or HTML is
labelled unavailable; it is never replaced with yesterday's edition. The reading
button opens the existing isolated Original brief/Verified companion reader and
returns to Today. Personal Podcasts and private storage behavior are unchanged.

The compact header uses 30 original, unattributed reflections, explicitly labelled
“Daily reflection”. These are not quotations from named people. The deterministic
Singapore-date rotation repeats every 30 days. It updates on opening, tab changes
and a local once-per-minute date check, without a remote service, schedule, data
collection, or reminders. Long text wraps responsively.

Checking a Log book item opens a native modal celebration. Keep going or Escape
closes it, then the completed label appears struck through with Undo. Native
modal focus containment and reduced-motion styling apply. Navigation and Lock
clean it up, and reloading a saved record never celebrates it again. As before,
checking is a session-only draft; Done is the explicit private save. No schema,
record, access, authentication, retention, or persistence migration is introduced.

`node scripts/daily-layout-browser-check.mjs` covers synthetic-only 390/1280-pixel
views, motion preferences, focus/Escape, undo, same-day reading, Previous playback,
and Singapore midnight rollover. It never accesses or changes owner task state.
