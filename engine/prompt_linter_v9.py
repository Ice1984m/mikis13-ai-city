#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path.home() / "mikis13-ai-city"

PROMPT = (
    ROOT
    / "prompts"
    / "MASTER-PROMPT-V9.md"
)

text = PROMPT.read_text(
    encoding="utf-8"
)

required = [
    "EVIDENCE",
    "PROVENANCE",
    "ROOT CAUSE",
    "ROLLBACK",
    "STOP_CONDITION",
    "UNKNOWN",
    "BOT BRANCH",
    "TGPT",
    "SELF-REVIEW",
    "COMPLEXITY",
    "CAPABILITY",
    "TERMUX"
]

missing = [
    word
    for word in required
    if word not in text
]

bad_patterns = [
    "blindly execute",
    "ignore failed tests",
    "force push main",
    "cannot be stopped by owner"
]

bad_found = [
    p
    for p in bad_patterns
    if p.lower()
    in text.lower()
]

result = {
    "required_missing":
        missing,

    "unsafe_patterns":
        bad_found,

    "pass":
        not missing
        and not bad_found
}

print(
    json.dumps(
        result,
        indent=2
    )
)

if not result["pass"]:
    raise SystemExit(2)
