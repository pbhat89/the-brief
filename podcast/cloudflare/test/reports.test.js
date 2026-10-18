import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {REPORTS} from '../src/reports.js';
test('reader entries match actual public report manifest',()=>{const manifest=JSON.parse(fs.readFileSync(new URL('../../reports.json',import.meta.url),'utf8'));assert.deepEqual(REPORTS.map(r=>r.id),manifest.reports.map(r=>r.id));for(const report of REPORTS){assert.match(report.source,/^https:\/\/pbhat89\.github\.io\/the-brief\/podcast\/reports\/[a-z0-9-]+\.html$/);assert.ok(report.blocks.length>0);for(const b of report.blocks){assert.ok(['h1','h2','h3','p','li','blockquote'].includes(b.type));assert.equal(typeof b.text,'string');for(const link of b.links)assert.equal(new URL(link).protocol,'https:');}}});
