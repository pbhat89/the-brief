import test from 'node:test';import assert from 'node:assert/strict';
import {coverageFixture,makePartial} from './test-fixtures/source-coverage.fixture.mjs';
import {requireSourceCoverageForRelease} from './source-coverage-contract.mjs';
function fixture(){const c=makePartial(coverageFixture(),'x:fixture0');const s=c.sources.find(x=>x.source_id==='x:fixture0');Object.assign(s,{history_status:'unknown',prior_full_window_cursor:null,history_unknown_reason:'Prior runtime ledger not retained',history_recovery_plan:'Recover prior ledger from authorized archive; keep cursor unchanged'});return c;}
test('explicit unknown history permits partial only',()=>assert.equal(requireSourceCoverageForRelease(fixture()).status,'partial'));
for(const [name,change] of Object.entries({fabricated:s=>s.prior_full_window_cursor='2026-10-18T00:00:00Z',noReason:s=>s.history_unknown_reason='',noPlan:s=>s.history_recovery_plan='',noGap:s=>s.gaps=[],advance:s=>s.advance_full_window_cursor=true,full:s=>s.coverage_scope='full_window'}))test('reject unknown '+name,()=>{const c=fixture();change(c.sources.find(x=>x.source_id==='x:fixture0'));assert.throws(()=>requireSourceCoverageForRelease(c));});
test('unknown history cannot waive unattempted source',()=>{const c=fixture();makePartial(c,'weather',true);assert.throws(()=>requireSourceCoverageForRelease(c));});
