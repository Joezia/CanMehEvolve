#!/usr/bin/env python3
"""Summarise the follow-up experiments in runs/followup/ into runs/followup/SUMMARY.md and SUMMARY.json. Reads only raw job outputs; tolerant of unfinished jobs.

Task 1  resume-greedy-sN-*        greedy seeds 3-5 completed to 40 HTTP requests (continuation of the frozen runs, other node)
Task 2  sdk-inert-*               false-accept rate of the frozen rule on the real SDK decode (inert patch, true ratio 1.000)
Task 3  null-search-*             greedy rank rule on no-op candidates (noise-driven record drift)
Task 4  correctness-diff-*, correctness-sanitize-*   differential test vs stock on mutated FIT files; ASan/UBSan/TSan runs
Task 6  stack-bestofn-*           stacking best-of-N's own single-function candidates
"""
import glob, json, math, re, statistics as st
from pathlib import Path
from scipy.stats import beta

ROOT = Path(__file__).resolve().parent.parent.parent
F = ROOT / "runs/followup"
S, L = {}, ["# Follow-up experiments (raw results; interpretation pending)", ""]


def J(p, d=None):
    try:
        return json.load(open(p))
    except Exception:
        return d


def jl(p):
    try:
        return [json.loads(l) for l in open(p) if l.strip()]
    except Exception:
        return []


def kv(p):
    d = {}
    try:
        for l in open(p):
            if "=" in l:
                k, v = l.strip().split("=", 1)
                d[k] = v
    except Exception:
        pass
    return d


def cp(k, n):
    return (0.0 if k == 0 else beta.ppf(0.025, k, n - k + 1)), (1.0 if k == n else beta.ppf(0.975, k + 1, n - k))


# ---- task 1 ----
L += ["## 1. Greedy seeds 3-5 completed to 40 HTTP requests", "", "| seed | original requests | extra requests | tokens added | updates in continuation | original final speedup | final speedup after continuation (3 re-measurements) | node (orig -> cont.) | state |", "|---|---|---|---|---|---|---|---|---|"]
t1 = []
for s in (3, 4, 5):
    orig = [d for d in glob.glob(str(ROOT / ("runs/deepseek/greedy-s%d-[0-9]*" % s))) if "resume" not in d][0]
    os_ = J(orig + "/summary.json", {})
    oev = J(orig + "/evaluate-best/summary.json", {})
    for rd in sorted(glob.glob(str(F / ("resume-greedy-s%d-*" % s)))):
        n = kv(rd + "/node.txt")
        rs = J(rd + "/summary.json", {})
        rows = jl(rd + "/results.jsonl")
        ev = J(rd + "/evaluate-best/summary.json", {}) or J(glob.glob(rd + "/evaluate-*/summary.json")[0] if glob.glob(rd + "/evaluate-*/summary.json") else "", {})
        extra = sum(int((r.get("llm") or {}).get("http_attempts", 0) or 0) for r in rows)
        ups = len([r for r in rows if r.get("updated")])
        state = "finished" if "end" in n else "running"
        t1.append({"seed": s, "extra": extra, "final": ev.get("median_speedup"), "orig_final": oev.get("median_speedup"), "updates": ups, "state": state})
        L.append("| %d | %s | %d | %s | %d | %.4f | %s | %s -> %s | %s |" % (s, os_.get("api_calls"), extra, rs.get("total_tokens"), ups, oev.get("median_speedup", float("nan")),
                 ("%.4f (pass %s/3)" % (ev["median_speedup"], ev.get("measurements_passing_rule"))) if ev.get("median_speedup") else "n/a", kv(orig + "/node.txt").get("host"), n.get("host"), state))
S["task1"] = t1

# ---- task 2 ----
L += ["", "## 2. False-accept rate of the frozen rule on the real SDK decode (inert patch)", "", "| family | jobs | measurements | judged faster | 95% CI of rate | median ratio [min, max] | unstable | median p |", "|---|---|---|---|---|---|---|---|"]
fam = {}
for d in sorted(glob.glob(str(F / "sdk-inert-*"))):
    n = kv(d + "/node.txt")
    for f in sorted(glob.glob(d + "/evaluate-*/m*.json")):
        pass
    ms = []
    for f in sorted(glob.glob(d + "/evaluate-*/m*.json")):
        j = J(f)
        if not j or not j.get("timings"):
            continue
        ms.append(f)
    summ = J(glob.glob(d + "/evaluate-*/summary.json")[0]) if glob.glob(d + "/evaluate-*/summary.json") else None
    key = re.search(r"sdk-inert-(xcn[cd])", d).group(1)
    if summ:
        fam.setdefault(key, []).extend(m["analysis"] for m in summ["measurements"] if m["analysis"].get("valid"))
for key, an in sorted(fam.items()):
    k = sum(1 for x in an if x["faster"])
    lo, hi = cp(k, len(an))
    rs = [x["ratio"] for x in an]
    L.append("| %s | %d | %d | %d | %.1f%% (%.1f%%-%.1f%%) | %.5f [%.5f, %.5f] | %d | %.3f |" % (key, len(glob.glob(str(F / ("sdk-inert-%s-*" % key)))), len(an), k, 100 * k / len(an), 100 * lo, 100 * hi,
             st.median(rs), min(rs), max(rs), sum(1 for x in an if x["unstable"]), st.median(x["p_value"] for x in an)))
    S.setdefault("task2", {})[key] = {"n": len(an), "faster": k, "cp95": [lo, hi], "median_ratio": st.median(rs)}
