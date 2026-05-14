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

    def install_addon(self, name, source_id, source="github"):
        provider = None
        version = None
        download_url = None
        url = None
        project_id = None

        if source == "github" or "github.com" in source_id:
            from providers.github import GitHubProvider
            token = self.config.get_github_token()
            provider = GitHubProvider(token=token)
            url = source_id
            download_url = provider.get_download_url(url)
            version = provider.get_latest_version(url)
            source = "github"
        elif source == "curseforge" or source_id.isdigit():
            from providers.curseforge import CurseForgeProvider
            api_key = self.config.config.get("api_key")
            provider = CurseForgeProvider(api_key=api_key)
            project_id = source_id
            download_url = provider.get_download_url(project_id)
            version = provider.get_latest_version(project_id)
            source = "curseforge"
        
        if provider and download_url and version:
            self._download_and_extract(name, download_url, version, source, url or project_id)
        else:
            logger.error(f"Could not find download URL or version for {source_id}")

    def _download_and_extract(self, name, download_url, version, source, identity):
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
                
                addon_info = {
                    "source": source,
                    "version": version,
                    "folders": list(top_level_entries)
                }
                if source == "github":
                    addon_info["url"] = identity
                else:
                    addon_info["id"] = identity
                
                self.registry.add_addon(name, addon_info)
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
            project_id = info.get("id")
            current_version = info.get("version")
            
            provider = None
            version_id = None
            
            if source == "github":
                from providers.github import GitHubProvider
                token = self.config.get_github_token()
                provider = GitHubProvider(token=token)
                version_id = url
            elif source == "curseforge":
                from providers.curseforge import CurseForgeProvider
                api_key = self.config.config.get("api_key")
                provider = CurseForgeProvider(api_key=api_key)
                version_id = project_id
            
            if provider and version_id:
                latest_version = provider.get_latest_version(version_id)
                if latest_version and latest_version != current_version:
                    print(f"Updating {name} from {current_version} to {latest_version}")
                    download_url = provider.get_download_url(version_id)
                    if download_url:
                        self._download_and_extract(name, download_url, latest_version, source, url or project_id)
                else:
                    print(f"{name} is up to date.")
            else:
                print(f"Skipping {name}: Unknown source or missing ID.")

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

    def sync_with_folder(self):
        """Scans the AddOns folder and imports known addons into the registry."""
        print("Scanning AddOns folder for existing addons...")
        found_addons = self.scanner.scan()
        current_registry = self.registry.list_addons()
        
        # Group folders by their project identity
        groups = {} # key: (source, id/url), value: {metadata, folders}
        
        for folder_name, metadata in found_addons.items():
            # Skip if already managed
            if any(folder_name in info.get("folders", []) for info in current_registry.values()):
                continue
                
            source = None
            id_val = None
            url = None
            
            # Try to identify source from TOC metadata
            if "X-Curse-Project-ID" in metadata:
                source = "curseforge"
                id_val = metadata["X-Curse-Project-ID"]
            elif "X-Curse-Packaged-With-Project-ID" in metadata:
                source = "curseforge"
                id_val = metadata["X-Curse-Packaged-With-Project-ID"]
            elif "X-GitHub-Repository" in metadata:
                source = "github"
                url = f"https://github.com/{metadata['X-GitHub-Repository']}"
            elif "X-Website" in metadata:
                ws = metadata["X-Website"].lower()
                if "github.com" in ws:
                    source = "github"
                    url = metadata["X-Website"]
                elif "curseforge.com" in ws:
                    source = "curseforge"
                    # Try to extract slug from URL: .../wow/addons/slug
                    parts = metadata["X-Website"].strip("/").split("/")
                    if "addons" in parts:
                        idx = parts.index("addons")
                        if idx + 1 < len(parts):
                            id_val = parts[idx+1]
                
            if source:
                key = (source, id_val or url)
                if key not in groups:
                    groups[key] = {
                        "metadata": metadata,
                        "folders": []
                    }
                groups[key]["folders"].append(folder_name)
        
        imported_count = 0
        cf_provider = None
        
        for (source, identity), data in groups.items():
            metadata = data["metadata"]
            folders = data["folders"]
            
            # If identity is a slug (not numeric), try to resolve it to an ID for CurseForge
            if source == "curseforge" and not identity.isdigit():
                if cf_provider is None:
                    from providers.curseforge import CurseForgeProvider
                    api_key = self.config.config.get("api_key")
                    cf_provider = CurseForgeProvider(api_key=api_key)
                
                resolved_id = cf_provider.get_id_by_slug(identity)
                if resolved_id:
                    identity = resolved_id
            
            # Use the first folder name as the addon name in registry
            name = folders[0]
            print(f"Found manageable addon: {name} ({source}) with folders: {', '.join(folders)}")
            
            self.registry.add_addon(name, {
                "source": source,
                "id": identity if source == "curseforge" else None,
                "url": identity if source == "github" else None,
                "version": metadata.get("Version", "0.0.0"),
                "folders": folders
            })
            imported_count += 1
        
        print(f"Sync complete. Imported {imported_count} new addons to registry.")
