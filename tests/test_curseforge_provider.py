import unittest
from unittest.mock import patch, MagicMock
from providers.curseforge import CurseForgeProvider

class TestCurseForgeProvider(unittest.TestCase):
    @patch('requests.get')
    def test_search(self, mock_get):
        # First call (slug) returns empty
        mock_response_empty = MagicMock()
        mock_response_empty.json.return_value = {"data": []}
        mock_response_empty.status_code = 200
        
        # Second call (filter) returns data
        mock_response_data = MagicMock()
        mock_response_data.json.return_value = [{"name": "DBM", "id": "123"}]
        mock_response_data.status_code = 200
        
        mock_get.side_effect = [mock_response_empty, mock_response_data]
        
        provider = CurseForgeProvider()
        results = provider.search("DBM")
        
        # Results should match the second call
        self.assertEqual(results[0]['name'], "DBM")
        
        # Verify first call was slug
        args1, kwargs1 = mock_get.call_args_list[0]
        self.assertEqual(kwargs1['params']['slug'], "dbm")
        
        # Verify second call was filter
        args2, kwargs2 = mock_get.call_args_list[1]
        self.assertEqual(kwargs2['params']['searchFilter'], "DBM")

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
