#!/usr/bin/env python3
"""Configuration summaries (median and full range over the five seeds) and within-model comparisons of search vs independent sampling.
Unit of analysis = the seed (one independent search). Tests are EXPLORATORY: none was pre-registered; seeds of different arms are NOT paired (different random streams)."""
import sys, itertools; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pm_lib import *
from runsets import CONFIGS, CFG, IMPL

R = list(csv.DictReader(open(PM / "tables/runs_all.csv")))
def f(x):
    try: return float(x)
    except Exception: return None
def col(cfg, key):
    return [f(r[key]) for r in sorted([r for r in R if r["config"] == cfg], key=lambda r: int(r["seed"])) if f(r[key]) is not None]
def mr(v):
    return (median(v), min(v), max(v)) if v else (None, None, None)
def req(cfg):
    v = col(cfg, "http_requests") or col(cfg, "api_calls_summary"); return v

summ = []
for cid, label, algo, model, impl in CONFIGS:
    row = {"config": cid, "label": label, "algorithm": algo, "model": model, "impl": impl, "seeds": len(col(cid, "seed"))}
    for key, nm in (("remeasure_speedup_median3", "remeasured_speedup"), ("search_best_confirmed_speedup", "search_best_confirmed_speedup"),
                    ("total_tokens", "total_tokens"), ("prompt_tokens", "prompt_tokens"), ("completion_tokens", "completion_tokens"),
                    ("reasoning_tokens_subset_of_completion", "reasoning_tokens"), ("search_elapsed_s", "search_elapsed_s"), ("remeasure_elapsed_s", "remeasure_elapsed_s"),
                    ("course_metric_search", "course_metric_search"), ("course_metric_remeasured", "course_metric_remeasured"),
                    ("lineage_depth", "lineage_depth"), ("cumulative_updates", "cumulative_updates"), ("measured_candidates", "measured_candidates"),
                    ("compile_fail", "compile_fail"), ("check_fail", "check_fail"), ("unchanged", "unchanged"), ("http_fail", "http_fail"), ("confirmed_candidates", "confirmed_candidates"),
                    ("no_usage_requests", "no_usage_requests"), ("truncated_replies", "truncated_replies")):
        m, lo, hi = mr(col(cid, key)); row[nm + "_median"], row[nm + "_min"], row[nm + "_max"] = m, lo, hi
    v = req(cid); row["requests_each_seed"] = json.dumps([int(x) for x in v]); row["requests_unit"] = "HTTP requests" if col(cid, "http_requests") else "model calls (HTTP attempts not recorded)"
    row["remeasure_all_pass_3of3"] = sum(1 for r in R if r["config"] == cid and r["remeasure_passes"] == "3/3")
    row["per_seed_remeasured_speedup"] = json.dumps([round(x, 6) for x in col(cid, "remeasure_speedup_median3")])
    summ.append(row)
write_csv(PM / "tables/config_summary.csv", summ)

# seed-level pivot
piv = []
for cid, *_ in CONFIGS:
    d = {"config": cid}
    for r in R:
        if r["config"] == cid:
            d[f"s{r['seed']}"] = r["remeasure_speedup_median3"]
    piv.append(d)
write_csv(PM / "tables/seed_pivot_remeasured_speedup.csv", piv)

def perm_p(a, b):
    allv = list(a) + list(b); n = len(a); obs = abs(median(a) - median(b)); ge = tot = 0
    for idx in itertools.combinations(range(len(allv)), n):
        x = [allv[i] for i in idx]; y = [allv[i] for i in range(len(allv)) if i not in idx]
        tot += 1; ge += 1 if abs(median(x) - median(y)) >= obs - 1e-12 else 0
    return ge / tot
