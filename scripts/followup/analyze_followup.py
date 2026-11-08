#!/usr/bin/env python3
"""Derived numbers for the follow-up experiments (reads runs/followup/*, runs/deepseek/*; writes runs/followup/ANALYSIS.md).
Everything here is computed from raw files; interpretation is in the text of the final write-up, not in this script."""
import glob, itertools, json, math, statistics as st, sys
from pathlib import Path
from scipy.stats import beta

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
F = ROOT / "runs/followup"
J = lambda p, d=None: (json.load(open(p)) if Path(p).exists() else d)
L = ["# Follow-up analysis (computed)", ""]


def cp(k, n):
    return (0.0 if k == 0 else beta.ppf(0.025, k, n - k + 1)), (1.0 if k == n else beta.ppf(0.975, k + 1, n - k))


def lag1(x):
    m = sum(x) / len(x)
    d = sum((v - m) ** 2 for v in x)
    return sum((x[i] - m) * (x[i + 1] - m) for i in range(len(x) - 1)) / d


# --- 2. inert on the SDK ---
an, ac = [], []
for d in sorted(glob.glob(str(F / "sdk-inert-*"))):
    for f in sorted(glob.glob(d + "/evaluate-*/m*.json")):
        j = J(f)
        if not j or "timings" not in j:
            continue
        ac.append(st.median(lag1(p["candidate_ns"]) for p in j["timings"]["process"]))
    s = J(next(iter(glob.glob(d + "/evaluate-*/summary.json")), ""))
    if s:
        an += [m["analysis"] for m in s["measurements"] if m["analysis"].get("valid")]
k = sum(1 for x in an if x["faster"])
lo, hi = cp(k, len(an))
rs = [x["ratio"] for x in an]
L += ["## 2. SDK inert patch, frozen rule", "",
      "- measurements pooled over both node families: %d; judged faster: %d; 95%% CI of the false-accept rate: [%.2f%%, %.2f%%]" % (len(an), k, 100 * lo, 100 * hi),
      "- reported ratio: median %.5f, sd %.5f, range [%.5f, %.5f] (the gate needs <= 0.98)" % (st.median(rs), st.pstdev(rs), min(rs), max(rs)),
      "- p-values below 0.01: %d of %d; unstable: %d" % (sum(1 for x in an if x["p_value"] < 0.01), len(an), sum(1 for x in an if x["unstable"])),
      "- lag-1 autocorrelation (median over processes of each measurement): median %.3f, range [%.3f, %.3f] over %d measurements" % (st.median(ac), min(ac), max(ac), len(ac)), ""]

# --- 3. null search vs real greedy steps ---
drops = []
finals = []
n_updates = []
for d in sorted(glob.glob(str(F / "null-search-xcn*"))):
    rows = [r for r in (json.loads(l) for l in open(d + "/steps.jsonl") if l.strip()) if r.get("stage") == "measured"]
    for r in rows:
        if r.get("updated"):
            drops.append(1 - r["R"] / r["record_before"])
    finals.append(min([r["R"] for r in rows if r.get("updated")], default=1.0))
    n_updates.append(sum(1 for r in rows if r.get("updated")))
greedy_steps = []
for d in sorted(glob.glob(str(ROOT / "runs/deepseek/greedy-s?-[0-9]*"))):
    if "resume" in d:
        continue
    for u in J(d + "/summary.json")["rank_updates"]:
        greedy_steps.append(1 - u["R"] / u["previous_R"])
mx = max(drops)
L += ["## 3. Null search (8 runs x 36 no-op candidates)", "",
      "- accepted updates per run (of 36 no-op candidates): %s" % sorted(n_updates),
      "- single update size from noise alone: median %.3f%%, max %.3f%% (n=%d updates)" % (100 * st.median(drops), 100 * mx, len(drops)),
      "- real greedy chains (5 runs, %d accepted steps): steps no larger than the largest noise step (%.3f%%): %d; no larger than 0.2%%: %d; no larger than 0.5%%: %d" % (
          len(greedy_steps), 100 * mx, sum(1 for s in greedy_steps if s <= mx), sum(1 for s in greedy_steps if s <= 0.002), sum(1 for s in greedy_steps if s <= 0.005)), ""]
