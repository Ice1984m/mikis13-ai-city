#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import subprocess
import json
import uuid

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "state" / "v10" / "scouts"
OUT.mkdir(parents=True, exist_ok=True)

def run(cmd):
    p = subprocess.run(
        cmd,
        text=True,
        capture_output=True
    )
    return {
        "returncode": p.returncode,
        "stdout": p.stdout[-30000:],
        "stderr": p.stderr[-10000:]
    }

cycle = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
cycle_id = f"v10-{cycle}-{uuid.uuid4().hex[:6]}"

repos = run([
    "gh","repo","list","Ice1984m",
    "--limit","100",
    "--json","name,nameWithOwner,isArchived,pushedAt"
])

repo_rows = []

try:
    repo_rows = json.loads(repos["stdout"])
except Exception:
    repo_rows = []

signals = []

for repo in repo_rows[:80]:

    full = repo["nameWithOwner"]

    runs = run([
        "gh","run","list",
        "--repo",full,
        "--limit","5",
        "--json",
        "databaseId,name,status,conclusion,createdAt"
    ])

    prs = run([
        "gh","pr","list",
        "--repo",full,
        "--state","open",
        "--limit","10",
        "--json",
        "number,title,isDraft,mergeStateStatus,updatedAt"
    ])

    try:
        run_rows = json.loads(runs["stdout"] or "[]")
    except Exception:
        run_rows = []

    try:
        pr_rows = json.loads(prs["stdout"] or "[]")
    except Exception:
        pr_rows = []

    failures = [
        r for r in run_rows
        if r.get("conclusion")
        in {"failure","cancelled","timed_out","action_required"}
    ]

    if failures or pr_rows:
        signals.append({
            "repository": full,
            "failed_runs": failures,
            "open_prs": pr_rows
        })

result = {
    "cycle_id": cycle_id,
    "generated": datetime.now(timezone.utc).isoformat(),
    "mode": "READ_ONLY",
    "repo_count": len(repo_rows),
    "signal_count": len(signals),
    "signals": signals
}

latest = OUT / "latest.json"

latest.write_text(
    json.dumps(result, indent=2) + "\n",
    encoding="utf-8"
)

print(json.dumps({
    "cycle_id": cycle_id,
    "repositories": len(repo_rows),
    "signals": len(signals)
}, indent=2))
