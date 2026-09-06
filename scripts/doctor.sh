#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"
cd "$ROOT"

echo; echo "===== AI CITY DOCTOR ====="
python engine/repair_bot.py

echo; echo "===== INTELLIGENCE ====="
python engine/intelligence_meter.py

echo; echo "===== GIT ====="
git status --short

echo; echo "===== BRANCH ====="
git rev-parse --abbrev-ref HEAD

echo; echo "===== REMOTE ====="
git remote -v

echo; echo "===== BACKUPS ====="
ls -1t "$HOME/.mikis13-ai-city-backups"/worktree-*.tar 2>/dev/null \
  | head -n5 || echo "(geen backups)"
