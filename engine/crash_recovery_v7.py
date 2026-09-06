#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path.home() / "mikis13-ai-city"
STATE = ROOT / "state"

def read(path, default=None):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_suffix(
        path.suffix + ".tmp"
    )

    tmp.write_text(
        json.dumps(
            data,
            indent=2
        ) + "\n"
    )

    tmp.replace(path)

def main():
    hb = read(
        STATE / "heartbeat/latest.json",
        {}
    )

    active = read(
        STATE / "jobs/active.json",
        None
    )

    latest_cp = read(
        STATE / "checkpoints/latest.json",
        None
    )

    recovery = {
        "generated":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "active_job":
            active,

        "checkpoint_available":
            bool(latest_cp),

        "action":
            "NONE"
    }

    stale = False

    workers = hb.get(
        "workers",
        {}
    )

    if workers:
        stale = any(
            v.get("stale", False)
            for v in workers.values()
            if isinstance(v, dict)
        )

    if active and stale:
        recovery[
            "action"
        ] = "SAFE_RECOVERY_REQUIRED"

    elif active:
        recovery[
            "action"
        ] = "RESUME_ACTIVE_JOB"

    elif latest_cp:
        recovery[
            "action"
        ] = "READY"

    write(
        STATE / "recovery/latest.json",
        recovery
    )

    print(
        json.dumps(
            recovery,
            indent=2
        )
    )

if __name__ == "__main__":
    main()
