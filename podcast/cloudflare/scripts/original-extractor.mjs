// Never execute upstream JavaScript. Read literal data only, then escape every value.
import {parse as parseJS} from 'acorn';
import {parse as parseHTML} from 'parse5';
const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const text=n=>n.nodeName==='#text'?n.value:(n.childNodes||[]).map(text).join('');
const find=(n,p)=>p(n)?n:(n.childNodes||[]).map(c=>find(c,p)).find(Boolean);
const attr=(n,k)=>n.attrs?.find(a=>a.name===k)?.value;
function literal(n){
 if(n?.type==='Literal'&&(n.value===null||['string','number','boolean'].includes(typeof n.value)))return n.value;
 if(n?.type==='ArrayExpression')return n.elements.map(literal);
 if(n?.type==='ObjectExpression')return Object.fromEntries(n.properties.map(p=>{if(p.type!=='Property'||p.kind!=='init'||p.method||p.computed||p.shorthand)throw Error('Nonliteral upstream property');const k=p.key.type==='Identifier'?p.key.name:literal(p.key);if(['__proto__','prototype','constructor'].includes(k))throw Error('Unsafe property');return [k,literal(p.value)];}));
 throw Error('Upstream data must contain only literals');
}
const href=s=>{try{const u=new URL(s);return u.protocol==='https:'&&!u.username&&!u.password?escape(u.href):null;}catch{return null;}};
export function extractOriginal(html,date){
 if(!/^\d{4}-\d{2}-\d{2}$/.test(date))throw Error('Invalid archive date');
 const dom=parseHTML(html),script=find(dom,n=>n.tagName==='script'&&text(n).includes('const SECTIONS'));
 if(!script)throw Error('Original archive template not recognized');
 const data={};
 for(const statement of parseJS(text(script),{ecmaVersion:'latest'}).body){if(statement.type==='VariableDeclaration')for(const d of statement.declarations)if(['SECTIONS','FUN_FACT','PUZZLE','WORD_PUZZLE'].includes(d.id.name))data[d.id.name]=literal(d.init);}
 if(!Array.isArray(data.SECTIONS)||!data.SECTIONS.length||data.SECTIONS.length>30)throw Error('Invalid original sections');
 const css=text(find(dom,n=>n.tagName==='style')||{});
 // CSS remains isolated and network-disabled; reject URLs/imports/HTML boundaries too.
 if(!css||/url\s*\(|image-set\s*\(|@import|expression\s*\(|<|\\/i.test(css))throw Error('Unsupported original CSS');
 const title=text(find(dom,n=>n.tagName==='title')||{});
 const sub=text(find(dom,n=>attr(n,'class')==='sub')||{});
 const metrics=text(find(dom,n=>attr(n,'class')==='metrics')||{});
 const sections=data.SECTIONS,ids=new Set();
 for(const s of sections){if(!/^[a-z0-9-]+$/.test(s.id)||ids.has(s.id)||!/^#[0-9a-f]{6}$/i.test(s.color))throw Error('Invalid section identity');ids.add(s.id);}
 const radio=sections.map((s,i)=>`<input class="section-radio" type="radio" name="section" id="select-${s.id}" aria-label="${escape(s.title)}"${i===0?' checked':''}>`).join('');
 const tabs=sections.map(s=>`<label class="tab" for="select-${s.id}">${escape(s.title)}</label>`).join('');
 const rules=sections.map(s=>`#select-${s.id}:checked~#content #sec-${s.id}{display:block}#select-${s.id}:checked~.tabs label[for="select-${s.id}"]{background:${s.color};border-color:${s.color};color:#0a0a0f}#select-${s.id}:focus-visible~.tabs label[for="select-${s.id}"]{outline:3px solid white;outline-offset:3px}`).join('');
 const item=it=>{const link=href(it.url);let h=`<div class="item"><div class="headline">${escape(it.headline)}</div><div class="summary">${escape(it.summary)}</div>`;if(it.source)h+=`<div class="source">— ${link?`<a href="${link}" target="_blank" rel="noopener noreferrer">${escape(it.source)} ↗</a>`:escape(it.source)} · ${escape(it.date)}</div>`;if(it.spectrum)h+=`<div class="spectrum">${['left','center','right'].map(k=>`<div class="spec-cell spec-${k}"><span class="spec-label">${k}</span><div class="txt">${escape(it.spectrum[k])}</div></div>`).join('')}</div>`;if(it.bias)h+=`<div class="bias-note"><b>◈ Bias Check</b>${escape(it.bias)}</div>`;return h+'</div>';};
 const content=sections.map(s=>{let body;if(s.custom==='fun'){body=`<div class="fun-box"><div class="fun-text">${escape(data.FUN_FACT?.text)}</div><div class="fun-tag">${escape(data.FUN_FACT?.tag)}</div></div>`;}else if(['puzzle','wpuzzle'].includes(s.custom)){const p=data[s.custom==='puzzle'?'PUZZLE':'WORD_PUZZLE']||{};body=`<div class="${s.custom==='puzzle'?'puzzle':'wpuzzle'}-box"><span class="${s.custom==='puzzle'?'ptype':'wptype'}">${escape(p.type)}</span><div class="puzzle-title">${escape(p.title)}</div><div class="puzzle-how">How to approach: ${escape(p.how)}</div><div class="puzzle-q">${escape(p.question)}</div><details><summary class="btn">Show answer</summary><div class="answer show">${escape(p.answer)}</div></details></div>`;}else{if(!Array.isArray(s.items))throw Error('Missing original items');body=s.items.map(item).join('');}return `<section class="sec" id="sec-${s.id}" aria-label="${escape(s.title)}"><h2 class="sec-title">${escape(s.title)}</h2><div class="rule" style="background:linear-gradient(90deg,${s.color},transparent)"></div>${body}</section>`;}).join('');
 return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(title)}</title><style>${css}\n.section-radio{position:absolute;width:1px;height:1px;opacity:0}.tabs{position:relative}.tab{display:inline-block}@media(max-width:600px){.tabs{flex-wrap:nowrap;overflow-x:auto;padding:4px 0 10px}.tab{flex-shrink:0}}.sec{display:none}h2{font-size:inherit}.original-note{font:13px/1.5 system-ui;color:#bdb9b0;margin:16px 0}a{overflow-wrap:anywhere}${rules}</style></head><body><main class="wrap"><div class="masthead"><div><div class="title">THE BRIEF</div><div class="sub">${escape(sub)}</div></div></div><div class="rule"></div><p class="original-note">Original upstream content. Corrections are in Verified companion.</p>${radio}<nav class="tabs" aria-label="Original brief sections">${tabs}</nav><div id="content">${content}</div><div class="rule"></div><div class="metrics">${escape(metrics)}</div></main></body></html>`;
}
