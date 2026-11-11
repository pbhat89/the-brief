"""Synthetic editorial contracts, not live research or automated truth judgments."""
import copy
import unittest
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from podcast.agent_pipeline.content import (
    EDITION_SCHEMA, EDITORIAL_CHECK_SCHEMA, research_prompt, editor_prompt,
    podcast_prompt, verify_edition, verify_edition_provenance, verify_script,
    verify_editorial_review, ROLES,
)
from podcast.agent_pipeline.test_content import story, edition
from podcast.agent_pipeline.pipeline import Pipeline
from jsonschema import validate


def grounded():
    """Invented example.org transport story, never real reporting."""
    result = edition()
    news = story('news', 'bus-pilot')
    passages = [
        'The authority began a six-month electric-bus trial on two routes on November 8.',
        'The trial replaces diesel buses on the two routes to test operating costs.',
        'Passengers on those routes will use electric buses while fares remain unchanged.',
        'The authority has not released cost or reliability results; expansion depends on the trial.',
    ]
    news.update(treatment='developed', treatment_reason='Passengers need to understand the trial scope and limitations.')
    news['headline'] = 'Electric-bus trial begins'
    news['evidence'] = [dict(url=news['sources'][0], quote=text, locator=f'Paragraph {i + 1}')
                        for i, text in enumerate(passages)]
    news['narrative'] = [dict(kind=kind, text=text, evidence_indexes=[i])
                         for i, (kind, text) in enumerate(zip(
                             ['development', 'context', 'stakes', 'caveat'], passages))]
    news['summary'] = ' '.join(passages)
    result['sections'].append(dict(name='Singapore', stories=[news]))
    result['selection'].append(dict(story_id=news['id'], decision='selected',
                                   reason='Service change with a defined trial scope and unchanged fares.'))
    candidates = [{'stories': [copy.deepcopy(result['sections'][0]['stories'][0]), copy.deepcopy(news)],
                   'gaps': ['X access incomplete'], 'sources': []}]
    # Researchers supply evidence packets, not editor-owned narration.
    for item in candidates[0]['stories']:
        item.pop('narrative', None)
        item.pop('treatment', None)
        item.pop('treatment_reason', None)
    script = {'sections': [dict(name='Weather', text='Conditions update.', story_ids=['one']),
                           dict(name='Singapore', text=news['summary'], story_ids=[news['id']])]}
    script['word_count'] = sum(len(s['text'].split()) for s in script['sections'])
    review = dict(passed=True, issues=[], coverage_gaps=[],
                  edition_review=dict(selection_is_justified=True, depth_is_sufficient=True,
                                      rationale="Synthetic service change explains scope, baseline and limits."), editorial_reviews=[dict(
        story_id=news['id'], supported_unit_indexes=[0, 1, 2, 3], context_is_useful=True,
        caveats_preserved=True,
        rationale='Paragraphs 1–4 establish scope, diesel baseline, unchanged fares and absent results.')])
    return result, candidates, script, review


def recount(script):
    script['word_count'] = sum(len(s['text'].split()) for s in script['sections'])


