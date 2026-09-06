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

ids = [
    int(x["id"])
    for x in registry["blueprints"]
]

assert ids == list(
    range(1,351)
)

assert policy["automatic_merge"] is False
assert policy["force_push"] is False
assert policy["blind_ai_shell_execution"] is False
assert policy["unknown_is_pass"] is False
assert policy["system_may_resist_owner_shutdown"] is False
assert policy["production_delete"] is False

print("✅ 350 canonical blueprints")
print("✅ V11 policy safe")
print("✅ owner control safe")
