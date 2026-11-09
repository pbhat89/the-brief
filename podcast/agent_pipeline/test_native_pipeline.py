import json
import os
from . import audit as audit_module
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from .native_pipeline import NativePipeline
from .content import ROLES

class NativePipelineTests(unittest.TestCase):
    def setUp(self):
        if os.name == 'nt':
            acl={'current_sid':'test','owner_sid':'test','dacl_present':True,'aces':[{'sid':'test','type':'Allow'}]}
            mock=patch.object(audit_module,'inspect_windows_acl',return_value=acl)
            mock.start();self.addCleanup(mock.stop)
    def test_failed_attempt_is_not_successful_read(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        runner=object.__new__(NativePipeline)
        runner.bridge=SimpleNamespace(result=Mock(return_value={'sources':[{'url':'https://example.com/news','status':'accessible','notes':''}]}),evidence=Mock(return_value=[{'basis':'driver_observed','operation':'open_failed','tool_ref':'turn1view0','started_at':'2026-11-09T00:00:00Z','observed_at':'2026-11-09T00:00:01Z','tool_result_sha256':'a'*64,'url':'https://example.com/news'}]))
        data,traces=runner._data({'id':'x','state':'completed'},True)
        self.assertEqual(data['sources'][0]['status'],'blocked')
        self.assertEqual(traces[0]['access_outcome'],'open_failed')
        self.assertEqual(traces[0]['timestamp_basis'],'driver_observed')
    def context(self,*args):
        return {'edition_date':'2026-11-09','missing_files':[],'required_source_ids':['weather'],'intake_events':[]}
    def test_queue_four_durable_and_resume_pending(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();repo=root/'repo';repo.mkdir();out=root/'private';out.mkdir(mode=0o700)
            with patch('podcast.agent_pipeline.native_pipeline.load_context',self.context):
                runner=NativePipeline(repo,out)
                try:
                    first=runner.run('2026-11-09','proof')
                    self.assertIn('__interrupt__',first)
                    self.assertEqual(runner.bridge.db.execute('SELECT count(*) FROM jobs').fetchone()[0],4)
                    second=runner.run('2026-11-09','proof',True)
                    self.assertIn('__interrupt__',second)
                    third=runner.run('2026-11-09','proof',True)
                    self.assertIn('__interrupt__',third)
                    self.assertEqual(runner.bridge.db.execute('SELECT count(*) FROM jobs').fetchone()[0],4)
                    runner.runtime_hash='f'*64
                    with self.assertRaises(ValueError):runner.run('2026-11-09','proof',True)
                finally:runner.bridge.close();runner.audit.close()
    def test_completed_jobs_without_driver_evidence_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();repo=root/'repo';repo.mkdir();out=root/'private';out.mkdir(mode=0o700)
            with patch('podcast.agent_pipeline.native_pipeline.load_context',self.context):
                runner=NativePipeline(repo,out)
                try:
                    runner.run('2026-11-09','proof')
                    for row in runner.bridge.db.execute('SELECT id FROM jobs').fetchall():
                        request=runner.bridge.request(row['id']); role=request['request']['role'].rsplit('_',1)[0]
                        runner.bridge.claim(row['id'],request['request_hash'],'test-worker-'+role)
                        runner.bridge.complete(row['id'],request['request_hash'],'test-worker-'+role,
                            {'role':role,'stories':[],'sources':[],'gaps':['Synthetic unit test, not researched']})
                    with self.assertRaisesRegex(RuntimeError,'measured driver'):
                        runner.run('2026-11-09','proof',True)
                finally:runner.bridge.close();runner.audit.close()

    def test_unsorted_nested_context_survives_new_runner_resume(self):
        context={'edition_date':'2026-11-09','policies':{'z_last':{'z':1,'a':2},'a_first':'policy'},
                 'required_source_ids':['weather'],'missing_files':[],
                 'private_comparison_references':{'original':{'text':'same-day baseline','sha256':'a'*64}},
                 'intake_events':[]}
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();repo=root/'repo';repo.mkdir();out=root/'private';out.mkdir(mode=0o700)
            with patch('podcast.agent_pipeline.native_pipeline.load_context',return_value=context):
                runner=NativePipeline(repo,out)
                try:
                    runner.run('2026-11-09','ordered-proof')
                    for row in runner.bridge.db.execute('SELECT id FROM jobs').fetchall():
                        request=runner.bridge.request(row['id']);role=request['request']['role'].rsplit('_',1)[0]
                        agent='test-worker-'+role
                        runner.bridge.claim(row['id'],request['request_hash'],agent)
                        runner.bridge.complete(row['id'],request['request_hash'],agent,
                            {'role':role,'stories':[],'sources':[],'gaps':['Synthetic test only']})
                finally:runner.bridge.close();runner.audit.close()
                resumed=NativePipeline(repo,out)
                try:
                    # The expected evidence gate proves job identity matched after disk reload.
                    with self.assertRaisesRegex(RuntimeError,'measured driver'):
                        resumed.run('2026-11-09','ordered-proof',True)
                    self.assertEqual(resumed.bridge.db.execute('SELECT count(*) FROM jobs').fetchone()[0],4)
                finally:resumed.bridge.close();resumed.audit.close()

    def test_stage_failure_is_audited_without_exception_payload(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);repo=root/'repo';repo.mkdir();out=root/'out';out.mkdir(mode=0o700)
            runner=NativePipeline(repo,out)
            try:
                with patch('podcast.agent_pipeline.native_pipeline.load_context',self.context),patch.object(runner,'research',side_effect=ValueError('SECRET_PAYLOAD')),patch.object(runner.audit,'event',wraps=runner.audit.event) as event,patch.object(runner.audit,'finish_run',wraps=runner.audit.finish_run) as finish:
                    with self.assertRaises(ValueError):runner.run('2026-11-09','failure-test')
                    event.assert_any_call('failure-test','pipeline_failed',error_type='ValueError')
                    self.assertNotIn('SECRET_PAYLOAD',str(event.call_args_list))
                    self.assertEqual(finish.call_args.args,('failure-test','failed'))
            finally:runner.bridge.close();runner.audit.close()

    def test_native_evidence_not_invented(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();repo=root/'repo';repo.mkdir();out=root/'out';out.mkdir(mode=0o700)
            runner=NativePipeline(repo,out)
            try:
                with patch.object(runner.bridge,'result',return_value={}),patch.object(runner.bridge,'evidence',return_value=[]):
                    with self.assertRaises(RuntimeError):runner._data({'id':'x','state':'completed'},True)
            finally:runner.bridge.close();runner.audit.close()

class LineageTests(unittest.TestCase):
    setUp = NativePipelineTests.setUp
    def test_parent_identity_exact_and_read_only(self):
        from .native_pipeline import validate_parent_manifest,private_json
        from .pipeline import digest,context_digest
        context={'edition_date':'2026-11-09','intake_events':[]}
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'original.json'
            doc={'identity':{'run_id':'old','date':'2026-11-09','context_hash':context_digest(context),'runtime_source_hash':'a'*64},'context':context,'snapshot_hash':digest(context)}
            private_json(path,doc);before=path.read_bytes()
            lineage=validate_parent_manifest(path,edition_date='2026-11-09',context_hash=context_digest(context),run_id='new')
            self.assertEqual(path.read_bytes(),before)
            self.assertEqual(lineage['parent_run_id'],'old')
            self.assertTrue(lineage['new_agent_review_required'])
            for date,hash_,run in [('2026-11-10',context_digest(context),'new'),('2026-11-09','b'*64,'new'),('2026-11-09',context_digest(context),'old')]:
                with self.assertRaises(ValueError):validate_parent_manifest(path,edition_date=date,context_hash=hash_,run_id=run)

if __name__=='__main__':unittest.main()

class FullNativeGraphTests(unittest.TestCase):
    setUp=NativePipelineTests.setUp
    def test_synthetic_full_graph_and_seed_carry_forward(self, script_failures=0):
        from .test_content import story,edition
        from .native_pipeline import private_json
        from .pipeline import context_digest,digest
        context={'edition_date':'2026-11-08','missing_files':[],'required_source_ids':['weather'],'intake_events':[]}
        # Synthetic test evidence only; never a claim of an actual external fetch.
        evidence=[{'basis':'driver_observed','operation':'open','tool_ref':'synthetic-test-ref',
            'started_at':'2026-11-08T00:00:00Z','observed_at':'2026-11-08T00:00:01Z',
            'tool_result_sha256':'a'*64,'url':'https://example.org/story'}]
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);repo=root/'repo';repo.mkdir();out=root/'private';out.mkdir(mode=0o700)
            with patch('podcast.agent_pipeline.native_pipeline.load_context',return_value=context):
                runner=NativePipeline(repo,out)
                try:
                    state=runner.run('2026-11-08','synthetic')
                    seen=[]
                    with patch.object(runner.bridge,'evidence',return_value=evidence):
                        for _ in range(12):
                            jobs=runner.bridge.db.execute("SELECT id FROM jobs WHERE state='queued'").fetchall()
                            if not jobs:break
                            for row in jobs:
                                req=runner.bridge.request(row['id']);role=req['request']['role'].rsplit('_',1)[0];seen.append(role)
                                if role in ROLES:
                                    data={'role':role,'stories':[story('weather')] if role=='singapore' else [],'sources':[], 'gaps':['Synthetic bounded coverage']}
                                    if role=='singapore':data['sources']=[{'id':'weather','url':'https://example.org/story','attempted_at':None,'status':'partial','queries':[],'notes':'Synthetic test','trace_ids':[],'timestamp_basis':'unverified'}]
                                elif role=='editor':data=edition()
                                elif role=='checker' or role.startswith('script_checker'):
                                    failures=sum(r.startswith('script_checker') for r in seen)
                                    failed=role.startswith('script_checker') and failures<=script_failures
                                    data={'passed':not failed,'issues':[{'story_id':'one','reason':'Missing explicit replay label'}] if failed else [],'coverage_gaps':[]}
                                elif role.startswith('podcast'):data={'sections':[{'name':'Weather','text':'Test briefing','story_ids':['one']}],'word_count':2}
                                else:self.fail('Unexpected stage '+role)
                                runner.bridge.claim(row['id'],req['request_hash'],'synthetic-worker')
                                runner.bridge.complete(row['id'],req['request_hash'],'synthetic-worker',data)
                            if script_failures>=3 and seen[-1]=='script_checker_repair_2':
                                with patch.object(runner.audit,'event',wraps=runner.audit.event) as failure_event,patch.object(runner.audit,'finish_run',wraps=runner.audit.finish_run) as failure_finish:
                                    with self.assertRaisesRegex(ValueError,'two repair attempts'):
                                        runner.run('2026-11-08','synthetic',True)
                                    failure_event.assert_any_call('synthetic','pipeline_failed',error_type='ValueError')
                                    self.assertEqual(failure_finish.call_args.args,('synthetic','failed'))
                                self.assertFalse((out/'synthetic'/'script.json').exists())
                                self.assertTrue(runner.audit.verify_chain())
                                return
                            state=runner.run('2026-11-08','synthetic',True)
                    self.assertEqual(state['status'],'comparison_draft_release_blocked')
                    self.assertEqual(seen,list(ROLES)+['editor','checker','podcast','script_checker']+sum(([f'podcast_repair_{i}',f'script_checker_repair_{i}'] for i in range(1,min(script_failures,2)+1)),[]))
                    self.assertTrue(runner.audit.verify_chain())
                    seed={k:state[k] for k in ('run_id','date','context_hash','research')};seed['status']='research_ready'
                    seed_path=out/'seed.json';private_json(seed_path,seed)
                finally:runner.bridge.close();runner.audit.close()
                newout=root/'carry';newout.mkdir(mode=0o700)
                carried=NativePipeline(repo,newout,parent_manifest=out/'synthetic-native-manifest.json',seed_research=seed_path)
                try:
                    value=carried.run('2026-11-08','new-synthetic')
                    self.assertIn('__interrupt__',value)
                    jobs=carried.bridge.db.execute('SELECT request FROM jobs').fetchall()
                    self.assertEqual(len(jobs),1)
                    self.assertEqual(json.loads(jobs[0][0])['role'],'editor_0')
                    self.assertEqual(value['research'],state['research'])
                    self.assertEqual(carried.manifest['research_seed']['parent_run_id'],'synthetic')
                finally:carried.bridge.close();carried.audit.close()
                # A seed from another date fails before any new jobs are created.
                seed['date']='2026-11-09';bad=out/'bad-seed.json';private_json(bad,seed)
                badout=root/'bad';badout.mkdir(mode=0o700)
                invalid=NativePipeline(repo,badout,parent_manifest=out/'synthetic-native-manifest.json',seed_research=bad)
                try:
                    with self.assertRaisesRegex(ValueError,'seed identity'):invalid.run('2026-11-08','bad-synthetic')
                finally:invalid.bridge.close();invalid.audit.close()

    def test_synthetic_script_repair_full_graph(self):
        self.test_synthetic_full_graph_and_seed_carry_forward(script_failures=1)

    def test_synthetic_script_repair_exhaustion(self):
        self.test_synthetic_full_graph_and_seed_carry_forward(script_failures=3)


class NativeExitStatusTests(unittest.TestCase):
    def test_pending_and_complete(self):
        from .native_pipeline import exit_status
        self.assertEqual(exit_status({'status':'researching','__interrupt__':[{'value':{'jobs':[]}}]}),0)
        self.assertEqual(exit_status({'status':'comparison_ready','artifacts':{'audio':'private.mp3'}}),0)
    def test_terminal_blocked_failed_unknown(self):
        from .native_pipeline import exit_status
        for status in ('comparison_draft_release_blocked','written_ready_audio_blocked','research_blocked','editorial_blocked','failed','written_ready','unexpected',None):
            result={'run_id':'comparison-test','date':'2026-11-09','status':status,'artifacts':{'edition':'edition.json','html':'brief.html','script':'script.json'},'errors':[]}
            self.assertEqual(exit_status(result),2)
        self.assertEqual(exit_status({'__interrupt__':[]}),2)
        self.assertEqual(exit_status(None),2)
