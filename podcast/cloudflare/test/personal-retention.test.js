import {test} from 'node:test';
import assert from 'node:assert/strict';
import worker,{migratePersonalRetention,deletePersonalEpisode,Auth} from '../src/worker.js';
import {digest} from '../src/security.js';
const id='aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';
function setup(){
 const data=new Map(),state=new Map(),writes=[];
 const kv={get:async(k,type)=>{const v=data.get(k);return type==='json'&&typeof v==='string'?JSON.parse(v):v},put:async(k,v,o)=>{writes.push([k,o]);data.set(k,v)},delete:async k=>data.delete(k),list:async({prefix,cursor,limit})=>{const keys=[...data.keys()].filter(k=>k.startsWith(prefix)).sort(),start=Number(cursor||0),chunk=keys.slice(start,start+limit);return {keys:chunk.map(name=>({name})),cursor:String(start+chunk.length),list_complete:start+chunk.length>=keys.length}}};
 const storage={get:async k=>state.get(k),put:async(k,v)=>state.set(k,structuredClone(v))};
 const env={EPISODES:kv};return {data,state,writes,env,storage};
}
function seed(h,extra={}){const meta={id,collection:'personal',created:1,expires:2,size:8,title:'Synthetic',...extra};h.data.set('meta:'+meta.id,JSON.stringify(meta));h.data.set('audio:'+meta.id,new Uint8Array(8).buffer);h.data.set('active-personal:'+meta.id,JSON.stringify(meta));return meta;}
test('migration cancels native expiry for surviving legacy bytes without changing them',async()=>{
 const h=setup();seed(h);const before=h.data.get('audio:'+id);const result=await migratePersonalRetention(h.env,h.storage);
 assert.equal(result.preserved,1);assert.equal(result.complete,true);assert.equal(h.data.get('audio:'+id),before);
 const meta=JSON.parse(h.data.get('meta:'+id));assert.equal(meta.expires,null);assert.equal(meta.retention,'manual');assert.ok(h.writes.every(([,options])=>options===undefined));
 const count=h.writes.length;await migratePersonalRetention(h.env,h.storage);assert.equal(h.writes.length,count,'completed migration never rewrites again');
});
test('missing bytes are never invented and daily/tombstoned episodes are never preserved',async()=>{
 const h=setup();seed(h);h.data.delete('audio:'+id);let result=await migratePersonalRetention(h.env,h.storage);assert.equal(result.missing,1);assert.equal(h.writes.length,0);
 for(const extra of [{collection:'daily'},{deleted:3}]){const h=setup();seed(h,extra);await migratePersonalRetention(h.env,h.storage);assert.equal(h.writes.length,0);}
});
test('bounded migration resumes all metadata pages, retaining only personal bytes',async()=>{
 const h=setup();for(let i=0;i<14;i++)seed(h,{id:String(i).padStart(36,'0'),collection:i%2?'daily':'personal'});
 let result;for(let i=0;i<3;i++)result=await migratePersonalRetention(h.env,h.storage);assert.equal(result.complete,true);assert.equal(result.preserved,7);
});
test('manual deletion still removes migrated bytes and keeps a tombstone',async()=>{
 const h=setup();seed(h);await migratePersonalRetention(h.env,h.storage);assert.equal((await deletePersonalEpisode(h.env,id)).status,200);assert.ok(!h.data.has('audio:'+id));assert.ok(!h.data.has('active-personal:'+id));assert.ok(JSON.parse(h.data.get('meta:'+id)).deleted);await migratePersonalRetention(h.env,h.storage);assert.ok(!h.data.has('audio:'+id));
});
test('delete observed before metadata rewrite wins and cleans attempted preservation',async()=>{
 const h=setup();seed(h);const get=h.env.EPISODES.get;let reads=0;h.env.EPISODES.get=async(k,t)=>{if(k==='meta:'+id&&++reads===2)return {...JSON.parse(h.data.get(k)),deleted:3};return get(k,t)};await migratePersonalRetention(h.env,h.storage);assert.ok(!h.data.has('audio:'+id));assert.ok(!h.data.has('active-personal:'+id));
});
test('migration and explicit delete share a queue without blocking session events',async()=>{
 const h=setup();seed(h);const token='synthetic';h.state.set('s:'+await digest(token),{csrf:'csrf',exp:Date.now()/1000+60,version:'hash'});
 const auth=new Auth({storage:h.storage},{...h.env,PIN_HASH:'hash'});let gated=0;const serialize=auth.serializeRetention.bind(auth);auth.serializeRetention=fn=>{gated++;return serialize(fn)};
 const call=x=>auth.fetch(new Request('https://internal/',{method:'POST',body:JSON.stringify(x)}));
 assert.equal((await call({op:'retention:migrate'})).status,200);assert.equal((await call({op:'episode:delete',token,csrf:'csrf',id})).status,200);assert.equal(gated,2);
 assert.equal((await call({op:'episode:delete',token,csrf:'wrong',id})).status,403);
});
test('public callers cannot invoke the internal migration operation',async()=>{
 const h=setup();assert.equal((await worker.fetch(new Request('https://example.com/api/retention:migrate',{method:'POST',headers:{Origin:'https://example.com'}}),h.env)).status,401);
});

test('interruption before index or metadata commit remains retryable',async()=>{
 for(const failKey of ['active-personal:'+id,'meta:'+id]){const h=setup();seed(h);const put=h.env.EPISODES.put;let fail=true;h.env.EPISODES.put=async(k,v,o)=>{if(fail&&k===failKey)throw Error('synthetic interruption');return put(k,v,o)};await assert.rejects(migratePersonalRetention(h.env,h.storage));assert.notEqual(JSON.parse(h.data.get('meta:'+id)).retention,'manual');fail=false;const result=await migratePersonalRetention(h.env,h.storage);assert.equal(result.preserved,1);assert.equal(JSON.parse(h.data.get('active-personal:'+id)).expires,null);assert.equal(JSON.parse(h.data.get('meta:'+id)).retention,'manual');}
});
