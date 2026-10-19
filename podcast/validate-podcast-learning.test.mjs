import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { validatePodcastLearningLedger, selectPodcastLearning, recordPodcastState, recordPodcastPublication, sgtDate, canonicalPodcastIdentity } from './validate-podcast-learning.mjs';

const original = JSON.parse(fs.readFileSync(new URL('./test-fixtures/podcast-learning-ledger.fixture.json', import.meta.url), 'utf8'));
const shipped = JSON.parse(fs.readFileSync(new URL('./podcast-learning-ledger.json', import.meta.url), 'utf8'));

test('shipped persistent ledger validates independently of its future size/state', () => {
  assert.deepEqual(validatePodcastLearningLedger(shipped), []);
});
const now = '2026-10-19T00:30:00Z';
const copy = value => structuredClone(value);
function context(time = now) {
  return { date_sgt: sgtDate(time), as_of: time, primary_check: { status: 'complete', checked_at: time }, fallback_check: { status: 'complete', checked_at: time }, candidates: [] };
}
function readyLedger(time = now) {
  const ledger = copy(original);
  for (const entry of ledger.episodes) {
    entry.transcript.checked_at = time;
    entry.dedup_review = { status: 'clear', story_keys: [entry.episode_id + ':new-explanation'], contribution: null, reviewed_at: time };
  }
  return ledger;
}
function candidate(id = 'everyday-ai:new', time = now) {
  const entry = copy(readyLedger(time).episodes[0]);
  entry.episode_id = id; entry.show = id.startsWith('big-technology:') ? 'big-technology' : 'everyday-ai'; entry.title = 'New substantive learning';
  entry.source_url = `https://example.org/episodes/${id}`; entry.aliases = [];
  entry.published_at = '2026-10-18T12:00:00Z';
  return entry;
}
function evidence(episode_id, overrides = {}) {
  return { publication_id: 'brief-2026-10-19-podcast', episode_id, status: 'verified_published', output_url: 'https://pbhat89.github.io/the-brief/podcast/reports/2026-10-19.html', revision: '1', content_sha256: 'a'.repeat(64), verified_at: '2026-10-19T00:31:00Z', confirmation: 'Opened the live report and verified this episode recap and its exact artifact hash.', ...overrides };
}
function finishSeed(ledger = readyLedger()) {
  for (const entry of ledger.episodes) { entry.status = 'skip'; entry.status_reason = 'No distinct useful content after full history review'; }
  return ledger;
}

