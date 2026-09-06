#!/data/data/com.termux/files/usr/bin/bash

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

mkdir -p "$ROOT/state/v11"

touch \
"$ROOT/state/v11/OWNER_STOP"

echo "🛑 OWNER_STOP actief"
