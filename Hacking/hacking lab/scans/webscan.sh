#!/bin/bash
# webscan.sh - Automated web scanning script
# Usage: ./webscan.sh <target_url> [wordlist]
# Saves output to ../output/ with timestamped filenames

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <target_url> [wordlist]"
  exit 1
fi

TARGET="$1"
WORDLIST="${2:-/usr/share/wordlists/dirb/common.txt}"
OUTDIR="$(dirname "$0")/../output"
TS="$(date +%Y%m%d-%H%M%S)"

mkdir -p "$OUTDIR"

# Nikto
if command -v nikto >/dev/null; then
  nikto -h "$TARGET" > "$OUTDIR/nikto-$TS.txt"
  echo "[+] Nikto saved to $OUTDIR/nikto-$TS.txt"
else
  echo "[!] nikto not found. Skipping."
fi

# WhatWeb
if command -v whatweb >/dev/null; then
  whatweb "$TARGET" > "$OUTDIR/whatweb-$TS.txt"
  echo "[+] WhatWeb saved to $OUTDIR/whatweb-$TS.txt"
else
  echo "[!] whatweb not found. Skipping."
fi

# Gobuster or Feroxbuster
if command -v gobuster >/dev/null; then
  gobuster dir -u "$TARGET" -w "$WORDLIST" -o "$OUTDIR/gobuster-$TS.txt"
  echo "[+] Gobuster saved to $OUTDIR/gobuster-$TS.txt"
elif command -v feroxbuster >/dev/null; then
  feroxbuster -u "$TARGET" -w "$WORDLIST" -o "$OUTDIR/feroxbuster-$TS.txt"
  echo "[+] Feroxbuster saved to $OUTDIR/feroxbuster-$TS.txt"
else
  echo "[!] Neither gobuster nor feroxbuster found. Skipping."
fi

echo "Web scan complete."
