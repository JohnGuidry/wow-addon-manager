import requests
import logging

logger = logging.getLogger(__name__)

class CurseForgeProvider:
    def __init__(self, api_key=None):
        # Using a public aggregator URL (placeholder example)
        self.api_base = "https://api.curseforge.com/v1" # Or a mirror
        self.headers = {"User-Agent": "WAM-Addon-Manager/1.0", "Accept": "application/json"}
        if api_key:
            self.headers["x-api-key"] = api_key
        self.timeout = 10
        self._cache = {}

    def search(self, query):
        if query in self._cache:
            return self._cache[query]

        # Placeholder for actual aggregator API call
        logger.info(f"Searching CurseForge for {query}...")
        try:
            # This endpoint is a placeholder based on common CurseForge API patterns
            url = f"{self.api_base}/mods/search"
            params = {"gameId": 1, "searchFilter": query}
            response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                self._cache[query] = data
                return data
            else:
                logger.error(f"CurseForge API error: {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Network error searching CurseForge: {e}")
        return []

    def _get_latest_file_info(self, project_id):
        """Internal helper to fetch the latest file info for WoW Retail (ID 517)."""
        if project_id in self._cache:
             return self._cache[project_id]
             
        try:
            # gameVersionTypeId 517 is for WoW Retail
            url = f"{self.api_base}/mods/{project_id}/files"
            params = {"gameVersionTypeId": 517, "pageSize": 1}
            response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                files = response.json().get("data", [])
                if files:
                    file_info = files[0]
                    self._cache[project_id] = file_info
                    return file_info
            else:
                logger.error(f"CurseForge API error fetching files for {project_id}: {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Network error fetching CurseForge files for {project_id}: {e}")
        return None

    def get_latest_version(self, project_id):
        file_info = self._get_latest_file_info(project_id)
        if file_info:
            # Use fileId or displayName as version. fileId is more reliable for comparison.
            return str(file_info.get("id"))
        return None

    def get_download_url(self, project_id):
        file_info = self._get_latest_file_info(project_id)
        if file_info:
            return file_info.get("downloadUrl")
        return None
