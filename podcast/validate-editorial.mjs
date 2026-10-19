import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import {validateEditorialPolicy, validateEditorialAudit, validateExpertSelection, validatePodcastSelection} from './editorial-contract.mjs';
import {validateExpertLearningLog} from './validate-expert-learning.mjs';
const policy = JSON.parse(readFileSync(new URL('./editorial-policy.json', import.meta.url), 'utf8'));
validateEditorialPolicy(policy);
if (process.argv[2]) {
  if (process.argv[2] !== '--audit' || !process.argv[3] || process.argv.length !== 4) throw Error('Usage: node podcast/validate-editorial.mjs [--audit /private/audit.json]');
  const audit = JSON.parse(readFileSync(process.argv[3], 'utf8'));
  const expertLog = JSON.parse(readFileSync(new URL('./expert-learning-log.json', import.meta.url), 'utf8'));
  assert.deepEqual(validateExpertLearningLog(expertLog), []);
  assert.match(audit.source_revision, /^[a-f0-9]{40}$/, 'Use the actual repository commit, never the synthetic example');
  assert.ok(audit.edition_date >= policy.effective_from, 'Policy applies to new editions only');
  validateEditorialAudit(policy, audit);
  validateExpertSelection(audit, expertLog);
  const podcastLedger = JSON.parse(readFileSync(new URL('./podcast-learning-ledger.json', import.meta.url), 'utf8'));
  validatePodcastSelection(audit, podcastLedger);
}
console.log('Editorial policy and any supplied audit passed; source truth, semantic novelty and listening quality still require review.');
