import {test} from 'node:test';
import assert from 'node:assert/strict';
import worker,{deletePersonalEpisode} from '../src/worker.js';
import {digest,TTL} from '../src/security.js';
const origin='https://brief.example',token='synthetic_publisher_'.repeat(3),id='aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';
const bytes=new Uint8Array(834);bytes.set([255,251,144,0]);bytes.set([255,251,144,0],417);
async function setup(){
 const data=new Map(),writes=[],deletes=[];
 const env={PUBLISHER_TOKEN_HASH:await digest(token),EXPIRY_APPROVED:'true',AUTH:{idFromName:()=>1,get:()=>({fetch:async r=>{const x=await r.json();if(x.op==='episode:delete'&&x.token==='synthetic'&&x.csrf==='csrf-value')return deletePersonalEpisode(env,x.id);return x.token==='synthetic'?new Response('{"csrf":"csrf-value"}'):new Response('Unauthorized',{status:401})}})},EPISODES:{
  get:async(k,type)=>{if(Array.isArray(k))return new Map(k.map(key=>[key,typeof data.get(key)==='string'?JSON.parse(data.get(key)):data.get(key)]));const v=data.get(k);return type==='json'&&typeof v==='string'?JSON.parse(v):v},
  put:async(k,v,opts)=>{writes.push([k,v,opts]);data.set(k,v)},
  delete:async k=>{deletes.push(k);data.delete(k)},
  list:async({prefix})=>({keys:[...data.keys()].filter(k=>k.startsWith(prefix)).map(name=>({name})),list_complete:true})
 }};
 const request=(path,options={})=>worker.fetch(new Request(origin+path,{...options,headers:{Cookie:'__Host-brief=synthetic',...options.headers}}),env);
 const upload=(extra={})=>request('/api/upload',{method:'POST',headers:{Origin:origin,Authorization:'Bearer '+token,'X-Brief-Publish':'1','Content-Type':'audio/mpeg','Content-Length':String(bytes.length),...extra},body:bytes});
 const remove=(episode=id,extra={})=>request('/api/episodes/'+episode,{method:'DELETE',headers:{Origin:origin,'X-CSRF-Token':'csrf-value','X-Brief-Delete':episode,...extra}});
 return {data,env,writes,deletes,request,upload,remove};
}
const personal={'X-Episode-Collection':'personal','X-Episode-Key':'example-topic','X-Episode-Duration':'753.25','X-Episode-Title':'Example topic','X-Episode-Chapters':'[{"title":"Start","start":0},{"title":"Context","start":30}]'};
test('personal upload uses a separate persistent index and preserves metadata/duration',async()=>{
 const h=await setup(),r=await h.upload(personal);assert.equal(r.status,201);const meta=await r.json();
 assert.equal(meta.collection,'personal');assert.equal(meta.episodeKey,'example-topic');assert.equal(meta.duration,753.25);assert.equal(meta.expires,null);assert.equal(meta.retention,'manual');
 assert.ok(h.data.has('audio:'+meta.id));assert.ok(h.data.has('meta:'+meta.id));assert.ok(h.data.has('active-personal:'+meta.id));assert.ok(!h.data.has('active:'+meta.id));
 assert.equal(h.writes[0][2],undefined);assert.equal(h.writes[1][2],undefined);assert.equal(h.writes[2][2],undefined);
});
test('default and legacy episodes remain daily; personal uploads do not displace daily listing',async()=>{
 const h=await setup();const daily=await (await h.upload()).json();const topic=await (await h.upload(personal)).json();
 const legacy={id,created:1,expires:Date.now()/1000+1000,size:100,title:'Legacy'};h.data.set('meta:'+id,legacy);h.data.set('active:'+id,legacy);
 const defaultList=await (await h.request('/api/episodes')).json();assert.deepEqual(defaultList.episodes.map(e=>e.id),[daily.id,id]);assert.ok(defaultList.episodes.every(e=>e.collection==='daily'));
 const personalList=await (await h.request('/api/episodes?collection=personal')).json();assert.deepEqual(personalList.episodes.map(e=>e.id),[topic.id]);
 const all=await (await h.request('/api/episodes?collection=all')).json();assert.equal(all.episodes.length,3);assert.equal((await h.request('/api/episodes?collection=invalid')).status,400);
});
test('invalid collection, stable key and duration reject before any writes',async()=>{
 for(const extra of [{'X-Episode-Collection':'private'},{'X-Episode-Collection':'personal'}, {...personal,'X-Episode-Key':'../other'}, {...personal,'X-Episode-Key':'-bad'}, {...personal,'X-Episode-Key':'x'.repeat(81)}, {'X-Episode-Key':'daily-key'}, ...['NaN','Infinity','0','-3','86401',''].map(d=>({...personal,'X-Episode-Duration':d}))]){const h=await setup();assert.equal((await h.upload(extra)).status,400);assert.equal(h.writes.length,0);}
});
test('personal metadata, storage, and deletion reject anonymous or forged sessions',async()=>{
 const h=await setup();for(const path of ['/api/episodes?collection=personal','/api/episodes?collection=all','/api/storage'])for(const Cookie of ['','__Host-brief=forged'])assert.equal((await h.request(path,{headers:{Cookie}})).status,401);
 for(const Cookie of ['','__Host-brief=forged'])assert.equal((await h.remove(id,{Cookie})).status,401);assert.equal(h.deletes.length,0);
});
test('deletion requires exact origin, CSRF, and episode confirmation; daily remains protected',async()=>{
 const h=await setup();const topic=await (await h.upload(personal)).json();
 for(const [extra,status] of [[{Origin:'https://other.example'},403],[{'Sec-Fetch-Site':'cross-site'},403],[{'X-CSRF-Token':'wrong'},403],[{'X-Brief-Delete':'different-id'},400]])assert.equal((await h.remove(topic.id,extra)).status,status);
 assert.ok(h.data.has('audio:'+topic.id));assert.equal(h.deletes.length,0);
 const daily=await (await h.upload()).json();assert.equal((await h.remove(daily.id)).status,400);assert.ok(h.data.has('audio:'+daily.id));
});
test('confirmed deletion removes physical audio/index, retains tombstone, and repeats safely',async()=>{
 const h=await setup(),topic=await (await h.upload(personal)).json();
 for(let i=0;i<2;i++){const r=await h.remove(topic.id);assert.equal(r.status,200);assert.deepEqual(await r.json(),{id:topic.id,deleted:true});}
 assert.ok(!h.data.has('audio:'+topic.id));assert.ok(!h.data.has('active-personal:'+topic.id));const meta=JSON.parse(h.data.get('meta:'+topic.id));assert.ok(meta.deleted);assert.equal(meta.episodeKey,'example-topic');
 assert.equal(h.writes.filter(([k])=>k==='meta:'+topic.id).length,2,'upload plus one tombstone, no duplicate write');
 for(const part of ['media','episodes'])for(const method of ['GET','HEAD'])assert.equal((await h.request('/api/'+part+'/'+topic.id,{method})).status,404);
 assert.deepEqual((await (await h.request('/api/episodes?collection=personal')).json()).episodes,[]);
});
test('interrupted physical cleanup remains hidden and supports retry',async()=>{
 const h=await setup(),topic=await (await h.upload(personal)).json();const remove=h.env.EPISODES.delete;let fail=true;h.env.EPISODES.delete=async k=>{if(fail)throw Error('Synthetic KV failure');return remove(k)};
 assert.equal((await h.remove(topic.id)).status,503);assert.ok(h.data.has('audio:'+topic.id));
 assert.equal((await h.request('/api/media/'+topic.id)).status,404);assert.deepEqual((await (await h.request('/api/episodes?collection=personal')).json()).episodes,[]);
 fail=false;assert.equal((await h.remove(topic.id)).status,200);assert.ok(!h.data.has('audio:'+topic.id));
});
test('storage is a bounded active-audio estimate, excluding expired and deleted records',async()=>{
 const h=await setup();await h.upload();const topic=await (await h.upload(personal)).json();
 const expired={id,collection:'personal',created:1,expires:2,size:9999};h.data.set('meta:'+id,expired);h.data.set('active-personal:'+id,expired);
 let storage=await (await h.request('/api/storage')).json();assert.equal(storage.activeAudioBytes,bytes.length*2);assert.equal(storage.activeEpisodes,2);assert.equal(storage.estimateOnly,true);assert.equal(storage.freeStorageBytes,1000000000);
 await h.remove(topic.id);storage=await (await h.request('/api/storage')).json();assert.equal(storage.activeAudioBytes,bytes.length);assert.equal(storage.activeEpisodes,1);
 const list=h.env.EPISODES.list;h.env.EPISODES.list=async o=>({...await list(o),list_complete:false});assert.equal((await (await h.request('/api/storage')).json()).complete,false);
});
test('missing, malformed or non-finite expiry and invalid sizes cannot serve media',async()=>{
 const h=await setup();for(const expires of [undefined,null,'9999999999','invalid',NaN,Infinity,-Infinity]){h.data.set('meta:'+id,{size:834,expires});h.data.set('audio:'+id,bytes.buffer);for(const part of ['episodes','media'])assert.equal((await h.request('/api/'+part+'/'+id)).status,404);}
 for(const size of [undefined,0,-1,1.5,Infinity,8388609]){h.data.set('meta:'+id,{expires:Date.now()/1000+100,size});assert.equal((await h.request('/api/media/'+id)).status,404);}
});
test('manual personal audio remains playable past seven days; daily expiry still rejects',async()=>{
 const h=await setup(),topic=await (await h.upload(personal)).json();topic.created=1;h.data.set('meta:'+topic.id,JSON.stringify(topic));
 assert.equal((await h.request('/api/media/'+topic.id)).status,200);assert.equal((await h.request('/api/media/'+topic.id,{method:'HEAD'})).status,200);
 const daily=await (await h.upload()).json();daily.expires=1;h.data.set('meta:'+daily.id,JSON.stringify(daily));assert.equal((await h.request('/api/media/'+daily.id)).status,404);
});
test('large library uses bulk metadata reads and new personal upload fails closed at safety cap',async()=>{
 const h=await setup();for(let n=0;n<90;n++){const key=String(n).padStart(36,'0'),meta={id:key,collection:'personal',retention:'manual',expires:null,created:n,size:834};h.data.set('meta:'+key,JSON.stringify(meta));h.data.set('active-personal:'+key,JSON.stringify(meta));}
 const get=h.env.EPISODES.get;let calls=0;h.env.EPISODES.get=async(...args)=>{calls++;return get(...args)};
 assert.equal((await (await h.request('/api/episodes?collection=all')).json()).episodes.length,90);assert.equal(calls,1);
 assert.equal((await h.upload(personal)).status,507);assert.equal(h.writes.length,0);
});
