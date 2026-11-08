import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from podcast.agent_pipeline.codex_adapter import CodexAdapter, CodexAdapterError, _kind, _summary, _environment

SCHEMA = {'type': 'object', 'properties': {'ok': {'type': 'boolean'}}, 'required': ['ok'], 'additionalProperties': False}

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.calls = []

    def fake(self, command, **kwargs):
        self.calls.append((command, kwargs))
        if command[-2:] == ['login', 'status']:
            return 0, 'Logged in using ChatGPT', ''
        Path(command[command.index('--output-last-message') + 1]).write_text('{"ok":true}')
        return 0, '\n'.join([json.dumps({'type':'item.completed','item':{'type':'web_search','id':'s1'}}), json.dumps({'type':'turn.completed','usage':{'input_tokens':10,'output_tokens':3}})]), ''

    @patch('podcast.agent_pipeline.codex_adapter._execute')
    def test_success(self, execute):
        execute.side_effect = self.fake
        r = CodexAdapter().run('Test', SCHEMA, self.tmp.name, require_search=True)
        self.assertEqual(r.data, {'ok': True})
        self.assertEqual(r.search_count, 1)
        self.assertEqual(r.usage['input_tokens'], 10)
        cmd = self.calls[-1][0]
        self.assertIn('read-only', cmd)
        self.assertIn('web_search="live"', cmd)
        self.assertIn('forced_login_method="chatgpt"', cmd)
        self.assertIn('--ephemeral', cmd)
        self.assertEqual(list(Path(self.tmp.name).iterdir()), [])

    @patch('podcast.agent_pipeline.codex_adapter._execute')
    def test_api_login_rejected(self, execute):
        execute.return_value = (0, 'Logged in using an API key', '')
        with self.assertRaises(CodexAdapterError) as ctx:
            CodexAdapter().run('Test', SCHEMA, self.tmp.name)
        self.assertEqual(ctx.exception.kind, 'auth')
        self.assertEqual(execute.call_count, 1)

    @patch('podcast.agent_pipeline.codex_adapter._execute')
    def test_access_does_not_retry(self, execute):
        execute.side_effect = [(0,'Logged in using ChatGPT',''), (1,'','403 Forbidden secret=DO_NOT_LOG')]
        with self.assertRaises(CodexAdapterError) as ctx:
            CodexAdapter().run('Test', SCHEMA, self.tmp.name)
        self.assertEqual(ctx.exception.kind, 'access')
        self.assertNotIn('DO_NOT_LOG', str(ctx.exception))
        self.assertEqual(execute.call_count, 2)

    @patch('podcast.agent_pipeline.codex_adapter.time.sleep')
    @patch('podcast.agent_pipeline.codex_adapter._execute')
    def test_transient_retries(self, execute, sleep):
        n = 0
        def fake(command, **kwargs):
            nonlocal n
            if command[-2:] != ['login','status']:
                n += 1
                if n == 1:
                    return 1, '', '503 temporarily unavailable'
            return self.fake(command, **kwargs)
        execute.side_effect = fake
        r = CodexAdapter().run('Test', SCHEMA, self.tmp.name)
        self.assertEqual(r.attempts, 2)
        sleep.assert_called_once()

    @patch('podcast.agent_pipeline.codex_adapter._execute')
    def test_schema_failure(self, execute):
        def fake(command, **kwargs):
            r = self.fake(command, **kwargs)
            if '--output-last-message' in command:
                Path(command[command.index('--output-last-message') + 1]).write_text('{"ok":"wrong"}')
            return r
        execute.side_effect = fake
        with self.assertRaises(CodexAdapterError) as ctx:
            CodexAdapter().run('Test', SCHEMA, self.tmp.name)
        self.assertEqual(ctx.exception.kind, 'schema')

    @patch('podcast.agent_pipeline.codex_adapter._execute')
    def test_search_is_required(self, execute):
        def fake(command, **kwargs):
            code, out, err = self.fake(command, **kwargs)
            return code, out if command[-2:] == ['login','status'] else '', err
        execute.side_effect = fake
        with self.assertRaises(CodexAdapterError) as ctx:
            CodexAdapter().run('Test', SCHEMA, self.tmp.name, require_search=True)
        self.assertEqual(ctx.exception.kind, 'search')

    def test_environment_filters_secrets_and_endpoints(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY':'secret','CODEX_API_KEY':'secret','OPENAI_BASE_URL':'bad','CODEX_HOME':'/supported/home'}):
            env = _environment()
            self.assertNotIn('OPENAI_API_KEY', env)
            self.assertNotIn('CODEX_API_KEY', env)
            self.assertNotIn('OPENAI_BASE_URL', env)
            self.assertEqual(env['CODEX_HOME'], '/supported/home')

    def test_unknown_usage_is_not_zero(self):
        self.assertEqual(_summary('not json')[0], None)
        self.assertEqual(_kind('Read-only file system'), 'runtime')
        self.assertEqual(_kind('429 quota exceeded'), 'rate_limit')

    @patch('podcast.agent_pipeline.codex_adapter.time.sleep')
    @patch('podcast.agent_pipeline.codex_adapter._execute')
    def test_callback_captures_every_retry(self, execute, sleep):
        events, tries = [], []
        def fake(command, **kwargs):
            if command[-2:] != ['login', 'status']:
                tries.append(1)
                if len(tries) == 1:
                    return 1, '', '503 temporarily unavailable PRIVATE_PAYLOAD'
            return self.fake(command, **kwargs)
        execute.side_effect = fake
        CodexAdapter().run('PRIVATE_PROMPT', SCHEMA, self.tmp.name, on_attempt=events.append)
        self.assertEqual([(e['attempt'],e['status']) for e in events],
                         [(1,'running'),(1,'failed'),(2,'running'),(2,'succeeded')])
        self.assertTrue(events[1]['will_retry'])
        self.assertEqual(events[-1]['usage']['output_tokens'], 3)
        self.assertTrue(all('timestamp' in e for e in events))
        self.assertNotIn('PRIVATE', json.dumps(events))

    @patch('podcast.agent_pipeline.codex_adapter._execute')
    def test_preflight_failure_callback(self, execute):
        execute.return_value = (1, '', 'not logged in')
        events = []
        with self.assertRaises(CodexAdapterError):
            CodexAdapter().run('Test', SCHEMA, self.tmp.name, on_attempt=events.append)
        self.assertEqual(events[0]['event'], 'preflight_failed')
        self.assertEqual(events[0]['attempt'], 0)

    @patch('podcast.agent_pipeline.codex_adapter._execute')
    def test_bad_root_never_invokes_codex(self, execute):
        invalid = [ {'type':'array', 'items':{'type':'string'}},
                    {'type':'object','properties':{'a':{'type':'string'}},'additionalProperties':False},
                    {'type':'object','properties':{},'required':[]} ]
        for schema in invalid:
            with self.subTest(schema=schema), self.assertRaises(CodexAdapterError) as ctx:
                CodexAdapter().run('Test', schema, self.tmp.name)
            self.assertEqual(ctx.exception.kind, 'schema')
        execute.assert_not_called()

    @patch('podcast.agent_pipeline.codex_adapter._execute')
    def test_audit_failure_stops_before_execution(self, execute):
        execute.side_effect = self.fake
        def broken(event):
            raise RuntimeError('private audit error')
        with self.assertRaises(CodexAdapterError) as ctx:
            CodexAdapter().run('Test', SCHEMA, self.tmp.name, on_attempt=broken)
        self.assertEqual(ctx.exception.kind, 'audit')
        self.assertEqual(execute.call_count, 1)
        self.assertNotIn('private audit error', str(ctx.exception))

    def test_invalid_configuration(self):
        with self.assertRaises(ValueError): CodexAdapter(max_attempts=4)
        with self.assertRaises(ValueError): CodexAdapter(timeout_seconds=0)

if __name__ == '__main__': unittest.main()
