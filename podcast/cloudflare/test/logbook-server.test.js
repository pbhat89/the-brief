import {test} from 'node:test';
import assert from 'node:assert/strict';
import worker,{Auth} from '../src/worker.js';
import {digest} from '../src/security.js';
import {LogbookModel as model} from '../src/logbook-model.js';

// All dates, sessions and habit values in this file are synthetic test fixtures.
const origin='https://brief.example',token='synthetic-logbook-session',csrf='synthetic-logbook-csrf';
const configKey='logbook:v1:config',dayKey=date=>'logbook:v1:day:'+date;
class Storage {
 data=new Map();writes=[];queue=Promise.resolve();failDayWrite=false;
 async get(key){return structuredClone(this.data.get(key));}
 async put(key,value,...options){this.writes.push([key,structuredClone(value),...options]);this.data.set(key,structuredClone(value));}
 async delete(key){return this.data.delete(key);}
 async setAlarm(){}
 async list({prefix}={}){return new Map([...this.data].filter(([key])=>!prefix||key.startsWith(prefix)));}
 async transaction(fn){
  const result=this.queue.then(async()=>{
   const snapshot=structuredClone(this.data),writes=[];
   const t={get:async key=>structuredClone(snapshot.get(key)),put:async(key,value,...options)=>{
    if(this.failDayWrite&&key.startsWith('logbook:v1:day:'))throw Error('Synthetic interrupted save');
    snapshot.set(key,structuredClone(value));writes.push([key,structuredClone(value),...options]);
   }};
   const value=await fn(t);this.data=snapshot;this.writes.push(...writes);return value;
  });
  this.queue=result.catch(()=>{});return result;
 }
}
function body(date,overrides={}){
 return {version:0,habits:Object.fromEntries(model.habitsFor(date).map(h=>[h.id,false])),fitnessActivities:[],...overrides};
}
async function setup(t,instant='2030-01-07T04:00:00.000Z'){
 let timestamp=Date.parse(instant);t.mock.method(Date,'now',()=>timestamp);
 const storage=new Storage(),sessionKey='s:'+await digest(token);
 const env={PIN_HASH:'a'.repeat(64),EPISODES:{get(){throw Error('Log book must not use audio storage');},put(){throw Error('Log book must not use audio storage');}}};
 await storage.put(sessionKey,{csrf,exp:Date.parse('2031-01-01T00:00:00Z')/1000,version:env.PIN_HASH});storage.writes=[];
 const auth=new Auth({storage},env);env.AUTH={idFromName:()=>1,get:()=>auth};
 const request=(path,options={})=>worker.fetch(new Request(origin+path,{...options,headers:{Cookie:'__Host-brief='+token,...options.headers}}),env);
 const get=(week,options)=>request('/api/logbook'+(week===undefined?'':'?week='+week),options);
 const put=(date,data=body(date),headers={})=>request('/api/logbook/'+date,{method:'PUT',headers:{Origin:origin,'X-CSRF-Token':csrf,'Content-Type':'application/json',...headers},body:JSON.stringify(data)});
 const direct=data=>auth.fetch(new Request('https://internal/',{method:'POST',body:JSON.stringify({token,...data})}));
 return {storage,sessionKey,env,auth,request,get,put,direct,setTime:iso=>{timestamp=Date.parse(iso);}};
}

test('first authenticated read starts tracking today, without invented history or habit records',async t=>{
 const h=await setup(t),r=await h.get();assert.equal(r.status,200);
 assert.deepEqual(await r.json(),{schemaVersion:1,timeZone:'Asia/Singapore',today:'2030-01-07',startDate:'2030-01-07',weekStart:'2030-01-07',records:[],pendingDates:['2030-01-07']});
 assert.deepEqual(h.storage.writes,[[configKey,{schemaVersion:1,timeZone:'Asia/Singapore',startDate:'2030-01-07'}]]);
 await h.get();assert.equal(h.storage.writes.length,1,'later reads do not write');
 assert.match(r.headers.get('cache-control'),/private, no-store/);assert.equal(r.headers.get('access-control-allow-origin'),null);
});

