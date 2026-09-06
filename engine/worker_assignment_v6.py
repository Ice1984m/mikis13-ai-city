#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path.home() / "mikis13-ai-city"
STATE = ROOT / "state"

ACTIVE = STATE / "jobs/active.json"
OUT = STATE / "workers/assignment.json"

ROLE_MAP = {
    "security": ["Security Guardian", "Testing Engineer", "Reliability Engineer"],
    "tests": ["Testing Engineer", "System Architect", "Reliability Engineer"],
    "healthcheck": ["Reliability Engineer", "Hosting Worker", "Testing Engineer"],
    "evidence": ["Research Scout", "System Architect", "Testing Engineer"],
    "learning": ["Failure Analyst", "Learning Officer", "Testing Engineer"],
    "local": ["Local AI Worker", "Testing Engineer", "Security Guardian"],
    "approval": ["Reality Juror", "Business Analyst", "Security Guardian"],
    "git": ["GitHub Coordinator", "Testing Engineer", "Security Guardian"],
    "lock": ["Orion", "GitHub Coordinator", "Reliability Engineer"],
    "budget": ["Orion", "Reliability Engineer", "Reality Juror"],
    "rollback": ["Release Planner", "Reliability Engineer", "Testing Engineer"]
}

def main():
    try:
        job = json.loads(ACTIVE.read_text())
    except Exception:
        print(json.dumps({"workers": [], "reason": "no active job"}))
        return

    workers = ROLE_MAP.get(
        job.get("gate"),
        ["System Architect", "Testing Engineer", "Security Guardian"]
    )

    workers = workers[:4]

    assignment = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "job_id": job["id"],
        "title": job["title"],
        "workers": workers,
        "contract": [
            "claim",
            "evidence",
            "missing_evidence",
            "risk",
            "alternative",
            "recommendation",
            "confidence",
            "expected_impact",
            "smallest_next_action",
            "success_test",
            "rollback"
        ]
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(assignment, indent=2) + "\n")

    print(json.dumps(assignment, indent=2))

if __name__ == "__main__":
    main()
