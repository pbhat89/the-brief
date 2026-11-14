// Synthetic authenticated responses only. No production PIN or user data.
import http from 'node:http';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {chromium} from 'playwright';
import worker from '../src/worker.js';
import {READER_DATES} from '../src/reader-dates.js';
const day=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Singapore',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
const availableDate=READER_DATES.find(id=>id<=day);
assert.ok(availableDate,'A non-future canonical issue is required');
const port=9885,origin='http://127.0.0.1:'+port;
const server=http.createServer(async(req,res)=>{try{const r=await worker.fetch(new Request(origin+req.url),{});res.writeHead(r.status,Object.fromEntries(r.headers));res.end(Buffer.from(await r.arrayBuffer()));}catch(e){res.writeHead(500);res.end(String(e));}});
await new Promise(r=>server.listen(port,'127.0.0.1',r));
let browser;
try{
 browser=await chromium.launch({headless:true,...(process.env.BROWSER_EXECUTABLE?{executablePath:process.env.BROWSER_EXECUTABLE}:{})});await fs.mkdir('qa-reader',{recursive:true});
 for(const width of [360,390,1280]){
  const page=await browser.newPage({viewport:{width,height:844}});const errors=[],external=[];page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(!r.url().startsWith(origin)&&!r.url().startsWith('data:'))external.push(r.url());});
  await page.route('**/api/**',route=>route.fulfill({json:new URL(route.request().url()).pathname==='/api/session'?{csrf:'synthetic'}:{episodes:[],activeAudioBytes:0,activeEpisodes:0,freeStorageBytes:1e9,complete:true}}));
  await page.goto(origin);await page.locator('#tab-brief').click();
  const frame=page.frameLocator('#brief-frame');await frame.locator('.title').waitFor();
  async function settled(){const f=await (await page.locator('#brief-frame').elementHandle()).contentFrame();await f.waitForURL(new URL(await page.locator('#brief-frame').getAttribute('src'),origin).href,{waitUntil:'load'});await frame.locator('#reader-presentation').waitFor({state:'attached'});}
  assert.equal(await page.locator('#brief-date').inputValue(),availableDate);assert.equal(await page.locator('#brief-source').getAttribute('href'),'https://pbhat89.github.io/the-brief/archive/'+availableDate+'.html');
  assert.ok(await page.locator('body').evaluate(e=>e.scrollWidth<=innerWidth));
  const sectionId=await frame.locator('label.tab').nth(1).getAttribute('for');await frame.locator('label.tab').nth(1).click();assert.ok(await frame.locator('#sec-'+sectionId.slice(7)).isVisible());
  await page.screenshot({path:'qa-reader/'+width+'-original.png',fullPage:true});
  await page.locator('#brief-mode').selectOption('reader');await page.locator('#brief-theme').selectOption('sepia');await page.locator('#brief-larger').click();
  await settled();assert.ok(await frame.locator('.sec').nth(0).isVisible());assert.ok(await frame.locator('.sec').nth(1).isVisible());assert.equal(await frame.locator('body').evaluate(e=>getComputedStyle(e).backgroundColor),'rgb(244, 234, 215)');
  assert.ok(await frame.locator('body').evaluate(e=>e.scrollWidth<=innerWidth));
  const size=await frame.locator('.summary').first().evaluate(e=>parseFloat(getComputedStyle(e).fontSize));assert.equal(size,19.8);
  await page.screenshot({path:'qa-reader/'+width+'-sepia-reader.png',fullPage:true});
  await page.reload();await page.locator('#tab-brief').click();await frame.locator('.title').waitFor();assert.equal(await page.locator('#brief-mode').inputValue(),'reader');assert.equal(await page.locator('#brief-theme').inputValue(),'sepia');assert.equal(await page.locator('#brief-size-label').innerText(),'110%');
  for(let i=0;i<12;i++)if(await page.locator('#brief-larger').isEnabled()){await page.locator('#brief-larger').click();await settled();}assert.equal(await page.locator('#brief-size-label').innerText(),'180%');assert.ok(await frame.locator('body').evaluate(e=>e.scrollWidth<=innerWidth));
  await page.locator('#brief-reset').click();await settled();assert.equal(await page.locator('#brief-size-label').innerText(),'100%');assert.equal(await page.locator('#brief-mode').inputValue(),'original');
  await page.locator('#tab-brief').focus();await page.keyboard.press('ArrowRight');assert.equal(await page.locator('#tab-personal').getAttribute('aria-selected'),'true');
  await page.locator('#tab-brief').click();await page.locator('#logout').click();await page.locator('#login').waitFor({state:'visible'});assert.equal(await page.locator('#brief-frame').getAttribute('src'),null);
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);await page.close();
 }
 console.log('PASS: 360/390/1280px, source/date, original sections, reader all-sections, sepia, text size bounds, reset, local preference reload, keyboard tabs, Lock cleanup, zero external requests/errors.');
}finally{await browser?.close();await new Promise(r=>server.close(r));}
