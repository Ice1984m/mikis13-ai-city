#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import contextlib
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "v13"
QUEUE = STATE / "jobs" / "queue.json"
NODE_STATE = STATE / "nodes" / "registry.json"
RESULTS = STATE / "results"
LOCKDIR = STATE / "locks" / "queue.lock"
OWNER_STOP = STATE / "OWNER_STOP"
SAFE_MODE = STATE / "SAFE_MODE"
POLICY = json.loads((ROOT / "config" / "v13-policy.json").read_text())
NODE_CONFIG = json.loads((ROOT / "config" / "nodes-v13.json").read_text())


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def load_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


@contextlib.contextmanager
def queue_lock(timeout: float = 8.0):
    LOCKDIR.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout
    while True:
        try:
            os.mkdir(LOCKDIR)
            (LOCKDIR / "owner").write_text(f"{os.getpid()} {utcnow()}\n")
            break
        except FileExistsError:
            try:
                age = time.time() - LOCKDIR.stat().st_mtime
                if age > 120:
                    shutil.rmtree(LOCKDIR, ignore_errors=True)
                    continue
            except FileNotFoundError:
                continue
            if time.monotonic() >= deadline:
                raise TimeoutError("queue lock timeout")
            time.sleep(0.05 + random.random() * 0.05)
    try:
        yield
    finally:
        shutil.rmtree(LOCKDIR, ignore_errors=True)


def init_state() -> None:
    for p in [QUEUE.parent, RESULTS, NODE_STATE.parent, LOCKDIR.parent, STATE / "incidents"]:
        p.mkdir(parents=True, exist_ok=True)
    if not QUEUE.exists():
        atomic_json(QUEUE, {"version": 13, "jobs": []})
    nodes = {"version": 13, "nodes": NODE_CONFIG["nodes"], "updated_at": utcnow()}
    atomic_json(NODE_STATE, nodes)


def node_by_id(node_id: str) -> dict:
    data = load_json(NODE_STATE, {"nodes": []})
    for node in data.get("nodes", []):
        if node.get("node_id") == node_id:
            return node
    raise SystemExit(f"Unknown node: {node_id}")


def validate_action(action: str) -> None:
    if action not in POLICY["safe_capabilities"]:
        raise SystemExit(f"Capability blocked: {action}")


def refresh_expired(data: dict) -> None:
    now = datetime.now(timezone.utc)
    max_attempts = int(POLICY["max_attempts"])
    for job in data.get("jobs", []):
        if job.get("state") != "CLAIMED" or not job.get("lease"):
            continue
        try:
            expires = datetime.fromisoformat(job["lease"]["expires_at"])
        except Exception:
            expires = now - timedelta(seconds=1)
        if expires <= now:
            job["last_error"] = "LEASE_EXPIRED"
            job["lease"] = None
            if int(job.get("attempts", 0)) >= max_attempts:
                job["state"] = "FAILED"
            else:
                job["state"] = "QUEUED"
            job["updated_at"] = utcnow()


def submit(action: str, target: str, expected: str, priority: int) -> dict:
    validate_action(action)
    if OWNER_STOP.exists():
        raise SystemExit("OWNER_STOP active")
    raw = f"{action}|{target}|{expected}".encode()
    fingerprint = hashlib.sha256(raw).hexdigest()[:24]
    with queue_lock():
        data = load_json(QUEUE, {"version": 13, "jobs": []})
        refresh_expired(data)
        for job in data["jobs"]:
            if job.get("fingerprint") == fingerprint and job.get("state") in {"QUEUED", "CLAIMED"}:
                return {"status": "DUPLICATE", "job": job}
        job = {
            "job_id": "JOB-" + uuid.uuid4().hex[:12],
            "fingerprint": fingerprint,
            "action": action,
            "target": target,
            "expected": str(expected),
            "priority": int(priority),
            "mutation": False,
            "state": "QUEUED",
            "attempts": 0,
            "lease": None,
            "created_at": utcnow(),
            "updated_at": utcnow()
        }
        data["jobs"].append(job)
        atomic_json(QUEUE, data)
    return {"status": "CREATED", "job": job}


def claim(node_id: str) -> dict:
    if OWNER_STOP.exists():
        return {"status": "STOPPED"}
    node = node_by_id(node_id)
    if node.get("status") != "HEALTHY":
        return {"status": "NODE_NOT_HEALTHY"}
    if node.get("mutation"):
        return {"status": "NODE_POLICY_INVALID"}
    capabilities = set(node.get("capabilities", []))
    with queue_lock():
        data = load_json(QUEUE, {"version": 13, "jobs": []})
        refresh_expired(data)
        candidates = [
            j for j in data["jobs"]
            if j.get("state") == "QUEUED" and j.get("action") in capabilities and not j.get("mutation")
        ]
        if not candidates:
            atomic_json(QUEUE, data)
            return {"status": "NO_JOB"}
        candidates.sort(key=lambda j: (int(j.get("priority", 0)), j.get("created_at", "")), reverse=True)
        job = candidates[0]
        token = uuid.uuid4().hex
        now = datetime.now(timezone.utc)
        job["attempts"] = int(job.get("attempts", 0)) + 1
        job["state"] = "CLAIMED"
        job["lease"] = {
            "node_id": node_id,
            "token": token,
            "claimed_at": now.isoformat(),
            "expires_at": (now + timedelta(seconds=int(POLICY["lease_seconds"]))).isoformat()
        }
        job["updated_at"] = utcnow()
        atomic_json(QUEUE, data)
        return {"status": "CLAIMED", "job": job}


