#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATE="$ROOT/state/v10"
LOCK="$STATE/cycle.lock"

mkdir -p "$STATE"

if [ -f "$STATE/OWNER_STOP" ]; then
    echo "🛑 Mikis13 V10 OWNER_STOP"
    exit 0
fi

if ! mkdir "$LOCK" 2>/dev/null; then
    echo "Another V10 cycle is already active"
    exit 0
fi

cleanup() {
    rmdir "$LOCK" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo
echo "=============================================================="
echo " MIKIS13 AI CITY V10 BACKGROUND CYCLE"
echo "=============================================================="

cd "$ROOT"

echo
echo "[1/6] Blueprint registry"
python engine/build_registry_v10.py

echo
echo "[2/6] GitHub scouts"
python engine/scout_cycle_v10.py

echo
echo "[3/6] Coordinator"
python engine/coordinator_v10.py

echo
echo "[4/6] TGPT reasoning"
bash scripts/tgpt-v10.sh || true

echo
echo "[5/6] Security"
if [ -f scripts/security.sh ]; then
    bash scripts/security.sh
fi

echo
echo "[6/6] Checkpoint"

python - <<'PY'
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

root=Path.cwd()
state=root/"state"/"v10"

payload={
    "time":datetime.now(timezone.utc).isoformat(),
    "files":{}
}

for rel in [
    "config/blueprints.json",
    "config/v10-policy.json",
    "state/v10/decision.json"
]:
    p=root/rel

    if p.exists():
        payload["files"][rel]=hashlib.sha256(
            p.read_bytes()
        ).hexdigest()

out=state/"checkpoints"/"latest.json"
out.parent.mkdir(parents=True,exist_ok=True)

out.write_text(
    json.dumps(payload,indent=2)+"\n"
)

print("✅ checkpoint",out)
PY

echo
echo "✅ V10 cycle complete"
