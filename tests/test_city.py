#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = (
    Path.home()
    / "mikis13-ai-city"
)

org = json.loads(
    (
        ROOT
        / "config"
        / "organization.json"
    ).read_text()
)

assert (
    org[
        "discussion"
    ][
        "maximum_rounds"
    ]
    == 2
)

assert (
    org[
        "execution"
    ][
        "maximum_active_projects"
    ]
    == 1
)

assert (
    org[
        "execution"
    ][
        "automatic_merge"
    ]
    is False
)

assert (
    org[
        "execution"
    ][
        "security_scan_required"
    ]
    is True
)

providers = json.loads(
    (
        ROOT
        / "config"
        / "providers.json"
    ).read_text()
)

assert (
    providers[
        "maximum_external_calls_per_cycle"
    ]
    == 0
)

for name, cfg in (
    providers[
        "providers"
    ].items()
):

    if name != "internal":
        assert (
            cfg["enabled"]
            is False
        )

print(
    "✅ AI City policy tests PASS"
)
