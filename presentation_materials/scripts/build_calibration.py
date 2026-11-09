#!/usr/bin/env python3
"""A. Known-ratio calibration (Phase 0): every number recomputed from the raw per-trial timings of both batches
(runs/phase0-1068829/trials, runs/phase0b-1069564/trials) with the independent rule replay in pm_lib.rule()."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pm_lib import *

B1, B2 = ROOT / "runs/phase0-1068829", ROOT / "runs/phase0b-1069564"
cal = jload(B1 / "calibration.json")
units = {}
for p in cal["pairs"]:
    units[p["pair"]] = (p["reference_units"], p["candidate_units"])
main_pairs = ["null", "faster-1-percent", "faster-2-percent", "faster-5-percent", "faster-10-percent", "slower-10-percent"]
sweeps = ["sweep-105", "sweep-110", "sweep-200", "sweep-400"]
stored = {}
for r in jl(B2 / "final/rule_rows.jsonl"):
    stored[r["path"]] = r
rows, trial_rows, mismatch = [], [], 0
for pair in main_pairs + sweeps:
    allv = []          # per batch lists in trial order
    for bname, base in (("batch1", B1), ("batch2", B2)):
        d = base / "trials" / pair
        if not d.exists():
            continue
        for f in sorted(d.glob("t*.json")):
            reply = jload(f)
            r = rule(reply) if reply else None
            rel = str(f.relative_to(ROOT))
            if r is None:
                trial_rows.append({"pair": pair, "batch": bname, "trial": f.stem, "valid": False})
                continue
            s = stored.get(rel)
            if s is not None and (s["faster"] != r["faster"] or abs(s["ratio"] - r["ratio"]) > 1e-9 or abs(s["p_value"] - r["p"]) > 1e-12):
                mismatch += 1
            trial_rows.append({"pair": pair, "batch": bname, "trial": f.stem, "valid": True, "ratio": r["ratio"], "p": r["p"], "spread": r["spread"],
                               "faster": r["faster"], "reason": r["reason"], "unstable": r["unstable"], "ac_median": r["ac_median"],
                               "dir_ok": r["dir_ok"], "p_ok": r["p_ok"], "mag_ok": r["mag_ok"]})
tr = {}
for t in trial_rows:
    tr.setdefault(t["pair"], []).append(t)
for pair in main_pairs + sweeps:
    ref, cand = units[pair]
    true = cand / ref
    v = [t for t in tr[pair] if t["valid"]]
    n = len(v)
    k = sum(1 for t in v if t["faster"])
    lo, hi = cp(k, n)
    med = median([t["ratio"] for t in v])
    pat = {}
    for t in v:
        key = ("D" if t["dir_ok"] else "-") + ("P" if t["p_ok"] else "-") + ("M" if t["mag_ok"] else "-")
        pat[key] = pat.get(key, 0) + 1
    reasons = {}
    for t in v:
        key = "pass" if t["faster"] else t["reason"]
        reasons[key] = reasons.get(key, 0) + 1
    # exact-boundary check: the 2% gate applies to the median ratio vs 0.98, while the pair's true ratio is on either side of it
    # offline two-stage pairing (adjacent, disjoint, same batch): (t1,t2),(t3,t4)...
    pairs_n = pairs_k = 0
    for bname in ("batch1", "batch2"):
        seq = [t for t in tr[pair] if t["batch"] == bname]
        for i in range(0, len(seq) - 1, 2):
            if seq[i]["valid"] and seq[i + 1]["valid"]:
                pairs_n += 1
                pairs_k += 1 if (seq[i]["faster"] and seq[i + 1]["faster"]) else 0
    lo2, hi2 = cp(pairs_k, pairs_n) if pairs_n else (float("nan"),) * 2
    rows.append({"pair": pair, "reference_units": ref, "candidate_units": cand, "true_ratio_exact": true, "true_reduction_pct": 100 * (1 - true),
                 "true_speedup": 1 / true, "valid_trials": n, "judged_faster": k, "rate": k / n, "cp95_lo": lo, "cp95_hi": hi,
                 "median_reported_ratio": med, "abs_bias": med - true, "rel_error_pct": 100 * (med - true) / true,
                 "reported_ratio_min": min(t["ratio"] for t in v), "reported_ratio_max": max(t["ratio"] for t in v),
                 "gate_patterns_DPM": json.dumps(pat, sort_keys=True), "p_pass_blocked_by_magnitude_only": pat.get("DP-", 0),
                 "reject_direction": reasons.get("direction", 0), "reject_p_only": reasons.get("p", 0), "reject_magnitude_only": reasons.get("magnitude", 0),
                 "two_stage_pairs": pairs_n, "two_stage_accepted": pairs_k, "two_stage_cp_lo": lo2, "two_stage_cp_hi": hi2,
                 "batches": "1+2" if pair in main_pairs else "1 only", "lag1_ac_median_over_trials": median([t["ac_median"] for t in v])})
write_csv(PM / "tables/calibration_pairs.csv", rows)
write_csv(PM / "tables/calibration_trials.csv", trial_rows)
# detection summary
det = [r for r in rows if r["pair"].startswith("faster")]
ge90 = [r for r in det if r["rate"] >= 0.9]
weakest = min(ge90, key=lambda r: r["true_reduction_pct"])
# deliberately wrong pairs
wrong = [{"pair": p["pair"], "expected_stage": p["expected_stage"], "observed_stage": p.get("stage"), "as_expected": p["as_expected"], "message": p.get("error", "")}
         for p in cal["pairs"] if p["pair"] in ("broken-digest", "shared-install-name")]
write_csv(PM / "tables/calibration_wrong_pairs.csv", wrong)
json.dump({"rule_replay_mismatches_vs_stored_rule_rows": mismatch, "n_trial_files": len(trial_rows), "unreadable": [t for t in trial_rows if not t["valid"]],
           "weakest_effect_ge90pct": {"pair": weakest["pair"], "true_reduction_pct": weakest["true_reduction_pct"], "rate": weakest["rate"]}},
          open(PM / "tables/calibration_checks.json", "w"), indent=1)
src("cal-1", "calibration rate / CP / bias per pair", "runs/phase0-1068829/trials/*, runs/phase0b-1069564/trials/*", "timings.process[*].candidate_ns/reference_ns",
    "pm_lib.rule() replay per trial; rate=k/n; exact Clopper-Pearson; bias=median reported ratio - candidate_units/reference_units")
src("cal-2", "two deliberately wrong pairs rejected at stages correctness / load", "runs/phase0-1068829/calibration.json", "pairs[].stage", "copied")
if __name__ == "__main__":
    print("replay mismatches vs stored:", mismatch, "files:", len(trial_rows))
    for r in rows:
        print(f"{r['pair']:20s} n={r['valid_trials']:3d} k={r['judged_faster']:3d} {r['rate']:.3f} [{r['cp95_lo']:.4f},{r['cp95_hi']:.4f}] true={r['true_ratio_exact']:.5f} med={r['median_reported_ratio']:.5f} bias={r['abs_bias']:+.5f} rel={r['rel_error_pct']:+.3f}% 2stage={r['two_stage_accepted']}/{r['two_stage_pairs']} rej(dir/p/mag)={r['reject_direction']}/{r['reject_p_only']}/{r['reject_magnitude_only']}")
    print("weakest>=90%:", weakest["pair"], weakest["true_reduction_pct"], weakest["rate"]); print(wrong)
