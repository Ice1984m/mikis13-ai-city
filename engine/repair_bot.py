#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import subprocess
import json
import os

HOME = Path.home()
ROOT = HOME / "mikis13-ai-city"

STATE = ROOT / "state"
REPORTS = ROOT / "reports"

def now():
    return datetime.now(timezone.utc).isoformat()

def run(cmd):
    p = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True
    )
    return {
        "code": p.returncode,
        "stdout": p.stdout.strip(),
        "stderr": p.stderr.strip()
    }

def check_file(path):
    p = ROOT / path

    return {
        "name": path,
        "ok": p.exists() and p.stat().st_size > 0
    }

def main():

    checks = []

    for path in [
        "config/organization.json",
        "config/providers.json",
        "config/startpoint.json",
        "engine/city.py",
        "engine/prompt_lab.py",
        "scripts/run-city.sh",
        "scripts/security.sh",
        "tests/test_city.py"
    ]:
        checks.append(
            check_file(path)
        )

    python_compile = run([
        "python",
        "-m",
        "py_compile",
        "engine/city.py",
        "engine/prompt_lab.py",
        "engine/repair_bot.py"
    ])

    checks.append({
        "name": "python-compile",
        "ok": python_compile["code"] == 0
    })

    json_org = run([
        "python",
        "-m",
        "json.tool",
        "config/organization.json"
    ])

    checks.append({
        "name": "organization-json",
        "ok": json_org["code"] == 0
    })

    security = run([
        "bash",
        "scripts/security.sh"
    ])

    checks.append({
        "name": "security-gate",
        "ok": security["code"] == 0
    })

    git_status = run([
        "git",
        "status",
        "--porcelain"
    ])

    failed = [
        x["name"]
        for x in checks
        if not x["ok"]
    ]

    health = round(
        100
        * (
            len(checks)
            - len(failed)
        )
        / max(1, len(checks))
    )

    result = {
        "generated": now(),
        "health_score": health,
        "checks": checks,
        "failed": failed,
        "git_dirty": bool(
            git_status["stdout"]
        ),
        "status":
            "HEALTHY"
            if not failed
            else "REPAIR_REQUIRED"
    }

    out = (
        STATE
        / "repair"
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
        )
        + "\n"
    )

    REPORTS.mkdir(
        parents=True,
        exist_ok=True
    )

    report = [
        "# Mikis13 AI City Repair Bot",
        "",
        f"Generated: {result['generated']}",
        "",
        f"Health: **{health}/100**",
        "",
        f"Status: **{result['status']}**",
        "",
        "## Checks",
        ""
    ]

    for item in checks:
        report.append(
            "- "
            + ("✅" if item["ok"] else "❌")
            + " "
            + item["name"]
        )

    if failed:

        report += [
            "",
            "## Required repair",
            ""
        ]

        for x in failed:
            report.append(
                f"- repair `{x}`"
            )

    (
        REPORTS
        / "repair-latest.md"
    ).write_text(
        "\n".join(report)
        + "\n"
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
