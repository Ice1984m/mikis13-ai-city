#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATE="$ROOT/state/v10"
mkdir -p "$STATE/tgpt"

if [ -f "$STATE/OWNER_STOP" ]; then
    echo "OWNER_STOP active"
    exit 0
fi

if ! command -v tgpt >/dev/null 2>&1; then
    echo "TGPT unavailable"
    exit 0
fi

SCOUT="$STATE/scouts/latest.json"

[ -f "$SCOUT" ] || {
    echo "No scout evidence"
    exit 0
}

CONTEXT="$(
python - "$SCOUT" <<'PY'
import json,sys

data=json.load(open(sys.argv[1]))

summary={
  "cycle_id":data.get("cycle_id"),
  "repo_count":data.get("repo_count"),
  "signals":data.get("signals",[])[:10]
}

print(json.dumps(summary,ensure_ascii=False))
PY
)"

PROMPT=$(cat <<EOF
You are a bounded Mikis13 V10 engineering analyst.

You have READ-ONLY scout evidence.

Rules:
- do not invent evidence;
- UNKNOWN is not PASS;
- prefer existing repositories;
- propose only one smallest useful next action;
- do not propose force push;
- do not propose direct main mutation;
- do not propose payments, crypto, mass email or paid ads;
- do not output a shell script for automatic execution;
- identify counterevidence;
- specify success condition and rollback if mutation would later occur.

Return concise JSON-compatible analysis with:
problem
evidence
unknowns
root_cause_hypothesis
counterevidence
recommended_repository
smallest_next_action
worker_roles
test
security_check
healthcheck
rollback
stop_condition

SCOUT EVIDENCE:
$CONTEXT
EOF
)

OUT="$STATE/tgpt/$(date -u +%Y%m%dT%H%M%SZ).txt"

if command -v timeout >/dev/null 2>&1; then
    timeout 120 tgpt "$PROMPT" > "$OUT" 2>&1 || true
else
    tgpt "$PROMPT" > "$OUT" 2>&1 || true
fi

ln -sf "$(basename "$OUT")" "$STATE/tgpt/latest.txt"

echo "TGPT proposal:"
echo "$OUT"
