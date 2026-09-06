#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "config" / "v13-policy.json").read_text())
SAFE = set(POLICY["safe_capabilities"])


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def inside_root(value: str) -> Path:
    p = (ROOT / value).resolve() if not Path(value).is_absolute() else Path(value).resolve()
    try:
        p.relative_to(ROOT.resolve())
    except ValueError:
        raise SystemExit("Path escapes repository root")
    return p


def validate_target(action: str, target: str) -> None:
    if action not in SAFE:
        raise SystemExit("Action blocked")
    if action in {"git-status", "git-diff-check", "shell-syntax", "json-validate", "file-sha256"}:
        p = inside_root(target)
        if action in {"shell-syntax", "json-validate", "file-sha256"} and not p.is_file():
            raise SystemExit("Target file does not exist")
        if action in {"git-status", "git-diff-check"} and not p.exists():
            raise SystemExit("Target path does not exist")
    elif action == "http-health":
        u = urlparse(target)
        if u.scheme != "https" or (u.hostname or "").lower() not in {x.lower() for x in POLICY["http_allow_hosts"]}:
            raise SystemExit("HTTP target host is not allow-listed HTTPS")
    elif action == "gh-pr-view":
        owner = re.escape(POLICY["allowed_github_owner"])
        if not re.fullmatch(rf"{owner}/[A-Za-z0-9_.-]+#[0-9]+", target):
            raise SystemExit("Invalid GitHub PR target")
    elif action == "gh-run-list":
        owner = re.escape(POLICY["allowed_github_owner"])
        if not re.fullmatch(rf"{owner}/[A-Za-z0-9_.-]+", target):
            raise SystemExit("Invalid GitHub repository target")


def command(action: str, target: str):
    if action == "git-status":
        return ["git", "-C", str(inside_root(target)), "status", "--short"]
    if action == "git-diff-check":
        return ["git", "-C", str(inside_root(target)), "diff", "--check"]
    if action == "shell-syntax":
        return ["bash", "-n", str(inside_root(target))]
    if action == "json-validate":
        return ["python", "-m", "json.tool", str(inside_root(target))]
    if action == "file-sha256":
        return ["sha256sum", str(inside_root(target))]
    if action == "http-health":
        return ["curl", "-L", "-sS", "-o", "/dev/null", "-w", "%{http_code}", "--connect-timeout", "8", "--max-time", "20", target]
    if action == "gh-pr-view":
        repo, number = target.split("#", 1)
        return ["gh", "pr", "view", number, "--repo", repo, "--json", "number,title,state,isDraft,mergeable"]
    if action == "gh-run-list":
        return ["gh", "run", "list", "--repo", target, "--limit", "10", "--json", "databaseId,name,status,conclusion,createdAt"]
    raise SystemExit("Unsupported action")


def execute(action: str, target: str) -> dict:
    validate_target(action, target)
    started = utcnow()
    try:
        p = subprocess.run(
            command(action, target),
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=int(POLICY["command_timeout_seconds"]),
            shell=False
        )
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as exc:
        rc = 124
        out = exc.stdout or ""
        err = (exc.stderr or "") + "\nTIMEOUT"
    if isinstance(out, bytes):
        out = out.decode(errors="replace")
    if isinstance(err, bytes):
        err = err.decode(errors="replace")
    return {
        "action": action,
        "target": target,
        "returncode": int(rc),
        "stdout": str(out)[-int(POLICY["max_stdout_bytes"]):],
        "stderr": str(err)[-int(POLICY["max_stderr_bytes"]):],
        "started_at": started,
        "finished_at": utcnow()
    }


def b64_result(result: dict) -> str:
    raw = json.dumps(result, separators=(",", ":"), sort_keys=True).encode()
    return base64.b64encode(raw).decode()


def local_once(node_id: str) -> int:
    from federation_v13 import claim, complete, init_state
    init_state()
    claimed = claim(node_id)
    if claimed.get("status") != "CLAIMED":
        print(json.dumps(claimed, indent=2))
        return 0
    job = claimed["job"]
    result = execute(job["action"], job["target"])
    record = complete(job["job_id"], node_id, job["lease"]["token"], b64_result(result))
    print(json.dumps(record, indent=2))
    return 0 if record["verified"] else 2


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("local-once")
    l.add_argument("--node", default="TERMUX-HOME-01")
    r = sub.add_parser("execute-remote")
    r.add_argument("--node", required=True)
    r.add_argument("--job-id", required=True)
    r.add_argument("--action", required=True)
    r.add_argument("--target", required=True)
    r.add_argument("--expected", default="200")
    args = p.parse_args()
    if args.cmd == "local-once":
        raise SystemExit(local_once(args.node))
    result = execute(args.action, args.target)
    print("MIKIS_JOB_ID=" + args.job_id)
    print("MIKIS_NODE=" + args.node)
    print("MIKIS_RESULT_B64=" + b64_result(result))


if __name__ == "__main__":
    main()
