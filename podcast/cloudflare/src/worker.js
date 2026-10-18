import {TTL,MAX,digest,equal,pinHash,range,mp3} from './security.js';
import {HTML,JS,CSS} from './ui.js';
const headers={'Cache-Control':'private, no-store, max-age=0','Pragma':'no-cache','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Cross-Origin-Resource-Policy':'same-origin','Content-Security-Policy':"default-src 'none'; script-src 'self'; style-src 'self'; media-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"};
const reply=(body,status=200,extra={})=>new Response(body!==null&&typeof body==='object'&&!(body instanceof ArrayBuffer)?JSON.stringify(body):body,{status,headers:{...headers,'Content-Type':'application/json',...extra}});
const now=()=>Math.floor(Date.now()/1000);
export class Auth {
 constructor(ctx,env){this.ctx=ctx;this.env=env;}
 async fetch(req){
  const x=await req.json(),s=this.ctx.storage;
  if(x.op==='login'){
   if(!/^[a-f0-9]{64}$/.test(this.env.PIN_HASH||'')||!this.env.PIN_SALT)return reply('Setup required',503);
   // Serialize the read/increment across awaits; count attempts before expensive verification.
   const allowed=await s.transaction(async t=>{const a=await t.get('attempts')||{until:0,n:0};if(a.until<=now()){a.until=now()+900;a.n=0;}if(a.n>=10)return false;a.n++;await t.put('attempts',a);return true;});
   if(!allowed)return reply('Try later',429,{'Retry-After':'900'});
   if(!/^[0-9]{12,32}$/.test(x.pin||'')||!equal(await pinHash(x.pin,this.env.PIN_SALT),this.env.PIN_HASH))return reply('Invalid PIN',401);
   const token=crypto.randomUUID()+crypto.randomUUID(),csrf=crypto.randomUUID();const exp=now()+43200;
   await s.put('s:'+await digest(token),{csrf,exp,version:this.env.PIN_HASH});await s.setAlarm(Date.now()+3100000);
   return reply({token,csrf,exp});
  }
  const key='s:'+await digest(x.token||'');const session=await s.get(key);
  if(!session||session.exp<=now()||session.version!==this.env.PIN_HASH)return reply('Unauthorized',401);
  if(x.op==='logout'){await s.delete(key);return reply({ok:true});}
  return reply({csrf:session.csrf});
 }
 async alarm(){const entries=await this.ctx.storage.list({prefix:'s:'});for(const [k,v]of entries)if(v.exp<=now())await this.ctx.storage.delete(k);if(entries.size)await this.ctx.storage.setAlarm(Date.now()+3100000);}
}
export default {async fetch(req,env){try{return await handle(req,env);}catch{return reply('Service unavailable',503);}}};
async function handle(req,env){
 const u=new URL(req.url),p=u.pathname,method=req.method;
 if(u.protocol!=='https:'&&u.hostname!=='localhost'&&u.hostname!=='127.0.0.1')return reply('HTTPS required',400);
 const write=!['GET','HEAD'].includes(method);
 if(write&&(req.headers.get('Origin')!==u.origin||req.headers.get('Sec-Fetch-Site')==='cross-site'))return reply('Origin rejected',403);
 if(p==='/'&&method==='GET')return reply(HTML,200,{'Content-Type':'text/html; charset=utf-8'});
 if(p==='/app.js'&&method==='GET')return reply(JS,200,{'Content-Type':'text/javascript'});
 if(p==='/app.css'&&method==='GET')return reply(CSS,200,{'Content-Type':'text/css'});
 const auth=async x=>env.AUTH.get(env.AUTH.idFromName('shared-pin')).fetch(new Request('https://internal/',{method:'POST',body:JSON.stringify(x)}));
 if(p==='/api/login'&&method==='POST'){
  if(Number(req.headers.get('Content-Length')||0)>256)return reply('Too large',413);
  const text=await bounded(req,256);if(!text)return reply('Too large',413);
  let data;try{data=JSON.parse(new TextDecoder().decode(text));}catch{return reply('Bad request',400);}
  const r=await auth({op:'login',pin:data.pin});if(!r.ok)return reply('Login unavailable or invalid',r.status, r.status===429?{'Retry-After':'900'}:{});
  const s=await r.json();return reply({csrf:s.csrf},200,{'Set-Cookie':`__Host-brief=${s.token}; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=43200`});
 }
 if(p==='/api/upload'&&method==='POST')return upload(req,env);
 const cookie=req.headers.get('Cookie')||'',token=/(?:^|;\s*)__Host-brief=([^;]+)/.exec(cookie)?.[1];
 if(!token)return reply('Unauthorized',401);
 const r=await auth({op:'check',token});if(!r.ok)return reply('Unauthorized',401);const session=await r.json();
 if(write&&!equal(req.headers.get('X-CSRF-Token'),session.csrf))return reply('CSRF rejected',403);
 if(p==='/api/logout'&&method==='POST'){await auth({op:'logout',token});return reply({ok:true},200,{'Set-Cookie':'__Host-brief=; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=0'});}
 if(p==='/api/session'&&method==='GET')return reply(session);
 if(p==='/api/episodes'&&['GET','HEAD'].includes(method)){
  const list=await env.EPISODES.list({prefix:'meta:',limit:100});const episodes=[];for(const k of list.keys){const v=await env.EPISODES.get(k.name,'json');if(v&&v.expires>now())episodes.push(v);}
  return reply(method==='HEAD'?null:{episodes:episodes.sort((a,b)=>b.created-a.created)});
 }
 const match=/^\/api\/(media|episodes)\/([a-f0-9-]{36})$/.exec(p);
 if(match&&['GET','HEAD'].includes(method)){
  const meta=await env.EPISODES.get('meta:'+match[2],'json');if(!meta||meta.expires<=now())return reply('Not found',404);
  if(match[1]==='episodes')return reply(method==='HEAD'?null:meta);
  const bounds=range(req.headers.get('Range'),meta.size);if(!bounds)return reply(null,416,{'Content-Range':`bytes */${meta.size}`});
  const [a,b]=bounds,partial=!!req.headers.get('Range'),h={'Content-Type':'audio/mpeg','Accept-Ranges':'bytes','Content-Length':String(b-a+1),...(partial?{'Content-Range':`bytes ${a}-${b}/${meta.size}`}:{})};
  if(method==='HEAD')return reply(null,partial?206:200,h);
  const audio=await env.EPISODES.get('audio:'+match[2],'arrayBuffer');if(!audio||audio.byteLength!==meta.size)return reply('Not found',404);
  return reply(audio.slice(a,b+1),partial?206:200,h);
 }
 return reply('Not found',404);
}
async function bounded(req,max){const reader=req.body?.getReader();if(!reader)return null;let total=0;const chunks=[];for(;;){const {done,value}=await reader.read();if(done)break;total+=value.byteLength;if(total>max){await reader.cancel();return null;}chunks.push(value);}const out=new Uint8Array(total);let at=0;for(const c of chunks){out.set(c,at);at+=c.length;}return out;}
async function upload(req,env){
 if(!/^[a-f0-9]{64}$/.test(env.PUBLISHER_TOKEN_HASH||''))return reply('Publisher setup required',503);
 const bearer=/^Bearer ([A-Za-z0-9_-]{32,256})$/.exec(req.headers.get('Authorization')||'');
 if(!bearer||!equal(await digest(bearer[1]),env.PUBLISHER_TOKEN_HASH))return reply('Unauthorized',401);
 if(req.headers.get('X-Brief-Publish')!=='1')return reply('CSRF rejected',403);
 if(env.EXPIRY_APPROVED!=='true')return reply('Expiry activation requires owner approval',503);
 if(req.headers.get('Content-Type')!=='audio/mpeg')return reply('MP3 required',415);
 const length=Number(req.headers.get('Content-Length'));if(!Number.isInteger(length)||length<8||length>MAX)return reply('Invalid size',413);
 const bytes=await bounded(req,MAX);if(!bytes||bytes.length!==length||!mp3(bytes))return reply('Invalid MP3',415);
 const title=req.headers.get('X-Episode-Title')||'Daily brief';if(title.length>120||/[\x00-\x1f]/.test(title))return reply('Invalid title',400);
 const id=crypto.randomUUID(),created=now(),expires=created+TTL;
 let chapters=[];try{chapters=JSON.parse(req.headers.get('X-Episode-Chapters')||'[]');}catch{return reply('Invalid chapters',400);}
 if(!Array.isArray(chapters)||chapters.length>30||chapters.some(c=>!c||typeof c.title!=='string'||c.title.length>80||!Number.isFinite(c.start)||c.start<0))return reply('Invalid chapters',400);
 const meta={id,title,created,expires,size:bytes.length,chapters:chapters.map(c=>({title:c.title,start:c.start})).sort((a,b)=>a.start-b.start)};
 await env.EPISODES.put('audio:'+id,bytes.buffer,{expiration:expires});
 await env.EPISODES.put('meta:'+id,JSON.stringify(meta),{expiration:expires});
 return reply(meta,201);
}
