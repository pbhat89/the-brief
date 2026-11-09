import os
from unittest.mock import patch
from podcast.agent_pipeline import audit as audit_module
import tempfile
import unittest
from podcast.agent_pipeline.native_bridge import NativeBridge,NativeBridgeError
from podcast.agent_pipeline.native_proof import advance,URL
class ProofTests(unittest.TestCase):
 def setUp(self):
  # Synthetic Windows ACL fixture only. Runtime ACL validation stays enabled.
  if os.name == 'nt':
   acl={'current_sid':'S-1-5-21-test-1001','owner_sid':'S-1-5-21-test-1001',
        'dacl_present':True,'aces':[{'sid':'S-1-5-21-test-1001','type':'Allow'}]}
   mock=patch.object(audit_module,'inspect_windows_acl',return_value=acl)
   mock.start();self.addCleanup(mock.stop)
 def test_real_graph_interrupt_resume_with_synthetic_outputs(self):
  with tempfile.TemporaryDirectory() as folder:
   result=advance(folder,'unit-proof')
   self.assertFalse(result['completed']);self.assertEqual(result['pending'][0]['role'],'research')
   with self.assertRaises(NativeBridgeError):advance(folder,'unit-proof')
   b=NativeBridge(folder);q=result['pending'][0]
   b.claim(q['job_id'],q['request_hash'],'synthetic_test_agent1')
   b.complete(q['job_id'],q['request_hash'],'synthetic_test_agent1',dict(title='Synthetic NEA',url=URL,description='Synthetic fixture only',tool_evidence=['TEST_ONLY']))
   b.close()
   result=advance(folder,'unit-proof',True)
   self.assertEqual(result['pending'][0]['role'],'checker')
   b=NativeBridge(folder);q=result['pending'][0]
   b.claim(q['job_id'],q['request_hash'],'synthetic_test_agent2')
   b.complete(q['job_id'],q['request_hash'],'synthetic_test_agent2',dict(verified=True,url=URL,title='Synthetic NEA',reason='Synthetic fixture only',tool_evidence=['TEST_ONLY']))
   b.close()
   result=advance(folder,'unit-proof',True)
   self.assertTrue(result['completed']);self.assertIsNone(result['usage'])
   with self.assertRaises(NativeBridgeError):advance(folder,'unit-proof',True)
if __name__=='__main__':unittest.main()
