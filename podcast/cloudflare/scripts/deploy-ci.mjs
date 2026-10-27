// Run only in the protected deployment job, never in PR jobs.
import {mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {spawnSync} from 'node:child_process';
for(const k of ['CLOUDFLARE_API_TOKEN','CF_ACCOUNT_ID','CF_KV_ID','CF_WORKER_NAME'])if(!process.env[k])throw Error('Deployment configuration incomplete; no changes made.');
if(!/^[a-f0-9]{32}$/.test(process.env.CF_ACCOUNT_ID)||!/^[a-f0-9]{32}$/.test(process.env.CF_KV_ID)||!/^[a-z0-9-]{1,63}$/.test(process.env.CF_WORKER_NAME))throw Error('Invalid deployment configuration.');
if(process.env.AUDIO_EXPIRY_APPROVED!=='true')throw Error('Audio expiry approval must be explicitly configured.');
const dir=mkdtempSync(join(tmpdir(),'brief-deploy-'));
try{
 const config={name:process.env.CF_WORKER_NAME,account_id:process.env.CF_ACCOUNT_ID,main:resolve('src/worker.js'),compatibility_date:'2026-10-18',workers_dev:true,preview_urls:false,kv_namespaces:[{binding:'EPISODES',id:process.env.CF_KV_ID}],durable_objects:{bindings:[{name:'AUTH',class_name:'Auth'}]},migrations:[{tag:'v1',new_sqlite_classes:['Auth']}],vars:{EXPIRY_APPROVED:'true'},triggers:{crons:['* * * * *']},observability:{enabled:false}};
 const path=join(dir,'wrangler.json');writeFileSync(path,JSON.stringify(config),{mode:0o600});
 const r=spawnSync(process.execPath,['node_modules/wrangler/bin/wrangler.js','deploy','--config',path],{stdio:'ignore',env:process.env});
 if(r.error||r.status!==0)throw Error('Deployment failed. Review privately in Cloudflare; no credential-bearing logs are published.');
 console.log('Tested Worker source deployed. Listening PIN and publisher secrets were not modified.');
}finally{rmSync(dir,{recursive:true,force:true});}
