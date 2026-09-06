#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"
FILE="$ROOT/state/mode/current"

mkdir -p "$(dirname "$FILE")"

MODE="${1:-status}"

case "$MODE" in

  normal)
    echo "NORMAL" > "$FILE"
    echo "✅ NORMAL mode"
    ;;

  degraded)
    echo "DEGRADED_READ_ONLY" > "$FILE"
    echo "⚠️ DEGRADED READ-ONLY mode"
    ;;

  safe)
    echo "SAFE_MODE" > "$FILE"
    echo "🛡 SAFE MODE"
    ;;

  status)
    cat "$FILE" 2>/dev/null || echo "NORMAL"
    ;;

  *)
    echo "Gebruik:"
    echo "  mikis-city-mode normal"
    echo "  mikis-city-mode degraded"
    echo "  mikis-city-mode safe"
    echo "  mikis-city-mode status"
    exit 2
    ;;

esac
