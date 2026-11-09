import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
from podcast.agent_pipeline.checkpoint_store import CheckpointKey, CheckpointStore, CheckpointError

class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name).resolve()
        # Unit-test verifier, not a claim about deployment ACLs.
        self.store = CheckpointStore(self.folder, privacy_verifier=lambda p: True)
        self.key = CheckpointKey('run1','india','2026-11-09', *['a'*64]*4)
        self.result = {'items':[{'headline':'Public news'}]}
        self.trace = [{'event':'attempt_finished','status':'succeeded','attempt':1,'usage':{'input_tokens':10},'search_count':2}]

    def test_roundtrip(self):
        digest = self.store.save(self.key,self.result,self.trace)
        loaded = self.store.load(self.key)
        self.assertEqual(loaded,dict(result=self.result,tool_trace=self.trace,payload_hash=digest))
        self.assertEqual(len(list(self.folder.iterdir())),1)

    def test_missing_or_any_changed_input_never_reused(self):
        self.store.save(self.key,self.result,self.trace)
        for field in ('context_hash','prompt_hash','schema_hash','runtime_source_hash'):
            self.assertIsNone(self.store.load(replace(self.key,**{field:'b'*64})))
        for field,value in [('run_id','run2'),('role','ai'),('edition_date','2026-11-10')]:
            self.assertIsNone(self.store.load(replace(self.key,**{field:value})))

    def test_immutable_and_idempotent(self):
        digest=self.store.save(self.key,self.result,self.trace)
        self.assertEqual(self.store.save(self.key,self.result,self.trace),digest)
        with self.assertRaises(CheckpointError):self.store.save(self.key,{'different':True},self.trace)
        self.assertEqual(self.store.load(self.key)['result'],self.result)

    def test_tampering_fails_closed(self):
        self.store.save(self.key,self.result,self.trace)
        path=next(self.folder.glob('*.json'))
        data=json.loads(path.read_text());data['payload']['result']={'tampered':True}
        path.write_text(json.dumps(data))
        with self.assertRaises(CheckpointError):self.store.load(self.key)

    def test_wrong_identity_fails(self):
        self.store.save(self.key,self.result,self.trace)
        path=next(self.folder.glob('*.json'))
        data=json.loads(path.read_text());data['key']['run_id']='other'
        path.write_text(json.dumps(data))
        with self.assertRaises(CheckpointError):self.store.load(self.key)

    def test_private_directory_required_and_rechecked(self):
        with self.assertRaises(CheckpointError):CheckpointStore(self.folder,lambda p:False)
        self.store.verify_private=lambda p:False
        with self.assertRaises(CheckpointError):self.store.save(self.key,self.result,self.trace)
        with self.assertRaises(CheckpointError):self.store.load(self.key)

    def test_raw_trace_fields_rejected(self):
        for field in ('prompt','query','raw_error','api_key','result'):
            with self.assertRaises(ValueError):self.store.save(self.key,self.result,[{field:'secret'}])
        self.assertEqual(list(self.folder.iterdir()),[])

    def test_failed_publish_leaves_no_checkpoint_or_temp(self):
        with patch('podcast.agent_pipeline.checkpoint_store.os.link',side_effect=OSError('unsupported')):
            with self.assertRaises(CheckpointError):self.store.save(self.key,self.result,self.trace)
        self.assertIsNone(self.store.load(self.key))
        self.assertEqual(list(self.folder.iterdir()),[])

    def test_interrupted_temp_is_not_resume_evidence(self):
        (self.folder/'.checkpoint-incomplete').write_text('partial')
        self.assertIsNone(self.store.load(self.key))

    def test_bad_inputs_rejected(self):
        with self.assertRaises(ValueError):replace(self.key,role='../escape')
        with self.assertRaises(ValueError):replace(self.key,prompt_hash='raw prompt')
        with self.assertRaises(ValueError):self.store.save(self.key,{'invalid':float('nan')},[])
        with self.assertRaises(ValueError):self.store.save(self.key,{},[{'usage':{'secret':1}}])

    def test_non_dict_json_is_rejected(self):
        self.store.save(self.key,self.result,self.trace)
        next(self.folder.glob('*.json')).write_text('[]')
        with self.assertRaises(CheckpointError):self.store.load(self.key)

    def test_real_batch_trace_roundtrip(self):
        from podcast.agent_pipeline.codex_adapter import _tool_observations
        event={'type':'item.completed','item':{'type':'web_search','id':'item_1','status':'completed',
            'action':{'type':'open_page','url':'https://example.com/one'},'results':[
            {'type':'text_result','url':'https://example.com/one','ref_id':'turn0view0'},
            {'type':'text_result','url':'https://example.com/two','ref_id':'turn0view1'}]}}
        trace=_tool_observations(event,'2026-11-09T06:00:00+00:00',1)
        self.store.save(self.key,self.result,trace)
        self.assertEqual(self.store.load(self.key)['tool_trace'],trace)

    def test_unsafe_or_incomplete_observation_rejected(self):
        from podcast.agent_pipeline.codex_adapter import _tool_observations
        event={'type':'item.completed','item':{'type':'web_search','id':'item_1','status':'completed','action':{'type':'open_page','url':'https://example.com/one'}}}
        row=_tool_observations(event,'2026-11-09T06:00:00+00:00',1)[0]
        for change in ({'url':'https://example.com/a?secret=foo'}, {'query_sha256':'raw query'}, {'timestamp_basis':'inferred'}, {'ref_id':'bad ref'}):
            with self.assertRaises(ValueError):self.store.save(self.key,self.result,[{**row,**change}])
        row.pop('trace_id')
        with self.assertRaises(ValueError):self.store.save(self.key,self.result,[row])

if __name__=='__main__':unittest.main()