test('synthetic initial ledger validates and has no publication/coverage claims', () => {
  assert.deepEqual(validatePodcastLearningLedger(original), []);
  assert.equal(original.episodes.length, 3);
  assert.equal(original.publications.length, 0);
  assert.ok(original.episodes.every(e => e.status === 'pending' && e.dedup_review.status === 'pending' && e.transcript.provenance === 'third-party-transcription'));
  assert.equal(selectPodcastLearning(original, context()).reason, 'catchup_pending_evidence');
});
test('SGT date boundary is UTC+8, independent of host timezone', () => {
  assert.equal(sgtDate('2026-10-18T15:59:59Z'), '2026-10-18');
  assert.equal(sgtDate('2026-10-18T16:00:00Z'), '2026-10-19');
  assert.throws(() => selectPodcastLearning(readyLedger(), { ...context(), date_sgt: '2026-10-18' }), /date_sgt/);
});
test('catchup chooses newest seed first without mutation or expansion', () => {
  const ledger = readyLedger(); const before = JSON.stringify(ledger); const c = context(); c.candidates = [candidate('big-technology:even-newer')];
  assert.equal(selectPodcastLearning(ledger, c).episode_id, ledger.catchup.seed_episode_ids[0]);
  assert.equal(JSON.stringify(ledger), before);
});
test('Everyday AI takes the only slot while catchup stays intact', () => {
  const ledger = readyLedger(); const c = context(); c.candidates = [candidate()];
  const chosen = selectPodcastLearning(ledger, c);
  assert.equal(chosen.episode_id, 'everyday-ai:new'); assert.equal(chosen.reason, 'everyday_ai_precedence');
  assert.deepEqual(ledger.catchup, original.catchup);
});
test('replay, promotional, non-substantive and beginner Everyday AI items cannot win', () => {
  for (const change of [{ replay: true }, { promotional: true }, { substantive: false }, { beginner_series: true }]) {
    const c = context(); const e = candidate(); Object.assign(e.classification, change); c.candidates = [e];
    assert.equal(selectPodcastLearning(readyLedger(), c).show, 'big-technology');
  }
});
test('substantive Big Technology how-to remains eligible', () => {
  const ledger = readyLedger(); ledger.episodes[0].title = 'How to understand a technical system'; ledger.episodes[0].classification.beginner_series = true;
  assert.equal(selectPodcastLearning(ledger, context()).episode_id, ledger.episodes[0].episode_id);
});
test('primary inaccessible transcript invokes fallback, not title-derived summary', () => {
  const c = context(); const e = candidate(); e.transcript.status = 'unavailable'; e.transcript.body_retrieved = false; c.candidates = [e];
  assert.equal(selectPodcastLearning(readyLedger(), c).reason, 'big_technology_catchup');
});
test('source outage needs a reason; current primary and fallback checks are required', () => {
  const c = context(); c.primary_check.status = 'inaccessible';
  assert.throws(() => selectPodcastLearning(readyLedger(), c), /Everyday AI source check/);
  c.primary_check.reason = 'Official source returned an access error';
  assert.equal(selectPodcastLearning(readyLedger(), c).show, 'big-technology');
  delete c.fallback_check;
  assert.equal(selectPodcastLearning(readyLedger(), c).reason, 'fallback_source_check_required');
  delete c.primary_check;
  assert.throws(() => selectPodcastLearning(readyLedger(), c), /Everyday AI source check/);
});
test('inaccessible or deferred seed remains uncovered and next seed may be selected', () => {
  let ledger = readyLedger(); ledger.episodes[0].transcript.status = 'unavailable'; ledger.episodes[0].transcript.body_retrieved = false;
  ledger = recordPodcastState(ledger, { episode_id: ledger.episodes[0].episode_id, status: 'deferred', reason: 'Transcript is temporarily unavailable', recorded_at: now });
  assert.equal(selectPodcastLearning(ledger, context()).episode_id, ledger.episodes[1].episode_id);
  assert.equal(ledger.publications.length, 0); assert.equal(ledger.episodes[0].status, 'deferred');
});
test('stale transcript access or story review cannot produce a recap', () => {
  for (const field of ['transcript', 'dedup_review']) {
    const ledger = readyLedger();
    for (const e of ledger.episodes) e[field][field === 'transcript' ? 'checked_at' : 'reviewed_at'] = '2026-10-17T00:00:00Z';
    assert.equal(selectPodcastLearning(ledger, context()).episode_id, null);
  }
});
test('duplicate underlying story needs a documented distinct contribution', () => {
  const ledger = readyLedger(); ledger.episodes[0].dedup_review.status = 'duplicate';
  assert.equal(selectPodcastLearning(ledger, context()).episode_id, ledger.episodes[1].episode_id);
  ledger.episodes[0].dedup_review.status = 'distinct_contribution';
  assert.ok(validatePodcastLearningLedger(ledger).some(x => x.includes('distinct contribution')));
  ledger.episodes[0].dedup_review.contribution = 'Explains the cost mechanism rather than repeating the previously covered announcement';
  assert.equal(selectPodcastLearning(ledger, context()).episode_id, ledger.episodes[0].episode_id);
});
test('Roose video alias resolves to the same episode and preserves RSS date', () => {
  const ledger = readyLedger(); const e = copy(ledger.episodes[1]);
  e.episode_id = 'youtube:fixture-roose'; e.source_url = 'https://example.org/video/fixture-roose'; e.title = 'AI Leaders Cannot Get Along'; e.published_at = '2026-10-18T23:00:00Z';
  const c = context(); c.candidates = [e]; ledger.episodes[0].status = 'skip'; ledger.episodes[0].status_reason = 'Duplicate story';
  const selected = selectPodcastLearning(ledger, c);
  assert.equal(selected.episode_id, ledger.episodes[1].episode_id);
  assert.equal(selected.episode.published_at, ledger.episodes[1].published_at);
});
test('fixed seed and alias collisions are validated', () => {
  const ledger = readyLedger(); ledger.catchup.seed_episode_ids.pop();
  assert.ok(validatePodcastLearningLedger(ledger).some(x => x.includes('three-episode')));
  const duplicate = readyLedger(); duplicate.episodes[2].aliases.push(duplicate.episodes[1].aliases[0]);
  assert.ok(validatePodcastLearningLedger(duplicate).some(x => x.includes('alias collision')));
});
test('latest-only chooses newest original and never older unseen backfill', () => {
  const ledger = finishSeed(); const c = context(); const old = candidate('big-technology:older-unseen'); old.published_at = '2026-10-08T00:00:00Z'; c.candidates = [old];
  assert.equal(selectPodcastLearning(ledger, c).episode_id, null);
  const fresh = candidate('big-technology:fresh'); c.candidates.push(fresh);
  assert.equal(selectPodcastLearning(ledger, c).episode_id, fresh.episode_id);
  fresh.transcript.status = 'unavailable'; fresh.transcript.body_retrieved = false;
  assert.equal(selectPodcastLearning(ledger, c).reason, 'latest_evidence_unavailable');
});
test('future episode metadata is never eligible', () => {
  const c = context(); const e = candidate(); e.published_at = '2026-10-20T00:00:00Z'; c.candidates = [e];
  assert.equal(selectPodcastLearning(readyLedger(), c).show, 'big-technology');
});
test('draft/commit evidence and unselected publication are rejected', () => {
  const ledger = readyLedger(); const id = ledger.episodes[0].episode_id;
  assert.throws(() => recordPodcastPublication(ledger, context(), evidence(id, { status: 'drafted' })), /Verified live/);
  assert.throws(() => recordPodcastPublication(ledger, context(), evidence(ledger.episodes[1].episode_id)), /selected episode/);
  assert.throws(() => recordPodcastState(ledger, { episode_id: id, status: 'published', recorded_at: now }), /recordPodcastPublication/);
  assert.equal(ledger.publications.length, 0);
});
test('publication is immutable-input, evidence-backed, idempotent and one slot per SGT date', () => {
  const ledger = readyLedger(); const before = JSON.stringify(ledger); const c = context(); const ev = evidence(ledger.episodes[0].episode_id);
  const next = recordPodcastPublication(ledger, c, ev);
  assert.equal(JSON.stringify(ledger), before); assert.deepEqual(validatePodcastLearningLedger(next), []);
  assert.equal(next.episodes[0].status, 'published'); assert.equal(next.publications.length, 1);
  assert.deepEqual(recordPodcastPublication(next, c, ev), next);
  assert.equal(selectPodcastLearning(next, c).reason, 'daily_slot_already_published');
  const primaryContext = context(); primaryContext.candidates = [candidate()];
  assert.equal(selectPodcastLearning(next, primaryContext).episode_id, null);
  assert.throws(() => recordPodcastPublication(next, primaryContext, evidence('everyday-ai:new', { publication_id: 'revision-2', revision: '2' })), /unused daily slot/);
  assert.throws(() => recordPodcastPublication(next, c, { ...ev, revision: '2' }), /different evidence/);
});
test('cannot bypass Everyday AI precedence at publication time', () => {
  const ledger = readyLedger(); const c = context(); c.candidates = [candidate()];
  assert.throws(() => recordPodcastPublication(ledger, c, evidence(ledger.episodes[0].episode_id)), /selected episode/);
});
test('next SGT date resumes next pending seed, without repeating prior episode', () => {
  let ledger = readyLedger(); ledger = recordPodcastPublication(ledger, context(), evidence(ledger.episodes[0].episode_id));
  const time = '2026-10-20T00:30:00Z'; const c = context(time);
  c.candidates = ledger.episodes.map(e => ({ ...copy(e), transcript: { ...e.transcript, checked_at: time }, dedup_review: { ...e.dedup_review, reviewed_at: time } }));
  assert.equal(selectPodcastLearning(ledger, c).episode_id, ledger.episodes[1].episode_id);
  assert.deepEqual(ledger.catchup, original.catchup);
});
test('forged published ledger without matching output evidence fails validation', () => {
  const ledger = readyLedger(); ledger.episodes[0].status = 'published'; ledger.episodes[0].publication_id = 'missing';
  assert.ok(validatePodcastLearningLedger(ledger).some(x => x.includes('matching evidence')));
});


