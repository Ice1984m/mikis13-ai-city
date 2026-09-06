#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path.home() / "mikis13-ai-city"

path = (
    ROOT
    / "config"
    / "automation-blueprints-101-200-v9.json"
)

data = json.loads(
    path.read_text()
)

items = data["blueprints"]

assert len(items) == 100

ids = [
    item["id"]
    for item in items
]

assert ids == list(
    range(
        101,
        201
    )
)

assert len(set(ids)) == 100

assert all(
    item["new_repository_required"]
    is False
    for item in items
)

assert all(
    item["execution_authorized"]
    is False
    for item in items
)

assert all(
    item["human_override_required"]
    is True
    for item in items
)

domains = {
    item["domain"]
    for item in items
}

expected_domains = {
    "causal_reasoning",
    "simulation",
    "code_intelligence",
    "testing",
    "prompt_engineering",
    "knowledge",
    "supply_chain",
    "android",
    "operations",
    "meta"
}

assert domains == expected_domains

print(
    "✅ V9 blueprints 101-200 PASS"
)
