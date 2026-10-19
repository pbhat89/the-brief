import {readFileSync, mkdtempSync, writeFileSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import test from 'node:test';
import assert from 'node:assert/strict';
import {validateEditorialPolicy, validateEditorialAudit, validateExpertSelection} from './editorial-contract.mjs';
const policy = JSON.parse(readFileSync(new URL('./editorial-policy.json', import.meta.url), 'utf8'));
const audit = () => ({edition_date:'2026-10-20', source_revision:'fixture-revision', conditions_seconds:25, expert_seconds:60, ending_seconds:17, routine_safety_announcement:false, regional_psi_recital:false, spoken_source_diagnostics:false, repeated_closing_summary:false, improvement_sentences:0, singapore_stories:[{event_id:'sg-policy-1',weather:false,fresh_verified:true,source_url:'https://example.org/policy'},{event_id:'sg-transport-2',weather:false,fresh_verified:true,source_url:'https://example.org/transport'}], expert_concept_ids:['fixture-concept'],expert_semantic_history_reviewed:true,expert_source_url:'https://example.org/original',podcast_recaps:[]});
test('shipped policy preserves requested budgets and source rules', () => assert.equal(validateEditorialPolicy(policy), true));
test('representative private audit passes', () => assert.equal(validateEditorialAudit(policy, audit()), true));
test('long weather fails unless an actionable sourced exception is recorded', () => {
 const a=audit();a.conditions_seconds=48;assert.throws(()=>validateEditorialAudit(policy,a));
 a.conditions_exception={kind:'verified-actionable-alert',reason:'A verified disruption changes morning travel.',source_url:'https://example.org/official-alert'};assert.equal(validateEditorialAudit(policy,a),true);
 a.conditions_exception.source_url='javascript:alert(1)';assert.throws(()=>validateEditorialAudit(policy,a));
});
test('reject routine safety, regional recitals, diagnostics and rambling ending', () => {
 for(const field of ['routine_safety_announcement','regional_psi_recital','spoken_source_diagnostics','repeated_closing_summary']){const a=audit();a[field]=true;assert.throws(()=>validateEditorialAudit(policy,a));}
 for(const [field,value] of [['ending_seconds',21],['ending_seconds',-1],['improvement_sentences',2]]){const a=audit();a[field]=value;assert.throws(()=>validateEditorialAudit(policy,a));}
});
test('Singapore news cannot be weather, stale, duplicate or padded', () => {
 for(const mutation of [a=>a.singapore_stories[0].weather=true,a=>a.singapore_stories[0].fresh_verified=false,a=>a.singapore_stories[1].event_id=a.singapore_stories[0].event_id,a=>a.singapore_stories=[]]){const a=audit();mutation(a);assert.throws(()=>validateEditorialAudit(policy,a));}
 const a=audit();a.singapore_stories=[];a.singapore_shortfall_reason='No fresh events verified within the intake window.';assert.equal(validateEditorialAudit(policy,a),true);
});
test('expert insight needs bounded duration, source and semantic review', () => {
 for(const mutation of [a=>a.expert_seconds=80,a=>a.expert_semantic_history_reviewed=false,a=>a.expert_source_url='',a=>a.expert_concept_ids.push('another-concept')]){const a=audit();mutation(a);assert.throws(()=>validateEditorialAudit(policy,a));}
 const a=audit();a.expert_concept_ids=[];a.expert_seconds=0;a.expert_omission_reason='No source-backed unused concept verified.';assert.equal(validateEditorialAudit(policy,a),true);
});
test('fallback requires primary-show gap, original identity and transcript references', () => {
 const a=audit();a.podcast_recaps=[{show:'Big Technology Podcast',episode_key:'fixture-episode',original_verified:true,transcript_accessible:true,previously_covered:false,segment_references:['00:40–03:12']}];
 assert.throws(()=>validateEditorialAudit(policy,a));a.everyday_ai_ineligible_reason='No unseen original with accessible transcript.';assert.equal(validateEditorialAudit(policy,a),true);
 for(const field of ['original_verified','transcript_accessible']){const b=structuredClone(a);b.podcast_recaps[0][field]=false;assert.throws(()=>validateEditorialAudit(policy,b));}
 a.podcast_recaps[0].previously_covered=true;assert.throws(()=>validateEditorialAudit(policy,a));
});

test('synthetic audit format stays usable, without claiming edition evidence', () => {const fixture=JSON.parse(readFileSync(new URL('./editorial-audit.example.json', import.meta.url), 'utf8'));assert.equal(validateEditorialAudit(policy,fixture),true);assert.match(fixture.source_revision,/REPLACE/);});
test('selection references a reviewed unused concept and its checked primary source', () => {
 const a=audit();const log={entries:[{concept_id:'fixture-concept',status:'researched_candidate',dedup_review:'reviewed_no_match',uses:[],sources:[{url:a.expert_source_url,kind:'first_party',verification:'direct_primary'}]}]};
 assert.equal(validateExpertSelection(a,log),true);
 for(const mutation of [l=>l.entries[0].dedup_review='pending_full_history',l=>l.entries[0].status='narrated',l=>l.entries[0].uses.push({date:'2026-10-19'}),l=>l.entries[0].sources[0].url='https://example.org/unrelated',l=>l.entries=[]]){const l=structuredClone(log);mutation(l);assert.throws(()=>validateExpertSelection(a,l));}
});

test('impossible calendar dates and credential-bearing source links are rejected', () => {const a=audit();a.edition_date='2026-02-30';assert.throws(()=>validateEditorialAudit(policy,a));const b=audit();b.singapore_stories[0].source_url='https://user:password@example.org/source';assert.throws(()=>validateEditorialAudit(policy,b));const p=structuredClone(policy);p.effective_from='2026-02-30';assert.throws(()=>validateEditorialPolicy(p));});
test('prepublication CLI rejects example placeholders and unknown concepts', () => {
 const cli=fileURLToPath(new URL('./validate-editorial.mjs',import.meta.url));
 const example=fileURLToPath(new URL('./editorial-audit.example.json',import.meta.url));
 assert.notEqual(spawnSync(process.execPath,[cli,'--audit',example]).status,0);
 const dir=mkdtempSync(join(tmpdir(),'brief-audit-test-'));
 try {
  const path=join(dir,'audit.json');const a=audit();a.source_revision='a'.repeat(40);
  writeFileSync(path,JSON.stringify(a));assert.notEqual(spawnSync(process.execPath,[cli,'--audit',path]).status,0);
  a.expert_concept_ids=[];a.expert_seconds=0;a.expert_omission_reason='No verified unused concept available.';
  writeFileSync(path,JSON.stringify(a));const result=spawnSync(process.execPath,[cli,'--audit',path]);assert.equal(result.status,0,result.stderr.toString());
  a.podcast_recaps=[{show:'Big Technology Podcast',episode_key:'invented-episode',original_verified:true,transcript_accessible:true,previously_covered:false,segment_references:['00:40–03:12']}];a.everyday_ai_ineligible_reason='No eligible original.';
  writeFileSync(path,JSON.stringify(a));const fabricated=spawnSync(process.execPath,[cli,'--audit',path]);assert.notEqual(fabricated.status,0);assert.match(fabricated.stderr.toString(),/selection context/);
 } finally {rmSync(dir,{recursive:true,force:true});}
});
