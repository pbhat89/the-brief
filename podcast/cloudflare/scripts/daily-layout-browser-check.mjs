// Synthetic fixtures only. Never reads or writes owner task state.
import http from 'node:http';
import {mkdir} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import worker from '../src/worker.js';
import {REPORTS} from '../src/reports.js';
// Use the newest shipped original for the positive case; the next day has no report.
const fixtureDay=REPORTS.map(r=>r.id).sort().at(-1);
assert.match(fixtureDay,/^\d{4}-\d{2}-\d{2}$/);
assert.ok(REPORTS.find(r=>r.id===fixtureDay)?.original, 'Newest report must provide the positive original-reader fixture');
const fixtureInstant=fixtureDay+'T12:00:00Z';
const previousDay=new Date(Date.parse(fixtureInstant)-86400000).toISOString().slice(0,10);
const fixtureDate=new Date(fixtureDay+'T00:00:00Z');
const weekStart=new Date(+fixtureDate-((fixtureDate.getUTCDay()+6)%7)*86400000).toISOString().slice(0,10);
const server=http.createServer(async(req,res)=>{const r=await worker.fetch(new Request('http://127.0.0.1:9881'+req.url),{});res.writeHead(r.status,Object.fromEntries(r.headers));res.end(Buffer.from(await r.arrayBuffer()));});
await new Promise(r=>server.listen(9881,'127.0.0.1',r));let browser;
try{
 browser=await chromium.launch({headless:true});await mkdir('qa-original',{recursive:true});
 for(const width of [390,1280])for(const reducedMotion of ['no-preference','reduce']){
  const page=await browser.newPage({viewport:{width,height:844},reducedMotion}),errors=[];let saves=0;
  page.on('pageerror',e=>errors.push(String(e)));
  await page.clock.install({time:new Date(fixtureInstant)});
  const now=Date.parse(fixtureInstant)/1000;
  await page.route('**/api/**',route=>{const path=new URL(route.request().url()).pathname;if(route.request().method()==='PUT')saves++;return route.fulfill({json:path==='/api/session'?{csrf:'synthetic'}:path==='/api/episodes'?{episodes:[{id:'fixture-today',edition:fixtureDay,title:'Today fixture',created:now,expires:now+604800,duration:600,chapters:[]},{id:'fixture-old',edition:previousDay,title:'Earlier fixture',created:now-86400,expires:now+500000,chapters:[]}]}:path==='/api/logbook'?{schemaVersion:1,timeZone:'Asia/Singapore',today:fixtureDay,startDate:fixtureDay,weekStart:weekStart,records:[],pendingDates:[fixtureDay]}:{activeAudioBytes:0,activeEpisodes:0,freeStorageBytes:1e9,complete:true}});});
  await page.goto('http://127.0.0.1:9881/');await page.locator('#player').waitFor({state:'visible'});
  assert.equal(await page.locator('#title').innerText(),'Today fixture');assert.equal(await page.locator('#episodes button').count(),0);
  assert.ok(await page.locator('#play').isVisible());assert.ok(await page.locator('#today-read').isVisible());
  assert.ok(await page.locator('body').evaluate(e=>e.scrollWidth<=innerWidth));
  await page.screenshot({path:`qa-original/${width}-${reducedMotion}-today.png`,fullPage:true});
  await page.locator('#today-read').click();await page.frameLocator('#reader-original-frame').locator('.title').waitFor();await page.locator('#reader-back').click();assert.equal(await page.locator('#tab-latest').getAttribute('aria-selected'),'true');
  await page.locator('#tab-previous').click();await page.locator('#previous-audio button').filter({hasText:'Earlier fixture'}).click();assert.equal(await page.locator('#tab-previous').getAttribute('aria-selected'),'true');assert.ok(await page.locator('#listening').isVisible());
  await page.locator('#tab-latest').click();assert.equal(await page.locator('#title').innerText(),'Today fixture');
  await page.locator('#tab-logbook').click();await page.locator('#log-check-noSmoke').click();assert.ok(await page.locator('#logbook-celebration').isVisible());assert.equal(await page.evaluate(()=>document.activeElement.id),'celebration-close');
  await page.keyboard.press('Shift+Tab');assert.equal(await page.evaluate(()=>document.activeElement.id),'celebration-close');await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement.id),'celebration-close');
  if(reducedMotion==='reduce')assert.equal(await page.locator('.celebration-art').evaluate(e=>getComputedStyle(e).animationName),'none');
  await page.screenshot({path:`qa-original/${width}-${reducedMotion}-celebration.png`,fullPage:true});
  await page.keyboard.press('Escape');await page.locator('#logbook-celebration').waitFor({state:'hidden'});assert.equal(await page.evaluate(()=>document.activeElement.id),'log-check-noSugar');
  assert.equal(await page.locator('.log-completed-item>span').evaluate(e=>getComputedStyle(e).textDecorationLine),'line-through');
  await page.getByRole('button',{name:'Undo No smoke',exact:true}).click();assert.ok(await page.locator('#log-check-noSmoke').isVisible());
  await page.locator('#log-check-noSmoke').click();await page.locator('#celebration-close').click();await page.locator('#tab-latest').click();
  const quote=await page.locator('#daily-quote').innerText();await page.clock.fastForward(4*3600000+61000);assert.notEqual(await page.locator('#daily-quote').innerText(),quote);assert.ok(await page.locator('#today-empty').isVisible());assert.ok(!(await page.locator('#today-read').isVisible()));assert.ok(!(await page.locator('#listening').isVisible()));
  assert.equal(saves,0);await page.reload();await page.locator('#player').waitFor({state:'visible'});assert.ok(!(await page.locator('#logbook-celebration').isVisible()));await page.locator('#logout').click();await page.locator('#login').waitFor({state:'visible'});assert.equal(await page.locator('#celebration-detail').innerText(),'');assert.deepEqual(errors,[]);await page.close();
 }
 console.log('PASS: Today/Previous separation, same-day original reader/back, Singapore midnight rollover, responsive reflection, reduced-motion modal, keyboard focus/Escape, strike/undo, reload/Lock; synthetic data only.');
}finally{await browser?.close();await new Promise(r=>server.close(r));}
