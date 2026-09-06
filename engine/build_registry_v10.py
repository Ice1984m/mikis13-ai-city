#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config"

sources = []

def load(name):
    path = CFG / name
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("blueprints", [])

v6 = load("automation-blueprints-50.json")
v8 = load("automation-blueprints-90-v8.json")
v9 = load("automation-blueprints-101-200-v9.json")
v10 = load("automation-blueprints-201-300-v10.json")

canonical = {}
legacy = []

# Canonical strategy:
# 1-50   = V6
# 51-100 = V8
# 101-200 = V9
# 201-300 = V10
#
# V8 entries 11-50 remain recorded as legacy aliases rather than
# producing duplicate executable IDs.

for item in v6:
    i = int(item["id"])
    if 1 <= i <= 50:
        row = dict(item)
        row["canonical_source"] = "V6"
        canonical[i] = row

for item in v8:
    i = int(item["id"])
    if 51 <= i <= 100:
        row = dict(item)
        row["canonical_source"] = "V8"
        canonical[i] = row
    elif 11 <= i <= 50:
        legacy.append({
            "legacy_id": i,
            "name": item.get("name"),
            "source": "V8",
            "reason": "Overlaps canonical V6 ID range; retained as legacy reference only."
        })

for item in v9:
    i = int(item["id"])
    if 101 <= i <= 200:
        row = dict(item)
        row["canonical_source"] = "V9"
        canonical[i] = row

for item in v10:
    i = int(item["id"])
    if 201 <= i <= 300:
        row = dict(item)
        row["canonical_source"] = "V10"
        canonical[i] = row

missing = [i for i in range(1, 301) if i not in canonical]

if missing:
    raise SystemExit(
        "Canonical registry incomplete. Missing IDs: "
        + ", ".join(map(str, missing[:40]))
    )

items = [canonical[i] for i in range(1, 301)]

names = {}
duplicate_names = []

for row in items:
    key = row["name"].strip().casefold()
    if key in names:
        duplicate_names.append({
            "name": row["name"],
            "ids": [names[key], row["id"]]
        })
    else:
        names[key] = row["id"]

result = {
    "version": 10,
    "canonical_count": len(items),
    "canonical_range": "1-300",
    "rules": {
        "unique_ids": True,
        "execution_uses_only_canonical_registry": True,
        "legacy_overlapping_blueprints_are_not_active_jobs": True
    },
    "duplicate_names": duplicate_names,
    "legacy_aliases": legacy,
    "blueprints": items
}

(CFG / "blueprints.json").write_text(
    json.dumps(result, indent=2) + "\n",
    encoding="utf-8"
)

print("✅ Canonical registry:", len(items))
print("Legacy overlapping V8 entries:", len(legacy))
print("Duplicate canonical names:", len(duplicate_names))
