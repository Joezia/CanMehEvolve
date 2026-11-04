#!/usr/bin/env python3
"""Lag-1 sample autocorrelation of each process's candidate_ns series, recomputed from the raw measurement files.

Formula (README, Phase 0): r1 = sum_i (x[i]-m)(x[i+1]-m) / sum_i (x[i]-m)^2, m = that series' own mean, over the 9 repetitions of
one process.  Per measurement (10 processes) we take the median and the range across processes, as the README asks; groups then
summarise those per-measurement numbers and also give the pooled range of single series.  Nine values per series give each r1 a
standard error near 1/sqrt(9) = 0.33, so single values are not interpretable on their own.

Inputs are raw `timings` blocks (`measure-pair` / `measure-patch --no-decision` output); nothing is read from a rule's rounded output.
The recomputed per-measurement medians are checked against the autocorr_lag1_median stored by the frozen rule on the same Phase 0 files.
Writes runs/phase1-final/autocorr.json and autocorr.md.
"""
import glob, json, statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def lag1(x):
    m = sum(x) / len(x)
    den = sum((v - m) ** 2 for v in x)
    return float("nan") if den == 0 else sum((x[i] - m) * (x[i + 1] - m) for i in range(len(x) - 1)) / den


def measurement(path):
    try:
        d = json.load(open(path))
    except Exception:          # e.g. the 0-byte interrupted file runs/phase0-1068829/trials/null/t051.json, kept but unreadable
        return None
    procs = (d.get("timings") or {}).get("process")
    if not procs:
        return None
    rs = [lag1(p["candidate_ns"]) for p in procs if len(p.get("candidate_ns", [])) >= 3]
    return rs or None


def summarise(files):
    meds, mins, maxs, pooled = [], [], [], []
    for f in files:
        rs = measurement(f)
        if not rs:
            continue
        meds.append(st.median(rs))
        mins.append(min(rs))
        maxs.append(max(rs))
        pooled += rs
    if not meds:
        return None
    return {"n_measurements": len(meds), "n_series": len(pooled),
            "median_of_per_measurement_process_medians": st.median(meds),
            "range_of_per_measurement_process_medians": [min(meds), max(meds)],
            "pooled_single_series_median": st.median(pooled), "pooled_single_series_range": [min(pooled), max(pooled)]}


def trials(batch_glob, pairs):
    out = []
    for p in pairs:
        out += sorted(glob.glob(str(ROOT / batch_glob / p / "t*.json")))
    return out


MAIN = ["null", "faster-1-percent", "faster-2-percent", "faster-5-percent", "faster-10-percent", "slower-10-percent"]
SWEEP = ["sweep-105", "sweep-110", "sweep-200", "sweep-400"]
b1, b2 = "runs/phase0-1068829/trials", "runs/phase0b-1069564/trials"
groups = {
    "calibration main pairs (6 pairs, both batches)": trials(b1, MAIN) + trials(b2, MAIN),
    "calibration null pair": trials(b1, ["null"]) + trials(b2, ["null"]),
    "calibration sweep pairs (batch 1 only)": trials(b1, SWEEP),
    "SDK inert patch (stock vs no-op patch)": sorted(glob.glob(str(ROOT / "runs/controls-1068897/eval-inert/**/m*.json"), recursive=True)) +
                                               sorted(glob.glob(str(ROOT / "runs/inert-check/measurement.json"))),
    "SDK DeepSeek search candidates (all measurements)": sorted(glob.glob(str(ROOT / "runs/deepseek/*-s?-[0-9]*/measurements/*.json"))),
    "SDK fixed final patches (3 re-measurements each, 10 runs)": sorted(glob.glob(str(ROOT / "runs/deepseek/*-s?-[0-9]*/evaluate-best/**/m*.json"), recursive=True)),
}
groups = {k: [f for f in v if "resume" not in f] for k, v in groups.items()}
res = {k: summarise(v) for k, v in groups.items()}

# cross-check against the stored value of the frozen rule on the Phase 0 files
chk = []
rows = [json.loads(l) for l in open(ROOT / "runs/phase0b-1069564/final/rule_rows.jsonl") if l.strip()]
for r in rows[:400]:
    f = r.get("file")
    f = str(ROOT / f) if f and not Path(f).is_absolute() else f
    if f and Path(f).exists() and "autocorr_lag1_median" in r and r["autocorr_lag1_median"] is not None:
        mine = measurement(f)
        if mine:
            chk.append(abs(st.median(mine) - r["autocorr_lag1_median"]))
res["_cross_check_vs_stored_rule_output"] = {"files_compared": len(chk), "max_abs_difference": max(chk) if chk else None}

out = ROOT / "runs/phase1-final"
(out / "autocorr.json").write_text(json.dumps(res, indent=2) + "\n")
L = ["# Lag-1 autocorrelation of candidate_ns series (recomputed from raw timings)", "",
     "Per measurement: median and range across its 10 processes (9 repetitions each); groups summarise measurements. SE of one series is about 0.33.", "",
     "| group | measurements | series | median of per-measurement medians | range of per-measurement medians | pooled single series: median [min, max] |", "|---|---|---|---|---|---|"]
for k, v in res.items():
    if k.startswith("_") or not v:
        continue
    L.append("| %s | %d | %d | %+.3f | [%+.3f, %+.3f] | %+.3f [%+.2f, %+.2f] |" % (
        k, v["n_measurements"], v["n_series"], v["median_of_per_measurement_process_medians"], *v["range_of_per_measurement_process_medians"],
        v["pooled_single_series_median"], *v["pooled_single_series_range"]))
L.append("")
L.append("Cross-check: %s" % json.dumps(res["_cross_check_vs_stored_rule_output"]))
(out / "autocorr.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
