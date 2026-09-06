#!/data/data/com.termux/files/usr/bin/bash

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo
echo "===== MIKIS13 V11 STATUS ====="

if [ -f "$ROOT/state/v11/OWNER_STOP" ]; then
    echo "MODE=OWNER_STOP"
else
    echo "MODE=ENABLED"
fi

jq '{
  version,
  canonical_count,
  canonical_range
}' \
"$ROOT/config/blueprints.json"

echo
python "$ROOT/engine/maturity_v11.py"

echo
if [ -f "$ROOT/state/v11/jobs/queue.json" ]; then
    jq '{
      jobs:(.jobs|length)
    }' \
    "$ROOT/state/v11/jobs/queue.json"
fi
