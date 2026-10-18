import {test} from 'node:test';
import assert from 'node:assert/strict';
import worker from '../src/worker.js';
const request=headers=>new Request('https://brief.example/api/session',{headers});
test('personalization remains unavailable without an authenticated session',async()=>{
 const env={PLAYER_BRAND:'Private sample',PLAYER_GREETING:'Private greeting',AUTH:{idFromName:()=>1,get:()=>({fetch:async()=>new Response('Unauthorized',{status:401})})}};
 for(const headers of [{},{Cookie:'__Host-brief=forged'}]){const r=await worker.fetch(request(headers),env);assert.equal(r.status,401);assert.ok(!(await r.text()).includes('Private'));}
});
test('authenticated session returns bounded text preferences and empty defaults',async()=>{
 const env={AUTH:{idFromName:()=>1,get:()=>({fetch:async()=>new Response('{"csrf":"synthetic"}')})}};
 const get=async()=>await (await worker.fetch(request({Cookie:'__Host-brief=synthetic'}),env)).json();
 assert.deepEqual((await get()).personalization,{brand:'',greeting:''});
 env.PLAYER_BRAND='B'.repeat(90);env.PLAYER_GREETING='Hello\u0000'+ 'g'.repeat(180);
 const session=await get();assert.equal(session.csrf,'synthetic');assert.equal(session.personalization.brand.length,80);assert.equal(session.personalization.greeting.length,160);assert.ok(!session.personalization.greeting.includes('\u0000'));
});

