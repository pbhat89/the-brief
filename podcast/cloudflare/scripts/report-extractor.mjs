// Build-time HTML parsing only. Runtime receives safe structured text, never raw HTML.
import {parse} from 'parse5';
const skip=new Set(['script','style','nav','form','template','svg','math','iframe','object','embed']);
const normal=s=>s.replace(/\s+/g,' ').trim();
export function extractReport(html,base){
 const document=parse(html),blocks=[];
 const children=n=>(n.childNodes||[]).filter(c=>!skip.has(c.tagName));
 const text=n=>n.nodeName==='#text'?n.value:children(n).map(text).join(' ');
 const href=n=>{try{const raw=n.attrs?.find(a=>a.name==='href')?.value;if(!raw)return null;const u=new URL(raw,base);return u.protocol==='https:'&&!u.username&&!u.password?u.href:null;}catch{return null;}};
 function links(n){return [...(n.tagName==='a'&&href(n)?[href(n)]:[]),...children(n).flatMap(links)];}
 function descendants(n,tag){return children(n).flatMap(c=>c.tagName===tag?[c]:descendants(c,tag));}
 function visit(n){
  if(skip.has(n.tagName))return;
  if(n.tagName==='table'){
   const caption=normal(descendants(n,'caption').map(text).join(' '));
   const rows=descendants(n,'tr').map(tr=>children(tr).filter(c=>['td','th'].includes(c.tagName)).map(c=>({text:normal(text(c)),header:c.tagName==='th',links:links(c)}))).filter(r=>r.length);
   blocks.push({type:'table',text:caption,links:[],rows});return;
  }
  if(['h1','h2','h3','p','li','blockquote','small','a'].includes(n.tagName)){
   const value=normal(text(n));if(value)blocks.push({type:['small','a'].includes(n.tagName)?'p':n.tagName,text:value,links:links(n)});return;
  }
  for(const c of children(n))visit(c);
 }
 visit(document);return blocks;
}
