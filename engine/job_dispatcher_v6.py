#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path.home() / "mikis13-ai-city"
STATE = ROOT / "state"

QUEUE = STATE / "jobs/queue.jsonl"
ACTIVE = STATE / "jobs/active.json"
REPORT = ROOT / "reports/jobs-latest.md"

def now():
    return datetime.now(timezone.utc).isoformat()

def fp(text):
    return hashlib.sha256(text.encode()).hexdigest()[:16]

def read_json(path, default):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default

def load_queue():
    result = []
    if QUEUE.exists():
        for line in QUEUE.read_text().splitlines():
            try:
                result.append(json.loads(line))
            except Exception:
                pass
    return result

def seed_from_blueprints():
    bp = read_json(
        ROOT / "config/automation-blueprints-50.json",
        {}
    )

    existing = {
        j.get("blueprint_id")
        for j in load_queue()
    }

    QUEUE.parent.mkdir(parents=True, exist_ok=True)

    with QUEUE.open("a") as f:
        for item in bp.get("blueprints", []):
            if item["id"] not in existing:
                job = {
                    "id": fp(f"{item['id']}:{item['name']}"),
                    "blueprint_id": item["id"],
                    "title": item["name"],
                    "owner": item["owner"],
                    "goal": item["goal"],
                    "gate": item["gate"],
                    "priority": 100 - item["id"],
                    "status": "NEW",
                    "created": now()
                }
                f.write(json.dumps(job) + "\n")

def select_one():
    active = read_json(ACTIVE, None)

    if active and active.get("status") == "ACTIVE":
        return active

    jobs = [
        j for j in load_queue()
        if j.get("status") == "NEW"
    ]

    if not jobs:
        return None

    jobs.sort(
        key=lambda x: x.get("priority", 0),
        reverse=True
    )

    job = jobs[0]
    job["status"] = "ACTIVE"
    job["activated"] = now()

    ACTIVE.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE.write_text(
        json.dumps(job, indent=2) + "\n"
    )

    return job

def main():
    seed_from_blueprints()
    job = select_one()

    queue = load_queue()

    lines = [
        "# AI City Job Dispatcher V6",
        "",
        f"Generated: {now()}",
        "",
        f"Queued jobs: {len(queue)}",
        ""
    ]

    if job:
        lines += [
            "## Active job",
            "",
            f"- id: `{job['id']}`",
            f"- blueprint: {job['blueprint_id']}",
            f"- title: {job['title']}",
            f"- owner: {job['owner']}",
            f"- goal: {job['goal']}",
            f"- gate: {job['gate']}",
            ""
        ]

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines))

    print(json.dumps({
        "active_job": job,
        "queue_count": len(queue)
    }, indent=2))

if __name__ == "__main__":
    main()
