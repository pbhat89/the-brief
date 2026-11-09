"""Private append-only pipeline telemetry and human-readable workbook exports.

This database is operational metadata, NOT an LLM chain-of-thought store. Never
pass credentials, raw prompts, private user logs, recordings, or authentication
payloads. Redaction is a second line of defence, not a substitute for that rule.
Hashes detect accidental edits but are not signatures against a database owner.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
from datetime import datetime, timezone
from threading import RLock
from typing import Any
from uuid import uuid4

REDACTED = "[REDACTED]"
_SECRET_KEY = re.compile(r"(?:password|passwd|secret|authorization|cookie|api[_-]?key|access[_-]?token|refresh[_-]?token|id[_-]?token|credential|private[_-]?key|bearer)", re.I)
_PRIVATE_KEY = re.compile(r"^(?:prompt|raw_prompt|system_prompt|raw_response|chain_of_thought|reasoning|transcript|audio|recording|user_log|supporting_passage|excerpt)$", re.I)
_SECRET_TEXT = re.compile(r"(?i)(?:bearer\s+[a-z0-9._~+/=-]+|sk-[a-z0-9_-]{12,}|eyJ[a-z0-9_-]+\.[a-z0-9_-]+\.[a-z0-9_-]+|(?:password|api[_-]?key|access[_-]?token|refresh[_-]?token|secret)\s*[:=]\s*[^\s,;]+)")
_URL_SECRET = re.compile(r"(?i)([?&](?:token|key|secret|code|signature|sig|password|access_token|api_key)=)[^&#\s]+")
_ENTITY_KINDS = {"attempt", "source", "claim", "evidence", "checkpoint", "artifact", "metric"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sanitize(value: Any, key: str = "") -> Any:
    """Remove secret values and raw model/private content, preserving metrics."""
    if _SECRET_KEY.search(key) or _PRIVATE_KEY.fullmatch(key):
        return REDACTED
    if isinstance(value, dict):
        return {str(k): sanitize(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitize(v) for v in value]
    if isinstance(value, str):
        if "-----BEGIN" in value and "PRIVATE KEY-----" in value:
            return REDACTED
        return _URL_SECRET.sub(lambda m: m[1] + REDACTED, _SECRET_TEXT.sub(REDACTED, value))
    if value is None or isinstance(value, (bool, int, float)):
        return value
    raise TypeError(f"Audit value {type(value).__name__} is not JSON metadata")


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _parse_time(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Audit timestamps must include a timezone")
    return dt.astimezone(timezone.utc)


def elapsed_seconds(started_at: str | None, ended_at: str | None) -> float | None:
    if not started_at or not ended_at:
        return None
    seconds = (_parse_time(ended_at) - _parse_time(started_at)).total_seconds()
    if seconds < 0:
        raise ValueError("ended_at precedes started_at")
    return round(seconds, 6)


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class PrivacyError(PermissionError):
    """Destination privacy cannot be established; no ACL is changed."""


def validate_windows_acl(snapshot: dict) -> None:
    """Conservative ACL validation. Unknown/application SIDs need review.

    Names such as CodexSandboxUsers are not proof of trust. We permit only the
    actual current user, SYSTEM, and built-in Administrators, compared by SID.
    This is not an effective-access calculation: additional Allow ACEs fail
    closed even if another Deny ACE might offset them.
    """
    current = snapshot.get("current_sid")
    if not current or snapshot.get("owner_sid") != current:
        raise PrivacyError("Audit destination is not owned by the current user")
    if snapshot.get("dacl_present") is not True:
        raise PrivacyError("Missing/null DACL does not establish private access")
    allowed = {current, "S-1-5-18", "S-1-5-32-544"}
    for ace in snapshot.get("aces", []):
        if ace.get("type") == "Deny":
            continue
        if ace.get("type") != "Allow" or ace.get("sid") not in allowed:
            raise PrivacyError("Unapproved audit ACL principal: " + str(ace.get("sid", "unknown")))


def inspect_windows_acl(path: str | Path) -> dict:
    """Read NTFS ACL via a literal path passed on stdin, never shell-expanded."""
    script = r"""
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSHOME 'Modules\Microsoft.PowerShell.Security') -ErrorAction Stop
$p = [Console]::In.ReadToEnd()
$a = Get-Acl -LiteralPath $p
$raw = New-Object System.Security.AccessControl.RawSecurityDescriptor($a.Sddl)
$rules = @($a.GetAccessRules($true, $true, [System.Security.Principal.SecurityIdentifier]) | ForEach-Object {
  @{sid=$_.IdentityReference.Value;type=$_.AccessControlType.ToString();rights=[int64]$_.FileSystemRights}
})
@{owner_sid=$a.GetOwner([System.Security.Principal.SecurityIdentifier]).Value;
  current_sid=[System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value;
  dacl_present=($null -ne $raw.DiscretionaryAcl);aces=$rules} | ConvertTo-Json -Depth 5 -Compress
"""
    try:
        result = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
                                input=str(Path(path).absolute()), text=True, capture_output=True,
                                check=True, timeout=20, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return json.loads(result.stdout)
    except (subprocess.SubprocessError, OSError, ValueError) as exc:
        raise PrivacyError("Cannot inspect Windows audit ACL; no data written") from exc


def verify_private_path(path: str | Path) -> None:
    """Validate existing destination without modifying permissions."""
    path = Path(path)
    if path.is_symlink():
        raise PrivacyError("Audit destination must not be a symlink")
    if os.name == "nt":
        validate_windows_acl(inspect_windows_acl(path))
    else:
        info = path.stat()
        if info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise PrivacyError("Audit destination must be owned by current user without group/other access")


def _prepare_private_parent(path: Path) -> None:
    if os.name == "nt":
        # Verify inherited access before creating even an empty destination.
        ancestor = path.parent
        while not ancestor.exists():
            ancestor = ancestor.parent
        verify_private_path(ancestor)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    verify_private_path(path.parent)
    if path.exists():
        verify_private_path(path)

class AuditStore:
    """Private SQLite event ledger. Every mutation appends a new event."""

    def __init__(self, path: str | Path | None = None):
        default = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "the-brief/audit.sqlite3"
        self.path = Path(path or default).expanduser().absolute()
        _prepare_private_parent(self.path)
        # Create with restrictive permissions before SQLite opens it.
        fd = os.open(self.path, os.O_CREAT | os.O_RDWR, 0o600)
        os.close(fd)
        if os.name != "nt":
            os.chmod(self.path, 0o600)
        verify_private_path(self.path)
        self._lock = RLock()
        self._db = sqlite3.connect(self.path, timeout=30, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA busy_timeout=30000")
        self._db.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL UNIQUE,
                run_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                entity_id TEXT,
                recorded_at TEXT NOT NULL,
                payload TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                event_hash TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS events_run ON events(run_id, seq);
            CREATE TRIGGER IF NOT EXISTS prevent_update BEFORE UPDATE ON events
              BEGIN SELECT RAISE(ABORT, 'audit events are append-only'); END;
            CREATE TRIGGER IF NOT EXISTS prevent_delete BEFORE DELETE ON events
              BEGIN SELECT RAISE(ABORT, 'audit events are append-only'); END;
        """)
        self._db.commit()

    def _has_run(self, run_id: str) -> bool:
        return self._db.execute("SELECT 1 FROM events WHERE run_id=? AND kind='run_started'", (run_id,)).fetchone() is not None

    def event(self, run_id: str, kind: str, **fields: Any) -> str:
        if not run_id or not kind:
            raise ValueError("run_id and kind are required")
        if sanitize(run_id) != run_id or sanitize(kind) != kind:
            raise ValueError("Identifiers may not contain credentials")
        entity_id = fields.pop("entity_id", None)
        if entity_id is not None and sanitize(entity_id) != entity_id:
            raise ValueError("Identifiers may not contain credentials")
        # Do not silently turn impossible clocks into plausible runtimes.
        for name in ("started_at", "ended_at", "deadline_at", "delivered_at"):
            if fields.get(name):
                _parse_time(fields[name])
        if fields.get("started_at") and fields.get("ended_at"):
            elapsed_seconds(fields["started_at"], fields["ended_at"])
        payload = _json(sanitize(fields))
        with self._lock:
            self._db.execute("BEGIN IMMEDIATE")
            try:
                if kind == "run_started":
                    if self._has_run(run_id):
                        raise ValueError(f"Run already exists: {run_id}")
                elif not self._has_run(run_id):
                    raise ValueError(f"Unknown run: {run_id}")
                row = self._db.execute("SELECT event_hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
                previous = row[0] if row else "0" * 64
                event_id, recorded_at = str(uuid4()), utc_now()
                record = [event_id, run_id, kind, entity_id, recorded_at, payload, previous]
                digest = hashlib.sha256(_json(record).encode()).hexdigest()
                self._db.execute("INSERT INTO events(event_id,run_id,kind,entity_id,recorded_at,payload,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?,?)", (*record, digest))
                self._db.commit()
                return event_id
            except BaseException:
                self._db.rollback()
                raise

    def start_run(self, run_id: str, **metadata: Any) -> str:
        metadata.setdefault("started_at", utc_now())
        metadata.setdefault("status", "running")
        return self.event(run_id, "run_started", **metadata)

    def finish_run(self, run_id: str, status: str, **fields: Any) -> str:
        fields.setdefault("ended_at", utc_now())
        fields["status"] = status
        runs = self.records("run", run_id)
        if not runs:
            raise ValueError(f"Unknown run: {run_id}")
        elapsed_seconds(runs[0].get("started_at"), fields["ended_at"])
        return self.event(run_id, "run_finished", **fields)

    def _record(self, kind: str, run_id: str, entity_id: str | None, fields: dict) -> str:
        entity_id = entity_id or f"{kind}-{uuid4()}"
        # Event for same ID is a new revision, not a destructive overwrite.
        self.event(run_id, kind, entity_id=entity_id, **fields)
        return entity_id

    def record_attempt(self, run_id: str, agent_id: str, attempt_id: str | None = None, **fields: Any) -> str:
        return self._record("attempt", run_id, attempt_id, {"agent_id": agent_id, **fields})

    def record_source(self, run_id: str, entity_id: str | None = None, **fields: Any) -> str:
        return self._record("source", run_id, entity_id, fields)

    def record_claim(self, run_id: str, entity_id: str | None = None, **fields: Any) -> str:
        return self._record("claim", run_id, entity_id, fields)

    def record_evidence(self, run_id: str, entity_id: str | None = None, **fields: Any) -> str:
        return self._record("evidence", run_id, entity_id, fields)

    def record_checkpoint(self, run_id: str, entity_id: str | None = None, **fields: Any) -> str:
        return self._record("checkpoint", run_id, entity_id, fields)

    def record_artifact(self, run_id: str, entity_id: str | None = None, **fields: Any) -> str:
        return self._record("artifact", run_id, entity_id, fields)

    def record_metric(self, run_id: str, entity_id: str | None = None, **fields: Any) -> str:
        return self._record("metric", run_id, entity_id, fields)

    def events(self, run_id: str | None = None) -> list[dict]:
        with self._lock:
            rows = self._db.execute("SELECT * FROM events" + (" WHERE run_id=?" if run_id else "") + " ORDER BY seq", (run_id,) if run_id else ()).fetchall()
        return [{**dict(row), "payload": json.loads(row["payload"])} for row in rows]

    def records(self, kind: str, run_id: str | None = None) -> list[dict]:
        if kind != "run" and kind not in _ENTITY_KINDS:
            raise ValueError(f"Unknown record kind: {kind}")
        result: dict[tuple, dict] = {}
        for event in self.events(run_id):
            if (kind == "run" and event["kind"] in ("run_started", "run_finished")) or event["kind"] == kind:
                key = (event["run_id"], event["entity_id"])
                record = result.setdefault(key, {"run_id": event["run_id"]})
                if kind != "run":
                    record[f"{kind}_id"] = event["entity_id"]
                record.update(event["payload"])
                record["last_event_id"] = event["event_id"]
        for record in result.values():
            if kind in ("run", "attempt"):
                record["runtime_seconds"] = elapsed_seconds(record.get("started_at"), record.get("ended_at"))
            if kind == "run":
                deadline, delivered = record.get("deadline_at"), record.get("delivered_at")
                record["lateness_seconds"] = max(0, (_parse_time(delivered) - _parse_time(deadline)).total_seconds()) if deadline and delivered else None
        return list(result.values())

    def verify_chain(self) -> bool:
        previous = "0" * 64
        for event in self.events():
            record = [event["event_id"], event["run_id"], event["kind"], event["entity_id"], event["recorded_at"], _json(event["payload"]), previous]
            digest = hashlib.sha256(_json(record).encode()).hexdigest()
            if previous != event["previous_hash"] or digest != event["event_hash"]:
                return False
            previous = digest
        return True

    def export_xlsx(self, path: str | Path, *, public: bool = False) -> Path:
        """Export a PRIVATE review copy. Public export deliberately unsupported.

        Automatic redaction cannot establish that arbitrary source metadata or
        artifact URLs are safe to publish. Public reports require explicit review.
        """
        if public:
            raise ValueError("Audit workbooks are private; public export requires an explicit reviewed allowlist")
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.utils import get_column_letter
        path = Path(path).expanduser().absolute()
        if path == self.path:
            raise ValueError("Workbook must not overwrite audit database")
        _prepare_private_parent(path)
        wb = Workbook()
        overview = wb.active
        overview.title = "Overview"
        for row in [
            ["THE BRIEF | Private runtime audit", "Value"],
            ["Exported UTC", utc_now()],
            ["Event chain valid", self.verify_chain()],
            ["Runs", len(self.records("run"))],
            ["Attempts", len(self.records("attempt"))],
            ["Events", len(self.events())],
            ["Unknown values", "Blank means unavailable, not zero"],
            ["Privacy", "Private export: do not commit to the public repository"],
            ["Scope", "Operational facts only; no hidden reasoning or raw prompts"],
            ["Integrity", "Hash chain detects accidental changes, not an authenticated signature"],
            ["Checkpoints", "Recorded as checkpoint events; filter Events by kind"],
            ["Timing", "UTC ISO timestamps; runtime and lateness are measured seconds"],
        ]:
            overview.append(row)
        specs = [
            ("Runs", "run", ["run_id", "edition_date", "status", "started_at", "ended_at", "runtime_seconds", "deadline_at", "delivered_at", "lateness_seconds", "code_version", "config_hash"]),
            ("Attempts", "attempt", ["run_id", "attempt_id", "agent_id", "attempt_number", "status", "started_at", "ended_at", "runtime_seconds", "error_code", "error", "recovery_action", "model", "prompt_hash"]),
            ("Sources", "source", ["run_id", "source_id", "attempt_id", "url", "status", "retrieved_at", "published_at", "content_hash", "gap_reason"]),
            ("Claims", "claim", ["run_id", "claim_id", "attempt_id", "source_ids", "evidence_ids", "status", "event_id", "freshness_status"]),
            ("Evidence", "evidence", ["run_id", "evidence_id", "source_id", "claim_id", "url", "content_hash", "private_reference", "verified_at"]),
            ("Events", "event", ["seq", "event_id", "run_id", "kind", "entity_id", "recorded_at", "payload", "previous_hash", "event_hash"]),
            ("Artifacts", "artifact", ["run_id", "artifact_id", "kind", "status", "sha256", "size_bytes", "private_reference", "receipt_id", "readback_status", "playback_status"]),
            ("Metrics", "metric", ["run_id", "metric_id", "attempt_id", "name", "value", "unit", "observed_at", "measurement_method"]),
        ]
        for title, kind, columns in specs:
            rows = self.events() if kind == "event" else self.records(kind)
            columns += sorted({key for row in rows for key in row} - set(columns))
            ws = wb.create_sheet(title)
            ws.append(columns)
            for row in rows:
                ws.append([_excel_cell(row.get(key)) for key in columns])
        for ws in wb:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for cell in ws[1]:
                cell.fill = PatternFill("solid", fgColor="17324D")
                cell.font = Font(color="FFFFFF", bold=True)
                cell.alignment = Alignment(wrap_text=True, vertical="top")
            for row in ws.iter_rows(min_row=2):
                for cell in row:
                    cell.alignment = Alignment(wrap_text=True, vertical="top")
            for index in range(1, ws.max_column + 1):
                ws.column_dimensions[get_column_letter(index)].width = 28 if index > 1 else 38
            ws.sheet_view.showGridLines = False
        fd = os.open(path, os.O_CREAT | os.O_TRUNC | os.O_WRONLY, 0o600)
        os.close(fd)
        if os.name != "nt":
            os.chmod(path, 0o600)
        verify_private_path(path)
        wb.save(path)
        return path

    def close(self) -> None:
        with self._lock:
            self._db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def _excel_cell(value: Any) -> Any:
    if isinstance(value, (dict, list, tuple)):
        value = _json(value)
    # Prevent spreadsheet formula injection from external source/error text.
    if isinstance(value, str):
        value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", value)
        if value.lstrip().startswith(("=", "+", "-", "@")):
            value = "'" + value
        return value[:32767]
    return value
