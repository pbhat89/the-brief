import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from openpyxl import load_workbook
from . import audit as audit_module
from .audit import AuditStore, validate_windows_acl, PrivacyError
from .native_bridge import NativeBridge,digest
from .native_report import collect,collect_related,export_report,TABS,checked

class ReportTests(unittest.TestCase):
    def setUp(self):
        # Explicit synthetic ACL evidence for portable fixtures; runtime validator remains active.
        if os.name == 'nt':
            acl={'current_sid':'S-1-5-21-test-1001','owner_sid':'S-1-5-21-test-1001',
                 'dacl_present':True,'aces':[{'sid':'S-1-5-21-test-1001','type':'Allow'}]}
            inspector=patch.object(audit_module,'inspect_windows_acl',return_value=acl)
            inspector.start();self.addCleanup(inspector.stop)
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name).resolve();self.root.chmod(0o700)
        b=NativeBridge(self.root);self.job=b.queue('run','india','SECRET RAW PROMPT',{'type':'object'},'a'*64,'b'*64);b.close()
        a=AuditStore(self.root/'audit.sqlite3');a.start_run('run');a.close()
    def tearDown(self):self.temp.cleanup()
    def mutate(self,sql):
        db=sqlite3.connect(self.root/'native-jobs.sqlite3');db.execute(sql);db.commit();db.close()
    def test_related_scopes_deduplicate(self):
        other=self.root/'related';other.mkdir(mode=0o700)
        b=NativeBridge(other);b.queue('run','india','other private prompt',{'type':'object'},'c'*64,'d'*64);b.close()
        result=collect_related(self.root,[other,other,self.root])
        self.assertEqual(len(result['AgentJobs']),2)
        self.assertEqual({r['report_scope'] for r in result['AgentJobs']},{self.root.name,'related'})
        self.assertTrue(all('report_scope' in row for rows in result.values() for row in rows))
        out=export_report(self.root,self.root/'combined.xlsx',related_directories=[other,other])
        wb=load_workbook(out);self.assertEqual(wb['AgentJobs'].max_row,3);wb.close()
    def test_pending_and_read_only(self):
        before={p.name:p.read_bytes() for p in self.root.glob('*.sqlite3')}
        result=collect(self.root);j=result['AgentJobs'][0]
        self.assertEqual(j['state'],'queued');self.assertIsNone(j['tokens']);self.assertIsNone(j['claimed_wall_seconds'])
        self.assertNotIn('SECRET RAW PROMPT',json.dumps(result));self.assertEqual(before,{p.name:p.read_bytes() for p in self.root.glob('*.sqlite3')})
    def test_completed_workbook(self):
        b=NativeBridge(self.root);j=self.job;b.claim(j['id'],j['request_hash'],'worker');b.complete(j['id'],j['request_hash'],'worker',{});b.close()
        out=export_report(self.root,self.root/'audit.xlsx');wb=load_workbook(out);self.assertEqual(wb.sheetnames,list(TABS));self.assertGreater(wb['AgentJobs'].max_row,1);wb.close()
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
        link=self.root/'alias'
        try:link.symlink_to(self.root,target_is_directory=True)
        except OSError as error:
            if os.name=='nt' and getattr(error,'winerror',None)==1314:
                self.skipTest('Windows symlink privilege unavailable; rejection not exercised')
            raise
        with self.assertRaises(ValueError):checked(link)
    @unittest.skipUnless(os.name=='nt','Windows actual verifier dispatch only')
    def test_windows_acl_fail_closed(self):
        bad={'current_sid':'S-1-5-21-test-1001','owner_sid':'S-1-5-21-test-1001',
             'dacl_present':True,'aces':[{'sid':'S-1-unknown','type':'Allow'}]}
        # Override only the inspector within the setup fixture, not the real validator.
        with patch.object(audit_module,'inspect_windows_acl',return_value=bad):
            with self.assertRaises(PrivacyError):checked(self.root)
    def test_synthetic_windows_acl(self):
        allowed={'current_sid':'S-1-user','owner_sid':'S-1-user','dacl_present':True,'aces':[{'type':'Allow','sid':'S-1-user'},{'type':'Allow','sid':'S-1-3-4'}]}
        with patch('podcast.agent_pipeline.native_report.verify_private_path',side_effect=lambda p:validate_windows_acl(allowed)):self.assertEqual(checked(self.root),self.root)
        bad=dict(allowed,aces=[{'type':'Allow','sid':'S-1-unknown'}])
        with patch('podcast.agent_pipeline.native_report.verify_private_path',side_effect=lambda p:validate_windows_acl(bad)):
            with self.assertRaises(PrivacyError):checked(self.root)
    def test_public_url_optin(self):
        urls=['https://www.example.com/news/one','https://example.com/news?token=secret','http://127.0.0.1/private','https://user:password@example.com/page','https://example.com/auth/token']
        db=sqlite3.connect(self.root/'native-jobs.sqlite3')
        for i,url in enumerate(urls):
            m={'manifest_id':str(i),'driver_id':'worker','entries':[{'url':url,'operation':'open_failed','tool_ref':'ref'+str(i)}]}
            db.execute('INSERT INTO evidence VALUES(?,?,?,?,?)',(self.job['id'],str(i),json.dumps(m),digest(m),'2026-11-09T00:00:00Z'))
        db.commit();db.close()
        default=collect(self.root);optin=collect(self.root,include_public_urls=True)
        self.assertTrue(all('public_source_url' not in r for r in default['ToolEvidence']))
        self.assertEqual([r.get('public_source_url') for r in optin['ToolEvidence']],[urls[0],None,None,None,None])
        self.assertTrue(all(r['url_sha256'] for r in optin['ToolEvidence']))
        self.assertNotIn('token=secret',json.dumps(optin))
    def test_evidence_corruption(self):
        d=sqlite3.connect(self.root/'native-jobs.sqlite3');d.execute('INSERT INTO evidence VALUES(?,?,?,?,?)',(self.job['id'],'m',json.dumps({'manifest_id':'m','entries':[]}),'bad','2026-11-09T00:00:00Z'));d.commit();d.close()
        with self.assertRaisesRegex(ValueError,'Evidence'):collect(self.root)
if __name__=='__main__':unittest.main()
