#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import subprocess
import hashlib
import json

HOME = Path.home()
ROOT = HOME / "mikis13-ai-city"

STATE = ROOT / "state"
REPORTS = ROOT / "reports"

OWNER = "Ice1984m"

PARTICIPANTS = [
    "System Architect",
    "Testing Engineer",
    "Security Guardian",
    "Research Scout",
    "Inventor",
    "Creative Director",
    "Failure Analyst",
    "Reliability Engineer"
]

def now():
    return datetime.now(timezone.utc).isoformat()

def ensure_dirs():
    for name in [
        "city",
        "council",
        "jury",
        "learning",
        "decisions",
        "blueprints",
        "history",
        "metrics",
        "inbox"
    ]:
        (STATE / name).mkdir(parents=True, exist_ok=True)

    REPORTS.mkdir(parents=True, exist_ok=True)

def run(cmd):
    p = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    return (
        p.returncode,
        p.stdout.strip(),
        p.stderr.strip()
    )

def fingerprint(text):
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()[:16]

def github_snapshot():

    code, out, err = run([
        "gh",
        "repo",
        "list",
        OWNER,
        "--limit",
        "200",
        "--json",
        "name,description,url,isArchived,updatedAt"
    ])

    repos = []

    if code == 0:
        try:
            repos = json.loads(out)
        except Exception:
            repos = []

    code, out, err = run([
        "gh",
        "search",
        "prs",
        "--owner",
        OWNER,
        "--state",
        "open",
        "--limit",
        "100",
        "--json",
        "number,title,url,repository"
    ])

    prs = []

    if code == 0:
        try:
            prs = json.loads(out)
        except Exception:
            prs = []

    result = {
        "generated": now(),
        "repositories": repos,
        "open_pull_requests": prs
    }

    (
        STATE
        / "city"
        / "github-snapshot.json"
    ).write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
        + "\n",
        encoding="utf-8"
    )

    return result

def evolution_candidate():

    candidates = []

    evo = (
        HOME
        / "mikis13-evolution-engine"
        / "state"
        / "coordinator"
        / "latest.json"
    )

    if evo.exists():

        try:
            data = json.loads(
                evo.read_text(
                    encoding="utf-8"
                )
            )

            task = data.get(
                "selected_task"
            )

            if task:

                candidates.append({
                    "title":
                        task.get(
                            "title",
                            "Evolution task"
                        ),

                    "source":
                        "mikis13-evolution-engine",

                    "score":
                        int(
                            task.get(
                                "evidence_score",
                                60
                            )
                        )
                })

        except Exception:
            pass

    inbox = (
        STATE
        / "inbox"
        / "tasks.jsonl"
    )

    if inbox.exists():

        for line in inbox.read_text(
            encoding="utf-8"
        ).splitlines():

            try:

                item = json.loads(line)

                if item.get(
                    "status",
                    "NEW"
                ) == "NEW":

                    candidates.append({
                        "title":
                            item["title"],

                        "source":
                            "city-inbox",

                        "score":
                            int(
                                item.get(
                                    "priority",
                                    70
                                )
                            )
                    })

            except Exception:
                pass

    if not candidates:

        candidates.append({
            "title":
                "Improve Mikis13 coordination and reduce duplicate work",

            "source":
                "default",

            "score":
                50
        })

    candidates.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return candidates[0]

