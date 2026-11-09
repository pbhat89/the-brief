import os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from podcast.agent_pipeline import audit as audit_module
from podcast.agent_pipeline.native_capture import save_receipt,manifest
from podcast.agent_pipeline.native_bridge import NativeBridgeError,digest
class CaptureTests(unittest.TestCase):
 def setUp(self):
  if os.name=='nt':
   acl={'current_sid':'test','owner_sid':'test','dacl_present':True,'aces':[{'sid':'test','type':'Allow'}]}
   mock=patch.object(audit_module,'inspect_windows_acl',return_value=acl);mock.start();self.addCleanup(mock.stop)
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.folder=Path(self.tmp.name).resolve()
  self.envelope={'request_url':'https://example.com/news','started_at':'2026-01-01T00:00:00Z','observed_at':'2026-01-01T00:00:01Z','tool_result':{'content':[{'type':'text','text':'Page result turn1view0'}]}}
 def test_exact_result_roundtrip_and_idempotency(self):
  receipt=save_receipt(self.folder,self.envelope)
  self.assertEqual(receipt,save_receipt(self.folder,self.envelope))
  m=manifest(self.folder,receipt['receipt_id'],'actual_driver','turn1view0','opened')
  self.assertEqual(m['entries'][0]['tool_result_sha256'],digest(self.envelope['tool_result']))
  self.assertEqual(m['entries'][0]['operation'],'open')
  self.assertFalse(receipt['actual_tool_attestation'])
 def test_failure_never_promoted(self):
  receipt=save_receipt(self.folder,self.envelope)
  for outcome in ('failed','unknown'):
   self.assertEqual(manifest(self.folder,receipt['receipt_id'],'driver','turn1view0',outcome)['entries'][0]['operation'],'open_'+outcome)
  with self.assertRaises(NativeBridgeError):manifest(self.folder,receipt['receipt_id'],'driver','INVENTED_REF','opened')
 def test_tamper_and_sensitive_url_rejected(self):
  receipt=save_receipt(self.folder,self.envelope);Path(receipt['receipt_file']).write_text('{}')
  with self.assertRaises(NativeBridgeError):manifest(self.folder,receipt['receipt_id'],'driver','turn1view0','opened')
  self.envelope['request_url']='https://example.com/news?secret=foo'
  with self.assertRaises(NativeBridgeError):save_receipt(self.folder,self.envelope)
if __name__=='__main__':unittest.main()
