import {test} from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {parse} from 'parse5';
import {JS} from '../src/app.js';
import {HTML,CSS} from '../src/ui.js';
import {LogbookModel as model} from '../src/logbook-model.js';
const TODAY='2026-10-22';
const settle=()=>new Promise(resolve=>setImmediate(resolve));
function harness({episodes=[],reduced=true,instant='2026-10-21T23:00:00Z',records=[]}={}){
 let now=Date.parse(instant);const requests=[];
 class Element{
  constructor(tag){this.tagName=tag;this.children=[];this.attributes={};this.hidden=false;this.disabled=false;this.style={setProperty(){}};this.classList={add(){},remove(){}};this._text='';this.value='';this.open=false;}
  get textContent(){return this._text+this.children.map(n=>n.textContent).join('');}
  set textContent(text){this._text=String(text);this.children=[];}
  append(...nodes){this.children.push(...nodes);}
  replaceChildren(...nodes){this._text='';this.children=[...nodes];}
  setAttribute(k,v){this.attributes[k]=String(v);if(k==='id')this.id=v;}
  getAttribute(k){return k==='src'?this.src||this.attributes.src||null:this.attributes[k]??null;}
  removeAttribute(k){delete this.attributes[k];if(k==='src')this.src='';}
  focus(){document.activeElement=this;}
  showModal(){this.open=true;}
  close(){this.open=false;this.onclose?.();}
 }
 const convert=n=>{const node=new Element(n.tagName||'root');for(const a of n.attrs||[]){node.setAttribute(a.name,a.value);if(a.name==='hidden')node.hidden=true;}for(const c of n.childNodes||[]){if(c.nodeName==='#text')node._text+=c.value;else node.append(convert(c));}return node;};
 const root=convert(parse(HTML));
 const find=(target,node=root)=>{if(target[0]==='#'?node.id===target.slice(1):node.tagName===target)return node;for(const child of node.children){const match=find(target,child);if(match)return match;}return null;};
 const document={querySelector:find,createElement:tag=>new Element(tag),body:find('body'),activeElement:null,addEventListener(){}};
 const audio=find('audio');audio.paused=true;audio.pause=()=>{audio.paused=true;audio.onpause?.();};audio.load=()=>{};
 class MockDate extends Date{constructor(...args){super(...(args.length?args:[now]));}static now(){return now;}}
 const response=data=>({status:200,ok:true,json:async()=>data});
 const context=vm.createContext({document,Date:MockDate,Intl,URL,Uint8Array,matchMedia:()=>({matches:reduced}),cancelAnimationFrame(){},requestAnimationFrame(){},fetch:async(url,options={})=>{requests.push({url,options});if(url==='/api/session')return response({csrf:'synthetic',personalization:{}});if(url.startsWith('/api/episodes'))return response({episodes});if(url==='/api/storage')return response({activeAudioBytes:0,activeEpisodes:0,complete:true,freeStorageBytes:1e9});if(url.startsWith('/api/logbook'))return response({schemaVersion:1,timeZone:'Asia/Singapore',today:TODAY,startDate:TODAY,weekStart:model.monday(TODAY),records,pendingDates:[TODAY]});return response({ok:true});}});
 vm.runInContext(JS,context);
 return {find,document,requests,run:s=>vm.runInContext(s,context),setDate:value=>now=Date.parse(value)};
}
function episode(id,edition,created='2026-10-21T23:00:00Z'){return {id,title:id,edition,created:Date.parse(created)/1000,expires:Date.parse('2026-10-29T00:00:00Z')/1000,chapters:[]};}
test('Today selects its Singapore edition, leaves earlier audio only in Previous, and never promotes tomorrow',async()=>{
 const h=harness({episodes:[episode('tomorrow','2026-10-23','2026-10-22T00:00:00Z'),episode('today',TODAY),episode('yesterday','2026-10-21','2026-10-21T00:00:00Z')]});await settle();
 assert.equal(h.find('#title').textContent,'today');assert.equal(h.run('todayEpisode().id'),'today');assert.equal(h.find('#episodes')?.children.length||0,0);assert.equal(h.find('#previous-audio').children.length,3);
 h.find('#tab-previous').onclick();h.find('#previous-audio').children.find(b=>b.textContent.includes('yesterday')).onclick();assert.equal(h.find('#previous').hidden,false);assert.equal(h.find('#title').textContent,'yesterday');
 h.find('#tab-latest').onclick();assert.equal(h.find('#title').textContent,'today');assert.equal(h.find('#latest').hidden,false);
});
test('when only yesterday audio exists, Today is honestly unavailable but same-day HTML is usable',async()=>{
 const h=harness({episodes:[episode('yesterday','2026-10-21','2026-10-21T00:00:00Z')]});await settle();
 assert.equal(h.run('todayEpisode()'),null);assert.equal(h.find('#listening').hidden,true);assert.equal(h.find('#today-read').disabled,false);h.find('#today-read').onclick();assert.equal(h.find('#viewer').hidden,false);assert.match(h.find('#viewer-date').textContent,/22 October 2026/);h.find('#reader-back').onclick();assert.equal(h.find('#latest').hidden,false);
});
test('Today never substitutes yesterday HTML when same-day written edition is absent',async()=>{
 const h=harness({instant:'2030-01-01T00:00:00Z'});await settle();assert.equal(h.find('#today-read').hidden,true);assert.match(h.find('#today-read-note').textContent,/not available/);assert.equal(h.run('currentReport'),null);
});
test('daily quote is stable within the Singapore day, changes across midnight, and is plainly attributed',async()=>{
 const h=harness({instant:'2026-10-22T15:59:59Z'});await settle();const first=h.find('#daily-quote').textContent;assert.ok(first.length>10);assert.match(h.find('#quote-credit').textContent,/reflection|original/i);h.run('renderDailyQuote()');assert.equal(h.find('#daily-quote').textContent,first);h.setDate('2026-10-22T16:00:00Z');h.run('renderDailyQuote()');assert.notEqual(h.find('#daily-quote').textContent,first);
});
test('task completion opens an accessible celebration before settling to strikethrough without an implicit save',async()=>{
 const h=harness();await settle();h.find('#tab-logbook').onclick();await settle();const check=h.find('#log-check-noSmoke');check.onclick();assert.equal(h.find('#logbook-celebration').open,true);assert.equal(h.document.activeElement.id,'celebration-close');assert.equal(h.requests.filter(r=>r.options.method==='PUT').length,0);check.onclick();h.find('#celebration-close').onclick();assert.equal(h.find('#logbook-celebration').open,false);assert.match(h.find('#logbook-day').textContent,/Checked/);assert.match(CSS,/text-decoration\s*:\s*line-through/);assert.equal(h.requests.filter(r=>r.options.method==='PUT').length,0);
});
test('Escape, navigation and Lock clean up celebration and never restore private content',async()=>{
 for(const action of ['escape','navigate','lock']){const h=harness({reduced:false});await settle();h.find('#tab-logbook').onclick();await settle();h.find('#log-check-noSmoke').onclick();const dialog=h.find('#logbook-celebration');assert.equal(dialog.open,true);
  if(action==='escape'){dialog.oncancel({preventDefault(){}});assert.equal(dialog.open,false);assert.equal(h.document.activeElement.id,'log-check-noSugar');}
  if(action==='navigate'){h.find('#tab-latest').onclick();assert.equal(dialog.open,false);assert.equal(h.find('#latest').hidden,false);}
  if(action==='lock'){h.run('resetToLogin()');assert.equal(dialog.open,false);assert.equal(h.find('#logbook-day').textContent,'');assert.equal(h.run('logbookDrafts.size'),0);}
 }
});
test('saved completed records do not celebrate again on loading the Log book',async()=>{
 const record={date:TODAY,version:1,status:'completed',habits:{...model.savePayload(TODAY).habits,noSmoke:true},fitnessActivities:[],savedAt:'2026-10-22T01:00:00Z'};const h=harness({records:[record]});await settle();h.find('#tab-logbook').onclick();await settle();assert.equal(h.find('#logbook-celebration').open,false);assert.match(h.find('#logbook-day').textContent,/Saved/);
});
test('daily matching respects explicit editions and legacy created dates across the Singapore midnight boundary',async()=>{
 const h=harness({episodes:[episode('uploaded-today-for-yesterday','2026-10-21'),episode('legacy-today',undefined,'2026-10-21T16:00:00Z'),episode('legacy-yesterday',undefined,'2026-10-21T15:59:59Z')]});await settle();assert.equal(h.run('todayEpisode().id'),'legacy-today');assert.equal(h.run("singaporeDay('2026-10-21T15:59:59Z')"),'2026-10-21');assert.equal(h.run("singaporeDay('2026-10-21T16:00:00Z')"),TODAY);
});
test('celebration has an accessible name and description, with a real keyboard-operable dismiss button',async()=>{
 const h=harness();await settle();const dialog=h.find('#logbook-celebration');assert.equal(dialog.tagName,'dialog');const label=dialog.getAttribute('aria-labelledby'),description=dialog.getAttribute('aria-describedby');assert.ok(label&&h.find('#'+label).textContent.trim());assert.ok(description&&h.find('#'+description));assert.equal(h.find('#celebration-close').tagName,'button');
});