def perspective(role, candidate):

    result = {
        "role": role,
        "claim":
            "Proceed with the smallest measurable safe step.",

        "evidence": [
            "candidate-source:"
            + candidate["source"]
        ],

        "risk":
            "medium",

        "recommendation":
            "EXPERIMENT",

        "confidence":
            70,

        "impact":
            65
    }

    if "Architect" in role:

        result.update({
            "claim":
                "Reuse or improve existing architecture before creating another repository.",

            "recommendation":
                "IMPROVE_EXISTING",

            "confidence":
                88,

            "impact":
                82
        })

    elif "Testing" in role:

        result.update({
            "claim":
                "Acceptance tests must be defined before implementation.",

            "recommendation":
                "EXPERIMENT",

            "confidence":
                92,

            "impact":
                80
        })

    elif "Security" in role:

        result.update({
            "claim":
                "Security gate must pass before merge.",

            "risk":
                "high",

            "recommendation":
                "EXPERIMENT",

            "confidence":
                94,

            "impact":
                88
        })

    elif "Research" in role:

        result.update({
            "claim":
                "Inspect existing repositories and open-source options before implementation.",

            "recommendation":
                "RESEARCH",

            "confidence":
                86,

            "impact":
                75
        })

    elif "Inventor" in role:

        result.update({
            "claim":
                "Build one bounded prototype that can prove or disprove the idea.",

            "recommendation":
                "EXPERIMENT",

            "confidence":
                80,

            "impact":
                90
        })

    elif "Creative" in role:

        result.update({
            "claim":
                "Generate one alternative solution focused on user value.",

            "recommendation":
                "EXPERIMENT",

            "confidence":
                76,

            "impact":
                75
        })

    elif "Failure" in role:

        result.update({
            "claim":
                "Compare this approach with previous failures before repeating it.",

            "recommendation":
                "RESEARCH",

            "confidence":
                86,

            "impact":
                78
        })

    elif "Reliability" in role:

        result.update({
            "claim":
                "Healthcheck and rollback must exist before deployment.",

            "recommendation":
                "EXPERIMENT",

            "confidence":
                91,

            "impact":
                84
        })

    return result

def debate(candidate):

    messages = [
        perspective(
            role,
            candidate
        )
        for role in PARTICIPANTS
    ]

    counts = Counter(
        x["recommendation"]
        for x in messages
    )

    ranking = counts.most_common()

    if (
        len(ranking) > 1
        and (
            ranking[0][1]
            - ranking[1][1]
        ) <= 2
    ):

        messages.append({
            "role":
                "Vega - Independent Second Judge",

            "claim":
                "Council disagreement is meaningful. Use a bounded experiment instead of immediate implementation.",

            "evidence": [
                "jury-disagreement"
            ],

            "risk":
                "medium",

            "recommendation":
                "EXPERIMENT",

            "confidence":
                90,

            "impact":
                80
        })

    return messages

def jury(messages):

    scores = Counter()

    for item in messages:

        score = (
            item["confidence"]
            / 100
        )

        score *= (
            item["impact"]
            / 100
        )

        scores[
            item["recommendation"]
        ] += score

    ranked = scores.most_common()

    winner = (
        ranked[0][0]
        if ranked
        else "RESEARCH"
    )

    return {
        "scores":
            dict(scores),

        "winner":
            winner
    }

def judge(candidate, messages, jury_result):

    decision = jury_result[
        "winner"
    ]

    # No direct irreversible implementation.
    if decision == "IMPLEMENT":
        decision = "EXPERIMENT"

    return {
        "generated":
            now(),

        "supreme_judge":
            "Astra",

        "right_hand":
            "Orion",

        "second_judge":
            "Vega",

        "candidate":
            candidate,

        "decision":
            decision,

        "discussion_rounds":
            (
                2
                if len(messages)
                > len(PARTICIPANTS)
                else 1
            ),

        "requirements": [
            "duplicate check",
            "tests",
            "security scan",
            "healthcheck",
            "rollback plan"
        ]
    }

def make_blueprint(
    candidate,
    decision
):

    blueprint = {
        "version":
            1,

        "created":
            now(),

        "status":
            "RESEARCH",

        "title":
            candidate["title"],

        "decision":
            decision["decision"],

        "problem":
            candidate["title"],

        "hypothesis":
            "A bounded coordinated experiment can produce measurable improvement.",

        "steps": [
            "inspect existing repositories",
            "inspect open PRs",
            "inspect previous failures",
            "define measurable success metric",
            "create smallest prototype",
            "write automated tests",
            "run security scan",
            "run healthcheck",
            "compare actual result",
            "record learning"
        ],

        "rollback_plan": [
            "do not merge failing work",
            "close invalid bot PR",
            "restore previous tested state if deployment regresses"
        ],

        "success_condition":
            "Measured improvement while tests, security and health remain green."
    }

    path = (
        STATE
        / "blueprints"
        / (
            fingerprint(
                candidate["title"]
            )
            + ".json"
        )
    )

    path.write_text(
        json.dumps(
            blueprint,
            indent=2,
            ensure_ascii=False
        )
        + "\n",
        encoding="utf-8"
    )

    return path

