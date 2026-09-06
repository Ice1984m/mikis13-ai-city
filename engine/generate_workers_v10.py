#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

families = [
    ("reliability", ["recovery","health","incident","checkpoint","rollback"]),
    ("testing", ["regression","contract","negative","mutation","coverage"]),
    ("security", ["secret","permissions","supply-chain","workflow","integrity"]),
    ("github", ["actions","pull-request","dependency","branch","release"]),
    ("architecture", ["dependencies","complexity","drift","reuse","sprawl"]),
    ("termux", ["android","scheduler","storage","network","battery"]),
    ("documentation", ["readme","runbook","adr","drift","examples"]),
    ("prompt", ["lint","benchmark","evidence","uncertainty","compression"]),
    ("knowledge", ["provenance","memory","assumptions","failures","decisions"]),
    ("simulation", ["workflow","deployment","network","state","recovery"]),
    ("performance", ["runtime","memory","cpu","network","api-budget"]),
    ("product", ["value","mvp","feedback","claims","roadmap"]),
    ("observability", ["timeline","trace","signals","trend","correlation"]),
    ("release", ["candidate","canary","compatibility","artifact","verification"]),
    ("governance", ["policy","owner-control","audit","scope","risk"]),
    ("repair", ["diagnosis","minimal-fix","validation","recurrence","rollback"]),
    ("code-intelligence", ["semantic-map","functions","configs","dead-code","duplicates"]),
    ("coordination", ["routing","worker-pair","handoff","deadlock","wip"]),
    ("research", ["alternatives","upstream","standards","patterns","comparison"]),
    ("critic", ["counterexample","assumptions","complexity","utility","evidence"])
]

workers = []
wid = 1

for family, specialties in families:
    for variant in range(1, 11):
        specialty = specialties[(variant - 1) % len(specialties)]

        workers.append({
            "worker_id": f"W{wid:03d}",
            "family": family,
            "specialty": specialty,
            "variant": variant,
            "enabled": True,
            "autonomous_write": False,
            "direct_main_write": False,
            "merge_permission": False,
            "shell_from_ai_permission": False,
            "max_jobs_per_cycle": 1,
            "required_output": [
                "claim",
                "evidence",
                "unknowns",
                "recommendation",
                "smallest_action",
                "success_condition",
                "rollback"
            ]
        })

        wid += 1

assert len(workers) == 200

(ROOT / "config" / "workers-200-v10.json").write_text(
    json.dumps({
        "version": 10,
        "count": len(workers),
        "workers": workers
    }, indent=2) + "\n",
    encoding="utf-8"
)

print("✅ Engineering worker profiles:", len(workers))
