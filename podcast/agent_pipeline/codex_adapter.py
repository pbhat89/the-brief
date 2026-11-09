"""Subscription-only Codex CLI adapter. Never reads, copies or logs auth secrets."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import hashlib
import ipaddress
import queue
import threading
from urllib.parse import urlsplit, urlunsplit
import os
from pathlib import Path
import signal
import shutil
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
    tool_trace: tuple[dict[str, Any], ...] = ()


def _environment() -> dict[str, str]:
    # Codex owns its supported subscription login. No API-key fallback or custom endpoint.
    return {k: v for k, v in os.environ.items()
            if not k.upper().startswith(('OPENAI_', 'AZURE_OPENAI_', 'ANTHROPIC_'))
            and k.upper() not in {'CODEX_API_KEY', 'CODEX_BASE_URL'}}


_WINDOWS = os.name == 'nt'


def _native_command(command: list[str]) -> list[str]:
    if not _WINDOWS:
        return command
    executable = shutil.which(command[0])
    if not executable or Path(executable).suffix.lower() != '.exe':
        raise CodexAdapterError('runtime', 'Windows requires the official native codex.exe path; batch shims are not supported.')
    return [str(Path(executable).resolve()), *command[1:]]


def _stop_process_tree(proc: Any, *, drain: bool = True) -> None:
    try:
        if _WINDOWS:
            # Fixed OS executable, numeric PID only. Never compose a shell command.
            taskkill = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32' / 'taskkill.exe'
            stopped = subprocess.run([str(taskkill), '/PID', str(proc.pid), '/T', '/F'],
                                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL, shell=False, timeout=10,
                                     creationflags=0x08000000)
            if stopped.returncode and proc.poll() is None:
                raise OSError('Process tree termination failed')
        else:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        proc.communicate(timeout=5) if drain else proc.wait(timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        raise CodexAdapterError('cleanup', 'Codex timeout cleanup could not be verified; execution stopped.') from None


def _execute(command: list[str], *, cwd: Path, prompt: str = '', timeout: float = 30,
             on_json_event: Callable[[dict[str, Any], str], None] | None = None) -> tuple[int, str, str]:
    command = _native_command(command)
    options = {'creationflags': 0x08000000} if _WINDOWS else {'start_new_session': True}
    try:
        proc = subprocess.Popen(command, cwd=cwd, env=_environment(), text=True,
                                encoding='utf-8', errors='replace', shell=False,
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, **options)
    except OSError:
        raise CodexAdapterError('runtime', 'Codex executable could not be started.') from None
    if on_json_event is not None:
        return _stream_process(proc, prompt, timeout, on_json_event)
    try:
        stdout, stderr = proc.communicate(prompt, timeout=timeout)
    except subprocess.TimeoutExpired:
        _stop_process_tree(proc)
        raise CodexAdapterError('timeout', 'Codex exceeded the configured deadline.') from None
    return proc.returncode, stdout, stderr



_MAX_STREAM_CHARS = 8 * 1024 * 1024
_MAX_LINE_CHARS = 1024 * 1024


def _stream_process(proc, prompt, timeout, callback):
    """Timestamp lines when read; never pretend this is server execution time."""
    messages = queue.Queue(maxsize=256)
    stop = threading.Event()
    def put(message):
        while not stop.is_set():
            try:
                messages.put(message, timeout=.05)
                return
            except queue.Full:
                pass
    def reader(stream, name):
        total = 0
        try:
            while not stop.is_set():
                line = stream.readline(_MAX_LINE_CHARS + 1)
                if not line:
                    break
                observed = datetime.now(timezone.utc).isoformat()
                total += len(line)
                if len(line) > _MAX_LINE_CHARS or total > _MAX_STREAM_CHARS:
                    put(('error', 'limit', observed))
                    return
                put((name, line, observed))
        except Exception:
            put(('error', 'read', None))
        finally:
            put(('done', name, None))
    def writer():
        try:
            proc.stdin.write(prompt)
            proc.stdin.close()
        except Exception:
            put(('error', 'write', None))
    threads = [threading.Thread(target=reader, args=(proc.stdout, 'stdout'), daemon=True),
               threading.Thread(target=reader, args=(proc.stderr, 'stderr'), daemon=True),
               threading.Thread(target=writer, daemon=True)]
    for thread in threads:
        thread.start()
    outputs = {'stdout': [], 'stderr': []}
    deadline = time.monotonic() + timeout
    done = set()
    try:
        while len(done) < 2:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise CodexAdapterError('timeout', 'Codex exceeded the configured deadline.')
            try:
                name, value, observed = messages.get(timeout=min(.1, remaining))
            except queue.Empty:
                continue
            if name == 'error':
                raise CodexAdapterError('runtime', 'Codex stream failed or exceeded its safe size limit.')
            if name == 'done':
                done.add(value)
                continue
            outputs[name].append(value)
            if name == 'stdout':
                try:
                    event = json.loads(value)
                except (ValueError, TypeError):
                    continue
                if isinstance(event, dict):
                    try:
                        callback(event, observed)
                    except Exception:
                        raise CodexAdapterError('audit', 'Live tool evidence could not be recorded.') from None
        proc.wait(timeout=max(.001, deadline - time.monotonic()))
        return proc.returncode, ''.join(outputs['stdout']), ''.join(outputs['stderr'])
    except (subprocess.TimeoutExpired, CodexAdapterError) as error:
        _stop_process_tree(proc, drain=False)
        if isinstance(error, subprocess.TimeoutExpired):
            raise CodexAdapterError('timeout', 'Codex exceeded the configured deadline.') from None
        raise
    finally:
        stop.set()
        for thread in threads:
            thread.join(timeout=1)
        for stream in (proc.stdin, proc.stdout, proc.stderr):
            try:
                stream.close()
            except (OSError, ValueError):
                pass


def _public_url(value):
    """Conservative public provenance: no credentials/query/fragment/private IP."""
    if not isinstance(value, str) or len(value) > 2048:
        return None
    try:
        parts = urlsplit(value)
        host = parts.hostname
        if parts.scheme not in ('https', 'http') or not host or parts.username or parts.password:
            return None
        if host == 'localhost' or '.' not in host or host.endswith(('.local', '.internal')):
            return None
        try:
            if not ipaddress.ip_address(host).is_global:
                return None
        except ValueError:
            pass
        # Query-bearing links can carry personal or credential data. Drop entirely.
        if parts.query or parts.fragment:
            return None
        path = parts.path
        if any(word in path.lower() for word in ('token', 'secret', 'password', 'auth', 'login', 'session', '@', '%40')):
            return None
        if any(len(segment) > 100 for segment in path.split('/')):
            return None
        return urlunsplit((parts.scheme, parts.netloc.lower(), path, '', ''))
    except ValueError:
        return None


def _tool_observation(event, observed_at, attempt):
    item = event.get('item')
    if event.get('type') not in ('item.started', 'item.completed') or not isinstance(item, dict) or item.get('type') != 'web_search':
        return None
    action = item.get('action') or {}
    if not isinstance(action, dict):
        action = {}
    kind = action.get('type')
    if kind not in ('search', 'open_page', 'find_in_page'):
        kind = 'unknown'
    query = action.get('query')
    url = _public_url(action.get('url')) if kind in ('open_page', 'find_in_page') else None
    item_id = item.get('id')
    # Item IDs are identifiers, not arbitrary model text.
    if not isinstance(item_id, str) or len(item_id) > 128 or not all(c.isalnum() or c in '_-' for c in item_id):
        item_id = None
    ref_id = action.get('ref_id')
    if not isinstance(ref_id, str) or len(ref_id) > 128 or not all(c.isalnum() or c in '_-' for c in ref_id):
        ref_id = None
    return {'ref_id': ref_id, 'status': item.get('status') if item.get('status') in ('completed', 'failed', 'in_progress') else None,
            'trace_id': hashlib.sha256(json.dumps([attempt, item_id, event['type'], observed_at]).encode()).hexdigest(),
            'item_id': item_id, 'attempt': attempt, 'event': event['type'],
            'action': kind, 'observed_at': observed_at, 'timestamp_basis': 'adapter_observed',
            'url': url, 'query_sha256': hashlib.sha256(query.encode()).hexdigest() if isinstance(query, str) else None}


def _tool_observations(event, observed_at, attempt):
    """Expand explicit completed open results, never promote search discoveries.

    Batch results share the line's adapter-observed timestamp, not an invented
    per-page fetch time. Titles/text are deliberately excluded from the trace.
    """
    primary = _tool_observation(event, observed_at, attempt)
    if primary is None:
        return []
    item = event['item']
    if (event['type'] != 'item.completed' or primary['action'] != 'open_page'
            or primary['status'] == 'failed'):
        return [primary]
    results = item.get('results')
    if not isinstance(results, list):
        return [primary]
    expanded, seen = [], set()
    for result in results:
        if not isinstance(result, dict) or result.get('type') != 'text_result':
            continue
        url = _public_url(result.get('url'))
        ref_id = result.get('ref_id')
        if (not url or not isinstance(ref_id, str) or not ref_id or len(ref_id) > 128
                or not all(c.isalnum() or c in '_-' for c in ref_id)):
            continue
        identity = (url, ref_id)
        if identity in seen:
            continue
        seen.add(identity)
        observation = {**primary, 'url': url, 'ref_id': ref_id,
                       'query_sha256': None}
        observation['trace_id'] = hashlib.sha256(json.dumps(
            [primary['trace_id'], 'open_result', url, ref_id]).encode()).hexdigest()
        expanded.append(observation)
    # The primary URL often represents only the first page in a batch. Prefer
    # its explicit result reference instead of creating a duplicate observation.
    if primary['url'] and not any(row['url'] == primary['url'] for row in expanded):
        expanded.insert(0, primary)
    return expanded or [primary]


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
            raise ValueError('Positive timeout and 1ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“3 attempts required.')
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
        tool_trace = []
        start = time.monotonic()
        for attempt in range(1, self.max_attempts + 1):
            remaining = self.timeout_seconds - (time.monotonic() - start)
            if remaining <= 0:
                raise CodexAdapterError('timeout', 'Codex exceeded the configured deadline.', attempt)
            with tempfile.TemporaryDirectory(prefix='codex-call-', dir=cwd) as temp:
                folder = Path(temp)
                # Windows inherits ACLs: runner provisioning must verify owner-private cwd.
                # chmod is a POSIX permission check, not a Windows privacy claim.
                if not _WINDOWS:
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
                    def observe(event, observed_at):
                        for observation in _tool_observations(event, observed_at, attempt):
                            tool_trace.append(observation)
                            emit({"event":"tool_observation","attempt":attempt,"observation":observation})
                    code, stdout, stderr = _execute(command, cwd=cwd, prompt=prompt, timeout=remaining,
                                                    on_json_event=observe)
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
                    return CodexResult(data, usage, searches, attempt, self.model, time.monotonic() - start, tuple(tool_trace))
                except CodexAdapterError as error:
                    error.attempts = attempt
                    error.tool_trace = tuple(tool_trace)
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
