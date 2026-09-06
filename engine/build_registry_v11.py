#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

registry_file = ROOT / "config" / "blueprints.json"
v11_file = (
    ROOT
    / "config"
    / "automation-blueprints-301-350-v11.json"
)

if not registry_file.exists():
    raise SystemExit(
        "❌ V10 canonical registry ontbreekt"
    )

registry = json.loads(
    registry_file.read_text()
)

old = {
    int(x["id"]): x
    for x in registry["blueprints"]
}

if len(old) != 300:
    raise SystemExit(
        f"❌ Verwacht 300 V10 blueprints, gevonden {len(old)}"
    )

v11 = json.loads(
    v11_file.read_text()
)

for item in v11["blueprints"]:
    row = dict(item)
    row["canonical_source"] = "V11"
    old[int(row["id"])] = row

missing = [
    x
    for x in range(1, 351)
    if x not in old
]

if missing:
    raise SystemExit(
        f"❌ Ontbrekende IDs: {missing}"
    )

items = [
    old[x]
    for x in range(1, 351)
]

result = {
    "version": 11,
    "canonical_count": 350,
    "canonical_range": "1-350",
    "blueprints": items
}

registry_file.write_text(
    json.dumps(result, indent=2) + "\n"
)

print("✅ Canonical registry = 350")
