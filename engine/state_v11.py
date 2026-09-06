#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import json
import os
import tempfile
import hashlib

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "v11"

def utcnow():
    return datetime.now(
        timezone.utc
    ).isoformat()

def atomic_json(path, obj):
    path = Path(path)
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fd, tmp = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=".tmp-",
        text=True
    )

    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(
                obj,
                fh,
                indent=2
            )
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())

        os.replace(tmp, path)

    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def load_json(path, default=None):
    p = Path(path)

    if not p.exists():
        return default

    return json.loads(
        p.read_text(encoding="utf-8")
    )

def sha256_file(path):
    h = hashlib.sha256()

    with open(path, "rb") as fh:
        for chunk in iter(
            lambda: fh.read(1024 * 1024),
            b""
        ):
            h.update(chunk)

    return h.hexdigest()
