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
