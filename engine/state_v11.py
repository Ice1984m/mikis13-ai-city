#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import tempfile
import json
import os

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "v11"

def now():
    return datetime.now(
        timezone.utc
    ).isoformat()

def read_json(path, default):
    path = Path(path)

    if not path.exists():
        return default

    return json.loads(
        path.read_text()
    )

def atomic_json(path, obj):
    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fd, tmp = tempfile.mkstemp(
        dir=path.parent,
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

        os.replace(
            tmp,
            path
        )

    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
