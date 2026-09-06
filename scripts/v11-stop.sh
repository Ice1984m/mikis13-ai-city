#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

mkdir -p "$ROOT/state/v11"

touch \
"$ROOT/state/v11/OWNER_STOP"

echo "🛑 V11 OWNER_STOP ACTIVE"
