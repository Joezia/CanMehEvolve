#!/usr/bin/env python3
"""Collect every number the report quotes, from raw/recomputed files; dump them to report/numbers.json.

Sources (all produced from raw logs by earlier scripts, none typed by hand):
  runs/phase0b-1069564/final/rule_rows.jsonl   per-trial output of the frozen rule on the Phase 0 trial files (both batches)
  runs/phase0-1068829/calibration.json         the 12-pair self-check (units, per-pair min_time, refusal stages)
  runs/phase1-final/{recomputed_stats,autocorr,run_facts,phase1_final}.json, runs/controls-*/...
Run order: recompute_stats.py, autocorr_report.py, collect_run_facts.py, then this module (imported by build_report.py).
"""
import json, re, statistics as st
from pathlib import Path
from scipy.stats import beta

ROOT = Path(__file__).resolve().parent.parent
J = lambda p: json.load(open(ROOT / p))


def cp(k, n, a=0.05):
    lo = 0.0 if k == 0 else beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - a / 2, k + 1, n - k)
    return lo, hi


def phase0():
    rows = [json.loads(l) for l in open(ROOT / "runs/phase0b-1069564/final/rule_rows.jsonl") if l.strip()]
    cal = {p["pair"]: p for p in J("runs/phase0-1068829/calibration.json")["pairs"]}
    out = {}
    for pair in ["null", "faster-1-percent", "faster-2-percent", "faster-5-percent", "faster-10-percent", "slower-10-percent",
                 "sweep-105", "sweep-110", "sweep-200", "sweep-400"]:
        rs = [r for r in rows if re.search(r"trials/%s/" % re.escape(pair), r["file"]) and r.get("valid")]
        c = cal[pair]
        true = c["candidate_units"] / c["reference_units"]
        k = sum(1 for r in rs if r["faster"])
        med = st.median(r["ratio"] for r in rs)
        lo, hi = cp(k, len(rs))
        out[pair] = {"reference_units": c["reference_units"], "candidate_units": c["candidate_units"], "min_time": c["min_time"], "true_ratio": true,
                     "trials": len(rs), "accepted": k, "cp95": [lo, hi], "median_reported_ratio": med, "bias": med - true, "unstable": sum(1 for r in rs if r["unstable"]),
                     "batches": sorted({r["batch"] for r in rs})}
    out["_refused"] = {p: {"stage": cal[p]["stage"], "error": cal[p]["error"][:90]} for p in ("broken-digest", "shared-install-name")}
    out["_selfcheck_all_as_expected"] = all(p["as_expected"] for p in cal.values())
    return out


def load():
    N = {"phase0": phase0()}
    N["stats"] = J("runs/phase1-final/recomputed_stats.json")
    N["autocorr"] = J("runs/phase1-final/autocorr.json")
    N["facts"] = J("runs/phase1-final/run_facts.json")
    ex = J("runs/phase1-final/phase1_final.json")
    N["controls"] = {c["control"]: c for c in ex["controls"]}
    N["runs"] = [r for r in ex["runs"] if r["experiment"] == "deepseek"]
    N["common34"] = ex["common_budget_34"]
    # C2: timestamps of the human-control files (file modification times; no stopwatch record exists)
    hc = ROOT / "runs/human-control/c2-1058781"
    mt = sorted((p.stat().st_mtime, p.name) for p in hc.iterdir() if p.is_file())
    import datetime as dt
    N["c2"] = {"first_file": [dt.datetime.fromtimestamp(mt[0][0]).isoformat(timespec="seconds"), mt[0][1]],
               "last_file": [dt.datetime.fromtimestamp(mt[-1][0]).isoformat(timespec="seconds"), mt[-1][1]],
               "span_min": (mt[-1][0] - mt[0][0]) / 60,
               "attempt1_patch_time": dt.datetime.fromtimestamp((hc / "attempt-1.patch").stat().st_mtime).isoformat(timespec="seconds"),
               "attempt2_patch_time": dt.datetime.fromtimestamp((hc / "attempt-2.patch").stat().st_mtime).isoformat(timespec="seconds")}
    first_search = min((p.stat().st_mtime for p in (ROOT / "runs").glob("main/*/results.jsonl")), default=None)
    N["c2"]["earliest_search_results_file"] = dt.datetime.fromtimestamp(first_search).isoformat(timespec="seconds") if first_search else None
    return N


if __name__ == "__main__":
    N = load()
    (ROOT / "report").mkdir(parents=True, exist_ok=True)
    (ROOT / "report/numbers.json").write_text(json.dumps(N, indent=1, default=str) + "\n")
    print(json.dumps(N["phase0"], indent=1)[:3000]); print(N["c2"])