test('anonymous, forged, expired and rotated sessions cannot read or save Log book',async t=>{
 const h=await setup(t);
 for(const Cookie of ['', '__Host-brief=forged']){
  assert.equal((await h.get(undefined,{headers:{Cookie}})).status,401);
  assert.equal((await h.put('2030-01-07',body('2030-01-07'),{Cookie})).status,401);
 }
 const original=await h.storage.get(h.sessionKey);
 for(const session of [{...original,exp:Date.now()/1000},{...original,version:'b'.repeat(64)}]){
  h.storage.data.set(h.sessionKey,session);
  assert.equal((await h.get()).status,401);assert.equal((await h.put('2030-01-07')).status,401);
 }
 assert.equal(h.storage.writes.length,0);
});

test('write requires exact Origin and CSRF, while reads reject explicit cross-site requests',async t=>{
 const h=await setup(t);await h.get();
 for(const headers of [{Origin:''},{Origin:'https://other.example'},{Origin:origin+'/'},{'Sec-Fetch-Site':'cross-site'},{'X-CSRF-Token':''},{'X-CSRF-Token':'wrong'}])assert.equal((await h.put('2030-01-07',body('2030-01-07'),headers)).status,403);
 for(const headers of [{Origin:'https://other.example'},{'Sec-Fetch-Site':'cross-site'}])assert.equal((await h.get(undefined,{headers})).status,403);
 assert.equal(h.storage.writes.length,1);
});

test('Durable Object rechecks session and CSRF, even after a successful outer check',async t=>{
 const h=await setup(t);await h.get();
 assert.equal((await h.direct({op:'logbook:put',csrf:'wrong',date:'2030-01-07',data:body('2030-01-07')})).status,403);
 const fetch=h.auth.fetch.bind(h.auth);
 h.env.AUTH.get=()=>({fetch:async request=>{
  const data=await request.clone().json(),response=await fetch(request);
  if(data.op==='check')await h.storage.delete(h.sessionKey);
  return response;
 }});
 assert.equal((await h.put('2030-01-07')).status,401);
 assert.ok(!h.storage.data.has(dayKey('2030-01-07')));
 assert.equal((await h.direct({op:'logbook:get'})).status,401);
});

test('invalid week/date, malformed JSON and oversized payloads fail without record writes',async t=>{
 const h=await setup(t);
 for(const week of ['','2030-01-08','2030-02-30','2030-1-7','not-a-date','2030-01-07&week=2030-01-14'])assert.equal((await h.get(week)).status,400);
 assert.equal(h.storage.writes.length,0,'invalid initial reads must not create config');
 await h.get();
 for(const date of ['2030-02-30','2030-1-7','not-a-date'])assert.equal((await h.put(date,body('2030-01-07'))).status,400);
 assert.equal((await h.request('/api/logbook/2030-01-07',{method:'PUT',headers:{Origin:origin,'X-CSRF-Token':csrf,'Content-Type':'application/json'},body:'{'})).status,400);
 assert.equal((await h.put('2030-01-07',body('2030-01-07'),{'Content-Type':'text/plain'})).status,415);
 assert.equal((await h.put('2030-01-07',{...body('2030-01-07'),padding:'x'.repeat(3000)})).status,413);
 assert.equal((await h.put('2030-01-07',body('2030-01-07'),{'Content-Length':'2049'})).status,413);
 assert.equal(h.storage.writes.length,1);
});

test('every applicable boolean is mandatory and unknown or mistyped input is rejected',async t=>{
 const h=await setup(t);await h.get();const good=body('2030-01-07');
 const invalid=[null,[],{}, {...good,version:-1},{...good,version:1.5},{...good,version:'0'},{...good,version:Number.MAX_SAFE_INTEGER+1},{...good,extra:true},{...good,habits:[]},{...good,fitnessActivities:null}];
 for(const key of Object.keys(good.habits)){
  const missing=structuredClone(good);delete missing.habits[key];invalid.push(missing);
  invalid.push({...good,habits:{...good.habits,[key]:0}});
 }
 invalid.push({...good,habits:{...good.habits,unknown:false}});
 for(const value of invalid)assert.equal((await h.put('2030-01-07',value)).status,400);
 assert.equal(h.storage.writes.length,1);
});

