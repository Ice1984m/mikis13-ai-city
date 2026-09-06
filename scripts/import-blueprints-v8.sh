#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/mikis13-ai-city"

python - <<'PY'
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path.home() / "mikis13-ai-city"

source = json.loads(
    (
        ROOT
        / "config"
        / "automation-blueprints-90-v8.json"
    ).read_text()
)

queue_path = (
    ROOT
    / "state"
    / "jobs"
    / "queue.jsonl"
)

queue_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

existing = set()

if queue_path.exists():

    for line in queue_path.read_text().splitlines():

        try:
            job = json.loads(line)

            bp = job.get(
                "blueprint_id"
            )

            if bp is not None:
                existing.add(
                    int(bp)
                )

        except Exception:
            pass

added = 0

with queue_path.open(
    "a",
    encoding="utf-8"
) as f:

    for item in source["blueprints"]:

        if item["id"] in existing:
            continue

        raw = (
            str(item["id"])
            + ":"
            + item["name"]
        )

        job_id = hashlib.sha256(
            raw.encode()
        ).hexdigest()[:16]

        job = {
            "id":
                job_id,

            "blueprint_id":
                item["id"],

            "title":
                item["name"],

            "owner":
                item["owner"],

            "goal":
                item["goal"],

            "gate":
                item["gate"],

            "priority":
                int(
                    item["expected_impact"]
                    - item["complexity"] * 0.2
                ),

            "status":
                "NEW",

            "created":
                datetime.now(
                    timezone.utc
                ).isoformat()
        }

        f.write(
            json.dumps(
                job,
                ensure_ascii=False
            )
            + "\n"
        )

        added += 1

print(
    f"✅ {added} nieuwe V8 jobs geïmporteerd"
)
PY
