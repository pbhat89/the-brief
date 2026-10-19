import fs from 'node:fs';
import { pathToFileURL } from 'node:url';

const EXPERTS = new Set(['Andrej Karpathy', 'Andrew Ng', 'Yann LeCun', 'Naval Ravikant']);
const THEMES = new Set(['technical_coding', 'ai_transition', 'management']);
const STATES = new Set(['researched_candidate', 'covered_in_report', 'narrated']);
const REVIEWS = new Set(['pending_full_history', 'reviewed_no_match', 'covered']);
const text = v => typeof v === 'string' && v.trim().length > 0;
const date = v => typeof v === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(v) && Number.isFinite(Date.parse(v)) && new Date(v).toISOString().slice(0, 10) === v;
const normalized = v => String(v).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
const publicUrl = v => {
  try {
    const u = new URL(v);
    return u.protocol === 'https:' && !u.username && !u.password && !/^(localhost|127\.|0\.|\[::1\])/.test(u.hostname)
      && ![...u.searchParams.keys()].some(k => /token|secret|signature|password|credential|api.?key/i.test(k));
  } catch { return false; }
};
const ENTRY_KEYS = ['concept_id', 'aliases', 'experts', 'theme', 'title', 'sources', 'classification', 'takeaway', 'editorial_application', 'caveat', 'status', 'dedup_review', 'last_used', 'last_narrated', 'uses'];
const SOURCE_KEYS = ['title', 'url', 'authors', 'original_date', 'original_date_basis', 'checked_on', 'kind', 'verification', 'locator'];
const USE_KEYS = ['date', 'channel', 'public_evidence_url', 'confirmation'];

