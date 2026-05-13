import unittest
import json
from pathlib import Path
import tempfile
from config import ConfigManager, DEFAULT_WOW_PATH

class TestConfig(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for each test to ensure isolation
        self.test_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.test_dir.name) / "test_config.json"

    def tearDown(self):
        # Clean up the temporary directory after each test
        self.test_dir.cleanup()

    def test_default_path(self):
        """Verify that the default path is returned when no config file exists."""
        config = ConfigManager(config_path=self.config_path)
        self.assertEqual(config.get_wow_path(), DEFAULT_WOW_PATH)

    def test_save_and_load_config(self):
        """Verify that saving a path and then loading it works correctly."""
        config = ConfigManager(config_path=self.config_path)
        new_path = "/new/path/to/wow"
        config.save_config(new_path)
        
        # Load again with a new instance to verify persistence
        new_config = ConfigManager(config_path=self.config_path)
        self.assertEqual(new_config.get_wow_path(), new_path)

    def test_corrupted_config(self):
        """Verify that the default path is returned when the config file is corrupted."""
        # Write malformed JSON
        with self.config_path.open('w') as f:
            f.write("{ invalid json")
        
        config = ConfigManager(config_path=self.config_path)
        self.assertEqual(config.get_wow_path(), DEFAULT_WOW_PATH)

    def test_empty_config(self):
        """Verify that the default path is returned when the config file is empty."""
        # Write empty file
        with self.config_path.open('w') as f:
            f.write("")
        
        config = ConfigManager(config_path=self.config_path)
        self.assertEqual(config.get_wow_path(), DEFAULT_WOW_PATH)

    def test_partial_config(self):
        """Verify that missing keys in the config file fall back to defaults."""
        # Write JSON without wow_path
        with self.config_path.open('w') as f:
            json.dump({"other_key": "value"}, f)
        
        config = ConfigManager(config_path=self.config_path)
        self.assertEqual(config.get_wow_path(), DEFAULT_WOW_PATH)

if __name__ == "__main__":
    unittest.main()
