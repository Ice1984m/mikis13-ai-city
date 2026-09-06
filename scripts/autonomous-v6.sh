#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"
LOGS="$ROOT/logs"

mkdir -p "$LOGS"

LOG="$LOGS/autonomous-$(date +%Y%m%d-%H%M%S).log"

exec > >(tee -a "$LOG") 2>&1

cd "$ROOT"

echo
echo "============================================================"
echo " MIKIS13 AI CITY V6 AUTONOMOUS CYCLE"
echo " $(date -Iseconds)"
echo "============================================================"

echo
echo "1/9 REPAIR"

if [ -f engine/repair_bot.py ]; then
  python engine/repair_bot.py || true
fi

echo
echo "2/9 JOB DISPATCH"

python engine/job_dispatcher_v6.py

echo
echo "3/9 WORKER ASSIGNMENT"

python engine/worker_assignment_v6.py

echo
echo "4/9 TGPT OPTIONAL WORKER"

workers/tgpt-worker-v6.sh || true

echo
echo "5/9 AI CITY COUNCIL"

python engine/city.py

echo
echo "6/9 PROMPT / LEARNING"

if [ -f engine/prompt_improver_v5.py ]; then
  python engine/prompt_improver_v5.py || true
elif [ -f engine/prompt_lab.py ]; then
  python engine/prompt_lab.py || true
fi

echo
echo "7/9 TEST + SECURITY"

python tests/test_city.py

if [ -f tests/test_v5.py ]; then
  python tests/test_v5.py
fi

bash scripts/security.sh

echo
echo "8/9 HEARTBEAT"

python engine/heartbeat_v6.py

echo
echo "9/9 GITHUB READ-ONLY SYNC"

git fetch origin --prune

echo
echo "============================================================"
echo " ✅ V6 AUTONOMOUS CYCLE COMPLETE"
echo "============================================================"
