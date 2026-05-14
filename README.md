# WoW Addon Manager (WAM)

A simple, reliable, and open-source CLI tool to manage World of Warcraft addons on Linux (and beyond). WAM focuses on a "Folder Analysis" approach combined with a local registry to ensure your addons are always up-to-date from sources like GitHub and CurseForge.

## Features
- **URL Installation:** Install addons directly from GitHub repository URLs.
- **CurseForge Integration:** Search and install addons via a CurseForge aggregator.
- **Single-Command Updates:** Update all your managed addons with one command: `python main.py update`.
- **Clean Removal:** Safely delete addon folders and their registry entries.
- **Local Registry:** Tracks installed versions and folder mappings for maximum reliability.

## Installation

### Prerequisites
- Python 3.x
- `pip` (Python package installer)

### Steps
1. Clone this repository:
   ```bash
   git clone https://github.com/JohnGuidry/wow-addon-manager
   cd wow-addon-manager
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

1. **Configure your Addon Path:**
   ```bash
   python main.py config --path "/path/to/World of Warcraft/_retail_/Interface/AddOns/"
   ```
   *Note: On Linux/Steam, it's often deep inside the `compatdata` folder.*

2. **(Optional) Set your API keys:**
   ```bash
   # Set CurseForge API key
   python main.py config --api-key "your_curseforge_key"
   
   # Set GitHub Token (to avoid rate limits)
   python main.py config --github-token "your_github_token"
   ```

3. **Search and install an addon:**
   ```bash
   python main.py search "Details"
   python main.py install "Details" 61284
   ```

4. **Sync your existing addons:**
   ```bash
   python main.py sync
   ```

5. **Update everything:**
   ```bash
   python main.py update
   ```

## Usage

WAM provides a simple set of commands to manage your library:

| Command | Description |
| --- | --- |
| `python main.py config` | View or set WoW path, CurseForge key, and GitHub token. |
| `python main.py search <query>` | Search CurseForge for addons. |
| `python main.py install <name> <id/url>` | Install from CurseForge ID or GitHub URL. |
| `python main.py list` | List all addons currently managed by WAM. |
| `python main.py sync` | Import existing addons from your WoW folder into WAM. |
| `python main.py update` | Check for updates and install them for all managed addons. |
| `python main.py remove <name>` | Delete an addon's folders and remove it from the registry. |

## Configuration

WAM uses a `config.json` file for its settings.

- `wow_path`: The absolute path to your World of Warcraft `_retail_/Interface/AddOns` directory.
- `api_key`: (Optional) Your CurseForge API key for searching and metadata.

Example `config.json`:
```json
{
  "wow_path": "/path/to/World of Warcraft/_retail_/Interface/AddOns/",
  "api_key": "your_api_key_here"
}
```

## How it Works

WAM uses a dual-layered approach to addon management:

1. **Folder Analysis:** WAM scans the `.toc` files within your `AddOns` directory to identify versions and project IDs.
2. **Local Registry:** Information about installed addons is mirrored in `.wam_registry.json`. This allows WAM to track which folders belong to which addon, ensuring that "multi-folder" addons are updated and removed cleanly.

## License

This project is licensed under the **GPLv3** License.
