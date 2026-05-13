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

    @patch('requests.get')
    def test_get_latest_version(self, mock_get):
        mock_get.return_value.json.return_value = {
            "data": [
                {
                    "id": 12345,
                    "displayName": "MyAddon-v1.2.3.zip",
                    "downloadUrl": "http://example.com/addon.zip"
                }
            ]
        }
        mock_get.return_value.status_code = 200
        provider = CurseForgeProvider()
        version = provider.get_latest_version("54321")
        self.assertEqual(version, "12345")
        
        # Verify gameVersionTypeId 517 is in params
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params']['gameVersionTypeId'], 517)
        self.assertEqual(kwargs['params']['pageSize'], 1)

    @patch('requests.get')
    def test_get_download_url(self, mock_get):
        mock_get.return_value.json.return_value = {
            "data": [
                {
                    "id": 12345,
                    "displayName": "MyAddon-v1.2.3.zip",
                    "downloadUrl": "http://example.com/addon.zip"
                }
            ]
        }
        mock_get.return_value.status_code = 200
        provider = CurseForgeProvider()
        url = provider.get_download_url("54321")
        self.assertEqual(url, "http://example.com/addon.zip")
