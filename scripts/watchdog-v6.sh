#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"

LOCK="$ROOT/state/watchdog/cycle.lock"
mkdir -p "$(dirname "$LOCK")"

exec 9>"$LOCK"

if ! flock -n 9; then
  echo "ℹ️ Andere AI City-cyclus is actief."
  exit 0
fi

if ! "$ROOT/scripts/autonomous-v6.sh"; then
  echo "$(date -Iseconds) cycle failed" \
    >> "$ROOT/logs/watchdog.log"

  sleep 30

  "$ROOT/scripts/autonomous-v6.sh" || true
fi
