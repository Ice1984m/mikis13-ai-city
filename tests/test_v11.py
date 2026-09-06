#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

policy = json.loads(
    (
        ROOT
        / "config"
        / "v11-policy.json"
    ).read_text()
)

registry = json.loads(
    (
        ROOT
        / "config"
        / "blueprints.json"
    ).read_text()
)

v11 = json.loads(
    (
        ROOT
        / "config"
        / "automation-blueprints-301-350-v11.json"
    ).read_text()
)

ids = [
    int(x["id"])
    for x in registry["blueprints"]
]

assert ids == list(
    range(1,351)
)

assert len(ids) == 350

assert len(
    set(ids)
) == 350

assert len(
    v11["blueprints"]
) == 50

assert [
    x["id"]
    for x in v11["blueprints"]
] == list(
    range(301,351)
)

assert (
    policy[
        "maximum_active_mutation_jobs"
    ]
    == 1
)

assert (
    policy[
        "automatic_merge"
    ]
    is False
)

assert (
    policy[
        "direct_main_write"
    ]
    is False
)

assert (
    policy[
        "blind_ai_shell_execution"
    ]
    is False
)

assert (
    policy[
        "owner_kill_switch_required"
    ]
    is True
)

print("✅ V11 registry PASS")
print("✅ 350 unique blueprints")
print("✅ 50 execution blueprints")
print("✅ owner control PASS")
print("✅ no blind merge PASS")
