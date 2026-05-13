import unittest
from unittest.mock import patch
from providers.github import GitHubProvider

class TestGitHubProvider(unittest.TestCase):
    @patch('requests.get')
    def test_get_latest_version(self, mock_get):
        mock_get.return_value.json.return_value = {"tag_name": "v1.2.3"}
        mock_get.return_value.status_code = 200
        provider = GitHubProvider()
        version = provider.get_latest_version("owner/repo")
        self.assertEqual(version, "v1.2.3")

    @patch('requests.get')
    def test_get_download_url_with_asset(self, mock_get):
        mock_get.return_value.json.return_value = {
            "assets": [
                {"name": "addon.zip", "browser_download_url": "https://github.com/owner/repo/releases/download/v1.2.3/addon.zip"}
            ]
        }
        mock_get.return_value.status_code = 200
        provider = GitHubProvider()
        url = provider.get_download_url("owner/repo")
        self.assertEqual(url, "https://github.com/owner/repo/releases/download/v1.2.3/addon.zip")

    @patch('requests.get')
    def test_get_download_url_fallback(self, mock_get):
        mock_get.return_value.json.return_value = {
            "assets": [],
            "zipball_url": "https://api.github.com/repos/owner/repo/zipball/v1.2.3"
        }
        mock_get.return_value.status_code = 200
        provider = GitHubProvider()
        url = provider.get_download_url("owner/repo")
        self.assertEqual(url, "https://api.github.com/repos/owner/repo/zipball/v1.2.3")
