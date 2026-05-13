import unittest
import os
import json
import tempfile
from pathlib import Path
from registry import RegistryManager

class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_file = Path(self.test_dir.name) / "test_registry.json"

    def tearDown(self):
        self.test_dir.cleanup()

    def test_add_remove_addon(self):
        reg = RegistryManager(self.test_file)
        reg.add_addon("MyAddon", {"source": "github", "version": "1.0.0", "folders": ["MyAddon"]})
        self.assertEqual(reg.get_addon("MyAddon")["version"], "1.0.0")
        reg.remove_addon("MyAddon")
        self.assertIsNone(reg.get_addon("MyAddon"))

    def test_list_addons(self):
        reg = RegistryManager(self.test_file)
        reg.add_addon("Addon1", {"version": "1.0.0"})
        reg.add_addon("Addon2", {"version": "2.0.0"})
        addons = reg.list_addons()
        self.assertEqual(len(addons), 2)
        self.assertIn("Addon1", addons)
        self.assertIn("Addon2", addons)

    def test_corrupt_json(self):
        with open(self.test_file, 'w') as f:
            f.write("invalid json")
        reg = RegistryManager(self.test_file)
        # Should handle error and return empty dict for addons
        self.assertEqual(reg.list_addons(), {})

    def test_save_creates_directory(self):
        # Test that _save creates parent directories if they don't exist
        nested_dir = Path(self.test_dir.name) / "subdir" / "registry.json"
        reg = RegistryManager(nested_dir)
        reg.add_addon("TestAddon", {"version": "1.0.0"})
        self.assertTrue(nested_dir.exists())
        self.assertEqual(reg.get_addon("TestAddon")["version"], "1.0.0")

    def test_list_addons_is_copy(self):
        reg = RegistryManager(self.test_file)
        reg.add_addon("Addon1", {"version": "1.0.0"})
        addons = reg.list_addons()
        # Modifying the returned dict should not affect internal state
        addons["Addon1"] = {"version": "2.0.0"}
        self.assertEqual(reg.get_addon("Addon1")["version"], "1.0.0")

if __name__ == "__main__":
    unittest.main()