if not fam:
    L.append("| (no finished job yet) | | | | | | | |")

# ---- task 3 ----
L += ["", "## 3. Null search: the greedy rank rule on no-op candidates (true ratio 1.000)", "", "| family | seed | steps | updates | final record (speedup) | updates at steps | first-measurement rule 'faster' | state |", "|---|---|---|---|---|---|---|---|"]
t3 = []
for d in sorted(glob.glob(str(F / "null-search-*"))):
    if "smoke" in d:
        continue
    m = re.search(r"null-search-(xcn[cd])-s(\d+)", d)
    steps = [r for r in jl(d + "/steps.jsonl") if r.get("stage") == "measured"]
    summ = J(d + "/summary.json")
    ups = [r["measured_index"] for r in steps if r.get("updated")]
    final = min([r["R"] for r in steps if r.get("updated")], default=1.0)
    f1 = sum(1 for r in steps if r.get("faster_1")) + sum(1 for r in steps if r.get("faster_2"))
    t3.append({"family": m.group(1), "seed": int(m.group(2)), "steps": len(steps), "updates": len(ups), "final_record": final})
    L.append("| %s | %s | %d | %d | %.5f (%.4f) | %s | %d | %s |" % (m.group(1), m.group(2), len(steps), len(ups), final, 1 / final, ups, f1, "finished" if summ else "running"))
S["task3"] = t3
if t3:
    for fm in ("xcnc", "xcnd"):
        v = [x for x in t3 if x["family"] == fm]
        if v:
            L.append("")
            L.append("%s: updates per run median %s (range %d-%d); final record speedup median %.4f (range %.4f-%.4f)." % (fm, st.median(x["updates"] for x in v), min(x["updates"] for x in v), max(x["updates"] for x in v),
                     st.median(1 / x["final_record"] for x in v), min(1 / x["final_record"] for x in v), max(1 / x["final_record"] for x in v)))

# ---- task 6 ----
L += ["", "## 6. Stacking best-of-N's own single-function candidates (cumulative patches, 3 independent re-measurements each)", ""]
t6 = {}
for d in sorted(glob.glob(str(F / "stack-bestofn-s*"))):
    s = int(re.search(r"-s(\d+)-", d).group(1))
    r = J(d + "/stack_results.json", {})
    t6[s] = r.get("results", [])
    bo = [x for x in glob.glob(str(ROOT / ("runs/deepseek/bestofn-s%d-[0-9]*" % s))) if "resume" not in x][0]
    gr = [x for x in glob.glob(str(ROOT / ("runs/deepseek/greedy-s%d-[0-9]*" % s))) if "resume" not in x][0]
    bev, gev = J(bo + "/evaluate-best/summary.json", {}), J(gr + "/evaluate-best/summary.json", {})
    L.append("**seed %d** (best-of-N final %.4f; greedy final %.4f): %s" % (s, bev.get("median_speedup", float("nan")), gev.get("median_speedup", float("nan")),
             "; ".join("K=%d +%s: %s" % (e["k"], e["added"], ("%.4f" % e["median_speedup"]) if e.get("median_speedup") else "failed") for e in t6[s]) or "(no result yet)"))
S["task6"] = t6

# ---- task 4 ----
L += ["", "## 4. Correctness", ""]
dif = {}
for d in sorted(glob.glob(str(F / "correctness-diff-*"))):
    dif.update(J(d + "/summary.json", {}) or {})
if dif:
    L += ["### 4a. Differential test vs stock on mutated FIT files", "", "| variant | compared | identical | differences | crash in both (same hostile input) | crash only in candidate | crash only in stock |", "|---|---|---|---|---|---|---|"]
    for k, v in sorted(dif.items()):
        if "build_failed" in v:
            L.append("| %s | build/harness check failed: %s | | | | |" % (k, v["build_failed"]))
        else:
            L.append("| %s | %d | %d | %d | %d | %d | %d |" % (k, v["compared"], v["identical"], v["n_differences"], v.get("n_crash_in_both", 0), v["n_crash_in_candidate"], v["n_crash_in_stock"]))
S["task4a"] = dif
san = {}
for _f in sorted(glob.glob(str(F / "correctness-sanitize-*/summary.json"))):
    san.update(J(_f, {}) or {})
if san:
    L += ["", "### 4b. Sanitizers", "", "| variant | config | result |", "|---|---|---|"]
    for k, v in sorted(san.items()):
        L.append("| %s | %s | %s |" % (k.split("|")[0], k.split("|")[1], json.dumps({x: y for x, y in v.items() if x not in ("changed_units",)})))
S["task4b"] = san
(F / "SUMMARY.md").write_text("\n".join(L) + "\n")
(F / "SUMMARY.json").write_text(json.dumps(S, indent=1, default=str) + "\n")
print("\n".join(L))
