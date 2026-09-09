import json
from pathlib import Path

config = json.loads(
    Path("config/virtual-workforce.json").read_text(
        encoding="utf-8"
    )
)

runtime = config["runtime"]

assert config["total_virtual_roles"] == 1_000_000
assert sum(config["roles"].values()) == 1_000_000

assert runtime["maximum_parallel_inspections"] == 10
assert runtime["maximum_active_mutation_jobs"] == 1
assert runtime["maximum_council_decisions_per_cycle"] == 1

for key in (
    "direct_main_write",
    "automatic_merge",
    "force_push",
    "blind_ai_shell_execution",
    "unknown_is_success"
):
    assert runtime[key] is False

assert config["community"][
    "external_repositories_are_read_only"
] is True

print("✅ V16-tests geslaagd")
