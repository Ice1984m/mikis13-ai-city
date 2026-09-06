#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
rm -f "$ROOT/state/v13/OWNER_STOP"
echo "V13 execution unlocked; mutation remains disabled by policy"
