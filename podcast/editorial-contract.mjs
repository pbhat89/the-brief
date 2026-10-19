import assert from 'node:assert/strict';
import {validatePodcastLearningLedger, selectPodcastLearning} from './validate-podcast-learning.mjs';

const nonempty = value => typeof value === 'string' && value.trim().length > 0;
const https = value => { try { const url = new URL(value); return url.protocol === 'https:' && !url.username && !url.password; } catch { return false; } };
const date = value => typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value) && Number.isFinite(Date.parse(value)) && new Date(value).toISOString().slice(0, 10) === value;
const seconds = value => Number.isFinite(value) && value >= 0;

export function validateEditorialPolicy(policy) {
  assert.equal(policy.version, 1);
  assert.ok(date(policy.effective_from), 'Invalid effective date');
  assert.equal(policy.scope, 'external-companion-only');
  assert.deepEqual(policy.conditions.target_seconds, [20, 30]);
  assert.equal(policy.conditions.routine_safety_announcement, false);
  assert.equal(policy.conditions.regional_psi_recital, false);
  assert.equal(policy.conditions.exception, 'verified-actionable-alert');
  assert.deepEqual(policy.singapore_news.target_stories, [2, 3]);
  assert.equal(policy.singapore_news.weather_counts_as_news, false);
  assert.equal(policy.singapore_news.require_fresh_verified, true);
  assert.equal(policy.singapore_news.allow_shortfall_with_reason, true);
  assert.equal(policy.singapore_news.padding, false);
  assert.deepEqual(policy.expert_learning.target_seconds, [45, 75]);
  assert.equal(policy.expert_learning.target_insights, 1);
  assert.equal(policy.expert_learning.allow_evergreen, true);
  assert.equal(policy.expert_learning.require_primary_source, true);
  assert.equal(policy.expert_learning.dedup, 'concept-across-experts-and-all-history');
  assert.equal(policy.expert_learning.covered_concepts_expire, false);
  assert.equal(policy.expert_learning.ledger, 'expert-learning-log.json');
  assert.equal(policy.podcast_recap.primary, 'Everyday AI');
  assert.equal(policy.podcast_recap.fallback, 'Big Technology Podcast');
  assert.equal(policy.podcast_recap.seed_originals, 3);
  assert.equal(policy.podcast_recap.maximum_per_day, 1);
  assert.equal(policy.podcast_recap.after_catchup, 'latest-unseen-original-only');
  assert.equal(policy.podcast_recap.require_accessible_transcript, true);
  assert.equal(policy.podcast_recap.mark_covered_after_publication, true);
  assert.equal(policy.ending.maximum_seconds, 20);
  assert.equal(policy.ending.optional_improvement_sentences, 1);
  assert.equal(policy.ending.recap, false);
  assert.equal(policy.ending.spoken_source_diagnostics, false);
  assert.deepEqual(policy.delivery.target_minutes, [10, 12]);
  assert.equal(policy.delivery.start_sgt, '07:00');
  assert.equal(policy.delivery.target_sgt, '07:30');
  assert.equal(policy.delivery.public_personal_content, false);
  return true;
}

