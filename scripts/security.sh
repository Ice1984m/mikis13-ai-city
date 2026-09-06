#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"

cd "$ROOT"

echo "🔐 Security gate"

python -m py_compile \
  engine/*.py

python -m json.tool \
  config/organization.json \
  >/dev/null

python -m json.tool \
  config/providers.json \
  >/dev/null

echo "✅ Syntax / JSON PASS"

TMP_BASE="${TMPDIR:-$PREFIX/tmp}"

mkdir -p "$TMP_BASE"

HITS="$(
  mktemp \
    "$TMP_BASE/mikis-city-secret-hits.XXXXXX"
)"

trap 'rm -f "$HITS"' EXIT

PATTERN='(BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16})'

if git grep -En "$PATTERN" -- \
  ':!docs/' \
  ':!state/' \
  ':!reports/' \
  ':!logs/' \
  >"$HITS" 2>/dev/null
then

  echo "❌ Mogelijk geheim gevonden"

  sed -E \
    's/[A-Za-z0-9_-]{12,}/[REDACTED]/g' \
    "$HITS"

  exit 1

fi

echo "✅ Secret scan PASS"
