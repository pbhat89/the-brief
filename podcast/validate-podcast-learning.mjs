import fs from 'node:fs';
import { pathToFileURL } from 'node:url';

const SHOWS = new Set(['everyday-ai', 'big-technology']);
const STATES = new Set(['pending', 'deferred', 'skip', 'published']);
const TERMINAL = new Set(['skip', 'published']);
const PROVENANCE = new Set(['publisher-transcript', 'official-channel-captions', 'third-party-transcription']);
const text = value => typeof value === 'string' && value.trim().length > 0;
const instant = value => text(value) && /(?:Z|[+-]\d\d:\d\d)$/.test(value) && Number.isFinite(Date.parse(value));
const day = value => /^\d{4}-\d{2}-\d{2}$/.test(value ?? '') && Number.isFinite(Date.parse(value)) && new Date(value).toISOString().slice(0, 10) === value;
const url = value => { try { const u = new URL(value); return u.protocol === 'https:' && !u.username && !u.password && !/^(localhost|127\.|0\.|\[::1\])/.test(u.hostname) && ![...u.searchParams.keys()].some(k => /token|secret|signature|password|credential|api.?key/i.test(k)); } catch { return false; } };
export const sgtDate = value => {
  if (!instant(value)) throw new Error('An ISO timestamp with timezone is required');
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Singapore', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date(value));
};
export function canonicalPodcastIdentity(value) {
  if (!text(value)) return value;
  try {
    const u = new URL(value); const host = u.hostname.toLowerCase().replace(/^www\./, '');
    if (['youtube.com', 'm.youtube.com', 'youtu.be'].includes(host)) {
      const parts = u.pathname.split('/').filter(Boolean);
      const id = host === 'youtu.be' ? parts[0] : u.searchParams.get('v') ?? (['live', 'shorts', 'embed'].includes(parts[0]) ? parts[1] : null);
      if (id) return `youtube:${id}`;
    }
    if (host === 'podcasts.apple.com' && /^\d+$/.test(u.searchParams.get('i') ?? '')) return `apple:${u.searchParams.get('i')}`;
    u.hash = '';
    for (const key of [...u.searchParams.keys()]) if (/^utm_|^(fbclid|gclid)$/i.test(key)) u.searchParams.delete(key);
    u.searchParams.sort(); return u.href;
  } catch { return value.trim(); }
}
const identityKeys = entry => [...new Set([entry.episode_id, ...(entry.aliases ?? []), entry.source_url].filter(text).map(canonicalPodcastIdentity))];
const publicReportUrl = value => {
  try {
    const u = new URL(value);
    return u.protocol === 'https:' && u.hostname === 'pbhat89.github.io' && !u.username && !u.password && !u.search && !u.hash
      && /^\/the-brief\/(?:archive|podcast\/reports)\/\d{4}-\d{2}-\d{2}(?:-[a-z0-9-]+)?\.html$/.test(u.pathname);
  } catch { return false; }
};

const ENTRY_FIELDS = ['episode_id', 'show', 'title', 'published_at', 'source_url', 'aliases', 'classification', 'transcript', 'dedup_review', 'status', 'status_reason', 'publication_id'];
const CLASSIFICATION_FIELDS = ['original', 'substantive', 'replay', 'promotional', 'beginner_series'];
const TRANSCRIPT_FIELDS = ['status', 'body_retrieved', 'source_url', 'provenance', 'checked_at', 'access_note'];
const DEDUP_FIELDS = ['status', 'story_keys', 'contribution', 'reviewed_at'];
const EVIDENCE_FIELDS = ['publication_id', 'episode_id', 'status', 'output_url', 'revision', 'content_sha256', 'verified_at', 'confirmation'];
const pick = (object, fields) => Object.fromEntries(fields.filter(k => Object.hasOwn(object ?? {}, k)).map(k => [k, object[k]]));
function publicEpisode(entry) {
  return { ...pick(entry, ENTRY_FIELDS), classification: pick(entry.classification, CLASSIFICATION_FIELDS), transcript: pick(entry.transcript, TRANSCRIPT_FIELDS), dedup_review: pick(entry.dedup_review, DEDUP_FIELDS) };
}

