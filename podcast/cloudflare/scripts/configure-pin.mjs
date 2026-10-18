// Owner runs locally after approving configuration. Never accepts a PIN in argv or logs it.
import {randomBytes,webcrypto} from 'node:crypto';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {pinHash} from '../src/security.js';
globalThis.crypto ??= webcrypto;
const root=fileURLToPath(new URL('../',import.meta.url));
const cli=fileURLToPath(new URL('../node_modules/wrangler/bin/wrangler.js',import.meta.url));
const config=fileURLToPath(new URL('../wrangler.jsonc',import.meta.url));
async function wrangler(args,{piped=false,value}={}){
  await new Promise((resolve,reject)=>{
    const child=spawn(process.execPath,[cli,...args,'--config',config],{cwd:root,env:process.env,stdio:[piped?'pipe':'inherit','inherit','inherit']});
    if(piped){child.stdin.on('error',()=>{});child.stdin.end(value);}
    child.on('error',reject);
    child.on('exit',code=>code===0?resolve():reject(Error('Wrangler authentication/setup failed. No PIN was collected if this occurred during preflight. Reauthenticate in this same terminal with the approved scopes; do not create an API token merely because the noninteractive error suggests one.')));
  });
}
const checkOnly=process.argv.includes('--check-auth');
if(!checkOnly&&!process.stdin.isTTY)throw Error('Use an interactive terminal.');
// Unlike whoami, secret list exercises requireAuth. It reads names only, never values.
// First preserve the owner's terminal for OAuth recovery; then verify the exact
// piped-stdin mode used below, before asking for any PIN.
console.log('Checking protected Worker authentication (secret names only)...');
await wrangler(['secret','list']);
await wrangler(['secret','list'],{piped:true});
if(checkOnly){console.log('Protected authentication passed in both input modes. No secrets changed.');process.exit(0);}
async function hidden(label){process.stdout.write(label);process.stdin.setRawMode(true);process.stdin.resume();let input='';return new Promise((resolve,reject)=>{function data(buf){for(const c of buf.toString()){if(c==='\u0003'){cleanup();reject(Error('Cancelled'));return;}if(c==='\r'||c==='\n'){cleanup();resolve(input);return;}if(c==='\u007f'||c==='\b')input=input.slice(0,-1);else if(/[0-9]/.test(c)&&input.length<32)input+=c;}}function cleanup(){process.stdin.off('data',data);process.stdin.setRawMode(false);process.stdin.pause();process.stdout.write('\n');}process.stdin.on('data',data);});}
let pin=await hidden('Enter a new 12-32 digit listening PIN (hidden): ');
if(!/^[0-9]{12,32}$/.test(pin))throw Error('Use 12-32 digits.');
if(pin!==await hidden('Confirm listening PIN (hidden): '))throw Error('PINs differ.');
const salt=randomBytes(32).toString('hex'),hash=await pinHash(pin,salt);pin='';
// Invoke Wrangler directly, avoiding shell interpolation and secrets in command arguments.
async function put(name,value){await wrangler(['secret','put',name],{piped:true,value});}
await put('PIN_SALT',salt);await put('PIN_HASH',hash);
console.log('PIN verifier configured. Existing sessions are invalidated by a PIN change.');
