#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "config" / "automation-blueprints-301-350-v11.json"

rows = [

# 301-305 Recovery Verification

(301, "Recovery Verification Contract",
 "recovery",
 "Define the exact observable condition proving that the original failure has disappeared.",
 "healthcheck", 100, 24, 14),

(302, "Before/After Evidence Snapshot",
 "recovery",
 "Capture evidence before a repair and compare it with evidence after the repair.",
 "evidence", 98, 24, 14),

(303, "Original Failure Replay",
 "recovery",
 "Re-run the original failing command, workflow check or health probe after repair.",
 "tests", 100, 30, 18),

(304, "False Recovery Detector",
 "recovery",
 "Reject repairs that only hide a symptom while the original failure remains reproducible.",
 "healthcheck", 100, 32, 18),

(305, "Recovery Proof Bundle",
 "recovery",
 "Store failure evidence, repair commit, tests, healthcheck and verification result together.",
 "evidence", 96, 26, 15),

# 306-310 Canonical Job Queue

(306, "Canonical Job State Machine",
 "job_queue",
 "Represent jobs as NEW, EVIDENCE_READY, READY, ACTIVE, BLOCKED, VERIFIED, FAILED or CLOSED.",
 "policy", 100, 32, 20),

(307, "Atomic Job Claim",
 "job_queue",
 "Allow only one worker group to claim a mutation job using atomic leases.",
 "reliability", 99, 34, 20),

(308, "Job Lease Expiration",
 "job_queue",
 "Automatically release abandoned jobs after a bounded lease expires.",
 "recovery", 96, 28, 18),

(309, "Job Deduplication Fingerprint",
 "job_queue",
 "Prevent creation of multiple active jobs describing the same repository problem.",
 "evidence", 98, 32, 20),

(310, "Job Priority Recalibration",
 "job_queue",
 "Recalculate priority when evidence, failures, urgency or dependency state changes.",
 "learning", 94, 32, 20),

# 311-315 Execution Engine

(311, "Bounded Execution Planner",
 "execution",
 "Translate one selected job into explicit deterministic execution stages.",
 "policy", 100, 36, 22),

(312, "Mutation Authorization Gate",
 "execution",
 "Permit repository mutation only after required gates are present and valid.",
 "security", 100, 30, 18),

(313, "Command Allowlist Runner",
 "execution",
 "Allow only deterministic predefined commands instead of arbitrary AI-generated shell.",
 "security", 100, 38, 24),

(314, "Execution Checkpoint Manager",
 "execution",
 "Create known-good state before any allowed mutation begins.",
 "rollback", 100, 34, 20),

(315, "Execution Result Normalizer",
 "execution",
 "Convert command, test, security and healthcheck results into one structured result format.",
 "learning", 96, 32, 20),

# 316-320 Regression Memory

(316, "Failure Signature Canonicalizer V2",
 "regression_memory",
 "Normalize recurring failures into stable signatures independent of noisy timestamps.",
 "learning", 99, 36, 24),

(317, "Regression Requirement Register",
 "regression_memory",
 "Require every confirmed recurring failure to gain a regression prevention requirement.",
 "tests", 100, 26, 16),

(318, "Regression Test Linker",
 "regression_memory",
 "Link a confirmed failure signature to the test that prevents recurrence.",
 "tests", 100, 32, 20),

(319, "Recurring Failure Escalator",
 "regression_memory",
 "Stop identical repair attempts after the failure limit and escalate to deeper diagnosis.",
 "reliability", 100, 28, 18),

(320, "Successful Fix Retrieval V2",
 "regression_memory",
 "Search verified historical fixes before inventing a new repair approach.",
 "learning", 97, 34, 22),

# 321-325 Worker Reputation

(321, "Worker Outcome Ledger",
 "worker_reputation",
 "Record whether each worker recommendation resulted in verified improvement.",
 "learning", 95, 30, 18),

(322, "Worker Accuracy Score",
 "worker_reputation",
 "Calculate worker quality from verified results instead of message volume.",
 "learning", 98, 32, 20),

(323, "Worker Domain Competence",
 "worker_reputation",
 "Track which worker families perform best for testing, reliability, GitHub, security and architecture.",
 "learning", 96, 34, 20),

(324, "Worker Cooldown Engine",
 "worker_reputation",
 "Reduce selection probability after repeated failed recommendations.",
 "reliability", 94, 28, 18),

(325, "Worker Promotion Gate",
 "worker_reputation",
 "Increase worker responsibility only after repeated verified successful outcomes.",
 "evidence", 96, 30, 18),

# 326-330 Blueprint Maturity

(326, "Blueprint Maturity State Machine",
 "maturity",
 "Enforce IDEA through PROVEN lifecycle transitions with explicit gate requirements.",
 "policy", 100, 34, 20),

(327, "Prototype Promotion Gate",
 "maturity",
 "Require reproducible prototype evidence before moving PLANNED to PROTOTYPE.",
 "tests", 97, 26, 16),

(328, "Verified Capability Gate",
 "maturity",
 "Require deterministic tests and health evidence before marking capability VERIFIED.",
 "healthcheck", 100, 28, 18),

(329, "Deployed Capability Verification",
 "maturity",
 "Confirm behavior in the deployed environment before DEPLOYED is accepted.",
 "healthcheck", 100, 30, 18),

(330, "Proven Capability Evidence",
 "maturity",
 "Require repeated real-world successful use before promoting DEPLOYED to PROVEN.",
 "evidence", 100, 28, 18),

# 331-335 Dependency Graph

(331, "Repository Dependency Graph V2",
 "dependency_graph",
 "Model repositories, workflows, domains, APIs and deployment relationships.",
 "evidence", 98, 42, 28),

(332, "Change Impact Propagation",
 "dependency_graph",
 "Predict which dependent repositories or services may be affected by a proposed change.",
 "evidence", 97, 42, 28),

(333, "Dependency Critical Path",
 "dependency_graph",
 "Identify the order in which blocked dependencies must be repaired.",
 "planning", 98, 38, 24),

(334, "Single Point Of Failure Finder",
 "dependency_graph",
 "Detect critical components that lack fallback, redundancy or recovery.",
 "reliability", 98, 36, 22),

(335, "Dependency Drift Monitor",
 "dependency_graph",
 "Detect when observed repository relationships differ from the stored system map.",
 "evidence", 94, 36, 22),

# 336-340 Prompt Benchmark

(336, "Historical Prompt Benchmark Corpus",
 "prompt_benchmark",
 "Store sanitized historical engineering cases used to evaluate prompt changes.",
 "tests", 96, 34, 20),

(337, "Prompt Behavioral Contract",
 "prompt_benchmark",
 "Define required safety, evidence and usefulness behaviors for every benchmark case.",
 "tests", 100, 30, 18),

(338, "Prompt Candidate Comparator",
 "prompt_benchmark",
 "Compare current and proposed prompts on the same benchmark cases.",
 "tests", 98, 40, 24),

(339, "Prompt Regression Rejector",
 "prompt_benchmark",
 "Reject prompt changes that reduce safety, evidence quality or successful task completion.",
 "tests", 100, 34, 20),

(340, "Prompt Improvement Evidence",
 "prompt_benchmark",
 "Require measurable benchmark improvement before accepting a prompt revision.",
 "evidence", 99, 32, 20),

# 341-345 Research Factory

(341, "Existing Solution Scout",
 "research_factory",
 "Search existing Mikis13 repositories before proposing new implementation.",
 "reuse", 100, 28, 16),

(342, "Upstream Open Source Scout",
 "research_factory",
 "Find relevant upstream or open-source implementations suitable for legal reuse.",
 "reuse", 96, 34, 20),

(343, "License Provenance Gate",
 "research_factory",
 "Block code reuse when license or provenance cannot be established.",
 "security", 100, 30, 18),

(344, "Solution Comparison Matrix",
 "research_factory",
 "Compare reuse, rewrite and new implementation by risk, complexity and maintenance.",
 "evidence", 97, 34, 20),

(345, "Research To Job Converter",
 "research_factory",
 "Turn the highest-confidence research result into one bounded canonical job.",
 "planning", 98, 32, 18),

# 346-350 Control Tower

(346, "Control Tower Status Model",
 "control_tower",
 "Expose jobs, evidence, gates, workers, failures and system mode in one structured status object.",
 "observability", 99, 34, 20),

(347, "Control Tower Health Summary",
 "control_tower",
 "Display repository and automation health without hiding UNKNOWN states.",
 "observability", 100, 32, 18),

(348, "Control Tower Active Job View",
 "control_tower",
 "Show the one active mutation job and why it was selected.",
 "observability", 96, 26, 15),

(349, "Control Tower Recovery View",
 "control_tower",
 "Display checkpoints, failed attempts, rollback and recovery verification.",
 "observability", 97, 30, 18),

(350, "Control Tower Owner Controls",
 "control_tower",
 "Expose clear owner-controlled start, stop and safe-mode state without autonomous resistance.",
 "policy", 100, 26, 16)
]

blueprints = []

for (
    ident,
    name,
    domain,
    goal,
    gate,
    impact,
    complexity,
    maintenance
) in rows:

    blueprints.append({
        "id": ident,
        "name": name,
        "domain": domain,
        "owner": "AI City V11 Execution Core",
        "goal": goal,
        "gate": gate,
        "status": "PLANNED",
        "expected_impact": impact,
        "complexity": complexity,
        "maintenance_cost": maintenance,
        "evidence_score": 45,
        "risk": 20,
        "existing_repo_required_first": True,
        "new_repository_required": False,
        "human_override_required": True,
        "execution_authorized": False,
        "source_version": "V11"
    })

assert len(blueprints) == 50
assert [x["id"] for x in blueprints] == list(range(301,351))

OUT.write_text(
    json.dumps({
        "version": 11,
        "range": "301-350",
        "count": 50,
        "blueprints": blueprints
    }, indent=2) + "\n",
    encoding="utf-8"
)

print("✅ V11 blueprints 301-350:", len(blueprints))
