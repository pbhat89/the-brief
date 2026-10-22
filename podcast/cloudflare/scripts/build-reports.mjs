// Refresh only the existing public news-report manifest; no private sources.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {extractOriginal} from './original-extractor.mjs';
import {extractReport} from './report-extractor.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'reports.json'),'utf8'));
const originals={};
const reports=manifest.reports.map(report=>{
 if(!/^reports\/[a-z0-9-]+\.html$/.test(report.report_url))throw Error('Unexpected public report path');
 const source='https://pbhat89.github.io/the-brief/podcast/'+report.report_url;
 const archive=path.join(root,'../archive',report.id+'.html');
 let original=null;
 if(/^\d{4}-\d{2}-\d{2}$/.test(report.id)&&fs.existsSync(archive)){
  const html=fs.readFileSync(archive,'utf8');
  originals[report.id]=extractOriginal(html,report.id);
  original={path:'/originals/'+report.id+'.html',source:'https://pbhat89.github.io/the-brief/archive/'+report.id+'.html'};
 }
 return {...report,source,original,blocks:extractReport(fs.readFileSync(path.join(root,report.report_url),'utf8'),source)};
});
fs.writeFileSync(path.join(root,'cloudflare/src/reports.js'),'// Generated from public podcast/reports.json and HTML only.\nexport const REPORTS='+JSON.stringify(reports)+';\n');
console.log('Built '+reports.length+' public report reader entries');

fs.writeFileSync(path.join(root,'cloudflare/src/originals.js'),'// Generated from public upstream archive HTML only; escaped literal content, no scripts.\nexport const ORIGINALS='+JSON.stringify(originals)+';\n');
