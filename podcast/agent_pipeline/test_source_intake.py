import hashlib
import unittest
from unittest.mock import patch
from .source_intake import allowed_url, parse_roster, classify, collect_public_roster_intake, fetch_public, RestrictedRedirect

def event(url, body=b'', status=200, stop=False):
    access, outcome, _ = classify(status, body)
    return dict(url=url, final_url=url, started_at='2026-11-09T01:00:00Z',completed_at='2026-11-09T01:00:01Z',status=status,error=None,
                access_status=access,outcome=outcome,stop=stop,body_sha256=hashlib.sha256(body).hexdigest(),body_bytes=len(body),body_truncated=False,body=body)

class IntakeTests(unittest.TestCase):
    def test_strict_url_scope(self):
        self.assertTrue(allowed_url('https://x.com/Alice'))
        for url in ('http://x.com/a','https://x.com.evil/a','https://user@x.com/a','https://x.com:444/a','https://x.com/a?token=x','https://127.0.0.1/a','https://x.com/a#x'):
            self.assertFalse(allowed_url(url))
    def test_parser(self):
        body=b'<a href="https://x.com/Alice">A</a><a href="https://twitter.com/alice/">A</a><a href="https://x.com/home">H</a><a href="https://x.com/a/status/1">P</a><a href="https://evil.com/b">E</a>'
        self.assertEqual(parse_roster(body), ['alice'])
    def test_status_not_read(self):
        self.assertEqual(classify(200,b'profile'), ('header_only','public_response_not_timeline_verified',False))
        self.assertEqual(classify(200,b'Log in to X')[0], 'blocked')
        self.assertTrue(classify(429,b'')[2]);self.assertTrue(classify(200,b'Verify you are human')[2])
    def test_stop_and_cursor_preservation(self):
        calls=[]
        def fetch(url):
            calls.append(url)
            if 'xstarterpack' in url: return event(url,b'<a href="https://x.com/a">A</a><a href="https://x.com/b">B</a>')
            return event(url,status=429,stop=True)
        prior={'sources':[{'source_id':'x:a','prior_full_window_cursor':'old','oldest_unresolved_gap_start':'older','unresolved_window':{'start':'older','end':'end'}}]}
        out=collect_public_roster_intake('2026-11-09',prior,fetch=fetch,sleep=lambda _:None)
        self.assertEqual(len(calls),2)
        self.assertEqual(out['sources'][0]['prior_full_window_cursor'],'old')
        self.assertEqual(out['sources'][1]['access_status'],'unattempted')
        self.assertFalse(out['global_full_window_cursor_advanced']);self.assertFalse(out['roster_completeness_verified'])
        self.assertNotIn('body',out['observations'][0])
    def test_limits_and_no_fabricated_history(self):
        def fetch(url): return event(url,b'<a href="https://x.com/a">A</a><a href="https://x.com/b">B</a>')
        out=collect_public_roster_intake('2026-11-09',fetch=fetch,max_profiles=1,sleep=lambda _:None)
        self.assertIsNone(out['sources'][0]['prior_full_window_cursor'])
        self.assertEqual(out['sources'][1]['attempts'],[])
        self.assertEqual(out['required_attempts_status'],'incomplete')
        with self.assertRaises(ValueError): collect_public_roster_intake('2026-11-09',max_profiles=999)
    def test_redirect_rejected(self):
        with self.assertRaises(ValueError): RestrictedRedirect().redirect_request(None,None,302,'',{},'https://evil.com/')
    def test_transport_has_no_cookies_and_bounds_body(self):
        from . import source_intake as module
        class Response:
            code=200
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def geturl(self): return 'https://x.com/a'
            def read(self,n):
                self.requested=n
                return b'x'*n
        response=Response()
        class Opener:
            def open(self,request,timeout):
                self.request=request
                return response
        opener=Opener()
        with patch.object(module,'build_opener',return_value=opener) as build:
            out=fetch_public('https://x.com/a',max_bytes=8)
        self.assertEqual(response.requested,9)
        self.assertTrue(out['body_truncated'])
        self.assertEqual(out['body_sha256'],hashlib.sha256(b'x'*8).hexdigest())
        self.assertFalse(any(k.lower() in ('cookie','authorization') for k in opener.request.headers))
        self.assertEqual(len(build.call_args.args),2)
        self.assertTrue(classify(403,b'')[2])

    def test_request_bounds(self):
        with self.assertRaises(ValueError): fetch_public('https://x.com/a',timeout=0)
        with self.assertRaises(ValueError): fetch_public('https://x.com/a',max_bytes=9999999)

if __name__=='__main__': unittest.main()
