#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import tempfile
import time

ROOT = Path.home() / "mikis13-ai-city"
STATE = ROOT / "state"

def now():
    return datetime.now(timezone.utc).isoformat()

def atomic_write(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    content = json.dumps(
        data,
        indent=2,
        ensure_ascii=False
    ) + "\n"

    fd, tmp = tempfile.mkstemp(
        prefix=path.name + ".",
        dir=str(path.parent)
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

        os.replace(tmp, path)

    finally:
        try:
            if os.path.exists(tmp):
                os.unlink(tmp)
        except Exception:
            pass

def safe_read(path: Path, default=None):
    try:
        return json.loads(
            path.read_text(encoding="utf-8")
        )
    except Exception:
        return default

def fingerprint(text):
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()[:20]

def checkpoint(label):
    payload = {
        "created": now(),
        "label": label,
        "files": {}
    }

    candidates = [
        STATE / "jobs/active.json",
        STATE / "workers/assignment.json",
        STATE / "decisions/latest.json",
        STATE / "heartbeat/latest.json"
    ]

    for path in candidates:
        if path.exists():
            try:
                payload["files"][
                    str(path.relative_to(ROOT))
                ] = safe_read(path, {})
            except Exception:
                pass

    name = (
        datetime.now(
            timezone.utc
        ).strftime("%Y%m%d-%H%M%S")
        + "-"
        + fingerprint(label)
        + ".json"
    )

    out = (
        STATE
        / "checkpoints"
        / name
    )

    atomic_write(out, payload)

    atomic_write(
        STATE / "checkpoints/latest.json",
        payload
    )

    return out

def create_transaction(name, idempotency_key):
    tx = {
        "created": now(),
        "updated": now(),
        "name": name,
        "idempotency_key": idempotency_key,
        "status": "STARTED"
    }

    out = (
        STATE
        / "transactions"
        / f"{idempotency_key}.json"
    )

    existing = safe_read(out, None)

    if existing and existing.get("status") == "DONE":
        return existing, True

    atomic_write(out, tx)

    return tx, False

def finish_transaction(idempotency_key, result):
    out = (
        STATE
        / "transactions"
        / f"{idempotency_key}.json"
    )

    tx = safe_read(out, {})

    tx.update({
        "updated": now(),
        "status": "DONE",
        "result": result
    })

    atomic_write(out, tx)

def lease_job(job_id, worker):
    leases = STATE / "leases"
    leases.mkdir(parents=True, exist_ok=True)

    path = leases / f"{job_id}.json"

    current = safe_read(path, None)

    now_ts = int(time.time())

    if current:
        expires = int(
            current.get(
                "expires_unix",
                0
            )
        )

        if expires > now_ts:
            return {
                "acquired": False,
                "lease": current
            }

    lease = {
        "job_id": job_id,
        "worker": worker,
        "created": now(),
        "expires_unix": now_ts + 1800
    }

    atomic_write(path, lease)

    return {
        "acquired": True,
        "lease": lease
    }

def clean_expired_leases():
    lease_dir = STATE / "leases"

    lease_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    now_ts = int(time.time())

    removed = []

    for path in lease_dir.glob("*.json"):
        data = safe_read(path, {})

        if int(
            data.get(
                "expires_unix",
                0
            )
        ) <= now_ts:
            try:
                path.unlink()
                removed.append(
                    path.name
                )
            except Exception:
                pass

    return removed

def main():
    removed = clean_expired_leases()

    result = {
        "generated": now(),
        "atomic_state": True,
        "expired_leases_removed": removed
    }

    atomic_write(
        STATE / "recovery/resilience-status.json",
        result
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )

if __name__ == "__main__":
    main()
