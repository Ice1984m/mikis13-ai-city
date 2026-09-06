#!/data/data/com.termux/files/usr/bin/bash

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

mkdir -p "$ROOT/state/v10"
touch "$ROOT/state/v10/OWNER_STOP"

echo "🛑 OWNER_STOP enabled"
