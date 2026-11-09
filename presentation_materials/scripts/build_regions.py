#!/usr/bin/env python3
"""Function (region) selection: profile samples -> draw probabilities (90% sample-weighted / 10% uniform; plus the 25% credit branch in the population arm),
and what the 40 runs actually drew. Sources: profile.json (top-40 regions, older runs) or profile_samples.json (all regions, round-2 runs), results.jsonl."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pm_lib import *
from runsets import *

UNIFORM, EXPLOIT = 0.1, 0.25
NREG = len(jload(ROOT / "runs/round2/runs/ds-population-s1/profile_samples.json"))
out, draws_table, top_example = [], [], None
for r in runs():
    cfg = CFG[r["cfg"]]; d0 = r["dirs"][0]
    rows = []
    for d in r["dirs"]:
        rows += jl(d / "results.jsonl")
    ps = jload(d0 / "profile_samples.json")
    if ps:
        samples = {int(k): v for k, v in ps.items()}; coverage = "all regions"
    else:
        pj = jload(d0 / "profile.json", {})
        samples = {t["id"]: t["samples"] for t in pj.get("top_regions", [])}; coverage = f"top {len(samples)} regions ({100*sum(samples.values())/max(pj.get('attributed',1),1):.1f}% of attributed samples)"
    S = sum(samples.values()); nsamp = sum(1 for v in samples.values() if v > 0)
    draws = [x for x in rows if not x.get("repair_attempt")]
    reg = [x["region"] for x in draws if x.get("region") is not None]
    cnt = {}
    for g in reg: cnt[g] = cnt.get(g, 0) + 1
    top5 = sorted(samples, key=samples.get, reverse=True)[:5]
    in_sampled = sum(1 for g in reg if samples.get(g, 0) > 0)
    # replay of the credit branch (population arm): best-credited region at each draw
    gain, exploit_equal, credited_draws = {}, 0, 0
    is_pop = cfg[2] == "population"
    for x in rows:
        if is_pop and not x.get("repair_attempt"):
            best = None; bg = 0.0
            for rid in sorted(gain):
                if gain[rid] > bg: bg, best = gain[rid], rid
            if best is not None:
                credited_draws += 1
                if x.get("region") == best: exploit_equal += 1
        if x.get("ok") and x.get("improved_on_parent"):
            gain[x["region"]] = max(gain.get(x["region"], 0.0), x["parent_ratio"] - x["ratio"])
    ex_share = EXPLOIT if is_pop else 0.0
    out.append({"run": r["id"], "config": r["cfg"], "algorithm": cfg[2], "independent_draws": len(reg), "repair_rows_excluded": len(rows) - len(draws),
                "distinct_regions_drawn": len(cnt), "repeat_draws": len(reg) - len(cnt), "max_times_one_region": max(cnt.values()) if cnt else 0,
                "most_drawn_region": max(cnt, key=cnt.get) if cnt else "", "draws_in_top5_profile_regions": sum(cnt.get(g, 0) for g in top5),
                "draws_in_regions_with_samples": in_sampled, "draws_in_zero_sample_regions": len(reg) - in_sampled,
                "profile_regions_with_samples": nsamp, "profile_total_samples": S, "profile_coverage": coverage,
                "expected_share_zero_sample_draws_if_no_credit_branch": UNIFORM * (1 - nsamp / NREG) if S else 1.0,
                "draws_after_first_credit": credited_draws, "draws_equal_to_best_credited_region": exploit_equal if is_pop else ""})
    if r["id"] == "ds_pop_I3_s1":
        lab = {}
        for x in rows: lab[x.get("region")] = x.get("label")
        pj = jload(d0 / "profile.json", {}); labs = {t["id"]: t["label"] for t in pj.get("top_regions", [])}
        top_example = [{"rank": i + 1, "region_id": g, "label": labs.get(g, lab.get(g, "")), "samples": samples[g], "share_of_attributed_samples_pct": 100 * samples[g] / S,
                        "p_weighted_draw_pct": 100 * (1 - UNIFORM) * samples[g] / S + 100 * UNIFORM / NREG,
                        "p_draw_population_arm_no_credit_yet_pct": 100 * (1 - UNIFORM) * samples[g] / S + 100 * UNIFORM / NREG,
                        "draws_observed_in_this_run": cnt.get(g, 0)} for i, g in enumerate(sorted(samples, key=samples.get, reverse=True)[:10])]
write_csv(PM / "tables/region_selection_by_run.csv", out)
write_csv(PM / "tables/region_probability_example_ds_pop_I3_s1.csv", top_example)
# per configuration summary
agg = []
for cid, label, algo, model, impl in CONFIGS:
    rs = [o for o in out if o["config"] == cid]
    agg.append({"config": cid, "runs": len(rs), "draws_total": sum(o["independent_draws"] for o in rs), "distinct_regions_median": median([o["distinct_regions_drawn"] for o in rs]),
                "repeat_draws_median": median([o["repeat_draws"] for o in rs]), "max_times_one_region_median": median([o["max_times_one_region"] for o in rs]),
                "zero_sample_draw_share_observed": sum(o["draws_in_zero_sample_regions"] for o in rs) / max(1, sum(o["independent_draws"] for o in rs)),
                "top5_profile_region_share_observed": sum(o["draws_in_top5_profile_regions"] for o in rs) / max(1, sum(o["independent_draws"] for o in rs)),
                "credit_branch_active_in_algorithm": algo == "population"})
write_csv(PM / "tables/region_selection_by_config.csv", agg)
if __name__ == "__main__":
    print("regions indexed:", NREG); print(json.dumps(top_example[:6], indent=0)[:900])
    for a in agg: print(a)
    for o in out[:0]: print(o)
    print([ (o["run"], o["draws_equal_to_best_credited_region"], o["draws_after_first_credit"]) for o in out if o["algorithm"]=="population"])
