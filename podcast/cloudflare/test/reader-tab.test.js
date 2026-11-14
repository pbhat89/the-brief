import {test} from 'node:test';
import assert from 'node:assert/strict';
import {parse} from 'parse5';
import fs from 'node:fs';
import {readerPresentation} from '../src/reader-presentation.js';
import {READER_DATES} from '../src/reader-dates.js';
import {ORIGINALS} from '../src/originals.js';
import {HTML} from '../src/ui.js';
import worker from '../src/worker.js';
test('standalone original dates are recent canonical HTML, independent of companion reports',()=>{
 assert.ok(READER_DATES.length<=14);assert.deepEqual(READER_DATES,[...READER_DATES].sort().reverse());
 const latest=fs.readdirSync(new URL('../../../archive/',import.meta.url)).filter(n=>/^\d{4}-\d{2}-\d{2}\.html$/.test(n)).sort().reverse()[0].slice(0,-5);assert.equal(READER_DATES[0],latest);assert.ok(ORIGINALS[latest]);
 for(const id of READER_DATES)assert.ok(fs.existsSync(new URL('../../../archive/'+id+'.html',import.meta.url)));
});
test('reader tab and controls have unique IDs and keyboard-associated panel',()=>{
 const ids=new Map();function walk(n){const id=n.attrs?.find(a=>a.name==='id')?.value;if(id){assert.ok(!ids.has(id),id);ids.set(id,n);}n.childNodes?.forEach(walk);}walk(parse(HTML));
 assert.equal(ids.get('tab-brief').attrs.find(a=>a.name==='aria-controls').value,'brief');
 assert.equal(ids.get('brief').attrs.find(a=>a.name==='aria-labelledby').value,'tab-brief');
 assert.equal(ids.get('brief-frame').attrs.find(a=>a.name==='sandbox').value,'allow-popups allow-popups-to-escape-sandbox');
 for(const id of ['brief-date','brief-mode','brief-theme','brief-smaller','brief-larger','brief-reset','brief-source'])assert.ok(ids.has(id));
});
test('presentation is bounded and cannot introduce supplied markup or arbitrary CSS',()=>{
 const source=ORIGINALS[READER_DATES[0]];
 const bad=readerPresentation(source,new URLSearchParams({mode:'<script>',theme:'red;}</style><script>',scale:'Infinity'}));
 assert.ok(!bad.includes('red;}'));assert.ok(!bad.includes('Infinity'));assert.ok(!bad.includes('<script'));
 const normal=readerPresentation(source,new URLSearchParams());assert.ok(normal.includes('section-radio'));assert.ok(!normal.includes('.sec{display:block!important'));
 const reader=readerPresentation(source,new URLSearchParams({mode:'reader',theme:'sepia',scale:'99999'}));
 assert.ok(reader.includes('.sec{display:block!important'));assert.ok(reader.includes('32.40px'));assert.ok(reader.includes('#f4ead7'));
});
test('original route retains isolation and does not interpret attacker parameters',async()=>{
 const r=await worker.fetch(new Request('https://example.com/originals/'+READER_DATES[0]+'.html?mode=reader&theme=light&scale=120'),{});
 assert.equal(r.status,200);assert.equal(r.headers.get('Set-Cookie'),null);
 const c=r.headers.get('Content-Security-Policy');assert.ok(!c.includes('allow-scripts'));assert.ok(!c.includes('allow-same-origin'));assert.match(c,/form-action 'none'/);
 const text=await r.text();assert.ok(text.includes('#fafafa'));assert.ok(text.includes('.sec{display:block!important'));assert.ok(text.includes('THE BRIEF'));assert.ok(!text.includes('<script'));
 assert.equal((await worker.fetch(new Request('https://example.com/originals/9999-99-99.html'),{})).status,404);
});
