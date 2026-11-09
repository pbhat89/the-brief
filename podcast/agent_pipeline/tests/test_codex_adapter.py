import json
import os
from pathlib import Path
import tempfile
import subprocess
import unittest
from unittest.mock import patch, Mock

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
    def test_observation_callback_precedes_process_completion(self, execute):
        events=[]
        def fake(command, **kwargs):
            if '--output-last-message' in command:
                kwargs['on_json_event']({'type':'item.completed','item':{'type':'web_search','id':'open-1','action':{'type':'open_page','url':'https://example.org/news'}}},'2026-11-09T07:00:00+00:00')
                self.assertTrue(any(e.get('event')=='tool_observation' for e in events))
                self.assertFalse(any(e.get('event')=='attempt_succeeded' for e in events))
            return self.fake(command, **kwargs)
        execute.side_effect=fake
        result=CodexAdapter().run('Test',SCHEMA,self.tmp.name,on_attempt=events.append)
        self.assertEqual(len(result.tool_trace),1)
        self.assertEqual(result.tool_trace[0]['observed_at'],'2026-11-09T07:00:00+00:00')

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

class PortabilityTests(unittest.TestCase):
    def test_windows_rejects_batch_shim(self):
        from podcast.agent_pipeline.codex_adapter import _native_command
        for executable in ('codex.cmd', 'codex.bat', None):
            with patch('podcast.agent_pipeline.codex_adapter._WINDOWS', True), patch('podcast.agent_pipeline.codex_adapter.shutil.which', return_value=executable):
                with self.assertRaises(CodexAdapterError):
                    _native_command(['codex', 'exec'])

    def test_native_arguments_remain_list_and_utf8(self):
        from podcast.agent_pipeline.codex_adapter import _execute
        proc = Mock(returncode=0)
        proc.communicate.return_value = ('news', '')
        command = ["C:/Users/Prateek's Pad/codex.exe", 'exec', '-']
        with patch('podcast.agent_pipeline.codex_adapter._WINDOWS', True), patch('podcast.agent_pipeline.codex_adapter._native_command', return_value=command), patch('podcast.agent_pipeline.codex_adapter.subprocess.Popen', return_value=proc) as popen:
            _execute(command, cwd=Path.cwd(), prompt='Unicode: \u092d\u093e\u0930\u0924')
        args, kw = popen.call_args
        self.assertEqual(args[0], command)
        self.assertFalse(kw['shell'])
        self.assertEqual(kw['encoding'], 'utf-8')
        self.assertEqual(kw['creationflags'], 0x08000000)
        self.assertNotIn('start_new_session', kw)
        self.assertIn('\u092d', proc.communicate.call_args.args[0])

    def test_windows_tree_cleanup_is_bounded(self):
        from podcast.agent_pipeline.codex_adapter import _stop_process_tree
        proc = Mock(pid=1234)
        with patch('podcast.agent_pipeline.codex_adapter._WINDOWS', True), patch('podcast.agent_pipeline.codex_adapter.subprocess.run', return_value=Mock(returncode=0)) as run:
            _stop_process_tree(proc)
        args, kw = run.call_args
        self.assertEqual(args[0][1:], ['/PID', '1234', '/T', '/F'])
        self.assertFalse(kw['shell'])
        self.assertEqual(kw['timeout'], 10)
        self.assertEqual(kw['creationflags'], 0x08000000)
        proc.communicate.assert_called_once_with(timeout=5)

    def test_failed_cleanup_is_not_retryable(self):
        from podcast.agent_pipeline.codex_adapter import _stop_process_tree
        proc = Mock(pid=1234)
        proc.poll.return_value = None
        with patch('podcast.agent_pipeline.codex_adapter._WINDOWS', True), patch('podcast.agent_pipeline.codex_adapter.subprocess.run', return_value=Mock(returncode=1)):
            with self.assertRaises(CodexAdapterError) as ctx:
                _stop_process_tree(proc)
        self.assertEqual(ctx.exception.kind, 'cleanup')

    def test_timeout_returns_classified_error(self):
        from podcast.agent_pipeline.codex_adapter import _execute
        proc = Mock()
        proc.communicate.side_effect = subprocess.TimeoutExpired('codex', 1)
        with patch('podcast.agent_pipeline.codex_adapter._native_command', return_value=['codex']), patch('podcast.agent_pipeline.codex_adapter.subprocess.Popen', return_value=proc), patch('podcast.agent_pipeline.codex_adapter._stop_process_tree') as stop:
            with self.assertRaises(CodexAdapterError) as ctx:
                _execute(['codex'], cwd=Path.cwd(), timeout=1)
        self.assertEqual(ctx.exception.kind, 'timeout')
        stop.assert_called_once_with(proc)

    def test_posix_process_group_retained(self):
        from podcast.agent_pipeline.codex_adapter import _execute, _stop_process_tree
        proc = Mock(returncode=0, pid=1234)
        proc.communicate.return_value = ('ok', '')
        with patch('podcast.agent_pipeline.codex_adapter._WINDOWS', False), patch('podcast.agent_pipeline.codex_adapter.subprocess.Popen', return_value=proc) as popen:
            _execute(['codex'], cwd=Path.cwd())
        self.assertTrue(popen.call_args.kwargs['start_new_session'])
        self.assertNotIn('creationflags', popen.call_args.kwargs)
        with patch('podcast.agent_pipeline.codex_adapter._WINDOWS', False), patch('podcast.agent_pipeline.codex_adapter.os.killpg', create=True) as kill, patch('podcast.agent_pipeline.codex_adapter.signal.SIGKILL', 9, create=True):
            _stop_process_tree(proc)
        kill.assert_called_once_with(1234, 9)

    def test_environment_keys_are_case_insensitive(self):
        with patch('podcast.agent_pipeline.codex_adapter.os.environ', {'OpenAi_Api_Key':'secret', 'codex_api_key':'secret', 'Safe':'yes'}):
            self.assertEqual(_environment(), {'Safe':'yes'})

if __name__ == '__main__': unittest.main()
