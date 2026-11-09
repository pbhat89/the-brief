import os
from unittest.mock import patch
from podcast.agent_pipeline import audit as audit_module
import tempfile
from pathlib import Path
import unittest
from jsonschema import ValidationError
from podcast.agent_pipeline.native_bridge import NativeBridge, NativeBridgeError

SCHEMA={'type':'object','properties':{'ok':{'type':'boolean'}},'required':['ok'],'additionalProperties':False}
class NativeTests(unittest.TestCase):
 def setUp(self):
  # Synthetic Windows ACL fixture only. Runtime ACL validation stays enabled.
  if os.name == 'nt':
   acl={'current_sid':'S-1-5-21-test-1001','owner_sid':'S-1-5-21-test-1001',
        'dacl_present':True,'aces':[{'sid':'S-1-5-21-test-1001','type':'Allow'}]}
   mock=patch.object(audit_module,'inspect_windows_acl',return_value=acl)
   mock.start();self.addCleanup(mock.stop)
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.b=NativeBridge(Path(self.tmp.name).resolve());self.addCleanup(self.b.close)
  self.kw=dict(run_id='proof',role='research',prompt='PUBLIC TEST PROMPT',schema=SCHEMA,context_hash='a'*64,runtime_source_hash='b'*64)
 def queued(self):return self.b.queue(**self.kw)
 def test_roundtrip_unknown_usage(self):
  q=self.queued();self.b.claim(q['id'],q['request_hash'],'agent_actual_1')
  s=self.b.complete(q['id'],q['request_hash'],'agent_actual_1',{'ok':True})
  self.assertEqual(s['state'],'completed');self.assertIsNone(s['usage']);self.assertGreaterEqual(s['runtime_seconds'],0)
  self.assertEqual(self.b.result(q['id']),{'ok':True});self.assertTrue(self.b.audit.verify_chain())
  self.assertNotIn('PUBLIC TEST PROMPT',str(self.b.audit.events()))
 def test_idempotent_queue_claim_complete(self):
  q=self.queued();self.assertEqual(q,self.queued())
  a=self.b.claim(q['id'],q['request_hash'],'agent1');self.assertEqual(a,self.b.claim(q['id'],q['request_hash'],'agent1'))
  a=self.b.complete(q['id'],q['request_hash'],'agent1',{'ok':True})
  self.assertEqual(a,self.b.complete(q['id'],q['request_hash'],'agent1',{'ok':True}))
 def test_conflicts_fail_closed(self):
  q=self.queued()
  with self.assertRaises(NativeBridgeError):self.b.queue(**(self.kw|{'prompt':'changed'}))
  with self.assertRaises(NativeBridgeError):self.b.claim(q['id'],'wrong','agent1')
  self.b.claim(q['id'],q['request_hash'],'agent1')
  with self.assertRaises(NativeBridgeError):self.b.claim(q['id'],q['request_hash'],'agent2')
  with self.assertRaises(NativeBridgeError):self.b.complete(q['id'],q['request_hash'],'agent2',{'ok':True})
  with self.assertRaises(ValidationError):self.b.complete(q['id'],q['request_hash'],'agent1',{'ok':'invalid'})
  self.assertEqual(self.b.status(q['id'])['state'],'claimed')
 def test_explicit_retry_only(self):
  q=self.queued()
  with self.assertRaises(NativeBridgeError):self.b.queue(**self.kw,attempt=2,retry_of=q['id'])
  self.b.claim(q['id'],q['request_hash'],'agent1');self.b.fail(q['id'],q['request_hash'],'agent1','source_unavailable')
  retry=self.b.queue(**self.kw,attempt=2,retry_of=q['id']);self.assertNotEqual(q['id'],retry['id'])
 def test_tamper_detected(self):
  q=self.queued();self.b.db.execute("UPDATE jobs SET request='{}' WHERE id=?",(q['id'],));self.b.db.commit()
  with self.assertRaises(NativeBridgeError):self.b.status(q['id'])
 def test_unclaimed_completion_rejected(self):
  q=self.queued()
  with self.assertRaises(NativeBridgeError):self.b.complete(q['id'],q['request_hash'],'agent1',{'ok':True})
 def test_persists_reopen(self):
  q=self.queued();b=NativeBridge(Path(self.tmp.name).resolve())
  try:self.assertEqual(b.status(q['id']),q)
  finally:b.close()
if __name__=='__main__':unittest.main()
