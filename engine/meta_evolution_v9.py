#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import json
import math

ROOT = Path.home() / "mikis13-ai-city"

SOURCE = (
    ROOT
    / "config"
    / "automation-blueprints-101-200-v9.json"
)

STATE = (
    ROOT
    / "state"
    / "meta-evolution"
)

REPORT = (
    ROOT
    / "reports"
    / "meta-evolution-v9.md"
)

def read_json(path, default=None):
    try:
        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        return default

def calculate(item):

    impact = float(
        item.get(
            "expected_impact",
            0
        )
    )

    evidence = float(
        item.get(
            "evidence_score",
            0
        )
    )

    novelty = float(
        item.get(
            "novel_capability_score",
            0
        )
    )

    complexity = float(
        item.get(
            "complexity",
            100
        )
    )

    maintenance = float(
        item.get(
            "maintenance_cost",
            100
        )
    )

    risk = float(
        item.get(
            "risk",
            100
        )
    )

    gate_bonus = {
        "security": 12,
        "tests": 12,
        "healthcheck": 12,
        "rollback": 10,
        "evidence": 8,
        "learning": 7,
        "local": 5,
        "approval": -4
    }.get(
        item.get("gate"),
        0
    )

    domain_bonus = {
        "causal_reasoning": 10,
        "simulation": 8,
        "code_intelligence": 9,
        "testing": 10,
        "prompt_engineering": 9,
        "knowledge": 8,
        "supply_chain": 8,
        "android": 8,
        "operations": 10,
        "meta": 10
    }.get(
        item.get("domain"),
        0
    )

    dependency_penalty = (
        0
        if item.get(
            "dependency_ready",
            True
        )
        else 25
    )

    score = (
        impact * 1.15
        + evidence * 0.40
        + novelty * 0.35
        + gate_bonus
        + domain_bonus
        - complexity * 0.38
        - maintenance * 0.30
        - risk * 0.27
        - dependency_penalty
    )

    return round(
        score,
        2
    )

def classify(item, score):

    complexity = item["complexity"]

    if score >= 125 and complexity <= 35:
        return "HIGH_VALUE_FAST"

    if score >= 115:
        return "HIGH_VALUE"

    if score >= 100:
        return "RESEARCH_NEXT"

    if score >= 85:
        return "BACKLOG"

    return "LOW_PRIORITY"

def main():

    data = read_json(
        SOURCE,
        {}
    )

    ranked = []

    for item in data.get(
        "blueprints",
        []
    ):

        if item.get(
            "status"
        ) in (
            "DONE",
            "REJECTED"
        ):
            continue

        row = dict(item)

        score = calculate(row)

        row[
            "meta_score"
        ] = score

        row[
            "classification"
        ] = classify(
            row,
            score
        )

        ranked.append(row)

    ranked.sort(
        key=lambda x:
            x["meta_score"],
        reverse=True
    )

    # Limit one recommended execution candidate.
    selected = (
        ranked[0]
        if ranked
        else None
    )

    domains = {}

    for row in ranked:
        domain = row["domain"]

        domains.setdefault(
            domain,
            []
        ).append(
            row["meta_score"]
        )

    domain_summary = []

    for domain, scores in domains.items():

        domain_summary.append({
            "domain":
                domain,

            "count":
                len(scores),

            "average_score":
                round(
                    sum(scores)
                    / len(scores),
                    2
                ),

            "best_score":
                max(scores)
        })

    domain_summary.sort(
        key=lambda x:
            x["average_score"],
        reverse=True
    )

    result = {
        "generated":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "candidate_count":
            len(ranked),

        "selected":
            selected,

        "top20":
            ranked[:20],

        "domain_summary":
            domain_summary,

        "execution_rule":
            (
                "Selection is a recommendation only. "
                "Implementation still requires evidence, duplicate check, "
                "tests, security, healthcheck and rollback."
            )
    }

    STATE.mkdir(
        parents=True,
        exist_ok=True
    )

    (
        STATE
        / "latest.json"
    ).write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
        + "\n"
    )

    lines = [
        "# Mikis13 AI City V9 — Meta Evolution",
        "",
        f"Generated: {result['generated']}",
        "",
        f"Candidates: {len(ranked)}",
        ""
    ]

    if selected:

        lines.extend([
            "## Highest-value candidate",
            "",
            f"### #{selected['id']} — {selected['name']}",
            "",
            f"- Domain: {selected['domain']}",
            f"- Owner: {selected['owner']}",
            f"- Gate: {selected['gate']}",
            f"- Meta score: {selected['meta_score']}",
            f"- Classification: {selected['classification']}",
            f"- Expected impact: {selected['expected_impact']}",
            f"- Complexity: {selected['complexity']}",
            f"- Maintenance: {selected['maintenance_cost']}",
            f"- Novel capability: {selected['novel_capability_score']}",
            "",
            selected["goal"],
            ""
        ])

    lines += [
        "## Top 20",
        ""
    ]

    for row in ranked[:20]:
        lines.append(
            f"- #{row['id']} {row['name']} "
            f"— {row['meta_score']} "
            f"— {row['classification']}"
        )

    lines += [
        "",
        "## Domains",
        ""
    ]

    for d in domain_summary:
        lines.append(
            f"- {d['domain']}: "
            f"avg={d['average_score']} "
            f"best={d['best_score']}"
        )

    lines += [
        "",
        "## Hard rule",
        "",
        "A high score is not permission to execute or merge.",
        ""
    ]

    REPORT.write_text(
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
