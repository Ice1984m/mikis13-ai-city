#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"

cd "$ROOT"

BRANCH="$(git branch --show-current)"

case "$BRANCH" in
  bot/*) ;;
  *)
    echo "❌ Alleen bot-branch toegestaan"
    exit 2
    ;;
esac

TMP_BASE="${TMPDIR:-$PREFIX/tmp}"

WORKTREE="$TMP_BASE/mikis13-ai-city-worktree"

rm -rf "$WORKTREE"

git worktree add \
  --detach \
  "$WORKTREE" \
  HEAD

cleanup() {
  git worktree remove \
    --force \
    "$WORKTREE" \
    >/dev/null 2>&1 || true
}

trap cleanup EXIT

cd "$WORKTREE"

python -m py_compile engine/*.py

for f in tests/test_*.py; do
  [ -f "$f" ] || continue
  python "$f"
done

bash -n scripts/*.sh

echo "✅ Temporary worktree validation PASS"
