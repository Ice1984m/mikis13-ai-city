#!/usr/bin/env python3

from pathlib import Path
from collections import Counter
import json

ROOT = (
    Path.home()
    / "mikis13-ai-city"
)

LEDGER = (
    ROOT
    / "state"
    / "city"
    / "ledger.jsonl"
)

OUT = (
    ROOT
    / "state"
    / "learning"
    / "prompt-feedback.json"
)

decisions = []
recommendations = []

if LEDGER.exists():

    for line in LEDGER.read_text(
        encoding="utf-8"
    ).splitlines():

        try:

            item = json.loads(
                line
            )

            decisions.append(
                item[
                    "decision"
                ][
                    "decision"
                ]
            )

            for msg in item.get(
                "messages",
                []
            ):

                rec = msg.get(
                    "recommendation"
                )

                if rec:
                    recommendations.append(
                        rec
                    )

        except Exception:
            pass

result = {
    "cycles":
        len(decisions),

    "decision_distribution":
        dict(
            Counter(
                decisions
            )
        ),

    "recommendation_distribution":
        dict(
            Counter(
                recommendations
            )
        ),

    "learning_rule":
        (
            "Improve prompts from measured outcomes, "
            "not from longer prompts alone."
        )
}

OUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

OUT.write_text(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )
    + "\n",
    encoding="utf-8"
)

print(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )
)
