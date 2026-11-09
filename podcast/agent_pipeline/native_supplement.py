"""Private receipt-bound additions; actual native review is mandatory before merge."""
import copy
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from jsonschema import Draft202012Validator
from .audit import verify_private_path
from .native_bridge import digest
from .native_capture import manifest
from .content import RESEARCH_SCHEMA,canonicalize_research_sources,reconcile_source_traces,obj,arr,S,B

REVIEW_SCHEMA=obj({'passed':B,'accepted_story_ids':arr(S),'issues':arr(S)})

def load_supplement(path, *, date, context_hash, parent_run_id, seed):
    path=Path(path).resolve();verify_private_path(path)
    raw=path.read_bytes();bundle=json.loads(raw)
    if (bundle.get('edition_date'),bundle.get('context_hash'),bundle.get('parent_run_id'))!=(date,context_hash,parent_run_id):
        raise ValueError('Supplement lineage mismatch')
    if not bundle.get('researcher_id'):raise ValueError('Actual researcher identity required')
    evidence={};traces=[];receipts=[]
    for row in bundle.get('receipts',[]):
        if row.get('tool_name')!='chat_search_web_run':raise ValueError('Only declared chat_search_web_run story receipts supported')
        f=Path(row['path']).resolve();verify_private_path(f);payload=f.read_bytes()
        if hashlib.sha256(payload).hexdigest()!=row['sha256']:raise ValueError('Supplement receipt file hash mismatch')
        envelope=json.loads(payload)
        start=datetime.fromisoformat(envelope['started_at'].replace('Z','+00:00'));end=datetime.fromisoformat(envelope['observed_at'].replace('Z','+00:00'))
        if start.tzinfo is None or end.tzinfo is None or end<start:raise ValueError('Invalid supplemental receipt times')
        m=manifest(str(f.parent),f.name.split('.')[0],row.get('researcher_id',bundle['researcher_id']),row['tool_ref'],'opened')
        entry=m['entries'][0]
        text='\n'.join(block.get('text','') for block in envelope['tool_result'].get('content',[]))
        if not text or 'not accessible via this tool' in text or 'Internal Error' in text:raise ValueError('Supplement evidence was not readable')
        # Validate native web extract structure, not browser screenshots or plain bodies.
        # This checks receipt consistency, not cryptographic tool authentication.
        if not re.fullmatch(r'turn[A-Za-z0-9_]+',row['tool_ref']) or ('【'+row['tool_ref']+'】') not in text:
            raise ValueError('Supplement is not a native chat search source extract')
        opened=re.findall(r'Source: open\((\{[^\n]*?\})\)',text)
        if not any(json.loads(value).get('ref_id')==entry['url'] for value in opened):
            raise ValueError('Supplement lacks exact native open request provenance')
        evidence.setdefault(entry['url'],[]).append(text)
        traces.append({'event':'item.completed','action':'open_page','timestamp_basis':'driver_observed','url':entry['url'],'observed_at':entry['observed_at'],'trace_id':digest(entry),'access_outcome':'open'})
        receipts.append({'path':str(f),'sha256':row['sha256'],'manifest':m})
    stories={s['id'] for r in seed for s in r.get('stories',[])}
    events={s['event_id'] for r in seed for s in r.get('stories',[])}
    sources={s['id'] for r in seed for s in r.get('sources',[])}
    additions=[]
    for result in bundle.get('research',[]):
        Draft202012Validator(RESEARCH_SCHEMA).validate(result)
        result,_=canonicalize_research_sources(result)
        for source in result['sources']:
            if source['id'] in sources:raise ValueError('Supplement source ID collision')
            sources.add(source['id'])
            if source['url'] not in evidence:raise ValueError('Supplement source lacks receipt')
        for story in result['stories']:
            if story['id'] in stories or story['event_id'] in events:raise ValueError('Supplement story/event collision')
            stories.add(story['id']);events.add(story['event_id'])
            if not story['evidence']:raise ValueError('Supplement story lacks evidence')
            for e in story['evidence']:
                if not e['quote'] or not any(e['quote'] in t for t in evidence.get(e['url'],[])):
                    raise ValueError('Supplement evidence quote not in retained receipt')
        additions.append(reconcile_source_traces(result,traces))
    if not additions or not any(r['stories'] for r in additions):raise ValueError('Empty supplement')
    identity={'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'canonical_sha256':digest(bundle),'parent_run_id':parent_run_id,'researcher_id':bundle['researcher_id'],'automatic_tool_attestation':False,'research_provenance':bundle.get('research_provenance',[])}
    coverage=None
    if bundle.get('coverage_artifact'):
        row=bundle['coverage_artifact'];coverage_path=Path(row['path']).resolve();verify_private_path(coverage_path)
        coverage_raw=coverage_path.read_bytes()
        if hashlib.sha256(coverage_raw).hexdigest()!=row['sha256']:raise ValueError('Coverage artifact hash mismatch')
        coverage=json.loads(coverage_raw)
        identity['coverage_artifact']={'path':str(coverage_path),'sha256':row['sha256'],'release_gate_passed':False}
    return {'identity':identity,'research':additions,'receipts':receipts,'source_extracts':evidence,'coverage_evidence_only':coverage}


def merge_supplement(seed,supplement,review):
    Draft202012Validator(REVIEW_SCHEMA).validate(review)
    known={s['id'] for r in supplement['research'] for s in r['stories']}
    accepted=review['accepted_story_ids']
    if not review['passed'] or review['issues']:raise ValueError('Supplement independent review failed')
    if len(accepted)!=len(set(accepted)) or not set(accepted).issubset(known):raise ValueError('Unknown or duplicate accepted supplement ID')
    merged=copy.deepcopy(seed)
    for result in supplement['research']:
        target=next(r for r in merged if r['role']==result['role'])
        target['stories'].extend(s for s in result['stories'] if s['id'] in accepted)
        target['sources'].extend(result['sources']);target['gaps'].extend(result['gaps'])
    return merged


def supplement_review_view(supplement):
    """Bound review context: full coverage stays in its independently checked artifact."""
    view={key:supplement[key] for key in ('identity','research','receipts','source_extracts')}
    coverage=supplement.get('coverage_evidence_only')
    if isinstance(coverage,dict):
        fields=('edition_date','recorded_at','agreed_source_coverage_status','required_attempts_status','upstream_reconciliation_status','global_full_window_cursor_advanced','claims_exhaustive','public_disclosure')
        summary={key:(value[:2000] if isinstance(value,str) else value) for key in fields if isinstance((value:=coverage.get(key)),(str,int,float,bool))}
        summary['tracked_source_rows']=len(coverage.get('sources',[])) if isinstance(coverage.get('sources'),list) else None
        summary['scope']='Summary only; full hash-bound coverage artifact must be reviewed separately. This does not establish editorial or release approval.'
        view['coverage_summary']=summary
    return view
