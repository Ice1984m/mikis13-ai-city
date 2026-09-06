#!/usr/bin/env python3

from pathlib import Path
import argparse
import json
import subprocess
import uuid

from state_v11 import (
    ROOT,
    STATE,
    atomic_json,
    load_json,
    utcnow
)

POLICY = json.loads(
    (
        ROOT
        / "config"
        / "v11-policy.json"
    ).read_text()
)

SAFE_ACTIONS = {
    "git-status",
    "git-diff-check",
    "python-compile",
    "python-test",
    "shell-syntax",
    "http-health",
    "gh-pr-view",
    "gh-run-list"
}

def run(cmd, cwd=None):

    p = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=120
    )

    return {
        "returncode": p.returncode,
        "stdout": p.stdout[-20000:],
        "stderr": p.stderr[-10000:]
    }

def execute(args):

    if (
        STATE
        / "OWNER_STOP"
    ).exists():

        raise SystemExit(
            "OWNER_STOP active"
        )

    if args.action not in SAFE_ACTIONS:
        raise SystemExit(
            "Action not allowed"
        )

    execution_id = (
        "EXEC-"
        + uuid.uuid4().hex[:12]
    )

    result = {
        "execution_id": execution_id,
        "job_id": args.job,
        "action": args.action,
        "target": args.target,
        "started_at": utcnow(),
        "mode": "BOUNDED_DETERMINISTIC",
        "result": None
    }

    if args.action == "git-status":

        result["result"] = run([
            "git",
            "-C",
            args.target,
            "status",
            "--short"
        ])

    elif args.action == "git-diff-check":

        result["result"] = run([
            "git",
            "-C",
            args.target,
            "diff",
            "--check"
        ])

    elif args.action == "python-compile":

        result["result"] = run([
            "python",
            "-m",
            "py_compile",
            args.target
        ])

    elif args.action == "python-test":

        result["result"] = run([
            "python",
            args.target
        ])

    elif args.action == "shell-syntax":

        result["result"] = run([
            "bash",
            "-n",
            args.target
        ])

    elif args.action == "http-health":

        result["result"] = run([
            "curl",
            "-L",
            "-sS",
            "-o",
            "/dev/null",
            "-w",
            "%{http_code}",
            "--connect-timeout",
            "8",
            "--max-time",
            "20",
            args.target
        ])

    elif args.action == "gh-pr-view":

        repo, number = args.target.split(
            "#",
            1
        )

        result["result"] = run([
            "gh",
            "pr",
            "view",
            number,
            "--repo",
            repo,
            "--json",
            "number,title,state,isDraft,mergeable,statusCheckRollup"
        ])

    elif args.action == "gh-run-list":

        result["result"] = run([
            "gh",
            "run",
            "list",
            "--repo",
            args.target,
            "--limit",
            "10",
            "--json",
            "databaseId,name,status,conclusion,createdAt"
        ])

    result["finished_at"] = utcnow()

    result["pass"] = (
        result["result"]["returncode"]
        == 0
    )

    atomic_json(
        STATE
        / "results"
        / f"{execution_id}.json",
        result
    )

    atomic_json(
        STATE
        / "results"
        / "latest.json",
        result
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )

    if not result["pass"]:
        raise SystemExit(2)

if __name__ == "__main__":

    p = argparse.ArgumentParser()

    p.add_argument(
        "--job",
        required=True
    )

    p.add_argument(
        "--action",
        required=True,
        choices=sorted(SAFE_ACTIONS)
    )

    p.add_argument(
        "--target",
        required=True
    )

    execute(
        p.parse_args()
    )
