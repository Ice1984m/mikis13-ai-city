#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"

mkdir -p "$ROOT/logs"

LOG="$ROOT/logs/city-$(date +%Y%m%d-%H%M%S).log"

exec > >(tee -a "$LOG") 2>&1

cd "$ROOT"

echo
echo "============================================================"
echo " MIKIS13 AI CITY"
echo " $(date -Iseconds)"
echo "============================================================"

echo
echo "1/4 TESTS"
python tests/test_city.py

echo
echo "2/4 SECURITY"
scripts/security.sh

echo
echo "3/4 CITY COUNCIL"
python engine/city.py

echo
echo "4/4 LEARNING"
python engine/prompt_lab.py

echo
echo "============================================================"
echo " ✅ CITY CYCLE COMPLETE"
echo "============================================================"

echo
cat reports/city-latest.md
