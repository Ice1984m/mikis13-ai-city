#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
[ -f state/v13/OWNER_STOP ] && { echo "OWNER_STOP"; exit 0; }
python engine/federation_v13.py init >/dev/null
python engine/global_worker_v13.py local-once --node TERMUX-HOME-01
python engine/federation_v13.py status
