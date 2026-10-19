import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { validateExpertLearningLog } from './validate-expert-learning.mjs';

// Synthetic, immutable test data. These examples are not researched or delivered
// lessons. Mutation tests must never depend on the live ledger's count or order.
function syntheticEntry(concept_id, status = 'researched_candidate') {
  const channel = status === 'narrated' ? 'podcast' : 'report';
  const uses = status === 'researched_candidate' ? [] : [{
    date: '2026-10-19', channel,
    public_evidence_url: `https://example.org/synthetic/${concept_id}`,
    confirmation: 'Synthetic test confirmation; not edition evidence.'
  }];
  return {
    concept_id, aliases: [`Synthetic alias ${concept_id}`], experts: ['Andrej Karpathy'],
    theme: 'technical_coding', title: `Synthetic ${concept_id}`,
    sources: [{
      title: 'Synthetic source; not research evidence.', url: `https://example.org/source/${concept_id}`,
      authors: ['Andrej Karpathy'], original_date: '2019-04-25',
      original_date_basis: 'Synthetic test publication date.', checked_on: '2026-10-19',
      kind: 'first_party', verification: 'direct_primary', locator: 'Synthetic test section.'
    }],
    classification: 'evergreen', takeaway: 'Synthetic test takeaway.',
    editorial_application: 'Synthetic test application.', caveat: 'This entry is only test data.',
    status, dedup_review: uses.length ? 'covered' : 'pending_full_history',
    last_used: uses.length ? '2026-10-19' : null,
    last_narrated: status === 'narrated' ? '2026-10-19' : null, uses
  };
}
function deepFreeze(value) {
  for (const child of Object.values(value)) if (child && typeof child === 'object') deepFreeze(child);
  return Object.freeze(value);
}
const fixture = deepFreeze({
  version: 1, updated_on: '2026-10-19', timezone: 'Asia/Singapore',
  history: { complete: false, reviewed_reports: ['synthetic-report'], gaps: ['Synthetic incomplete-history gap.'] },
  entries: [
    syntheticEntry('candidate-one'), syntheticEntry('candidate-two'),
    syntheticEntry('narrated-one', 'narrated'), syntheticEntry('report-one', 'covered_in_report')
  ]
});
const entry = (log, id = 'candidate-one') => {
  const result = log.entries.find(item => item.concept_id === id);
  assert.ok(result, `Missing synthetic test entry ${id}`);
  return result;
};
const copy = () => structuredClone(fixture);
const errorsAfter = mutate => { const x = copy(); mutate(x); return validateExpertLearningLog(x); };

test('shipped growing log satisfies the contract without fixed counts or order', () => {
  const log = JSON.parse(fs.readFileSync(new URL('./expert-learning-log.json', import.meta.url), 'utf8'));
  assert.deepEqual(validateExpertLearningLog(log), []);
});
test('synthetic mutation fixture independently satisfies the contract', () => {
  assert.deepEqual(validateExpertLearningLog(fixture), []);
  assert.ok(Object.isFrozen(fixture.entries));
  assert.ok(Object.isFrozen(entry(fixture).sources[0]));
});
test('valid additions, reordering and recording a first use remain valid', () => {
  const log = copy();
  log.entries.push(syntheticEntry('new-candidate'));
  log.entries.reverse();
  assert.deepEqual(validateExpertLearningLog(log), []);
  const candidate = entry(log);
  candidate.status = 'narrated'; candidate.dedup_review = 'covered';
  candidate.last_used = '2026-10-19'; candidate.last_narrated = '2026-10-19';
  candidate.uses = [{ date: '2026-10-19', channel: 'podcast', public_evidence_url: 'https://example.org/synthetic/new-use', confirmation: 'Synthetic first-use confirmation.' }];
  assert.deepEqual(validateExpertLearningLog(log), []);
});
test('concept ID cannot be reset under another expert', () => {
  assert.ok(errorsAfter(x => { const e = structuredClone(entry(x)); e.experts = ['Andrew Ng']; e.aliases = ['different wording']; x.entries.push(e); }).some(e => e.includes('duplicate concept_id')));
});
test('same normalized alias is a duplicate despite punctuation and case', () => {
  assert.ok(errorsAfter(x => { entry(x, 'candidate-two').aliases.push(entry(x).aliases[0].toUpperCase() + '!'); }).some(e => e.includes('duplicate normalized alias')));
});
test('researched candidates cannot pretend to have been used', () => {
  assert.ok(errorsAfter(x => { entry(x).last_used = '2026-10-19'; }).some(e => e.includes('candidate cannot')));
});
test('report coverage is not proof of narration', () => {
  assert.ok(errorsAfter(x => { entry(x, 'report-one').status = 'narrated'; }).some(e => e.includes('exactly one confirmed podcast use')));
});
test('covered concept cannot return to candidate status', () => {
  assert.ok(errorsAfter(x => { entry(x, 'narrated-one').status = 'researched_candidate'; }).some(e => e.includes('candidate cannot')));
});
test('narration cannot be repeated on another date', () => {
  assert.ok(errorsAfter(x => { const e = entry(x, 'narrated-one'); e.uses.push({ ...e.uses[0], date: '2026-10-18' }); }).some(e => e.includes('no repeat concepts')));
});
test('source must retain original publication date and first-party provenance', () => {
  assert.ok(errorsAfter(x => { entry(x).sources[0].original_date = null; }).length > 0);
  assert.ok(errorsAfter(x => { entry(x).sources[0].kind = 'aggregator'; }).some(e => e.includes('first-party')));
});
test('archive-only evidence cannot seed an eligible research candidate', () => {
  assert.ok(errorsAfter(x => { entry(x).sources[0].verification = 'archived_primary_evidence'; }).some(e => e.includes('directly verified')));
});
test('source dates and public URLs are checked', () => {
  assert.ok(errorsAfter(x => { entry(x).sources[0].original_date = '2026-10-20'; }).some(e => e.includes('chronology')));
  assert.ok(errorsAfter(x => { entry(x).sources[0].url = 'https://example.com/?token=private'; }).some(e => e.includes('public HTTPS')));
});
test('history gaps prevent false full-history completeness claim', () => {
  assert.ok(errorsAfter(x => { x.history.complete = true; }).some(e => e.includes('known gaps')));
});
test('unrecognized fields and invalid dates fail cleanly', () => {
  assert.ok(errorsAfter(x => { entry(x).private_url = 'private'; }).some(e => e.includes('fields')));
  assert.ok(errorsAfter(x => { x.updated_on = '2026-02-30'; }).some(e => e.includes('updated_on')));
  assert.ok(validateExpertLearningLog(null).length > 0);
});
test('malformed nested records return errors rather than throw', () => {
  assert.ok(errorsAfter(x => { entry(x).uses = [null]; }).length > 0);
  assert.ok(errorsAfter(x => { entry(x).sources = [null]; }).length > 0);
});
