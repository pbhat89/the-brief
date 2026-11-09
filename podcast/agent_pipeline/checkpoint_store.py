"""Immutable per-role checkpoints. No prompts, credentials, or inferred resume evidence."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import date, datetime
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
from typing import Callable


class CheckpointError(RuntimeError):
    pass


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def _hash(value):
    return hashlib.sha256(_canonical(value)).hexdigest()


@dataclass(frozen=True)
class CheckpointKey:
    run_id: str
    role: str
    edition_date: str
    context_hash: str
    prompt_hash: str
    schema_hash: str
    runtime_source_hash: str

    def __post_init__(self):
        for label in ("run_id", "role"):
            if not re.fullmatch(r"[A-Za-z0-9_-]{1,120}", getattr(self, label)):
                raise ValueError("Invalid checkpoint identifier")
        if date.fromisoformat(self.edition_date).isoformat() != self.edition_date:
            raise ValueError("Invalid edition date")
        for label in ("context_hash", "prompt_hash", "schema_hash", "runtime_source_hash"):
            if not re.fullmatch(r"[0-9a-f]{64}", getattr(self, label)):
                raise ValueError("Checkpoint input hashes must be SHA256")


def _posix_private(path):
    if os.name == "nt":
        return False  # Windows callers must supply a real ACL verifier.
    info = path.stat()
    return info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) & 0o077 == 0


def _trace(entries):
    # Strict metadata whitelist: never persist query text, prompt, output, raw error or auth.
    allowed = {"event", "attempt", "status", "timestamp", "duration_seconds", "usage",
               "search_count", "error_kind", "will_retry", "model",
               "trace_id", "item_id", "action", "observed_at", "timestamp_basis",
               "url", "query_sha256", "ref_id"}
    if not isinstance(entries, list):
        raise ValueError("Tool trace must be a list")
    for item in entries:
        if not isinstance(item, dict) or set(item) - allowed:
            raise ValueError("Tool trace contains unsupported metadata")
        if set(item) & {'trace_id','item_id','action','observed_at','timestamp_basis','url','query_sha256','ref_id'}:
            required = {'trace_id','item_id','attempt','event','action','observed_at',
                        'timestamp_basis','url','query_sha256','ref_id','status'}
            if set(item) != required:
                raise ValueError("Incomplete or mixed tool observation")
            if item['event'] not in ('item.started','item.completed') or item['action'] not in ('search','open_page','find_in_page','unknown'):
                raise ValueError("Unknown observation semantics")
            if item['timestamp_basis'] != 'adapter_observed' or type(item['attempt']) is not int or item['attempt'] < 1:
                raise ValueError("Invalid observation provenance")
            if item['status'] not in (None,'completed','failed','in_progress'):
                raise ValueError("Invalid observation status")
            observed=datetime.fromisoformat(item['observed_at'])
            if observed.tzinfo is None:
                raise ValueError("Observation timestamp must be timezone-aware")
            for field in ('trace_id','query_sha256'):
                value=item[field]
                if not (field=='query_sha256' and value is None) and (not isinstance(value,str) or not re.fullmatch(r'[0-9a-f]{64}',value)):
                    raise ValueError("Invalid observation hash")
            for field in ('item_id','ref_id'):
                value=item[field]
                if value is not None and (not isinstance(value,str) or not value or len(value)>128 or not all(c.isalnum() or c in '_-' for c in value)):
                    raise ValueError("Invalid observation identifier")
            if item['url'] is not None:
                from .codex_adapter import _public_url
                if item['action'] not in ('open_page','find_in_page') or _public_url(item['url']) != item['url']:
                    raise ValueError("Unsafe observation URL")
        for name, value in item.items():
            if name == "usage":
                if value is not None and (not isinstance(value, dict) or
                        any(k not in {"input_tokens", "output_tokens", "cached_input_tokens", "reasoning_output_tokens", "total_tokens"}
                            or type(v) is not int or v < 0 for k, v in value.items())):
                    raise ValueError("Invalid usage metadata")
            elif not isinstance(value, (str, int, float, bool, type(None))) or isinstance(value, str) and len(value) > (2048 if name == 'url' else 160):
                raise ValueError("Invalid trace metadata")
    return entries


class CheckpointStore:
    def __init__(self, private_dir: str | Path, privacy_verifier: Callable[[Path], bool] | None = None):
        self.directory = Path(private_dir).absolute()
        self.verify_private = privacy_verifier or _posix_private
        self._check_private()

    def _check_private(self):
        if self.directory.is_symlink() or self.directory.resolve() != self.directory or not self.directory.is_dir():
            raise CheckpointError("Checkpoint directory must be an existing non-linked private directory")
        try:
            private = self.verify_private(self.directory)
        except Exception:
            raise CheckpointError("Private directory verification failed") from None
        if private is not True:
            raise CheckpointError("Verified private directory required")

    def _path(self, key):
        if not isinstance(key, CheckpointKey):
            raise TypeError("CheckpointKey required")
        return self.directory / (_hash(asdict(key)) + ".json")

    def load(self, key: CheckpointKey):
        """Return result, tool_trace and payload_hash only for the exact verified key, else None."""
        self._check_private()
        path = self._path(key)
        if path.is_symlink():
            raise CheckpointError("Linked checkpoint rejected")
        try:
            with path.open("rb") as handle:
                if os.fstat(handle.fileno()).st_size > 16 * 1024 * 1024:
                    raise CheckpointError("Checkpoint exceeds size limit")
                record = json.load(handle)
        except FileNotFoundError:
            return None
        except (OSError, ValueError):
            raise CheckpointError("Checkpoint cannot be decoded") from None
        try:
            if set(record) != {"version", "key", "payload", "payload_hash"} or record["version"] != 1:
                raise ValueError()
            if record["key"] != asdict(key) or record["payload_hash"] != _hash(record["payload"]):
                raise ValueError()
            payload = record["payload"]
            if set(payload) != {"result", "tool_trace"} or not isinstance(payload["result"], dict):
                raise ValueError()
            _trace(payload["tool_trace"])
        except (ValueError, TypeError, KeyError):
            raise CheckpointError("Checkpoint integrity or identity verification failed") from None
        return {**payload, "payload_hash": record["payload_hash"]}

    def save(self, key: CheckpointKey, result: dict, tool_trace: list) -> str:
        """Commit once atomically; identical repeat is idempotent, conflicting output fails closed."""
        self._check_private()
        if not isinstance(result, dict):
            raise ValueError("Structured result object required")
        payload = {"result": result, "tool_trace": _trace(tool_trace)}
        digest = _hash(payload)
        record = {"version": 1, "key": asdict(key), "payload": payload, "payload_hash": digest}
        encoded = _canonical(record)
        if len(encoded) > 16 * 1024 * 1024:
            raise CheckpointError("Checkpoint exceeds size limit")
        path = self._path(key)
        existing = self.load(key)
        if existing is not None:
            if existing["payload_hash"] != digest:
                raise CheckpointError("Immutable checkpoint conflict")
            return digest
        fd, temp = tempfile.mkstemp(prefix=".checkpoint-", dir=self.directory)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            self._check_private()
            try:
                # Same-filesystem hard-link publish is atomic and cannot replace an existing file.
                os.link(temp, path)
            except FileExistsError:
                winner = self.load(key)
                if winner is None or winner["payload_hash"] != digest:
                    raise CheckpointError("Immutable checkpoint conflict") from None
            except OSError:
                raise CheckpointError("Atomic checkpoint publication unavailable") from None
        finally:
            Path(temp).unlink(missing_ok=True)
        return digest
