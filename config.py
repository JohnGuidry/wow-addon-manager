import json
from pathlib import Path

DEFAULT_WOW_PATH = str(Path.home() / ".local/share/Steam/steamapps/compatdata/4206469918/pfx/drive_c/Program Files (x86)/World of Warcraft/_retail_/Interface/AddOns/")

class ConfigManager:
    def __init__(self, config_path="config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()

    def load_config(self):
        if self.config_path.exists():
            try:
                with self.config_path.open('r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If the config file is corrupted or can't be read, fall back to defaults
                pass
        return {"wow_path": DEFAULT_WOW_PATH}

    def get_wow_path(self):
        return self.config.get("wow_path", DEFAULT_WOW_PATH)

    def get_github_token(self):
        return self.config.get("github_token")

    def is_path_valid(self):
        path = Path(self.get_wow_path())
        return path.exists() and path.is_dir()

    def save_config(self, wow_path=None, api_key=None, github_token=None):
        if wow_path:
            self.config["wow_path"] = wow_path.strip()
        if api_key:
            self.config["api_key"] = api_key.strip()
        if github_token:
            self.config["github_token"] = github_token.strip()
        with self.config_path.open('w') as f:
            json.dump(self.config, f, indent=2)
