// Refresh only the existing public news-report manifest; no private sources.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {extractReport} from './report-extractor.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'reports.json'),'utf8'));
const reports=manifest.reports.map(report=>{
 if(!/^reports\/[a-z0-9-]+\.html$/.test(report.report_url))throw Error('Unexpected public report path');
 const source='https://pbhat89.github.io/the-brief/podcast/'+report.report_url;
 return {...report,source,blocks:extractReport(fs.readFileSync(path.join(root,report.report_url),'utf8'),source)};
});
fs.writeFileSync(path.join(root,'cloudflare/src/reports.js'),'// Generated from public podcast/reports.json and HTML only.\nexport const REPORTS='+JSON.stringify(reports)+';\n');
console.log('Built '+reports.length+' public report reader entries');
