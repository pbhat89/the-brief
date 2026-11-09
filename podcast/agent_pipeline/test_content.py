import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from .content import (load_context, research_prompt, verify_edition, render_html, ROLES, RESEARCH_SCHEMA, EDITION_SCHEMA)


def story(kind='news', sid='one'):
    return dict(id=sid,event_id='event-'+sid,headline='Test <news>',summary='A factual summary.',published_at='2026-11-08',event_date='2026-11-08',sources=['https://example.org/story'],evidence=[dict(url='https://example.org/story',quote='Source passage',locator='Paragraph 2')],kind=kind,material_update=False,previous_event_id=None,new_fact=None)


def edition():
    return dict(edition_date='2026-11-08',title='Review',coverage_status='partial',gaps=['X access incomplete'],sections=[dict(name='Weather',stories=[story('weather')])],fact=None,learning=None)


class ContentTests(unittest.TestCase):
    def test_valid(self): self.assertEqual(verify_edition(edition(),'2026-11-08'),[])
    def test_missing_evidence(self):
        e=edition();e['sections'][0]['stories'][0]['evidence']=[]
        self.assertTrue(any('evidence' in x for x in verify_edition(e,'2026-11-08')))
    def test_future_and_stale(self):
        for d,expected in [('2026-11-09','future'),('2026-11-01','stale')]:
            e=edition();e['sections'][0]['stories'][0]['published_at']=d
            self.assertTrue(any(expected in x for x in verify_edition(e,'2026-11-08')))
    def test_unknown_date(self):
        e=edition();e['sections'][0]['stories'][0]['published_at']=None
        self.assertTrue(any('unknown' in x for x in verify_edition(e,'2026-11-08')))
    def test_duplicate_event(self):
        e=edition();e['sections'][0]['stories'].append(copy.deepcopy(e['sections'][0]['stories'][0]))
        self.assertTrue(any('duplicate event' in x for x in verify_edition(e,'2026-11-08')))
    def test_gaps_and_order(self):
        e=edition();e['gaps']=[];e['sections'][0]['name']='India'
        self.assertEqual(len(verify_edition(e,'2026-11-08')),2)
    def test_update_new_fact(self):
        e=edition();e['sections'][0]['stories'][0]['material_update']=True
        self.assertTrue(any('update lacks' in x for x in verify_edition(e,'2026-11-08')))
    def test_xss_escape(self):
        e=edition();e['title']='<script>alert(1)</script>';e['sections'][0]['stories'][0]['sources'].append('javascript:alert(1)')
        rendered=render_html(e)
        self.assertNotIn('<script>',rendered);self.assertNotIn('javascript:',rendered)
        self.assertIn('&lt;script&gt;',rendered)
    def test_fact_learning(self):
        e=edition();e['learning']=story('learning','two');e['fact']=story('fact','three')
        self.assertEqual(verify_edition(e,'2026-11-08'),[])
        self.assertIn('Daily fact',render_html(e));self.assertIn('Learning',render_html(e))
    def test_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'archive').mkdir();(root/'podcast').mkdir()
            for date in ['2026-11-06','2026-11-08','2026-11-09']:
                (root/'archive'/f'{date}.json').write_text(json.dumps({'date':date,'items':[]}), encoding='utf-8')
            c=load_context(root,'2026-11-08')
            self.assertEqual(len(c['prior_archives']),1);self.assertEqual(c['upstream']['date'],'2026-11-08')
            self.assertTrue(c['missing_files'])
    def test_role_prompts(self):
        for role in ROLES:
            text=research_prompt(role,{})
            self.assertIn('untrusted data',text);self.assertIn(role,text)
        with self.assertRaises(ValueError): research_prompt('random',{})
    def test_schema_objects_are_strict(self):
        def visit(node):
            if isinstance(node,dict):
                if node.get('type')=='object':
                    self.assertFalse(node['additionalProperties']);self.assertEqual(set(node['properties']),set(node['required']))
                for x in node.values():visit(x)
            elif isinstance(node,list):
                for x in node:visit(x)
        visit(RESEARCH_SCHEMA);visit(EDITION_SCHEMA)


class ProvenanceTests(unittest.TestCase):
    def test_editor_cannot_invent_story(self):
        from .content import verify_edition_provenance
        self.assertTrue(verify_edition_provenance(edition(), []))
    def test_editor_cannot_change_evidence(self):
        from .content import verify_edition_provenance
        e=edition();original=copy.deepcopy(e['sections'][0]['stories'][0])
        e['sections'][0]['stories'][0]['evidence'][0]['quote']='Invented'
        self.assertTrue(any('evidence' in x for x in verify_edition_provenance(e,[{'stories':[original]}])))
    def test_complete_disallowed_on_gap(self):
        from .content import verify_edition_provenance
        e=edition();e['coverage_status']='complete';e['gaps']=[]
        self.assertTrue(any('coverage' in x for x in verify_edition_provenance(e,[{'stories':[story('weather')],'gaps':['blocked']}])) )
    def test_required_sources_fail_closed(self):
        from .content import verify_research
        r=[{'role':role,'stories':[],'sources':[],'gaps':[]} for role in ROLES]
        self.assertIn('weather: mandatory source unattempted',verify_research(r,{'required_source_ids':['weather']}))
    def test_script_word_count_and_missing_claims(self):
        from .content import verify_script
        self.assertEqual(verify_script({'sections':[{'name':'Weather','text':'Two words','story_ids':['one']}],'word_count':2},edition()),[])
        errors=verify_script({'sections':[{'name':'India','text':'Two words','story_ids':[]}],'word_count':7},edition())
        self.assertEqual(len(errors),3)


class EncodingTests(unittest.TestCase):
    def test_context_utf8_with_windows_default(self):
        # Emulate cp1252 even on UTF-8 hosts; exercise policies and both archives.
        original = Path.read_text
        def windows_read(path, encoding=None, errors=None):
            return original(path, encoding=encoding or "cp1252", errors=errors)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "archive").mkdir()
            (root / "podcast").mkdir()
            sample = "\u65b0\u52a0\u5761 \u2014 \u0939\u093f\u0902\u0926\u0940 \U0001f4f0"
            (root / "podcast" / "SOURCE_COVERAGE.md").write_text(sample, encoding="utf-8")
            for day in ("2026-11-07", "2026-11-08"):
                (root / "archive" / (day + ".json")).write_text(
                    json.dumps({"date": day, "items": [], "text": sample}, ensure_ascii=False),
                    encoding="utf-8")
            with patch.object(Path, "read_text", windows_read):
                context = load_context(root, "2026-11-08")
            self.assertEqual(context["upstream"]["text"], sample)
            self.assertIn(sample, json.dumps(context, ensure_ascii=False))
            self.assertIn(sample, json.dumps(context["prior_archives"], ensure_ascii=False))

if __name__ == "__main__":
    unittest.main()
