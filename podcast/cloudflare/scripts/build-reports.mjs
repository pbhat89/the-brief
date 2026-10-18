// Build a text-only reader snapshot from the existing public news-report manifest.
// Raw HTML is never sent to the browser or assigned to innerHTML.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const decode=s=>s.replace(/&#(x[0-9a-f]+|[0-9]+);/gi,(_,n)=>String.fromCodePoint(parseInt(n[0].toLowerCase()==='x'?n.slice(1):n,n[0].toLowerCase()==='x'?16:10))).replace(/&(amp|lt|gt|quot|apos|nbsp);/g,(_,n)=>({amp:'&',lt:'<',gt:'>',quot:'"',apos:"'",nbsp:' '})[n]);
const manifest=JSON.parse(fs.readFileSync(path.join(root,'reports.json'),'utf8'));
const reports=manifest.reports.map(report=>{
 if(!/^reports\/[a-z0-9-]+\.html$/.test(report.report_url))throw Error('Unexpected public report path');
 const html=fs.readFileSync(path.join(root,report.report_url),'utf8').replace(/<(script|style|nav|form)\b[^>]*>[\s\S]*?<\/\1>/gi,'');
 const blocks=[...html.matchAll(/<(h1|h2|h3|p|li|blockquote)\b[^>]*>([\s\S]*?)<\/\1>/gi)].map(m=>({type:m[1],text:decode(m[2].replace(/<[^>]*>/g,' ')).replace(/\s+/g,' ').trim(),links:[...m[2].matchAll(/href="(https:\/\/[^"\s]+)"/g)].map(a=>decode(a[1]))})).filter(b=>b.text);
 return {...report,source:'https://pbhat89.github.io/the-brief/podcast/'+report.report_url,blocks};
});
fs.writeFileSync(path.join(root,'cloudflare/src/reports.js'),'// Generated from public podcast/reports.json and HTML only.\nexport const REPORTS='+JSON.stringify(reports)+';\n');
console.log('Built '+reports.length+' public report reader entries');
