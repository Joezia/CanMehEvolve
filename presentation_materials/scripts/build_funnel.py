#!/usr/bin/env python3
"""Request funnel per configuration (median over 5 seeds) and expected-vs-observed function draws."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pm_lib import *
from runsets import *
R = list(csv.DictReader(open(PM / "tables/runs_all.csv")))
def f(x):
    try: return float(x)
    except Exception: return 0.0
out = []
for cid, label, algo, model, impl in CONFIGS:
    rs = [r for r in R if r["config"] == cid]
    rows_total = [f(r["result_rows"]) for r in rs]
    d = {"config": cid, "label": f"{'Qwen' if cid.startswith('qwen') else 'DeepSeek'} {algo} ({impl})",
         "http_or_no_code_or_truncated": median([f(r["http_fail"]) + f(r["no_code"]) + f(r["truncated_stage"]) for r in rs]),
         "unchanged": median([f(r["unchanged"]) for r in rs]), "compile_fail": median([f(r["compile_fail"]) for r in rs]), "check_fail": median([f(r["check_fail"]) for r in rs]),
         "measured_not_confirmed": median([f(r["measured_candidates"]) - f(r["confirmed_candidates"]) for r in rs]),
         "confirmed_inherited_or_not_better_than_parent": median([(0.0 if algo == "best-of-N" else max(0.0, f(r["confirmed_candidates"]) - (f(r["record_updates_rank_rule"]) if impl == "I2" else f(r["improved_on_parent_rows"])))) for r in rs]),
         "new_step_accepted": median([(f(r["record_updates_rank_rule"]) if impl == "I2" and algo != "best-of-N" else f(r["improved_on_parent_rows"]) if algo != "best-of-N" else f(r["confirmed_candidates"])) for r in rs]),
         "confirmed": median([f(r["confirmed_candidates"]) for r in rs]),
         "rows_without_request_median": median([f(r["no_request_rows"]) for r in rs]),
         "in_final_patch_lineage_median": median([f(r["lineage_depth"]) for r in rs]), "accepted_steps_median": median([f(r["cumulative_updates"]) for r in rs])}
    out.append(d)
write_csv(PM / "tables/request_funnel.csv", out)
# expected vs observed draws, DeepSeek I3 runs (population + best-of-N), top 8 profile regions by mean share
import collections
runs_ = [x for x in runs() if x["cfg"] in ("ds_pop_I3", "ds_bon_I3")]
prof = [jload(x["dirs"][0] / "profile_samples.json") for x in runs_]
tot = collections.Counter(); S = 0
share = collections.Counter()
for p in prof:
    s = sum(p.values())
    for k, v in p.items(): share[int(k)] += v / s / len(prof)
top = [k for k, _ in share.most_common(8)]
labels = {}
for x in runs_:
    for t in jload(x["dirs"][0] / "profile.json", {}).get("top_regions", []): labels[t["id"]] = t["label"]
nreg = len(prof[0])
obs = collections.Counter(); ndraw = 0; exp_tot = collections.Counter()
for x, p in zip(runs_, prof):
    rows = [r for r in jl(x["dirs"][0] / "results.jsonl") if not r.get("repair_attempt")]
    ndraw += len(rows); s = sum(p.values())
    for r in rows: obs[r["region"]] += 1
    for k in top: exp_tot[k] += len(rows) * (0.9 * p[str(k)] / s + 0.1 / nreg)
rows_out = [{"region_id": k, "function": labels.get(k, str(k)), "mean_sample_share_pct": 100 * share[k], "expected_pct": 100 * exp_tot[k] / ndraw, "observed_pct": 100 * obs[k] / ndraw, "observed_draws": obs[k], "total_draws": ndraw} for k in top]
write_csv(PM / "figure_data/region_expected_vs_observed.csv", rows_out)
if __name__ == "__main__":
    for o in out: print({k: o[k] for k in ("config", "http_or_no_code_or_truncated", "unchanged", "compile_fail", "check_fail", "measured_not_confirmed", "confirmed", "rows_without_request_median")})
    for r in rows_out: print(r["function"], f"{r['mean_sample_share_pct']:.1f}% exp {r['expected_pct']:.1f}% obs {r['observed_pct']:.1f}% ({r['observed_draws']}/{r['total_draws']})")
