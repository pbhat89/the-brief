// Real-browser QA with synthetic session responses only. No production secrets or data.
import http from 'node:http';
import {mkdir} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import worker from '../src/worker.js';
import {REPORTS} from '../src/reports.js';
const reviewedReport=REPORTS.find(r=>r.id==='2026-10-22');
const missingReport=REPORTS.find(r=>r.id==='2026-10-21');
const server=http.createServer(async(req,res)=>{try{const r=await worker.fetch(new Request('http://127.0.0.1:9880'+req.url),{});res.writeHead(r.status,Object.fromEntries(r.headers));res.end(Buffer.from(await r.arrayBuffer()));}catch{res.writeHead(500);res.end('Preview unavailable');}});
await new Promise(r=>server.listen(9880,'127.0.0.1',r));
let browser;
try{
 browser=await chromium.launch({headless:true});await mkdir('qa-original',{recursive:true});
 for(const width of [390,1280]){
  const page=await browser.newPage({viewport:{width,height:844}}),errors=[],external=[];
  page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:9880')&&!r.url().startsWith('data:'))external.push(r.url());});
  await page.route('**/api/**',route=>{const path=new URL(route.request().url()).pathname;return route.fulfill({json:path==='/api/session'?{csrf:'synthetic'}:path==='/api/episodes'?{episodes:[]}:{activeAudioBytes:0,activeEpisodes:0,freeStorageBytes:1000000000,complete:true}});});
  await page.goto('http://127.0.0.1:9880/');await page.locator('#tab-previous').click();await page.locator('#reports button').filter({hasText:reviewedReport.title}).first().click();
  const frame=page.frameLocator('#reader-original-frame');await frame.locator('.title').waitFor();
  assert.equal(await page.locator('#viewer-date').innerText(),'22 October 2026');
  assert.equal(await page.locator('#reader-original').getAttribute('aria-pressed'),'true');
  assert.equal(await frame.locator('.title').evaluate(e=>getComputedStyle(e).fontFamily),'"Playfair Display", serif');
  await frame.locator('.title').evaluate(()=>document.fonts.ready);await page.screenshot({path:`qa-original/${width}-original.png`,fullPage:true});
  assert.ok(await frame.locator('.title').evaluate(()=>document.fonts.check('900 40px "Playfair Display"')));
  assert.ok(await frame.locator('body').evaluate(e=>e.scrollWidth<=innerWidth));
  await frame.locator('label[for="select-fun"]').click();assert.ok(await frame.locator('#sec-fun').isVisible());assert.ok(!(await frame.locator('#sec-sg').isVisible()));assert.match(await frame.locator('#sec-fun').innerText(),/Cleopatra/);
  await page.screenshot({path:`qa-original/${width}-fact.png`,fullPage:true});
  await page.locator('#reader-verified').click();assert.ok(await page.locator('#reader-content').isVisible());assert.match(await page.locator('#reader-content').innerText(),/Uranus/);assert.equal(await page.locator('#reader-original-frame').getAttribute('src'),null);
  await page.screenshot({path:`qa-original/${width}-verified.png`,fullPage:true});
  await page.locator('#reader-original').click();await frame.locator('.title').waitFor();await page.locator('#reader-back').click();assert.equal(await page.locator('#reader-original-frame').getAttribute('src'),null);
  await page.locator('#reports button').filter({hasText:missingReport.title}).first().click();assert.ok(await page.locator('#reader-original').isDisabled());assert.match(await page.locator('#reader-notice').innerText(),/No original upstream HTML/);
  await page.locator('#reader-back').click();await page.locator('#reports button').filter({hasText:reviewedReport.title}).first().click();await page.locator('#logout').click();await page.locator('#login').waitFor({state:'visible'});assert.ok(await page.locator('#login').isVisible());assert.equal(await page.locator('#reader-original-frame').getAttribute('src'),null);
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);await page.close();
 }
 console.log('PASS: 390px/1280px original design and local fonts, original/verified fact distinction, section selection, repeated view switching, missing original fallback, Back/Lock cleanup, no external network requests or page errors.');
}finally{await browser?.close();await new Promise(r=>server.close(r));}
