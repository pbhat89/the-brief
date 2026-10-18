// Owner runs locally after approving configuration. Never accepts a PIN in argv or logs it.
import {randomBytes,webcrypto} from 'node:crypto';
import {spawn} from 'node:child_process';
import {pinHash} from '../src/security.js';
globalThis.crypto ??= webcrypto;
if(!process.stdin.isTTY)throw Error('Use an interactive terminal.');
async function hidden(label){process.stdout.write(label);process.stdin.setRawMode(true);process.stdin.resume();let input='';return new Promise((resolve,reject)=>{function data(buf){for(const c of buf.toString()){if(c==='\u0003'){cleanup();reject(Error('Cancelled'));return;}if(c==='\r'||c==='\n'){cleanup();resolve(input);return;}if(c==='\u007f'||c==='\b')input=input.slice(0,-1);else if(/[0-9]/.test(c)&&input.length<32)input+=c;}}function cleanup(){process.stdin.off('data',data);process.stdin.setRawMode(false);process.stdin.pause();process.stdout.write('\n');}process.stdin.on('data',data);});}
let pin=await hidden('Enter a new 12–32 digit listening PIN (hidden): ');
if(!/^[0-9]{12,32}$/.test(pin))throw Error('Use 12–32 digits.');
if(pin!==await hidden('Confirm listening PIN (hidden): '))throw Error('PINs differ.');
const salt=randomBytes(32).toString('hex'),hash=await pinHash(pin,salt);pin='';
// Invoke Wrangler directly, avoiding shell interpolation and secrets in command arguments.
async function put(name,value){await new Promise((resolve,reject)=>{const child=spawn(process.execPath,['node_modules/wrangler/bin/wrangler.js','secret','put',name],{stdio:['pipe','inherit','inherit']});child.stdin.end(value);child.on('error',reject);child.on('exit',code=>code===0?resolve():reject(Error('Wrangler failed: '+name)));});}
await put('PIN_SALT',salt);await put('PIN_HASH',hash);
console.log('PIN verifier configured. Existing sessions are invalidated by a PIN change.');
