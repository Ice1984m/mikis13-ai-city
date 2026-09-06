#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"

cd "$ROOT"

echo
echo "===== AI CITY DOCTOR ====="

python engine/repair_bot.py

echo
echo "===== INTELLIGENCE ====="

python engine/intelligence_meter.py

echo
echo "===== GIT ====="

git status --short

echo
echo "===== REMOTE ====="

git remote -v
