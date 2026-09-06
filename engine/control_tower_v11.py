#!/usr/bin/env python3

from pathlib import Path
import html
import json

from state_v11 import (
    ROOT,
    STATE,
    load_json,
    utcnow
)

OUT = (
    ROOT
    / "public"
    / "control-tower"
    / "index.html"
)

queue = load_json(
    STATE
    / "jobs"
    / "queue.json",
    {
        "jobs": []
    }
)

research = load_json(
    STATE
    / "research"
    / "latest.json",
    {}
)

reputation = load_json(
    STATE
    / "reputation"
    / "workers.json",
    {
        "workers": {}
    }
)

maturity = load_json(
    STATE
    / "maturity"
    / "blueprints.json",
    {
        "blueprints": {}
    }
)

recovery_dir = (
    STATE
    / "recovery"
)

recovery_count = (
    len(
        list(
            recovery_dir.glob("*.json")
        )
    )
    if recovery_dir.exists()
    else 0
)

active_jobs = [
    j
    for j in queue.get(
        "jobs",
        []
    )
    if j.get("state") == "ACTIVE"
]

ready_jobs = [
    j
    for j in queue.get(
        "jobs",
        []
    )
    if j.get("state") == "READY"
]

failed_jobs = [
    j
    for j in queue.get(
        "jobs",
        []
    )
    if j.get("state") == "FAILED"
]

maturity_counts = {}

for row in maturity.get(
    "blueprints",
    {}
).values():

    state = row.get(
        "state",
        "UNKNOWN"
    )

    maturity_counts[state] = (
        maturity_counts.get(
            state,
            0
        )
        + 1
    )

mode = (
    "OWNER_STOP"
    if (
        STATE
        / "OWNER_STOP"
    ).exists()
    else "ENABLED"
)

def card(title, value, note=""):
    return f"""
    <div class="card">
      <small>{html.escape(title)}</small>
      <strong>{html.escape(str(value))}</strong>
      <p>{html.escape(note)}</p>
    </div>
    """

cards = "".join([
    card(
        "SYSTEM MODE",
        mode,
        "Owner control remains authoritative"
    ),
    card(
        "ACTIVE JOBS",
        len(active_jobs),
        "Maximum mutation jobs: 1"
    ),
    card(
        "READY JOBS",
        len(ready_jobs),
        "Evidence-backed work waiting"
    ),
    card(
        "FAILED JOBS",
        len(failed_jobs),
        "Requires diagnosis or escalation"
    ),
    card(
        "RESEARCH SIGNALS",
        len(
            research.get(
                "signals",
                []
            )
        ),
        "Read-only GitHub observations"
    ),
    card(
        "RECOVERY PROOFS",
        recovery_count,
        "Verification evidence bundles"
    ),
    card(
        "WORKERS SCORED",
        len(
            reputation.get(
                "workers",
                {}
            )
        ),
        "Only real outcomes influence reputation"
    ),
    card(
        "PROVEN BLUEPRINTS",
        maturity_counts.get(
            "PROVEN",
            0
        ),
        "PLANNED is not PROVEN"
    )
])

html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport"
      content="width=device-width,initial-scale=1">

<title>Mikis13 AI City V11 Control Tower</title>

<style>

* {{
    box-sizing:border-box;
}}

body {{
    margin:0;
    background:
      radial-gradient(circle at top,
      #24103f 0,
      #080811 50%,
      #020205 100%);
    color:#eef;
    font-family:
      system-ui,
      -apple-system,
      sans-serif;
}}

main {{
    max-width:1400px;
    margin:auto;
    padding:60px 24px;
}}

h1 {{
    font-size:clamp(
      3rem,
      8vw,
      7rem
    );
    margin:0;
}}

h1 span {{
    color:#b46cff;
}}

.subtitle {{
    opacity:.75;
    max-width:850px;
    font-size:1.1rem;
}}

.grid {{
    display:grid;
    grid-template-columns:
      repeat(
        auto-fit,
        minmax(220px,1fr)
      );
    gap:18px;
    margin-top:40px;
}}

.card {{
    padding:24px;
    border-radius:20px;
    border:
      1px solid
      rgba(180,108,255,.45);
    background:
      rgba(15,10,30,.82);
    box-shadow:
      0 0 30px
      rgba(120,60,255,.10);
}}

.card small {{
    opacity:.7;
}}

.card strong {{
    display:block;
    margin-top:8px;
    font-size:2.1rem;
    color:#c88cff;
}}

.panel {{
    margin-top:32px;
    padding:24px;
    border-radius:20px;
    background:#0d0b16;
    border:
      1px solid
      rgba(80,190,255,.25);
}}

pre {{
    white-space:pre-wrap;
    overflow-wrap:anywhere;
}}

footer {{
    margin-top:50px;
    opacity:.6;
}}

</style>
</head>

<body>

<main>

<p>MIKIS13 AI CITY</p>

<h1>
V11 <span>CONTROL TOWER</span>
</h1>

<p class="subtitle">
Execution, recovery, evidence,
maturity, worker reputation and
research status.
Generated {html.escape(utcnow())}.
</p>

<div class="grid">
{cards}
</div>

<div class="panel">
<h2>Active job</h2>
<pre>{html.escape(json.dumps(active_jobs[:1], indent=2))}</pre>
</div>

<div class="panel">
<h2>Blueprint maturity</h2>
<pre>{html.escape(json.dumps(maturity_counts, indent=2))}</pre>
</div>

<div class="panel">
<h2>Latest research signals</h2>
<pre>{html.escape(json.dumps(research.get("signals", [])[:5], indent=2))}</pre>
</div>

<footer>
Mikis13 AI City V11 •
UNKNOWN ≠ PASS •
No blind merge •
Owner stop remains authoritative
</footer>

</main>
</body>
</html>
"""

OUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

OUT.write_text(
    html_doc,
    encoding="utf-8"
)

print(
    "✅ Control Tower:",
    OUT
)
