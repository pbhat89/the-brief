import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from types import SimpleNamespace
from podcast.agent_pipeline.pipeline import Pipeline
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
    def test_success_and_duplicate(self,*mocks):
        with tempfile.TemporaryDirectory() as t:
            repo=Path(t)/'repo';repo.mkdir();adapter=Fake();p=Pipeline(repo,Path(t)/'private',adapter)
            r=p.run('2026-11-08','comparison-test')
            self.assertEqual(r['status'],'comparison_draft_release_blocked')
            self.assertTrue(Path(r['artifacts']['html']).exists())
            self.assertTrue(p.audit.verify_chain())
            with self.assertRaises(ValueError):p.run('2026-11-08','comparison-test')
            calls=adapter.calls;p.run('2026-11-08','comparison-test',True);self.assertEqual(calls,adapter.calls)
    def test_bounded_repairs(self,*mocks):
        with tempfile.TemporaryDirectory() as t:
            repo=Path(t)/'repo';repo.mkdir();p=Pipeline(repo,Path(t)/'private',Fake(True))
            r=p.run('2026-11-08','failed');self.assertEqual(r['status'],'editorial_blocked');self.assertEqual(r['repair_round'],2)
    def test_public_output_rejected(self,*mocks):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):Pipeline(t,Path(t)/'out',Fake())
    def test_unsafe_id(self,*mocks):
        with tempfile.TemporaryDirectory() as t:
            repo=Path(t)/'repo';repo.mkdir();p=Pipeline(repo,Path(t)/'private',Fake())
            with self.assertRaises(ValueError):p.run('2026-11-08','../bad')
if __name__=='__main__':unittest.main()
