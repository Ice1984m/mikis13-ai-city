#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"
BACKUP_DIR="$HOME/.mikis13-ai-city-backups"

cd "$ROOT"

mkdir -p "$BACKUP_DIR"
BACKUP="$BACKUP_DIR/worktree-$(date -u +%Y%m%d-%H%M%S).tar"
tar --exclude=.git -cf "$BACKUP" .
echo "✅ Backup: $BACKUP"

git reset >/dev/null 2>&1 || true
git clean -fd -e state -e logs -e reports -e .venv -e __pycache__ || true

echo "✅ Worktree vrijgemaakt — checkout kan nu weer"
git status --short
