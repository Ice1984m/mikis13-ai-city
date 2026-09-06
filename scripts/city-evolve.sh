#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"

mkdir -p "$ROOT/logs"

LOG="$ROOT/logs/evolve-$(date +%Y%m%d-%H%M%S).log"

exec > >(tee -a "$LOG") 2>&1

cd "$ROOT"

echo
echo "============================================================"
echo " MIKIS13 AI CITY DEVELOPMENT CYCLE"
echo "============================================================"

echo
echo "1/6 REPAIR BOT"

python engine/repair_bot.py

echo
echo "2/6 POLICY TESTS"

python tests/test_city.py

echo
echo "3/6 COUNCIL"

python engine/city.py

echo
echo "4/6 LEARNING"

python engine/prompt_lab.py

echo
echo "5/6 INTELLIGENCE METER"

python engine/intelligence_meter.py

echo
echo "6/6 FINAL REPAIR CHECK"

python engine/repair_bot.py

echo
echo "============================================================"
echo " ✅ DEVELOPMENT CYCLE COMPLETE"
echo "============================================================"