L.insert(len(L) - 2, "- total record drift (1 - final record) over the 8 runs: median %.3f%%, max %.3f%%" % (100 * st.median(1 - f for f in finals), 100 * max(1 - f for f in finals)))

# --- 6. stacking ---
L += ["## 6. Stacking best-of-N's own candidates vs greedy", "", "| seed | best-of-N final | greedy final (40 req.) | stack K=2 | K=3 | K=5 | best K (oracle) | best K speedup | last K |", "|---|---|---|---|---|---|---|---|---|"]
tab = {}
res_greedy = {}
for s in range(1, 6):
    bo = [x for x in glob.glob(str(ROOT / ("runs/deepseek/bestofn-s%d-[0-9]*" % s))) if "resume" not in x][0]
    gr = [x for x in glob.glob(str(ROOT / ("runs/deepseek/greedy-s%d-[0-9]*" % s))) if "resume" not in x][0]
    g = J(gr + "/evaluate-best/summary.json")["median_speedup"]
    rr = glob.glob(str(F / ("resume-greedy-s%d-*/evaluate-*/summary.json" % s)))
    if rr:
        g = J(rr[0])["median_speedup"]
    res_greedy[s] = g
    b = J(bo + "/evaluate-best/summary.json")["median_speedup"]
    sr = J(next(iter(glob.glob(str(F / ("stack-bestofn-s%d-*/stack_results.json" % s)))), ""), {}).get("results", [])
    v = {e["k"]: e["median_speedup"] for e in sr if e.get("median_speedup")}
    bestk = max(v, key=v.get)
    tab[s] = {"bo": b, "g": g, "v": v, "bestk": bestk}
    L.append("| %d | %.4f | %.4f | %.4f | %.4f | %.4f | %d | %.4f | %.4f |" % (s, b, g, v.get(2, float("nan")), v.get(3, float("nan")), v.get(5, float("nan")), bestk, v[bestk], v[max(v)]))
med = lambda xs: st.median(xs)
L += ["", "medians over 5 seeds: best-of-N final %.4f; greedy %.4f; stack K=2 %.4f; K=3 %.4f; K=5 %.4f; best K per seed (oracle) %.4f; last K %.4f" % (
    med([t["bo"] for t in tab.values()]), med([t["g"] for t in tab.values()]), med([t["v"][2] for t in tab.values()]), med([t["v"][3] for t in tab.values()]),
    med([t["v"][5] for t in tab.values()]), med([t["v"][t["bestk"]] for t in tab.values()]), med([t["v"][max(t["v"])] for t in tab.values()])), ""]

# --- 1. greedy with 40 requests: updated medians and tests ---
bo = [tab[s]["bo"] for s in range(1, 6)]
g = [res_greedy[s] for s in range(1, 6)]


def perm_med(x, y):
    a = x + y
    obs = abs(st.median(x) - st.median(y))
    h = t = 0
    for idx in itertools.combinations(range(10), 5):
        p = [a[i] for i in idx]
        q = [a[i] for i in range(10) if i not in idx]
        t += 1
        h += abs(st.median(p) - st.median(q)) >= obs - 1e-15
    return h / t


L += ["## 1. All five greedy runs at 40 HTTP requests", "", "greedy final speedups: %s (median %.4f, range %.4f-%.4f); best-of-N median %.4f; greedy higher in %d/5 seeds; exact permutation test of the median difference p = %.4f (exploratory)" % (
    [round(x, 4) for x in g], med(g), min(g), max(g), med(bo), sum(a > b for a, b in zip(g, bo)), perm_med(g, bo)), ""]
(F / "ANALYSIS.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
