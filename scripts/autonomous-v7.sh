#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"
MODE_FILE="$ROOT/state/mode/current"

MODE="$(
  cat "$MODE_FILE" 2>/dev/null ||
  echo NORMAL
)"

if [ "$MODE" = "STOPPED_BY_OWNER" ]; then
  echo "🛑 Systeem staat uit via kill switch."
  exit 0
fi

cd "$ROOT"

echo
echo "============================================================"
echo " MIKIS13 AI CITY V7 RESILIENCE CYCLE"
echo "============================================================"

echo "1/10 RESILIENCE"
python engine/resilience_v7.py

echo "2/10 CHECKPOINT"
python - <<'PY'
from engine.resilience_v7 import checkpoint
print(checkpoint("before-v7-cycle"))
PY

echo "3/10 CRASH RECOVERY"
python engine/crash_recovery_v7.py

echo "4/10 CRITICAL PATH"
python engine/critical_path_v7.py

if [ "$MODE" = "DEGRADED_READ_ONLY" ] || \
   [ "$MODE" = "SAFE_MODE" ]
then

  echo "⚠️ $MODE: geen uitvoerende workers."

  python engine/heartbeat_v6.py || true

  exit 0
fi

echo "5/10 JOB DISPATCH"
python engine/job_dispatcher_v6.py

echo "6/10 WORKERS"
python engine/worker_assignment_v6.py
python engine/adaptive_workers_v7.py

echo "7/10 TGPT RELIABLE"
workers/tgpt-reliable-v7.sh || true

echo "8/10 COUNCIL"
python engine/city.py

echo "9/10 SANDBOX TEST"
scripts/worktree-v7.sh

echo "10/10 HEARTBEAT"
python engine/heartbeat_v6.py

python - <<'PY'
from engine.resilience_v7 import checkpoint
print(checkpoint("after-v7-cycle"))
PY

echo
echo "✅ V7 cycle complete"
