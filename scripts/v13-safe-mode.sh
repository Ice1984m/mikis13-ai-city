#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/state/v13"
touch "$ROOT/state/v13/SAFE_MODE"
echo "V13 SAFE_MODE active (read-only jobs only; mutations are disabled anyway)"
