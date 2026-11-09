import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from openpyxl import load_workbook

try:
    from . import audit as audit_module
    from .audit import AuditStore, elapsed_seconds, file_sha256, sanitize, REDACTED, verify_private_path, validate_windows_acl, PrivacyError
except ImportError:
    import audit as audit_module
    from audit import AuditStore, elapsed_seconds, file_sha256, sanitize, REDACTED, verify_private_path, validate_windows_acl, PrivacyError


class AuditTests(unittest.TestCase):
    def setUp(self):
        # Storage logic uses an explicit synthetic private ACL on Windows.
        # Real-host privacy is an integration prerequisite, never inferred from
        # these fixtures. validate_windows_acl itself remains active below.
        if os.name == "nt":
            acl = {"current_sid": "S-1-5-21-test-1001", "owner_sid": "S-1-5-21-test-1001",
                   "dacl_present": True, "aces": [{"sid": "S-1-5-21-test-1001", "type": "Allow"}]}
            mock = patch.object(audit_module, "inspect_windows_acl", return_value=acl)
            mock.start()
            self.addCleanup(mock.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "audit.sqlite3"
        self.store = AuditStore(self.path)
        self.store.start_run("run-1", started_at="2026-11-08T00:00:00Z", deadline_at="2026-11-08T00:10:00Z")

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_duration_and_lateness(self):
        self.store.finish_run("run-1", "success", ended_at="2026-11-08T00:11:00Z", delivered_at="2026-11-08T00:10:15Z")
        run = self.store.records("run")[0]
        self.assertEqual(run["runtime_seconds"], 660)
        self.assertEqual(run["lateness_seconds"], 15)

    def test_unknown_is_null(self):
        self.assertIsNone(self.store.records("run")[0]["runtime_seconds"])
        self.assertIsNone(self.store.records("run")[0]["lateness_seconds"])
        self.store.record_metric("run-1", name="tokens", value=None)
        self.assertIsNone(self.store.records("metric")[0]["value"])

    def test_chronology_validation(self):
        with self.assertRaises(ValueError):
            self.store.finish_run("run-1", "success", ended_at="2026-11-07T00:00:00Z")
        with self.assertRaises(ValueError):
            elapsed_seconds("2026-11-08T00:00:00", "2026-11-08T00:01:00")
        self.assertEqual(elapsed_seconds("2026-11-08T08:00:00+08:00", "2026-11-08T00:01:00Z"), 60)

    def test_run_identity(self):
        with self.assertRaises(ValueError):
            self.store.start_run("run-1")
        with self.assertRaises(ValueError):
            self.store.event("unknown", "check")

    def test_attempt_revisions_append(self):
        attempt = self.store.record_attempt("run-1", "india", started_at="2026-11-08T00:00:00Z", status="running")
        self.store.record_attempt("run-1", "india", attempt_id=attempt, ended_at="2026-11-08T00:02:00Z", status="success")
        self.assertEqual(len(self.store.events()), 3)
        self.assertEqual(len(self.store.records("attempt")), 1)
        self.assertEqual(self.store.records("attempt")[0]["runtime_seconds"], 120)
        self.assertTrue(self.store.verify_chain())

    def test_secrets_redacted_not_token_metrics(self):
        value = sanitize({"api_key": "abc", "input_tokens": 10, "prompt": "private", "error": "Failed Bearer abcdef1234 and https://example.org/?token=private&other=ok", "nested": {"password": "x"}})
        self.assertEqual(value["api_key"], REDACTED)
        self.assertEqual(value["prompt"], REDACTED)
        self.assertEqual(value["input_tokens"], 10)
        self.assertNotIn("abcdef", value["error"])
        self.assertNotIn("private", value["error"])
        self.assertEqual(value["nested"]["password"], REDACTED)

    def test_private_file_permissions(self):
        verify_private_path(self.path)

    def test_immutable_events(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.store._db.execute("DELETE FROM events")
        self.store._db.rollback()
        with self.assertRaises(sqlite3.IntegrityError):
            self.store._db.execute("UPDATE events SET payload='{}'")
        self.store._db.rollback()
        self.assertTrue(self.store.verify_chain())

    def test_tamper_detection(self):
        self.store._db.execute("DROP TRIGGER prevent_update")
        self.store._db.execute("UPDATE events SET payload='{}'")
        self.store._db.commit()
        self.assertFalse(self.store.verify_chain())

    def test_concurrent_events(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda i: self.store.event("run-1", "check", index=i), range(20)))
        self.assertEqual(len(self.store.events()), 21)
        self.assertTrue(self.store.verify_chain())

    def test_all_records_and_workbook(self):
        self.store.record_source("run-1", "src-1", url="https://example.org")
        self.store.record_claim("run-1", "cl-1", source_ids=["src-1"])
        self.store.record_evidence("run-1", "ev-1", claim_id="cl-1", source_id="src-1")
        self.store.record_checkpoint("run-1", "cp-1", status="passed")
        self.store.record_artifact("run-1", "ar-1", sha256="a" * 64, playback_status="unverified")
        self.store.record_metric("run-1", "m-1", name="unknown", value=None)
        self.store.record_attempt("run-1", "checker", error="=HYPERLINK(\"https://evil\")")
        target = self.store.export_xlsx(Path(self.temp.name) / "audit.xlsx")
        workbook = load_workbook(target, data_only=False)
        self.assertEqual(workbook.sheetnames, ["Overview", "Runs", "Attempts", "Sources", "Claims", "Evidence", "Events", "Artifacts", "Metrics"])
        error_col = [c.value for c in workbook["Attempts"][1]].index("error") + 1
        self.assertTrue(workbook["Attempts"].cell(2, error_col).value.startswith("'="))
        verify_private_path(target)
        self.assertEqual(len(file_sha256(target)), 64)
        workbook.close()

    def test_public_export_rejected(self):
        with self.assertRaises(ValueError):
            self.store.export_xlsx(Path(self.temp.name) / "public.xlsx", public=True)

    def test_nonfinite_and_unsupported_rejected(self):
        with self.assertRaises(ValueError):
            self.store.event("run-1", "metric", value=float("nan"))
        with self.assertRaises(TypeError):
            self.store.event("run-1", "metric", value=object())


class WindowsAclTests(unittest.TestCase):
    def snapshot(self):
        return {"current_sid": "S-1-5-21-test-1001", "owner_sid": "S-1-5-21-test-1001",
                "dacl_present": True, "aces": [
                    {"sid": "S-1-5-21-test-1001", "type": "Allow"},
                    {"sid": "S-1-5-18", "type": "Allow"},
                    {"sid": "S-1-5-32-544", "type": "Allow"}]}

    def test_private_owner_system_admin_accepted(self):
        validate_windows_acl(self.snapshot())

    def test_unknown_and_application_principals_rejected(self):
        for sid in ("S-1-1-0", "S-1-5-11", "S-1-5-21-test-1003", "S-1-5-21-unresolved-123"):
            snapshot = self.snapshot()
            snapshot["aces"].append({"sid": sid, "type": "Allow"})
            with self.assertRaises(PrivacyError):
                validate_windows_acl(snapshot)

    def test_wrong_owner_and_null_dacl_rejected(self):
        for field, value in (("owner_sid", "someone-else"), ("dacl_present", False), ("current_sid", None)):
            snapshot = self.snapshot()
            snapshot[field] = value
            with self.assertRaises(PrivacyError):
                validate_windows_acl(snapshot)

    def test_unknown_ace_type_rejected(self):
        snapshot = self.snapshot()
        snapshot["aces"].append({"sid": snapshot["current_sid"], "type": "unexpected"})
        with self.assertRaises(PrivacyError):
            validate_windows_acl(snapshot)

    def test_deny_does_not_authorize_unknown_allow(self):
        snapshot = self.snapshot()
        snapshot["aces"] += [{"sid": "S-1-1-0", "type": "Deny"}, {"sid": "S-1-1-0", "type": "Allow"}]
        with self.assertRaises(PrivacyError):
            validate_windows_acl(snapshot)

    def test_acl_inspection_failure_blocks(self):
        with patch.object(audit_module.subprocess, "run", side_effect=OSError("unavailable")):
            with self.assertRaises(PrivacyError):
                audit_module.inspect_windows_acl("test-path")

if __name__ == "__main__":
    unittest.main()

class OwnerRightsTests(unittest.TestCase):
    def test_owner_rights_only_for_current_owner(self):
        from podcast.agent_pipeline.audit import validate_windows_acl, PrivacyError
        snapshot = {'current_sid':'user', 'owner_sid':'user', 'dacl_present':True, 'aces':[{'type':'Allow','sid':'S-1-3-4'}]}
        validate_windows_acl(snapshot)
        snapshot['owner_sid']='other'
        with self.assertRaises(PrivacyError): validate_windows_acl(snapshot)
