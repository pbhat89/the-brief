import {REPORTS} from './reports.js';
export const JS='const REPORTS='+JSON.stringify(REPORTS)+';\n'+String.raw`
const $=s=>document.querySelector(s),audio=$('audio');
let csrf,context,analyser,frame,epoch=0;
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
function resetToLogin(message='Please unlock the player.') {
 epoch++; csrf=undefined; resetBranding(); document.body.classList.remove('unlocked'); document.body.classList.remove('reader');
 audio.pause(); audio.removeAttribute('src'); audio.load(); audio.playbackRate=1;
 cancelAnimationFrame(frame); document.body.classList.remove('playing');
 $('#orb').style.setProperty('--energy',1);
 $('#episodes').replaceChildren(); $('#chapters').replaceChildren();
 $('#previous-audio').replaceChildren(); $('#reports').replaceChildren(); $('#reader-content').replaceChildren();
 $('#viewer').hidden=true; $('#archive-list').hidden=false; showTab('latest');
 $('#episode-date').textContent='YOUR NEXT MOMENT OF CLARITY';
 $('#title').textContent='Ready to listen'; $('#status').textContent='Select an episode below';
 $('#elapsed').textContent='0:00'; $('#duration').textContent='0:00'; $('#seek').value=0; $('#speed').value='1';
 $('#play').textContent='▶'; $('#play').setAttribute('aria-label','Play');
 $('#pin').value=''; $('#player').hidden=true; $('#login').hidden=false;
 $('#error').textContent=message; $('#pin').focus();
 setControls(false);
}
async function api(url,options={}) {
 const generation=epoch;
 const r=await fetch(url,{...options,cache:'no-store'});
 if(generation!==epoch)throw Error('Session changed. Please unlock again.');
 if(r.status===401){resetToLogin();throw Error('Please unlock the player.');}
 if(!r.ok)throw Error(r.status===429?'Too many attempts. Try again in 15 minutes.':'Request failed ('+r.status+').');
 const data=await r.json();
 if(generation!==epoch)throw Error('Session changed. Please unlock again.');
 return data;
}
function error(e){$('#error').textContent=e.message;}
function time(t){return Number.isFinite(t)?Math.floor(t/60)+':'+String(Math.floor(t%60)).padStart(2,'0'):'0:00';}
function date(t){const d=new Date(t);return Number.isFinite(d.getTime())?d.toLocaleDateString('en-GB',{day:'numeric',month:'long',year:'numeric'}):'Written edition';}
function resetBranding(){document.title='The Brief · Your daily perspective';$('#brand-label').textContent='the brief';$('#brand-dot').hidden=false;$('#brand-link').setAttribute('aria-label','The Brief home');$('#hero-line-one').textContent='Make sense of';$('#hero-line-two').textContent='what matters.';$('#hero-intro').textContent='Your world, thoughtfully distilled. Listen, catch up, and carry on.';}
function applyPersonalization(value){const p=value&&typeof value==='object'?value:{};const clean=(x,max)=>typeof x==='string'?x.replace(/[\x00-\x1f\x7f]/g,'').trim().slice(0,max):'';const brand=clean(p.brand,80),greeting=clean(p.greeting,180);$('#brand-label').textContent=brand||'the brief';$('#brand-dot').hidden=!!brand;$('#brand-link').setAttribute('aria-label',brand?brand+' home':'The Brief home');document.title=brand?brand+' · Listen':'The Brief · Listen';$('#hero-line-one').textContent='A little perspective,';$('#hero-line-two').textContent='just for you.';$('#hero-intro').textContent=greeting||'A small pause, a clearer view. Welcome back.';}
// The first title segment is the editorial title. Technical annotations belong to metadata, not the heading.
function episodeTitle(episode){return typeof episode.title==='string'&&episode.title.trim()?episode.title.split('·')[0].trim():'Daily brief';}
function setControls(ready){for(const s of ['#play','#back','#forward','#seek','#speed'])$(s).disabled=!ready;}
function showTab(name){document.body.classList[name==='previous'?'add':'remove']('archive');for(const n of ['latest','previous']){$('#'+n).hidden=n!==name;$('#tab-'+n).setAttribute('aria-selected',String(n===name));$('#tab-'+n).setAttribute('tabindex',n===name?'0':'-1');}}
for(const name of ['latest','previous']){$('#tab-'+name).onclick=()=>showTab(name);$('#tab-'+name).onkeydown=e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();const next=e.key==='Home'?'latest':e.key==='End'?'previous':name==='latest'?'previous':'latest';showTab(next);$('#tab-'+next).focus();}};}
function card(title,meta,icon,action){const b=document.createElement('button');b.className='edition-card';const badge=document.createElement('span');badge.className='card-icon';badge.textContent=icon;badge.setAttribute('aria-hidden','true');const body=document.createElement('span');body.className='card-body';const name=document.createElement('span');name.className='card-title';name.textContent=title;const detail=document.createElement('span');detail.className='card-meta';detail.textContent=meta;const arrow=document.createElement('span');arrow.className='card-arrow';arrow.textContent='↗';arrow.setAttribute('aria-hidden','true');body.append(name);body.append(detail);b.append(badge);b.append(body);b.append(arrow);b.onclick=action;return b;}
function chooseEpisode(e){audio.pause();audio.src='/api/media/'+encodeURIComponent(e.id);$('#title').textContent=episodeTitle(e);$('#episode-date').textContent=date(e.created*1000).toUpperCase();$('#status').textContent='Ready when you are';$('#seek').value=0;$('#elapsed').textContent='0:00';$('#duration').textContent='0:00';$('#chapters').replaceChildren();setControls(true);for(const c of e.chapters||[]){const b=document.createElement('button');b.textContent=c.title;b.onclick=()=>audio.currentTime=c.start;$('#chapters').append(b);}showTab('latest');}
function safeURL(value){try{const u=new URL(value);return u.protocol==='https:'&&!u.username&&!u.password?u.href:null;}catch{return null;}}
function appendLinks(parent,urls){const links=document.createElement('div');links.className='source-links';for(const raw of urls||[]){const href=safeURL(raw);if(!href)continue;const a=document.createElement('a');a.href=href;a.target='_blank';a.rel='noopener noreferrer';a.textContent=new URL(href).hostname.replace(/^www\./,'');links.append(a);}if((urls||[]).length)parent.append(links);}
function renderBlock(parent,block){
 if(block.type==='h1')return;
 if(block.type==='table'){
  const wrap=document.createElement('div');wrap.className='reader-table-wrap';wrap.setAttribute('role','region');wrap.setAttribute('aria-label',block.text||'Report data table');wrap.setAttribute('tabindex','0');const table=document.createElement('table');
  if(block.text){const caption=document.createElement('caption');caption.textContent=block.text;table.append(caption);}
  const body=document.createElement('tbody');for(const row of block.rows||[]){const tr=document.createElement('tr');for(const cell of row){const td=document.createElement(cell.header?'th':'td');if(cell.header)td.setAttribute('scope','col');td.textContent=cell.text;appendLinks(td,cell.links);tr.append(td);}body.append(tr);}table.append(body);wrap.append(table);parent.append(wrap);return;
 }
 const tag=['h2','h3','p','li','blockquote'].includes(block.type)?block.type:'p';const p=document.createElement(tag==='li'?'p':tag);p.textContent=block.text;parent.append(p);appendLinks(parent,block.links);
}
function openReport(report){document.body.classList.add('reader');$('#archive-list').hidden=true;$('#viewer').hidden=false;$('#viewer-title').textContent=report.title;$('#viewer-date').textContent=date(report.published_at);$('#reader-content').replaceChildren();for(const block of report.blocks)renderBlock($('#reader-content'),block);const source=safeURL(report.source);$('#reader-source').href=source||'';$('#reader-source').hidden=!source;$('#viewer-title').focus();}
$('#reader-back').onclick=()=>{document.body.classList.remove('reader');$('#viewer').hidden=true;$('#archive-list').hidden=false;$('#reader-content').replaceChildren();$('#tab-previous').focus();};
function renderReports(){$('#reports').replaceChildren();for(const r of REPORTS)$('#reports').append(card(r.title,date(r.published_at)+' · Read edition','≡',()=>openReport(r)));}
async function load(personalization={}){
 const data=await api('/api/episodes'); document.body.classList.add('unlocked'); applyPersonalization(personalization); $('#login').hidden=true; $('#player').hidden=false; $('#episodes').replaceChildren();
 $('#previous-audio').replaceChildren();renderReports();
 const episodes=data.episodes.filter(e=>e.expires>Date.now()/1000).sort((a,b)=>b.created-a.created).slice(0,20);
 for(const e of episodes){const label=date(e.created*1000)+' · Audio available until '+date(e.expires*1000);$('#episodes').append(card(episodeTitle(e),label,'♪',()=>chooseEpisode(e)));$('#previous-audio').append(card(episodeTitle(e),label,'♪',()=>chooseEpisode(e)));}
 if(episodes.length){chooseEpisode(episodes[0]);}else{
  setControls(false);$('#status').textContent='No recordings available yet. The reading room is open.';
  const empty=document.createElement('div');empty.className='empty-state';const text=document.createElement('p');text.textContent='Your next recording will appear here.';const browse=document.createElement('button');browse.textContent='Explore previous editions ↗';browse.onclick=()=>showTab('previous');empty.append(text);empty.append(browse);$('#episodes').append(empty);
  const note=document.createElement('div');note.className='empty-state';note.textContent='No recordings from the last seven days. Written editions are available below.';$('#previous-audio').append(note);
 }
}
$('form').onsubmit=async e=>{e.preventDefault();try{
 const pin=$('#pin').value;$('#pin').value='';
 ({csrf}=await api('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pin})}));
 $('#error').textContent='';const session=await api('/api/session');csrf=session.csrf;await load(session.personalization);
}catch(e){error(e);}};
function animate(){if(!analyser||audio.paused||reduced.matches)return;const bins=new Uint8Array(analyser.frequencyBinCount);analyser.getByteFrequencyData(bins);const power=bins.reduce((a,b)=>a+b,0)/bins.length/255;$('#orb').style.setProperty('--energy',1+power*.35);frame=requestAnimationFrame(animate);}
$('#play').onclick=async()=>{try{
 if(!audio.paused){audio.pause();return;}
 if(!audio.getAttribute('src'))return;
 if(!context){context=new AudioContext();analyser=context.createAnalyser();analyser.fftSize=128;context.createMediaElementSource(audio).connect(analyser);analyser.connect(context.destination);}
 // Start both calls within the user gesture; the media endpoint enforces auth.
 const resumed=context.resume(),played=audio.play();
 await Promise.all([resumed,played]);
}catch(e){error(e);}};
audio.onplay=()=>{document.body.classList.add('playing');$('#play').textContent='Ⅱ';$('#play').setAttribute('aria-label','Pause');$('#status').textContent='Now playing';animate();};
audio.onpause=()=>{document.body.classList.remove('playing');cancelAnimationFrame(frame);$('#orb').style.setProperty('--energy',1);$('#play').textContent='▶';$('#play').setAttribute('aria-label','Play');$('#status').textContent='Paused';};
audio.onended=audio.onpause;
// Media elements do not expose HTTP status. Recheck the session on a media failure.
audio.onerror=async()=>{
 if(!audio.getAttribute('src'))return;
 try{await api('/api/session');error(Error('Audio unavailable. Choose another episode.'));}catch(e){error(e);}
};
audio.ontimeupdate=()=>{$('#elapsed').textContent=time(audio.currentTime);$('#duration').textContent=time(audio.duration);$('#seek').value=audio.duration?audio.currentTime/audio.duration*1000:0;};
$('#seek').oninput=e=>{if(Number.isFinite(audio.duration))audio.currentTime=+e.target.value/1000*audio.duration;};
$('#back').onclick=()=>audio.currentTime=Math.max(0,audio.currentTime-15);
$('#forward').onclick=()=>{if(Number.isFinite(audio.duration))audio.currentTime=Math.min(audio.duration,audio.currentTime+15);};
$('#speed').onchange=e=>audio.playbackRate=+e.target.value;
$('#logout').onclick=async()=>{try{
 await api('/api/logout',{method:'POST',headers:{'X-CSRF-Token':csrf}});resetToLogin('Player locked.');
}catch(e){resetToLogin(e.message);}};
api('/api/session').then(s=>{csrf=s.csrf;return load(s.personalization);}).catch(()=>{});
`;
