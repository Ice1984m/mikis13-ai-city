#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone, timedelta
import argparse
import hashlib
import json
import uuid

from state_v11 import (
    ROOT,
    STATE,
    atomic_json,
    load_json,
    utcnow
)

QUEUE = STATE / "jobs" / "queue.json"
ACTIVE = STATE / "jobs" / "active.json"

VALID_STATES = {
    "NEW",
    "EVIDENCE_READY",
    "READY",
    "ACTIVE",
    "BLOCKED",
    "VERIFIED",
    "FAILED",
    "CLOSED"
}

def queue():
    return load_json(
        QUEUE,
        {
            "version": 11,
            "jobs": []
        }
    )

def fingerprint(repository, problem, blueprint_id):
    raw = (
        repository.strip().lower()
        + "|"
        + problem.strip().lower()
        + "|"
        + str(blueprint_id)
    )

    return hashlib.sha256(
        raw.encode()
    ).hexdigest()[:24]

def create_job(
    repository,
    problem,
    blueprint_id,
    evidence_strength="UNKNOWN",
    priority=50
):
    data = queue()

    fp = fingerprint(
        repository,
        problem,
        blueprint_id
    )

    active_states = {
        "NEW",
        "EVIDENCE_READY",
        "READY",
        "ACTIVE",
        "BLOCKED"
    }

    for job in data["jobs"]:
        if (
            job["fingerprint"] == fp
            and job["state"] in active_states
        ):
            print(
                json.dumps(
                    {
                        "status": "DUPLICATE",
                        "job": job
                    },
                    indent=2
                )
            )
            return job

    job = {
        "job_id": "JOB-" + uuid.uuid4().hex[:12],
        "fingerprint": fp,
        "repository": repository,
        "problem": problem,
        "blueprint_id": int(blueprint_id),
        "state": (
            "EVIDENCE_READY"
            if evidence_strength != "UNKNOWN"
            else "NEW"
        ),
        "evidence_strength": evidence_strength,
        "priority": int(priority),
        "created_at": utcnow(),
        "updated_at": utcnow(),
        "attempts": 0,
        "lease": None,
        "gates": {
            "evidence": evidence_strength != "UNKNOWN",
            "duplicate_check": True,
            "repository_scope": bool(repository),
            "rollback_plan": False,
            "tests": "UNKNOWN",
            "security": "UNKNOWN",
            "healthcheck": "UNKNOWN",
            "recovery_verification": "UNKNOWN"
        }
    }

    data["jobs"].append(job)

    atomic_json(
        QUEUE,
        data
    )

    print(
        json.dumps(
            {
                "status": "CREATED",
                "job": job
            },
            indent=2
        )
    )

    return job

def refresh_states(data):
    for job in data["jobs"]:

        if job["state"] in {
            "VERIFIED",
            "FAILED",
            "CLOSED"
        }:
            continue

        lease = job.get("lease")

        if lease:
            expires = datetime.fromisoformat(
                lease["expires_at"]
            )

            if expires < datetime.now(timezone.utc):
                job["lease"] = None

                if job["state"] == "ACTIVE":
                    job["state"] = "READY"

        gates = job["gates"]

        if (
            gates["evidence"]
            and gates["duplicate_check"]
            and gates["repository_scope"]
            and gates["rollback_plan"]
            and job["state"] not in {
                "ACTIVE",
                "BLOCKED"
            }
        ):
            job["state"] = "READY"

        elif (
            gates["evidence"]
            and job["state"] == "NEW"
        ):
            job["state"] = "EVIDENCE_READY"

def claim():
    data = queue()
    refresh_states(data)

    already = [
        j for j in data["jobs"]
        if j["state"] == "ACTIVE"
    ]

    if already:
        print(
            json.dumps({
                "status": "BUSY",
                "active_job": already[0]
            }, indent=2)
        )

        atomic_json(
            QUEUE,
            data
        )

        return None

    candidates = [
        j for j in data["jobs"]
        if j["state"] == "READY"
    ]

    if not candidates:
        print(
            json.dumps({
                "status": "NO_READY_JOB"
            })
        )

        atomic_json(
            QUEUE,
            data
        )

        return None

    candidates.sort(
        key=lambda x: (
            x["priority"],
            x["created_at"]
        ),
        reverse=True
    )

    job = candidates[0]

    now = datetime.now(timezone.utc)

    job["lease"] = {
        "claimed_at": now.isoformat(),
        "expires_at": (
            now + timedelta(seconds=1800)
        ).isoformat()
    }

    job["state"] = "ACTIVE"
    job["updated_at"] = utcnow()

    atomic_json(
        QUEUE,
        data
    )

    atomic_json(
        ACTIVE,
        job
    )

    print(
        json.dumps({
            "status": "CLAIMED",
            "job": job
        }, indent=2)
    )

    return job

def show():
    data = queue()
    refresh_states(data)

    atomic_json(
        QUEUE,
        data
    )

    print(
        json.dumps(
            data,
            indent=2
        )
    )

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(
        dest="cmd",
        required=True
    )

    add = sub.add_parser("add")

    add.add_argument("--repo", required=True)
    add.add_argument("--problem", required=True)
    add.add_argument("--blueprint", type=int, required=True)
    add.add_argument("--evidence", default="UNKNOWN")
    add.add_argument("--priority", type=int, default=50)

    sub.add_parser("claim")
    sub.add_parser("show")

    args = parser.parse_args()

    if args.cmd == "add":
        create_job(
            args.repo,
            args.problem,
            args.blueprint,
            args.evidence,
            args.priority
        )

    elif args.cmd == "claim":
        claim()

    else:
        show()
