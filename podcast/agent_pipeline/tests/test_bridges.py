import hashlib
import tempfile
import unittest
from pathlib import Path
from podcast.agent_pipeline.bridges import publish_verified,validate_editorial,validate_voice
class Client:
    def __init__(self,timeout=False):self.receipt=None;self.calls=0;self.timeout=timeout
    def lookup(self,id):return self.receipt
    def upload(self,id,data,metadata):
        self.calls+=1;self.data=data;self.receipt=metadata
        if self.timeout:raise TimeoutError()
        return metadata
    def readback(self,r):return self.data
class BridgeTests(unittest.TestCase):
    def test_disabled(self):
        with self.assertRaises(ValueError):publish_verified(None,edition_id='x',audio_path='none',metadata={})
    def test_once_and_readback(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'a';p.write_bytes(b'audio');c=Client(True)
            for _ in range(2):
                r=publish_verified(c,edition_id='comparison',audio_path=p,metadata={},allow_publish=True)
                self.assertTrue(r['readback_verified']);self.assertFalse(r['playback_verified'])
            self.assertEqual(c.calls,1)
            p.write_bytes(b'changed')
            with self.assertRaises(ValueError):publish_verified(c,edition_id='comparison',audio_path=p,metadata={},allow_publish=True)
    def test_missing_contracts(self):
        with self.assertRaises(ValueError):validate_editorial('.', '/missing/audit')
        with self.assertRaises(ValueError):validate_voice('/missing','/missing','/missing','/missing')
