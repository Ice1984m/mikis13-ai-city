#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

scopes = [
    "github_actions",
    "open_pull_requests",
    "dependency_updates",
    "repository_structure",
    "duplicate_logic",
    "documentation_drift",
    "security_signals",
    "release_health",
    "website_health",
    "architecture_complexity"
]

scouts = []

for scope_index, scope in enumerate(scopes):
    for variant in range(1, 11):

        sid = scope_index * 10 + variant

        scouts.append({
            "scout_id": f"S{sid:03d}",
            "scope": scope,
            "variant": variant,
            "mode": "READ_ONLY",
            "enabled": True,
            "may_execute_shell_from_ai": False,
            "may_merge": False,
            "may_write_main": False,
            "mission":
                "Inspect evidence, find reusable solutions, identify stronger architecture and report bounded recommendations.",
            "required_output": [
                "observation",
                "source",
                "evidence_strength",
                "problem",
                "reuse_candidate",
                "possible_solution",
                "risk",
                "smallest_next_action"
            ]
        })

assert len(scouts) == 100

(ROOT / "config" / "scouts-100-v10.json").write_text(
    json.dumps({
        "version": 10,
        "count": 100,
        "scouts": scouts
    }, indent=2) + "\n",
    encoding="utf-8"
)

print("✅ Scout profiles:", len(scouts))