/** Structural/state validation only. Editorial judgments and live evidence must be verified by the caller. */
export function validatePodcastLearningLedger(ledger) {
  const errors = [];
  const check = (ok, message) => { if (!ok) errors.push(message); };
  if (!ledger || typeof ledger !== 'object') return ['ledger must be an object'];
  check(ledger.version === 1, 'version must be 1');
  check(ledger.timezone === 'Asia/Singapore', 'timezone must be Asia/Singapore');
  check(ledger.daily_limit === 1, 'daily_limit must be 1 across shows and revisions');
  check(instant(ledger.updated_at), 'updated_at must be an ISO timestamp with timezone');
  if (!Array.isArray(ledger.episodes) || !Array.isArray(ledger.publications)) return [...errors, 'episodes and publications must be arrays'];
  const allowed = (object, keys, at) => check(object && typeof object === 'object' && Object.keys(object).every(k => keys.includes(k)), `${at}: unexpected fields are not allowed in the public ledger`);
  allowed(ledger, ['version', 'timezone', 'daily_limit', 'updated_at', 'catchup', 'episodes', 'publications'], 'ledger');
  if (ledger.catchup) allowed(ledger.catchup, ['initialized_at', 'limit', 'order', 'seed_episode_ids'], 'catchup');
  const ids = new Map(); const identities = new Map();
  for (const [i, entry] of ledger.episodes.entries()) {
    const at = `episodes[${i}]`;
    if (!entry || typeof entry !== 'object') { errors.push(`${at} must be an object`); continue; }
    allowed(entry, ENTRY_FIELDS, at);
    if (entry.classification) allowed(entry.classification, CLASSIFICATION_FIELDS, at + '.classification');
    if (entry.transcript) allowed(entry.transcript, TRANSCRIPT_FIELDS, at + '.transcript');
    if (entry.dedup_review) allowed(entry.dedup_review, DEDUP_FIELDS, at + '.dedup_review');
    check(text(entry.episode_id) && !ids.has(entry.episode_id), `${at}: unique episode_id required`); ids.set(entry.episode_id, entry);
    check(SHOWS.has(entry.show), `${at}: unsupported show`);
    check(text(entry.title) && instant(entry.published_at) && url(entry.source_url), `${at}: title, original publication time and source URL required`);
    check(Array.isArray(entry.aliases) && entry.aliases.every(text), `${at}: aliases must be strings`);
    for (const key of identityKeys({ ...entry, aliases: Array.isArray(entry.aliases) ? entry.aliases : [] })) {
      check(!identities.has(key) || identities.get(key) === entry.episode_id, `${at}: alias collision: ${key}`); identities.set(key, entry.episode_id);
    }
    check(STATES.has(entry.status), `${at}: invalid status`);
    if (['skip', 'deferred'].includes(entry.status)) check(text(entry.status_reason), `${at}: ${entry.status} requires a reason`);
    const c = entry.classification;
    check(c && ['original', 'substantive', 'replay', 'promotional', 'beginner_series'].every(k => typeof c[k] === 'boolean'), `${at}: explicit classification required`);
    const t = entry.transcript;
    check(t && ['retrieved', 'unavailable', 'unverified'].includes(t.status), `${at}: explicit transcript status required`);
    if (t?.status === 'retrieved') check(t.body_retrieved === true && url(t.source_url) && PROVENANCE.has(t.provenance) && instant(t.checked_at), `${at}: retrieved transcript needs actual body evidence, URL, provenance and check time`);
    const d = entry.dedup_review;
    check(d && ['pending', 'clear', 'distinct_contribution', 'duplicate'].includes(d.status) && Array.isArray(d.story_keys) && d.story_keys.every(text), `${at}: explicit story dedup review required`);
    if (['clear', 'distinct_contribution'].includes(d?.status)) check(d.story_keys?.length > 0 && instant(d.reviewed_at), `${at}: completed dedup review needs story keys and review time`);
    if (d?.status === 'distinct_contribution') check(text(d.contribution), `${at}: distinct contribution must be explained`);
    if (entry.status === 'published') check(text(entry.publication_id), `${at}: published requires publication_id`);
    else check(entry.publication_id == null, `${at}: unpublished episode cannot carry publication_id`);
    if ('covered' in entry) check(entry.covered === (entry.status === 'published'), `${at}: covered is true only after publication`);
  }
  const seed = ledger.catchup;
  check(seed && instant(seed.initialized_at) && seed.limit === 3 && seed.order === 'newest-first' && Array.isArray(seed.seed_episode_ids) && seed.seed_episode_ids.length === 3 && new Set(seed.seed_episode_ids).size === 3, 'catchup must retain its fixed, unique three-episode newest-first seed');
  if (Array.isArray(seed?.seed_episode_ids)) {
    let previous = Infinity;
    for (const id of seed.seed_episode_ids) {
      const entry = ids.get(id); check(entry?.show === 'big-technology', `seed ${id}: Big Technology episode required`);
      const time = Date.parse(entry?.published_at); check(time <= previous, 'catchup seed must be newest first'); previous = time;
      check(time <= Date.parse(seed.initialized_at), `seed ${id}: cannot postdate initialization`);
    }
  }
  const dates = new Set(); const publicationIds = new Set(); const usedEpisodes = new Set();
  for (const [i, p] of ledger.publications.entries()) {
    const at = `publications[${i}]`;
    if (!p || typeof p !== 'object') { errors.push(`${at}: object required`); continue; }
    allowed(p, [...EVIDENCE_FIELDS, 'date_sgt', 'show'], at);
    check(text(p.publication_id) && !publicationIds.has(p.publication_id), `${at}: unique publication_id required`); publicationIds.add(p.publication_id);
    check(day(p.date_sgt) && !dates.has(p.date_sgt), `${at}: only one recap per SGT date across shows/revisions`); dates.add(p.date_sgt);
    check(!usedEpisodes.has(p.episode_id), `${at}: episode already covered`); usedEpisodes.add(p.episode_id);
    check(p.status === 'verified_published' && publicReportUrl(p.output_url) && text(p.revision) && /^[a-f0-9]{64}$/.test(p.content_sha256 ?? '') && instant(p.verified_at) && text(p.confirmation), `${at}: verified publication evidence required`);
    check(typeof p.output_url === 'string' && p.output_url.includes('/' + p.date_sgt), `${at}: public report must match the SGT edition date`);
    const entry = ids.get(p.episode_id);
    check(entry?.status === 'published' && entry.publication_id === p.publication_id && entry.show === p.show, `${at}: publication must match a published episode`);
    check(instant(p.verified_at) && Date.parse(p.verified_at) <= Date.parse(ledger.updated_at), `${at}: evidence cannot postdate updated_at`);
  }
  for (const entry of ledger.episodes) if (entry?.status === 'published') check(ledger.publications.some(p => p.episode_id === entry.episode_id && p.publication_id === entry.publication_id), `${entry.episode_id}: published state requires matching evidence`);
  return errors;
}
const assertLedger = ledger => { const errors = validatePodcastLearningLedger(ledger); if (errors.length) throw new Error(errors.join('\n')); };
const clone = value => JSON.parse(JSON.stringify(value));

