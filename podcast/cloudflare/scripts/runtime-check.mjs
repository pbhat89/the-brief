// Local workerd/SQLite/KV smoke test. Synthetic values only; no remote resources.
import {spawn} from 'node:child_process';
import assert from 'node:assert/strict';
import {pinHash,digest} from '../src/security.js';
const hash=await pinHash('123456789012','isolated-test');
const publisher='synthetic-test-token-'.repeat(3);
const child=spawn(process.execPath,['node_modules/wrangler/bin/wrangler.js','dev','--local','--port','9878','--ip','127.0.0.1','--persist-to','.wrangler/runtime-'+crypto.randomUUID(),'--var','PIN_SALT:isolated-test','--var','PIN_HASH:'+hash,'--var','PUBLISHER_TOKEN_HASH:'+await digest(publisher),'--var','EXPIRY_APPROVED:true'],{env:{...process.env,WRANGLER_SEND_METRICS:'false',WRANGLER_LOG_PATH:'.wrangler/logs'},stdio:['ignore','pipe','pipe']});
let logs='';child.stdout.on('data',b=>logs+=b);child.stderr.on('data',b=>logs+=b);
const base='http://127.0.0.1:9878';
try{
 let ready=false;for(let i=0;i<80;i++){try{const r=await fetch(base);if(r.ok){ready=true;break}}catch{}await new Promise(r=>setTimeout(r,250));}assert.ok(ready,logs);
 assert.equal((await fetch(base+'/api/episodes')).status,401);
 const login=await fetch(base+'/api/login',{method:'POST',headers:{Origin:base,'Content-Type':'application/json'},body:'{"pin":"123456789012"}'});
 assert.equal(login.status,200,await login.clone().text());const cookie=login.headers.get('set-cookie').split(';')[0];
 const session=await fetch(base+'/api/episodes',{headers:{Cookie:cookie}});assert.equal(session.status,200);assert.deepEqual(await session.json(),{episodes:[]});
 const bytes=new Uint8Array(7360000);bytes.set([255,251,144,0]);bytes.set([255,251,144,0],417);
 const upload=await fetch(base+'/api/upload',{method:'POST',headers:{Origin:base,Authorization:'Bearer '+publisher,'X-Brief-Publish':'1','Content-Type':'audio/mpeg','Content-Length':String(bytes.length)},body:bytes});assert.equal(upload.status,201,await upload.clone().text());const meta=await upload.json();
 const full=await fetch(base+'/api/media/'+meta.id,{headers:{Cookie:cookie}});assert.equal(full.status,200);assert.equal((await full.arrayBuffer()).byteLength,bytes.length);
 const partial=await fetch(base+'/api/media/'+meta.id,{headers:{Cookie:cookie,Range:'bytes=7359900-'}});assert.equal(partial.status,206);assert.equal((await partial.arrayBuffer()).byteLength,100);
 const head=await fetch(base+'/api/media/'+meta.id,{method:'HEAD',headers:{Cookie:cookie}});assert.equal(head.headers.get('Content-Length'),String(bytes.length));assert.equal(await head.text(),'');
 for(const Range of ['bytes=1-99','invalid','bytes=99999999-']){const h=await fetch(base+'/api/media/'+meta.id,{method:'HEAD',headers:{Cookie:cookie,Range}});assert.equal(h.status,200);assert.equal(h.headers.get('Content-Length'),String(bytes.length));assert.equal(h.headers.get('Content-Range'),null);assert.equal(await h.text(),'');}
 const attempts=await Promise.all(Array.from({length:11},()=>fetch(base+'/api/login',{method:'POST',headers:{Origin:base},body:'{"pin":"bad"}'})));
 assert.equal(attempts.filter(r=>r.status===401).length,9);assert.equal(attempts.filter(r=>r.status===429).length,2);
 console.log('PASS: workerd + SQLite DO PIN verification, session, private KV list, 7.36 MB upload/full/range/HEAD, concurrent global limiter');
}finally{child.kill();}
