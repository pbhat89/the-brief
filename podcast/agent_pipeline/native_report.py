"""Read-only private native bridge audit export; never renders prompts or tool bodies."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from .audit import verify_private_path, elapsed_seconds, utc_now, sanitize, _json
from .native_urls import public_source_url
from .native_bridge import digest
from jsonschema import Draft202012Validator

TABS=('Runs','AgentJobs','ToolEvidence','Rejections','Quality','Artifacts','Lineage','Limitations','Events')

def checked(path):
    p=Path(path).expanduser().absolute()
    if p.resolve()!=p:raise ValueError('Canonical non-linked path required')
    verify_private_path(p)
    return p

def read_db(path):
    p=checked(path)
    db=sqlite3.connect(p.as_uri()+'?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
    return db

def fields(data,names):
    return {k:sanitize(data.get(k),k) for k in names}

def chain(db):
    previous='0'*64;rows=[]
    for row in db.execute('SELECT * FROM events ORDER BY seq'):
        e=dict(row);payload=json.loads(e['payload'])
        values=[e['event_id'],e['run_id'],e['kind'],e['entity_id'],e['recorded_at'],_json(payload),previous]
        expected=hashlib.sha256(_json(values).encode()).hexdigest()
        if previous!=e['previous_hash'] or expected!=e['event_hash']:raise ValueError('Audit chain invalid')
        previous=expected;e['payload']=payload;rows.append(e)
    return rows

def collect(directory, *, include_public_urls=False):
    root=checked(directory);data={k:[] for k in TABS};runrows={}
    for name in ('audit.sqlite3','native-audit.sqlite3'):
        path=root/name
        if not path.exists():
            data['Limitations'].append({'limitation':'Missing optional audit database','database':name});continue
        db=read_db(path)
        try:events=chain(db)
        finally:db.close()
        data['Quality'].append({'database':name,'check':'event_hash_chain','outcome':'pass','events':len(events)})
        for e in events:
            row=fields(e,('seq','event_id','run_id','kind','entity_id','recorded_at','previous_hash','event_hash'));row['database']=name;data['Events'].append(row)
            p=e['payload']
            if e['kind'] in ('run_started','run_finished'):
                key=(name,e['run_id']);r=runrows.setdefault(key,{'database':name,'run_id':e['run_id']})
                r.update({k:v for k,v in fields(p,('started_at','ended_at','status','deadline_at','delivered_at')).items() if v is not None})
            if e['kind'] in ('checkpoint','validation'):
                data['Quality'].append(dict(row,**fields(p,('status','passed','check','error_kind'))))
            if e['kind']=='artifact':data['Artifacts'].append(dict(row,**fields(p,('sha256','status','bytes','media_type'))))
    for r in runrows.values():
        r['wall_seconds']=elapsed_seconds(r.get('started_at'),r.get('ended_at'));r.setdefault('status','pending');data['Runs'].append(r)
    db=read_db(root/'native-jobs.sqlite3')
    try:
        for job in db.execute('SELECT * FROM jobs ORDER BY queued_at,id'):
            j=dict(job);req=json.loads(j['request'])
            if digest(req)!=j['request_hash'] or digest(req['prompt'])!=req['prompt_hash'] or digest(req['schema'])!=req['schema_hash']:raise ValueError('Job request hash invalid')
            if digest([req['run_id'],req['role'],req['attempt']])!=j['id']:raise ValueError('Job identity hash invalid')
            if j['output'] is not None and digest(json.loads(j['output']))!=j['output_hash']:raise ValueError('Job output hash invalid')
            if j['output'] is not None:Draft202012Validator(req['schema']).validate(json.loads(j['output']))
            if j['state']=='completed' and (j['output'] is None or not j['completed_at']):raise ValueError('Completed job missing output or completion')
            row=fields(j,('id','state','agent_id','queued_at','started_at','completed_at','request_hash','output_hash','error_kind'))
            row.update(fields(req,('run_id','role','attempt','retry_of','provider','transport','context_hash','runtime_source_hash','prompt_hash','schema_hash')))
            row.update(queue_wall_seconds=elapsed_seconds(j['queued_at'],j['started_at']),claimed_wall_seconds=elapsed_seconds(j['started_at'],j['completed_at']),inference_seconds=None,tokens=None)
            data['AgentJobs'].append(row)
            data['Lineage'].append(fields(row,('id','run_id','role','attempt','retry_of','context_hash','runtime_source_hash','request_hash','output_hash')))
        for record in db.execute('SELECT * FROM evidence ORDER BY ingested_at,job_id,manifest_id'):
            e=dict(record);m=json.loads(e['payload'])
            if digest(m)!=e['payload_hash'] or m['manifest_id']!=e['manifest_id']:raise ValueError('Evidence payload hash invalid')
            for entry in m['entries']:
                row=fields(e,('job_id','manifest_id','payload_hash','ingested_at'));row.update(fields(m,('driver_id',)))
                row.update(fields(entry,('tool_ref','tool_name','operation','basis','started_at','observed_at','tool_result_sha256')))
                # Exact safe public URL only with explicit private-report opt-in; never redact then misattribute.
                if include_public_urls and public_source_url(entry.get('url'))==entry.get('url') and entry.get('url') is not None:
                    row['public_source_url']=entry['url']
                row['url_sha256']=digest(entry.get('url'));row['source_observed_wall_seconds']=elapsed_seconds(entry.get('started_at'),entry.get('observed_at'))
                data['ToolEvidence'].append(row)
        for record in db.execute('SELECT seq,job_id,metadata,mirrored FROM transitions ORDER BY seq'):
            t=dict(record);m=json.loads(t['metadata'])
            if m.get('state')=='submission_rejected':
                data['Rejections'].append(dict(fields(t,('seq','job_id','mirrored')),**fields(m,('state','observed_at','operation','rejection_kind','submission_hash'))))
        data['Quality'].append({'check':'native_request_output_evidence_hashes','outcome':'pass'})
    finally:db.close()
    for p in sorted(root.glob('*manifest.json')):
        checked(p);data['Lineage'].append({'manifest_file':p.name,'file_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    data['Limitations'].append({'limitation':'Exact syntactically public source URLs included only if safe filter accepts them; not proof of public access' if include_public_urls else 'Public source URLs excluded; hash-only source identity (default)'})
    data['Limitations'] += [{'limitation':s} for s in (
        'Private operational export. No raw prompts, tool content, source quotations or credentials.',
        'Blank metrics are unknown, not zero. Token usage and inference duration are unavailable.',
        'Queued-to-claim and claim-to-completion are bridge wall time, not inference time; preclaim review excluded.',
        'Source started_at/observed_at are original driver-captured timestamps; ingested_at is reattachment time, not a fresh fetch.',
        'Hash integrity is not cryptographic tool attestation or proof of source truth.',
        'Each database is a read-only transaction snapshot; concurrent cross-database updates can produce temporary mirror lag.',
        'Pending jobs are unfinished, not successful. No fabricated completion or publication status.',
        'Manifest file hashes identify snapshot bytes; external files and raw receipt authenticity require separate validation.')]
    return data

def collect_related(directory, related_directories=(), *, include_public_urls=False):
    """Keep independent verified snapshots distinct; never combine databases."""
    data={k:[] for k in TABS};seen=set()
    for directory in (directory,*related_directories):
        root=checked(directory)
        if root in seen:continue
        seen.add(root)
        for tab,rows in collect(root,include_public_urls=include_public_urls).items():
            for row in rows:
                data[tab].append(dict(row,report_scope=root.name))
    return data

def export_report(directory,output, *, include_public_urls=False, related_directories=()):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    root=checked(directory);out=Path(output).expanduser().absolute()
    if out.resolve()!=out or out.suffix.lower()!='.xlsx':raise ValueError('Canonical XLSX output required')
    checked(out.parent)
    if out.exists():raise FileExistsError('Refusing to overwrite existing artifact')
    data=collect_related(root,related_directories,include_public_urls=include_public_urls);wb=Workbook();wb.remove(wb.active)
    for title in TABS:
        ws=wb.create_sheet(title);rows=data[title];columns=list(dict.fromkeys(k for row in rows for k in row)) or ['status']
        ws.append(columns)
        for row in rows:
            values=[]
            for c in columns:
                value=row.get(c)
                if isinstance(value,(dict,list)):value=json.dumps(value,sort_keys=True)
                if isinstance(value,str) and value.startswith(('=','+','-','@')):value="'"+value
                values.append(value)
            ws.append(values)
        ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
        for cell in ws[1]:cell.font=Font(bold=True)
        for col in ws.columns:ws.column_dimensions[col[0].column_letter].width=28
    fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(fd,'wb') as f:wb.save(f)
        verify_private_path(out)
    except Exception:
        # Preserve partial artifact for diagnosis; caller must not report it as complete.
        raise
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',required=True);p.add_argument('--output',required=True);p.add_argument('--include-public-urls',action='store_true');p.add_argument('--related-directory',action='append',default=[]);a=p.parse_args();print(export_report(a.directory,a.output,include_public_urls=a.include_public_urls,related_directories=a.related_directory))
if __name__=='__main__':main()