def update_learning(
    decision,
    jury_result
):

    path = (
        STATE
        / "learning"
        / "patterns.json"
    )

    try:

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except Exception:

        data = {
            "cycles":
                0,

            "decisions":
                {}
        }

    data["cycles"] += 1

    choice = decision[
        "decision"
    ]

    data["decisions"][
        choice
    ] = (
        data["decisions"].get(
            choice,
            0
        )
        + 1
    )

    data[
        "latest_jury_scores"
    ] = jury_result[
        "scores"
    ]

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False
        )
        + "\n",
        encoding="utf-8"
    )

def append_ledger(record):

    path = (
        STATE
        / "city"
        / "ledger.jsonl"
    )

    with path.open(
        "a",
        encoding="utf-8"
    ) as fh:

        fh.write(
            json.dumps(
                record,
                ensure_ascii=False
            )
            + "\n"
        )

def make_report(
    candidate,
    messages,
    jury_result,
    decision,
    blueprint_path,
    snapshot
):

    lines = [
        "# Mikis13 AI City",
        "",
        f"Generated: {now()}",
        "",
        "## Selected problem",
        "",
        candidate["title"],
        "",
        "## Leadership",
        "",
        "- Astra — Supreme Judge",
        "- Orion — Chief Coordinator",
        "- Vega — Independent Second Judge",
        "",
        "## Council"
    ]

    for m in messages:

        lines.extend([
            "",
            f"### {m['role']}",
            "",
            m["claim"],
            "",
            (
                "- recommendation: "
                f"`{m['recommendation']}`"
            ),
            (
                "- confidence: "
                f"{m['confidence']}%"
            ),
            (
                "- expected impact: "
                f"{m['impact']}%"
            )
        ])

    lines.extend([
        "",
        "## Jury",
        "",
        (
            "Winner: "
            f"**{jury_result['winner']}**"
        ),
        "",
        "## Astra decision",
        "",
        f"**{decision['decision']}**",
        "",
        (
            "Discussion rounds: "
            f"{decision['discussion_rounds']}"
        ),
        "",
        "## Blueprint",
        "",
        (
            "`"
            + str(
                blueprint_path.relative_to(
                    ROOT
                )
            )
            + "`"
        ),
        "",
        "## GitHub",
        "",
        (
            "- repositories observed: "
            f"{len(snapshot['repositories'])}"
        ),
        (
            "- open PRs observed: "
            f"{len(snapshot['open_pull_requests'])}"
        ),
        "",
        "## Rule",
        "",
        "Evidence beats opinion. Results beat endless discussion.",
        ""
    ])

    (
        REPORTS
        / "city-latest.md"
    ).write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

def main():

    ensure_dirs()

    print(
        "🏙️ GitHub snapshot..."
    )

    snapshot = github_snapshot()

    print(
        "Repositories:",
        len(
            snapshot[
                "repositories"
            ]
        )
    )

    print(
        "Open PRs:",
        len(
            snapshot[
                "open_pull_requests"
            ]
        )
    )

    candidate = evolution_candidate()

    print(
        "Selected candidate:",
        candidate["title"]
    )

    messages = debate(
        candidate
    )

    jury_result = jury(
        messages
    )

    decision = judge(
        candidate,
        messages,
        jury_result
    )

    blueprint_path = make_blueprint(
        candidate,
        decision
    )

    record = {
        "timestamp":
            now(),

        "candidate":
            candidate,

        "messages":
            messages,

        "jury":
            jury_result,

        "decision":
            decision,

        "blueprint":
            str(
                blueprint_path
            )
    }

    append_ledger(
        record
    )

    update_learning(
        decision,
        jury_result
    )

    (
        STATE
        / "decisions"
        / "latest.json"
    ).write_text(
        json.dumps(
            record,
            indent=2,
            ensure_ascii=False
        )
        + "\n",
        encoding="utf-8"
    )

    make_report(
        candidate,
        messages,
        jury_result,
        decision,
        blueprint_path,
        snapshot
    )

    print()
    print(
        "⚖️ Jury:",
        jury_result["winner"]
    )

    print(
        "👑 Astra:",
        decision["decision"]
    )

    print(
        "📘 Blueprint:",
        blueprint_path
    )

if __name__ == "__main__":
    main()
