# Hacking Lab

A modular, scriptable offensive security lab inspired by Kali Linux, designed for automation and extensibility inside VS Code on Ubuntu.

## Folder Structure
```
hacking-lab/
├── recon/         # Reconnaissance scripts
├── scans/         # Scanning scripts
├── exploits/      # Exploit scripts/tools
├── output/        # All tool/script output (timestamped)
├── wordlists/     # Wordlists for brute-forcing, fuzzing, etc.
└── .vscode/       # VS Code tasks for automation
```

## Setup
1. Run `setup.sh` to install all required tools, create folders, and set permissions:
   ```bash
   bash setup.sh
   ```
2. Open the folder in VS Code.
3. Use the VS Code task runner (Ctrl+Shift+P → Run Task) to launch recon or scan scripts.

## Usage
- **Recon:**
  - Run `quickrecon.sh <target>` (domain or IP)
  - Output saved in `output/` with timestamps
- **Web Scan:**
  - Run `webscan.sh <target_url> [wordlist]`
  - Output saved in `output/` with timestamps

## Adding More Tools
- Add new scripts to `recon/`, `scans/`, or `exploits/` as needed.
- Update `.vscode/tasks.json` to integrate new scripts with the VS Code task runner.
- Place custom wordlists in `wordlists/`.

## Notes
- All scripts are commented for clarity.
- Output is always saved in `output/` for easy review.
- Scripts check for required tools and skip steps if missing.

## Extending the Lab
- Clone or download additional wordlists (e.g., SecLists) into `wordlists/`.
- Add new automation scripts for post-exploitation, reporting, etc.
- Use the setup script as a template for future tool installations.

---
Happy hacking!
