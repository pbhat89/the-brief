import {test} from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {JS} from '../src/app.js';
function harness(){
 const nodes=new Map();function node(selector){if(!nodes.has(selector))nodes.set(selector,{hidden:false,value:'',textContent:'',children:[],attributes:{},style:{setProperty(){}},setAttribute(k,v){this.attributes[k]=v},getAttribute(k){return this.attributes[k]||null},removeAttribute(k){delete this.attributes[k]},replaceChildren(){this.children=[]},append(x){this.children.push(x)},focus(){this.focused=true}});return nodes.get(selector);}
 const audio=node('audio');audio.paused=true;audio.pause=()=>{audio.paused=true;audio.onpause?.()};audio.load=()=>audio.loaded=true;
 let response={status:200,ok:true,json:async()=>({csrf:'synthetic',episodes:[]})};
 const context=vm.createContext({document:{querySelector:node,createElement:()=>node('created-'+Math.random()),body:{classList:{add(){},remove(){}}}},matchMedia:()=>({matches:true}),fetch:async()=>response,cancelAnimationFrame(){},requestAnimationFrame(){},Uint8Array,Error,Number,String});
 vm.runInContext(JS,context);
 return {node,audio,context,setResponse:r=>response=r,run:s=>vm.runInContext(s,context)};
}
const settle=()=>new Promise(r=>setImmediate(r));
function assertReset(h){assert.equal(h.node('#login').hidden,false);assert.equal(h.node('#player').hidden,true);assert.equal(h.audio.getAttribute('src'),null);assert.equal(h.audio.paused,true);assert.equal(h.audio.loaded,true);assert.equal(h.node('#pin').value,'');assert.equal(h.node('#seek').value,0);assert.equal(h.node('#episodes').children.length,0);assert.equal(h.node('#chapters').children.length,0);assert.equal(h.run('csrf'),undefined);}
async function unlocked(){const h=harness();await settle();h.audio.setAttribute('src','/api/media/synthetic');h.node('#pin').value='stale';h.node('#chapters').append({});h.node('#episodes').append({});return h;}
test('API 401 restores PIN form and clears private player state',async()=>{const h=await unlocked();h.setResponse({status:401,ok:false});await assert.rejects(h.run("api('/api/episodes')"));assertReset(h);assert.equal(h.node('#pin').focused,true)});
test('expired-session Lock player returns to login even when logout is 401',async()=>{const h=await unlocked();h.setResponse({status:401,ok:false});await h.node('#logout').onclick();assertReset(h)});
test('audio auth failure rechecks session and returns to login',async()=>{const h=await unlocked();h.setResponse({status:401,ok:false});await h.audio.onerror();assertReset(h)});
test('a non-auth audio failure preserves the unlocked player',async()=>{const h=await unlocked();await h.audio.onerror();assert.equal(h.node('#player').hidden,false);assert.match(h.node('#error').textContent,/Audio unavailable/)});
test('an in-flight episode load cannot reopen the player after reset',async()=>{const h=await unlocked();let finish;h.setResponse({status:200,ok:true,json:()=>new Promise(r=>finish=r)});const pending=h.run('load()');await settle();h.run('resetToLogin()');finish({episodes:[]});await assert.rejects(pending);assertReset(h)});
test('pause is synchronous and never requests the unreachable session endpoint',async()=>{const h=await unlocked();h.audio.paused=false;let requests=0;h.context.fetch=()=>{requests++;throw Error('Offline')};const pending=h.node('#play').onclick();assert.equal(h.audio.paused,true);assert.equal(requests,0);await pending;assert.equal(requests,0)});
test('resume and initial play start in the click gesture before any await',async()=>{const h=await unlocked();const calls=[];let resumed,played;h.context.AudioContext=class{createAnalyser(){return {fftSize:0,connect(){}}}createMediaElementSource(){return {connect(){}}}resume(){calls.push('resume');return new Promise(r=>resumed=r)}};h.audio.play=()=>{calls.push('play');return new Promise(r=>played=r)};h.context.fetch=()=>{throw Error('Playback must not wait on session fetch')};const pending=h.node('#play').onclick();assert.deepEqual(calls,['resume','play']);resumed();played();await pending;});