test('Done saves every explicit false value, retains records with no expiry and reloads across sessions',async t=>{
 const h=await setup(t);await h.get();const r=await h.put('2030-01-07');assert.equal(r.status,200);const {record}=await r.json();
 assert.deepEqual(record,{date:'2030-01-07',version:1,status:'completed',habits:{noSmoke:false,noSugar:false,publicTransport:false,fitness:false,meditation:false},fitnessActivities:[],savedAt:'2030-01-07T04:00:00.000Z'});
 assert.deepEqual(h.storage.writes.at(-1),[dayKey('2030-01-07'),record]);
 const state=await (await h.get()).json();assert.deepEqual(state.records,[record]);assert.deepEqual(state.pendingDates,[]);
 const newToken='synthetic-second-device';h.storage.data.set('s:'+await digest(newToken),{csrf:'second',exp:Date.now()/1000+3600,version:h.env.PIN_HASH});
 const other=await (await h.get(undefined,{headers:{Cookie:'__Host-brief='+newToken}})).json();assert.deepEqual(other.records,[record]);
 h.setTime('2030-01-14T04:00:00Z');await h.auth.alarm();assert.ok(h.storage.data.has(dayKey('2030-01-07')),'session cleanup must not expire habit history');
});

test('weekends omit public transport and do not accept an extra non-applicable boolean',async t=>{
 const h=await setup(t,'2030-01-05T04:00:00Z');await h.get();assert.equal(model.weekday('2030-01-05'),6);
 const wrong=body('2030-01-05');wrong.habits.publicTransport=false;assert.equal((await h.put('2030-01-05',wrong)).status,400);
 const {record}=await (await h.put('2030-01-05')).json();assert.equal(Object.keys(record.habits).length,4);assert.ok(!Object.hasOwn(record.habits,'publicTransport'));
 h.setTime('2030-01-06T04:00:00Z');assert.equal((await h.put('2030-01-06')).status,200);
 h.setTime('2030-01-07T04:00:00Z');const missing=body('2030-01-07');delete missing.habits.publicTransport;assert.equal((await h.put('2030-01-07',missing)).status,400);
});

test('fitness allows an aggregate true with no activity or up to four unique known activities',async t=>{
 const h=await setup(t);await h.get();const good=body('2030-01-07');good.habits.fitness=true;
 for(const fitnessActivities of [['run'],['walk','walk'],['walk',null],['walk','tennis','cycle','yoga','walk'],'walk'])assert.equal((await h.put('2030-01-07',{...good,fitnessActivities})).status,400);
 assert.equal((await h.put('2030-01-07',{...body('2030-01-07'),fitnessActivities:['walk']})).status,400);
 const {record}=await (await h.put('2030-01-07',{...good,fitnessActivities:['yoga','walk','cycle','tennis']})).json();assert.deepEqual(record.fitnessActivities,['walk','tennis','cycle','yoga']);
 h.setTime('2030-01-08T04:00:00Z');const aggregate=body('2030-01-08');aggregate.habits.fitness=true;assert.equal((await h.put('2030-01-08',aggregate)).status,200);
});

test('previous five calendar days are eligible, bounded by feature start; no future or fabricated history',async t=>{
 const h=await setup(t,'2030-01-01T04:00:00Z');
 assert.equal((await h.put('2030-01-01')).status,409,'GET must initialize tracking first');await h.get();
 assert.equal((await h.put('2029-12-31')).status,400,'before feature start');
 h.setTime('2030-01-08T04:00:00Z');
 const state=await (await h.get()).json();assert.deepEqual(state.pendingDates,['2030-01-08','2030-01-07','2030-01-06','2030-01-05','2030-01-04','2030-01-03']);
 assert.equal((await h.put('2030-01-03')).status,200,'fifth preceding calendar day is allowed');
 for(const date of ['2030-01-02','2030-01-09','2029-12-31'])assert.equal((await h.put(date)).status,400);
 const next=await (await h.get()).json();assert.ok(!next.pendingDates.includes('2030-01-03'));assert.ok(!next.pendingDates.includes('2030-01-02'),'do not fill gaps with older unfinished days');
});

test('server owns the Singapore calendar day across UTC midnight and Monday rollover',async t=>{
 const h=await setup(t,'2030-01-06T15:59:59Z');let state=await (await h.get()).json();assert.equal(state.today,'2030-01-06');assert.equal(state.weekStart,'2029-12-31');
 h.setTime('2030-01-06T16:00:00Z');state=await (await h.get()).json();assert.equal(state.today,'2030-01-07');assert.equal(state.weekStart,'2030-01-07');assert.equal(state.startDate,'2030-01-06');assert.deepEqual(state.pendingDates,['2030-01-07','2030-01-06']);
 assert.equal((await h.put('2030-01-08')).status,400);
});

