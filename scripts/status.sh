#!/data/data/com.termux/files/usr/bin/bash

ROOT="$HOME/mikis13-ai-city"

echo
echo "===== LATEST DECISION ====="

jq '.decision' \
 "$ROOT/state/decisions/latest.json" \
 2>/dev/null || echo "Nog geen beslissing"

echo
echo "===== LEARNING ====="

jq . \
 "$ROOT/state/learning/patterns.json" \
 2>/dev/null || true

echo
echo "===== REPORT ====="

cat \
 "$ROOT/reports/city-latest.md" \
 2>/dev/null || true
