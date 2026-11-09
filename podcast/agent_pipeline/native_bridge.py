"""Private durable handoff, NOT a standalone native-agent spawning API.

An assistant driver must actually spawn an agent, then supply its returned ID.
No subscription attribution, model token estimates, raw audit prompts or API keys.
"""
from __future__ import annotations
import argparse
import hashlib
from functools import wraps
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3
from contextlib import contextmanager
from jsonschema import Draft202012Validator, ValidationError, SchemaError
from .audit import AuditStore, verify_private_path, utc_now, elapsed_seconds

PROVIDER = 'native_assistant_subagent'
TRANSPORT = 'assistant_tool_handoff'

class NativeBridgeError(RuntimeError):
    pass

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def identifier(value):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9_./:-]{1,200}',value) or '..' in value:
        raise NativeBridgeError('Invalid handoff identifier')
    return value


def audit_rejections(method):
    @wraps(method)
    def wrapped(self,*args,**kwargs):
        try:
            return method(self,*args,**kwargs)
        except (NativeBridgeError,ValidationError,SchemaError,ValueError,TypeError) as error:
            kind='schema' if isinstance(error,(ValidationError,SchemaError)) else 'invalid_submission'
            if isinstance(error,NativeBridgeError):
                text=str(error).lower()
                if 'identity' in text or 'hash' in text:kind='identity'
                elif 'claim' in text or 'complete' in text or 'retry' in text:kind='state'
            self._reject(method.__name__,args,kwargs,kind)
            raise
    return wrapped

