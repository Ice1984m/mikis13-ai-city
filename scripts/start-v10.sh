#!/data/data/com.termux/files/usr/bin/bash

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

rm -f "$ROOT/state/v10/OWNER_STOP"

echo "✅ OWNER_STOP removed"
echo "V10 may run again."
