#!/usr/bin/env python3
"""Where the speed-up comes from: functions in the final patches, the step table of the representative greedy chain (seed 3), and best-of-N candidate stacking."""
import sys, collections; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pm_lib import *
from runsets import *

R = list(csv.DictReader(open(PM / "tables/runs_all.csv")))
# --- 1. function frequency in final patches, per configuration
freq = collections.defaultdict(collections.Counter)
for r in R:
    for fn in dict.fromkeys(x for x in r["functions_in_final_patch"].split(";") if x):
        freq[r["config"]][fn] += 1
rows = []
for cid, c in freq.items():
    for fn, n in c.most_common():
        rows.append({"config": cid, "function": fn, "final_patches_containing_it_of_5": n})
write_csv(PM / "tables/functions_in_final_patches.csv", rows)
# --- 2. step table of the representative chain (DeepSeek greedy seed 3, 40 requests); search-time values only
d = [x for x in runs() if x["id"] == "ds_greedy_I2_s3"][0]
summ = jload(d["dirs"][-1] / "summary.json")
steps_corr = {}
for line in open(ROOT / "runs/followup/CORRECTNESS_BY_PATCH.md"):
    if line.startswith("| s3-step"):
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        steps_corr[c[0].split("-")[1]] = {"differential": c[1], "asan_errors": c[5], "tsan_locations": c[8], "tsan_digest_mismatches": c[9], "tsan_result": c[10]}
chain = []
prev = 1.0
for i, u in enumerate(summ["rank_updates"], 1):
    sp = 1 / u["R"]
    chain.append({"step": i, "generation": u["generation"], "function": u["label"], "R_after": u["R"], "cumulative_speedup_at_search_time": sp,
                  "step_gain_pct": 100 * (1 - u["R"] / u["previous_R"]), "independently_confirmed": "no (only the fixed final patch is re-measured)" if i < len(summ["rank_updates"]) else "yes: 3 re-measurements of the 40-request final patch",
                  **{"corr_" + k: v for k, v in steps_corr.get("step%02d" % i, {}).items()}})
write_csv(PM / "tables/chain_steps_ds_greedy_s3.csv", chain)
# --- 3. best-of-N stacking (DeepSeek rank-rule best-of-N candidates, no new model call)
st = []
seeds = {}
for s in range(1, 6):
    sd = sorted((ROOT / "runs/followup").glob(f"stack-bestofn-s{s}-*"))[0]
    res = jload(sd / "stack_results.json")
    sk = res.get("skipped", [])
    ks = [e for e in res["results"] if e.get("median_speedup")]
    bo = [r for r in R if r["config"] == "ds_bon_I2" and int(r["seed"]) == s][0]
    gr = [r for r in R if r["config"] == "ds_greedy_I2" and int(r["seed"]) == s][0]
    best = max(ks, key=lambda e: e["median_speedup"])
    seeds[s] = {"K": {e["k"]: e["median_speedup"] for e in ks}, "best": best}
    node = kv(sd / "node.txt")
    st.append({"seed": s, "best_of_N_final_remeasured": float(bo["remeasure_speedup_median3"]), "greedy_final_remeasured_40req": float(gr["remeasure_speedup_median3"]),
               "candidates_available": len(jload(sd / "candidates.json", [])), "stack_K1": seeds[s]["K"].get(1), "stack_K2_fixed": seeds[s]["K"].get(2), "stack_K3_fixed": seeds[s]["K"].get(3),
               "stack_K5_fixed": seeds[s]["K"].get(5), "bestK_posthoc": best["k"], "bestK_speedup_posthoc": best["median_speedup"], "last_K": ks[-1]["k"], "last_K_speedup": ks[-1]["median_speedup"],
               "stacks_measured": len(res["results"]), "independent_measurements": sum(e.get("valid_measurements", 0) for e in res["results"]), "skipped_candidates_conflict_or_failure": len(sk),
               "functions_in_bestK": ";".join(best["functions"]), "model_calls_added": 0, "node": node.get("host"),
               "bestK_all_3_pass_rule": best.get("passes") == 3})
write_csv(PM / "tables/stacking_by_seed.csv", st)
def med(key): return median([x[key] for x in st if x.get(key) is not None])
summary = {"median_best_of_N": med("best_of_N_final_remeasured"), "median_greedy": med("greedy_final_remeasured_40req"), "median_K2": med("stack_K2_fixed"), "median_K3": med("stack_K3_fixed"),
           "median_K5": med("stack_K5_fixed"), "median_bestK_posthoc": med("bestK_speedup_posthoc"), "median_lastK": med("last_K_speedup"),
           "range_K5": [min(x["stack_K5_fixed"] for x in st), max(x["stack_K5_fixed"] for x in st)], "range_bestK": [min(x["bestK_speedup_posthoc"] for x in st), max(x["bestK_speedup_posthoc"] for x in st)],
           "total_independent_measurements": sum(x["independent_measurements"] for x in st), "total_stacks": sum(x["stacks_measured"] for x in st)}
# fraction of the gap (greedy - best-of-N) closed, per seed: (stack - bon) / (greedy - bon)
for key in ("stack_K2_fixed", "stack_K3_fixed", "stack_K5_fixed", "bestK_speedup_posthoc"):
    summary["gap_closed_median_" + key] = median([(x[key] - x["best_of_N_final_remeasured"]) / (x["greedy_final_remeasured_40req"] - x["best_of_N_final_remeasured"]) for x in st])
json.dump(summary, open(PM / "tables/stacking_summary.json", "w"), indent=1)
# per-step records for the stack curve figure
curve = []
for s, v in seeds.items():
    for k, sp in v["K"].items(): curve.append({"seed": s, "K": k, "speedup": sp})
write_csv(PM / "figure_data/stack_curve.csv", curve)
src("mech-1", "stacking K=2,3,5 and best K", "runs/followup/stack-bestofn-s*/stack_results.json", "results[].median_speedup (3 independent measurements per stack)", "median over seeds; bestK chosen post hoc by max median_speedup")
if __name__ == "__main__":
    for c in chain: print(c["step"], c["generation"], c["function"], f"{c['cumulative_speedup_at_search_time']:.4f}", f"{c['step_gain_pct']:.2f}%", c.get("corr_tsan_digest_mismatches"), c.get("corr_tsan_locations"))
    print(json.dumps(summary, indent=1))
    for x in st: print(x["seed"], x["best_of_N_final_remeasured"], x["stack_K2_fixed"], x["stack_K3_fixed"], x["stack_K5_fixed"], x["bestK_posthoc"], x["bestK_speedup_posthoc"], x["greedy_final_remeasured_40req"], x["skipped_candidates_conflict_or_failure"])
    top = collections.Counter(); 
    for r in rows: 
        if r["config"] in ("ds_greedy_I2","ds_pop_I3","qwen_pop_I3"): top[(r["config"],r["function"])]=r["final_patches_containing_it_of_5"]
    print(sorted(top.items(), key=lambda x:-x[1])[:14])
