import unittest
from unittest.mock import patch
from providers.curseforge import CurseForgeProvider

class TestCurseForgeProvider(unittest.TestCase):
    @patch('requests.get')
    def test_search(self, mock_get):
        mock_get.return_value.json.return_value = [{"name": "DBM", "id": "123"}]
        mock_get.return_value.status_code = 200
        provider = CurseForgeProvider()
        results = provider.search("DBM")
        self.assertEqual(results[0]['name'], "DBM")
        
        # Verify gameId is in params
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params']['gameId'], 1)
        self.assertEqual(kwargs['params']['searchFilter'], "DBM")

    @patch('requests.get')
    def test_search_caching(self, mock_get):
        mock_get.return_value.json.return_value = [{"name": "DBM", "id": "123"}]
        mock_get.return_value.status_code = 200
        provider = CurseForgeProvider()
        
        # First call
        provider.search("DBM")
        # Second call
        provider.search("DBM")
        
        # Should only be called once due to caching
        self.assertEqual(mock_get.call_count, 1)

    def test_api_key(self):
        provider = CurseForgeProvider(api_key="test-key")
        self.assertEqual(provider.headers["x-api-key"], "test-key")

    def test_get_latest_version_skeleton(self):
        provider = CurseForgeProvider()
        # Should return None instead of hardcoded "1.0.0"
        self.assertIsNone(provider.get_latest_version("123"))

    def test_get_download_url_skeleton(self):
        provider = CurseForgeProvider()
        self.assertIsNone(provider.get_download_url("123"))
