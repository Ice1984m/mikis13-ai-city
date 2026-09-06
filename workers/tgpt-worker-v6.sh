#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"
STATE="$ROOT/state/tgpt"

mkdir -p "$STATE"

ACTIVE="$ROOT/state/jobs/active.json"
OUT="$STATE/latest.txt"
META="$STATE/latest.json"

if [ ! -s "$ACTIVE" ]; then
  echo "Geen actieve taak."
  exit 0
fi

TITLE="$(jq -r '.title // "unknown"' "$ACTIVE")"
GOAL="$(jq -r '.goal // ""' "$ACTIVE")"

if ! command -v tgpt >/dev/null 2>&1; then
  jq -n \
    --arg status "SKIPPED" \
    --arg reason "tgpt not installed" \
    --arg title "$TITLE" \
    '{
       status:$status,
       reason:$reason,
       title:$title
     }' > "$META"

  echo "ℹ️ TGPT niet gevonden; council gaat verder zonder TGPT."
  exit 0
fi

PROMPT="
You are the optional local AI worker inside Mikis13 AI City.

Task:
$TITLE

Goal:
$GOAL

Do NOT execute commands.
Do NOT request or reveal secrets.

Return only:
CLAIM
EVIDENCE_TO_CHECK
RISK
ALTERNATIVE
RECOMMENDATION
SMALLEST_NEXT_ACTION
TEST
ROLLBACK

Prefer improvement of existing repositories.
"

timeout 120 \
  tgpt "$PROMPT" \
  > "$OUT" 2>&1 || {

    jq -n \
      --arg status "FAILED" \
      --arg title "$TITLE" \
      '{
        status:$status,
        title:$title
      }' > "$META"

    exit 0
  }

jq -n \
  --arg status "SUCCESS" \
  --arg title "$TITLE" \
  --arg output "$OUT" \
  '{
    status:$status,
    title:$title,
    output_file:$output
  }' > "$META"

echo "✅ TGPT analyse gereed"
