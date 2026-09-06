#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path.home() / "mikis13-ai-city"

STATE = (
    ROOT
    / "state"
    / "meta-evolution"
)

catalog = json.loads(
    (
        ROOT
        / "config"
        / "automation-blueprints-101-200-v9.json"
    ).read_text()
)

domains = {}

for item in catalog["blueprints"]:

    domain = item["domain"]

    d = domains.setdefault(
        domain,
        {
            "planned": 0,
            "done": 0,
            "proven": 0
        }
    )

    d["planned"] += 1

    if item["status"] == "DONE":
        d["done"] += 1

result = {
    "generated":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "domains":
        domains,

    "warning":
        (
            "PLANNED capabilities are not PROVEN capabilities."
        )
}

STATE.mkdir(
    parents=True,
    exist_ok=True
)

(
    STATE
    / "capability-gap.json"
).write_text(
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
