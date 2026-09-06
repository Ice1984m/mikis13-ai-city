#!/usr/bin/env python3

from pathlib import Path
import json
import subprocess

from state_v11 import (
    STATE,
    atomic_json,
    utcnow
)

OUT = STATE / "dependencies" / "graph.json"

def run(cmd):

    p = subprocess.run(
        cmd,
        text=True,
        capture_output=True
    )

    if p.returncode != 0:
        return []

    try:
        return json.loads(
            p.stdout
        )
    except Exception:
        return []

repos = run([
    "gh",
    "repo",
    "list",
    "Ice1984m",
    "--limit",
    "100",
    "--json",
    "name,nameWithOwner,description,isArchived,pushedAt"
])

nodes = []
edges = []

for repo in repos:

    if repo.get("isArchived"):
        continue

    nodes.append({
        "id": repo["nameWithOwner"],
        "name": repo["name"],
        "description": repo.get("description"),
        "pushedAt": repo.get("pushedAt")
    })

known_links = {
    "mikis13-ai-city": [
        "mikis13-evolution-engine",
        "mikis13-control-plane",
        "mikis13-site"
    ],
    "mikis13-evolution-engine": [
        "mikis13-site"
    ],
    "mikis13-control-plane": [
        "mikis13-site"
    ]
}

available = {
    x["name"]
    for x in nodes
}

for source, targets in known_links.items():

    if source not in available:
        continue

    for target in targets:

        if target in available:
            edges.append({
                "from": f"Ice1984m/{source}",
                "to": f"Ice1984m/{target}",
                "type": "known_operational_relationship",
                "confidence": "MODERATE"
            })

result = {
    "generated": utcnow(),
    "nodes": nodes,
    "edges": edges,
    "warning":
        "Only evidence-backed or explicitly known relationships should be treated as dependencies."
}

atomic_json(
    OUT,
    result
)

print(
    json.dumps(
        {
            "repositories": len(nodes),
            "edges": len(edges)
        },
        indent=2
    )
)
