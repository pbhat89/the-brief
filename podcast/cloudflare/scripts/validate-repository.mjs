import {readFileSync,readdirSync} from 'node:fs';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {join} from 'node:path';
const root=fileURLToPath(new URL('../../../',import.meta.url));
const read=p=>readFileSync(join(root,p),'utf8');
for(const p of ['podcast/evidence.schema.json','podcast/ledger.example.json','podcast/reports.json','podcast/status.json'])assert.ok(JSON.parse(read(p)));
for(const p of ['routine-prompt.md','podcast/README.md','podcast/IMPROVEMENTS.md','podcast/RUN_FEEDBACK.md'])assert.ok(read(p).trim().length>100,'Required operational document is empty: '+p);
const config=JSON.parse(read('podcast/cloudflare/wrangler.jsonc'));
assert.equal(config.observability.enabled,false);assert.equal(config.preview_urls,false);
assert.equal(config.vars.EXPIRY_APPROVED,'false','Public example must remain opt-in.');
assert.equal(config.kv_namespaces[0].id,'REPLACE_WITH_NEW_PRIVATE_KV_NAMESPACE_ID');
assert.ok(!('account_id' in config),'Account configuration belongs in protected deployment secrets.');
function scan(dir){for(const item of readdirSync(join(root,dir),{withFileTypes:true})){if(['node_modules','.wrangler','.git'].includes(item.name))continue;const p=join(dir,item.name);if(item.isDirectory())scan(p);else{assert.ok(!/\.(mp3|wav|m4a|ogg|pem|key)$/i.test(p),'Private media/key material must not enter source.');if(/\.(js|mjs|json|jsonc|md|html|yml)$/.test(p)){const text=read(p);assert.ok(!/-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/.test(text),'Private key detected.');assert.ok(!/https:\/\/[^\s"'<>]+\.workers\.dev/.test(text),'Private listener URL must stay out of source.');}}}}
scan('podcast/cloudflare');
console.log('Repository contracts, operational documents, example config and scoped privacy guards passed. Feedback remains data; semantic truth and permissions require review.');
