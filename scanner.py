import re
from pathlib import Path

def parse_toc(content):
    """Parses the content of a .toc file and returns a dictionary of metadata."""
    metadata = {}
    for line in content.splitlines():
        # Match lines starting with ##, followed by key: value
        match = re.match(r'^##\s*([^:]+):\s*(.*)$', line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            metadata[key] = value
    return metadata

class AddonScanner:
    def __init__(self, addon_path):
        """Initializes the scanner with the path to the WoW AddOns folder."""
        self.addon_path = Path(addon_path)

    def scan(self):
        """Scans the addon path for folders containing .toc files and parses them."""
        addons = {}
        if not self.addon_path.exists() or not self.addon_path.is_dir():
            return addons
            
        for folder in self.addon_path.iterdir():
            if folder.is_dir():
                # A WoW addon folder usually contains a .toc file with the same name as the folder
                toc_file = folder / f"{folder.name}.toc"
                if toc_file.exists():
                    try:
                        # Using errors='ignore' to handle potential encoding issues in .toc files
                        with toc_file.open('r', encoding='utf-8', errors='ignore') as f:
                            addons[folder.name] = parse_toc(f.read())
                    except (IOError, OSError):
                        # Gracefully handle I/O errors by skipping the problematic addon
                        continue
        return addons
