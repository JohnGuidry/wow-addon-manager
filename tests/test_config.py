import unittest
import os
import json
from config import ConfigManager

class TestConfig(unittest.TestCase):
    def test_default_path(self):
        config = ConfigManager(config_path="test_config.json")
        self.assertIn("_retail_/Interface/AddOns", config.get_wow_path())
