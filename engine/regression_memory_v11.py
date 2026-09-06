#!/usr/bin/env python3

from pathlib import Path
import argparse
import hashlib
import json
import re

from state_v11 import (
    STATE,
    atomic_json,
    load_json,
    utcnow
)

DB = STATE / "regressions" / "memory.json"

def normalize(text):

    text = text.lower()

    text = re.sub(
        r'\b\d{4}-\d{2}-\d{2}[t ][0-9:.+\-z]+\b',
        '<timestamp>',
        text
    )

    text = re.sub(
        r'\b[0-9a-f]{7,40}\b',
        '<sha>',
        text
    )

    text = re.sub(
        r'\b\d+\b',
        '<n>',
        text
    )

    text = re.sub(
        r'\s+',
        ' ',
        text
    ).strip()

    return text

def signature(text):

    canonical = normalize(text)

    return hashlib.sha256(
        canonical.encode()
    ).hexdigest()[:20]

def add(args):

    db = load_json(
        DB,
        {
            "version": 11,
            "failures": []
        }
    )

    sig = signature(args.error)

    existing = None

    for row in db["failures"]:
        if (
            row["signature"] == sig
            and row["repository"] == args.repo
        ):
            existing = row
            break

    if not existing:

        existing = {
            "signature": sig,
            "repository": args.repo,
            "canonical_error": normalize(
                args.error
            ),
            "count": 0,
            "first_seen": utcnow(),
            "last_seen": None,
            "confirmed_cause": None,
            "successful_fix": None,
            "regression_test": None
        }

        db["failures"].append(
            existing
        )

    existing["count"] += 1
    existing["last_seen"] = utcnow()

    atomic_json(
        DB,
        db
    )

    print(
        json.dumps(
            existing,
            indent=2
        )
    )

    if existing["count"] >= 3:
        print(
            "⚠️ recurring failure: deeper diagnosis required"
        )

def show():

    print(
        json.dumps(
            load_json(
                DB,
                {
                    "version": 11,
                    "failures": []
                }
            ),
            indent=2
        )
    )

if __name__ == "__main__":

    p = argparse.ArgumentParser()
    s = p.add_subparsers(
        dest="cmd",
        required=True
    )

    a = s.add_parser("add")
    a.add_argument("--repo", required=True)
    a.add_argument("--error", required=True)

    s.add_parser("show")

    args = p.parse_args()

    if args.cmd == "add":
        add(args)
    else:
        show()
