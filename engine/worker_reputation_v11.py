#!/usr/bin/env python3

import argparse
import json

from state_v11 import (
    STATE,
    atomic_json,
    load_json,
    utcnow
)

DB = STATE / "reputation" / "workers.json"

def load():
    return load_json(
        DB,
        {
            "version": 11,
            "workers": {}
        }
    )

def record(args):

    db = load()

    row = db["workers"].setdefault(
        args.worker,
        {
            "success": 0,
            "failure": 0,
            "unknown": 0,
            "domains": {},
            "history": []
        }
    )

    if args.result == "SUCCESS":
        row["success"] += 1

    elif args.result == "FAILURE":
        row["failure"] += 1

    else:
        row["unknown"] += 1

    domain = row["domains"].setdefault(
        args.domain,
        {
            "success": 0,
            "failure": 0,
            "unknown": 0
        }
    )

    if args.result == "SUCCESS":
        domain["success"] += 1

    elif args.result == "FAILURE":
        domain["failure"] += 1

    else:
        domain["unknown"] += 1

    row["history"].append({
        "time": utcnow(),
        "job": args.job,
        "domain": args.domain,
        "result": args.result
    })

    attempts = (
        row["success"]
        + row["failure"]
    )

    row["accuracy"] = (
        round(
            row["success"]
            / attempts,
            3
        )
        if attempts
        else None
    )

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

def rank():

    db = load()

    rows = []

    for worker, data in db["workers"].items():

        attempts = (
            data["success"]
            + data["failure"]
        )

        score = (
            (data["success"] + 1)
            / (attempts + 2)
        )

        rows.append({
            "worker": worker,
            "score": round(score, 3),
            "success": data["success"],
            "failure": data["failure"],
            "unknown": data["unknown"]
        })

    rows.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    print(
        json.dumps(
            rows,
            indent=2
        )
    )

if __name__ == "__main__":

    p = argparse.ArgumentParser()
    s = p.add_subparsers(
        dest="cmd",
        required=True
    )

    r = s.add_parser("record")
    r.add_argument("--worker", required=True)
    r.add_argument("--job", required=True)
    r.add_argument("--domain", required=True)
    r.add_argument(
        "--result",
        required=True,
        choices=[
            "SUCCESS",
            "FAILURE",
            "UNKNOWN"
        ]
    )

    s.add_parser("rank")

    args = p.parse_args()

    if args.cmd == "record":
        record(args)
    else:
        rank()
