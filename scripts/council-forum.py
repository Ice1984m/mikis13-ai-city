#!/usr/bin/env python3

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORUM = ROOT / "docs/council/forum"
DECISIONS = ROOT / "docs/council/decisions"
AUDIT = ROOT / "logs/council/audit.jsonl"

def slug(value):
    return (
        re.sub(r"[^a-z0-9-]+", "-", value.lower())
        .strip("-")[:60]
        or "topic"
    )

def write_audit(event):
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    previous = "0" * 64

    if AUDIT.exists() and AUDIT.stat().st_size:
        previous = json.loads(
            AUDIT.read_text(encoding="utf-8")
            .splitlines()[-1]
        )["record_hash"]

    event = {
        "utc": dt.datetime.now(
            dt.timezone.utc
        ).isoformat(),
        **event,
        "previous_hash": previous
    }

    canonical = json.dumps(
        event,
        sort_keys=True,
        separators=(",", ":")
    )

    event["record_hash"] = hashlib.sha256(
        canonical.encode()
    ).hexdigest()

    with AUDIT.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(event, sort_keys=True) + "\n"
        )

parser = argparse.ArgumentParser()
parser.add_argument("--title", required=True)
parser.add_argument("--evidence", required=True)
parser.add_argument(
    "--decision",
    choices=["approve", "reject", "defer"],
    required=True
)
parser.add_argument("--reason", required=True)
args = parser.parse_args()

stamp = dt.datetime.now(
    dt.timezone.utc
).strftime("%Y%m%d-%H%M%S")

name = slug(args.title)

FORUM.mkdir(parents=True, exist_ok=True)
DECISIONS.mkdir(parents=True, exist_ok=True)

forum_text = f"""# {args.title}

## Bewijs

{args.evidence}

## Councilbesluit

{args.decision}

## Motivering

{args.reason}
"""

decision_text = f"""# Councilbeslissing: {args.title}

- Tijd: {stamp} UTC
- Uitkomst: {args.decision}

## Bewijs

{args.evidence}

## Motivering

{args.reason}
"""

(FORUM / f"{stamp}-{name}.md").write_text(
    forum_text,
    encoding="utf-8"
)

(DECISIONS / f"ADR-{stamp}-{name}.md").write_text(
    decision_text,
    encoding="utf-8"
)

write_audit({
    "type": "council_decision",
    "title": args.title,
    "decision": args.decision,
    "evidence_hash": hashlib.sha256(
        args.evidence.encode()
    ).hexdigest()
})

print("✅ Forumverslag en Councilbesluit opgeslagen")
