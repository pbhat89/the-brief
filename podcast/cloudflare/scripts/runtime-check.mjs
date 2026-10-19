// Local workerd/SQLite/KV smoke test. Synthetic values only; no remote resources.
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {mkdir} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {pinHash,digest} from '../src/security.js';
import {LogbookModel} from '../src/logbook-model.js';
import {verifyBrowserScript} from './browser-smoke.mjs';
const hash=await pinHash('123456789012','isolated-test');
const publisher='synthetic-test-token-'.repeat(3);
const publisherHash=await digest(publisher),persistence='.wrangler/runtime-'+crypto.randomUUID();
await mkdir(persistence+'/config',{recursive:true});
let child,logs='';
function launch(){
 child=spawn(process.execPath,['node_modules/wrangler/bin/wrangler.js','dev','--local','--port','9878','--ip','127.0.0.1','--persist-to',persistence,'--var','PIN_SALT:isolated-test','--var','PIN_HASH:'+hash,'--var','PUBLISHER_TOKEN_HASH:'+publisherHash,'--var','EXPIRY_APPROVED:true'],{env:{...process.env,XDG_CONFIG_HOME:persistence+'/config',WRANGLER_SEND_METRICS:'false',WRANGLER_LOG_PATH:'.wrangler/logs'},stdio:['ignore','pipe','pipe']});
 child.stdout.on('data',b=>logs+=b);child.stderr.on('data',b=>logs+=b);
}
async function stop(){if(!child||child.exitCode!==null)return;const exited=once(child,'exit');child.kill();await exited;}
const base='http://127.0.0.1:9878';
async function ready(){let available=false;for(let i=0;i<80;i++){try{const r=await fetch(base);if(r.ok){available=true;break}}catch{}await new Promise(r=>setTimeout(r,250));}assert.ok(available,logs);}
launch();
try{
 await ready();
 const browserScript=await fetch(base+'/app.js');assert.equal(browserScript.status,200);verifyBrowserScript(await browserScript.text());
 assert.equal((await fetch(base+'/api/episodes')).status,401);
 assert.equal((await fetch(base+'/api/logbook')).status,401);
 const login=await fetch(base+'/api/login',{method:'POST',headers:{Origin:base,'Content-Type':'application/json'},body:'{"pin":"123456789012"}'});
 assert.equal(login.status,200,await login.clone().text());const cookie=login.headers.get('set-cookie').split(';')[0];const {csrf}=await login.json();
 const session=await fetch(base+'/api/episodes',{headers:{Cookie:cookie}});assert.equal(session.status,200);assert.deepEqual(await session.json(),{episodes:[]});
 const logbookRead=()=>fetch(base+'/api/logbook',{headers:{Cookie:cookie}});
 const opened=await logbookRead();assert.equal(opened.status,200);const initial=await opened.json();
 assert.equal(initial.timeZone,'Asia/Singapore');assert.equal(initial.startDate,initial.today);assert.equal(initial.records.length,0);assert.ok(initial.pendingDates.length===1&&initial.pendingDates[0]===initial.today);
 // Synthetic all-false values test explicit finalization, not any person's habits.
 const logbookData={version:0,habits:Object.fromEntries(LogbookModel.habitsFor(initial.today).map(h=>[h.id,false])),fitnessActivities:[]};
 const saveDay=(data=logbookData,extra={})=>fetch(base+'/api/logbook/'+initial.today,{method:'PUT',headers:{Origin:base,Cookie:cookie,'X-CSRF-Token':csrf,'Content-Type':'application/json',...extra},body:JSON.stringify(data)});
 assert.equal((await saveDay(logbookData,{'X-CSRF-Token':'wrong'})).status,403);
 assert.equal((await saveDay(logbookData,{Origin:'https://other.example'})).status,403);
 const savedResponse=await saveDay();assert.equal(savedResponse.status,200);const saved=await savedResponse.json();
 assert.equal(saved.record.status,'completed');assert.equal(saved.record.version,1);assert.ok(Object.values(saved.record.habits).every(value=>value===false));
 const repeated=await Promise.all([saveDay(),saveDay()]);
 for(const response of repeated){assert.equal(response.status,200);assert.ok(JSON.stringify(await response.json())===JSON.stringify(saved),'An identical retry must preserve the original receipt');}
 const conflicting={...logbookData,habits:{...logbookData.habits,meditation:true}};
 const conflict=await saveDay(conflicting);assert.equal(conflict.status,409);assert.ok(JSON.stringify((await conflict.json()).currentRecord)===JSON.stringify(saved.record),'Conflicting save must return the current record');
 const readBack=await (await logbookRead()).json();assert.ok(readBack.records.length===1&&JSON.stringify(readBack.records[0])===JSON.stringify(saved.record),'Reload must show the saved synthetic day');assert.ok(!readBack.pendingDates.includes(initial.today));
 const bytes=new Uint8Array(7360000);bytes.set([255,251,144,0]);bytes.set([255,251,144,0],417);
 const upload=await fetch(base+'/api/upload',{method:'POST',headers:{Origin:base,Authorization:'Bearer '+publisher,'X-Brief-Publish':'1','Content-Type':'audio/mpeg','Content-Length':String(bytes.length)},body:bytes});assert.equal(upload.status,201,await upload.clone().text());const meta=await upload.json();
 const full=await fetch(base+'/api/media/'+meta.id,{headers:{Cookie:cookie}});assert.equal(full.status,200);assert.equal((await full.arrayBuffer()).byteLength,bytes.length);
 const partial=await fetch(base+'/api/media/'+meta.id,{headers:{Cookie:cookie,Range:'bytes=7359900-'}});assert.equal(partial.status,206);assert.equal((await partial.arrayBuffer()).byteLength,100);
 const head=await fetch(base+'/api/media/'+meta.id,{method:'HEAD',headers:{Cookie:cookie}});assert.equal(head.headers.get('Content-Length'),String(bytes.length));assert.equal(await head.text(),'');
 for(const Range of ['bytes=1-99','invalid','bytes=99999999-']){const h=await fetch(base+'/api/media/'+meta.id,{method:'HEAD',headers:{Cookie:cookie,Range}});assert.equal(h.status,200);assert.equal(h.headers.get('Content-Length'),String(bytes.length));assert.equal(h.headers.get('Content-Range'),null);assert.equal(await h.text(),'');}
 const topic=await fetch(base+'/api/upload',{method:'POST',headers:{Origin:base,Authorization:'Bearer '+publisher,'X-Brief-Publish':'1','Content-Type':'audio/mpeg','Content-Length':'834','X-Episode-Collection':'personal','X-Episode-Key':'synthetic-topic','X-Episode-Duration':'13'},body:bytes.slice(0,834)});assert.equal(topic.status,201,await topic.clone().text());const topicMeta=await topic.json();assert.equal(topicMeta.collection,'personal');assert.equal(topicMeta.episodeKey,'synthetic-topic');
 const dailyList=await (await fetch(base+'/api/episodes',{headers:{Cookie:cookie}})).json();assert.equal(dailyList.episodes.length,1);assert.equal(dailyList.episodes[0].id,meta.id);
 const topics=await (await fetch(base+'/api/episodes?collection=personal',{headers:{Cookie:cookie}})).json();assert.equal(topics.episodes.length,1);
 const storage=await (await fetch(base+'/api/storage',{headers:{Cookie:cookie}})).json();assert.equal(storage.activeAudioBytes,bytes.length+834);
 // KV permits only one write per key per second, including the initial metadata write.
 await new Promise(r=>setTimeout(r,1100));
 const remove=()=>fetch(base+'/api/episodes/'+topicMeta.id,{method:'DELETE',headers:{Origin:base,Cookie:cookie,'X-CSRF-Token':csrf,'X-Brief-Delete':topicMeta.id}});
 for(let i=0;i<2;i++){const deleted=await remove();assert.equal(deleted.status,200,await deleted.clone().text());}
 assert.equal((await fetch(base+'/api/media/'+topicMeta.id,{headers:{Cookie:cookie}})).status,404);
 assert.equal((await (await fetch(base+'/api/episodes?collection=personal',{headers:{Cookie:cookie}})).json()).episodes.length,0);
 const remaining=await (await fetch(base+'/api/storage',{headers:{Cookie:cookie}})).json();assert.equal(remaining.activeAudioBytes,bytes.length);
 // A new workerd process must load the same receipt from the isolated SQLite store.
 await stop();launch();await ready();
 const restarted=await logbookRead();assert.equal(restarted.status,200);const persisted=await restarted.json();
 assert.equal(persisted.startDate,initial.startDate);assert.ok(persisted.records.some(record=>JSON.stringify(record)===JSON.stringify(saved.record)),'Saved Log book data must survive a process restart');
 const postRestartRetry=await saveDay();assert.equal(postRestartRetry.status,200);assert.ok(JSON.stringify(await postRestartRetry.json())===JSON.stringify(saved),'Post-restart retry must preserve the original receipt');
 const attempts=await Promise.all(Array.from({length:11},()=>fetch(base+'/api/login',{method:'POST',headers:{Origin:base},body:'{"pin":"bad"}'})));
 assert.equal(attempts.filter(r=>r.status===401).length,9);assert.equal(attempts.filter(r=>r.status===429).length,2);
 const logout=await fetch(base+'/api/logout',{method:'POST',headers:{Origin:base,Cookie:cookie,'X-CSRF-Token':csrf}});assert.equal(logout.status,200);assert.equal((await logbookRead()).status,401);assert.equal((await saveDay()).status,401);
 console.log('PASS: served browser bundle initialization; workerd + SQLite DO PIN verification, session, private KV list, 7.36 MB upload/full/range/HEAD, personal collection/duration, authenticated deletion, storage estimate, concurrent global limiter; Log book private initialization, explicit false values, CSRF/origin rejection, identical retry, conflict, readback, persisted restart, logout protection');
}finally{await stop();}

