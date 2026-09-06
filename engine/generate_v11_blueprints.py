#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

definitions = [
    ("Recovery Verification Contract", "recovery"),
    ("Before After Evidence Snapshot", "recovery"),
    ("Original Failure Replay", "recovery"),
    ("False Recovery Detector", "recovery"),
    ("Recovery Proof Bundle", "recovery"),

    ("Canonical Job State Machine", "jobs"),
    ("Atomic Job Claim", "jobs"),
    ("Job Lease Expiration", "jobs"),
    ("Job Deduplication Fingerprint", "jobs"),
    ("Job Priority Recalibration", "jobs"),

    ("Bounded Execution Planner", "execution"),
    ("Mutation Authorization Gate", "execution"),
    ("Command Allowlist Runner", "execution"),
    ("Execution Checkpoint Manager", "execution"),
    ("Execution Result Normalizer", "execution"),

    ("Failure Signature Canonicalizer", "regression"),
    ("Regression Requirement Register", "regression"),
    ("Regression Test Linker", "regression"),
    ("Recurring Failure Escalator", "regression"),
    ("Successful Fix Retrieval", "regression"),

    ("Worker Outcome Ledger", "workers"),
    ("Worker Accuracy Score", "workers"),
    ("Worker Domain Competence", "workers"),
    ("Worker Cooldown Engine", "workers"),
    ("Worker Promotion Gate", "workers"),

    ("Blueprint Maturity State Machine", "maturity"),
    ("Prototype Promotion Gate", "maturity"),
    ("Verified Capability Gate", "maturity"),
    ("Deployment Verification Gate", "maturity"),
    ("Proven Capability Evidence", "maturity"),

    ("Repository Dependency Graph", "dependencies"),
    ("Change Impact Propagation", "dependencies"),
    ("Dependency Critical Path", "dependencies"),
    ("Single Point Failure Finder", "dependencies"),
    ("Dependency Drift Monitor", "dependencies"),

    ("Prompt Benchmark Corpus", "prompt"),
    ("Prompt Behavioral Contract", "prompt"),
    ("Prompt Candidate Comparator", "prompt"),
    ("Prompt Regression Rejector", "prompt"),
    ("Prompt Improvement Evidence", "prompt"),

    ("Existing Solution Scout", "research"),
    ("Open Source Scout", "research"),
    ("License Provenance Gate", "research"),
    ("Solution Comparison Matrix", "research"),
    ("Research To Job Converter", "research"),

    ("Control Tower Status Model", "control"),
    ("Control Tower Health Summary", "control"),
    ("Control Tower Active Job View", "control"),
    ("Control Tower Recovery View", "control"),
    ("Control Tower Owner Controls", "control")
]

assert len(definitions) == 50

blueprints = []

for ident, (name, domain) in enumerate(
    definitions,
    start=301
):
    blueprints.append({
        "id": ident,
        "name": name,
        "domain": domain,
        "status": "PLANNED",

        "goal":
            "Increase verified capability while preserving "
            "evidence, rollback, safety and owner control.",

        "expected_impact": 95,
        "complexity": 30,
        "maintenance_cost": 20,
        "risk": 20,

        "existing_repo_required_first": True,
        "new_repository_required": False,

        "execution_authorized": False,
        "human_override_required": True,

        "source_version": "V11"
    })

assert [b["id"] for b in blueprints] == list(
    range(301, 351)
)

out = {
    "version": 11,
    "range": "301-350",
    "count": 50,
    "blueprints": blueprints
}

(ROOT / "config" / "automation-blueprints-301-350-v11.json").write_text(
    json.dumps(out, indent=2) + "\n",
    encoding="utf-8"
)

print("✅ 50 V11 blueprints geschreven")
