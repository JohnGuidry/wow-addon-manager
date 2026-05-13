# WoW Addon Manager (WAM)

A simple, reliable, and open-source CLI tool to manage World of Warcraft addons on Linux (and beyond). WAM focuses on a "Folder Analysis" approach combined with a local registry to ensure your addons are always up-to-date from sources like GitHub and CurseForge.

## Features
- **URL Installation:** Install addons directly from GitHub repository URLs.
- **CurseForge Integration:** Search and install addons via a CurseForge aggregator.
- **Single-Command Updates:** Update all your managed addons with one command: `wam update`.
- **Clean Removal:** Safely delete addon folders and their registry entries.
- **Local Registry:** Tracks installed versions and folder mappings for maximum reliability.

## Installation

### Prerequisites
- Python 3.x
- `pip` (Python package installer)

### Steps
1. Clone this repository:
   ```bash
   git clone https://github.com/Ochrus/wow-addon-manager.git
   cd wow-addon-manager
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

1. **Configure your Addon Path:**
   Open `config.json` (created on first run or manually) and set your `wow_path`.
   *Note: On Linux/Steam, it's often deep inside the `compatdata` folder.*

2. **List your addons:**
   ```bash
   python main.py list
   ```

3. **Install an addon from GitHub:**
   ```bash
   python main.py install WeakAuras https://github.com/WeakAuras/WeakAuras2
   ```

## Usage

WAM provides a simple set of commands to manage your library:

| Command | Description |
| --- | --- |
| `python main.py list` | List all addons currently managed by WAM. |
| `python main.py install <name> <url>` | Install a new addon from a GitHub URL. |
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