def mw_exact_p(a, b):
    allv = list(a) + list(b); n = len(a); ranks = sps.rankdata(allv); obs = abs(sum(ranks[:n]) - n * (len(allv) + 1) / 2); ge = tot = 0
    for idx in itertools.combinations(range(len(allv)), n):
        s = sum(ranks[i] for i in idx); tot += 1; ge += 1 if abs(s - n * (len(allv) + 1) / 2) >= obs - 1e-9 else 0
    return ge / tot

pairs = [("qwen_pop_I1", "qwen_bon_I1", "Qwen, I1 (original population search vs best-of-N)"),
         ("qwen_pop_I3", "qwen_bon_I3", "Qwen, I3 (README loop vs matched best-of-N)"),
         ("ds_greedy_I2", "ds_bon_I2", "DeepSeek, I2 (greedy chain vs best-of-N, rank rule)"),
         ("ds_pop_I3", "ds_bon_I3", "DeepSeek, I3 (README loop vs matched best-of-N)")]
tests = []
for A, B, name in pairs:
    for key, nm in (("remeasure_speedup_median3", "remeasured final speedup (primary)"), ("search_best_confirmed_speedup", "best confirmed in search"),
                    ("total_tokens", "total tokens"), ("course_metric_remeasured", "course metric (speedup-1)/tokens, remeasured speedup"), ("course_metric_search", "course metric, search-time value")):
        a, b = col(A, key), col(B, key)
        tests.append({"comparison": name, "A": A, "B": B, "quantity": nm, "n_A": len(a), "n_B": len(b), "median_A": median(a), "median_B": median(b), "difference_of_medians_A_minus_B": median(a) - median(b),
                      "range_A": f"{min(a):.6g}..{max(a):.6g}", "range_B": f"{min(b):.6g}..{max(b):.6g}", "all_A_above_all_B": min(a) > max(b), "all_B_above_all_A": min(b) > max(a),
                      "exact_permutation_p_two_sided_median_diff": perm_p(a, b), "exact_mannwhitney_p_two_sided": mw_exact_p(a, b),
                      "design": "unpaired (seeds are independent searches; same seed number does not pair outcomes)", "preregistered": "no (exploratory)"})
# Holm over the 4 primary tests (remeasured speedup, Mann-Whitney)
prim = [t for t in tests if t["quantity"].startswith("remeasured final")]
order = sorted(range(len(prim)), key=lambda i: prim[i]["exact_mannwhitney_p_two_sided"]); run_max = 0
for rank, i in enumerate(order):
    adj = min(1.0, (len(prim) - rank) * prim[i]["exact_mannwhitney_p_two_sided"]); run_max = max(run_max, adj); prim[i]["holm_adjusted_mannwhitney_p_over_4_primary_tests"] = run_max
write_csv(PM / "tables/within_model_tests.csv", tests)
src("cmp-1", "per-config median/range and within-model tests", "presentation_materials/tables/runs_all.csv (from runs/*)", "remeasure_speedup_median3 etc.", "median/min/max over 5 seeds; exact permutation and exact Mann-Whitney over all C(10,5)=252 splits")
if __name__ == "__main__":
    for s in summ:
        print(f"{s['config']:14s} remeas {s['remeasured_speedup_median']:.4f} [{s['remeasured_speedup_min']:.4f},{s['remeasured_speedup_max']:.4f}]  tokens {s['total_tokens_median']:.0f} [{s['total_tokens_min']:.0f},{s['total_tokens_max']:.0f}] search_s {s['search_elapsed_s_median']:.0f} course_B {s['course_metric_remeasured_median']:.3e}")
    for t in tests:
        if t["quantity"].startswith(("remeasured", "total tokens", "course metric (")):
            print(f"{t['comparison'][:44]:44s} {t['quantity'][:34]:34s} A {t['median_A']:.5g} B {t['median_B']:.5g} permP {t['exact_permutation_p_two_sided_median_diff']:.4f} MW {t['exact_mannwhitney_p_two_sided']:.4f} sep {t['all_A_above_all_B']}/{t['all_B_above_all_A']}")
