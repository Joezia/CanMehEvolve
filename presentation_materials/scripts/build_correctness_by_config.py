#!/usr/bin/env python3
"""Correctness status of the final patch of every run, summarised per configuration (4 levels + not tested), and by code reading (unsynchronised shared state)."""
import sys, re, collections; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pm_lib import *
R = list(csv.DictReader(open(PM / "tables/runs_all.csv")))
CORR = {r["object"]: r for r in csv.DictReader(open(PM / "tables/correctness_unified.csv"))}
CONC = {r["object"]: r for r in csv.DictReader(open(PM / "tables/concurrency_patterns_by_patch.csv"))}
def obj(r):
    c, s = r["config"], r["seed"]
    if c.endswith("I3"): return "r2-" + {"qwen_pop": "qwen-population", "qwen_bon": "qwen-bestofn", "ds_pop": "ds-population", "ds_bon": "ds-bestofn"}[c[:-3]] + f"-s{s}"
    if c == "ds_bon_I2": return f"final-bestofn-seed{s}"
    if c == "ds_greedy_I2": return None if s == "3" else f"final-greedy-seed{s}"
    return None
def level(o):
    r = CORR.get(o)
    if not r or r.get("tested") != "yes": return "not tested"
    f = r.get("findings", "")
    if "legal encoder file" in f or "original file" in f or "digest mismatch" in f or "crashes where" in f or "ASan error" in f: return "wrong output / crash / memory error"
    if "output differs" in f: return "differs only on hostile mutants"
    if "TSan" in f: return "TSan race only"
    return "no finding in tested conditions"
out, per = [], []
for cid in dict.fromkeys(r["config"] for r in R):
    c = collections.Counter(); unsafe = collections.Counter()
    for r in [x for x in R if x["config"] == cid]:
        o = obj(r); lv = level(o) if o else "not tested"; c[lv] += 1
        name = o or ("s3-gen39 (40-request final)" if cid == "ds_greedy_I2" and r["seed"] == "3" else ("I1-" + {"qwen_pop_I1": "search", "qwen_bon_I1": "bestofn"}.get(cid, "") + f"-s{r['seed']}"))
        rd = CONC.get(name)
        unsafe[("reading: unsafe" if rd["reading_says_unsafe"] == "True" else "reading: safe/none") if rd else "reading: n/a"] += 1
        per.append({"run": r["run"], "tested_object": o or "", "level": lv, "code_reading": rd["reading_of_added_code"] if rd else "", "remeasured_speedup": r["remeasure_speedup_median3"]})
    out.append({"config": cid, **{k: c.get(k, 0) for k in ("no finding in tested conditions", "TSan race only", "differs only on hostile mutants", "wrong output / crash / memory error", "not tested")}, **dict(unsafe)})
write_csv(PM / "tables/correctness_by_config.csv", out); write_csv(PM / "tables/correctness_per_run_final_patch.csv", per)
for o in out: print(o)
