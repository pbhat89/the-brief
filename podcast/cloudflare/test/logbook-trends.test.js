import {test} from 'node:test';
import assert from 'node:assert/strict';
import {LogbookModel as m} from '../src/logbook-model.js';
const rec=(date,habits={},fitnessActivities=[])=>({date,version:1,status:'completed',habits:{...m.savePayload(date).habits,...habits},fitnessActivities});
test('rolling summary counts inverse no-sugar/no-smoke and excludes missing days',()=>{
 const records=Array.from({length:14},(_,i)=>rec(m.addDays('2030-01-28',-i),{noSugar:i>=4,noSmoke:i>=2,fitness:i<6,meditation:i<10},i<6?['walk']:[]));
 const s=m.rollingSummary('2030-01-28',records);
 assert.deepEqual(s.counts,{sugar:4,smoke:2,workout:6,meditation:10});assert.deepEqual(s.weekly,{sugar:2,smoke:1,workout:3,meditation:5});assert.equal(s.loggedDays,14);assert.equal(s.activities.walk,6);
});
test('rolling bounds exclude old, future, and unfinished records',()=>{
 const s=m.rollingSummary('2030-01-28',[rec('2030-01-01'),rec('2029-12-31'),rec('2030-01-29'),{...rec('2030-01-20'),status:'draft'}]);
 assert.equal(s.loggedDays,1);assert.equal(s.start,'2030-01-01');assert.equal(s.weekly.sugar,null);
});
test('activity chart counts each selected type and unclassified workouts',()=>{
 const s=m.rollingSummary('2030-01-28',[rec('2030-01-28',{fitness:true},['walk','tennis']),rec('2030-01-27',{fitness:true})]);
 assert.equal(s.counts.workout,2);assert.deepEqual(s.activities,{walk:1,tennis:1,cycle:0,yoga:0,other:1});
});
test('empty summary does not invent a zero average',()=>{
 const s=m.rollingSummary('2030-01-28',[]);assert.equal(s.loggedDays,0);assert.deepEqual(s.weekly,{sugar:null,smoke:null,workout:null,meditation:null});
});
