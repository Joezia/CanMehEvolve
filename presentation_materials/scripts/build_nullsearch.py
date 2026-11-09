#!/usr/bin/env python3
"""C. Null search: the greedy rank rule on no-op candidates (8 runs x 36 measured candidates, runs/followup/null-search-*), replayed from the raw
measurement files with the independent rule, and compared with the update steps of the real DeepSeek greedy chains (runs/deepseek + resume).
Definitions (all in ratio of candidate/reference medians, relative to stock = 1.000):
  update          = the rank rule moved the record: r1 stable and < record, r2 measured, both stable, R=max(r1,r2) < record.
  step size (%)   = 100 * (1 - R_new / R_previous)      (percent of the previous record; unit %)
  false progress  = 100 * (1 - final record)            (percent reduction of the ratio, = what a chain would claim from noise alone)
"""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pm_lib import *

runs, steps_all, mism = [], [], 0
for d in sorted((ROOT / "runs/followup").glob("null-search-x*")):
    steps = jl(d / "steps.jsonl")
    record, upd, nmeas, first_stage = 1.0, [], 0, {}
    rows = []
    for s in steps:
        if s.get("stage") != "measured":
            continue
        a = s["attempt"]
        m1 = rule(jload(d / "measurements" / f"a{a:03d}.m1.json"))
        if not m1:
            continue
        nmeas += 1
        possibly = (not m1["unstable"]) and m1["ratio"] < record
        updated, R, r2 = False, m1["ratio"], None
        if possibly:
            m2 = rule(jload(d / "measurements" / f"a{a:03d}.m2.json"))
            if m2 and not m2["unstable"]:
                r2 = m2["ratio"]; R = max(m1["ratio"], m2["ratio"])
                if R < record:
                    updated = True
        if updated != bool(s.get("updated")):
            mism += 1
        step = 100 * (1 - R / record) if updated else 0.0
        rows.append({"run": d.name, "attempt": a, "record_before": record, "r1": m1["ratio"], "r2": r2, "updated": updated, "R": R, "step_pct": step,
                     "rule_pass_1": m1["faster"]})
        if updated:
            upd.append(step); record = R
    node = kv(d / "node.txt")
    summ = jload(d / "summary.json", {})
    runs.append({"run": d.name, "node": node.get("host"), "seed": summ.get("seed"), "measured_candidates": nmeas, "updates": len(upd), "final_record": record,
                 "false_progress_pct": 100 * (1 - record), "false_speedup": 1 / record, "max_single_update_pct": max(upd) if upd else 0.0,
                 "median_update_pct": median(upd) if upd else "", "any_candidate_passed_rule_single": any(r["rule_pass_1"] for r in rows),
                 "stored_final_record": summ.get("final_record")})
    steps_all += rows
write_csv(PM / "tables/null_search_runs.csv", runs)
write_csv(PM / "figure_data/null_search_steps.csv", steps_all)
allupd = [r["step_pct"] for r in steps_all if r["updated"]]
# real greedy chains: rank_updates of the final (40-request) state of the five DeepSeek greedy runs
real = []
for s in range(1, 6):
    cands = sorted((ROOT / "runs/followup").glob(f"resume-greedy-s{s}-*")) or sorted((ROOT / f"runs/deepseek").glob(f"greedy-s{s}-*-resume-*"))
    d = cands[-1] if cands else sorted((ROOT / "runs/deepseek").glob(f"greedy-s{s}-[0-9]*"))[0]
    if s == 1:
        d = sorted((ROOT / "runs/deepseek").glob("greedy-s1-1072019-resume-*"))[0]
    sm = jload(d / "summary.json")
    for u in sm["rank_updates"]:
        real.append({"seed": s, "generation": u["generation"], "label": u["label"], "previous_R": u["previous_R"], "R": u["R"], "step_pct": 100 * (1 - u["R"] / u["previous_R"]),
                     "source": str(d.relative_to(ROOT))})
write_csv(PM / "tables/greedy_real_update_steps.csv", real)
mx = max(allupd)
ks = [r["step_pct"] for r in real]
out = {"null_runs": len(runs), "candidates_per_run": sorted({r["measured_candidates"] for r in runs}), "updates_per_run": [r["updates"] for r in runs], "total_updates": len(allupd),
       "max_single_update_pct": mx, "median_single_update_pct": median(allupd), "false_progress_pct_per_run": [round(r["false_progress_pct"], 4) for r in runs],
       "false_progress_median": median([r["false_progress_pct"] for r in runs]), "false_progress_max": max(r["false_progress_pct"] for r in runs),
       "real_greedy_steps": len(ks), "real_steps_leq_max_null_step": sum(1 for k in ks if k <= mx), "real_steps_leq_0.2pct": sum(1 for k in ks if k <= 0.2),
       "real_steps_leq_0.5pct": sum(1 for k in ks if k <= 0.5), "real_median_step_pct": median(ks), "real_max_step_pct": max(ks),
       "replay_vs_stored_update_mismatches": mism, "any_null_candidate_passed_single_rule": any(r["any_candidate_passed_rule_single"] for r in runs)}
json.dump(out, open(PM / "tables/null_search_summary.json", "w"), indent=1)
src("null-1", "null-search updates, drift, max single step", "runs/followup/null-search-*/measurements/a*.m1/m2.json", "timings", "rank rule replay (see script docstring)")
if __name__ == "__main__":
    for r in runs: print(r["run"], r["node"], r["measured_candidates"], "upd", r["updates"], f"final {r['final_record']:.5f}", f"max step {r['max_single_update_pct']:.4f}%", "passed_rule", r["any_candidate_passed_rule_single"])
    print(json.dumps(out, indent=1))
