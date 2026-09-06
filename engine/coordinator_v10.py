#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "v10"
CFG = ROOT / "config"

STATE.mkdir(parents=True, exist_ok=True)
(STATE / "jobs").mkdir(exist_ok=True)
(STATE / "results").mkdir(exist_ok=True)

if (STATE / "OWNER_STOP").exists():
    print("OWNER_STOP")
    raise SystemExit(0)

registry = json.loads(
    (CFG / "blueprints.json").read_text()
)

jobs = json.loads(
    (CFG / "priority-jobs-50-v10.json").read_text()
)

workers = json.loads(
    (CFG / "workers-200-v10.json").read_text()
)

scouts = json.loads(
    (CFG / "scouts-100-v10.json").read_text()
)

scout_file = STATE / "scouts" / "latest.json"

scout_data = {}

if scout_file.exists():
    scout_data = json.loads(
        scout_file.read_text()
    )

signals = scout_data.get("signals", [])

if signals:
    selected_job = jobs["jobs"][2]
else:
    selected_job = jobs["jobs"][12]

preferred_families = [
    "reliability",
    "testing",
    "critic",
    "github"
]

selected_workers = []

for family in preferred_families:
    for w in workers["workers"]:
        if w["family"] == family:
            selected_workers.append(w)
            break

selected_scouts = scouts["scouts"][:8]

decision = {
    "generated": datetime.now(timezone.utc).isoformat(),
    "mode": "PLAN_ONLY",
    "canonical_blueprints": len(registry["blueprints"]),
    "github_signal_count": len(signals),
    "selected_job": selected_job,
    "workers": [
        w["worker_id"]
        for w in selected_workers
    ],
    "scouts": [
        s["scout_id"]
        for s in selected_scouts
    ],
    "mutation_authorized": False,
    "reason":
        "V10 planning cycle gathers evidence first; mutation requires a separate gated execution stage."
}

(STATE / "decision.json").write_text(
    json.dumps(decision, indent=2) + "\n"
)

print(json.dumps(decision, indent=2))
