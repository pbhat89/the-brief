import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from openpyxl import load_workbook
from .audit import AuditStore, validate_windows_acl, PrivacyError
from .native_bridge import NativeBridge
from .native_report import collect,export_report,TABS,checked

class ReportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name).resolve();self.root.chmod(0o700)
        b=NativeBridge(self.root);self.job=b.queue('run','india','SECRET RAW PROMPT',{'type':'object'},'a'*64,'b'*64);b.close()
        a=AuditStore(self.root/'audit.sqlite3');a.start_run('run');a.close()
    def tearDown(self):self.temp.cleanup()
    def mutate(self,sql):
        db=sqlite3.connect(self.root/'native-jobs.sqlite3');db.execute(sql);db.commit();db.close()
    def test_pending_and_read_only(self):
        before={p.name:p.read_bytes() for p in self.root.glob('*.sqlite3')}
        result=collect(self.root);j=result['AgentJobs'][0]
        self.assertEqual(j['state'],'queued');self.assertIsNone(j['tokens']);self.assertIsNone(j['claimed_wall_seconds'])
        self.assertNotIn('SECRET RAW PROMPT',json.dumps(result));self.assertEqual(before,{p.name:p.read_bytes() for p in self.root.glob('*.sqlite3')})
    def test_completed_workbook(self):
        b=NativeBridge(self.root);j=self.job;b.claim(j['id'],j['request_hash'],'worker');b.complete(j['id'],j['request_hash'],'worker',{});b.close()
        out=export_report(self.root,self.root/'audit.xlsx');wb=load_workbook(out);self.assertEqual(wb.sheetnames,list(TABS));self.assertGreater(wb['AgentJobs'].max_row,1)
        with self.assertRaises(FileExistsError):export_report(self.root,out)
    def test_request_corruption(self):
        self.mutate("UPDATE jobs SET request_hash='bad'")
        with self.assertRaisesRegex(ValueError,'request hash'):collect(self.root)
    def test_output_corruption(self):
        b=NativeBridge(self.root);j=self.job;b.claim(j['id'],j['request_hash'],'worker');b.complete(j['id'],j['request_hash'],'worker',{});b.close()
        self.mutate("UPDATE jobs SET output_hash='bad'")
        with self.assertRaisesRegex(ValueError,'output hash'):collect(self.root)
    def test_chain_corruption(self):
        d=sqlite3.connect(self.root/'audit.sqlite3');d.execute('DROP TRIGGER prevent_update');d.execute("UPDATE events SET event_hash='bad'");d.commit();d.close()
        with self.assertRaisesRegex(ValueError,'chain'):collect(self.root)
    def test_link_rejected(self):
        link=self.root/'alias';link.symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(ValueError):checked(link)
    def test_synthetic_windows_acl(self):
        allowed={'current_sid':'S-1-user','owner_sid':'S-1-user','dacl_present':True,'aces':[{'type':'Allow','sid':'S-1-user'},{'type':'Allow','sid':'S-1-3-4'}]}
        with patch('podcast.agent_pipeline.native_report.verify_private_path',side_effect=lambda p:validate_windows_acl(allowed)):self.assertEqual(checked(self.root),self.root)
        bad=dict(allowed,aces=[{'type':'Allow','sid':'S-1-unknown'}])
        with patch('podcast.agent_pipeline.native_report.verify_private_path',side_effect=lambda p:validate_windows_acl(bad)):
            with self.assertRaises(PrivacyError):checked(self.root)
    def test_evidence_corruption(self):
        d=sqlite3.connect(self.root/'native-jobs.sqlite3');d.execute('INSERT INTO evidence VALUES(?,?,?,?,?)',(self.job['id'],'m',json.dumps({'manifest_id':'m','entries':[]}),'bad','2026-11-09T00:00:00Z'));d.commit();d.close()
        with self.assertRaisesRegex(ValueError,'Evidence'):collect(self.root)
if __name__=='__main__':unittest.main()