/** Merge same-episode aliases while preserving the authoritative ledger's publication state. */
function candidatesFor(ledger, context) {
  const entries = new Map(ledger.episodes.map(e => [e.episode_id, clone(e)]));
  const keys = new Map();
  for (const entry of entries.values()) for (const key of identityKeys(entry)) keys.set(key, entry.episode_id);
  for (const supplied of context.candidates ?? []) {
    if (!supplied || !text(supplied.episode_id)) throw new Error('Candidate episode_id required');
    const matches = new Set(identityKeys(supplied).map(k => keys.get(k)).filter(Boolean));
    if (supplied.canonical_episode_id) matches.add(supplied.canonical_episode_id);
    if (matches.size > 1) throw new Error('Candidate aliases identify conflicting episodes');
    const id = [...matches][0] ?? supplied.episode_id;
    const existing = entries.get(id);
    if (matches.size && !existing) throw new Error('Unknown canonical_episode_id');
    if (existing && supplied.show !== existing.show) throw new Error('Candidate alias crosses shows');
    const merged = { ...clone(publicEpisode(supplied)), ...(existing ? { title: existing.title, published_at: existing.published_at, source_url: existing.source_url } : {}), episode_id: id, aliases: [...new Set([...(existing?.aliases ?? []), ...identityKeys(supplied)].filter(k => k !== id))], status: existing?.status ?? 'pending', status_reason: existing?.status_reason ?? null, publication_id: existing?.publication_id ?? null };
    entries.set(id, merged);
    for (const key of identityKeys(merged)) keys.set(key, id);
  }
  const test = { ...ledger, episodes: [...entries.values()] };
  assertLedger(test);
  return [...entries.values()];
}
function qualifies(entry, asOf) {
  const c = entry.classification;
  return c.original && c.substantive && !c.replay && !c.promotional && !(entry.show === 'everyday-ai' && c.beginner_series)
    && Date.parse(entry.published_at) <= Date.parse(asOf);
}
function ready(entry, context) {
  const t = entry.transcript; const d = entry.dedup_review;
  return t.status === 'retrieved' && t.body_retrieved === true && PROVENANCE.has(t.provenance)
    && sgtDate(t.checked_at) === context.date_sgt && Date.parse(t.checked_at) <= Date.parse(context.as_of)
    && ['clear', 'distinct_contribution'].includes(d.status) && sgtDate(d.reviewed_at) === context.date_sgt && Date.parse(d.reviewed_at) <= Date.parse(context.as_of);
}
const newest = entries => [...entries].sort((a, b) => Date.parse(b.published_at) - Date.parse(a.published_at) || a.episode_id.localeCompare(b.episode_id));

