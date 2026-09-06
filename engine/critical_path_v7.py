#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path.home() / "mikis13-ai-city"
STATE = ROOT / "state"

def load_queue():
    path = (
        STATE
        / "jobs"
        / "queue.jsonl"
    )

    jobs = []

    if path.exists():
        for line in path.read_text().splitlines():
            try:
                jobs.append(
                    json.loads(line)
                )
            except Exception:
                pass

    return jobs

def score(job):
    priority = int(
        job.get(
            "priority",
            0
        )
    )

    gate = job.get(
        "gate",
        ""
    )

    multiplier = {
        "security": 1.35,
        "healthcheck": 1.30,
        "tests": 1.25,
        "lock": 1.20,
        "rollback": 1.15,
        "evidence": 1.00,
        "learning": 0.90,
        "approval": 0.75
    }.get(gate, 1.0)

    return round(
        priority
        * multiplier,
        2
    )

def main():
    jobs = [
        j
        for j in load_queue()
        if j.get("status")
        in ("NEW", "ACTIVE")
    ]

    ranked = sorted(
        (
            {
                **j,
                "critical_score":
                    score(j)
            }
            for j in jobs
        ),
        key=lambda x:
            x["critical_score"],
        reverse=True
    )

    result = {
        "generated":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "critical_job":
            ranked[0]
            if ranked
            else None,

        "top5":
            ranked[:5]
    }

    out = (
        STATE
        / "critical-path"
        / "latest.json"
    )

    out.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    out.write_text(
        json.dumps(
            result,
            indent=2
        ) + "\n"
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )

if __name__ == "__main__":
    main()
