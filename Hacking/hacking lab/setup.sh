#!/bin/bash
# setup.sh - Setup script for hacking-lab
# Installs required tools, creates folder structure, copies scripts, and sets permissions

set -e

LABDIR="$HOME/Projects/hacking-lab"

TOOLS=(nmap sqlmap whois dnsutils hydra john nikto gobuster wfuzz whatweb theharvester feroxbuster dnsenum)

# Install tools
install_tools() {
  echo "[+] Installing required tools..."
  sudo apt-get update
  for tool in "${TOOLS[@]}"; do
    if ! command -v "$tool" >/dev/null; then
      echo "[+] Installing $tool..."
      sudo apt-get install -y "$tool" || echo "[!] Could not install $tool. Please install manually."
    else
      echo "[+] $tool already installed."
    fi
  done
}

# Create folder structure
create_folders() {
  echo "[+] Creating folder structure at $LABDIR..."
  mkdir -p "$LABDIR/recon" "$LABDIR/scans" "$LABDIR/exploits" "$LABDIR/output" "$LABDIR/wordlists" "$LABDIR/.vscode"
}

# Copy scripts
copy_scripts() {
  echo "[+] Copying scripts..."
  cp "$(dirname "$0")/recon/quickrecon.sh" "$LABDIR/recon/"
  cp "$(dirname "$0")/scans/webscan.sh" "$LABDIR/scans/"
  cp "$(dirname "$0")/.vscode/tasks.json" "$LABDIR/.vscode/"
}

# Set permissions
set_permissions() {
  echo "[+] Setting script permissions..."
  chmod +x "$LABDIR/recon/quickrecon.sh" "$LABDIR/scans/webscan.sh"
}

# Main
install_tools
create_folders
copy_scripts
set_permissions

echo "[+] Hacking lab setup complete!"
