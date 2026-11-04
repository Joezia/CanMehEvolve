#!/usr/bin/env python3
"""Aggregate the main matrix: one row per run, medians/ranges per arm, and the figure.

Usage: aggregate.py runs/main  [out_dir]
Every number is read from a run's own files (summary.json, credits.csv,
results.jsonl, evaluate-best/summary.json, run.json, node.txt).
"""
import csv, json, statistics, sys
from pathlib import Path

def load(p):
    try: return json.load(open(p))
    except Exception: return None

def jsonl(p):
    try: return [json.loads(l) for l in open(p) if l.strip()]
    except Exception: return []

def run_row(d):
    s = load(d / "summary.json"); run = load(d / "run.json")
    if not s or not run: return None
    ev = load(d / "evaluate-best" / "summary.json")
    res = jsonl(d / "results.jsonl")
    node = dict(l.strip().split("=", 1) for l in open(d / "node.txt") if "=" in l)
    stages = {}
    for r in res: stages[r.get("stage") or "measured"] = stages.get(r.get("stage") or "measured", 0) + 1
    meas = [r for r in res if r.get("ok")]
    best = max((r for r in res if r.get("confirmed")), key=lambda r: r.get("speedup", 0), default=None)
    row = {
        "arm": s["mode"], "seed": s["seed"], "dir": str(d), "host": run["hostname"],
        "job": run["slurm_job_id"], "api_calls": s["api_calls"], "total_tokens": s["total_tokens"],
        "prompt_tokens": s["prompt_tokens"], "completion_tokens": s["completion_tokens"],
        "elapsed_min": round(s["elapsed_s"] / 60, 1), "ended_because": s["ended_because"],
        "model_requested": run["model_requested"], "model_returned": run["model_probe"].get("model"),
        "measured": len(meas), "confirmed": s["confirmed_candidates"],
        "improved_on_parent": s["improved_on_parent_candidates"], "stages": stages,
        "search_best_confirmed_speedup": s["best_confirmed_speedup"],
        "search_best_confirmed_generation": s["best_confirmed_generation"],
        "search_best_retained_speedup": s["best_retained_speedup"],
        "best_label": best["label"] if best else None,
        "baseline_ms": run["meta"].get("baseline_ms"), "null_ok": run["null_evidence"].get("null_ok"),
        "git_commit": run["git_commit"], "git_dirty": run["git_dirty"],
    }
    if ev and ev.get("valid_measurements"):
        row["final_ratios"] = [m["analysis"]["ratio"] for m in ev["measurements"] if m["analysis"]["valid"]]
        row["final_passes"] = ev["measurements_passing_rule"]
        row["final_median_speedup"] = ev["median_speedup"]
        row["final_worst_speedup"] = 1.0 / ev["worst_ratio"]
        # claim = what survives the independent re-measurement: all three must pass the rule
        row["final_confirmed_speedup"] = ev["median_speedup"] if ev["all_pass"] else 1.0
    else:
        row["final_confirmed_speedup"] = 1.0
    row["bonus_quotient"] = (row["final_confirmed_speedup"] - 1.0) / max(1, row["total_tokens"])
    return row

def arm_summary(rows, key):
    v = [r[key] for r in rows if r.get(key) is not None]
    return {"n": len(v), "median": statistics.median(v), "min": min(v), "max": max(v)} if v else None

def main(root, out):
    root = Path(root); out = Path(out); out.mkdir(parents=True, exist_ok=True)
    rows = [r for r in (run_row(d) for d in sorted(root.glob("*-s*-*")) if d.is_dir()) if r]
    rows.sort(key=lambda r: (r["arm"], r["seed"]))
    summary = {"runs": rows, "arms": {}}
    for arm in sorted({r["arm"] for r in rows}):
        a = [r for r in rows if r["arm"] == arm]
        summary["arms"][arm] = {k: arm_summary(a, k) for k in
            ["search_best_confirmed_speedup", "final_confirmed_speedup", "final_median_speedup",
             "total_tokens", "api_calls", "confirmed", "improved_on_parent", "bonus_quotient", "elapsed_min"]}
    (out / "matrix_summary.json").write_text(json.dumps(summary, indent=2))
    with open(out / "matrix_runs.csv", "w", newline="") as f:
        cols = ["arm", "seed", "host", "job", "api_calls", "total_tokens", "elapsed_min", "measured", "confirmed",
                "improved_on_parent", "search_best_confirmed_speedup", "final_median_speedup",
                "final_confirmed_speedup", "bonus_quotient", "best_label", "model_returned", "ended_because"]
        w = csv.DictWriter(f, cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    for r in rows:
        print(f'{r["arm"]:8s} s{r["seed"]} {r["host"]:7s} calls={r["api_calls"]:3d} tok={r["total_tokens"]:7d} '
              f'meas={r["measured"]:2d} conf={r["confirmed"]:2d} search_best={r["search_best_confirmed_speedup"]:.4f} '
              f'final={r.get("final_median_speedup", float("nan")):.4f} claim={r["final_confirmed_speedup"]:.4f} '
              f'stages={r["stages"]}')
    for arm, s in summary["arms"].items(): print(arm, json.dumps(s["final_confirmed_speedup"]), json.dumps(s["total_tokens"]))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "runs/analysis")
