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
    return dict(edition_date='2026-11-08',title='Review',coverage_status='partial',gaps=['X access incomplete'],sections=[dict(name='Weather',stories=[dict(story('weather'),narrative=[],written_context=[],retention=[],treatment='not_applicable',treatment_reason='Conditions')])],fact=None,learning=None,selection=[dict(story_id='one',decision='selected',reason='Timestamped conditions')])


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
        self.assertIn('<h2>Fact</h2>',render_html(e));self.assertIn('Learning',render_html(e))
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

class SourceAssignmentTests(unittest.TestCase):
    def test_every_contract_category_has_exactly_one_owner(self):
        from .content import ROLE_SOURCE_IDS
        import re
        contract = (Path(__file__).resolve().parents[1] / "source-coverage-contract.mjs").read_text(encoding="utf-8")
        required = re.findall(r"'([^']+)'", re.search(r"REQUIRED_SOURCE_IDS=(\[.*?\]);", contract).group(1))
        assigned = [sid for ids in ROLE_SOURCE_IDS.values() for sid in ids]
        self.assertEqual(sorted(required), sorted(assigned))
        self.assertEqual(len(assigned), len(set(assigned)))

    def test_prompt_assigns_category_without_fabricating_attempt(self):
        from .content import source_assignment
        context = {"required_source_ids": ["world-independent", "weather"], "fixed_source_targets": {}}
        self.assertEqual(source_assignment("world", context), [{"id": "world-independent", "fixed_url": None}])
        prompt = research_prompt("world", context)
        self.assertIn("Owned mandatory source rows", prompt)
        self.assertIn("never manufacture a time", prompt)
        self.assertIn("real open-page tool attempt at the exact reported URL", prompt)
        self.assertIn("search-only discovery is insufficient", prompt)
        self.assertIn("mark unattempted", prompt)
        self.assertIn("never invent an HTTPS URL", prompt)

class TraceTests(unittest.TestCase):
    def test_exact_attempt_only_and_no_mutation(self):
        from .content import reconcile_source_traces
        result = {"sources": [{"url": "https://example.org/a", "status": "blocked", "attempted_at": "invented"}]}
        event = {"event": "item.completed", "action": "open_page", "url": "https://example.org/a", "timestamp_basis": "adapter_observed", "observed_at": "2026-11-09T01:02:03Z", "trace_id": "t1"}
        row = reconcile_source_traces(result, [event])["sources"][0]
        self.assertEqual(row["attempted_at"], event["observed_at"])
        self.assertEqual(row["status"], "blocked")
        self.assertEqual(result["sources"][0]["attempted_at"], "invented")
        for changes in ({"action": "search"}, {"event": "item.started"}, {"url": "https://example.org/b"}, {"observed_at": "2026-11-09"}):
            changed = dict(event, **changes)
            self.assertIsNone(reconcile_source_traces(result, [changed])["sources"][0]["attempted_at"])
        result["sources"][0]["url"] += "?id=2"
        self.assertIsNone(reconcile_source_traces(result, [event])["sources"][0]["attempted_at"])

    def test_measured_local_intake_hash(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "archive").mkdir()
            (root / "podcast").mkdir()
            raw = b'{"items": []}'
            (root / "archive/2026-11-09.json").write_bytes(raw)
            (root / "podcast/expert-learning-log.json").write_bytes(raw)
            c = load_context(root, "2026-11-09")
            self.assertEqual(len(c["intake_events"]), 2)
            for event in c["intake_events"]:
                self.assertEqual(event["sha256"], hashlib.sha256(raw).hexdigest())
                self.assertEqual(event["timestamp_basis"], "host_read")
                self.assertNotIn("url", event)
            from .content import reconcile_source_traces, verify_research
            research = [reconcile_source_traces({"role": role, "sources": [], "stories": []}, [], c["intake_events"]) for role in ROLES]
            c["required_source_ids"] = ["upstream", "expert-knowledge-log"]
            self.assertEqual(verify_research(research, c), [])
            forged = copy.deepcopy(research)
            next(row for r in forged for row in r["sources"] if row["id"] == "upstream")["host_evidence"]["sha256"] = "0" * 64
            self.assertTrue(any("host intake" in e for e in verify_research(forged, c)))

if __name__ == "__main__":
    unittest.main()


class SourceIdentityTests(unittest.TestCase):
    def test_research_id_to_edition_preserves_provenance(self):
        from .content import canonicalize_research_sources,verify_edition_provenance
        raw={'stories':[story('weather')],'sources':[{'id':'weather-source','url':'https://example.org/story'}],'gaps':['Partial']}
        raw['stories'][0]['sources']=['weather-source']
        normalized,mappings=canonicalize_research_sources(raw)
        e=edition();e['sections'][0]['stories']=copy.deepcopy(normalized['stories']);e['gaps']+=normalized['gaps']
        self.assertEqual(verify_edition(e,'2026-11-08'),[])
        self.assertEqual(verify_edition_provenance(e,[normalized]),[])
        self.assertEqual(raw['stories'][0]['sources'],['weather-source'])
        self.assertEqual(mappings,[{'story_id':'one','source_id':'weather-source','url':'https://example.org/story'}])
        self.assertNotIn('mappings',normalized['stories'][0])
    def test_missing_ambiguous_and_no_evidence_fail(self):
        from .content import canonicalize_research_sources
        for rows in ([],[{'id':'ref','url':'https://example.org/story'},{'id':'ref','url':'https://example.org/other'}],[{'id':'ref','url':'https://example.org/other'}]):
            raw={'stories':[story()],'sources':rows};raw['stories'][0]['sources']=['ref']
            with self.assertRaises(ValueError):canonicalize_research_sources(raw)
    def test_existing_url_stays_exact(self):
        from .content import canonicalize_research_sources
        raw={'stories':[story()],'sources':[]}
        normalized,mappings=canonicalize_research_sources(raw)
        self.assertEqual(normalized,raw);self.assertEqual(mappings,[])


class RenderSectionTests(unittest.TestCase):
    def test_order_single_named_sections_and_all_content(self):
        from .content import SECTION_ORDER
        e=edition();e['learning']=story('learning','lesson');e['fact']=story('fact','fact')
        e['learning']['headline']='Learning headline';e['fact']['headline']='Fact headline'
        e['sections']=[{'name':'Fact','stories':[]},{'name':'Learning','stories':[copy.deepcopy(e['learning'])]},{'name':'Science','stories':[]}]+e['sections']
        output=render_html(e)
        for name in SECTION_ORDER:self.assertEqual(output.count('<h2>'+name+'</h2>'),1)
        positions=[output.index('<h2>'+name+'</h2>') for name in SECTION_ORDER]
        self.assertEqual(positions,sorted(positions))
        for sid in ['one','lesson','fact']:self.assertEqual(output.count('data-story-id="'+sid+'"'),1)
        self.assertIn('Learning headline',output);self.assertIn('Fact headline',output)
        self.assertIn('No item selected for this section.',output)
    def test_named_fields_and_ids_remain_escaped(self):
        e=edition();e['fact']=story('fact','"><script>alert(1)</script>')
        e['fact']['summary']='<script>alert(2)</script>';e['fact']['sources']=['javascript:alert(3)']
        output=render_html(e)
        self.assertNotIn('<script>',output);self.assertNotIn('javascript:',output)
        self.assertIn('&lt;script&gt;',output)
