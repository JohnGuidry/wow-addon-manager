# WoW Addon Manager (WAM) README Specification

**Date:** 2026-05-13
**Status:** Approved
**Topic:** README for the WoW Addon Manager CLI tool

## 1. Overview
The README will serve as the primary documentation for the `wow-addon-manager` (WAM). It will be user-centric, focusing on ease of use, installation, and command reference, while briefly explaining the underlying "Folder Analysis" mechanism.

## 2. Target Audience
WoW players who are comfortable with a terminal and want a lightweight, open-source alternative to heavy addon managers.

## 3. Tone
Professional and approachable.

## 4. Proposed Sections

### 4.1. Header
- Project Title: WoW Addon Manager (WAM)
- A brief (1-2 sentence) description.

### 4.2. Features
- Highlight key capabilities: URL-based installation (GitHub), CurseForge integration (Aggregator), clean updates, and registry-based tracking.

### 4.3. Installation
- Prerequisites: Python 3.
- Steps:
    1. Clone the repository.
    2. Install dependencies: `pip install -r requirements.txt`.

### 4.4. Quick Start
- Initial configuration: Explain where `config.json` lives and how to set the `wow_path`.
- First command: Example of `wam list` or `wam install`.

### 4.5. Usage Commands
Detailed breakdown of:
- `install <name> <url>`: For GitHub/Direct URLs.
- `update`: To update all managed addons.
- `list`: To see what's currently managed.
- `remove <name>`: To safely delete an addon.

### 4.6. Configuration
Explain the `config.json` fields:
- `wow_path`: Absolute path to the WoW `AddOns` folder.
- `api_key`: How to obtain and add a CurseForge API key (marked as optional/placeholder).

### 4.7. How it Works
A short section explaining:
- **Folder Analysis:** How WAM scans `.toc` files to identify addons.
- **Registry:** How `.wam_registry.json` tracks metadata for reliable updates.

### 4.8. License
- GPLv3.

## 5. Constraints & Considerations
- Ensure the default path mentioned in the code is noted as a default that likely needs changing.
- Verify that command examples match the `main.py` implementation.
