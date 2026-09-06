#!/data/data/com.termux/files/usr/bin/bash

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo
echo "=============================================================="
echo " MIKIS13 AI CITY V11 STATUS"
echo "=============================================================="

if [ -f "$ROOT/state/v11/OWNER_STOP" ]; then
    echo "MODE: OWNER_STOP"
elif [ -f "$ROOT/state/v11/SAFE_MODE" ]; then
    echo "MODE: SAFE_MODE"
else
    echo "MODE: ENABLED"
fi

echo

jq '{
  blueprint_count:.canonical_count,
  blueprint_range:.canonical_range,
  duplicate_names:(.duplicate_names|length)
}' \
"$ROOT/config/blueprints.json"

echo

if [ -f "$ROOT/state/v11/jobs/queue.json" ]; then

    jq '{
      jobs:(.jobs|length),
      active:([
        .jobs[] |
        select(.state=="ACTIVE")
      ]|length),
      ready:([
        .jobs[] |
        select(.state=="READY")
      ]|length),
      blocked:([
        .jobs[] |
        select(.state=="BLOCKED")
      ]|length),
      verified:([
        .jobs[] |
        select(.state=="VERIFIED")
      ]|length)
    }' \
    "$ROOT/state/v11/jobs/queue.json"

fi

echo

python \
"$ROOT/engine/maturity_v11.py" \
summary

echo

if [ -f "$ROOT/state/v11/research/latest.json" ]; then
    jq '{
      repositories:.repositories,
      signals:(.signals|length)
    }' \
    "$ROOT/state/v11/research/latest.json"
fi

echo
echo "Control Tower:"
echo "  $ROOT/public/control-tower/index.html"

echo "=============================================================="
