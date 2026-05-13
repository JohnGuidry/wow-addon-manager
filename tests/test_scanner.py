import unittest
import tempfile
import shutil
from pathlib import Path
from scanner import parse_toc, AddonScanner

class TestScanner(unittest.TestCase):
    def test_parse_toc(self):
        toc_content = "## Interface: 100205\n## Title: MyAddon\n## Version: 1.0.0\n## X-Curse-Project-ID: 12345"
        metadata = parse_toc(toc_content)
        self.assertEqual(metadata['Title'], 'MyAddon')
        self.assertEqual(metadata['Version'], '1.0.0')
        self.assertEqual(metadata['X-Curse-Project-ID'], '12345')

    def test_addon_scanner(self):
        # Create a temporary directory structure for testing
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create a mock addon folder
            addon_name = "TestAddon"
            addon_dir = tmp_path / addon_name
            addon_dir.mkdir()
            
            toc_content = "## Interface: 100205\n## Title: Test Addon\n## Version: 1.2.3"
            toc_file = addon_dir / f"{addon_name}.toc"
            toc_file.write_text(toc_content)
            
            # Create another folder without a .toc file (should be ignored)
            ignored_dir = tmp_path / "IgnoredFolder"
            ignored_dir.mkdir()
            
            scanner = AddonScanner(tmpdir)
            addons = scanner.scan()
            
            self.assertIn(addon_name, addons)
            self.assertEqual(addons[addon_name]['Title'], 'Test Addon')
            self.assertEqual(addons[addon_name]['Version'], '1.2.3')
            self.assertNotIn("IgnoredFolder", addons)

    def test_scan_nonexistent_directory(self):
        scanner = AddonScanner("/non/existent/path")
        addons = scanner.scan()
        self.assertEqual(addons, {})

if __name__ == '__main__':
    unittest.main()
