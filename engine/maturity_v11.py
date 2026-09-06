#!/usr/bin/env python3

import argparse
import json

from state_v11 import (
    ROOT,
    STATE,
    atomic_json,
    load_json,
    utcnow
)

DB = STATE / "maturity" / "blueprints.json"

ORDER = [
    "IDEA",
    "PLANNED",
    "PROTOTYPE",
    "TESTED",
    "VERIFIED",
    "DEPLOYED",
    "PROVEN"
]

REQUIREMENTS = {
    "PROTOTYPE": [
        "prototype_evidence"
    ],
    "TESTED": [
        "tests_pass"
    ],
    "VERIFIED": [
        "tests_pass",
        "healthcheck_pass"
    ],
    "DEPLOYED": [
        "deployment_evidence",
        "healthcheck_pass"
    ],
    "PROVEN": [
        "deployment_evidence",
        "healthcheck_pass",
        "repeated_success"
    ]
}

def registry():

    return json.loads(
        (
            ROOT
            / "config"
            / "blueprints.json"
        ).read_text()
    )

def initialise():

    db = load_json(
        DB,
        {
            "version": 11,
            "blueprints": {}
        }
    )

    for b in registry()["blueprints"]:

        key = str(b["id"])

        db["blueprints"].setdefault(
            key,
            {
                "id": int(b["id"]),
                "name": b["name"],
                "state": (
                    b.get(
                        "status",
                        "PLANNED"
                    )
                    if b.get(
                        "status",
                        "PLANNED"
                    ) in ORDER
                    else "PLANNED"
                ),
                "evidence": {},
                "updated_at": utcnow()
            }
        )

    atomic_json(
        DB,
        db
    )

    return db

def promote(args):

    db = initialise()

    row = db["blueprints"].get(
        str(args.id)
    )

    if not row:
        raise SystemExit(
            "Blueprint not found"
        )

    target = args.target

    if target not in ORDER:
        raise SystemExit(
            "Unsupported maturity state"
        )

    current = row["state"]

    if current not in ORDER:
        raise SystemExit(
            "Current state cannot be auto-promoted"
        )

    if (
        ORDER.index(target)
        != ORDER.index(current) + 1
    ):
        raise SystemExit(
            "Only one maturity step at a time is allowed"
        )

    missing = [
        req
        for req in REQUIREMENTS.get(
            target,
            []
        )
        if not row["evidence"].get(req)
    ]

    if missing:
        raise SystemExit(
            "Missing evidence: "
            + ", ".join(missing)
        )

    row["state"] = target
    row["updated_at"] = utcnow()

    atomic_json(
        DB,
        db
    )

    print(
        json.dumps(
            row,
            indent=2
        )
    )

def evidence(args):

    db = initialise()

    row = db["blueprints"].get(
        str(args.id)
    )

    if not row:
        raise SystemExit(
            "Blueprint not found"
        )

    row["evidence"][args.key] = True
    row["updated_at"] = utcnow()

    atomic_json(
        DB,
        db
    )

    print(
        json.dumps(
            row,
            indent=2
        )
    )

def summary():

    db = initialise()

    counts = {}

    for row in db["blueprints"].values():
        counts[row["state"]] = (
            counts.get(
                row["state"],
                0
            )
            + 1
        )

    print(
        json.dumps(
            counts,
            indent=2
        )
    )

if __name__ == "__main__":

    p = argparse.ArgumentParser()
    s = p.add_subparsers(
        dest="cmd",
        required=True
    )

    e = s.add_parser("evidence")
    e.add_argument("--id", type=int, required=True)
    e.add_argument("--key", required=True)

    pr = s.add_parser("promote")
    pr.add_argument("--id", type=int, required=True)
    pr.add_argument("--target", required=True)

    s.add_parser("summary")

    args = p.parse_args()

    if args.cmd == "evidence":
        evidence(args)

    elif args.cmd == "promote":
        promote(args)

    else:
        summary()
