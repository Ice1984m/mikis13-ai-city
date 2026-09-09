#!/usr/bin/env python3
import argparse, datetime as dt, fcntl, hashlib, json, os, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
POLICY=json.loads((ROOT/"config/council-policy.json").read_text())
OWNER=POLICY["owner"]
REPORT=ROOT/"reports/city-council-latest.json"
AUDIT=ROOT/"logs/council/audit.jsonl"
LOCK=ROOT/"state/mutation.lock"
KILL=ROOT/"state/KILL_SWITCH"
SAFE=ROOT/"state/SAFE_MODE"

def gh(*args, check=True):
    p=subprocess.run(["gh",*args],text=True,capture_output=True)
    if check and p.returncode:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip())
    return p

def repos():
    p=gh("repo","list",OWNER,"--limit","1000","--json","nameWithOwner,isArchived,isFork,visibility")
    return [r for r in json.loads(p.stdout) if not r["isArchived"] and not r["isFork"]]

def latest_failure(repo):
    p=gh("run","list","--repo",repo,"--limit","10","--json","databaseId,name,conclusion,status,url",check=False)
    if p.returncode: return None
    for run in json.loads(p.stdout or "[]"):
        if run["status"]=="completed" and run["conclusion"] in {"failure","timed_out","cancelled","action_required"}:
            return run
    return None

def has_safe_workflow(repo):
    p=gh("api",f"repos/{repo}/contents/.github/workflows/mikis13-safe-repair.yml",check=False)
    return p.returncode==0

def append_audit(event):
    AUDIT.parent.mkdir(parents=True,exist_ok=True)
    previous="0"*64
    if AUDIT.exists() and AUDIT.stat().st_size:
        previous=json.loads(AUDIT.read_text().splitlines()[-1])["record_hash"]
    event={"utc":dt.datetime.now(dt.timezone.utc).isoformat(),**event,"previous_hash":previous}
    raw=json.dumps(event,sort_keys=True,separators=(",",":"))
    event["record_hash"]=hashlib.sha256(raw.encode()).hexdigest()
    with AUDIT.open("a") as f: f.write(json.dumps(event,sort_keys=True)+"\n")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dispatch",action="store_true",help="dispatch one allowlisted safe repair")
    args=ap.parse_args()
    inventory=[]
    for r in repos():
        name=r["nameWithOwner"]
        failure=latest_failure(name)
        inventory.append({**r,"latest_failure":failure,"safe_repair_available":has_safe_workflow(name)})
    candidates=[x for x in inventory if x["latest_failure"] and x["safe_repair_available"]]
    candidates.sort(key=lambda x:x["latest_failure"]["databaseId"],reverse=True)
    decision={"action":"monitor_only","reason":"no eligible failure"}
    if args.dispatch:
        if KILL.exists(): decision={"action":"blocked","reason":"kill switch active"}
        elif SAFE.exists(): decision={"action":"blocked","reason":"safe mode active"}
        elif candidates:
            LOCK.parent.mkdir(parents=True,exist_ok=True)
            with LOCK.open("w") as lock:
                try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                except BlockingIOError:
                    decision={"action":"blocked","reason":"another mutation job is active"}
                else:
                    target=candidates[0]["nameWithOwner"]
                    p=gh("workflow","run","mikis13-safe-repair.yml","--repo",target,check=False)
                    decision={"action":"repair_dispatched" if p.returncode==0 else "dispatch_failed",
                              "repository":target,"error":p.stderr.strip()[:500]}
    report={"generated_at":dt.datetime.now(dt.timezone.utc).isoformat(),
            "policy":POLICY,"repository_count":len(inventory),
            "eligible_repairs":len(candidates),"decision":decision,"repositories":inventory}
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps(report,indent=2)+"\n")
    append_audit({"type":"council_cycle","decision":decision,"repository_count":len(inventory)})
    print(json.dumps({"repositories":len(inventory),"eligible":len(candidates),"decision":decision},indent=2))
    return 1 if decision["action"]=="dispatch_failed" else 0

if __name__=="__main__": raise SystemExit(main())
