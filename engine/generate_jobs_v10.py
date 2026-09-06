#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

jobs = [
("Verify previous repair", "Prove the original failure disappeared after a repair."),
("Create regression guard", "Turn a confirmed recurring failure into a deterministic regression test."),
("Investigate failed Actions run", "Collect failed job and step evidence before proposing a fix."),
("Reduce workflow permissions", "Find and reduce unnecessary GitHub workflow permissions."),
("Split risky dependency upgrade", "Separate security fixes from breaking framework migrations."),
("Detect duplicate PR", "Compare overlapping pull requests and select one continuation path."),
("Detect duplicate repository", "Find repositories solving the same problem before creating another."),
("Repair documentation drift", "Update instructions only after verifying current behavior."),
("Verify public website route", "Confirm page, assets, links and expected content."),
("Verify DNS and HTTPS", "Check domain resolution, TLS and public HTTP behavior."),
("Termux environment repair", "Check packages, PATH, TMPDIR, storage access, gh and Python."),
("Android scheduler audit", "Detect fragile cron assumptions under Android background restrictions."),
("Repository health score", "Create evidence-backed health status, not a cosmetic score."),
("Find missing tests", "Identify high-risk changed code without direct validation."),
("Create minimal reproduction", "Reduce a failure to the smallest reproducible case."),
("Generate rollback plan", "Create deterministic rollback steps before risky changes."),
("Check artifact integrity", "Verify artifact hashes and source provenance."),
("Check release readiness", "Require green tests, security, health and rollback."),
("Post deployment verify", "Test actual public behavior after a deployment."),
("Detect stale bot branch", "Find old completed bot branches safe for later cleanup."),
("Find architecture drift", "Compare current structure with intended repository ownership."),
("Reduce complexity", "Find code or automation that can be removed or consolidated."),
("Find intelligence theater", "Detect bots or scoring mechanisms producing activity without decision improvement."),
("Validate blueprint impact", "Compare expected impact with actual measurable outcome."),
("Calibrate worker reliability", "Measure which worker recommendations resulted in successful outcomes."),
("Calibrate prompt quality", "Benchmark prompt changes against historical cases."),
("Find broken command example", "Test documentation commands safely."),
("Build service dependency map", "Map repository, workflow, domain and deployment dependencies."),
("Find single point of failure", "Identify components without fallback or recovery."),
("Backup restore drill", "Verify a backup can restore known-good state."),
("Detect silent degradation", "Find worsening operational state without explicit failure."),
("Reconcile local GitHub state", "Safely compare local branch and remote state."),
("Analyze recurring failure", "Search failure memory for repeat signatures."),
("Find upstream reusable solution", "Search existing open-source or upstream implementation before rebuilding."),
("Analyze repository maintenance cost", "Estimate recurring maintenance burden."),
("Find feature with no evidence", "Flag development not connected to user value or reliability."),
("Generate runbook", "Document verified recovery actions."),
("Generate incident timeline", "Create evidence-backed incident sequence."),
("Detect evidence expiration", "Mark stale evidence before decisions."),
("Check LAB claim accuracy", "Ensure public claims match verified status."),
("Prepare bounded repair PR", "Create one focused bot-branch change after required gates."),
("Check changed surface risk", "Estimate impact from the files and systems touched."),
("Find unused automation", "Identify jobs with no useful result over repeated cycles."),
("Check scheduler redundancy", "Ensure important monitoring has more than one reliable trigger path."),
("Optimize API requests", "Reduce redundant GitHub queries."),
("Optimize Termux load", "Reduce CPU, memory and battery pressure."),
("Find capability gap", "Compare desired capability with proven capability."),
("Generate next experiment", "Select a reversible experiment for an unresolved assumption."),
("Stop low-value work", "Pause work when evidence does not justify further development."),
("Architecture self-review", "Review capability, risk, complexity, reuse and owner control.")
]

out = []

for i, (name, goal) in enumerate(jobs, start=1):
    out.append({
        "job_archetype_id": f"J{i:03d}",
        "name": name,
        "goal": goal,
        "status": "AVAILABLE",
        "maximum_concurrent_instances": 1,
        "requires_evidence": True,
        "requires_rollback_for_mutation": True,
        "direct_main": False,
        "auto_merge": False
    })

assert len(out) == 50

(ROOT / "config" / "priority-jobs-50-v10.json").write_text(
    json.dumps({
        "version": 10,
        "count": 50,
        "jobs": out
    }, indent=2) + "\n",
    encoding="utf-8"
)

print("✅ Priority job archetypes:", len(out))
