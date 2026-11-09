#!/usr/bin/env python3
"""B. False-accept evidence: synthetic null pairs and the real-SDK inert patch, kept apart, by node class and by batch. Recomputed from raw timings."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pm_lib import *

def node_class(host):
    return "xcnc" if (host or "").startswith("xcnc") else ("xcnd" if (host or "").startswith("xcnd") else "other")

def eval_files(files):
    out = []
    for f in files:
        r = rule(jload(f))
        if r:
            out.append(r)
    return out

batches = []   # (label, family, node_class, host, job, results)
# synthetic null: Phase 0 (both batches of the 'null' pair, node xcnc2)
for bname, base in (("phase0-batch1", ROOT / "runs/phase0-1068829"), ("phase0-batch2", ROOT / "runs/phase0b-1069564")):
    nd = kv(base / "node.txt")
    batches.append((bname, "synthetic null", "xcnc", nd.get("host") or nd.get("NodeList") or "xcnc2", nd.get("job", ""), eval_files(sorted((base / "trials/null").glob("t*.json")))))
for d in sorted((ROOT / "runs/round2/fpr").glob("null-*")):
    nd = kv(d / "node.txt")
    batches.append((d.name, "synthetic null", node_class(nd.get("host")), nd.get("host"), nd.get("job"), eval_files(sorted((d / "trials").glob("t*.json")))))
for d in sorted((ROOT / "runs/followup").glob("sdk-inert-*")):
    nd = kv(d / "node.txt")
    batches.append((d.name, "SDK inert (follow-up batches)", node_class(nd.get("host")), nd.get("host"), nd.get("job"), eval_files(sorted((d / "evaluate-inert").glob("m*.json")))))
for d in sorted((ROOT / "runs/round2/fpr").glob("sdk-inert-*")):
    nd = kv(d / "node.txt")
    batches.append((d.name, "SDK inert (round-2 batches)", node_class(nd.get("host")), nd.get("host"), nd.get("job"), eval_files(sorted((d / "evaluate-inert").glob("m*.json")))))
# the 5 hand-run measurements of the inert patch in the controls job (kept separate)
ctrl = ROOT / "runs/controls-1068897/eval-inert/evaluate-inert"
batches.append(("controls-1068897-eval-inert", "SDK inert (controls job)", "xcnd", "xcnd24", "1068897", eval_files(sorted(ctrl.glob("m*.json")))))

def tally(label, family, rows):
    n = len(rows)
    k = sum(1 for r in rows if r["faster"])
    lo, hi = cp(k, n) if n else (float("nan"),) * 2
    ratios = [r["ratio"] for r in rows]
    pat = {}
    for r in rows:
        key = ("D" if r["dir_ok"] else "-") + ("P" if r["p_ok"] else "-") + ("M" if r["mag_ok"] else "-")
        pat[key] = pat.get(key, 0) + 1
    acs = [r["ac_median"] for r in rows]
    return {"group": label, "family": family, "valid_measurements": n, "false_accepts": k, "rate": k / n if n else float("nan"), "cp95_lo": lo, "cp95_hi": hi,
            "p_below_alpha_any_direction": sum(1 for r in rows if r["p_ok"]), "p_pass_and_direction_ok_but_blocked_by_2pct_gate": pat.get("DP-", 0),
            "unstable": sum(1 for r in rows if r["unstable"]),
            "ratio_median": median(ratios) if n else "", "ratio_min": min(ratios) if n else "", "ratio_max": max(ratios) if n else "",
            "ratio_sd": float(np.std(ratios, ddof=1)) if n > 1 else "", "ratio_p01": float(np.percentile(ratios, 1)) if n else "", "ratio_p99": float(np.percentile(ratios, 99)) if n else "",
            "lag1_ac_median_of_measurement_medians": median(acs) if n else "", "lag1_ac_min": min(acs) if n else "", "lag1_ac_max": max(acs) if n else "",
            "pvalue_min": min(r["p"] for r in rows) if n else "", "gate_patterns_DPM": json.dumps(pat, sort_keys=True)}

by_batch = []
for lab, fam, cls, host, job, rows in batches:
    t = tally(lab, fam, rows); t.update({"node_class": cls, "host": host, "job": job}); by_batch.append(t)
write_csv(PM / "tables/fpr_by_batch.csv", by_batch)
groups = []
def add(label, fam, sel):
    rows = [r for (lab, f, cls, h, j, rr) in batches if sel(lab, f, cls) for r in rr]
    t = tally(label, fam, rows); groups.append(t); return t
add("Synthetic null, calibration batches (xcnc2, 2 batches)", "synthetic null", lambda l, f, c: l.startswith("phase0"))
add("Synthetic null, extra batches, xcnc", "synthetic null", lambda l, f, c: l.startswith("null-") and c == "xcnc")
add("Synthetic null, extra batches, xcnd", "synthetic null", lambda l, f, c: l.startswith("null-") and c == "xcnd")
add("Synthetic null, all xcnc (calibration + extra)", "synthetic null", lambda l, f, c: f == "synthetic null" and c == "xcnc")
add("Synthetic null, all", "synthetic null", lambda l, f, c: f == "synthetic null")
add("SDK inert, batch group A, xcnc", "SDK inert", lambda l, f, c: f.startswith("SDK inert (follow") and c == "xcnc")
add("SDK inert, batch group A, xcnd", "SDK inert", lambda l, f, c: f.startswith("SDK inert (follow") and c == "xcnd")
add("SDK inert, batch group B, xcnc", "SDK inert", lambda l, f, c: f.startswith("SDK inert (round") and c == "xcnc")
add("SDK inert, batch group B, xcnd", "SDK inert", lambda l, f, c: f.startswith("SDK inert (round") and c == "xcnd")
add("SDK inert, all batches, xcnc", "SDK inert", lambda l, f, c: f.startswith("SDK inert (") and "controls" not in f and c == "xcnc")
add("SDK inert, all batches, xcnd", "SDK inert", lambda l, f, c: f.startswith("SDK inert (") and "controls" not in f and c == "xcnd")
add("SDK inert, all batches, both classes", "SDK inert", lambda l, f, c: f.startswith("SDK inert (") and "controls" not in f)
add("SDK inert, controls job (5 hand-run measurements, xcnd24)", "SDK inert", lambda l, f, c: "controls" in f)
write_csv(PM / "tables/fpr_summary.csv", groups)
# per-measurement rows for figures
fig = []
for lab, fam, cls, host, job, rows in batches:
    for r in rows:
        fig.append({"batch": lab, "family": fam, "node_class": cls, "ratio": r["ratio"], "p": r["p"], "faster": r["faster"], "ac_median": r["ac_median"], "spread": r["spread"]})
write_csv(PM / "figure_data/fpr_measurements.csv", fig)
src("fpr-1", "false-accept counts, CP intervals, ratio distribution, autocorrelation for synthetic null and SDK inert", "runs/phase0*/trials/null, runs/round2/fpr/null-*/trials, runs/followup/sdk-inert-*/evaluate-inert, runs/round2/fpr/sdk-inert-*/evaluate-inert",
    "timings.process[*]", "pm_lib.rule() replay per measurement; exact Clopper-Pearson; lag-1 autocorrelation of each process's candidate_ns series, median over the 10 processes, then summarised over measurements")
if __name__ == "__main__":
    for g in groups:
        print(f"{g['group']:62s} n={g['valid_measurements']:4d} k={g['false_accepts']} CP=[{100*g['cp95_lo']:.3f}%,{100*g['cp95_hi']:.3f}%] p<a={g['p_below_alpha_any_direction']} blocked_by_gate={g['p_pass_and_direction_ok_but_blocked_by_2pct_gate']} unst={g['unstable']} ratio med {g['ratio_median']:.5f} [{g['ratio_min']:.5f},{g['ratio_max']:.5f}] ac med {g['lag1_ac_median_of_measurement_medians']:.3f} [{g['lag1_ac_min']:.2f},{g['lag1_ac_max']:.2f}]")
    print(len(by_batch), "batches")