class NativeBridge:
    def __init__(self, private_dir):
        self.root=Path(private_dir).absolute()
        if self.root.resolve()!=self.root or not self.root.is_dir():
            raise NativeBridgeError('Existing non-linked private directory required')
        verify_private_path(self.root)
        for name in ('native-jobs.sqlite3','native-audit.sqlite3'):
            if (self.root/name).exists():verify_private_path(self.root/name)
        self.db=sqlite3.connect(self.root/'native-jobs.sqlite3',timeout=30)
        self.db.row_factory=sqlite3.Row
        # Private parent protects files even while SQLite creates them.
        if __import__('os').name!='nt':(self.root/'native-jobs.sqlite3').chmod(0o600)
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, request TEXT NOT NULL, request_hash TEXT NOT NULL, state TEXT NOT NULL, agent_id TEXT, queued_at TEXT NOT NULL, started_at TEXT, completed_at TEXT, output TEXT, output_hash TEXT, error_kind TEXT)')
        self.db.execute('CREATE TABLE IF NOT EXISTS transitions(seq INTEGER PRIMARY KEY, job_id TEXT NOT NULL, metadata TEXT NOT NULL, mirrored INTEGER NOT NULL DEFAULT 0)')
        self.db.execute('CREATE TABLE IF NOT EXISTS rejections(id TEXT PRIMARY KEY)')
        self.db.execute('CREATE TABLE IF NOT EXISTS evidence(job_id TEXT NOT NULL, manifest_id TEXT NOT NULL, payload TEXT NOT NULL, payload_hash TEXT NOT NULL, ingested_at TEXT NOT NULL, PRIMARY KEY(job_id,manifest_id))')
        self.db.commit()
        self.audit=AuditStore(self.root/'native-audit.sqlite3')
        if not self.audit.events('native-handoff'):
            self.audit.start_run('native-handoff',provider=PROVIDER,transport=TRANSPORT)
        self._mirror()

    def close(self):
        self.audit.close();self.db.close()

    @contextmanager
    def _transaction(self):
        verify_private_path(self.root)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield
            self.db.commit()
        except BaseException:
            self.db.rollback();raise
        self._mirror()

    def _mirror(self):
        # Durable outbox: a failed audit mirror never loses a committed transition.
        # On retry, inspect metadata IDs before append to avoid duplicate replay.
        for row in self.db.execute('SELECT * FROM transitions WHERE mirrored=0 ORDER BY seq').fetchall():
            eid='native-transition-'+str(row['seq'])
            found=any(e.get('entity_id')==eid for e in self.audit.events('native-handoff'))
            if not found:
                self.audit.event('native-handoff','native_transition',entity_id=eid,**json.loads(row['metadata']))
            self.db.execute('UPDATE transitions SET mirrored=1 WHERE seq=?',(row['seq'],));self.db.commit()

    def _record(self,job_id,state,**fields):
        metadata=dict(job_id=job_id,state=state,observed_at=utc_now(),provider=PROVIDER,
                      transport=TRANSPORT,usage=None,**fields)
        self.db.execute('INSERT INTO transitions(job_id,metadata) VALUES(?,?)',(job_id,canonical(metadata)))

    def _reject(self,operation,args,kwargs,kind):
        # Values are hashed only, never rendered in logs (including schema errors).
        try:
            fingerprint=digest([operation,args,kwargs])
        except (ValueError,TypeError):
            fingerprint=digest([operation,'non_json_submission',kind])
        with self._transaction():
            inserted=self.db.execute('INSERT OR IGNORE INTO rejections(id) VALUES(?)',(fingerprint,)).rowcount
            if inserted:
                self._record('rejected-'+fingerprint,'submission_rejected',operation=operation,
                             rejection_kind=kind,submission_hash=fingerprint)

    def _row(self,job_id):
        row=self.db.execute('SELECT * FROM jobs WHERE id=?',(identifier(job_id),)).fetchone()
        if row is None:raise NativeBridgeError('Unknown job')
        try:request=json.loads(row['request'])
        except ValueError:raise NativeBridgeError('Request corruption') from None
        if digest(request)!=row['request_hash']:raise NativeBridgeError('Request hash mismatch')
        return row,request

    @audit_rejections
    def queue(self,run_id,role,prompt,schema,context_hash,runtime_source_hash,attempt=1,retry_of=None):
        identifier(run_id);identifier(role)
        if not isinstance(prompt,str) or not prompt or len(prompt)>1000000:raise NativeBridgeError('Bounded prompt required')
        if not isinstance(schema,dict):raise NativeBridgeError('Schema object required')
        Draft202012Validator.check_schema(schema)
        for value in (context_hash,runtime_source_hash):
            if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{64}',value):raise NativeBridgeError('SHA256 identity required')
        if type(attempt)!=int or not 1<=attempt<=3:raise NativeBridgeError('One to three explicit attempts required')
        req=dict(run_id=run_id,role=role,prompt=prompt,schema=schema,context_hash=context_hash,
                 runtime_source_hash=runtime_source_hash,attempt=attempt,retry_of=retry_of,
                 prompt_hash=digest(prompt),schema_hash=digest(schema),provider=PROVIDER,transport=TRANSPORT)
        job_id=digest([run_id,role,attempt]);rh=digest(req)
        with self._transaction():
            old=self.db.execute('SELECT request_hash FROM jobs WHERE id=?',(job_id,)).fetchone()
            if old:
                self._row(job_id)
                if old['request_hash']!=rh:raise NativeBridgeError('Immutable request conflict')
            else:
                if attempt>1:
                    previous,pr=self._row(retry_of)
                    if previous['state']!='failed' or pr['run_id']!=run_id or pr['role']!=role or pr['attempt']!=attempt-1:
                        raise NativeBridgeError('Retry requires matching failed previous attempt')
                elif retry_of is not None:raise NativeBridgeError('First attempt cannot retry')
                self.db.execute('INSERT INTO jobs(id,request,request_hash,state,queued_at) VALUES(?,?,?,?,?)',
                                (job_id,canonical(req),rh,'queued',utc_now()))
                self._record(job_id,'queued',request_hash=rh,origin_run_id=run_id,role=role,attempt=attempt)
        return self.status(job_id)

    def request(self,job_id):
        verify_private_path(self.root)
        row,req=self._row(job_id)
        return dict(job_id=job_id,request_hash=row['request_hash'],request=req)

    @audit_rejections
    def claim(self,job_id,request_hash,agent_id):
        identifier(agent_id)
        with self._transaction():
            row,_=self._row(job_id)
            if request_hash!=row['request_hash']:raise NativeBridgeError('Request identity mismatch')
            if row['state']=='claimed' and row['agent_id']==agent_id:pass
            elif row['state']!='queued':raise NativeBridgeError('Job cannot be claimed')
            else:
                now=utc_now()
                self.db.execute('UPDATE jobs SET state=?,agent_id=?,started_at=? WHERE id=?',('claimed',agent_id,now,job_id))
                self._record(job_id,'claimed',agent_id=agent_id,started_at=now,queue_seconds=elapsed_seconds(row['queued_at'],now))
        return self.status(job_id)

    def _finish(self,job_id,request_hash,agent_id,output=None,error_kind=None):
        identifier(agent_id)
        with self._transaction():
            row,req=self._row(job_id)
            if row['request_hash']!=request_hash or row['agent_id']!=agent_id:raise NativeBridgeError('Claim identity mismatch')
            target='failed' if error_kind is not None else 'completed'
            oh=digest(output) if target=='completed' else None
            if row['state']==target and row['output_hash']==oh and row['error_kind']==error_kind:pass
            elif row['state']!='claimed':raise NativeBridgeError('Job cannot be completed')
            else:
                if target=='completed':Draft202012Validator(req['schema']).validate(output)
                else:identifier(error_kind)
                now=utc_now();seconds=elapsed_seconds(row['started_at'],now)
                self.db.execute('UPDATE jobs SET state=?,completed_at=?,output=?,output_hash=?,error_kind=? WHERE id=?',
                    (target,now,canonical(output) if target=='completed' else None,oh,error_kind,job_id))
                self._record(job_id,target,agent_id=agent_id,completed_at=now,runtime_seconds=seconds,output_hash=oh,error_kind=error_kind)
        return self.status(job_id)

    @audit_rejections
    def complete(self,job_id,request_hash,agent_id,output):
        return self._finish(job_id,request_hash,agent_id,output=output)

    @audit_rejections
    def fail(self,job_id,request_hash,agent_id,error_kind):
        return self._finish(job_id,request_hash,agent_id,error_kind=error_kind)

    @audit_rejections
    def ingest_evidence(self,job_id,request_hash,agent_id,manifest):
        """Driver-supplied evidence, NOT automatic tool attestation.

        driver_observed timestamps mean the caller asserts seeing the tool event.
        Only ingested_at is measured here. Agent declarations never become
        measured observations. No raw tool content, prompts or URLs with queries.
        """
        from .native_urls import public_source_url as _public_url
        required={'manifest_id','driver_id','entries'}
        if not isinstance(manifest,dict) or set(manifest)!=required:
            raise NativeBridgeError('Invalid evidence manifest')
        identifier(manifest['manifest_id']);identifier(manifest['driver_id']);identifier(agent_id)
        entries=manifest['entries']
        if not isinstance(entries,list) or not 1<=len(entries)<=500:
            raise NativeBridgeError('Bounded evidence entries required')
        now=utc_now();now_dt=datetime.fromisoformat(now.replace('Z','+00:00'))
        refs=set()
        for entry in entries:
            if not isinstance(entry,dict) or set(entry)!={'tool_ref','tool_name','operation','url','basis','started_at','observed_at','tool_result_sha256'}:
                raise NativeBridgeError('Invalid evidence entry fields')
            identifier(entry['tool_ref']);identifier(entry['tool_name'])
            if entry['operation'] not in ('open','open_failed','open_unknown','search','other'):raise NativeBridgeError('Invalid tool operation')
            if entry['tool_ref'] in refs:raise NativeBridgeError('Duplicate evidence reference')
            refs.add(entry['tool_ref'])
            if _public_url(entry['url'])!=entry['url'] or entry['url'] is None:
                raise NativeBridgeError('Unsafe evidence URL')
            if entry['basis'] not in ('driver_observed','agent_declared'):
                raise NativeBridgeError('Unsupported evidence basis')
            timestamp=entry['observed_at']
            if entry['basis']=='agent_declared':
                if any(entry[k] is not None for k in ('started_at','observed_at','tool_result_sha256')):raise NativeBridgeError('Agent declarations cannot supply measured evidence')
            else:
                if not isinstance(timestamp,str):raise NativeBridgeError('Driver observation timestamp required')
                observed=datetime.fromisoformat(timestamp.replace('Z','+00:00'))
                start=entry['started_at']
                rh=entry['tool_result_sha256']
                if not isinstance(start,str) or not isinstance(rh,str) or not re.fullmatch('[0-9a-f]{64}',rh):
                    raise NativeBridgeError('Driver wrapper start and original result hash required')
                began=datetime.fromisoformat(start.replace('Z','+00:00'))
                if observed.tzinfo is None or began.tzinfo is None or observed>now_dt or began>observed:
                    raise NativeBridgeError('Invalid observation timestamp')
        ph=digest(manifest)
        with self._transaction():
            row,_=self._row(job_id)
            if row['request_hash']!=request_hash or row['agent_id']!=agent_id:
                raise NativeBridgeError('Evidence claim identity mismatch')
            if row['state'] not in ('claimed','completed'):
                raise NativeBridgeError('Evidence requires an active or completed claim')
            old=self.db.execute('SELECT payload_hash FROM evidence WHERE job_id=? AND manifest_id=?',(job_id,manifest['manifest_id'])).fetchone()
            if old and old['payload_hash']!=ph:raise NativeBridgeError('Immutable evidence identity conflict')
            if not old:
                self.db.execute('INSERT INTO evidence VALUES(?,?,?,?,?)',(job_id,manifest['manifest_id'],canonical(manifest),ph,now))
                self._record(job_id,'evidence_ingested',agent_id=agent_id,driver_id=manifest['driver_id'],
                    manifest_id=manifest['manifest_id'],manifest_hash=ph,entry_count=len(entries),
                    driver_observed_count=sum(e['basis']=='driver_observed' for e in entries),
                    agent_declared_count=sum(e['basis']=='agent_declared' for e in entries),
                    ingested_at=now,automatic_tool_attestation=False)
        return self.evidence(job_id,manifest['manifest_id'])

    def evidence(self,job_id,manifest_id=None):
        verify_private_path(self.root);self._row(job_id)
        if manifest_id is None:
            flattened=[]
            for item in self.db.execute('SELECT manifest_id FROM evidence WHERE job_id=? ORDER BY ingested_at,manifest_id',(job_id,)).fetchall():
                record=self.evidence(job_id,item['manifest_id'])
                for entry in record['manifest']['entries']:
                    flattened.append({**entry,'driver_id':record['manifest']['driver_id'],
                        'manifest_id':item['manifest_id'],'manifest_hash':record['manifest_hash'],
                        'ingested_at':record['ingested_at'],'automatic_tool_attestation':False,
                        'timestamp_basis':entry['basis']})
            return flattened
        identifier(manifest_id)
        row=self.db.execute('SELECT * FROM evidence WHERE job_id=? AND manifest_id=?',(job_id,manifest_id)).fetchone()
        if row is None:raise NativeBridgeError('Unknown evidence manifest')
        payload=json.loads(row['payload'])
        if digest(payload)!=row['payload_hash']:raise NativeBridgeError('Evidence hash mismatch')
        return {'manifest':payload,'manifest_hash':row['payload_hash'],'ingested_at':row['ingested_at'],
                'automatic_tool_attestation':False,'timestamp_basis':'driver_assertion_except_bridge_ingested_at'}

    def status(self,job_id):
        verify_private_path(self.root)
        row,req=self._row(job_id)
        if row['state']=='completed':
            output=json.loads(row['output'])
            if digest(output)!=row['output_hash']:raise NativeBridgeError('Output hash mismatch')
            Draft202012Validator(req['schema']).validate(output)
        return {k:row[k] for k in ('id','request_hash','state','agent_id','queued_at','started_at','completed_at','output_hash','error_kind')} | dict(
            provider=PROVIDER,transport=TRANSPORT,usage=None,attempt=req['attempt'],
            queue_seconds=elapsed_seconds(row['queued_at'],row['started_at']),runtime_seconds=elapsed_seconds(row['started_at'],row['completed_at']))

    def result(self,job_id):
        status=self.status(job_id)
        if status['state']!='completed':raise NativeBridgeError('No completed result')
        row,_=self._row(job_id)
        return json.loads(row['output'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',required=True)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('queue');p.add_argument('--request-file',required=True)
    for name in ('claim','complete','fail','status','request','result','ingest_evidence','evidence'):
        p=sub.add_parser(name);p.add_argument('--job-id',required=True)
        if name in ('claim','complete','fail','ingest_evidence'):
            p.add_argument('--request-hash',required=True);p.add_argument('--agent-id',required=True)
        if name=='complete':p.add_argument('--output-file',required=True)
        if name=='ingest_evidence':p.add_argument('--manifest-file',required=True)
        if name=='evidence':p.add_argument('--manifest-id')
        if name=='fail':p.add_argument('--error-kind',required=True)
    args=vars(parser.parse_args());directory=args.pop('directory');command=args.pop('command')
    bridge=NativeBridge(directory)
    try:
        if command=='queue':args=json.loads(Path(args['request_file']).read_text(encoding='utf-8'))
        if command=='complete':args['output']=json.loads(Path(args.pop('output_file')).read_text(encoding='utf-8'))
        if command=='ingest_evidence':args['manifest']=json.loads(Path(args.pop('manifest_file')).read_text(encoding='utf-8'))
        print(canonical(getattr(bridge,command)(**args)))
    finally:bridge.close()

if __name__=='__main__':main()
