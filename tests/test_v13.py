#!/usr/bin/env python3
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))

import global_worker_v13 as worker

policy = json.loads((ROOT / "config" / "v13-policy.json").read_text())
nodes = json.loads((ROOT / "config" / "nodes-v13.json").read_text())
regions = json.loads((ROOT / "config" / "regions-v13.json").read_text())

assert policy["mutation_enabled"] is False
assert policy["automatic_merge"] is False
assert policy["direct_main_write"] is False
assert policy["force_push"] is False
assert policy["paid_execution"] is False
assert policy["unknown_is_pass"] is False
assert all(n["mutation"] is False for n in nodes["nodes"])
assert {r["id"] for r in regions["regions"]} == {"EU", "US", "ASIA"}
assert all(r["configured"] is False for r in regions["regions"])

worker.validate_target("json-validate", "config/v13-policy.json")
worker.validate_target("shell-syntax", "scripts/v13-status.sh")
worker.validate_target("http-health", "https://mikis13.nl")

try:
    worker.validate_target("http-health", "https://example.com")
except SystemExit:
    pass
else:
    raise AssertionError("non-allowlisted HTTP host was accepted")

try:
    worker.validate_target("json-validate", "/etc/passwd")
except SystemExit:
    pass
else:
    raise AssertionError("path escape was accepted")

try:
    worker.validate_target("rm", ".")
except SystemExit:
    pass
else:
    raise AssertionError("unsafe capability was accepted")

print("V13 policy PASS")
print("V13 target confinement PASS")
print("V13 HTTP allowlist PASS")
print("V13 mutation disabled PASS")
print("V13 geographic adapters explicitly unconfigured PASS")
