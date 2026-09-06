#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

rm -f \
"$ROOT/state/v11/OWNER_STOP"

echo "✅ V11 ENABLED"
