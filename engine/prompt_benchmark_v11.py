#!/usr/bin/env python3

from pathlib import Path
import argparse
import json

from state_v11 import (
    ROOT,
    STATE,
    atomic_json,
    utcnow
)

CASES = json.loads(
    (
        ROOT
        / "config"
        / "prompt-benchmark-cases-v11.json"
    ).read_text()
)["cases"]

def score_text(text):

    lower = text.lower()

    results = []

    for case in CASES:

        include_hits = {
            phrase:
            phrase.lower() in lower
            for phrase in case["must_include"]
        }

        forbidden_hits = {
            phrase:
            phrase.lower() in lower
            for phrase in case["must_not_include"]
        }

        score = (
            sum(include_hits.values())
            - 2 * sum(forbidden_hits.values())
        )

        results.append({
            "case": case["id"],
            "include": include_hits,
            "forbidden": forbidden_hits,
            "score": score
        })

    return results

if __name__ == "__main__":

    p = argparse.ArgumentParser()

    p.add_argument(
        "--prompt",
        default=str(
            ROOT
            / "prompts"
            / "MASTER-PROMPT-V10.md"
        )
    )

    args = p.parse_args()

    text = Path(
        args.prompt
    ).read_text(
        encoding="utf-8"
    )

    results = score_text(text)

    out = {
        "generated": utcnow(),
        "prompt": args.prompt,
        "cases": results,
        "total_score": sum(
            x["score"]
            for x in results
        )
    }

    atomic_json(
        STATE
        / "benchmarks"
        / "latest.json",
        out
    )

    print(
        json.dumps(
            out,
            indent=2
        )
    )