class EditorialDepthTests(unittest.TestCase):
    def test_grounded_context_passes_all_contracts(self):
        e, research, script, review = grounded()
        validate(e, EDITION_SCHEMA)
        validate(review, EDITORIAL_CHECK_SCHEMA)
        self.assertEqual(verify_edition(e, e['edition_date']), [])
        self.assertEqual(verify_edition_provenance(e, research), [])
        self.assertEqual(verify_script(script, e), [])
        self.assertEqual(verify_editorial_review(review, e), [])

    def test_headline_only_fails_without_word_threshold(self):
        e, _, _, _ = grounded()
        news = e['sections'][1]['stories'][0]
        news['narrative'] = news['narrative'][:1]
        news['summary'] = news['narrative'][0]['text']
        self.assertTrue(any('development/context/stakes' in x for x in verify_edition(e, e['edition_date'])))

    def test_repeated_headline_cannot_fill_three_slots(self):
        e, _, _, _ = grounded()
        news = e['sections'][1]['stories'][0]
        for unit in news['narrative']:
            unit['text'] = news['headline']
        news['summary'] = ' '.join(u['text'] for u in news['narrative'])
        self.assertTrue(any('duplicated' in x for x in verify_edition(e, e['edition_date'])))

    def test_unlinked_expansion_fails(self):
        e, _, _, _ = grounded()
        news = e['sections'][1]['stories'][0]
        news['narrative'][2] = dict(kind='stakes', text='The buses cut costs by half.', evidence_indexes=[99])
        news['summary'] = ' '.join(u['text'] for u in news['narrative'])
        self.assertTrue(any('linked evidence' in x for x in verify_edition(e, e['edition_date'])))

    def test_forged_quote_cannot_become_research(self):
        e, research, _, _ = grounded()
        e['sections'][1]['stories'][0]['evidence'][2]['quote'] = 'The buses cut costs by half.'
        self.assertTrue(any('unresearched evidence' in x for x in verify_edition_provenance(e, research)))

    def test_unsupported_expansion_with_valid_link_needs_semantic_rejection(self):
        e, _, _, review = grounded()
        news = e['sections'][1]['stories'][0]
        news['narrative'][2]['text'] = 'The buses cut costs by half.'
        news['summary'] = ' '.join(u['text'] for u in news['narrative'])
        # A valid index is not entailment. Simulate an independent evidence finding.
        self.assertEqual(verify_edition(e, e['edition_date']), [])
        review['editorial_reviews'][0]['supported_unit_indexes'].remove(2)
        review['editorial_reviews'][0]['rationale'] = 'Paragraph 3 discusses fares, not measured cost savings.'
        self.assertTrue(verify_editorial_review(review, e))

    def test_overall_pass_cannot_override_missing_or_failed_review(self):
        e, _, _, review = grounded()
        review['editorial_reviews'] = []
        self.assertTrue(verify_editorial_review(review, e))
        for key in ['context_is_useful', 'caveats_preserved']:
            _, _, _, review = grounded()
            review['editorial_reviews'][0][key] = False
            self.assertTrue(verify_editorial_review(review, e))

    def test_script_id_does_not_mask_headline_compression(self):
        e, _, script, _ = grounded()
        script['sections'][1]['text'] = 'An electric-bus trial has begun.'
        recount(script)
        self.assertTrue(any('lost locked narrative' in x for x in verify_script(script, e)))

    def test_script_cannot_remove_only_caveat(self):
        e, _, script, _ = grounded()
        script['sections'][1]['text'] = ' '.join(u['text'] for u in e['sections'][1]['stories'][0]['narrative'][:3])
        recount(script)
        self.assertEqual(verify_script(script, e), ['bus-pilot: script lost locked narrative unit 3'])

    def test_core_in_unrelated_section_does_not_count(self):
        e, _, script, _ = grounded()
        script['sections'][0]['text'] += ' ' + script['sections'][1]['text']
        script['sections'][1]['text'] = 'An electric-bus trial has begun.'
        recount(script)
        self.assertTrue(verify_script(script, e))

    def test_script_duplicate_or_reordered_core_fails(self):
        for mode in ('duplicate', 'reorder'):
            e, _, script, _ = grounded()
            units = e['sections'][1]['stories'][0]['narrative']
            script['sections'][1]['text'] = (' '.join(u['text'] for u in reversed(units))
                if mode == 'reorder' else script['sections'][1]['text'] + ' ' + units[0]['text'])
            recount(script)
            self.assertTrue(verify_script(script, e))

    def test_justified_brief_does_not_require_padded_stakes(self):
        e, _, _, review = grounded()
        news = e['sections'][1]['stories'][0]
        news.update(treatment='brief', treatment_reason='Synthetic bounded update for a previously explained trial.')
        news['narrative'] = [news['narrative'][0], news['narrative'][3]]
        news['summary'] = ' '.join(u['text'] for u in news['narrative'])
        self.assertEqual(verify_edition(e, e['edition_date']), [])
        review['editorial_reviews'][0]['supported_unit_indexes'] = [0, 1]
        self.assertEqual(verify_editorial_review(review, e), [])
        # Valid brief structure alone cannot approve a shallow whole edition.
        review['edition_review']['depth_is_sufficient'] = False
        self.assertTrue(verify_editorial_review(review, e))

    def test_summary_cannot_hide_context_from_html(self):
        e, _, _, _ = grounded()
        e['sections'][1]['stories'][0]['summary'] = 'An electric-bus trial has begun.'
        self.assertTrue(any('complete locked narrative' in x for x in verify_edition(e, e['edition_date'])))

    def test_candidate_selection_is_exhaustive_not_story_count(self):
        e, research, _, _ = grounded()
        research[0]['stories'].append(story('news', 'not-selected'))
        self.assertTrue(any('every candidate' in x for x in verify_edition_provenance(e, research)))
        e['selection'].append(dict(story_id='not-selected', decision='excluded',
                                   reason='No evidence beyond the headline; further research required.'))
        self.assertEqual(verify_edition_provenance(e, research), [])

    def test_blocked_x_cannot_become_complete_if_agent_omits_gap(self):
        e, research, _, _ = grounded()
        e.update(coverage_status='complete', gaps=[])
        research[0]['gaps'] = []
        research[0]['sources'] = [dict(id='x:example', status='blocked')]
        self.assertTrue(any('complete coverage' in x for x in verify_edition_provenance(e, research)))

    def test_pipeline_enforces_review_even_when_passed_flag_true(self):
        e, research, _, review = grounded()
        review['editorial_reviews'][0]['context_is_useful'] = False
        runner = object.__new__(Pipeline)
        runner.context = {}
        runner.audit = SimpleNamespace(record_checkpoint=Mock())
        runner.invoke_agent = Mock(return_value=review)
        outcome = runner.check(dict(edition=e, research=research, date=e['edition_date'], run_id='synthetic'))
        self.assertEqual(outcome['status'], 'repair')
        self.assertIn('depth/caveat', ' '.join(outcome['errors']))

    def test_renderer_blocks_compression_even_if_checker_says_pass(self):
        e, _, script, review = grounded()
        script['sections'][1]['text'] = 'An electric-bus trial has begun.'
        recount(script)
        with tempfile.TemporaryDirectory() as private:
            runner = object.__new__(Pipeline)
            runner.output = Path(private)
            runner.audit = Mock()
            runner.invoke_agent = Mock(side_effect=lambda state, role, *args:
                copy.deepcopy(review if role.startswith('script_checker') else script))
            with self.assertRaisesRegex(ValueError, 'two repair attempts'):
                runner.render(dict(edition=e, run_id='synthetic'))
            self.assertEqual(runner.invoke_agent.call_count, 6)
            self.assertFalse((Path(private) / 'synthetic' / 'script.json').exists())

    def test_renderer_accepts_grounded_core_without_padding(self):
        e, _, script, review = grounded()
        with tempfile.TemporaryDirectory() as private:
            runner = object.__new__(Pipeline)
            runner.output = Path(private)
            runner.audit = Mock()
            runner.invoke_agent = Mock(side_effect=lambda state, role, *args:
                copy.deepcopy(review if role.startswith('script_checker') else script))
            result = runner.render(dict(edition=e, run_id='synthetic'))
            self.assertEqual(result['status'], 'written_ready')
            self.assertTrue(Path(result['artifacts']['script']).exists())

    def test_negating_transition_still_requires_semantic_review(self):
        e, _, script, review = grounded()
        script['sections'][1]['text'] += ' Actually, none of the statements above is true.'
        recount(script)
        # Retention alone cannot classify a contradiction; independent review must.
        self.assertEqual(verify_script(script, e), [])
        review['editorial_reviews'][0]['supported_unit_indexes'] = []
        review['editorial_reviews'][0]['rationale'] = 'The closing transition contradicts every supported unit.'
        self.assertTrue(verify_editorial_review(review, e))

    def test_research_not_limited_by_audio_and_no_headline_instruction(self):
        e, research, _, _ = grounded()
        for role in ROLES:
            prompt = research_prompt(role, {})
            self.assertIn('must not be constrained by audio duration', prompt)
            self.assertNotIn('headline plus one short', prompt)
        self.assertIn('EVERY supplied candidate', editor_prompt(research, {}))
        self.assertNotIn('headline plus one short', podcast_prompt(e))
        self.assertIn('never shorten them to headline snippets', podcast_prompt(e))


if __name__ == '__main__':
    unittest.main()
