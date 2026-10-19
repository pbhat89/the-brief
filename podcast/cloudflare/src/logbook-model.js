// Pure shared UI rules. No records, credentials or network destinations live here.
export function createLogbookModel() {
 const timeZone='Asia/Singapore';
 const activityOptions=['walk','tennis','cycle','yoga'];
 const definitions=[
  {id:'noSmoke',label:'No smoke'},
  {id:'noSugar',label:'No sugar'},
  {id:'publicTransport',label:'One way public transport'},
  {id:'fitness',label:'Fitness'},
  {id:'meditation',label:'Meditation'}
 ];
 function validDate(value){return typeof value==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(value)&&Number.isFinite(Date.parse(value+'T12:00:00Z'))&&new Date(value+'T12:00:00Z').toISOString().slice(0,10)===value;}
 function singaporeDate(now=new Date()){const parts=new Intl.DateTimeFormat('en-GB',{timeZone,year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(now);return ['year','month','day'].map(type=>parts.find(p=>p.type===type).value).join('-');}
 function addDays(date,count){if(!validDate(date)||!Number.isInteger(count))throw Error('Invalid day');const value=new Date(date+'T12:00:00Z');value.setUTCDate(value.getUTCDate()+count);return value.toISOString().slice(0,10);}
 function weekday(date){if(!validDate(date))throw Error('Invalid day');return new Date(date+'T12:00:00Z').getUTCDay();}
 function monday(date){return addDays(date,-((weekday(date)+6)%7));}
 function habitsFor(date){const weekend=[0,6].includes(weekday(date));return definitions.filter(h=>!weekend||h.id!=='publicTransport');}
 function label(date,options={weekday:'long',day:'numeric',month:'long'}){if(!validDate(date))return '';return new Intl.DateTimeFormat('en-GB',{...options,timeZone:'UTC'}).format(new Date(date+'T12:00:00Z'));}
 function completed(record){return !!record&&record.status==='completed';}
 function offeredDates(today,startDate,records=[]){if(!validDate(today)||!validDate(startDate)||startDate>today)return [];const saved=new Set(records.filter(completed).map(r=>r.date));const dates=[today];for(let offset=1;offset<=5;offset++){const date=addDays(today,-offset);if(date>=startDate&&!saved.has(date))dates.push(date);}return dates;}
 function savePayload(date,draft={}){const habits=Object.fromEntries(habitsFor(date).map(h=>[h.id,draft.habits?.[h.id]===true]));const fitnessActivities=habits.fitness?activityOptions.filter(activity=>draft.fitnessActivities?.includes(activity)):[];return {version:0,habits,fitnessActivities};}
 function validRecord(record){if(!record||!validDate(record.date)||record.status!=='completed'||!Number.isSafeInteger(record.version)||record.version<1||!record.habits||!Array.isArray(record.fitnessActivities))return false;const keys=habitsFor(record.date).map(h=>h.id);return Object.keys(record.habits).length===keys.length&&keys.every(key=>typeof record.habits[key]==='boolean')&&record.fitnessActivities.length<=4&&new Set(record.fitnessActivities).size===record.fitnessActivities.length&&record.fitnessActivities.every(activity=>activityOptions.includes(activity))&&(record.habits.fitness||record.fitnessActivities.length===0);}
 function readState(value){if(!value||value.schemaVersion!==1||value.timeZone!==timeZone||!validDate(value.today)||!validDate(value.startDate)||value.startDate>value.today||!validDate(value.weekStart)||monday(value.weekStart)!==value.weekStart||!Array.isArray(value.records)||value.records.length>100||!value.records.every(validRecord)||new Set(value.records.map(r=>r.date)).size!==value.records.length||value.records.some(r=>r.date<value.startDate||r.date>value.today))throw Error('Log book is temporarily unavailable. Try again.');return value;}
 function summary(record){return habitsFor(record.date).map(h=>({...h,done:record.habits[h.id],activities:h.id==='fitness'?record.fitnessActivities:[]}));}
 return {timeZone,activityOptions,definitions,validDate,singaporeDate,addDays,weekday,monday,habitsFor,label,completed,offeredDates,savePayload,validRecord,readState,summary};
}
export const LogbookModel=createLogbookModel();
