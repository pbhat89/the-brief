import copy,json
from jsonschema import ValidationError
from podcast.agent_pipeline.tests.test_native_bridge import NativeTests
from podcast.agent_pipeline.native_bridge import NativeBridgeError
class NativeEvidenceTests(NativeTests):
 def manifest(self):
  return {'manifest_id':'receipt1','driver_id':'root_driver','entries':[
   {'tool_ref':'turn1view0','tool_name':'web_open','operation':'open','url':'https://www.nea.gov.sg/corporate-functions/weather','basis':'driver_observed','started_at':'2026-01-01T00:00:00Z','observed_at':'2026-01-01T00:00:01Z','tool_result_sha256':'c'*64}]}
 def claimed(self):
  q=self.queued();self.b.claim(q['id'],q['request_hash'],'agent1');return q
 def reject_rows(self):
  return [json.loads(r[0]) for r in self.b.db.execute('SELECT metadata FROM transitions') if json.loads(r[0])['state']=='submission_rejected']
 def test_schema_rejections_metadata_only_idempotent(self):
  q=self.claimed()
  for _ in range(2):
   with self.assertRaises(ValidationError):self.b.complete(q['id'],q['request_hash'],'agent1',{'ok':'RAW_SECRET_INVALID_OUTPUT'})
  rows=self.reject_rows();self.assertEqual(len(rows),1);self.assertEqual(rows[0]['rejection_kind'],'schema')
  self.assertNotIn('RAW_SECRET_INVALID_OUTPUT',str(self.b.audit.events()))
  self.assertEqual(self.b.status(q['id'])['state'],'claimed')
 def test_identity_and_state_rejections(self):
  q=self.queued()
  with self.assertRaises(NativeBridgeError):self.b.claim(q['id'],'wrong','agent1')
  self.b.claim(q['id'],q['request_hash'],'agent1')
  with self.assertRaises(NativeBridgeError):self.b.claim(q['id'],q['request_hash'],'agent2')
  self.assertEqual({r['rejection_kind'] for r in self.reject_rows()},{'identity','state'})
 def test_evidence_roundtrip_idempotent_and_no_auto_attestation(self):
  q=self.claimed();m=self.manifest()
  one=self.b.ingest_evidence(q['id'],q['request_hash'],'agent1',m)
  self.assertEqual(one,self.b.ingest_evidence(q['id'],q['request_hash'],'agent1',m))
  rows=self.b.evidence(q['id']);self.assertEqual(len(rows),1)
  self.assertEqual(rows[0]['timestamp_basis'],'driver_observed');self.assertFalse(rows[0]['automatic_tool_attestation'])
  self.assertEqual(rows[0]['tool_result_sha256'],'c'*64)
  changed=copy.deepcopy(m);changed['entries'][0]['tool_ref']='other'
  with self.assertRaises(NativeBridgeError):self.b.ingest_evidence(q['id'],q['request_hash'],'agent1',changed)
 def test_declared_never_promoted(self):
  q=self.claimed();m=self.manifest();e=m['entries'][0];e.update(basis='agent_declared',started_at=None,observed_at=None,tool_result_sha256=None)
  self.b.ingest_evidence(q['id'],q['request_hash'],'agent1',m)
  self.assertEqual(self.b.evidence(q['id'])[0]['timestamp_basis'],'agent_declared')
 def test_unsafe_missing_and_fake_measured_fields_rejected(self):
  q=self.claimed()
  for change in ({'operation':'inferred_fetch'},{'url':'https://example.com/?token=secret'},{'tool_result_sha256':None},{'started_at':'2026-01-02T00:00:00Z'},{'basis':'adapter_observed'},{'basis':'agent_declared'}):
   m=self.manifest();m['entries'][0].update(change)
   with self.assertRaises(NativeBridgeError):self.b.ingest_evidence(q['id'],q['request_hash'],'agent1',m)
  self.assertEqual(self.b.evidence(q['id']),[])
 def test_evidence_wrong_owner_and_tamper(self):
  q=self.claimed();m=self.manifest()
  with self.assertRaises(NativeBridgeError):self.b.ingest_evidence(q['id'],q['request_hash'],'wrong_agent',m)
  self.b.ingest_evidence(q['id'],q['request_hash'],'agent1',m)
  self.b.db.execute("UPDATE evidence SET payload='{}'");self.b.db.commit()
  with self.assertRaises(NativeBridgeError):self.b.evidence(q['id'])
