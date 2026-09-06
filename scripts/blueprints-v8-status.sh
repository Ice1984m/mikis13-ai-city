#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"

echo "===== V8 PRIORITY ====="

jq . \
  "$ROOT/state/blueprint-priority/latest.json" \
  2>/dev/null || true

echo
echo "===== TOP 10 ====="

jq -r '
  .top10[] |
  "#\(.id) \(.name) | score=\(.priority_score) | impact=\(.expected_impact) | complexity=\(.complexity)"
' \
  "$ROOT/state/blueprint-priority/latest.json" \
  2>/dev/null || true
