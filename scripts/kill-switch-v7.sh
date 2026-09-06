#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"

mkdir -p "$ROOT/state/mode"

echo "STOPPED_BY_OWNER" \
  > "$ROOT/state/mode/current"

pkill -f \
  "$ROOT/scripts/watchdog-v6.sh" \
  2>/dev/null || true

pkill -f \
  "$ROOT/scripts/autonomous-v6.sh" \
  2>/dev/null || true

pkill -f \
  "$ROOT/scripts/autonomous-v7.sh" \
  2>/dev/null || true

echo "🛑 AI City workers gestopt door eigenaar."
echo "Start opnieuw met:"
echo "  mikis-city-mode normal"
echo "  mikis-city-v7"
