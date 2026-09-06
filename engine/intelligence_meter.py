#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = (
    Path.home()
    / "mikis13-ai-city"
)

STATE = ROOT / "state"

def read_json(path, fallback):
    try:
        return json.loads(
            path.read_text()
        )
    except Exception:
        return fallback

learning = read_json(
    STATE / "learning/patterns.json",
    {
        "cycles": 0,
        "decisions": {}
    }
)

repair = read_json(
    STATE / "repair/latest.json",
    {
        "health_score": 0
    }
)

ledger = (
    STATE
    / "city"
    / "ledger.jsonl"
)

cycles = 0

if ledger.exists():

    cycles = len([
        x
        for x in ledger.read_text().splitlines()
        if x.strip()
    ])

health = int(
    repair.get(
        "health_score",
        0
    )
)

experience = min(
    25,
    cycles * 2
)

learning_score = min(
    25,
    int(
        learning.get(
            "cycles",
            0
        )
        * 2
    )
)

reliability = int(
    health * 0.35
)

score = min(
    100,
    experience
    + learning_score
    + reliability
)

if score < 25:
    level = "FOUNDATION"
elif score < 45:
    level = "COORDINATED"
elif score < 65:
    level = "RELIABLE"
elif score < 80:
    level = "LEARNING"
elif score < 95:
    level = "ADAPTIVE"
else:
    level = "OPTIMIZED"

result = {
    "generated":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "city_cycles":
        cycles,

    "repair_health":
        health,

    "learning_cycles":
        learning.get(
            "cycles",
            0
        ),

    "operational_intelligence_score":
        score,

    "level":
        level,

    "meaning":
        (
            "Operational intelligence measures "
            "learning, reliability and accumulated "
            "tested experience. It is not model retraining."
        )
}

out = (
    STATE
    / "intelligence"
    / "latest.json"
)

out.parent.mkdir(
    parents=True,
    exist_ok=True
)

out.write_text(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )
    + "\n"
)

print(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )
)
