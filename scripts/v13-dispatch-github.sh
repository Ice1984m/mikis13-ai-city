#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
REPO="Ice1984m/mikis13-ai-city"
NODE="${1:-GH-RUNNER-A}"

CLAIM="$(python engine/federation_v13.py claim --node "$NODE")"
STATUS="$(jq -r '.status' <<<"$CLAIM")"
if [ "$STATUS" != "CLAIMED" ]; then
  echo "$CLAIM"
  exit 0
fi

JOB_ID="$(jq -r '.job.job_id' <<<"$CLAIM")"
ACTION="$(jq -r '.job.action' <<<"$CLAIM")"
TARGET="$(jq -r '.job.target' <<<"$CLAIM")"
EXPECTED="$(jq -r '.job.expected' <<<"$CLAIM")"
TOKEN="$(jq -r '.job.lease.token' <<<"$CLAIM")"
BRANCH="$(git branch --show-current)"

echo "Dispatching $JOB_ID to $NODE via GitHub Actions..."

if ! gh workflow run global-worker-v13.yml \
  --repo "$REPO" \
  --ref "$BRANCH" \
  -f node="$NODE" \
  -f job_id="$JOB_ID" \
  -f action="$ACTION" \
  -f target="$TARGET" \
  -f expected="$EXPECTED"; then
  echo "Workflow dispatch failed. The workflow must first exist on the repository default branch."
  echo "The claimed lease will expire automatically and the job will become retryable."
  exit 2
fi

RUN_ID=""
for _ in $(seq 1 30); do
  RUN_ID="$(gh run list --repo "$REPO" --workflow global-worker-v13.yml --branch "$BRANCH" --limit 20 \
    --json databaseId,displayTitle \
    --jq ".[] | select(.displayTitle == \"V13 $JOB_ID\") | .databaseId" | head -n1)"
  [ -n "$RUN_ID" ] && break
  sleep 2
done

[ -n "$RUN_ID" ] || { echo "Could not resolve workflow run for $JOB_ID"; exit 2; }

gh run watch "$RUN_ID" --repo "$REPO" --exit-status || true
LOG="$(gh run view "$RUN_ID" --repo "$REPO" --log)"
RESULT_B64="$(printf '%s\n' "$LOG" | sed -n 's/^.*MIKIS_RESULT_B64=//p' | tail -n1)"

if [ -z "$RESULT_B64" ]; then
  echo "No result payload found; lease will expire for safe retry."
  exit 2
fi

python engine/federation_v13.py complete \
  --job "$JOB_ID" \
  --node "$NODE" \
  --lease-token "$TOKEN" \
  --result-b64 "$RESULT_B64"
