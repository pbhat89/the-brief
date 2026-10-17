import test from 'node:test';import assert from 'node:assert/strict';import {validateReports,validateStatus,duplicateEvent} from './validate.mjs';
test('empty manifest is truthful',()=>assert.equal(validateReports({latest_id:null,reports:[]}),true));
test('latest cannot point to missing report',()=>assert.throws(()=>validateReports({latest_id:'missing',reports:[]})));
test('reject script URLs and private fields',()=>{for(const extra of [{report_url:'javascript:alert(1)'},{audio_url:'https://example.com/private.mp3'}])assert.throws(()=>validateReports({latest_id:'r',reports:[{id:'r',title:'News',published_at:'2026-10-18T07:00:00+08:00',report_url:'report.html',...extra}]}))});
test('unknown state is rejected',()=>assert.throws(()=>validateStatus({run_id:'r',updated_at:'2026-10-18T00:00:00Z',steps:[{id:'a',label:'A',detail:'D',updated_at:'2026-10-18T00:00:00Z',state:'almost'}]})));
test('same event across channels remains duplicate',()=>assert.equal(duplicateEvent({event_id:'launch'},[{event_id:'launch',channels:['report']}]),true));
test('material update must have a new fact',()=>{assert.equal(duplicateEvent({event_id:'launch',material_update_of:'launch',material_new_fact:'Now generally available'},[{event_id:'launch'}]),false);assert.equal(duplicateEvent({event_id:'launch',material_update_of:'launch',material_new_fact:' '},[{event_id:'launch'}]),true)});
