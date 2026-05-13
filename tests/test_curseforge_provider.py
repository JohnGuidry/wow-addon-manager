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
