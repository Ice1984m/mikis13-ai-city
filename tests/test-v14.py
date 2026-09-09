import json
from pathlib import Path
r=json.loads(Path("config/agent-registry.json").read_text())["agents"]
p=json.loads(Path("config/council-policy.json").read_text())
assert len(r)==1300 and len({a["id"] for a in r})==1300
assert sum(a["class"]=="inspector" for a in r)==200
assert sum(a["class"]=="repository_discoverer" for a in r)==100
assert sum(a["class"]=="repair_role" for a in r)==1000
assert p["maximum_active_mutation_jobs"]==1
for key in ("direct_main_write","automatic_merge","force_push","unknown_is_success","blind_ai_shell_execution"):
    assert p[key] is False
assert p["repair_workflow_names"]==["mikis13-safe-repair.yml"]
print("V14 policy and exact 1,300-agent registry: PASS")
