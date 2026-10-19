// Run the exact served browser bundle without any real session, network or data.
import vm from 'node:vm';
import assert from 'node:assert/strict';
export function verifyBrowserScript(script){
 const nodes=new Map();
 function node(selector){if(!nodes.has(selector))nodes.set(selector,{hidden:false,value:'',textContent:'',children:[],attributes:{},style:{setProperty(){}},setAttribute(k,v){this.attributes[k]=v;},getAttribute(k){return this.attributes[k]||null;},removeAttribute(k){delete this.attributes[k];},replaceChildren(){this.children=[];},append(x){this.children.push(x);},focus(){}});return nodes.get(selector);}
 const audio=node('audio');audio.paused=true;audio.pause=()=>{};audio.load=()=>{};
 const context=vm.createContext({document:{querySelector:node,createElement:()=>node('created-'+Math.random()),body:{classList:{add(){},remove(){}}}},matchMedia:()=>({matches:true}),fetch:()=>new Promise(()=>{}),cancelAnimationFrame(){},requestAnimationFrame(){},setTimeout(){},Uint8Array,URL});
 vm.runInContext(script,context,{timeout:2000});
 assert.equal(vm.runInContext("LogbookModel.singaporeDate(new Date('2026-10-18T16:00:00Z'))",context),'2026-10-19');
 assert.equal(vm.runInContext("LogbookModel.habitsFor('2026-10-18').length",context),4);
 assert.equal(typeof node('#tab-logbook').onclick,'function');
 assert.equal(typeof node('#logbook-load').onclick,'function');
}
