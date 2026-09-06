#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"
BACKUP_DIR="$HOME/.mikis13-ai-city-backups"

cd "$ROOT"

LATEST="$(ls -1t "$BACKUP_DIR"/worktree-*.tar 2>/dev/null | head -n1 || true)"

if [ -z "$LATEST" ]; then
  echo "❌ Geen backups gevonden in $BACKUP_DIR"
  exit 1
fi

echo "Herstellen uit: $LATEST"
echo "Bestaande bestanden worden NIET overschreven."

tar -xf "$LATEST" -C "$ROOT" --keep-old-files 2>/dev/null || true

echo "✅ Restore klaar"
git status --short
