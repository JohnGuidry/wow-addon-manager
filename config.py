import os
import json

DEFAULT_WOW_PATH = "/home/Ochrus/.local/share/Steam/steamapps/compatdata/4206469918/pfx/drive_c/Program Files (x86)/World of Warcraft/_retail_/Interface/AddOns/"

class ConfigManager:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {"wow_path": DEFAULT_WOW_PATH}

    def get_wow_path(self):
        return self.config.get("wow_path", DEFAULT_WOW_PATH)

    def save_config(self, wow_path):
        self.config["wow_path"] = wow_path
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
