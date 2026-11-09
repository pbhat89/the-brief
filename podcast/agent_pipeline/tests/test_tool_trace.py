import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from podcast.agent_pipeline.codex_adapter import _execute, _tool_observation, _public_url, CodexAdapterError

class TraceTests(unittest.TestCase):
    def test_measured_live_jsonl(self):
        events=[]
        script="import sys,time; print('{\"type\":\"item.started\",\"item\":{\"type\":\"web_search\",\"id\":\"x\"}}',flush=True); time.sleep(.2)"
        code,out,err=_execute([sys.executable,'-c',script],cwd=Path.cwd(),on_json_event=lambda e,t:events.append((e,t)),timeout=5)
        self.assertEqual(code,0)
        self.assertEqual(events[0][0]['type'],'item.started')
        self.assertIn('+00:00',events[0][1])

    def test_safe_minimal_observation(self):
        event={'type':'item.completed','item':{'type':'web_search','id':'item_1','action':{'type':'open_page','url':'https://example.org/news'}}}
        row=_tool_observation(event,'2026-11-09T00:00:00+00:00',2)
        self.assertEqual(row['url'],'https://example.org/news')
        self.assertEqual(row['timestamp_basis'],'adapter_observed')
        event['item']['action']={'type':'search','query':'private query','url':'https://example.org/news'}
        row=_tool_observation(event,'now',2)
        self.assertIsNone(row['url'])
        self.assertNotIn('private query',json.dumps(row))
        self.assertEqual(len(row['query_sha256']),64)

    def test_sensitive_urls(self):
        for url in ['http://127.0.0.1/a','https://localhost/a','https://x.local/a','https://user:pass@example.org/a','https://example.org/a?token=secret','https://example.org/auth/secret','https://example.org/a#secret']:
            self.assertIsNone(_public_url(url),url)

    def test_oversize_fails_closed(self):
        with patch('podcast.agent_pipeline.codex_adapter._MAX_LINE_CHARS',64):
            with self.assertRaises(CodexAdapterError):
                _execute([sys.executable,'-c',"print('x'*1000)"],cwd=Path.cwd(),on_json_event=lambda e,t:None,timeout=5)

    def test_callback_failure_stops(self):
        def fail(e,t): raise ValueError('secret')
        with self.assertRaises(CodexAdapterError) as raised:
            _execute([sys.executable,'-c',"print('{}')"],cwd=Path.cwd(),on_json_event=fail,timeout=5)
        self.assertEqual(raised.exception.kind,'audit')
        self.assertNotIn('secret',str(raised.exception))

    def test_timeout(self):
        with self.assertRaises(CodexAdapterError) as raised:
            _execute([sys.executable,'-c',"import time;time.sleep(5)"],cwd=Path.cwd(),on_json_event=lambda e,t:None,timeout=.1)
        self.assertEqual(raised.exception.kind,'timeout')

class AclEncodingTests(unittest.TestCase):
    def test_unicode_acl_path_transport(self):
        from podcast.agent_pipeline.audit import inspect_windows_acl
        from types import SimpleNamespace
        with patch('podcast.agent_pipeline.audit.subprocess.run', return_value=SimpleNamespace(stdout='{}')) as run:
            inspect_windows_acl(Path('भारत') / 'audit.sqlite3')
        self.assertEqual(run.call_args.kwargs['encoding'], 'utf-8')
        self.assertIn('भारत',run.call_args.kwargs['input'])
        self.assertIn('[Console]::InputEncoding', run.call_args.args[0][-1])
        self.assertIn('[Console]::OutputEncoding', run.call_args.args[0][-1])
