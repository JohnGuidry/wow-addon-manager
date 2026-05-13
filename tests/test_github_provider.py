import unittest
from unittest.mock import patch, MagicMock
from providers.github import GitHubProvider

class TestGitHubProvider(unittest.TestCase):
    @patch('requests.get')
    def test_get_latest_version(self, mock_get):
        mock_get.return_value.json.return_value = {"tag_name": "v1.2.3"}
        mock_get.return_value.status_code = 200
        provider = GitHubProvider()
        version = provider.get_latest_version("owner/repo")
        self.assertEqual(version, "v1.2.3")
        
        # Verify headers and timeout
        mock_get.assert_called_with(
            "https://api.github.com/repos/owner/repo/releases/latest",
            headers={"User-Agent": "WAM-Addon-Manager/1.0"},
            timeout=10
        )

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

    @patch('requests.get')
    def test_caching(self, mock_get):
        mock_get.return_value.json.return_value = {"tag_name": "v1.2.3", "assets": []}
        mock_get.return_value.status_code = 200
        provider = GitHubProvider()
        
        provider.get_latest_version("owner/repo")
        provider.get_download_url("owner/repo")
        
        # Should only be called once due to cache
        self.assertEqual(mock_get.call_count, 1)

    @patch('requests.get')
    def test_tag_fallback(self, mock_get):
        # First call (releases/latest) returns 404
        # Second call (tags) returns list of tags
        mock_response_404 = MagicMock()
        mock_response_404.status_code = 404
        
        mock_response_tags = MagicMock()
        mock_response_tags.status_code = 200
        mock_response_tags.json.return_value = [
            {"name": "v1.2.3", "zipball_url": "https://api.github.com/repos/owner/repo/zipball/v1.2.3"}
        ]
        
        mock_get.side_effect = [mock_response_404, mock_response_tags]
        
        provider = GitHubProvider()
        version = provider.get_latest_version("owner/repo")
        
        self.assertEqual(version, "v1.2.3")
        self.assertEqual(mock_get.call_count, 2)
        
        # Verify second call URL
        mock_get.assert_called_with(
            "https://api.github.com/repos/owner/repo/tags",
            headers={"User-Agent": "WAM-Addon-Manager/1.0"},
            timeout=10
        )
