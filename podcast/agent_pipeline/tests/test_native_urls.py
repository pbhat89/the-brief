import unittest
from podcast.agent_pipeline.native_urls import public_source_url
class NativeUrlTests(unittest.TestCase):
 def test_known_public_routes(self):
  for url in ['https://www.youtube.com/@EverydayAI/videos','https://www.gov.uk/government/news/scottish-secretary-honours-armed-forces-at-remembrance-service','https://www.pmindia.gov.in/en/news_updates/'+('public-news-'*12)]:
   self.assertEqual(public_source_url(url),url)
 def test_sensitive_routes_remain_rejected(self):
  for url in ['https://x.com/user?token=secret','https://user:pass@example.com/news','https://127.0.0.1/news','https://example.com/session/abc','https://example.com/auth-token/value','https://example.com/@private','https://example.com/'+('x'*101),'https://example.com/news#token']:
   self.assertIsNone(public_source_url(url))
