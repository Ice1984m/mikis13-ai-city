#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATE="$ROOT/state/v11"
LOCK="$STATE/cycle.lock"

mkdir -p "$STATE"

if [ -f "$STATE/OWNER_STOP" ]; then
    echo "🛑 OWNER_STOP"
    exit 0
fi

if ! mkdir "$LOCK" 2>/dev/null; then
    echo "⚠️ V11 cycle already active"
    exit 0
fi

cleanup() {
    rmdir "$LOCK" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

cd "$ROOT"

echo
echo "=============================================================="
echo " MIKIS13 AI CITY V11 EXECUTION CYCLE"
echo "=============================================================="

echo
echo "[1/8] Canonical registry"
python engine/build_registry_v11.py

echo
echo "[2/8] Maturity state"
python engine/maturity_v11.py summary

echo
echo "[3/8] Research factory"
python engine/research_factory_v11.py

echo
echo "[4/8] Dependency graph"
python engine/dependency_graph_v11.py

echo
echo "[5/8] Job queue"
python engine/job_queue_v11.py show

echo
echo "[6/8] Prompt benchmark"
python engine/prompt_benchmark_v11.py \
    --prompt prompts/MASTER-PROMPT-V10.md \
    || true

echo
echo "[7/8] Control Tower"
python engine/control_tower_v11.py

echo
echo "[8/8] Security"

if [ -f scripts/security.sh ]; then
    bash scripts/security.sh
fi

python - <<'PY'
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import tempfile

root=Path.cwd()
state=root/"state"/"v11"
out=state/"checkpoints"/"latest.json"

files=[
    "config/blueprints.json",
    "config/v11-policy.json",
    "state/v11/jobs/queue.json",
    "state/v11/dependencies/graph.json",
    "state/v11/research/latest.json"
]

payload={
    "generated":
        datetime.now(
            timezone.utc
        ).isoformat(),
    "files":{}
}

for rel in files:

    p=root/rel

    if not p.exists():
        continue

    payload["files"][rel]=(
        hashlib.sha256(
            p.read_bytes()
        ).hexdigest()
    )

out.parent.mkdir(
    parents=True,
    exist_ok=True
)

fd,tmp=tempfile.mkstemp(
    dir=out.parent,
    prefix=".checkpoint-",
    text=True
)

with os.fdopen(fd,"w") as fh:
    json.dump(
        payload,
        fh,
        indent=2
    )
    fh.write("\n")
    fh.flush()
    os.fsync(fh.fileno())

os.replace(
    tmp,
    out
)

print("✅ checkpoint:",out)
PY

echo
echo "=============================================================="
echo " ✅ V11 CYCLE COMPLETE"
echo "=============================================================="
