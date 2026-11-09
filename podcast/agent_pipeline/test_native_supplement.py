import copy,json,tempfile,hashlib,os
from pathlib import Path
import unittest
from .native_capture import save_receipt
from .native_supplement import load_supplement,merge_supplement
from .test_content import story

class SupplementTests(unittest.TestCase):
    def setUp(self):
        # Synthetic orchestration fixture only; production ACL checks stay active.
        if os.name == 'nt':
            from unittest.mock import patch
            from . import audit as audit_module
            acl={'current_sid':'test','owner_sid':'test','dacl_present':True,'aces':[{'sid':'test','type':'Allow'}]}
            mock=patch.object(audit_module,'inspect_windows_acl',return_value=acl)
            mock.start();self.addCleanup(mock.stop)

    def test_verified_receipts_review_and_rejections(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);root.chmod(0o700)
            envelope={'request_url':'https://example.org/story','started_at':'2026-11-08T00:00:00Z','observed_at':'2026-11-08T00:00:01Z','tool_result':{'content':[{'type':'text','text':'【turnSyntheticview0】 Source: open({"ref_id":"https://example.org/story"}); Source passage'}]}}
            receipt=save_receipt(root,envelope);path=Path(receipt['receipt_file'])
            seed=[{'role':r,'stories':[],'sources':[],'gaps':[]} for r in ('india','singapore','world','ai_learning')]
            research={'role':'world','stories':[story()], 'sources':[{'id':'supplement-source','url':envelope['request_url'],'attempted_at':None,'status':'partial','queries':[],'notes':'Synthetic test only','trace_ids':[],'timestamp_basis':'unverified'}],'gaps':['Synthetic partial scope']}
            bundle={'edition_date':'2026-11-08','context_hash':'a'*64,'parent_run_id':'prior','researcher_id':'synthetic-worker','research':[research],'receipts':[{'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'tool_ref':'turnSyntheticview0','tool_name':'chat_search_web_run'}]}
            file=root/'bundle.json'
            def load(value):
                file.write_text(json.dumps(value));file.chmod(0o600)
                return load_supplement(file,date='2026-11-08',context_hash='a'*64,parent_run_id='prior',seed=seed)
            coverage=root/'coverage.json';coverage.write_text('{"status":"partial"}');coverage.chmod(0o600)
            bundle['coverage_artifact']={'path':str(coverage),'sha256':hashlib.sha256(coverage.read_bytes()).hexdigest()}
            supplement=load(bundle)
            self.assertFalse(supplement['identity']['coverage_artifact']['release_gate_passed'])
            bad=copy.deepcopy(bundle);bad['coverage_artifact']['sha256']='0'*64
            with self.assertRaises(ValueError):load(bad)
            self.assertEqual(supplement['research'][0]['sources'][0]['attempted_at'],envelope['observed_at'])
            self.assertIn('source_extracts',supplement)
            review={'passed':True,'accepted_story_ids':['one'],'issues':[]}
            merged=merge_supplement(seed,supplement,review)
            self.assertEqual(len(merged[2]['stories']),1);self.assertEqual(seed[2]['stories'],[])
            for bad_review in ({'passed':False,'accepted_story_ids':[],'issues':['unsupported']},{'passed':True,'accepted_story_ids':['invented'],'issues':[]}):
                with self.assertRaises(ValueError):merge_supplement(seed,supplement,bad_review)
            for field,value in [('edition_date','2026-11-09'),('context_hash','b'*64),('parent_run_id','other')]:
                bad=copy.deepcopy(bundle);bad[field]=value
                with self.assertRaises(ValueError):load(bad)
            bad=copy.deepcopy(bundle);bad['receipts'][0]['sha256']='0'*64
            with self.assertRaises(ValueError):load(bad)
            bad=copy.deepcopy(bundle);bad['receipts'][0]['tool_name']='browser'
            with self.assertRaises(ValueError):load(bad)
            # Even a declared chat tool cannot turn a browser/plain-body receipt into a web extract.
            plain=copy.deepcopy(envelope);plain['tool_result']['content'][0]['text']='turnSyntheticview0 Source passage'
            plain_receipt=save_receipt(root,plain);plain_path=Path(plain_receipt['receipt_file'])
            bad=copy.deepcopy(bundle);bad['receipts'][0].update(path=str(plain_path),sha256=hashlib.sha256(plain_path.read_bytes()).hexdigest())
            with self.assertRaises(ValueError):load(bad)
            bad=copy.deepcopy(bundle);bad['research'][0]['stories'][0]['evidence'][0]['quote']='invented quote'
            with self.assertRaises(ValueError):load(bad)
            bad=copy.deepcopy(bundle);bad['research'][0]['stories'][0]['sources']=['https://example.org/changed']
            with self.assertRaises(ValueError):load(bad)
            seed[2]['stories']=[story()]
            with self.assertRaises(ValueError):load(bundle)

    def test_real_native_queue_requires_review_before_editor(self):
        from unittest.mock import patch
        from .native_pipeline import NativePipeline,private_json
        from .pipeline import context_digest,digest
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);root.chmod(0o700);repo=root/'repo';repo.mkdir();out=root/'out';out.mkdir(mode=0o700)
            context={'edition_date':'2026-11-08','missing_files':[],'required_source_ids':['weather'],'intake_events':[]}
            seed={'run_id':'prior','date':'2026-11-08','context_hash':context_digest(context),'status':'research_ready','research':[{'role':r,'stories':[],'sources':[],'gaps':[]} for r in ('india','singapore','world','ai_learning')]}
            seed['research'][1]['stories']=[story('weather','weather-story')]
            seed['research'][1]['sources']=[{'id':'weather','url':'https://example.org/story','attempted_at':'2026-11-08T00:00:00Z','status':'partial','queries':[],'notes':'Synthetic','trace_ids':['fixture'],'timestamp_basis':'driver_observed'}]
            parent=root/'parent.json';private_json(parent,{'identity':{'run_id':'prior','date':'2026-11-08','context_hash':context_digest(context),'runtime_source_hash':'f'*64},'context':context,'snapshot_hash':digest(context)})
            seed_path=root/'seed.json';private_json(seed_path,seed)
            receipt=save_receipt(root,{'request_url':'https://example.org/story','started_at':'2026-11-08T00:00:00Z','observed_at':'2026-11-08T00:00:01Z','tool_result':{'content':[{'type':'text','text':'【turnSyntheticview0】 Source: open({"ref_id":"https://example.org/story"}); Source passage'}]}})
            f=Path(receipt['receipt_file'])
            supplement=root/'supplement.json';private_json(supplement,{'edition_date':'2026-11-08','context_hash':context_digest(context),'parent_run_id':'prior','researcher_id':'synthetic-worker','research':[{'role':'world','stories':[story('news','addition'),story('news','rejected-addition')],'sources':[{'id':'supplement-source','url':'https://example.org/story','attempted_at':None,'status':'partial','queries':[],'notes':'Synthetic','trace_ids':[],'timestamp_basis':'unverified'}],'gaps':['Not complete']}],'receipts':[{'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'tool_ref':'turnSyntheticview0','tool_name':'chat_search_web_run'}]})
            # Realistic large coverage ledger must stay out of the native prompt.
            large=root/'large-coverage.json'
            private_json(large,{'edition_date':'2026-11-08','agreed_source_coverage_status':'partial','sources':[{'pending_history':'DO_NOT_EMBED_RAW_COVERAGE'+('x'*1100000)}]})
            bundle=json.loads(supplement.read_text())
            bundle['coverage_artifact']={'path':str(large),'sha256':hashlib.sha256(large.read_bytes()).hexdigest()}
            supplement.write_text(json.dumps(bundle))
            with patch('podcast.agent_pipeline.native_pipeline.load_context',return_value=context):
                runner=NativePipeline(repo,out,parent_manifest=parent,seed_research=seed_path,research_supplement=supplement)
                try:
                    state=runner.run('2026-11-08','new')
                    jobs=runner.bridge.db.execute('SELECT id FROM jobs').fetchall();self.assertEqual(len(jobs),1)
                    req=runner.bridge.request(jobs[0]['id']);self.assertEqual(req['request']['role'],'supplemental_review_0')
                    self.assertLess(len(req['request']['prompt']),1000000)
                    self.assertNotIn('DO_NOT_EMBED_RAW_COVERAGE',req['request']['prompt'])
                    self.assertIn('coverage_summary',req['request']['prompt'])
                    self.assertIn(hashlib.sha256(large.read_bytes()).hexdigest(),req['request']['prompt'])
                    runner.bridge.claim(jobs[0]['id'],req['request_hash'],'actual-synthetic-review-worker')
                    runner.bridge.complete(jobs[0]['id'],req['request_hash'],'actual-synthetic-review-worker',{'passed':True,'accepted_story_ids':['addition'],'issues':[]})
                    state=runner.run('2026-11-08','new',True)
                    self.assertEqual(state['research'][2]['stories'][0]['id'],'addition')
                    queued=runner.bridge.db.execute("SELECT request FROM jobs WHERE state='queued'").fetchall()
                    self.assertEqual(json.loads(queued[0][0])['role'],'editor_0')
                    self.assertIn('research_supplement',runner.manifest)
                    audit_events=runner.audit.events('new')
                    self.assertTrue(any('supplement_story_disposition' in str(e) and 'rejected-addition' in str(e) and 'rejected' in str(e) for e in audit_events))
                finally:runner.bridge.close();runner.audit.close()
