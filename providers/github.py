import requests
import logging

logger = logging.getLogger(__name__)

class GitHubProvider:
    def __init__(self, token=None):
        self._cache = {}
        self.headers = {"User-Agent": "WAM-Addon-Manager/1.0"}
        if token:
            self.headers["Authorization"] = f"token {token}"

    def _get_release_info(self, repo_url):
        repo = repo_url.replace("https://github.com/", "").strip("/")
        if repo in self._cache:
            return self._cache[repo]

        api_url = f"https://api.github.com/repos/{repo}/releases/latest"
        try:
            response = requests.get(api_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                self._cache[repo] = response.json()
                return self._cache[repo]
            elif response.status_code == 404:
                logger.info(f"No releases found for {repo}, falling back to tags")
                tags_url = f"https://api.github.com/repos/{repo}/tags"
                response = requests.get(tags_url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    tags = response.json()
                    if tags:
                        latest_tag = tags[0]
                        release_info = {
                            "tag_name": latest_tag.get("name"),
                            "zipball_url": latest_tag.get("zipball_url"),
                            "assets": []
                        }
                        self._cache[repo] = release_info
                        return release_info
                    else:
                        logger.error(f"No tags found for {repo}")
                else:
                    logger.error(f"GitHub API error (tags): {response.status_code} for {tags_url}")
            elif response.status_code == 403:
                logger.error(f"GitHub API rate limit exceeded or forbidden: {response.status_code}. Consider setting a GitHub Token in config.")
            else:
                logger.error(f"GitHub API error (releases): {response.status_code} for {api_url}")
        except requests.RequestException as e:
            logger.error(f"Network error fetching GitHub info for {repo}: {e}")
        return None

    def get_latest_version(self, repo_url):
        info = self._get_release_info(repo_url)
        return info.get("tag_name") if info else None

    def get_download_url(self, repo_url):
        info = self._get_release_info(repo_url)
        if not info:
            return None
        
        assets = info.get("assets", [])
        for asset in assets:
            if asset['name'].endswith('.zip'):
                return asset['browser_download_url']
        return info.get("zipball_url")
