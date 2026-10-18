export const JS=String.raw`
const $=s=>document.querySelector(s),audio=$('audio');
let csrf,context,analyser,frame,epoch=0;
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
function resetToLogin(message='Please unlock the player.') {
 epoch++; csrf=undefined;
 audio.pause(); audio.removeAttribute('src'); audio.load(); audio.playbackRate=1;
 cancelAnimationFrame(frame); document.body.classList.remove('playing');
 $('#orb').style.setProperty('--energy',1);
 $('#episodes').replaceChildren(); $('#chapters').replaceChildren();
 $('#title').textContent='Ready to listen'; $('#status').textContent='Select an episode below';
 $('#elapsed').textContent='0:00'; $('#duration').textContent='0:00'; $('#seek').value=0; $('#speed').value='1';
 $('#play').textContent='▶'; $('#play').setAttribute('aria-label','Play');
 $('#pin').value=''; $('#player').hidden=true; $('#login').hidden=false;
 $('#error').textContent=message; $('#pin').focus();
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
async function load(){
 const data=await api('/api/episodes'); $('#login').hidden=true; $('#player').hidden=false; $('#episodes').replaceChildren();
 for(const e of data.episodes){
  const b=document.createElement('button');b.textContent=e.title;
  b.onclick=()=>{audio.src='/api/media/'+e.id;$('#title').textContent=e.title;$('#status').textContent='Ready when you are';$('#chapters').replaceChildren();
   for(const c of e.chapters||[]){const x=document.createElement('button');x.textContent=c.title;x.onclick=()=>audio.currentTime=c.start;$('#chapters').append(x);}};
  $('#episodes').append(b);
 }
 if(!data.episodes.length)$('#status').textContent='No current episodes yet.';
}
$('form').onsubmit=async e=>{e.preventDefault();try{
 const pin=$('#pin').value;$('#pin').value='';
 ({csrf}=await api('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pin})}));
 $('#error').textContent='';await load();
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
api('/api/session').then(s=>{csrf=s.csrf;return load();}).catch(()=>{});
`;
