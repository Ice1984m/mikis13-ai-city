#!/usr/bin/env python3

import argparse
import hashlib
import json
from pathlib import Path

config = json.loads(
    Path("config/virtual-workforce.json").read_text(
        encoding="utf-8"
    )
)

ranges = []
start = 1

for role, count in config["roles"].items():
    end = start + count - 1
    ranges.append((start, end, role))
    start = end + 1

assert start - 1 == config["total_virtual_roles"]

parser = argparse.ArgumentParser()
parser.add_argument("worker_id", type=int)
args = parser.parse_args()

if not 1 <= args.worker_id <= config["total_virtual_roles"]:
    raise SystemExit("Worker-ID valt buiten het register")

role = next(
    role
    for low, high, role in ranges
    if low <= args.worker_id <= high
)

identity = f"v16-{args.worker_id:07d}"

print(json.dumps({
    "id": identity,
    "role": role,
    "deterministic_key": hashlib.sha256(
        identity.encode()
    ).hexdigest()
}, indent=2))
