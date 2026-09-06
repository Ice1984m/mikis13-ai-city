#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path.home() / "mikis13-ai-city"

data = json.loads(
    (
        ROOT
        / "config"
        / "automation-blueprints-90-v8.json"
    ).read_text()
)

items = data["blueprints"]

assert len(items) == 90

ids = [x["id"] for x in items]

assert ids == list(range(11, 101))

assert len(set(ids)) == 90

assert all(
    x["new_repository_required"] is False
    for x in items
)

assert all(
    0 <= x["expected_impact"] <= 100
    for x in items
)

assert all(
    0 <= x["complexity"] <= 100
    for x in items
)

assert all(
    0 <= x["maintenance_cost"] <= 100
    for x in items
)

print("✅ 90 V8 blueprints PASS")
