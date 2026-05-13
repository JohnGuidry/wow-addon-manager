import requests
import logging

logger = logging.getLogger(__name__)

class GitHubProvider:
    def get_latest_version(self, repo_url):
        # repo_url expected as 'owner/repo' or full URL
        repo = repo_url.replace("https://github.com/", "").strip("/")
        api_url = f"https://api.github.com/repos/{repo}/releases/latest"
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                return response.json().get("tag_name")
            else:
                logger.error(f"GitHub API error: {response.status_code} for {api_url}")
        except requests.RequestException as e:
            logger.error(f"Network error fetching GitHub version: {e}")
        return None

    def get_download_url(self, repo_url):
        repo = repo_url.replace("https://github.com/", "").strip("/")
        api_url = f"https://api.github.com/repos/{repo}/releases/latest"
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                assets = data.get("assets", [])
                for asset in assets:
                    if asset['name'].endswith('.zip'):
                        return asset['browser_download_url']
                # Fallback to source zip if no binary asset
                return data.get("zipball_url")
        except requests.RequestException as e:
            logger.error(f"Network error fetching GitHub download URL: {e}")
        return None