/** Pure selection: no fetch, state mutation, or inferred transcript access. */
export function selectPodcastLearning(ledger, context) {
  assertLedger(ledger);
  if (!context || !day(context.date_sgt) || !instant(context.as_of) || sgtDate(context.as_of) !== context.date_sgt) throw new Error('Context date_sgt must match as_of in Asia/Singapore');
  const previous = ledger.publications.find(p => p.date_sgt === context.date_sgt);
  if (previous) return { episode_id: null, reason: 'daily_slot_already_published', existing_episode_id: previous.episode_id };
  const check = context.primary_check;
  if (!check || !['complete', 'inaccessible'].includes(check.status) || !instant(check.checked_at) || sgtDate(check.checked_at) !== context.date_sgt || Date.parse(check.checked_at) > Date.parse(context.as_of) || (check.status === 'inaccessible' && !text(check.reason))) throw new Error('A current Everyday AI source check is required before fallback');
  const candidates = candidatesFor(ledger, context);
  const primaryOriginals = candidates.filter(e => e.show === 'everyday-ai' && !TERMINAL.has(e.status) && qualifies(e, context.as_of));
  const primary = newest(primaryOriginals.filter(e => ready(e, context)))[0];
  if (check.status === 'complete' && primary && ready(primary, context)) return { episode_id: primary.episode_id, show: primary.show, reason: 'everyday_ai_precedence', episode: primary };
  const primaryReason = check.status === 'inaccessible' ? 'source_inaccessible' : !primaryOriginals.length ? 'no_new_qualifying_original' : 'transcript_or_editorial_evidence_unavailable';
  const fallbackCheck = context.fallback_check;
  if (!fallbackCheck || fallbackCheck.status !== 'complete' || !instant(fallbackCheck.checked_at) || sgtDate(fallbackCheck.checked_at) !== context.date_sgt || Date.parse(fallbackCheck.checked_at) > Date.parse(context.as_of)) return { episode_id: null, reason: 'fallback_source_check_required', primary_reason: primaryReason };
  const seed = ledger.catchup.seed_episode_ids.map(id => candidates.find(e => e.episode_id === id));
  const pending = seed.filter(e => !TERMINAL.has(e.status));
  if (pending.length) {
    const chosen = pending.find(e => qualifies(e, context.as_of) && ready(e, context));
    return chosen ? { episode_id: chosen.episode_id, show: chosen.show, reason: 'big_technology_catchup', primary_reason: primaryReason, episode: chosen }
      : { episode_id: null, reason: 'catchup_pending_evidence', primary_reason: primaryReason };
  }
  // Choose the latest qualifying original BEFORE coverage/transcript checks: no older backfill.
  const latest = newest(candidates.filter(e => e.show === 'big-technology' && qualifies(e, context.as_of)))[0];
  if (!latest || TERMINAL.has(latest.status)) return { episode_id: null, reason: 'latest_already_covered_or_excluded', primary_reason: primaryReason };
  if (!ready(latest, context)) return { episode_id: null, reason: 'latest_evidence_unavailable', primary_reason: primaryReason };
  return { episode_id: latest.episode_id, show: latest.show, reason: 'big_technology_latest_only', primary_reason: primaryReason, episode: latest };
}

