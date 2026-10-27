import {test} from 'node:test';
import assert from 'node:assert/strict';
import worker from '../src/worker.js';
import {digest,TTL} from '../src/security.js';
const origin='https://brief.example';
test('audio and active index expire together; private metadata has no expiry',async()=>{
 const writes=[];const token='synthetic_publisher_'.repeat(3);
 const env={PUBLISHER_TOKEN_HASH:await digest(token),EXPIRY_APPROVED:'true',EPISODES:{put:async(...args)=>writes.push(args)}};
 const bytes=new Uint8Array(834);bytes.set([255,251,144,0]);bytes.set([255,251,144,0],417);
 const before=Math.floor(Date.now()/1000);
 const r=await worker.fetch(new Request(origin+'/api/upload',{method:'POST',headers:{Origin:origin,Authorization:'Bearer '+token,'X-Brief-Publish':'1','Content-Type':'audio/mpeg','Content-Length':String(bytes.length)},body:bytes}),env);
 assert.equal(r.status,201);const meta=await r.json();assert.ok(Math.abs(meta.expires-before-TTL)<2);
 assert.equal(writes.length,3);
 assert.equal(writes[0][0],'audio:'+meta.id);assert.equal(writes[0][2].expiration,meta.expires);
 assert.equal(writes[1][0],'meta:'+meta.id);assert.equal(writes[1].length,2);
 assert.equal(writes[2][0],'active:'+meta.id);assert.equal(writes[2][2].expiration,meta.expires);
});
test('retained expired metadata cannot play or crowd the active list',async()=>{
 const id='aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';let listing;
 const expired={id,expires:1,size:834};
 const env={AUTH:{idFromName:()=>1,get:()=>({fetch:async()=>new Response('{"csrf":"synthetic"}')})},EPISODES:{list:async opts=>{listing=opts;return {keys:[{name:'active:'+id}]}},get:async k=>{if(Array.isArray(k))return new Map(k.map(key=>[key,expired]));assert.ok(!k.startsWith('audio:'));return expired;}}};
 const request=p=>new Request(origin+p,{headers:{Cookie:'__Host-brief=synthetic'}});
 const r=await worker.fetch(request('/api/episodes'),env);assert.deepEqual(await r.json(),{episodes:[]});assert.equal(listing.prefix,'active:');
 for(const path of ['/api/media/','/api/episodes/'])assert.equal((await worker.fetch(request(path+id),env)).status,404);
});
