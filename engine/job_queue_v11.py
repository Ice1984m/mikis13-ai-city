#!/usr/bin/env python3

import argparse
import hashlib
import json
import uuid

from state_v11 import (
    STATE,
    atomic_json,
    read_json,
    now
)

QUEUE = (
    STATE
    / "jobs"
    / "queue.json"
)

def load():
    return read_json(
        QUEUE,
        {
            "version": 11,
            "jobs": []
        }
    )

def fingerprint(repo, problem, blueprint):
    raw = (
        repo.lower()
        + "|"
        + problem.lower()
        + "|"
        + str(blueprint)
    )

    return hashlib.sha256(
        raw.encode()
    ).hexdigest()[:24]

def add(args):
    data = load()

    fp = fingerprint(
        args.repo,
        args.problem,
        args.blueprint
    )

    for job in data["jobs"]:

        if (
            job["fingerprint"] == fp
            and job["state"]
            not in {
                "FAILED",
                "VERIFIED",
                "CLOSED"
            }
        ):
            print(
                json.dumps({
                    "status": "DUPLICATE",
                    "job": job
                }, indent=2)
            )

            return

    job = {
        "job_id":
            "JOB-"
            + uuid.uuid4().hex[:12],

        "fingerprint": fp,
        "repository": args.repo,
        "problem": args.problem,
        "blueprint_id": args.blueprint,
        "priority": args.priority,

        "evidence":
            args.evidence,

        "state":
            "EVIDENCE_READY"
            if args.evidence != "UNKNOWN"
            else "NEW",

        "created_at": now(),

        "gates": {
            "evidence":
                args.evidence != "UNKNOWN",

            "duplicate_check":
                True,

            "repository_scope":
                True,

            "rollback_plan":
                False,

            "tests":
                "UNKNOWN",

            "security":
                "UNKNOWN",

            "healthcheck":
                "UNKNOWN",

            "recovery_verification":
                "UNKNOWN"
        }
    }

    data["jobs"].append(job)

    atomic_json(
        QUEUE,
        data
    )

    print(
        json.dumps(
            job,
            indent=2
        )
    )

def show():
    print(
        json.dumps(
            load(),
            indent=2
        )
    )

parser = argparse.ArgumentParser()

sub = parser.add_subparsers(
    dest="cmd",
    required=True
)

a = sub.add_parser("add")

a.add_argument(
    "--repo",
    required=True
)

a.add_argument(
    "--problem",
    required=True
)

a.add_argument(
    "--blueprint",
    type=int,
    required=True
)

a.add_argument(
    "--evidence",
    default="UNKNOWN"
)

a.add_argument(
    "--priority",
    type=int,
    default=50
)

sub.add_parser("show")

args = parser.parse_args()

if args.cmd == "add":
    add(args)
else:
    show()
