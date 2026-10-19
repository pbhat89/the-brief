import {test} from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {parse} from 'parse5';
import {JS} from '../src/app.js';
import {HTML,CSS} from '../src/ui.js';
import {LogbookModel as model} from '../src/logbook-model.js';
const TODAY='2026-10-19';
const record=(date,habits={})=>({date,version:1,status:'completed',habits:{...model.savePayload(date).habits,...habits},fitnessActivities:[],savedAt:'2026-10-19T10:00:00.000Z'});
const state=(extra={})=>({schemaVersion:1,timeZone:'Asia/Singapore',today:TODAY,startDate:TODAY,weekStart:model.monday(TODAY),records:[],pendingDates:[TODAY],...extra});
const settle=()=>new Promise(r=>setImmediate(r));
function harness({payload=state(),reduced=true}={}){
 const timers=[],requests=[];let currentTime=Date.parse(TODAY+'T10:00:00Z'),handler;
 class Element{
  constructor(tag){this.tagName=tag;this.children=[];this.attributes={};this.hidden=false;this.style={setProperty(){}};this.classList={add(){},remove(){}};this._text='';this.value='';}
  get textContent(){return this._text+this.children.map(n=>n.textContent).join('');}
  set textContent(text){this._text=String(text);this.children=[];}
  append(...nodes){this.children.push(...nodes);}
  replaceChildren(...nodes){this._text='';this.children=[...nodes];}
  setAttribute(k,v){this.attributes[k]=String(v);if(k==='id')this.id=v;}
  getAttribute(k){return k==='src'?this.src||this.attributes.src||null:this.attributes[k]??null;}
  removeAttribute(k){delete this.attributes[k];if(k==='src')this.src='';}
  focus(){document.activeElement=this;}
 }
 const convert=n=>{const node=new Element(n.tagName||'root');for(const a of n.attrs||[]){node.setAttribute(a.name,a.value);if(a.name==='hidden')node.hidden=true;}for(const c of n.childNodes||[]){if(c.nodeName==='#text')node._text+=c.value;else node.append(convert(c));}return node;};
 const root=convert(parse(HTML));
 const find=(target,node=root)=>{if((target[0]==='#'?node.id===target.slice(1):node.tagName===target))return node;for(const child of node.children){const match=find(target,child);if(match)return match;}return null;};
 const document={querySelector:find,createElement:tag=>new Element(tag),body:find('body'),activeElement:null};
 const audio=find('audio');audio.paused=true;audio.pause=()=>{audio.paused=true;audio.onpause?.();};audio.load=()=>{};
 class MockDate extends Date{constructor(...args){super(...(args.length?args:[currentTime]));}static now(){return currentTime;}}
 const response=data=>({status:200,ok:true,json:async()=>data});
 const context=vm.createContext({document,Date:MockDate,Intl,URL,Uint8Array,matchMedia:()=>({matches:reduced}),cancelAnimationFrame(){},requestAnimationFrame(){},setTimeout:fn=>timers.push(fn),fetch:async(url,options={})=>{requests.push({url,options});if(handler)return handler(url,options);if(url==='/api/session')return response({csrf:'synthetic',personalization:{}});if(url.startsWith('/api/episodes'))return response({episodes:[]});if(url==='/api/storage')return response({activeAudioBytes:0,activeEpisodes:0,complete:true,freeStorageBytes:1e9});if(url.startsWith('/api/logbook'))return response(payload);return response({ok:true});}});
 vm.runInContext(JS,context);
 return {find,document,requests,timers,run:s=>vm.runInContext(s,context),respond:response,setHandler:fn=>handler=fn,setDate:date=>currentTime=Date.parse(date),context};
}
async function opened(options){const h=harness(options);await settle();h.find('#tab-logbook').onclick();await settle();assert.equal(h.find('#logbook').hidden,false);return h;}
function flat(value){return JSON.parse(JSON.stringify(value));}
test('Singapore date, strict dates, weeks, and weekend habit rules are independent of viewer timezone',()=>{
 assert.equal(model.singaporeDate(new Date('2026-10-18T15:59:59Z')),'2026-10-18');assert.equal(model.singaporeDate(new Date('2026-10-18T16:00:00Z')),'2026-10-19');assert.equal(model.monday('2026-10-18'),'2026-10-12');assert.equal(model.monday('2026-10-19'),'2026-10-19');assert.equal(model.validDate('2026-02-30'),false);assert.equal(model.validDate('2024-02-29'),true);assert.equal(model.habitsFor('2026-10-18').length,4);assert.equal(model.habitsFor(TODAY).length,5);
});
test('offered days include today plus at most five preceding unfinished calendar days after feature start',()=>{
 assert.deepEqual(model.offeredDates(TODAY,TODAY),[TODAY]);assert.deepEqual(model.offeredDates(TODAY,'2026-10-01',[record('2026-10-18'),record(TODAY)]),[TODAY,'2026-10-17','2026-10-16','2026-10-15','2026-10-14']);assert.ok(!model.offeredDates(TODAY,'2026-10-01').includes('2026-10-13'));assert.deepEqual(model.offeredDates(TODAY,'2026-10-17'),[TODAY,'2026-10-18','2026-10-17']);
});
test('Done payload explicitly records false, weekend not-applicable is absent, and fitness is one habit',()=>{
 assert.deepEqual(model.savePayload(TODAY,{habits:{noSmoke:true}}),{version:0,habits:{noSmoke:true,noSugar:false,publicTransport:false,fitness:false,meditation:false},fitnessActivities:[]});assert.equal('publicTransport' in model.savePayload('2026-10-18').habits,false);assert.deepEqual(model.savePayload(TODAY,{habits:{fitness:true},fitnessActivities:['yoga','walk','walk','invalid']}).fitnessActivities,['walk','yoga']);assert.deepEqual(model.savePayload(TODAY,{fitnessActivities:['walk']}).fitnessActivities,[]);
});
test('invalid, duplicate, pre-start, future, and incomplete server records fail closed',()=>{
 for(const value of [state({records:[record(TODAY),record(TODAY)]}),state({records:[record('2026-10-18')]}),state({records:[record('2026-10-20')]}),state({records:[{...record(TODAY),habits:{noSmoke:false}}]}),state({weekStart:'2026-10-20'})])assert.throws(()=>model.readState(value));
});
test('Log book loads only on its tab, shows today alone initially, and keeps history collapsed',async()=>{
 const h=harness();await settle();assert.equal(h.requests.filter(r=>r.url.startsWith('/api/logbook')).length,0);h.find('#tab-logbook').onclick();await settle();assert.equal(h.find('#logbook-day-title').textContent,'Monday');assert.equal(h.find('#logbook-days').hidden,true);assert.equal(h.find('#logbook-day').textContent.includes('One way public transport'),true);assert.equal(h.find('#listening').hidden,true);assert.notEqual(h.find('#logbook-history').open,true);assert.equal(h.find('#logbook-history-days').textContent.includes('Not logged'),true);
});
test('circle removes a habit, retains Undo and keyboard focus, and never saves before Done',async()=>{
 const h=await opened();h.find('#log-check-noSmoke').onclick();assert.equal(h.find('#log-check-noSmoke'),null);assert.equal(h.document.activeElement.id,'log-check-noSugar');assert.match(h.find('#logbook-day').textContent,/Checked · 1/);const undo=h.find('#logbook-day').children.flatMap(n=>n.children).flatMap(n=>n.children).find(n=>n.attributes['aria-label']==='Undo No smoke');assert.ok(undo);undo.onclick();assert.ok(h.find('#log-check-noSmoke'));assert.equal(h.document.activeElement.id,'log-check-noSmoke');assert.equal(h.requests.filter(r=>r.options.method==='PUT').length,0);
});
test('Done saves checked true and unchecked false once, then shows an immutable honest summary',async()=>{
 const h=await opened();h.find('#log-check-noSmoke').onclick();let body;h.setHandler(async(url,options)=>{body=JSON.parse(options.body);return h.respond({record:record(TODAY,body.habits)});});await h.find('#logbook-done').onclick();assert.deepEqual(body.habits,{noSmoke:true,noSugar:false,publicTransport:false,fitness:false,meditation:false});assert.equal(h.find('#logbook-done'),null);assert.match(h.find('#logbook-day').textContent,/Didn’t do/);assert.match(h.find('#logbook-day').textContent,/Saved/);assert.equal(h.run('logbookDrafts.size'),0);
});
test('missed habits in a completed earlier day do not keep that day in catch-up',async()=>{
 const h=await opened({payload:state({startDate:'2026-10-14',records:[record('2026-10-18')]})});assert.equal(h.find('#logbook-days').children.length,5);assert.ok(!h.find('#logbook-days').textContent.includes('18 Oct'));assert.match(h.find('#logbook-history-days').textContent,/Monday/);
});
test('weekend list omits transport and saved weekend summary marks it not applicable',async()=>{
 const h=await opened({payload:state({today:'2026-10-18',startDate:'2026-10-18',weekStart:'2026-10-12',records:[record('2026-10-18')]})});assert.match(h.find('#logbook-day').textContent,/Sunday/);assert.match(h.find('#logbook-day').textContent,/Not applicable on weekends/);assert.equal(h.find('#log-check-publicTransport'),null);
});
test('a failed or ambiguous save keeps exact selections frozen for idempotent retry',async()=>{
 const h=await opened();h.find('#log-check-noSmoke').onclick();const bodies=[];h.setHandler(async(url,options)=>{bodies.push(options.body);if(bodies.length===1)throw Error('Offline');return h.respond({record:record(TODAY,JSON.parse(options.body).habits)});});await h.find('#logbook-done').onclick();assert.equal(h.find('#logbook-done').textContent,'Retry Done');assert.equal(h.find('#log-check-noSugar').disabled,true);h.find('#log-check-noSugar').onclick();assert.equal(h.run('logbookDrafts.get(logbookDate).habits.noSugar'),undefined);await h.find('#logbook-done').onclick();assert.equal(bodies.length,2);assert.equal(bodies[0],bodies[1]);assert.equal(h.find('#logbook-done'),null);
});
test('concurrent save conflict displays saved values and does not invite endless retry',async()=>{
 const h=await opened();h.find('#log-check-noSmoke').onclick();h.setHandler(async()=>({status:409,ok:false,json:async()=>({error:'Already saved',currentRecord:record(TODAY,{meditation:true})})}));await h.find('#logbook-done').onclick();assert.equal(h.find('#logbook-done'),null);assert.match(h.find('#logbook-message').textContent,/already saved in another session/);assert.match(h.find('#logbook-message').textContent,/new selections were not applied/);assert.equal(h.run('logbookRecords.get(logbookDate).habits.noSmoke'),false);assert.equal(h.run('logbookRecords.get(logbookDate).habits.meditation'),true);
});
test('rapid Done clicks create one request and lock day switching and all choices while saving',async()=>{
 const h=await opened({payload:state({startDate:'2026-10-18'})});let finish,count=0;h.setHandler(async()=>{count++;return new Promise(r=>finish=()=>r(h.respond({record:record(TODAY)})));});const first=h.find('#logbook-done').onclick();await h.find('#logbook-done').onclick();assert.equal(count,1);assert.equal(h.find('#logbook-done').disabled,true);assert.equal(h.find('#log-check-noSmoke').disabled,true);assert.ok(h.find('#logbook-days').children.every(button=>button.disabled));finish();await first;
});
test('late load and late save responses cannot restore private DOM after Lock',async()=>{
 for(const operation of ['load','save']){const h=await opened();let finish;h.setHandler(async()=>new Promise(r=>finish=data=>r(h.respond(data))));const pending=operation==='load'?h.run('loadLogbook()'):h.find('#logbook-done').onclick();h.run('resetToLogin()');finish(operation==='load'?state():{record:record(TODAY)});await pending;assert.equal(h.find('#player').hidden,true);assert.equal(h.find('#logbook-day').textContent,'');assert.equal(h.find('#logbook-history-days').textContent,'');assert.equal(h.run('logbookRecords.size'),0);assert.equal(h.run('logbookDrafts.size'),0);}
});
test('401 during save clears all private habit state and returns to PIN entry',async()=>{
 const h=await opened();h.find('#log-check-noSmoke').onclick();h.setHandler(async()=>({status:401,ok:false}));await h.find('#logbook-done').onclick();assert.equal(h.find('#player').hidden,true);assert.equal(h.find('#logbook-day').textContent,'');assert.equal(h.run('logbookAttempts.size'),0);assert.equal(h.document.activeElement.id,'pin');
});
test('slash animation honors reduced motion and cannot repopulate after reset',async()=>{
 const h=await opened({reduced:false});h.find('#log-check-noSmoke').onclick();assert.equal(h.timers.length,1);assert.equal(h.find('#log-check-noSmoke').attributes['aria-checked'],'true');assert.equal(h.find('#logbook-done').disabled,true);h.run('resetToLogin()');h.timers[0]();assert.equal(h.find('#logbook-day').textContent,'');assert.equal(h.run('logbookAnimations.size'),0);assert.match(CSS,/@media\(prefers-reduced-motion:reduce\)/);assert.match(CSS,/@keyframes log-slash/);
});
test('a user action after Singapore midnight refreshes dates before toggling the old day',async()=>{
 const h=await opened();h.setDate('2026-10-19T16:01:00Z');h.setHandler(async()=>h.respond(state({today:'2026-10-20',startDate:TODAY,weekStart:TODAY})));h.find('#log-check-noSmoke').onclick();await settle();assert.equal(h.run('logbookState.today'),'2026-10-20');assert.equal(h.find('#logbook-day-title').textContent,'Tuesday');assert.equal(h.run('logbookDrafts.get("2026-10-19").habits.noSmoke'),undefined);assert.equal(h.requests.filter(r=>r.options.method==='PUT').length,0);
});
test('no browser persistence, external analytics or habit reminder scheduler is introduced',()=>{
 assert.ok(!JS.includes('localStorage'));assert.ok(!JS.includes('sessionStorage'));assert.ok(!JS.includes('indexedDB'));assert.ok(!JS.includes('Notification'));assert.ok(!JS.includes('setInterval'));assert.equal(flat(model.savePayload(TODAY)).version,0);
});

test('finishing an animation after changing tabs never steals keyboard focus',async()=>{
 const h=await opened({reduced:false});h.find('#log-check-noSmoke').onclick();h.find('#tab-latest').onclick();h.find('#tab-latest').focus();h.timers[0]();assert.equal(h.document.activeElement.id,'tab-latest');assert.equal(h.find('#latest').hidden,false);
});
