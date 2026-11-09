"""Bounded anonymous public-source attempts; never proves timeline coverage.

No credentials, cookies, browser sessions, authentication or access workarounds.
Returned observations are private runtime artifacts, not repository content.
"""
from __future__ import annotations
import hashlib
import re
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, HTTPRedirectHandler, ProxyHandler, build_opener

HOSTS = frozenset(('xstarterpack.com', 'x.com', 'www.x.com', 'twitter.com', 'www.twitter.com'))
PROFILE_HOSTS = HOSTS - {'xstarterpack.com'}
RESERVED = frozenset(('home', 'search', 'intent', 'i', 'login', 'logout', 'signup', 'explore', 'settings', 'messages', 'notifications', 'compose', 'share', 'tos', 'privacy', 'about'))
MAX_BYTES = 1_000_000

def now():
    return datetime.now(timezone.utc).isoformat()

def allowed_url(url):
    try:
        p = urlsplit(url)
        return (p.scheme == 'https' and p.hostname in HOSTS and p.port in (None, 443)
                and not p.username and not p.password and not p.query and not p.fragment)
    except (TypeError, ValueError):
        return False

class RestrictedRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not allowed_url(newurl):
            raise ValueError('Redirect outside permitted public URL scope')
        return super().redirect_request(req, fp, code, msg, headers, newurl)

class RosterParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.handles = set()
    def handle_starttag(self, tag, attrs):
        if tag != 'a': return
        url = dict(attrs).get('href', '')
        if not allowed_url(url): return
        p = urlsplit(url)
        handle = p.path.strip('/')
        if p.hostname in PROFILE_HOSTS and re.fullmatch(r'[A-Za-z0-9_]{1,15}', handle) and handle.lower() not in RESERVED:
            self.handles.add(handle.lower())

def parse_roster(body):
    parser = RosterParser(); parser.feed(body.decode('utf-8', errors='replace'))
    return sorted(parser.handles)

def classify(status, body):
    text = body.decode('utf-8', errors='replace').lower()
    challenge = any(x in text for x in ('verify you are human', 'captcha', 'checking your browser', 'access denied', 'automated requests'))
    if status == 429: return 'blocked', 'rate_limit', True
    if challenge or status in (401, 403): return 'blocked', 'security_or_access_restriction', True
    if status is None or status >= 400: return 'blocked', 'http_or_transport_error', False
    if any(x in text for x in ('log in to x', 'sign in to x', 'sign in to twitter', 'javascript is not available')):
        return 'blocked', 'login_or_script_required', False
    return 'header_only', 'public_response_not_timeline_verified', False

def fetch_public(url, timeout=10, max_bytes=MAX_BYTES):
    if not allowed_url(url): raise ValueError('URL outside permitted public scope')
    if not 0 < timeout <= 30 or not 0 < max_bytes <= MAX_BYTES: raise ValueError('Unsafe request limits')
    started = now(); body = b''; status = None; final_url = url; error = None; truncated = False
    # Ignore environment proxy settings and never install a cookie/auth handler.
    opener = build_opener(ProxyHandler({}), RestrictedRedirect())
    request = Request(url, headers={'User-Agent': 'BriefPublicSourceIntake/1.0', 'Accept': 'text/html'})
    try:
        try: response = opener.open(request, timeout=timeout)
        except HTTPError as exc: response = exc
        with response:
            status = response.code
            final_url = response.geturl()
            if not allowed_url(final_url): raise ValueError('Response URL outside scope')
            body = response.read(max_bytes + 1)
            truncated = len(body) > max_bytes
            body = body[:max_bytes]
    except (URLError, OSError, ValueError) as exc:
        error = type(exc).__name__  # Do not leak arbitrary URLs or environment details.
    completed = now()
    access, outcome, stop = classify(status, body)
    if error: access, outcome = 'blocked', 'transport_or_redirect_blocked'
    return {'url': url, 'final_url': final_url, 'started_at': started, 'completed_at': completed,
            'status': status, 'error': error, 'access_status': access, 'outcome': outcome,
            'stop': stop, 'body_sha256': hashlib.sha256(body).hexdigest(), 'body_bytes': len(body),
            'body_truncated': truncated, 'body': body}

def collect_public_roster_intake(edition_date, prior_coverage=None, *, fetch=fetch_public,
                                max_profiles=250, deadline_seconds=600, delay_seconds=1, sleep=time.sleep):
    """Sequential (concurrency=1), bounded collection. No CLI or automatic run.

    Parsing visible links is NOT proof of full roster enumeration. Integration
    must independently verify snapshot completeness before treating its roster
    as the mandatory denominator. Missing cursor history remains a blocker.
    """
    if not 1 <= max_profiles <= 500 or not 0 < deadline_seconds <= 3600 or not 0 <= delay_seconds <= 10:
        raise ValueError('Unsafe batch limits')
    begin = time.monotonic(); snapshot = fetch('https://xstarterpack.com/')
    observations = [{k:v for k,v in snapshot.items() if k != 'body'}]
    handles = parse_roster(snapshot['body']) if snapshot['status'] == 200 and snapshot['access_status'] != 'blocked' and not snapshot['stop'] else []
    blockers = ['Roster completeness requires independent verification; extracted links alone are insufficient.']
    prior = {row['source_id']: row for row in (prior_coverage or {}).get('sources', [])}
    stopped = snapshot['stop'] or not handles or snapshot['body_truncated']
    rows = []
    for index, handle in enumerate(handles):
        sid = 'x:' + handle; url = 'https://x.com/' + handle
        history = prior.get(sid, {})
        row = {'source_id': sid, 'roster_member': True, 'roster_snapshot_sha256': snapshot['body_sha256'],
               'access_status': 'unattempted', 'coverage_scope': 'unknown', 'scope_note': 'No complete timeline traversal.',
               'attempts': [], 'queries': [], 'gaps': [], 'advance_full_window_cursor': False,
               'counts': {'discovered':0,'reviewed':0,'pending':0,'retained':0,'excluded':0}}
        for key in ('prior_full_window_cursor', 'oldest_unresolved_gap_start', 'unresolved_window'):
            row[key] = history.get(key)
        if not history:
            blockers.append(sid + ': prior cursor history unavailable')
        if stopped or index >= max_profiles or time.monotonic() - begin >= deadline_seconds:
            row['gaps'] = ['Not attempted: batch stop, roster uncertainty, profile limit or deadline.']
        else:
            event = fetch(url)
            observations.append({k:v for k,v in event.items() if k != 'body'})
            row['access_status'] = event['access_status']
            row['attempts'] = [{'url':url,'at':event['completed_at'],'method':'anonymous HTTPS GET','outcome':event['outcome']}]
            row['gaps'] = ['Timeline and unresolved historical window not reviewed.']
            stopped = event['stop']
            if stopped: blockers.append('Stopped further requests after rate-limit or security challenge.')
            if not stopped and index + 1 < len(handles): sleep(delay_seconds)
        rows.append(row)
    return {'edition_date':edition_date,'recorded_at':now(), 'roster':{'url':'https://xstarterpack.com/',
            'retrieved_at':snapshot['completed_at'],'content_sha256':snapshot['body_sha256'],'handles':handles,'count':len(handles)},
            'roster_completeness_verified':False, 'observations':observations,'sources':rows,'items':[],
            'blockers':blockers,'agreed_source_coverage_status':'partial','global_full_window_cursor_advanced':False,
            'claims_exhaustive':False, 'required_attempts_status':'incomplete',
            'note':'Collector fragment only; not a complete legacy release audit.'}
