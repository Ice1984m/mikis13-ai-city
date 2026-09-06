#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"
STATE="$ROOT/state/tgpt"

mkdir -p "$STATE"

if ! command -v tgpt >/dev/null 2>&1; then
  echo '{"status":"SKIPPED","reason":"tgpt unavailable"}' \
    > "$STATE/reliable-latest.json"

  exit 0
fi

ACTIVE="$ROOT/state/jobs/active.json"

[ -s "$ACTIVE" ] || {
  echo '{"status":"SKIPPED","reason":"no active job"}' \
    > "$STATE/reliable-latest.json"

  exit 0
}

TITLE="$(jq -r '.title // "unknown"' "$ACTIVE")"
GOAL="$(jq -r '.goal // ""' "$ACTIVE")"

PROMPT="
Mikis13 AI City V7 bounded local worker.

Task:
$TITLE

Goal:
$GOAL

Do not execute commands.
Do not expose secrets.
Do not propose destructive persistence.

Return:
CLAIM
EVIDENCE_TO_VERIFY
RISK
ALTERNATIVE
SMALLEST_NEXT_ACTION
TEST
ROLLBACK
"

OUT="$STATE/reliable-output.txt"

SUCCESS=0

for ATTEMPT in 1 2; do

  if timeout 90 \
      tgpt "$PROMPT" \
      > "$OUT" 2>&1
  then
      SUCCESS=1
      break
  fi

  sleep 3
done

if [ "$SUCCESS" -eq 1 ]; then

  jq -n \
    --arg status "SUCCESS" \
    --arg title "$TITLE" \
    --arg output "$OUT" \
    '{
       status:$status,
       title:$title,
       output:$output
     }' \
    > "$STATE/reliable-latest.json"

else

  jq -n \
    --arg status "FAILED" \
    --arg title "$TITLE" \
    '{
       status:$status,
       title:$title
     }' \
    > "$STATE/reliable-latest.json"

fi
