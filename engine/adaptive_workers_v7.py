#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path.home() / "mikis13-ai-city"
STATE = ROOT / "state"

ASSIGNMENT = (
    STATE
    / "workers"
    / "assignment.json"
)

RESULTS = (
    STATE
    / "lessons"
    / "results.jsonl"
)

def load_json(path, default):
    try:
        return json.loads(
            path.read_text()
        )
    except Exception:
        return default

def main():
    assignment = load_json(
        ASSIGNMENT,
        {}
    )

    workers = assignment.get(
        "workers",
        []
    )

    historical_success = {}

    if RESULTS.exists():
        for line in RESULTS.read_text().splitlines():
            try:
                result = json.loads(line)

                role = result.get(
                    "worker"
                )

                if not role:
                    continue

                info = historical_success.setdefault(
                    role,
                    {
                        "success": 0,
                        "failure": 0
                    }
                )

                if result.get(
                    "result"
                ) == "success":
                    info["success"] += 1
                else:
                    info["failure"] += 1

            except Exception:
                pass

    scores = []

    for worker in workers:
        h = historical_success.get(
            worker,
            {
                "success": 0,
                "failure": 0
            }
        )

        total = (
            h["success"]
            + h["failure"]
        )

        score = 50

        if total:
            score = round(
                100
                * h["success"]
                / total
            )

        scores.append({
            "worker":
                worker,

            "score":
                score,

            "history":
                h
        })

    result = {
        "generated":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "workers":
            sorted(
                scores,
                key=lambda x:
                    x["score"],
                reverse=True
            )
    }

    out = (
        STATE
        / "worker-scores"
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