test('an older unseen but ready Everyday AI original beats fallback when newest transcript is unavailable', () => {
  const c = context(); const latest = candidate('everyday-ai:latest'); const earlier = candidate('everyday-ai:earlier');
  latest.transcript.status = 'unavailable'; latest.transcript.body_retrieved = false;
  earlier.published_at = '2026-10-17T12:00:00Z'; c.candidates = [latest, earlier];
  assert.equal(selectPodcastLearning(readyLedger(), c).episode_id, earlier.episode_id);
});
test('exact publication retry remains idempotent after later ledger updates', () => {
  const ledger = readyLedger(); const c = context(); const ev = evidence(ledger.episodes[0].episode_id);
  let next = recordPodcastPublication(ledger, c, ev);
  next = recordPodcastState(next, { episode_id: ledger.episodes[1].episode_id, status: 'deferred', reason: 'Needs source recheck', recorded_at: '2026-10-20T00:30:00Z' });
  assert.deepEqual(recordPodcastPublication(next, c, ev), next);
});
test('YouTube and Apple URL variants canonicalize to episode identities', () => {
  for (const address of ['https://youtu.be/TmMYvtp4abI?si=abc', 'https://www.youtube.com/watch?v=TmMYvtp4abI&utm_source=test&t=30', 'https://youtube.com/live/TmMYvtp4abI']) assert.equal(canonicalPodcastIdentity(address), 'youtube:TmMYvtp4abI');
  assert.equal(canonicalPodcastIdentity('https://podcasts.apple.com/sg/podcast/renamed/id1522960417?i=1000796329967&uo=4'), 'apple:1000796329967');
});
test('private listener and token-bearing publication URLs are rejected', () => {
  const ledger = readyLedger(); const id = ledger.episodes[0].episode_id;
  for (const address of ['https://listener.workers.dev/listen', 'https://pbhat89.github.io/the-brief/podcast/reports/2026-10-19.html?token=secret', 'https://pbhat89.github.io/the-brief/podcast/reports/2026-10-19.html#secret', 'https://pbhat89.github.io/the-brief/listen/2026-10-19.html']) assert.throws(() => recordPodcastPublication(ledger, context(), evidence(id, { output_url: address })), /Verified live/);
});


test('public writes strip private receipts, listener URLs and transcript bodies', () => {
  const ledger = readyLedger(); const c = context(); const e = candidate();
  e.listener_url = 'https://private-listener.workers.dev/?token=secret'; e.private_receipt = { personal: 'private' };
  e.transcript.transcript_body = 'Do not persist raw copyrighted or private transcript bodies';
  c.candidates = [e];
  const next = recordPodcastPublication(ledger, c, evidence(e.episode_id, { listener_url: e.listener_url, private_receipt: e.private_receipt, transcript_body: 'private body' }));
  const serialized = JSON.stringify(next);
  assert.ok(!serialized.includes('listener_url') && !serialized.includes('private_receipt') && !serialized.includes('transcript_body') && !serialized.includes('token=secret'));
  assert.deepEqual(validatePodcastLearningLedger(next), []);
  next.publications[0].private_receipt = 'not allowed';
  assert.ok(validatePodcastLearningLedger(next).some(x => x.includes('unexpected fields')));
});
