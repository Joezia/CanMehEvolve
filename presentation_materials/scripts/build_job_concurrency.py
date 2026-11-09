#!/usr/bin/env python3
"""Observed maximum number of concurrently running LLM search jobs per code version, from the start/finish times recorded in each run."""
import sys, re, datetime; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pm_lib import *
def ts(s):
    s = (s or "").replace("+0800", "+08:00")
    try: return datetime.datetime.fromisoformat(s).timestamp()
    except Exception: return None
iv = []
for fam, pat in (("I1 (Qwen)", "runs/main/*"), ("I2 (DeepSeek)", "runs/deepseek/greedy-s?-[0-9]*"), ("I2 (DeepSeek)", "runs/deepseek/bestofn-s*")):
    for d in sorted(ROOT.glob(pat)):
        if "-resume" in d.name: continue
        r, s = jload(d / "run.json", {}), jload(d / "summary.json", {})
        a, e = ts(r.get("started")), ts(s.get("finished"))
        if a and e: iv.append((fam, d.name, a, e))
for d in sorted((ROOT / "runs/round2/runs").glob("*")):
    for f in sorted(d.glob("segments/*.node.txt")):
        txt = f.read_text(errors="replace"); m1 = re.search(r"^start=(\S+)", txt, re.M); m2 = re.search(r"\bend=(\S+)", txt)
        a, e = ts(m1.group(1) if m1 else None), ts(m2.group(1) if m2 else None)
        if a and e: iv.append(("I3 (both models)", d.name, a, e))
def conc(L):
    ev = sorted([(a, 1) for _, _, a, e in L] + [(e, -1) for _, _, a, e in L], key=lambda x: (x[0], x[1])); c = m = 0
    for t, k in ev: c += k; m = max(m, c)
    return m
out = []
for fam in ("I1 (Qwen)", "I2 (DeepSeek)", "I3 (both models)"):
    L = [x for x in iv if x[0] == fam]
    out.append({"code_version": fam, "jobs_or_segments": len(L), "max_concurrent": conc(L), "first_start": datetime.datetime.fromtimestamp(min(x[2] for x in L)).isoformat(), "last_end": datetime.datetime.fromtimestamp(max(x[3] for x in L)).isoformat()})
write_csv(PM / "tables/llm_job_concurrency.csv", out); print(out)
