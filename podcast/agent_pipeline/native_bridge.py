"""Private durable handoff, NOT a standalone native-agent spawning API.

An assistant driver must actually spawn an agent, then supply its returned ID.
No subscription attribution, model token estimates, raw audit prompts or API keys.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from contextlib import contextmanager
from jsonschema import Draft202012Validator
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

    def _row(self,job_id):
        row=self.db.execute('SELECT * FROM jobs WHERE id=?',(identifier(job_id),)).fetchone()
        if row is None:raise NativeBridgeError('Unknown job')
        try:request=json.loads(row['request'])
        except ValueError:raise NativeBridgeError('Request corruption') from None
        if digest(request)!=row['request_hash']:raise NativeBridgeError('Request hash mismatch')
        return row,request

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

    def complete(self,job_id,request_hash,agent_id,output):
        return self._finish(job_id,request_hash,agent_id,output=output)

    def fail(self,job_id,request_hash,agent_id,error_kind):
        return self._finish(job_id,request_hash,agent_id,error_kind=error_kind)

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
    for name in ('claim','complete','fail','status','request','result'):
        p=sub.add_parser(name);p.add_argument('--job-id',required=True)
        if name in ('claim','complete','fail'):
            p.add_argument('--request-hash',required=True);p.add_argument('--agent-id',required=True)
        if name=='complete':p.add_argument('--output-file',required=True)
        if name=='fail':p.add_argument('--error-kind',required=True)
    args=vars(parser.parse_args());directory=args.pop('directory');command=args.pop('command')
    bridge=NativeBridge(directory)
    try:
        if command=='queue':args=json.loads(Path(args['request_file']).read_text(encoding='utf-8'))
        if command=='complete':args['output']=json.loads(Path(args.pop('output_file')).read_text(encoding='utf-8'))
        print(canonical(getattr(bridge,command)(**args)))
    finally:bridge.close()

if __name__=='__main__':main()
