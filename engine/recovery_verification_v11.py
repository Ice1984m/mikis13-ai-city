#!/usr/bin/env python3

import argparse
import subprocess
import json

from pathlib import Path

from state_v11 import (
    STATE,
    atomic_json,
    now
)

parser = argparse.ArgumentParser()

parser.add_argument(
    "--job",
    required=True
)

parser.add_argument(
    "--type",
    required=True,
    choices=[
        "file-exists",
        "http-status",
        "git-clean"
    ]
)

parser.add_argument(
    "--target",
    required=True
)

parser.add_argument(
    "--expected",
    default="200"
)

args = parser.parse_args()

result = {
    "job_id": args.job,
    "type": args.type,
    "target": args.target,
    "checked_at": now(),
    "pass": False
}

if args.type == "file-exists":

    result["pass"] = (
        Path(args.target).exists()
    )

elif args.type == "git-clean":

    p = subprocess.run(
        [
            "git",
            "-C",
            args.target,
            "status",
            "--porcelain"
        ],
        text=True,
        capture_output=True
    )

    result["pass"] = (
        p.returncode == 0
        and not p.stdout.strip()
    )

elif args.type == "http-status":

    p = subprocess.run(
        [
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
        ],
        text=True,
        capture_output=True
    )

    result["observed"] = (
        p.stdout.strip()
    )

    result["pass"] = (
        p.returncode == 0
        and result["observed"]
        == args.expected
    )

atomic_json(
    STATE
    / "recovery"
    / f"{args.job}.json",
    result
)

print(
    json.dumps(
        result,
        indent=2
    )
)

raise SystemExit(
    0
    if result["pass"]
    else 2
)
