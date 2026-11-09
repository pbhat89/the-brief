import tempfile
import os
from contextlib import ExitStack
import unittest
from unittest.mock import patch
from pathlib import Path
from types import SimpleNamespace
from podcast.agent_pipeline.pipeline import Pipeline, context_digest
from podcast.agent_pipeline.content import ROLES
from podcast.agent_pipeline.test_content import edition,story

class Fake:
    def __init__(self,fail_check=False): self.calls=0;self.fail_check=fail_check
    def run(self,prompt,schema,**kw):
        self.calls+=1
        keys=schema['properties']
        if 'role' in keys: data={'role':'india','stories':[story()],'sources':[],'gaps':['partial']}
        elif 'edition_date' in keys: data=edition()
        elif 'passed' in keys: data={'passed':not self.fail_check,'issues':[{'story_id':'one','reason':'unsupported'}] if self.fail_check else [],'coverage_gaps':[]}
        else: data={'sections':[{'name':'Weather','text':'Test briefing','story_ids':['one']}],'word_count':2}
        return SimpleNamespace(data=data,usage=None,attempts=1)

@patch("podcast.agent_pipeline.pipeline.verify_research", return_value=[])
@patch("podcast.agent_pipeline.pipeline.verify_edition_provenance", return_value=[])
@patch("podcast.agent_pipeline.pipeline.load_context", return_value={"missing_files":[]})
class PipelineTests(unittest.TestCase):
    def setUp(self):
        # Synthetic ACL for orchestration fixtures; real host privacy is checked
        # independently and must not be inferred from these tests.
        if os.name == 'nt':
            acl={'current_sid':'S-1-5-21-test-1001','owner_sid':'S-1-5-21-test-1001','dacl_present':True,'aces':[{'sid':'S-1-5-21-test-1001','type':'Allow'}]}
            mock=patch('podcast.agent_pipeline.audit.inspect_windows_acl',return_value=acl)
            mock.start();self.addCleanup(mock.stop)

    def test_context_identity_excludes_observation_time_only(self,*mocks):
        a={'files':{'policy':'hash-one'},'intake_events':[{'observed_at':'one'}]}
        b={'files':{'policy':'hash-one'},'intake_events':[{'observed_at':'two'}]}
        self.assertEqual(context_digest(a),context_digest(b))
        b['files']['policy']='hash-two'
        self.assertNotEqual(context_digest(a),context_digest(b))
    def test_success_and_duplicate(self,*mocks):
        with tempfile.TemporaryDirectory() as t, ExitStack() as resources:
            repo=Path(t)/'repo';repo.mkdir();adapter=Fake();p=Pipeline(repo,Path(t)/'private',adapter)
            resources.enter_context(p.audit)
            r=p.run('2026-11-08','comparison-test')
            self.assertEqual(r['status'],'comparison_draft_release_blocked')
            self.assertTrue(Path(r['artifacts']['html']).exists())
            self.assertTrue(p.audit.verify_chain())
            with self.assertRaises(ValueError):p.run('2026-11-08','comparison-test')
            calls=adapter.calls;p.run('2026-11-08','comparison-test',True);self.assertEqual(calls,adapter.calls)
    def test_bounded_repairs(self,*mocks):
        with tempfile.TemporaryDirectory() as t, ExitStack() as resources:
            repo=Path(t)/'repo';repo.mkdir();p=Pipeline(repo,Path(t)/'private',Fake(True))
            resources.enter_context(p.audit)
            r=p.run('2026-11-08','failed');self.assertEqual(r['status'],'editorial_blocked');self.assertEqual(r['repair_round'],2)
    def test_public_output_rejected(self,*mocks):
        with tempfile.TemporaryDirectory() as t, ExitStack() as resources:
            with self.assertRaises(ValueError):Pipeline(t,Path(t)/'out',Fake())
    def test_unsafe_id(self,*mocks):
        with tempfile.TemporaryDirectory() as t, ExitStack() as resources:
            repo=Path(t)/'repo';repo.mkdir();p=Pipeline(repo,Path(t)/'private',Fake())
            resources.enter_context(p.audit)
            with self.assertRaises(ValueError):p.run('2026-11-08','../bad')
if __name__=='__main__':unittest.main()
