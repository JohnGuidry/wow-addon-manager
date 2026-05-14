import json
import logging
from pathlib import Path

# Use a module-level logger
logger = logging.getLogger(__name__)

class RegistryManager:
    def __init__(self, path):
        self.path = Path(path)
        self.data = self._load()

    def _load(self):
        """Loads the registry data from the specified path."""
        if not self.path.exists():
            return {"installed_addons": {}}
        
        if self.path.stat().st_size == 0:
            logger.debug(f"Registry file at {self.path} is empty. Initializing new data.")
            return {"installed_addons": {}}
        
        try:
            with self.path.open('r') as f:
                data = json.load(f)
                if not isinstance(data, dict) or "installed_addons" not in data:
                    logger.debug(f"Malformed registry file at {self.path}. Initializing new data.")
                    return {"installed_addons": {}}
                return data
        except (json.JSONDecodeError, IOError) as e:
            logger.debug(f"Error loading registry from {self.path}: {e}")
            return {"installed_addons": {}}

    def _save(self):
        """Saves the current registry data to the specified path."""
        try:
            # Ensure parent directory exists
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open('w') as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            logger.error(f"Error saving registry to {self.path}: {e}")

    def add_addon(self, name, info):
        """Adds or updates an addon in the registry."""
        self.data["installed_addons"][name] = info
        self._save()

    def get_addon(self, name):
        """Retrieves information for a specific addon."""
        return self.data["installed_addons"].get(name)

    def remove_addon(self, name):
        """Removes an addon from the registry."""
        if name in self.data["installed_addons"]:
            del self.data["installed_addons"][name]
            self._save()

    def list_addons(self):
        """Returns a copy of all installed addons."""
        return self.data["installed_addons"].copy()
