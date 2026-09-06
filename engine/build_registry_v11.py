#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config"

def read(path):
    p = CFG / path
    if not p.exists():
        return []
    return json.loads(
        p.read_text(encoding="utf-8")
    ).get("blueprints", [])

existing = CFG / "blueprints.json"

canonical = {}

if existing.exists():
    old = json.loads(existing.read_text())
    for item in old.get("blueprints", []):
        canonical[int(item["id"])] = item

for item in read("automation-blueprints-301-350-v11.json"):
    row = dict(item)
    row["canonical_source"] = "V11"
    canonical[int(row["id"])] = row

missing = [
    i
    for i in range(1,351)
    if i not in canonical
]

if missing:
    raise SystemExit(
        "❌ Canonical registry mist IDs: "
        + ",".join(map(str,missing[:50]))
    )

items = [
    canonical[i]
    for i in range(1,351)
]

names = {}
duplicate_names = []

for row in items:
    key = row["name"].strip().casefold()

    if key in names:
        duplicate_names.append({
            "name": row["name"],
            "ids": [
                names[key],
                int(row["id"])
            ]
        })
    else:
        names[key] = int(row["id"])

result = {
    "version": 11,
    "canonical_count": len(items),
    "canonical_range": "1-350",
    "duplicate_names": duplicate_names,
    "blueprints": items
}

existing.write_text(
    json.dumps(result, indent=2) + "\n",
    encoding="utf-8"
)

print("✅ Canonical blueprint registry:", len(items))
print("Duplicate names:", len(duplicate_names))
