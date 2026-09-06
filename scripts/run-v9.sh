#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"

cd "$ROOT"

echo
echo "=============================================================="
echo " MIKIS13 AI CITY V9 META EVOLUTION"
echo "=============================================================="

echo
echo "1/5 PROMPT LINT"
python engine/prompt_linter_v9.py

echo
echo "2/5 BLUEPRINT VALIDATION"
python tests/test_v9.py

echo
echo "3/5 META EVOLUTION"
python engine/meta_evolution_v9.py

echo
echo "4/5 CAPABILITY GAP"
python engine/capability_gap_v9.py

echo
echo "5/5 SECURITY"

if [ -f scripts/security.sh ]; then
  bash scripts/security.sh
fi

echo
echo "=============================================================="
echo " ✅ V9 ANALYSIS COMPLETE"
echo "=============================================================="

echo
cat reports/meta-evolution-v9.md