// Private per-edition measurements and source review supplied by the operator.
// This does not inspect audio or establish semantic truth by itself.
export function validateEditorialAudit(policy, audit) {
  validateEditorialPolicy(policy);
  assert.ok(date(audit.edition_date), 'Invalid edition date');
  assert.ok(nonempty(audit.source_revision), 'Record the repository revision');
  for (const key of ['conditions_seconds', 'expert_seconds', 'ending_seconds']) assert.ok(seconds(audit[key]), `Invalid ${key}`);
  if (audit.conditions_seconds > policy.conditions.target_seconds[1]) {
    assert.equal(audit.conditions_exception?.kind, 'verified-actionable-alert');
    assert.ok(nonempty(audit.conditions_exception.reason) && https(audit.conditions_exception.source_url), 'Long conditions require a sourced actionable exception');
  }
  assert.equal(audit.routine_safety_announcement, false);
  assert.equal(audit.regional_psi_recital, false);
  assert.equal(audit.spoken_source_diagnostics, false);
  assert.equal(audit.repeated_closing_summary, false);
  assert.ok(audit.ending_seconds <= policy.ending.maximum_seconds, 'Ending exceeds 20 seconds');
  assert.ok(Number.isInteger(audit.improvement_sentences) && audit.improvement_sentences >= 0 && audit.improvement_sentences <= 1);
  assert.ok(Array.isArray(audit.singapore_stories));
  const events = new Set();
  for (const story of audit.singapore_stories) {
    assert.ok(nonempty(story.event_id) && !events.has(story.event_id), 'Duplicate Singapore event'); events.add(story.event_id);
    assert.equal(story.weather, false, 'Weather does not count as Singapore news');
    assert.equal(story.fresh_verified, true);
    assert.ok(https(story.source_url));
  }
  if (audit.singapore_stories.length < policy.singapore_news.target_stories[0]) assert.ok(nonempty(audit.singapore_shortfall_reason), 'Explain the verified-news shortfall');
  assert.ok(Array.isArray(audit.expert_concept_ids) && audit.expert_concept_ids.length <= 1);
  if (audit.expert_concept_ids.length) {
    assert.ok(nonempty(audit.expert_concept_ids[0]));
    assert.ok(audit.expert_seconds >= 45 && audit.expert_seconds <= 75, 'Expert learning must be 45–75 seconds');
    assert.equal(audit.expert_semantic_history_reviewed, true);
    assert.ok(https(audit.expert_source_url));
  } else {
    assert.equal(audit.expert_seconds, 0);
    assert.ok(nonempty(audit.expert_omission_reason), 'Explain the source gap instead of padding');
  }
  assert.ok(Array.isArray(audit.podcast_recaps) && audit.podcast_recaps.length <= 1, 'At most one recap per edition');
  for (const recap of audit.podcast_recaps) {
    assert.ok(['Everyday AI', 'Big Technology Podcast'].includes(recap.show));
    assert.ok(nonempty(recap.episode_key));
    assert.equal(recap.original_verified, true);
    assert.equal(recap.transcript_accessible, true);
    assert.equal(recap.previously_covered, false);
    assert.ok(Array.isArray(recap.segment_references) && recap.segment_references.length && recap.segment_references.every(nonempty));
    if (recap.show === 'Big Technology Podcast') assert.ok(nonempty(audit.everyday_ai_ineligible_reason));
  }
  return true;
}

// Pre-publication reference check: the selected concept must be an actually
// reviewed, unused entry, not just a plausible ID written in the private audit.
export function validateExpertSelection(audit, log) {
  for (const id of audit.expert_concept_ids) {
    const entry = log.entries.find(item => item.concept_id === id);
    assert.ok(entry, 'Selected expert concept is absent from the learning log');
    assert.equal(entry.status, 'researched_candidate', 'Covered concepts cannot be selected again');
    assert.equal(entry.dedup_review, 'reviewed_no_match', 'Complete the semantic history review before selection');
    assert.equal(entry.uses.length, 0);
    assert.ok(entry.sources.some(source => source.url === audit.expert_source_url && source.kind === 'first_party' && source.verification === 'direct_primary'), 'Selected source must match directly checked primary evidence');
  }
  return true;
}

export function validatePodcastSelection(audit, ledger) {
  assert.deepEqual(validatePodcastLearningLedger(ledger), [], 'Invalid podcast learning ledger');
  if (!audit.podcast_recaps.length) return true;
  const context = audit.podcast_selection_context;
  assert.ok(context, 'Recaps require the current podcast selection context');
  assert.equal(context.date_sgt, audit.edition_date);
  const selected = selectPodcastLearning(ledger, context);
  const recap = audit.podcast_recaps[0];
  assert.ok(selected.episode_id, 'No episode is eligible for this daily recap slot');
  assert.equal(recap.episode_key, selected.episode_id, 'Recap must match the eligible canonical episode');
  assert.equal(recap.show, {'everyday-ai':'Everyday AI','big-technology':'Big Technology Podcast'}[selected.show]);
  assert.equal(recap.transcript_source_url, selected.episode.transcript.source_url);
  assert.equal(recap.transcript_provenance, selected.episode.transcript.provenance, 'Do not upgrade third-party transcripts to official provenance');
  return true;
}
