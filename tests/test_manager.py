import unittest
from unittest.mock import MagicMock, patch
import tempfile
import io
import zipfile
from pathlib import Path
from manager import AddonManager

class TestAddonManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.wow_path = Path(self.test_dir.name) / "AddOns"
        self.wow_path.mkdir()
        
        self.mock_config = MagicMock()
        self.mock_config.get_wow_path.return_value = str(self.wow_path)
        
        self.mock_registry = MagicMock()
        self.mock_scanner = MagicMock()
        
        self.manager = AddonManager(self.mock_config, self.mock_registry, self.mock_scanner)

    def tearDown(self):
        self.test_dir.cleanup()

    @patch('requests.get')
    @patch('providers.github.GitHubProvider')
    def test_install_addon_github(self, mock_github_class, mock_get):
        # Mock GitHubProvider
        mock_github = mock_github_class.return_value
        mock_github.get_download_url.return_value = "http://example.com/addon.zip"
        mock_github.get_latest_version.return_value = "1.0.0"
        
        # Mock requests.get
        mock_response = MagicMock()
        
        # Create a dummy zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as z:
            z.writestr('MyAddon/MyAddon.toc', '## Interface: 90000\n## Version: 1.0.0')
            z.writestr('MyAddon/core.lua', '-- empty')
        
        mock_response.content = zip_buffer.getvalue()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        self.manager.install_addon("MyAddon", "https://github.com/user/repo")
        
        # Verify
        self.mock_registry.add_addon.assert_called_once()
        args, kwargs = self.mock_registry.add_addon.call_args
        self.assertEqual(args[0], "MyAddon")
        self.assertEqual(args[1]["version"], "1.0.0")
        self.assertIn("MyAddon", args[1]["folders"])
        
        # Check if files were "extracted"
        self.assertTrue((self.wow_path / "MyAddon" / "MyAddon.toc").exists())

    def test_remove_addon(self):
        # Setup registry info
        self.mock_registry.get_addon.return_value = {
            "folders": ["AddonFolder1", "AddonFolder2", "file_at_root.txt"]
        }
        
        # Create dummy folders and files
        folder1 = self.wow_path / "AddonFolder1"
        folder1.mkdir()
        folder2 = self.wow_path / "AddonFolder2"
        folder2.mkdir()
        file1 = self.wow_path / "file_at_root.txt"
        file1.write_text("content")
        
        self.manager.remove_addon("MyAddon")
        
        self.assertFalse(folder1.exists())
        self.assertFalse(folder2.exists())
        self.assertFalse(file1.exists())
        self.mock_registry.remove_addon.assert_called_once_with("MyAddon")

    @patch('providers.curseforge.CurseForgeProvider')
    @patch('providers.github.GitHubProvider')
    def test_update_all_mixed(self, mock_github_class, mock_curse_class):
        # Setup registry
        self.mock_registry.list_addons.return_value = {
            "GitHubAddon": {
                "source": "github",
                "url": "https://github.com/user/repo",
                "version": "1.0.0",
                "folders": ["GitHubAddon"]
            },
            "CurseAddon": {
                "source": "curseforge",
                "id": "12345",
                "version": "100",
                "folders": ["CurseAddon"]
            }
        }
        
        mock_github = mock_github_class.return_value
        mock_github.get_latest_version.return_value = "1.1.0"
        mock_github.get_download_url.return_value = "http://example.com/github-1.1.0.zip"
        
        mock_curse = mock_curse_class.return_value
        mock_curse.get_latest_version.return_value = "101"
        mock_curse.get_download_url.return_value = "http://example.com/curse-101.zip"
        
        # Setup config for API key
        self.mock_config.config = {"api_key": "test-key"}
        
        with patch.object(self.manager, '_download_and_extract') as mock_download:
            self.manager.update_all()
            
            # Check GitHub update
            mock_download.assert_any_call(
                "GitHubAddon", "http://example.com/github-1.1.0.zip", "1.1.0", "github", "https://github.com/user/repo"
            )
            
            # Check CurseForge update
            mock_download.assert_any_call(
                "CurseAddon", "http://example.com/curse-101.zip", "101", "curseforge", "12345"
            )
            
            self.assertEqual(mock_download.call_count, 2)

    @patch('requests.get')
    def test_download_and_extract_robust(self, mock_get):
        mock_response = MagicMock()
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as z:
            z.writestr('Folder1/file1.txt', 'content')
            z.writestr('file_at_root.txt', 'content')
        
        mock_response.content = zip_buffer.getvalue()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        self.manager._download_and_extract("TestAddon", "http://url", "1.0", "github", "http://repo")
        
        self.mock_registry.add_addon.assert_called_once()
        args, _ = self.mock_registry.add_addon.call_args
        folders = args[1]["folders"]
        self.assertIn("Folder1", folders)
        self.assertIn("file_at_root.txt", folders)
        self.assertEqual(len(folders), 2)

    def test_sync_with_folder_grouping(self):
        # Mock scanner to return multiple folders for the same project
        self.mock_scanner.scan.return_value = {
            "AddonMain": {"X-Curse-Project-ID": "12345", "Version": "1.0"},
            "AddonSub": {"X-Curse-Project-ID": "12345", "Version": "1.0"}
        }
        self.mock_registry.list_addons.return_value = {}
        
        self.manager.sync_with_folder()
        
        # Should call add_addon once with both folders
        self.mock_registry.add_addon.assert_called_once()
        args, kwargs = self.mock_registry.add_addon.call_args
        folders = args[1]["folders"]
        self.assertIn("AddonMain", folders)
        self.assertIn("AddonSub", folders)
        self.assertEqual(len(folders), 2)
        self.assertEqual(args[1]["id"], "12345")

if __name__ == "__main__":
    unittest.main()