/** Dependency-free contract checks, not a generic JSON Schema engine or semantic verifier. */
export function validateExpertLearningLog(log) {
  const errors = [];
  const check = (ok, message) => { if (!ok) errors.push(message); };
  const shape = (v, keys, where) => {
    if (!v || typeof v !== 'object' || Array.isArray(v)) { errors.push(`${where}: expected object`); return false; }
    check(keys.every(k => Object.hasOwn(v, k)) && Object.keys(v).every(k => keys.includes(k)), `${where}: unexpected or missing fields`);
    return true;
  };
  if (!shape(log, ['version', 'updated_on', 'timezone', 'history', 'entries'], 'log')) return errors;
  check(log.version === 1, 'log: version must be 1');
  check(date(log.updated_on), 'log: valid updated_on required');
  check(log.timezone === 'Asia/Singapore', 'log: dates use Asia/Singapore');
  if (shape(log.history, ['complete', 'reviewed_reports', 'gaps'], 'history')) {
    check(typeof log.history.complete === 'boolean', 'history: complete must be boolean');
    for (const key of ['reviewed_reports', 'gaps']) check(Array.isArray(log.history[key]) && log.history[key].every(text), `history: ${key} must contain strings`);
    check(!log.history.complete || log.history.gaps?.length === 0, 'history: complete cannot coexist with known gaps');
    check(log.history.complete || (Array.isArray(log.history.gaps) && log.history.gaps.length > 0), 'history: incomplete coverage needs a gap');
  }
  if (!Array.isArray(log.entries)) return [...errors, 'log: entries must be an array'];
  const ids = new Set();
  const aliases = new Map();
  for (const [i, entry] of log.entries.entries()) {
    const at = `entry ${i}`;
    if (!shape(entry, ENTRY_KEYS, at)) continue;
    check(typeof entry.concept_id === 'string' && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(entry.concept_id), `${at}: valid concept_id required`);
    check(!ids.has(entry.concept_id), `${at}: duplicate concept_id (dedup crosses experts)`);
    ids.add(entry.concept_id);
    for (const key of ['title', 'takeaway', 'editorial_application', 'caveat']) check(text(entry[key]), `${at}: ${key} required`);
    check(Array.isArray(entry.aliases) && entry.aliases.length > 0 && entry.aliases.every(text), `${at}: aliases required`);
    for (const alias of Array.isArray(entry.aliases) ? entry.aliases : []) {
      const key = normalized(alias);
      check(!aliases.has(key), `${at}: duplicate normalized alias ${key}`);
      aliases.set(key, entry.concept_id);
    }
    check(Array.isArray(entry.experts) && entry.experts.length > 0 && entry.experts.every(e => EXPERTS.has(e)) && new Set(entry.experts).size === entry.experts.length, `${at}: recognized, unique experts required`);
    check(THEMES.has(entry.theme), `${at}: invalid theme`);
    check(STATES.has(entry.status), `${at}: invalid status`);
    check(REVIEWS.has(entry.dedup_review), `${at}: invalid dedup_review`);
    check(['evergreen', 'recent_context'].includes(entry.classification), `${at}: classify source age separately from use status`);
    check(Array.isArray(entry.sources) && entry.sources.length > 0, `${at}: primary source required`);
    for (const [j, source] of (Array.isArray(entry.sources) ? entry.sources : []).entries()) {
      const where = `${at} source ${j}`;
      if (!shape(source, SOURCE_KEYS, where)) continue;
      for (const key of ['title', 'original_date_basis', 'locator']) check(text(source[key]), `${where}: ${key} required`);
      check(source.kind === 'first_party', `${where}: first-party evidence required`);
      check(publicUrl(source.url), `${where}: public HTTPS source URL required`);
      check(Array.isArray(source.authors) && source.authors.length > 0 && source.authors.every(text), `${where}: authors required`);
      check(date(source.original_date) && date(source.checked_on), `${where}: valid original and checked dates required`);
      check(source.original_date <= source.checked_on && source.checked_on <= log.updated_on, `${where}: inconsistent source chronology`);
      check(['direct_primary', 'archived_primary_evidence'].includes(source.verification), `${where}: explicit verification method required`);
      if (entry.status === 'researched_candidate') check(source.verification === 'direct_primary', `${where}: candidate requires directly verified primary evidence`);
    }
    check(Array.isArray(entry.uses), `${at}: uses must be an array`);
    const uses = Array.isArray(entry.uses) ? entry.uses : [];
    const useKeys = new Set();
    for (const [j, use] of uses.entries()) {
      const where = `${at} use ${j}`;
      if (!shape(use, USE_KEYS, where)) continue;
      check(date(use.date) && use.date <= log.updated_on, `${where}: valid past use date required`);
      check(['report', 'podcast'].includes(use.channel), `${where}: invalid channel`);
      check(publicUrl(use.public_evidence_url) && text(use.confirmation), `${where}: public evidence and confirmation required`);
      const key = `${use.date}:${use.channel}`;
      check(!useKeys.has(key), `${where}: duplicate use`); useKeys.add(key);
    }
    const podcasts = uses.filter(u => u?.channel === 'podcast');
    const latest = list => list.map(u => u?.date).filter(date).sort().at(-1) ?? null;
    check(entry.last_used === latest(uses), `${at}: last_used must match recorded uses`);
    check(entry.last_narrated === latest(podcasts), `${at}: last_narrated must match confirmed podcast uses`);
    check(entry.last_used === null || date(entry.last_used), `${at}: invalid last_used`);
    check(entry.last_narrated === null || date(entry.last_narrated), `${at}: invalid last_narrated`);
    if (entry.status === 'researched_candidate') {
      check(uses.length === 0 && entry.last_used === null && entry.last_narrated === null, `${at}: candidate cannot have prior uses`);
      check(entry.dedup_review !== 'covered', `${at}: covered concept cannot be a candidate`);
    } else {
      check(uses.length > 0 && entry.dedup_review === 'covered', `${at}: covered status needs usage evidence and covered review`);
    }
    if (entry.status === 'narrated') check(podcasts.length === 1, `${at}: narrated requires exactly one confirmed podcast use (no repeat concepts)`);
    if (entry.status === 'covered_in_report') check(podcasts.length === 0 && uses.some(u => u?.channel === 'report'), `${at}: report-only status cannot assert podcast narration`);
  }
  return errors;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const path = process.argv[2] ?? new URL('./expert-learning-log.json', import.meta.url);
  const errors = validateExpertLearningLog(JSON.parse(fs.readFileSync(path, 'utf8')));
  if (errors.length) { console.error(errors.join('\n')); process.exitCode = 1; }
  else console.log('Expert learning log checks passed. Semantic history review is still required.');
}
