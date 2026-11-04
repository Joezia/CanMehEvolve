#!/usr/bin/env python3
"""Independent recomputation of every p-value, speedup and token metric in the report from RAW run files (unrounded).

Reads only, per run directory: summary.json, credits.csv, results.jsonl, evaluate-best/**/summary.json (three raw ratios),
plus the post hoc re-measurement summaries in runs/deepseek-common34/.  Does not use phase1_final.json for its inputs; it
compares its results with that export at the end (max abs difference printed) so the two code paths check each other.

All tests are EXPLORATORY (the test choice was made after the data were seen; nothing was pre-registered):
  * exact two-sided permutation test of the difference of medians (all C(10,5)=252 splits)
  * exact two-sided Mann-Whitney test (same 252 splits)
  * exact two-sided sign test on the 5 seed pairs (ties dropped)
Two token metrics are kept apart:
  A "search-time confirmed" = (best search-time confirmed speedup - 1) / total_tokens.  README's quotient reads best_confirmed_speedup from the last
                        credits.csv row, but our rank-mode credits.csv has no such column and summary.json keeps an unused default (1.0).  We therefore
                        compute it from results.jsonl: the best speedup 1/ratio among candidates whose TWO measurements both passed the frozen rule
                        (rule_pass_1 and rule_pass_2: ratio <= 0.98, p < 0.01 each).  Reported next to the ranking value (best_ranked_speedup) to show
                        they coincide in all 10 runs; the ranking value itself is NOT used as the confirmed speedup.
  B "re-measured"     = (median speedup of the 3 independent re-measurements of the fixed final patch - 1) / total_tokens.
Full runs use all tokens spent (seed-1 greedy adds its resume call's tokens, from the resume run's own credits.csv).
The 34-request analysis uses the cumulative tokens of the first 34 requests (rows' llm.total_tokens; equals credits.csv at that generation).
Token accounting: a request that returned no usage object counts 0 tokens (listed below); truncated replies count their reported usage.
Writes runs/phase1-final/recomputed_stats.json and recomputed_stats.md.
"""
import csv, glob, itertools, json, math, re, statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DS = ROOT / "runs/deepseek"
K = 34


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def eval_summary(p):
    return json.load(open(p))


def speed_from_eval(ev):
    ratios = [m["analysis"]["ratio"] for m in ev["measurements"] if m["analysis"]["valid"]]
    passes = ev["measurements_passing_rule"]
    sp = 1.0 / st.median(ratios)                       # recomputed from raw ratios; equals ev["median_speedup"]
    assert abs(sp - ev["median_speedup"]) < 1e-9 or abs(sp - 1 / ev["median_ratio_over_measurements"]) < 1e-9
    return (sp if len(ratios) == 3 and passes == 3 else 1.0), ratios, passes


def perm_median_p(x, y):
    allv, n = list(x) + list(y), len(x)
    obs = abs(st.median(x) - st.median(y))
    hit = tot = 0
    for idx in itertools.combinations(range(len(allv)), n):
        a = [allv[i] for i in idx]
        b = [allv[i] for i in range(len(allv)) if i not in idx]
        tot += 1
        hit += abs(st.median(a) - st.median(b)) >= obs - 1e-15
    return hit / tot


def mw_p(x, y):
    U = lambda a, b: sum((p > q) + 0.5 * (p == q) for p in a for q in b)
    allv, n = list(x) + list(y), len(x)
    mu, uo = len(x) * len(y) / 2, U(x, y)
    hit = tot = 0
    for idx in itertools.combinations(range(len(allv)), n):
        a = [allv[i] for i in idx]
        b = [allv[i] for i in range(len(allv)) if i not in idx]
        tot += 1
        hit += abs(U(a, b) - mu) >= abs(uo - mu) - 1e-15
    return hit / tot


def sign_p(diffs):
    n = sum(1 for d in diffs if d != 0)
    k = sum(1 for d in diffs if d > 0)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(max(k, n - k), n + 1)) / 2 ** n)


