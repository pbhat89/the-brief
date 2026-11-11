"""LangGraph orchestration; no API billing, implicit publishing or fabricated success."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
from datetime import datetime, timezone
from typing import TypedDict
from concurrent.futures import ThreadPoolExecutor
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .audit import AuditStore, verify_private_path
from .checkpoint_store import CheckpointStore, CheckpointKey
from .bridges import validate_editorial
from .source_repair import REPAIR_SCHEMA, repair_targets, repair_prompt, merge_source_repair, validate_repair_origin
from .codex_adapter import CodexAdapter
from .content import (ROLES, RESEARCH_SCHEMA, EDITION_SCHEMA, CHECK_SCHEMA, EDITORIAL_CHECK_SCHEMA, PODCAST_SCHEMA,
    verify_editorial_review, script_checker_prompt,
    load_context, research_prompt, editor_prompt, checker_prompt, podcast_prompt,
    render_html, verify_edition, all_stories, verify_research, verify_edition_provenance, verify_script, reconcile_source_traces)


def now(): return datetime.now(timezone.utc).isoformat()
def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
def context_digest(value):
    # Observation time changes on every read; source contents/hashes remain bound.
    return digest({k:v for k,v in value.items() if k!='intake_events'})

class State(TypedDict, total=False):
    run_id: str
    date: str
    context_hash: str
    research: list
    edition: dict
    checks: dict
    script: dict
    repair_round: int
    status: str
    errors: list
    artifacts: dict

class Pipeline:
    def __init__(self, repo, output, adapter=None, concurrency=3, hooks=None, repair_from=None):
        self.repo=Path(repo).resolve(); self.output=Path(output).resolve()
        if self.output==self.repo or self.repo in self.output.parents:
            raise ValueError('Private runtime output must be outside repository')
        self.output.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.adapter=adapter or CodexAdapter(); self.concurrency=min(max(concurrency,1),4)
        self.hooks=hooks or {}; self.context={}; self.audit=AuditStore(self.output/'audit.sqlite3')
        cache=self.output/'agent-checkpoints';cache.mkdir(exist_ok=True,mode=0o700)
        self.agent_cache=CheckpointStore(cache,privacy_verifier=lambda p:(verify_private_path(p),True)[1])
        self.repair_previous=None;self.repair_input_hash=None
        if repair_from is not None:
            path=Path(repair_from).resolve();verify_private_path(path)
            raw=path.read_bytes();self.repair_previous=json.loads(raw);self.repair_input_hash=hashlib.sha256(raw).hexdigest()
        self.runtime_hash=digest({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')})
    def invoke_agent(self,state,role,prompt,schema,search=False,with_trace=False):
        started=now(); aid=f'{state["run_id"]}:{role}:{state.get("repair_round",0)}'
        observed_ids=set()
        key=CheckpointKey(state['run_id'],role+'_'+str(state.get('repair_round',0)),state['date'],state['context_hash'],digest(prompt),digest(schema),self.runtime_hash)
        try:
            cached=self.agent_cache.load(key)
            if cached is not None:
                self.audit.record_attempt(state['run_id'],role,attempt_id=aid,status='reused',checkpoint_hash=cached['payload_hash'],input_hash=digest(prompt),usage=None)
                if role in ROLES: return reconcile_source_traces(cached['result'],cached['tool_trace'],self.context.get('intake_events',()))
                return (cached['result'],cached['tool_trace']) if with_trace else cached['result']
            def trace(event):
                if event.get('event')=='tool_observation':
                    observation=event['observation']
                    self.audit.event(state['run_id'],'tool_observation',agent_id=role,**observation)
                    observed_ids.add(observation['trace_id'])
                    return
                self.audit.record_attempt(state['run_id'],role,attempt_id=f'{aid}:try-{event.get("attempt",0)}',**event)
                self.audit.event(state['run_id'],'codex_attempt',agent_id=role,parent_attempt_id=aid,**event)
            result=self.adapter.run(prompt,schema,cwd=str(self.output),require_search=search,on_attempt=trace)
            checkpoint_hash=self.agent_cache.save(key,result.data,list(getattr(result,'tool_trace',())))
            self.audit.record_checkpoint(state['run_id'],role+'_result',status='saved',payload_hash=checkpoint_hash,runtime_source_hash=self.runtime_hash)
            self.audit.record_attempt(state['run_id'],role,attempt_id=aid,started_at=started,ended_at=now(),status='success',input_hash=digest(prompt),output_hash=digest(result.data),usage=result.usage)
            traces=getattr(result,'tool_trace',())
            for observation in traces:
                if observation.get('trace_id') in observed_ids: continue
                self.audit.event(state['run_id'],'tool_observation',agent_id=role,**observation)
            if role in ROLES:
                return reconcile_source_traces(result.data,traces,self.context.get('intake_events',()))
            return (result.data,traces) if with_trace else result.data
        except Exception as exc:
            for observation in getattr(exc,'tool_trace',()):
                if observation.get('trace_id') in observed_ids: continue
                self.audit.event(state['run_id'],'tool_observation',agent_id=role,**observation)
            self.audit.record_attempt(state['run_id'],role,attempt_id=aid,started_at=started,ended_at=now(),status='failed',error_type=getattr(exc,'kind',type(exc).__name__),error=str(exc)[:500])
            raise
    def readiness(self,s):
        self.context=load_context(self.repo,s['date'])
        current=context_digest(self.context)
        if s.get('context_hash') and s['context_hash']!=current: raise ValueError('Resume inputs changed; use new run ID')
        self.audit.start_run(s['run_id'],edition_date=s['date'],started_at=now(),mode='comparison',context_hash=current,runtime_source_hash=self.runtime_hash)
        if self.repair_previous is not None:
            validate_repair_origin(self.repair_previous,edition_date=s['date'],context_hash=current,new_run_id=s['run_id'])
            self.audit.event(s['run_id'],'repair_origin',parent_run_id=self.repair_previous['run_id'],input_sha256=self.repair_input_hash)
        if self.context.get('missing_files'): raise ValueError('Required policy/history files missing: '+','.join(self.context['missing_files']))
        for observation in self.context.get('intake_events',()):
            self.audit.event(s['run_id'],'local_intake',**observation)
        self.audit.record_checkpoint(s['run_id'], 'readiness',status='passed',checks=['private output path','policy context loaded'])
        return {'context_hash':current,'repair_round':0,'status':'researching','errors':[]}
    def research(self,s):
        if self.repair_previous is not None: return self.repair_research(s)
        def run(role):
            try:
                result=self.invoke_agent(s,role,research_prompt(role,{k:v for k,v in self.context.items() if k!='intake_events'}),RESEARCH_SCHEMA,True)
                for source in result.get('sources',[]):
                    data=dict(source); source_id=data.pop('id',None)
                    self.audit.record_source(s['run_id'],source_id,**data)
                for story in result.get('stories',[]):
                    self.audit.record_claim(s['run_id'],story['id'],event_id=story['event_id'],source_ids=story['sources'],claim=story['summary'])
                    for n,evidence in enumerate(story.get('evidence',[])):
                        self.audit.record_evidence(s['run_id'],f'{story["id"]}-{n}',claim_id=story['id'],**evidence)
                return result
            except Exception as exc: return {'role':role,'stories':[],'sources':[],'gaps':[f'{role} blocked: {type(exc).__name__}']}
        with ThreadPoolExecutor(max_workers=self.concurrency) as pool: results=list(pool.map(run,ROLES))
        issues=verify_research(results,self.context)
        self.audit.record_checkpoint(s['run_id'],'coverage',status='failed' if issues else 'passed',errors=issues)
        return {'research':results,'errors':issues,'status':'research_ready' if not issues and any(x.get('stories') for x in results) else 'research_blocked'}
    def repair_research(self,s):
        previous=self.repair_previous
        targets=repair_targets(previous['research'],required_source_ids=self.context.get('required_source_ids',()))
        owners={}
        for role in previous['research']:
            for row in role.get('sources',[]): owners.setdefault((row.get('id'),row.get('url')),role['role'])
        groups={role:[t for t in targets if owners[(t['source_id'],t['url'])]==role] for role in ROLES}
        def repair(role):
            if not groups[role]: return {'sources':[]},[]
            try:
                return self.invoke_agent(s,'evidence_repair_'+role,repair_prompt(groups[role]),REPAIR_SCHEMA,True,with_trace=True)
            except Exception as exc:
                self.audit.event(s['run_id'],'evidence_repair_blocked',agent_id=role,error_type=type(exc).__name__)
                return {'sources':[]},[]
        with ThreadPoolExecutor(max_workers=self.concurrency) as pool: responses=list(pool.map(repair,ROLES))
        update={'sources':[row for data,_ in responses for row in data['sources']]}
        traces=[t for _,items in responses for t in items]
        repaired=merge_source_repair(previous,update,traces,targets=targets,edition_date=s['date'],context_hash=s['context_hash'],new_run_id=s['run_id'],intake_events=self.context.get('intake_events',()))
        results=repaired['research']
        for role in results:
            for source in role.get('sources',[]):
                data=dict(source);sid=data.pop('id');self.audit.record_source(s['run_id'],sid,**data)
            for story in role.get('stories',[]):
                self.audit.record_claim(s['run_id'],story['id'],event_id=story['event_id'],source_ids=story['sources'],claim=story['summary'],carried_from_run=previous['run_id'])
                for n,evidence in enumerate(story.get('evidence',[])):
                    self.audit.record_evidence(s['run_id'],f"{story['id']}-{n}",claim_id=story['id'],carried_from_run=previous['run_id'],**evidence)
        issues=verify_research(results,self.context)
        self.audit.record_checkpoint(s['run_id'],'coverage_repair',status='failed' if issues else 'passed',errors=issues,**repaired['repair_evidence'])
        return {'research':results,'errors':issues,'status':'research_ready' if not issues else 'research_blocked'}
    def edit(self,s):
        edition=self.invoke_agent(s,'editor',editor_prompt(s['research'],self.context),EDITION_SCHEMA)
        return {'edition':edition}
    def check(self,s):
        errors=verify_edition(s['edition'],s['date'])+verify_edition_provenance(s['edition'],s['research'])
        if not any(r.get('stories') for r in s['research']): errors.append('All research roles returned no supported stories')
        review=self.invoke_agent(s,'checker',checker_prompt(s['edition'],self.context,s['research']),EDITORIAL_CHECK_SCHEMA,True)
        errors.extend(verify_editorial_review(review,s['edition']))
        errors.extend(i.get('reason','failed check') for i in review.get('issues',[]))
        if review.get('coverage_gaps') and s['edition'].get('coverage_status')!='partial': errors.append('Checker identified undisclosed coverage gaps')
        passed=not errors and review.get('passed') is True
        self.audit.record_checkpoint(s['run_id'],f'editorial-{s.get("repair_round",0)}',status='passed' if passed else 'failed',errors=errors)
        return {'checks':review,'errors':errors,'status':'approved' if passed else 'repair'}
    def repair(self,s):
        context={**self.context,'repair_issues':s['errors'],'previous_edition':s['edition']}
        edition=self.invoke_agent(s,'editor_repair',editor_prompt(s['research'],context),EDITION_SCHEMA)
        return {'edition':edition,'repair_round':s.get('repair_round',0)+1}
    def render(self,s):
        script=None
        issues=[]
        for attempt in range(3):
            role='podcast' if attempt==0 else 'podcast_repair_'+str(attempt)
            prompt=podcast_prompt(s['edition'])
            if attempt:
                prompt+='\nRepair only the spoken script against the unchanged locked edition. Preserve factual identities and coverage disclosures. '+json.dumps({'prior_issues':issues,'previous_script':script})
            script=self.invoke_agent(s,role,prompt,PODCAST_SCHEMA)
            script_errors=verify_script(script,s['edition'])
            check_role='script_checker' if attempt==0 else 'script_checker_repair_'+str(attempt)
            review=self.invoke_agent(s,check_role,script_checker_prompt(s['edition'],script),EDITORIAL_CHECK_SCHEMA)
            issues=script_errors+verify_editorial_review(review,s['edition'])+[item.get('reason','Narration fidelity issue') for item in review.get('issues',[])]
            if not review.get('passed') and not issues:issues=['Narration fidelity check failed']
            self.audit.record_checkpoint(s['run_id'],'script-quality-'+str(attempt),status='failed' if issues else 'passed',errors=issues)
            if not issues:break
        else:
            raise ValueError('Narration fidelity check failed after two repair attempts')
        allowed={x['id'] for x in all_stories(s['edition'])}
        if any(set(section['story_ids'])-allowed for section in script['sections']): raise ValueError('Podcast references an unapproved story')
        self.audit.record_checkpoint(s['run_id'],'edition_lock',status='passed',edition_hash=digest(s['edition']))
        folder=self.output/s['run_id']; folder.mkdir(exist_ok=True)
        paths={'edition':folder/'edition.json','html':folder/'brief.html','script':folder/'script.json'}
        paths['edition'].write_text(json.dumps(s['edition'],ensure_ascii=False,indent=2))
        paths['html'].write_text(render_html(s['edition']))
        paths['script'].write_text(json.dumps(script,ensure_ascii=False,indent=2))
        artifacts={}
        for kind,path in paths.items():
            h=hashlib.sha256(path.read_bytes()).hexdigest(); artifacts[kind]=str(path)
            self.audit.record_artifact(s['run_id'],kind,path=str(path),sha256=h,status='created')
        return {'script':script,'artifacts':artifacts,'status':'written_ready'}
    def audio(self,s):
        audit_path=self.hooks.get('editorial_audit')
        if not audit_path:
            self.audit.record_checkpoint(s['run_id'],'release_gate',status='blocked',reason='Existing editorial/source-coverage audit required')
            return {'status':'comparison_draft_release_blocked'}
        validate_editorial(self.repo,audit_path)
        # Existing approved renderer is supplied by the private runner, never public voice data.
        hook=self.hooks.get('audio')
        if not hook:
            self.audit.record_checkpoint(s['run_id'],'audio',status='blocked',reason='Approved private voice runner not configured')
            return {'status':'written_ready_audio_blocked'}
        receipt=self.run_hook(hook,s,'audio')
        if receipt.get('qa_passed') is not True or not receipt.get('approved_voice'):
            raise ValueError('Audio hook failed approved-voice/QA gate')
        p=Path(receipt['path']).resolve()
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=receipt.get('sha256'): raise ValueError('Audio bytes/hash mismatch')
        self.audit.record_artifact(s['run_id'],'audio',**receipt)
        return {'artifacts':{**s['artifacts'],'audio':str(p)},'status':'comparison_ready'}
    def run_hook(self,command,s,kind):
        if not isinstance(command,list) or not command: raise ValueError('Hook must be argv list')
        p=subprocess.run(command,input=json.dumps(s),text=True,capture_output=True,timeout=900,cwd=self.output,check=True)
        receipt=json.loads(p.stdout)
        self.audit.record_checkpoint(s['run_id'],kind,status='passed' if receipt.get('qa_passed') else 'failed')
        return receipt
    def finish(self,s):
        status=s.get('status','failed')
        if status=='repair': status='editorial_blocked'
        self.audit.finish_run(s['run_id'],status,ended_at=now())
        self.audit.export_xlsx(self.output/f'{s["run_id"]}-metalog.xlsx')
        return {'status':status}
    def graph(self,checkpointer):
        g=StateGraph(State)
        for name in ('readiness','research','edit','check','repair','render','audio','finish'): g.add_node(name,getattr(self,name))
        g.add_edge(START,'readiness');g.add_edge('readiness','research');g.add_conditional_edges('research',lambda s:'edit' if s['status']=='research_ready' else 'finish');g.add_edge('edit','check')
        g.add_conditional_edges('check',lambda s:'render' if s['status']=='approved' else ('repair' if s.get('repair_round',0)<2 else 'finish'))
        g.add_edge('repair','check');g.add_edge('render','audio');g.add_edge('audio','finish');g.add_edge('finish',END)
        return g.compile(checkpointer=checkpointer)
    def run(self,date,run_id,resume=False):
        if not run_id.replace('-','').replace('_','').isalnum(): raise ValueError('Unsafe run ID')
        config={'configurable':{'thread_id':run_id}}
        self.context=load_context(self.repo,date)
        with SqliteSaver.from_conn_string(str(self.output/'checkpoints.sqlite3')) as cp:
            graph=self.graph(cp); snapshot=graph.get_state(config)
            if snapshot.values and not resume: raise ValueError('Run exists; explicitly resume or choose new run ID')
            if resume:
                if not snapshot.values: raise ValueError('No saved run')
                if snapshot.values.get('date')!=date or snapshot.values.get('context_hash')!=context_digest(self.context): raise ValueError('Resume context changed')
            try: return graph.invoke(None if resume else {'run_id':run_id,'date':date},config)
            except Exception as exc:
                self.audit.event(run_id,'pipeline_failed',error_type=type(exc).__name__,error=str(exc)[:500])
                self.audit.finish_run(run_id,'failed',ended_at=now())
                self.audit.export_xlsx(self.output/f'{run_id}-metalog.xlsx')
                raise

def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--output',required=True);p.add_argument('--date',required=True);p.add_argument('--run-id',required=True);p.add_argument('--resume',action='store_true');p.add_argument('--hooks',help='Private JSON mapping audio argv; never secrets');p.add_argument('--repair-from',help='Private research_blocked result from same edition/context; requires new run ID');p.add_argument('--codex-executable',default='codex',help='Native Codex executable; on Windows use codex.exe, not a batch shim')
    a=p.parse_args(); hooks=json.loads(Path(a.hooks).read_text(encoding='utf-8')) if a.hooks else {}
    pipeline=Pipeline(a.repo,a.output,adapter=CodexAdapter(executable=a.codex_executable),hooks=hooks,repair_from=a.repair_from)
    try: result=pipeline.run(a.date,a.run_id,a.resume)
    finally: pipeline.audit.close()
    print(json.dumps(result,ensure_ascii=False))
    if result.get('status')!='comparison_ready': raise SystemExit(2)
if __name__=='__main__': main()
