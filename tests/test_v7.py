#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path.home() / "mikis13-ai-city"

policy = json.loads(
    (
        ROOT
        / "config/v7-resilience-policy.json"
    ).read_text()
)

assert policy["maximum_active_jobs"] == 1
assert policy["require_atomic_state"] is True
assert policy["require_checkpoint_before_execution"] is True
assert policy["require_idempotency_key"] is True
assert policy["manual_kill_switch_required"] is True
assert policy["automatic_self_preservation_against_owner"] is False
assert policy["automatic_merge"] is False

assert "disable_owner_control" in policy["blocked"]
assert "resist_authorized_shutdown" in policy["blocked"]

print("✅ V7 resilience policy PASS")
