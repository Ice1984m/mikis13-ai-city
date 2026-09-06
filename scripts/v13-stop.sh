#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/state/v13"
touch "$ROOT/state/v13/OWNER_STOP"
echo "V13 OWNER_STOP active"