def verify_result(job: dict, result: dict) -> tuple[bool, str]:
    required = {"returncode", "stdout", "stderr", "started_at", "finished_at", "action", "target"}
    if not required.issubset(result):
        return False, "MISSING_EVIDENCE"
    if result["action"] != job["action"] or result["target"] != job["target"]:
        return False, "JOB_RESULT_MISMATCH"
    if int(result["returncode"]) != 0:
        return False, "NONZERO_RETURN"
    action = job["action"]
    stdout = str(result.get("stdout", "")).strip()
    if action == "http-health" and stdout != str(job.get("expected", "200")):
        return False, "HTTP_STATUS_MISMATCH"
    if action == "file-sha256":
        value = stdout.split()[0] if stdout else ""
        if len(value) != 64 or any(c not in "0123456789abcdefABCDEF" for c in value):
            return False, "INVALID_SHA256_EVIDENCE"
    return True, "VERIFIED"


def complete(job_id: str, node_id: str, token: str, result_b64: str) -> dict:
    try:
        result = json.loads(base64.b64decode(result_b64).decode("utf-8"))
    except Exception as exc:
        raise SystemExit(f"Invalid result payload: {exc}")
    with queue_lock():
        data = load_json(QUEUE, {"version": 13, "jobs": []})
        refresh_expired(data)
        job = next((j for j in data["jobs"] if j.get("job_id") == job_id), None)
        if not job:
            raise SystemExit("Unknown job")
        lease = job.get("lease") or {}
        if job.get("state") != "CLAIMED":
            raise SystemExit(f"Job is not CLAIMED: {job.get('state')}")
        if lease.get("node_id") != node_id or lease.get("token") != token:
            raise SystemExit("Lease mismatch")
        ok, reason = verify_result(job, result)
        evidence_hash = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()
        record = {
            "job_id": job_id,
            "node_id": node_id,
            "verified": ok,
            "reason": reason,
            "evidence_hash": evidence_hash,
            "result": result,
            "verified_at": utcnow()
        }
        atomic_json(RESULTS / f"{job_id}.json", record)
        job["lease"] = None
        job["updated_at"] = utcnow()
        job["result_ref"] = f"state/v13/results/{job_id}.json"
        if ok:
            job["state"] = "VERIFIED"
        elif int(job.get("attempts", 0)) < int(POLICY["max_attempts"]):
            job["state"] = "QUEUED"
            job["last_error"] = reason
        else:
            job["state"] = "FAILED"
            job["last_error"] = reason
        atomic_json(QUEUE, data)
        return record


def status() -> dict:
    with queue_lock():
        data = load_json(QUEUE, {"version": 13, "jobs": []})
        refresh_expired(data)
        atomic_json(QUEUE, data)
    counts = {}
    for job in data.get("jobs", []):
        counts[job["state"]] = counts.get(job["state"], 0) + 1
    nodes = load_json(NODE_STATE, {"nodes": []}).get("nodes", [])
    regions = json.loads((ROOT / "config" / "regions-v13.json").read_text())["regions"]
    return {
        "mode": "OWNER_STOP" if OWNER_STOP.exists() else ("SAFE_MODE" if SAFE_MODE.exists() else "READ_ONLY"),
        "mutation_enabled": False,
        "jobs": counts,
        "nodes": [{"node_id": n["node_id"], "type": n["type"], "zone": n["zone"], "status": n["status"]} for n in nodes],
        "geographic_regions": regions
    }


def main() -> None:
    init_state()
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    s = sub.add_parser("submit")
    s.add_argument("--action", required=True)
    s.add_argument("--target", required=True)
    s.add_argument("--expected", default="200")
    s.add_argument("--priority", type=int, default=50)
    c = sub.add_parser("claim")
    c.add_argument("--node", required=True)
    d = sub.add_parser("complete")
    d.add_argument("--job", required=True)
    d.add_argument("--node", required=True)
    d.add_argument("--lease-token", required=True)
    d.add_argument("--result-b64", required=True)
    sub.add_parser("status")
    args = p.parse_args()
    if args.cmd == "init":
        print(json.dumps({"status": "INITIALIZED", "state": str(STATE)}, indent=2))
    elif args.cmd == "submit":
        print(json.dumps(submit(args.action, args.target, args.expected, args.priority), indent=2))
    elif args.cmd == "claim":
        print(json.dumps(claim(args.node), indent=2))
    elif args.cmd == "complete":
        print(json.dumps(complete(args.job, args.node, args.lease_token, args.result_b64), indent=2))
    else:
        print(json.dumps(status(), indent=2))


if __name__ == "__main__":
    main()
