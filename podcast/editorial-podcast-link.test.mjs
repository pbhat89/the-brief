import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validatePodcastSelection} from './editorial-contract.mjs';
import {selectPodcastLearning, recordPodcastPublication} from './validate-podcast-learning.mjs';
const fixture = JSON.parse(readFileSync(new URL('./test-fixtures/podcast-learning-ledger.fixture.json', import.meta.url), 'utf8'));
function setup() {
 const ledger=structuredClone(fixture), time='2026-10-20T00:10:00Z';
 for(const entry of ledger.episodes){entry.transcript.checked_at=time;entry.dedup_review={status:'clear',story_keys:[entry.episode_id+':fixture-explanation'],contribution:null,reviewed_at:time};}
 const context={date_sgt:'2026-10-20',as_of:time,primary_check:{status:'complete',checked_at:time},fallback_check:{status:'complete',checked_at:time},candidates:[]};
 const selected=selectPodcastLearning(ledger,context);
 const audit={edition_date:context.date_sgt,podcast_selection_context:context,podcast_recaps:[{episode_key:selected.episode_id,show:'Big Technology Podcast',transcript_source_url:selected.episode.transcript.source_url,transcript_provenance:selected.episode.transcript.provenance}]};
 return {ledger,audit,context};
}
test('private audit uses an eligible canonical episode and honest transcript provenance',()=>{const {ledger,audit}=setup();assert.equal(validatePodcastSelection(audit,ledger),true);});
test('unknown episodes, missing context, wrong date and upgraded provenance fail',()=>{
 for(const mutate of [a=>a.podcast_recaps[0].episode_key='invented',a=>delete a.podcast_selection_context,a=>a.edition_date='2026-10-21',a=>a.podcast_recaps[0].transcript_provenance='publisher-transcript',a=>a.podcast_recaps[0].transcript_source_url='https://example.org/unrelated']){const {ledger,audit}=setup();mutate(audit);assert.throws(()=>validatePodcastSelection(audit,ledger));}
});
test('publication consumes the date slot and cannot be relabelled as another recap',()=>{
 const {ledger,audit,context}=setup();
 const next=recordPodcastPublication(ledger,context,{publication_id:'fixture-published',episode_id:audit.podcast_recaps[0].episode_key,status:'verified_published',output_url:'https://pbhat89.github.io/the-brief/podcast/reports/2026-10-20.html',revision:'fixture',content_sha256:'a'.repeat(64),verified_at:'2026-10-20T00:11:00Z',confirmation:'Synthetic fixture publication evidence.'});
 assert.throws(()=>validatePodcastSelection(audit,next));
});
test('pending semantic review is not sufficient to narrate a seed',()=>{const {ledger,audit}=setup();for(const e of ledger.episodes)e.dedup_review={status:'pending',story_keys:[],contribution:null,reviewed_at:null};assert.throws(()=>validatePodcastSelection(audit,ledger));});
