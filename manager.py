import requests
import zipfile
import io
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class AddonManager:
    def __init__(self, config, registry, scanner):
        self.config = config
        self.registry = registry
        self.scanner = scanner

    def install_from_url(self, name, url, source="github"):
        if source == "github" or "github.com" in url:
            from providers.github import GitHubProvider
            provider = GitHubProvider()
            download_url = provider.get_download_url(url)
            version = provider.get_latest_version(url)
            
            if download_url and version:
                self._download_and_extract(name, download_url, version, "github", url)
            else:
                logger.error(f"Could not find download URL or version for {url}")
        else:
            logger.error(f"Unsupported source: {source}")

    def _download_and_extract(self, name, download_url, version, source, url):
        print(f"Downloading {name} from {download_url}...")
        try:
            r = requests.get(download_url, timeout=30, headers={"User-Agent": "WAM-Addon-Manager/1.0"})
            r.raise_for_status()
            
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                addon_path = Path(self.config.get_wow_path())
                if not addon_path.exists():
                    addon_path.mkdir(parents=True, exist_ok=True)
                
                members = z.namelist()
                # Extract top-level folders/files in the ZIP to track for removal
                top_level_entries = set()
                for m in members:
                    parts = Path(m).parts
                    if parts:
                        top_level_entries.add(parts[0])
                
                z.extractall(addon_path)
                
                self.registry.add_addon(name, {
                    "source": source,
                    "url": url,
                    "version": version,
                    "folders": list(top_level_entries)
                })
                print(f"Successfully installed {name} version {version}")
        except Exception as e:
            logger.error(f"Failed to install {name}: {e}")
            print(f"Failed to install {name}: {e}")

    def update_all(self):
        installed = self.registry.list_addons()
        for name, info in installed.items():
            print(f"Checking updates for {name}...")
            source = info.get("source")
            url = info.get("url")
            current_version = info.get("version")
            
            if source == "github":
                from providers.github import GitHubProvider
                provider = GitHubProvider()
                latest_version = provider.get_latest_version(url)
                if latest_version and latest_version != current_version:
                    print(f"Updating {name} from {current_version} to {latest_version}")
                    download_url = provider.get_download_url(url)
                    if download_url:
                        self._download_and_extract(name, download_url, latest_version, source, url)
                else:
                    print(f"{name} is up to date.")

    def remove_addon(self, name):
        info = self.registry.get_addon(name)
        if info:
            addon_path = Path(self.config.get_wow_path())
            for folder in info.get("folders", []):
                full_path = addon_path / folder
                if full_path.exists():
                    print(f"Removing {full_path}")
                    if full_path.is_dir():
                        shutil.rmtree(full_path)
                    else:
                        full_path.unlink()
            self.registry.remove_addon(name)
            print(f"Removed {name}")
        else:
            print(f"Addon {name} not found in registry.")