/** Record a reversible research/editorial state. This function cannot mark publication. */
export function recordPodcastState(ledger, { episode_id, status, reason = null, recorded_at }) {
  assertLedger(ledger);
  if (!['pending', 'deferred', 'skip'].includes(status)) throw new Error('Use recordPodcastPublication for published state');
  if (!instant(recorded_at) || Date.parse(recorded_at) < Date.parse(ledger.updated_at)) throw new Error('recorded_at must not precede ledger updated_at');
  const next = clone(ledger); const entry = next.episodes.find(e => e.episode_id === episode_id || e.aliases.includes(episode_id));
  if (!entry || entry.status === 'published') throw new Error('Cannot change an unknown or published episode');
  entry.status = status; entry.status_reason = reason; next.updated_at = recorded_at;
  assertLedger(next); return next;
}

/** Re-select under the same current facts, then record only a verified live publication. */
export function recordPodcastPublication(ledger, context, evidence) {
  assertLedger(ledger);
  if (!evidence || evidence.status !== 'verified_published' || !text(evidence.publication_id) || !publicReportUrl(evidence.output_url) || !text(evidence.revision) || !/^[a-f0-9]{64}$/.test(evidence.content_sha256 ?? '') || !instant(evidence.verified_at) || !text(evidence.confirmation)) throw new Error('Verified live publication evidence is required; a draft, commit, or successful upload alone is insufficient');
  const previous = ledger.publications.find(p => p.publication_id === evidence.publication_id);
  if (previous) {
    const same = ['episode_id', 'status', 'output_url', 'revision', 'content_sha256', 'verified_at', 'confirmation'].every(k => previous[k] === evidence[k]) && previous.date_sgt === context.date_sgt;
    if (!same) throw new Error('Publication ID already exists with different evidence');
    return clone(ledger); // Exact retry only; revisions cannot consume a second slot.
  }
  if (Date.parse(evidence.verified_at) < Date.parse(ledger.updated_at)) throw new Error('Publication verification cannot predate the ledger');
  if (Date.parse(evidence.verified_at) < Date.parse(context.as_of)) throw new Error('Publication verification must follow selection');
  const decision = selectPodcastLearning(ledger, context);
  if (!decision.episode_id || decision.episode_id !== evidence.episode_id) throw new Error('Publication must match the eligible selected episode and unused daily slot');
  const next = clone(ledger); const entry = clone(decision.episode);
  entry.status = 'published'; entry.status_reason = null; entry.publication_id = evidence.publication_id;
  const index = next.episodes.findIndex(e => e.episode_id === entry.episode_id);
  if (index >= 0) next.episodes[index] = entry; else next.episodes.push(entry);
  next.publications.push({ ...clone(pick(evidence, EVIDENCE_FIELDS)), date_sgt: context.date_sgt, episode_id: entry.episode_id, show: entry.show });
  next.updated_at = evidence.verified_at; assertLedger(next); return next;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const filename = process.argv[2] ?? new URL('./podcast-learning-ledger.json', import.meta.url);
    const ledger = JSON.parse(fs.readFileSync(filename, 'utf8'));
    const errors = validatePodcastLearningLedger(ledger);
    if (errors.length) { console.error(errors.join('\n')); process.exitCode = 1; }
    else console.log('Podcast learning ledger checks passed. Live-source and semantic editorial review remain required.');
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
