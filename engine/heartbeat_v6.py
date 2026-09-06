#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import json
import os

ROOT = Path.home() / "mikis13-ai-city"

files = {
    "decision": ROOT / "state/decisions/latest.json",
    "active_job": ROOT / "state/jobs/active.json",
    "workers": ROOT / "state/workers/assignment.json",
    "tgpt": ROOT / "state/tgpt/latest.json",
    "report": ROOT / "reports/city-latest.md"
}

result = {
    "generated": datetime.now(timezone.utc).isoformat(),
    "workers": {}
}

now = datetime.now(timezone.utc).timestamp()

for name, path in files.items():
    if path.exists():
        age = int(now - path.stat().st_mtime)
        result["workers"][name] = {
            "exists": True,
            "age_seconds": age,
            "stale": age > 8 * 3600
        }
    else:
        result["workers"][name] = {
            "exists": False,
            "stale": True
        }

out = ROOT / "state/heartbeat/latest.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, indent=2) + "\n")

print(json.dumps(result, indent=2))
