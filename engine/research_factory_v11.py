#!/usr/bin/env python3

import json
import subprocess

from state_v11 import (
    STATE,
    atomic_json,
    utcnow
)

def run(cmd):

    p = subprocess.run(
        cmd,
        text=True,
        capture_output=True
    )

    return {
        "returncode": p.returncode,
        "stdout": p.stdout[-30000:],
        "stderr": p.stderr[-5000:]
    }

repos = run([
    "gh",
    "repo",
    "list",
    "Ice1984m",
    "--limit",
    "100",
    "--json",
    "name,nameWithOwner,description,pushedAt,isArchived"
])

try:
    repository_rows = json.loads(
        repos["stdout"]
    )
except Exception:
    repository_rows = []

signals = []

for repo in repository_rows:

    if repo.get("isArchived"):
        continue

    full = repo["nameWithOwner"]

    runs = run([
        "gh",
        "run",
        "list",
        "--repo",
        full,
        "--limit",
        "3",
        "--json",
        "databaseId,name,status,conclusion,createdAt"
    ])

    prs = run([
        "gh",
        "pr",
        "list",
        "--repo",
        full,
        "--state",
        "open",
        "--limit",
        "10",
        "--json",
        "number,title,isDraft,mergeStateStatus,updatedAt"
    ])

    try:
        run_rows = json.loads(
            runs["stdout"] or "[]"
        )
    except Exception:
        run_rows = []

    try:
        pr_rows = json.loads(
            prs["stdout"] or "[]"
        )
    except Exception:
        pr_rows = []

    failures = [
        r
        for r in run_rows
        if r.get("conclusion") in {
            "failure",
            "cancelled",
            "timed_out",
            "action_required"
        }
    ]

    if failures or pr_rows:

        signals.append({
            "repository": full,
            "failed_runs": failures,
            "open_prs": pr_rows,
            "evidence_strength":
                "STRONG"
                if failures
                else "MODERATE"
        })

result = {
    "generated": utcnow(),
    "mode": "READ_ONLY",
    "repositories": len(repository_rows),
    "signals": signals,
    "rules": {
        "no_mutation": True,
        "existing_repository_first": True,
        "unknown_license_blocks_reuse": True
    }
}

atomic_json(
    STATE
    / "research"
    / "latest.json",
    result
)

print(
    json.dumps({
        "repositories": len(repository_rows),
        "signals": len(signals)
    }, indent=2)
)
