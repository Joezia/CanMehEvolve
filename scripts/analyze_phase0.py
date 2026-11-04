#!/usr/bin/env python3
"""Summarise Phase 0: false-positive rate, detection rates, bias, autocorrelation.

Reads runs/phase0-<job>/rule-<pair>.jsonl (written by `CanMehSearch --rule-eval`)
and each pair's true ratio from build/calibration/<pair>/meta.json. Prints a
JSON summary and writes phase0_summary.json next to the inputs.
Usage: analyze_phase0.py runs/phase0-<job>
"""
import json, math, statistics, sys
from pathlib import Path

def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p**i * (1 - p)**(n - i) for i in range(0, k + 1))

def clopper_pearson(k, n, alpha=0.05):
    lo = 0.0 if k == 0 else None
    hi = 1.0 if k == n else None
    if lo is None:  # P(X >= k | lo) = alpha/2
        a, b = 0.0, 1.0
        for _ in range(100):
            m = (a + b) / 2
            if 1 - binom_cdf(k - 1, n, m) < alpha / 2: a = m
            else: b = m
        lo = (a + b) / 2
    if hi is None:  # P(X <= k | hi) = alpha/2
        a, b = 0.0, 1.0
        for _ in range(100):
            m = (a + b) / 2
            if binom_cdf(k, n, m) > alpha / 2: a = m
            else: b = m
        hi = (a + b) / 2
    return lo, hi

def wilson(k, n, z=1.959964):
    if n == 0: return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)

def main(root):
    root = Path(root)
    summary = {"dir": str(root), "pairs": {}}
    for f in sorted(root.glob("rule-*.jsonl")):
        pair = f.stem[len("rule-"):]
        meta = json.load(open(Path("build/calibration") / pair / "meta.json"))["calibration"]
        true_ratio = meta["candidate_units"] / meta["reference_units"]
        rows = [json.loads(l) for l in open(f) if l.strip()]
        valid = [r for r in rows if r.get("valid")]
        fast = [bool(r["faster"]) for r in valid]
        n, k = len(valid), sum(fast)
        ratios = [r["ratio"] for r in valid]
        # two-stage protocol: disjoint consecutive trial pairs, both must pass
        pairs = [(fast[i], fast[i + 1]) for i in range(0, n - 1, 2)]
        k2 = sum(1 for a, b in pairs if a and b)
        acs = [r["autocorr_lag1_median"] for r in valid]
        entry = {
            "true_ratio": true_ratio, "trials": len(rows), "valid_trials": n,
            "reported_faster": k, "rate": k / n if n else None,
            "clopper_pearson_95": clopper_pearson(k, n), "wilson_95": wilson(k, n),
            "two_stage_trials": len(pairs), "two_stage_faster": k2,
            "two_stage_clopper_pearson_95": clopper_pearson(k2, len(pairs)),
            "median_reported_ratio": statistics.median(ratios) if ratios else None,
            "mean_reported_ratio": statistics.mean(ratios) if ratios else None,
            "bias_median": statistics.median(ratios) - true_ratio if ratios else None,
            "bias_mean": statistics.mean(ratios) - true_ratio if ratios else None,
            "reported_ratio_range": [min(ratios), max(ratios)] if ratios else None,
            "reported_ratio_sd": statistics.pstdev(ratios) if len(ratios) > 1 else None,
            "median_p": statistics.median([r["p_value"] for r in valid]) if valid else None,
            "autocorr_lag1_median_of_medians": statistics.median(acs) if acs else None,
            "autocorr_lag1_min_of_mins": min((r["autocorr_lag1_min"] for r in valid), default=None),
            "autocorr_lag1_max_of_maxes": max((r["autocorr_lag1_max"] for r in valid), default=None),
            "min_time": valid[0].get("min_time") if valid else None,
        }
        summary["pairs"][pair] = entry
    eff = [(p, e) for p, e in summary["pairs"].items() if p.startswith("faster-")]
    eff.sort(key=lambda pe: pe[1]["true_ratio"], reverse=True)
    summary["detection_threshold"] = next(
        ({"pair": p, "true_ratio": e["true_ratio"]} for p, e in sorted(eff, key=lambda pe: -pe[1]["true_ratio"])
         if e["rate"] is not None and e["rate"] >= 0.9), None)
    # smallest effect (closest to 1) at which ALL larger effects also reach 0.9
    ok = [e["rate"] >= 0.9 for _, e in sorted(eff, key=lambda pe: pe[1]["true_ratio"])]
    summary["detection_threshold_note"] = "first pair, scanning from the weakest effect, with rate >= 0.9 (rates at every size are in `pairs`)"
    (root / "phase0_summary.json").write_text(json.dumps(summary, indent=2))
    for p, e in summary["pairs"].items():
        cp = e["clopper_pearson_95"]
        print(f'{p:20s} true={e["true_ratio"]:.4f} n={e["valid_trials"]:3d} faster={e["reported_faster"]:3d} '
              f'rate={e["rate"]:.3f} CP=[{cp[0]:.3f},{cp[1]:.3f}] med_ratio={e["median_reported_ratio"]:.4f} '
              f'bias={e["bias_median"]:+.4f} ac1={e["autocorr_lag1_median_of_medians"]:+.2f}')
    print("detection threshold:", summary["detection_threshold"])

if __name__ == "__main__":
    main(sys.argv[1])
