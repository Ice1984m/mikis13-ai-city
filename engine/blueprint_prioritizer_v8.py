#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path.home() / "mikis13-ai-city"
STATE = ROOT / "state"
REPORTS = ROOT / "reports"

SOURCE = ROOT / "config/automation-blueprints-90-v8.json"

def read_json(path, default=None):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default

def score(item):
    impact = float(item.get("expected_impact", 0))
    evidence = float(item.get("evidence_score", 0))
    complexity = float(item.get("complexity", 100))
    maintenance = float(item.get("maintenance_cost", 100))
    risk = float(item.get("risk", 100))

    gate_bonus = {
        "security": 18,
        "healthcheck": 16,
        "tests": 14,
        "lock": 12,
        "rollback": 12,
        "evidence": 10,
        "learning": 8,
        "git": 10,
        "local": 6,
        "budget": 6,
        "approval": -4
    }.get(item.get("gate"), 0)

    dependency_penalty = (
        0
        if item.get("dependency_ready", True)
        else 30
    )

    result = (
        impact * 1.4
        + evidence * 0.5
        + gate_bonus
        - complexity * 0.45
        - maintenance * 0.35
        - risk * 0.30
        - dependency_penalty
    )

    return round(result, 2)

def main():

    data = read_json(
        SOURCE,
        {}
    )

    candidates = []

    for item in data.get("blueprints", []):

        if item.get("status") in (
            "DONE",
            "REJECTED",
            "PAUSED"
        ):
            continue

        row = dict(item)
        row["priority_score"] = score(item)

        candidates.append(row)

    candidates.sort(
        key=lambda x: x["priority_score"],
        reverse=True
    )

    selected = (
        candidates[0]
        if candidates
        else None
    )

    result = {
        "generated":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "candidate_count":
            len(candidates),

        "selected":
            selected,

        "top10":
            candidates[:10],

        "rule":
            (
                "Highest score does not authorize execution. "
                "Evidence, tests, security, healthcheck and rollback remain mandatory."
            )
    }

    out = (
        STATE
        / "blueprint-priority"
        / "latest.json"
    )

    out.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    out.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        ) + "\n"
    )

    REPORTS.mkdir(
        parents=True,
        exist_ok=True
    )

    lines = [
        "# AI City Blueprint Priority V8",
        "",
        f"Generated: {result['generated']}",
        "",
        f"Candidates: {len(candidates)}",
        ""
    ]

    if selected:
        lines += [
            "## Recommended next blueprint",
            "",
            f"**#{selected['id']} — {selected['name']}**",
            "",
            f"- owner: {selected['owner']}",
            f"- gate: {selected['gate']}",
            f"- score: {selected['priority_score']}",
            f"- expected impact: {selected['expected_impact']}",
            f"- complexity: {selected['complexity']}",
            f"- maintenance: {selected['maintenance_cost']}",
            "",
            selected["goal"],
            ""
        ]

    lines += [
        "## Top 10",
        ""
    ]

    for item in candidates[:10]:
        lines.append(
            f"- #{item['id']} {item['name']} — "
            f"score {item['priority_score']}"
        )

    lines += [
        "",
        "## Safety",
        "",
        "Priority does not equal permission to merge.",
        "",
        "Required before implementation:",
        "- duplicate check",
        "- bot branch",
        "- tests",
        "- security",
        "- healthcheck",
        "- rollback",
        ""
    ]

    (
        REPORTS
        / "blueprint-priority-v8.md"
    ).write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )

if __name__ == "__main__":
    main()
