"""Shared helpers for the presentation package. Everything is recomputed from raw project files; nothing here starts an experiment.

rule(): an independent Python re-implementation of the decision rule in src/Search.cpp (analyzeTimings / signFlipPValue / candidateIsFaster):
  per process: ratio_p = median(candidate_ns) / median(reference_ns); ratio = median_p(ratio_p); p = exact two-sided sign-flip p of sum(log ratio_p)
  over 2^10 sign patterns; spread = max_p - min_p; unstable iff spread > 0.25; faster iff mean(log ratio_p) < 0 and p < alpha and ratio <= 1 - min_effect.
"""
import csv, glob, json, math, os, statistics as st
from pathlib import Path
import numpy as np
from scipy import stats as sps

ROOT = Path(__file__).resolve().parent.parent.parent
PM = ROOT / "presentation_materials"
ALPHA, MIN_EFFECT, UNSTABLE = 0.01, 0.02, 0.25


def jload(p, default=None):
    try:
        return json.load(open(p))
    except Exception:
        return default


def jl(p):
    out = []
    try:
        for l in open(p, errors="replace"):
            l = l.strip()
            if l:
                try:
                    out.append(json.loads(l))
                except Exception:
                    pass
    except FileNotFoundError:
        pass
    return out


def kv(path):
    d = {}
    try:
        for l in open(path, errors="replace"):
            l = l.strip()
            if "=" in l and not l.startswith("#"):
                k, v = l.split("=", 1)
                d.setdefault(k.strip(), v.strip())
    except FileNotFoundError:
        pass
    return d


def median(x):
    return float(np.median(x)) if len(x) else float("nan")


def cp(k, n, conf=0.95):
    """Exact (Clopper-Pearson) two-sided interval."""
    a = 1 - conf
    lo = 0.0 if k == 0 else sps.beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else sps.beta.ppf(1 - a / 2, k + 1, n - k)
    return float(lo), float(hi)


_masks = {}


def signflip_p(logs):
    n = len(logs)
    if n not in _masks:
        m = np.array([[1 if (mask >> i) & 1 else -1 for i in range(n)] for mask in range(1 << n)], dtype=float)
        _masks[n] = m
    sums = np.abs(_masks[n] @ np.array(logs))
    obs = abs(sum(logs))
    tol = 1e-12 * max(sum(abs(v) for v in logs), 1e-300)
    return float(np.sum(sums >= obs - tol)) / (1 << n)


def rule_from_process_ratios(pr, alpha=ALPHA, min_effect=MIN_EFFECT):
    logs = [math.log(r) for r in pr]
    ratio = median(pr)
    p = signflip_p(logs)
    spread = max(pr) - min(pr)
    mean_log = sum(logs) / len(logs)
    reason = ""
    if not mean_log < 0:
        reason = "direction"
    elif not p < alpha:
        reason = "p"
    elif not ratio <= 1 - min_effect:
        reason = "magnitude"
    return {"ratio": ratio, "p": p, "spread": spread, "unstable": spread > UNSTABLE, "faster": reason == "", "reason": reason,
            "mean_log": mean_log, "n_proc": len(pr), "dir_ok": mean_log < 0, "p_ok": p < alpha, "mag_ok": ratio <= 1 - min_effect}


def acf1(x):
    x = np.asarray(x, float)
    if len(x) < 3:
        return 0.0
    m = x.mean()
    den = float(np.sum((x - m) ** 2))
    return float(np.sum((x[:-1] - m) * (x[1:] - m)) / den) if den > 0 else 0.0


def rule(reply, alpha=ALPHA, min_effect=MIN_EFFECT):
    """reply: a measure-patch / measure-pair JSON reply with timings.process[*].candidate_ns/reference_ns. Returns None if not usable."""
    t = (reply or {}).get("timings")
    if not reply or not reply.get("ok", True) or not t or "process" not in t:
        return None
    pr, acs = [], []
    for p in t["process"]:
        c, r = p.get("candidate_ns"), p.get("reference_ns")
        if not c or not r or len(c) != len(r) or len(c) < 3:
            return None
        pr.append(median(c) / median(r))
        acs.append(acf1(c))
    if len(pr) != 10:
        return None
    out = rule_from_process_ratios(pr, alpha, min_effect)
    out["ac_median"] = median(acs)
    out["process_ratios"] = pr
    out["cand_ms"] = median([median(p["candidate_ns"]) for p in t["process"]]) / 1e6
    out["ref_ms"] = median([median(p["reference_ns"]) for p in t["process"]]) / 1e6
    return out


def write_csv(path, rows, fields=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if fields is None:
        fields = []
        for r in rows:
            for k in r:
                if k not in fields:
                    fields.append(k)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    return path


SOURCES = []   # (id, claim, file, field, computation) collected by the build scripts and written to sources.csv


def src(id_, claim, file, field, comp):
    SOURCES.append({"id": id_, "claim": claim, "source_file": str(file), "field": field, "computation": comp})


def fmt(x, nd=4):
    return "" if x is None or (isinstance(x, float) and math.isnan(x)) else (f"{x:.{nd}f}" if isinstance(x, float) else str(x))
