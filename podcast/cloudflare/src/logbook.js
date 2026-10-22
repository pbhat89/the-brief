import {LOGBOOK_MODEL_SOURCE} from './logbook-model-browser.js';
export const LOGBOOK_JS='\nconst LogbookModel=('+LOGBOOK_MODEL_SOURCE+')();\n'+String.raw`
let logbookState=null,logbookDate=null,logbookWeek=null,logbookRecords=new Map(),logbookDrafts=new Map(),logbookAttempts=new Map(),logbookLoading=false,logbookSaving=false,logbookSequence=0,logbookAnimations=new Set();
function logNode(tag,className,text){const node=document.createElement(tag);if(className)node.className=className;if(text!==undefined)node.textContent=text;return node;}
function logButton(text,action,className=''){const button=logNode('button',className,text);button.type='button';button.onclick=action;return button;}
function logMessage(text){$('#logbook-message').textContent=text;}
function resetLogbook(){closeCelebration(false);$('#celebration-detail').textContent='';logbookSequence++;logbookState=null;logbookDate=null;logbookWeek=null;logbookRecords.clear();logbookDrafts.clear();logbookAttempts.clear();logbookLoading=false;logbookSaving=false;logbookAnimations.clear();for(const id of ['logbook-days','logbook-day','logbook-history-days'])$('#'+id).replaceChildren();$('#logbook-history').open=false;$('#logbook-history').hidden=true;$('#logbook-message').textContent='';$('#logbook-load').hidden=false;$('#logbook-load').textContent='Open your Log book';$('#logbook-load').disabled=false;}
function logbookDraft(date){if(!logbookDrafts.has(date))logbookDrafts.set(date,{habits:{},fitnessActivities:[]});return logbookDrafts.get(date);}
function logbookOffered(){return logbookState?LogbookModel.offeredDates(logbookState.today,logbookState.startDate,[...logbookRecords.values()]):[];}
function logbookBusy(){return logbookLoading||logbookSaving||logbookAnimations.size>0;}
function rememberLogbookState(state){const oldToday=logbookState?.today;logbookState=LogbookModel.readState(state);for(const record of state.records){logbookRecords.set(record.date,record);logbookAttempts.delete(record.date);logbookDrafts.delete(record.date);}logbookWeek=state.weekStart;if(!logbookDate||!logbookOffered().includes(logbookDate))logbookDate=state.today;return oldToday&&oldToday!==state.today;}
async function loadLogbook(week,selectToday=false){
 if(logbookLoading||logbookSaving)return;
 const generation=epoch,sequence=++logbookSequence;logbookLoading=true;$('#logbook-load').disabled=true;$('#logbook-load').textContent='Loading Log book…';renderLogbook();
 try{const state=await api('/api/logbook'+(week?'?week='+encodeURIComponent(week):''));if(generation!==epoch||sequence!==logbookSequence)return;const dayChanged=rememberLogbookState(state);if(selectToday||dayChanged)logbookDate=state.today;$('#logbook-load').hidden=true;logMessage('');}
 catch(e){if(generation!==epoch||sequence!==logbookSequence)return;$('#logbook-load').hidden=false;$('#logbook-load').textContent='Try loading again';logMessage('Couldn’t load your Log book. '+e.message);}
 finally{if(generation===epoch&&sequence===logbookSequence){logbookLoading=false;$('#logbook-load').disabled=false;renderLogbook();}}
}
function openLogbook(){if(!logbookLoading&&!logbookSaving)loadLogbook(logbookWeek,!logbookState);}
function focusLogbookControl(id){if(viewing!=='logbook')return;const node=$('#'+id)||$('#logbook-done')||$('#logbook-day-title');node?.focus();}
function renderLogbook(){
 if(!logbookState)return;
 const busy=logbookBusy(),offered=logbookOffered();$('#logbook-days').replaceChildren();$('#logbook-days').hidden=offered.length<=1;
 for(const day of offered){const button=logButton((day===logbookState.today?'Today · ':'')+LogbookModel.label(day,{weekday:'short',day:'numeric',month:'short'}),()=>{if(logbookBusy())return;logbookDate=day;logMessage('');renderLogbook();$('#logbook-day-title').focus();},'log-day-button');button.setAttribute('aria-pressed',String(day===logbookDate));button.disabled=busy;$('#logbook-days').append(button);}
 const host=$('#logbook-day');host.replaceChildren();
 const heading=logNode('div','log-day-heading'),date=logNode('p','eyebrow',LogbookModel.label(logbookDate,{day:'numeric',month:'long',year:'numeric'}).toUpperCase()),title=logNode('h3','',LogbookModel.label(logbookDate,{weekday:'long'}));title.id='logbook-day-title';title.setAttribute('tabindex','-1');heading.append(date);heading.append(title);host.append(heading);
 const record=logbookRecords.get(logbookDate);
 if(record){renderLogbookSummary(host,record);host.append(logNode('p','log-saved-note','Saved. Your day is recorded, including anything you didn’t do.'));}
 else{
  const draft=logbookDraft(logbookDate),locked=busy||logbookAttempts.has(logbookDate),habits=LogbookModel.habitsFor(logbookDate),remaining=habits.filter(h=>!draft.habits[h.id]),done=habits.filter(h=>draft.habits[h.id]);
  host.append(logNode('p','log-instruction','Tap a circle for what you did. Press Done whenever you’re ready to save this day.'));
  const list=logNode('div','log-habits');list.setAttribute('role','group');list.setAttribute('aria-label','Habits for '+LogbookModel.label(logbookDate));
  for(const habit of remaining){
   const row=logNode('div','log-habit'),button=logButton('',()=>checkLogbookHabit(habit.id,row),'log-check');button.id='log-check-'+habit.id;button.setAttribute('role','checkbox');button.setAttribute('aria-checked','false');button.setAttribute('aria-label','Mark '+habit.label+' done');button.disabled=locked;
   const circle=logNode('span','log-circle');circle.setAttribute('aria-hidden','true');button.append(circle);row.append(button);
   const body=logNode('div','log-habit-body'),label=logNode('span','log-habit-label',habit.label);body.append(label);
   if(habit.id==='fitness'){
    body.append(logNode('span','log-habit-hint','Walk / tennis / cycle / yoga'));
    const choices=logNode('div','log-activities');choices.setAttribute('role','group');choices.setAttribute('aria-label','Fitness activities, optional');
    for(const activity of LogbookModel.activityOptions){const chip=logButton(activity[0].toUpperCase()+activity.slice(1),()=>{if(logbookBusy()||logbookAttempts.has(logbookDate))return;const set=new Set(draft.fitnessActivities);set.has(activity)?set.delete(activity):set.add(activity);draft.fitnessActivities=[...set];renderLogbook();focusLogbookControl('log-activity-'+activity);},'log-activity');chip.id='log-activity-'+activity;chip.setAttribute('aria-pressed',String(draft.fitnessActivities.includes(activity)));chip.setAttribute('aria-label',activity+', optional fitness activity');chip.disabled=locked;choices.append(chip);}body.append(choices);
   }
   row.append(body);list.append(row);
  }
  if(!remaining.length)list.append(logNode('p','log-all-done','Everything checked. A little moment for yourself.'));
  host.append(list);
  if(done.length){const tray=logNode('div','log-completed');tray.append(logNode('p','log-tray-label','Checked · '+done.length));for(const habit of done){const item=logNode('div','log-completed-item');const activities=habit.id==='fitness'&&draft.fitnessActivities.length?' · '+draft.fitnessActivities.join(', '):'';item.append(logNode('span','','✓ '+habit.label+activities));const undo=logButton('Undo',()=>{if(logbookBusy()||logbookAttempts.has(logbookDate))return;draft.habits[habit.id]=false;if(habit.id==='fitness')draft.fitnessActivities=[];renderLogbook();focusLogbookControl('log-check-'+habit.id);logMessage(habit.label+' moved back to your list.');},'log-undo');undo.setAttribute('aria-label','Undo '+habit.label);undo.disabled=locked;item.append(undo);tray.append(item);}host.append(tray);}
  const footer=logNode('div','log-save-area');footer.append(logNode('p','log-save-hint','Unchecked habits will be saved as “Didn’t do”. Until you press Done, this day is unlogged.'));
  const save=logButton(logbookSaving?'Saving…':logbookAttempts.has(logbookDate)?'Retry Done':'Done',()=>saveLogbook(),'log-done');save.id='logbook-done';save.disabled=busy;footer.append(save);footer.append(logNode('p','log-draft-note','Selections stay in this session until saved. Locking or reloading clears unsaved selections.'));host.append(footer);
 }
 renderLogbookHistory();
}
let celebrationFinish=null;
function closeCelebration(restore=true){const finish=celebrationFinish;celebrationFinish=null;const dialog=$('#logbook-celebration');if(dialog.open&&typeof dialog.close==='function')dialog.close();else dialog.removeAttribute('open');if(finish)finish(restore);}
$('#celebration-close').onclick=()=>closeCelebration();
$('#logbook-celebration').oncancel=e=>{e.preventDefault();closeCelebration();};
$('#logbook-celebration').onclose=()=>closeCelebration();
function checkLogbookHabit(id,row){
 if(logbookBusy()||!logbookState||logbookRecords.has(logbookDate)||logbookAttempts.has(logbookDate))return;
 if(LogbookModel.singaporeDate()!==logbookState.today){loadLogbook(logbookWeek);return;}
 const targetDate=logbookDate,draft=logbookDraft(targetDate),generation=epoch,sequence=logbookSequence;if(draft.habits[id])return;draft.habits[id]=true;
 const habit=LogbookModel.habitsFor(targetDate).find(h=>h.id===id),remaining=LogbookModel.habitsFor(targetDate).filter(h=>!draft.habits[h.id]);
 logbookAnimations.add(id);row.children[0].setAttribute('aria-checked','true');row.children[0].disabled=true;$('#logbook-done').disabled=true;
 celebrationFinish=restore=>{logbookAnimations.delete(id);if(generation!==epoch||sequence!==logbookSequence||logbookDate!==targetDate)return;renderLogbook();if(restore)focusLogbookControl(remaining.length?'log-check-'+remaining[0].id:'logbook-done');logMessage(habit.label+' checked. Use Undo to put it back.');};
 $('#celebration-detail').textContent=habit.label+' completed.';const dialog=$('#logbook-celebration');if(typeof dialog.showModal==='function')dialog.showModal();else dialog.setAttribute('open','');$('#celebration-close').focus();
}
async function saveLogbook(){
 if(logbookBusy()||!logbookState||logbookRecords.has(logbookDate))return;
 const targetDate=logbookDate,generation=epoch,sequence=logbookSequence,payload=logbookAttempts.get(targetDate)||LogbookModel.savePayload(targetDate,logbookDraft(targetDate));
 logbookAttempts.set(targetDate,payload);
 logbookSaving=true;logMessage('');renderLogbook();
 try{
  const result=await api('/api/logbook/'+encodeURIComponent(targetDate),{method:'PUT',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:JSON.stringify(payload)});
  if(generation!==epoch||sequence!==logbookSequence)return;
  if(!LogbookModel.validRecord(result.record)||result.record.date!==targetDate)throw Error('The save response could not be verified.');
  logbookRecords.set(targetDate,result.record);logbookDrafts.delete(targetDate);logbookAttempts.delete(targetDate);logMessage(LogbookModel.label(targetDate,{weekday:'long'})+' saved.');
 }catch(e){if(generation!==epoch||sequence!==logbookSequence)return;if(e.status===409&&LogbookModel.validRecord(e.currentRecord)&&e.currentRecord.date===targetDate){logbookRecords.set(targetDate,e.currentRecord);logbookDrafts.delete(targetDate);logbookAttempts.delete(targetDate);logMessage('This day was already saved in another session. Showing the saved record; your new selections were not applied.');return;}logMessage('Couldn’t confirm this save. Your selections are still here. Retry Done to check or save the same day. '+e.message);}
 finally{if(generation===epoch&&sequence===logbookSequence){logbookSaving=false;renderLogbook();if(logbookRecords.has(targetDate)&&viewing==='logbook')$('#logbook-day-title').focus();if(LogbookModel.singaporeDate()!==logbookState.today)loadLogbook(undefined,true);}}
}
function renderLogbookSummary(host,record,compact=false){const summary=logNode('div',compact?'log-summary compact':'log-summary');for(const done of [true,false]){const group=logNode('div','log-summary-group');group.append(logNode('h4','',done?'Did':'Didn’t do'));const items=LogbookModel.summary(record).filter(h=>h.done===done);if(!items.length)group.append(logNode('p','log-none',done?'None recorded':'Nothing missed'));for(const habit of items){const detail=habit.activities.length?' · '+habit.activities.join(', '):'';group.append(logNode('p','',habit.label+detail));}summary.append(group);}host.append(summary);if([0,6].includes(LogbookModel.weekday(record.date)))host.append(logNode('p','log-unlogged','Public transport · Not applicable on weekends'));}
function renderLogbookHistory(){
 if(!logbookState)return;$('#logbook-history').hidden=false;const week=logbookWeek||LogbookModel.monday(logbookState.today),end=LogbookModel.addDays(week,6);$('#logbook-week-label').textContent=LogbookModel.label(week,{day:'numeric',month:'short'})+' – '+LogbookModel.label(end,{day:'numeric',month:'short',year:'numeric'});$('#logbook-week-back').disabled=logbookBusy()||week<=LogbookModel.monday(logbookState.startDate);$('#logbook-week-next').disabled=logbookBusy()||week>=LogbookModel.monday(logbookState.today);const host=$('#logbook-history-days');host.replaceChildren();
 for(let i=0;i<7;i++){const day=LogbookModel.addDays(week,i);if(day<logbookState.startDate||day>logbookState.today)continue;const item=logNode('div','log-history-day');item.append(logNode('h4','',LogbookModel.label(day,{weekday:'long',day:'numeric',month:'short'})));const record=logbookRecords.get(day);if(record)renderLogbookSummary(item,record,true);else item.append(logNode('p','log-unlogged','Not logged'+(logbookDrafts.has(day)?' · selections not saved':'')));host.append(item);}
}
$('#logbook-load').onclick=()=>loadLogbook(logbookWeek);
$('#logbook-week-back').onclick=()=>{if(!logbookBusy())loadLogbook(LogbookModel.addDays(logbookWeek,-7));};
$('#logbook-week-next').onclick=()=>{if(!logbookBusy())loadLogbook(LogbookModel.addDays(logbookWeek,7));};
`;