runs = {}
usage_missing, trunc_tokens, trunc_n, http_fail_rows = [], 0, 0, 0
for d in sorted(DS.glob("*-s[1-5]-[0-9]*")):
    if "resume" in d.name or not d.is_dir():
        continue
    arm, seed = re.match(r"(greedy|bestofn)-s(\d)-", d.name).groups()
    seed = int(seed)
    rows = jl(d / "results.jsonl")
    cred = list(csv.DictReader(open(d / "credits.csv")))
    last = cred[-1]
    tokens = int(last["total_tokens"])
    ranked = float(last["best_ranked_speedup"])
    resume = sorted(d.parent.glob(d.name + "-resume-*"))
    attempts = sum(int((r.get("llm") or {}).get("http_attempts", 0) or 0) for r in rows)
    rrows = []
    if resume:
        rcred = list(csv.DictReader(open(resume[-1] / "credits.csv")))
        tokens += int(rcred[-1]["total_tokens"])
        ranked = float(rcred[-1]["best_ranked_speedup"])
        rrows = jl(resume[-1] / "results.jsonl")
        attempts += sum(int((r.get("llm") or {}).get("http_attempts", 0) or 0) for r in rrows)
    conf_full = max([r["speedup"] for r in rows + rrows if r.get("ok") and r.get("rule_pass_1") and r.get("rule_pass_2")], default=1.0)
    for r in rows + rrows:
        l = r.get("llm") or {}
        if l and not l.get("usage_seen", False):
            usage_missing.append((d.name, r["generation"], l.get("http_status"), l.get("finish_reason")))
        if l.get("finish_reason") == "length":
            trunc_n += 1
            trunc_tokens += l.get("total_tokens", 0) or 0
    ev = eval_summary(d / "evaluate-best/summary.json")
    sp, ratios, passes = speed_from_eval(ev)
    # 34-request analysis
    cum = tok34 = 0
    best = None
    lastgen = None
    conf34 = 1.0
    for r in rows:
        a = int((r.get("llm") or {}).get("http_attempts", 0) or 0)
        if cum + a > K:
            break
        cum += a
        lastgen = r["generation"]
        tok34 += (r.get("llm") or {}).get("total_tokens", 0) or 0
        if r.get("ok") and r.get("rule_pass_1") and r.get("rule_pass_2"):
            conf34 = max(conf34, r["speedup"])
        if r.get("updated"):
            best = r
    cr = {int(c["generation"]): c for c in cred}
    assert tok34 == int(cr[lastgen]["total_tokens"])
    final_gen = json.load(open(d / "summary.json"))["rank_updates"][-1]["generation"]
    if best is None:
        sp34, ranked34 = 1.0, 1.0
    elif best["generation"] == final_gen:
        sp34, ranked34 = sp, 1.0 / best["rank_R"]
    else:
        hit = [json.load(open(f)) for f in glob.glob(str(ROOT / "runs/deepseek-common34/*/evaluate-*/summary.json"))
               if json.load(open(f))["patch"].endswith("/%s/patches/gen_%d.patch" % (d.name, best["generation"]))]
        assert len(hit) == 1, (d.name, best["generation"])
        sp34 = speed_from_eval(hit[0])[0]
        ranked34 = 1.0 / best["rank_R"]
    runs[(arm, seed)] = dict(tokens=tokens, attempts=attempts, speed=sp, ratios=ratios, passes=passes, A=(conf_full - 1) / tokens, B=(sp - 1) / tokens,
                             ranked=ranked, confirmed=conf_full, tok34=tok34, speed34=sp34, A34=(conf34 - 1) / tok34, B34=(sp34 - 1) / tok34, ranked34=ranked34, confirmed34=conf34)


def group(key):
    return ([runs[("greedy", s)][key] for s in range(1, 6)], [runs[("bestofn", s)][key] for s in range(1, 6)])


res = {"tests": {}, "per_run": {"%s-s%d" % k: v for k, v in runs.items()}}
for key, label in (("speed", "full speedup (re-measured)"), ("A", "full search-time confirmed metric"), ("B", "full re-measured metric"),
                   ("speed34", "34-request speedup (re-measured)"), ("A34", "34-request search-time confirmed metric"), ("B34", "34-request re-measured metric")):
    g, b = group(key)
    res["tests"][label] = {"greedy_median": st.median(g), "greedy_range": [min(g), max(g)], "bestofn_median": st.median(b), "bestofn_range": [min(b), max(b)],
                           "perm_median_p": perm_median_p(g, b), "mannwhitney_p": mw_p(g, b), "greedy_higher_pairs": sum(x > y for x, y in zip(g, b)),
                           "sign_p": sign_p([x - y for x, y in zip(g, b)])}
res["confirmed_vs_ranked_max_abs_difference"] = max(max(abs(r["confirmed"] - r["ranked"]) for r in runs.values()), max(abs(r["confirmed34"] - r["ranked34"]) for r in runs.values()))
res["token_accounting"] = {"note": "requests without a usage object (HTTP 502) consumed an UNKNOWN number of tokens; they are not included, so totals may underestimate cost and overstate efficiency",
                           "requests_without_usage_object": usage_missing, "truncated_requests": trunc_n, "truncated_total_tokens": trunc_tokens,
                           "total_tokens_all_runs": sum(r["tokens"] for r in runs.values())}

# cross-check against the earlier export (different code path)
try:
    ex = json.load(open(ROOT / "runs/phase1-final/phase1_final.json"))
    diffs = []
    for r in ex["runs"]:
        if r["experiment"] == "deepseek":
            mine = runs[(r["arm"], r["seed"])]
            diffs += [abs(mine["B"] - r["course_metric"]), abs(mine["speed"] - r["best_confirmed_speedup"])]
    res["cross_check_vs_phase1_final_max_abs_diff"] = max(diffs)
except Exception as e:  # pragma: no cover
    res["cross_check_vs_phase1_final_max_abs_diff"] = "n/a: %s" % e

out = ROOT / "runs/phase1-final"
(out / "recomputed_stats.json").write_text(json.dumps(res, indent=2) + "\n")
L = ["# Recomputed statistics (exploratory; unrounded raw inputs)", "",
     "| quantity | greedy median [range] | best-of-N median [range] | permutation (median) p | Mann-Whitney p | greedy higher | sign p |", "|---|---|---|---|---|---|---|"]
for k, v in res["tests"].items():
    f = (lambda x: "%.4g" % x)
    L.append("| %s | %s [%s, %s] | %s [%s, %s] | %.4f | %.4f | %d/5 | %.4f |" % (k, f(v["greedy_median"]), f(v["greedy_range"][0]), f(v["greedy_range"][1]), f(v["bestofn_median"]),
                                                                                f(v["bestofn_range"][0]), f(v["bestofn_range"][1]), v["perm_median_p"], v["mannwhitney_p"], v["greedy_higher_pairs"], v["sign_p"]))
L += ["", "Token accounting: %s" % json.dumps(res["token_accounting"]), "Cross-check vs phase1_final.json (max abs diff): %s" % res["cross_check_vs_phase1_final_max_abs_diff"]]
(out / "recomputed_stats.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
