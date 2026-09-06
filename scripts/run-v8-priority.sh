#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"

cd "$ROOT"

echo
echo "============================================================"
echo " AI CITY V8 BLUEPRINT PRIORITY"
echo "============================================================"

echo
echo "1/4 VALIDATE"

python tests/test_v8_blueprints.py

echo
echo "2/4 PRIORITIZE"

python engine/blueprint_prioritizer_v8.py

echo
echo "3/4 IMPORT JOBS"

scripts/import-blueprints-v8.sh

echo
echo "4/4 STATUS"

scripts/blueprints-v8-status.sh

echo
echo "✅ V8 priority cycle complete"
