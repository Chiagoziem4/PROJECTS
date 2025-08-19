#!/bin/bash
# quickrecon.sh - Automated reconnaissance script
# Usage: ./quickrecon.sh <target>
# Saves output to ../output/ with timestamped filenames

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <target>"
  exit 1
fi

TARGET="$1"
OUTDIR="$(dirname "$0")/../output"
TS="$(date +%Y%m%d-%H%M%S)"

mkdir -p "$OUTDIR"

# WHOIS
whois "$TARGET" > "$OUTDIR/whois-$TARGET-$TS.txt"
echo "[+] WHOIS saved to $OUTDIR/whois-$TARGET-$TS.txt"

# DIG
if command -v dig >/dev/null; then
  dig "$TARGET" ANY +noall +answer > "$OUTDIR/dig-$TARGET-$TS.txt"
  echo "[+] DIG saved to $OUTDIR/dig-$TARGET-$TS.txt"
else
  echo "[!] dig not found. Skipping."
fi

# DNSENUM
if command -v dnsenum >/dev/null; then
  dnsenum "$TARGET" > "$OUTDIR/dnsenum-$TARGET-$TS.txt"
  echo "[+] DNSENUM saved to $OUTDIR/dnsenum-$TARGET-$TS.txt"
else
  echo "[!] dnsenum not found. Skipping."
fi

# theHarvester
if command -v theHarvester >/dev/null; then
  theHarvester -d "$TARGET" -b all > "$OUTDIR/theHarvester-$TARGET-$TS.txt"
  echo "[+] theHarvester saved to $OUTDIR/theHarvester-$TARGET-$TS.txt"
else
  echo "[!] theHarvester not found. Skipping."
fi

echo "Recon complete."
