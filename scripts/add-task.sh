#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"

TITLE="${*:-}"

if [ -z "$TITLE" ]; then
  echo "Gebruik:"
  echo 'mikis-city-task "jouw opdracht"'
  exit 1
fi

mkdir -p "$ROOT/state/inbox"

python - "$TITLE" <<'PY'
from pathlib import Path
from datetime import datetime, timezone
import json
import sys

ROOT = (
    Path.home()
    / "mikis13-ai-city"
)

PATH_OUT = (
    ROOT
    / "state"
    / "inbox"
    / "tasks.jsonl"
)

entry = {
    "created":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "title":
        sys.argv[1],

    "priority":
        70,

    "status":
        "NEW"
}

with PATH_OUT.open(
    "a",
    encoding="utf-8"
) as fh:

    fh.write(
        json.dumps(
            entry,
            ensure_ascii=False
        )
        + "\n"
    )

print(
    "✅ Taak toegevoegd:",
    entry["title"]
)
PY
