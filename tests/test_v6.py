#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path.home() / "mikis13-ai-city"

policy = json.loads(
    (ROOT / "config/v6-policy.json").read_text()
)

bp = json.loads(
    (ROOT / "config/automation-blueprints-50.json").read_text()
)

assert policy["maximum_active_jobs"] == 1
assert policy["maximum_debate_rounds"] <= 2
assert policy["external_paid_calls"] == 0
assert len(bp["blueprints"]) == 50
assert len({x["id"] for x in bp["blueprints"]}) == 50
assert all(
    x["new_repository_required"] is False
    for x in bp["blueprints"]
)

print("✅ AI City V6 policy + 50 blueprints PASS")
