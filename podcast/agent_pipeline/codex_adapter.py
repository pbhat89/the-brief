"""Subscription-only Codex CLI adapter. Never reads, copies or logs auth secrets."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
from typing import Any, Callable


class CodexAdapterError(RuntimeError):
    def __init__(self, kind: str, message: str, attempts: int = 1):
        self.kind, self.attempts = kind, attempts
        super().__init__(message)


@dataclass(frozen=True)
class CodexResult:
    data: dict[str, Any]
    usage: dict[str, int] | None
    search_count: int
    attempts: int
    model: str | None
    duration_seconds: float


def _environment() -> dict[str, str]:
    # Codex owns its supported subscription login. No API-key fallback or custom endpoint.
    return {k: v for k, v in os.environ.items()
            if not k.startswith(('OPENAI_', 'AZURE_OPENAI_', 'ANTHROPIC_'))
            and k not in {'CODEX_API_KEY', 'CODEX_BASE_URL'}}


def _execute(command: list[str], *, cwd: Path, prompt: str = '', timeout: float = 30) -> tuple[int, str, str]:
    try:
        proc = subprocess.Popen(command, cwd=cwd, env=_environment(), text=True,
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, start_new_session=True)
    except OSError:
        raise CodexAdapterError('runtime', 'Codex executable could not be started.') from None
    try:
        stdout, stderr = proc.communicate(prompt, timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.communicate()
        raise CodexAdapterError('timeout', 'Codex exceeded the configured deadline.') from None
    return proc.returncode, stdout, stderr


def _kind(message: str) -> str:
    value = message.lower()
    if any(s in value for s in ('read-only file system', 'failed to initialize', 'permission denied')):
        return 'runtime'
    if any(s in value for s in ('unauthorized', '401', 'login required', 'not logged in', 'authentication')):
        return 'auth'
    if any(s in value for s in ('403', 'forbidden', 'access denied', 'security warning')):
        return 'access'
    if any(s in value for s in ('usage limit', 'quota', 'rate limit', '429')):
        return 'rate_limit'
    if any(s in value for s in ('502', '503', '504', 'temporarily unavailable', 'connection reset', 'timed out')):
        return 'transient'
    return 'runtime'


def _summary(stdout: str) -> tuple[dict[str, int] | None, int, bool]:
    usage, searches, failed = None, set(), False
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except (ValueError, TypeError):
            continue
        if event.get('type') == 'turn.completed':
            raw = event.get('usage') or {}
            usage = {k: v for k, v in raw.items() if isinstance(v, int) and not isinstance(v, bool) and v >= 0}
        if event.get('type') in ('turn.failed', 'error'):
            failed = True
        item = event.get('item') or {}
        if item.get('type') == 'web_search' and event.get('type') == 'item.completed':
            searches.add(item.get('id') or str(len(searches)))
    return usage, len(searches), failed


class CodexAdapter:
    def __init__(self, model: str | None = None, timeout_seconds: float = 240,
                 max_attempts: int = 3, executable: str = 'codex'):
        if timeout_seconds <= 0 or not 1 <= max_attempts <= 3:
            raise ValueError('Positive timeout and 1–3 attempts required.')
        self.model, self.timeout_seconds = model, timeout_seconds
        self.max_attempts, self.executable = max_attempts, executable

    def preflight(self, cwd: str | Path) -> None:
        code, stdout, stderr = _execute([self.executable, 'login', 'status'], cwd=Path(cwd), timeout=20)
        if code or 'logged in using chatgpt' not in (stdout + stderr).lower():
            raise CodexAdapterError('auth', 'A supported ChatGPT subscription login is required; API-key fallback is disabled.')

    def run(self, prompt: str, schema: dict[str, Any], cwd: str | Path,
            require_search: bool = False,
            on_attempt: Callable[[dict[str, Any]], None] | None = None) -> CodexResult:
        from jsonschema import Draft202012Validator, ValidationError
        Draft202012Validator.check_schema(schema)
        # Codex output schemas use the OpenAI structured-output object-root contract.
        # Reject incompatible roots locally, before consuming subscription usage.
        if schema.get('type') != 'object' or any(k in schema for k in ('anyOf', 'oneOf', 'allOf')):
            raise CodexAdapterError('schema', 'Codex output schema must have a direct object root.')
        if schema.get('additionalProperties') is not False:
            raise CodexAdapterError('schema', 'Codex object-root schema must prohibit additional properties.')
        if set(schema.get('required', [])) != set(schema.get('properties', {})):
            raise CodexAdapterError('schema', 'All Codex object-root properties must be required; use nullable fields for optional values.')

        def emit(event: dict[str, Any]) -> None:
            if on_attempt is not None:
                # No prompt, response, raw error, source query, path or credential.
                event['timestamp'] = datetime.now(timezone.utc).isoformat()
                event['model'] = self.model
                try:
                    on_attempt(event)
                except Exception:
                    raise CodexAdapterError('audit', 'Attempt metadata could not be recorded; execution stopped.') from None
        cwd = Path(cwd).resolve()
        if not cwd.is_dir():
            raise ValueError('cwd must be an existing private work directory.')
        try:
            self.preflight(cwd)
        except CodexAdapterError as error:
            emit({'event': 'preflight_failed', 'attempt': 0, 'status': 'failed',
                  'error_kind': error.kind, 'usage': None, 'search_count': 0,
                  'will_retry': False})
            raise
        start = time.monotonic()
        for attempt in range(1, self.max_attempts + 1):
            remaining = self.timeout_seconds - (time.monotonic() - start)
            if remaining <= 0:
                raise CodexAdapterError('timeout', 'Codex exceeded the configured deadline.', attempt)
            with tempfile.TemporaryDirectory(prefix='codex-call-', dir=cwd) as temp:
                folder = Path(temp)
                folder.chmod(0o700)
                schema_file, output_file = folder / 'schema.json', folder / 'result.json'
                schema_file.write_text(json.dumps(schema), encoding='utf-8')
                command = [self.executable, '-a', 'never', 'exec', '--ephemeral', '--ignore-user-config',
                           '--json', '--sandbox', 'read-only', '--skip-git-repo-check',
                           '-c', 'forced_login_method="chatgpt"', '-c', 'features.shell_tool=false',
                           '-c', 'web_search="live"' if require_search else 'web_search="disabled"',
                           '--output-schema', str(schema_file), '--output-last-message', str(output_file)]
                if self.model:
                    command += ['--model', self.model]
                command += ['-']
                attempt_start = time.monotonic()
                usage, searches = None, 0
                emit({'event': 'attempt_started', 'attempt': attempt, 'status': 'running',
                      'usage': None, 'search_count': 0})
                try:
                    code, stdout, stderr = _execute(command, cwd=cwd, prompt=prompt, timeout=remaining)
                    usage, searches, failed = _summary(stdout)
                    if code or failed:
                        kind = _kind(stderr + '\n' + stdout)
                        raise CodexAdapterError(kind, f'Codex execution failed ({kind}); raw output is not logged.', attempt)
                    try:
                        data = json.loads(output_file.read_text(encoding='utf-8'))
                        Draft202012Validator(schema).validate(data)
                    except (OSError, ValueError, ValidationError):
                        raise CodexAdapterError('schema', 'Codex output failed the required JSON schema.', attempt) from None
                    if not isinstance(data, dict):
                        raise CodexAdapterError('schema', 'Codex output must be a JSON object.', attempt)
                    if require_search and searches == 0:
                        raise CodexAdapterError('search', 'Required live search was not observed.', attempt)
                    emit({'event': 'attempt_finished', 'attempt': attempt, 'status': 'succeeded',
                          'duration_seconds': time.monotonic() - attempt_start,
                          'usage': usage, 'search_count': searches, 'will_retry': False})
                    return CodexResult(data, usage, searches, attempt, self.model, time.monotonic() - start)
                except CodexAdapterError as error:
                    error.attempts = attempt
                    # No auth/access/quota retries, no paid or alternate-provider fallback.
                    retry = error.kind == 'transient' and attempt < self.max_attempts and time.monotonic() - start < self.timeout_seconds
                    if error.kind != 'audit':
                        emit({'event': 'attempt_finished', 'attempt': attempt, 'status': 'failed',
                              'error_kind': error.kind, 'duration_seconds': time.monotonic() - attempt_start,
                              'usage': usage, 'search_count': searches, 'will_retry': retry})
                    if not retry:
                        raise
                    delay = min(2 ** attempt, max(0, self.timeout_seconds - (time.monotonic() - start)))
                    time.sleep(delay)
        raise AssertionError('Unreachable')
