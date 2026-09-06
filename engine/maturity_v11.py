#!/usr/bin/env python3

from pathlib import Path
import json

from state_v11 import (
    ROOT,
    STATE,
    atomic_json,
    read_json,
    now
)

registry = json.loads(
    (
        ROOT
        / "config"
        / "blueprints.json"
    ).read_text()
)

dbfile = (
    STATE
    / "maturity"
    / "blueprints.json"
)

db = read_json(
    dbfile,
    {
        "version": 11,
        "blueprints": {}
    }
)

valid = {
    "IDEA",
    "PLANNED",
    "PROTOTYPE",
    "TESTED",
    "VERIFIED",
    "DEPLOYED",
    "PROVEN"
}

for b in registry["blueprints"]:

    state = b.get(
        "status",
        "PLANNED"
    )

    if state not in valid:
        state = "PLANNED"

    db["blueprints"].setdefault(
        str(b["id"]),
        {
            "id": b["id"],
            "name": b["name"],
            "state": state,
            "updated_at": now()
        }
    )

atomic_json(
    dbfile,
    db
)

counts = {}

for row in db["blueprints"].values():

    counts[row["state"]] = (
        counts.get(
            row["state"],
            0
        )
        + 1
    )

print(
    json.dumps(
        counts,
        indent=2
    )
)
