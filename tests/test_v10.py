#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

blueprints = json.loads(
    (ROOT/"config"/"blueprints.json").read_text()
)

workers = json.loads(
    (ROOT/"config"/"workers-200-v10.json").read_text()
)

scouts = json.loads(
    (ROOT/"config"/"scouts-100-v10.json").read_text()
)

jobs = json.loads(
    (ROOT/"config"/"priority-jobs-50-v10.json").read_text()
)

policy = json.loads(
    (ROOT/"config"/"v10-policy.json").read_text()
)

ids = [
    int(x["id"])
    for x in blueprints["blueprints"]
]

assert ids == list(range(1,301))
assert len(ids) == 300
assert len(set(ids)) == 300

assert len(workers["workers"]) == 200
assert len(scouts["scouts"]) == 100
assert len(jobs["jobs"]) == 50

assert policy["maximum_active_execution_jobs"] == 1
assert policy["automatic_merge"] is False
assert policy["direct_main_changes"] is False
assert policy["owner_kill_switch_required"] is True

assert all(
    not x["merge_permission"]
    for x in workers["workers"]
)

assert all(
    x["mode"] == "READ_ONLY"
    for x in scouts["scouts"]
)

print("✅ AI City V10 PASS")
print("✅ 300 canonical blueprints")
print("✅ 200 engineering workers")
print("✅ 100 scouts")
print("✅ 50 priority jobs")