test('requested history includes its week plus today and recent saved dates without duplicates',async t=>{
 const h=await setup(t,'2029-12-31T04:00:00Z');await h.get();await h.put('2029-12-31');
 h.setTime('2030-01-07T04:00:00Z');await h.put('2030-01-07');
 h.setTime('2030-01-14T04:00:00Z');await h.put('2030-01-10');await h.put('2030-01-14');
 const history=await (await h.get('2029-12-31')).json();assert.equal(history.weekStart,'2029-12-31');assert.deepEqual(history.records.map(r=>r.date),['2029-12-31','2030-01-10','2030-01-14']);
 const current=await (await h.get()).json();assert.deepEqual(current.records.map(r=>r.date),['2030-01-10','2030-01-14']);assert.equal(new Set(current.records.map(r=>r.date)).size,current.records.length);
 assert.deepEqual(current.pendingDates,['2030-01-13','2030-01-12','2030-01-11','2030-01-09']);
});

test('identical retries reuse a durable receipt, including after the entry window closes',async t=>{
 const h=await setup(t);await h.get();const payload=body('2030-01-07');payload.habits.fitness=true;payload.fitnessActivities=['yoga','walk'];
 const first=await (await h.put('2030-01-07',payload)).json();const writes=h.storage.writes.length;
 for(const version of [0,1]){
  const response=await h.put('2030-01-07',{...payload,version,fitnessActivities:['walk','yoga']});assert.equal(response.status,200);assert.deepEqual(await response.json(),first);
 }
 h.setTime('2030-02-01T04:00:00Z');const retry=await h.put('2030-01-07',payload);assert.equal(retry.status,200);assert.deepEqual(await retry.json(),first);assert.equal(h.storage.writes.length,writes);
});

test('stale or conflicting finalization returns the current record and never overwrites it',async t=>{
 const h=await setup(t);await h.get();const current=await (await h.put('2030-01-07')).json();const writes=h.storage.writes.length;
 for(const version of [0,1,2]){
  const changed=body('2030-01-07',{version});changed.habits.meditation=true;const response=await h.put('2030-01-07',changed);assert.equal(response.status,409);assert.deepEqual((await response.json()).currentRecord,current.record);
 }
 assert.equal(h.storage.writes.length,writes);assert.deepEqual(await h.storage.get(dayKey('2030-01-07')),current.record);
 h.setTime('2030-01-08T04:00:00Z');const missing=await h.put('2030-01-08',body('2030-01-08',{version:1}));assert.equal(missing.status,409);assert.equal((await missing.json()).currentRecord,null);
});

test('concurrent conflicting Done requests serialize to one record and one conflict',async t=>{
 const h=await setup(t);await h.get();const alternate=body('2030-01-07');alternate.habits.noSugar=true;
 const results=await Promise.all([h.put('2030-01-07'),h.put('2030-01-07',alternate)]);assert.deepEqual(results.map(r=>r.status).sort(),[200,409]);
 assert.equal(h.storage.writes.filter(([key])=>key===dayKey('2030-01-07')).length,1);
 const saved=await h.storage.get(dayKey('2030-01-07'));assert.deepEqual((await results.find(r=>r.status===409).json()).currentRecord,saved);
});

test('failed persistence returns unavailable without a false receipt and can be retried',async t=>{
 const h=await setup(t);await h.get();h.storage.failDayWrite=true;
 assert.equal((await h.put('2030-01-07')).status,503);assert.ok(!h.storage.data.has(dayKey('2030-01-07')));
 assert.deepEqual((await (await h.get()).json()).pendingDates,['2030-01-07']);
 h.storage.failDayWrite=false;assert.equal((await h.put('2030-01-07')).status,200);
});

test('malformed private state fails closed instead of serving or overwriting it',async t=>{
 const h=await setup(t);await h.get();h.storage.data.set(dayKey('2030-01-07'),{date:'2030-01-07',habits:{}});
 assert.equal((await h.get()).status,503);assert.equal((await h.put('2030-01-07')).status,503);
 h.storage.data.delete(dayKey('2030-01-07'));h.storage.data.set(configKey,{schemaVersion:1,timeZone:'Asia/Singapore',startDate:'invalid'});assert.equal((await h.get()).status,503);
});
