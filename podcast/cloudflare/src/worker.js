import {ORIGINAL_FONT_CSS} from './original-fonts.js';
import {ORIGINALS} from './originals.js';
import {TTL,MAX,digest,equal,pinHash,range,mp3} from './security.js';
import {HTML,JS,CSS} from './ui.js';
import {LogbookModel as logbook} from './logbook-model.js';
const headers={'Cache-Control':'private, no-store, max-age=0','Pragma':'no-cache','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Cross-Origin-Resource-Policy':'same-origin','Content-Security-Policy':"default-src 'none'; script-src 'self'; style-src 'self'; media-src 'self'; connect-src 'self'; frame-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"};
const reply=(body,status=200,extra={})=>new Response(body!==null&&typeof body==='object'&&!(body instanceof ArrayBuffer)?JSON.stringify(body):body,{status,headers:{...headers,'Content-Type':'application/json',...extra}});
const now=()=>Math.floor(Date.now()/1000);
const collectionOf=meta=>meta.collection==='personal'?'personal':'daily';
const indexPrefix=collection=>collection==='personal'?'active-personal:':'active:';
const logbookConfigKey='logbook:v1:config',logbookDayKey=date=>'logbook:v1:day:'+date;
const object=value=>value!==null&&typeof value==='object'&&!Array.isArray(value);
function logbookPayload(date,value){
 if(!object(value)||Object.keys(value).length!==3||!Number.isSafeInteger(value.version)||value.version<0||!object(value.habits)||!Array.isArray(value.fitnessActivities))return null;
 const keys=logbook.habitsFor(date).map(h=>h.id),activities=value.fitnessActivities;
 if(Object.keys(value.habits).length!==keys.length||!keys.every(key=>Object.hasOwn(value.habits,key)&&typeof value.habits[key]==='boolean')||activities.length>4||new Set(activities).size!==activities.length||activities.some(activity=>!logbook.activityOptions.includes(activity))||(!value.habits.fitness&&activities.length))return null;
 // Stable ordering makes semantically identical retries match, regardless of JSON key order.
 return {version:value.version,habits:Object.fromEntries(keys.map(key=>[key,value.habits[key]])),fitnessActivities:logbook.activityOptions.filter(activity=>activities.includes(activity))};
}
async function logbookOperation(x,storage,env,sessionKey){
 return storage.transaction(async t=>{
  // Check again inside the same serialized transaction as the private record access.
  const session=await t.get(sessionKey);
  if(!session||session.exp<=now()||session.version!==env.PIN_HASH)return reply('Unauthorized',401);
  if(x.op==='logbook:put'&&!equal(x.csrf,session.csrf))return reply('CSRF rejected',403);
  const timestamp=Date.now(),today=logbook.singaporeDate(new Date(timestamp));
  const weekStart=x.week===null||x.week===undefined?logbook.monday(today):x.week;
  if(x.op==='logbook:get'&&(!logbook.validDate(weekStart)||logbook.weekday(weekStart)!==1))return reply('Invalid week',400);
  let payload;
  if(x.op==='logbook:put'){
   if(!logbook.validDate(x.date))return reply('Invalid date',400);
   payload=logbookPayload(x.date,x.data);if(!payload)return reply('Invalid log book entry',400);
  }
  let config=await t.get(logbookConfigKey);
  if(!config){
   if(x.op!=='logbook:get')return reply({error:'Open Log book before saving a day',currentRecord:null},409);
   // First use starts tracking; reading never invents or finalizes a day's habits.
   config={schemaVersion:1,timeZone:logbook.timeZone,startDate:today};await t.put(logbookConfigKey,config);
  }
  if(config.schemaVersion!==1||config.timeZone!==logbook.timeZone||!logbook.validDate(config.startDate)||config.startDate>today)return reply('Log book unavailable',503);
  if(x.op==='logbook:get'){
   const dates=new Set();
   for(let offset=0;offset<7;offset++)dates.add(logbook.addDays(weekStart,offset));
   for(let offset=0;offset<=5;offset++)dates.add(logbook.addDays(today,-offset));
   const records=[];
   for(const date of [...dates].sort()){
    if(date<config.startDate||date>today)continue;
    const record=await t.get(logbookDayKey(date));
    if(record){if(!logbook.validRecord(record)||record.date!==date)return reply('Log book unavailable',503);records.push(record);}
   }
   const completed=new Set(records.map(record=>record.date)),pendingDates=[];
   for(let offset=0;offset<=5;offset++){const date=logbook.addDays(today,-offset);if(date>=config.startDate&&!completed.has(date))pendingDates.push(date);}
   return reply({schemaVersion:1,timeZone:logbook.timeZone,today,startDate:config.startDate,weekStart,records,pendingDates});
  }
  const currentRecord=await t.get(logbookDayKey(x.date));
  if(currentRecord){
   if(!logbook.validRecord(currentRecord)||currentRecord.date!==x.date)return reply('Log book unavailable',503);
   const same=Object.keys(payload.habits).every(key=>payload.habits[key]===currentRecord.habits[key])&&JSON.stringify(payload.fitnessActivities)===JSON.stringify(currentRecord.fitnessActivities);
   // A lost response can be retried even after the five-day entry window closes.
   if(same&&payload.version<=currentRecord.version)return reply({record:currentRecord});
   return reply({error:'This day has already been completed',currentRecord},409);
  }
  if(x.date<config.startDate||x.date>today||x.date<logbook.addDays(today,-5))return reply('Date is outside the log book entry window',400);
  if(payload.version!==0)return reply({error:'This day has changed; reload Log book',currentRecord:null},409);
  const record={date:x.date,version:1,status:'completed',habits:payload.habits,fitnessActivities:payload.fitnessActivities,savedAt:new Date(timestamp).toISOString()};
  // No expiration: habit records are separate from the disposable audio and session data.
  await t.put(logbookDayKey(x.date),record);
  return reply({record});
 });
}
async function activeEpisodes(env,collection='all'){
 const episodes=[];let complete=true;
 for(const kind of collection==='all'?['daily','personal']:[collection]){
  const list=await env.EPISODES.list({prefix:indexPrefix(kind),limit:100});
  if(list.list_complete===false)complete=false;
  for(const k of list.keys){const v=await env.EPISODES.get('meta:'+k.name.slice(indexPrefix(kind).length),'json');if(v&&!v.deleted&&Number.isFinite(v.expires)&&v.expires>now()&&collectionOf(v)===kind)episodes.push({...v,collection:kind});}
 }
 return {episodes:episodes.sort((a,b)=>b.created-a.created),complete};
}
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
  const key='s:'+await digest(x.token||'');
  if(x.op==='logbook:get'||x.op==='logbook:put')return logbookOperation(x,s,this.env,key);
  const session=await s.get(key);
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
 // Public, build-time escaped archive snapshots. No private/session data is exposed here.
 const originalId=/^\/originals\/(\d{4}-\d{2}-\d{2})\.html$/.exec(p)?.[1];
 if(originalId&&method==='GET')return Object.hasOwn(ORIGINALS,originalId)?reply(ORIGINALS[originalId].replace('</head>','<style>'+ORIGINAL_FONT_CSS+'</style></head>'),200,{'Content-Type':'text/html; charset=utf-8','Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; font-src data:; base-uri 'none'; form-action 'none'; frame-ancestors 'self'; sandbox allow-popups allow-popups-to-escape-sandbox"}):reply('Original edition unavailable',404);
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
 if(p==='/api/session'&&method==='GET')return reply({...session,personalization:{brand:String(env.PLAYER_BRAND||'').replace(/[\x00-\x1f]/g,'').slice(0,80),greeting:String(env.PLAYER_GREETING||'').replace(/[\x00-\x1f]/g,'').slice(0,160)}});
 if(p==='/api/logbook'&&method==='GET'){
  if(req.headers.get('Sec-Fetch-Site')==='cross-site'||(req.headers.has('Origin')&&req.headers.get('Origin')!==u.origin))return reply('Origin rejected',403);
  if(u.searchParams.getAll('week').length>1)return reply('Invalid week',400);
  return auth({op:'logbook:get',token,week:u.searchParams.get('week')});
 }
 const logbookMatch=/^\/api\/logbook\/([^/]+)$/.exec(p);
 if(logbookMatch&&method==='PUT'){
  if((req.headers.get('Content-Type')||'').split(';')[0].trim().toLowerCase()!=='application/json')return reply('JSON required',415);
  if(Number(req.headers.get('Content-Length')||0)>2048)return reply('Too large',413);
  const text=await bounded(req,2048);if(!text)return reply('Too large',413);
  let data;try{data=JSON.parse(new TextDecoder().decode(text));}catch{return reply('Bad request',400);}
  return auth({op:'logbook:put',token,csrf:req.headers.get('X-CSRF-Token'),date:logbookMatch[1],data});
 }
 if(p==='/api/episodes'&&['GET','HEAD'].includes(method)){
  const collection=u.searchParams.get('collection')||'daily';
  if(!['daily','personal','all'].includes(collection))return reply('Invalid collection',400);
  const {episodes}=await activeEpisodes(env,collection);
  return reply(method==='HEAD'?null:{episodes});
 }
 if(p==='/api/storage'&&method==='GET'){
  const {episodes,complete}=await activeEpisodes(env);
  return reply({activeAudioBytes:episodes.reduce((n,e)=>n+(Number.isFinite(e.size)?e.size:0),0),activeEpisodes:episodes.length,complete,freeStorageBytes:1000000000,estimateOnly:true});
 }
 const match=/^\/api\/(media|episodes)\/([a-f0-9-]{36})$/.exec(p);
 if(match&&match[1]==='episodes'&&method==='DELETE'){
  if(req.headers.get('X-Brief-Delete')!==match[2])return reply('Deletion confirmation required',400);
  const key='meta:'+match[2],meta=await env.EPISODES.get(key,'json');
  if(!meta)return reply('Not found',404);
  if(collectionOf(meta)!=='personal')return reply('Only personal podcasts can be deleted here',400);
  // Tombstone first: failed cleanup remains non-playable and can safely be retried.
  const tombstone={...meta,deleted:meta.deleted||now()};
  if(!meta.deleted)await env.EPISODES.put(key,JSON.stringify(tombstone));
  await env.EPISODES.delete('audio:'+match[2]);
  await env.EPISODES.delete(indexPrefix(collectionOf(meta))+match[2]);
  return reply({id:match[2],deleted:true});
 }
 if(match&&['GET','HEAD'].includes(method)){
  const meta=await env.EPISODES.get('meta:'+match[2],'json');if(!meta||meta.deleted||!Number.isFinite(meta.expires)||meta.expires<=now()||!Number.isSafeInteger(meta.size)||meta.size<1||meta.size>MAX)return reply('Not found',404);
  if(match[1]==='episodes')return reply(method==='HEAD'?null:{...meta,collection:collectionOf(meta)});
  const requestedRange=method==='GET'?req.headers.get('Range'):null;
  const bounds=range(requestedRange,meta.size);if(!bounds)return reply(null,416,{'Content-Range':`bytes */${meta.size}`});
  const [a,b]=bounds,partial=!!requestedRange,h={'Content-Type':'audio/mpeg','Accept-Ranges':'bytes','Content-Length':String(b-a+1),...(partial?{'Content-Range':`bytes ${a}-${b}/${meta.size}`}:{})};
  if(method==='HEAD')return reply(null,partial?206:200,h);
  const audio=await env.EPISODES.get('audio:'+match[2],'arrayBuffer');if(!audio||audio.byteLength!==meta.size)return reply('Not found',404);
  return reply(partial?audio.slice(a,b+1):audio,partial?206:200,h);
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
 const collection=req.headers.get('X-Episode-Collection')||'daily';
 if(!['daily','personal'].includes(collection))return reply('Invalid collection',400);
 const episodeKey=req.headers.get('X-Episode-Key');
 if(collection==='personal'&&(!episodeKey||!/^[a-z0-9][a-z0-9-]{0,79}$/.test(episodeKey)))return reply('Invalid episode key',400);
 if(collection==='daily'&&episodeKey!==null)return reply('Episode key is for personal podcasts',400);
 const rawDuration=req.headers.get('X-Episode-Duration'),duration=rawDuration===null?undefined:Number(rawDuration);
 if(rawDuration!==null&&(!rawDuration.trim()||!Number.isFinite(duration)||duration<=0||duration>86400))return reply('Invalid duration',400);
 const title=req.headers.get('X-Episode-Title')||(collection==='personal'?'Personal podcast':'Daily brief');if(title.length>120||/[\x00-\x1f]/.test(title))return reply('Invalid title',400);
 const id=crypto.randomUUID(),created=now(),expires=created+TTL;
 let chapters=[];try{chapters=JSON.parse(req.headers.get('X-Episode-Chapters')||'[]');}catch{return reply('Invalid chapters',400);}
 if(!Array.isArray(chapters)||chapters.length>30||chapters.some(c=>!c||typeof c.title!=='string'||c.title.length>80||!Number.isFinite(c.start)||c.start<0))return reply('Invalid chapters',400);
 const meta={id,title,collection,...(episodeKey?{episodeKey}:{}),...(duration===undefined?{}:{duration}),created,expires,size:bytes.length,chapters:chapters.map(c=>({title:c.title,start:c.start})).sort((a,b)=>a.start-b.start)};
 await env.EPISODES.put('audio:'+id,bytes.buffer,{expiration:expires});
 // Retain private playback metadata independently of expiring audio bytes.
 await env.EPISODES.put('meta:'+id,JSON.stringify(meta));
 // The disposable listing index prevents retained history crowding out current audio.
 await env.EPISODES.put(indexPrefix(collection)+id,JSON.stringify(meta),{expiration:expires});
 return reply(meta,201);
}

