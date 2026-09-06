#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import subprocess

from state_v11 import (
    STATE,
    atomic_json,
    utcnow
)

OUT = STATE / "recovery"

SAFE_CHECKS = {
    "command-exists",
    "file-exists",
    "http-status",
    "git-clean",
    "github-pr"
}

def run_capture(cmd):
    p = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        timeout=45
    )

    return {
        "returncode": p.returncode,
        "stdout": p.stdout[-10000:],
        "stderr": p.stderr[-10000:]
    }

def verify(args):

    result = {
        "job_id": args.job,
        "check_type": args.type,
        "target": args.target,
        "expected": args.expected,
        "observed_at": utcnow(),
        "pass": False,
        "evidence": {}
    }

    if args.type not in SAFE_CHECKS:
        raise SystemExit(
            "Unsupported verification type"
        )

    if args.type == "command-exists":
        result["evidence"] = run_capture([
            "sh",
            "-lc",
            "command -v \"$1\"",
            "sh",
            args.target
        ])

        result["pass"] = (
            result["evidence"]["returncode"] == 0
        )

    elif args.type == "file-exists":
        p = Path(args.target)

        result["evidence"] = {
            "exists": p.exists(),
            "size": (
                p.stat().st_size
                if p.exists()
                else None
            )
        }

        result["pass"] = p.exists()

    elif args.type == "git-clean":
        result["evidence"] = run_capture([
            "git",
            "-C",
            args.target,
            "status",
            "--porcelain"
        ])

        result["pass"] = (
            result["evidence"]["returncode"] == 0
            and not result["evidence"]["stdout"].strip()
        )

    elif args.type == "http-status":
        result["evidence"] = run_capture([
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

        observed = (
            result["evidence"]["stdout"].strip()
        )

        result["pass"] = (
            observed == str(args.expected)
        )

    elif args.type == "github-pr":
        repo, number = args.target.split(
            "#",
            1
        )

        result["evidence"] = run_capture([
            "gh",
            "pr",
            "view",
            number,
            "--repo",
            repo,
            "--json",
            "state,mergeable,isDraft"
        ])

        result["pass"] = (
            result["evidence"]["returncode"] == 0
        )

    out = OUT / f"{args.job}.json"

    atomic_json(
        out,
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

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--job",
        required=True
    )

    parser.add_argument(
        "--type",
        required=True,
        choices=sorted(SAFE_CHECKS)
    )

    parser.add_argument(
        "--target",
        required=True
    )

    parser.add_argument(
        "--expected",
        default="200"
    )

    verify(
        parser.parse_args()
    )
