#!/usr/bin/env python3
"""Final Phase 0 summary over batch 1 (runs/phase0-<job>) and batch 2 (runs/phase0b-<job>).

Every trial file is judged offline by the frozen rule (`CanMehSearch --rule-eval`,
which reads only `timings`). One trial = one complete `measure-pair` call (10
processes x 9 repetitions); the ten processes inside it are NOT ten trials.
Numbers are pooled from counts and raw ratios, never by averaging batch
percentages. Batches are also reported separately and compared.

Two-stage (confirmation) protocol, offline: inside one batch and one pair, trials
are paired by consecutive index (f0,f0+1), (f0+2,f0+3), ... Both members come from
the same node and the same job, are measured back to back, and never overlap with
another pair. A pair is "accepted" iff both trials pass the single-trial rule, which
has the same acceptance probability as the live protocol (re-measure only if the
first passes; accept iff both pass). The kept ratio is the less flattering of the
two. Pairs with a missing/invalid member are dropped and counted. Trials of
different batches are never paired together.

Usage: phase0_final.py --b1 runs/phase0-A [--b2 runs/phase0b-B] --out DIR
"""
import argparse, csv, hashlib, json, math, random, statistics, subprocess, sys
from pathlib import Path

MAIN = ["null", "faster-1-percent", "faster-2-percent", "faster-5-percent",
        "faster-10-percent", "slower-10-percent"]
SWEEPS = ["sweep-105", "sweep-110", "sweep-200", "sweep-400"]


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p**i * (1 - p)**(n - i) for i in range(0, k + 1))


def clopper_pearson(k, n, alpha=0.05):
    if n == 0:
        return (0.0, 1.0)
    lo = 0.0
    hi = 1.0
    if k > 0:
        a, b = 0.0, 1.0
        for _ in range(100):
            m = (a + b) / 2
            if 1 - binom_cdf(k - 1, n, m) < alpha / 2: a = m
            else: b = m
        lo = (a + b) / 2
    if k < n:
        a, b = 0.0, 1.0
        for _ in range(100):
            m = (a + b) / 2
            if binom_cdf(k, n, m) > alpha / 2: a = m
            else: b = m
        hi = (a + b) / 2
    return (lo, hi)


def wilson(k, n, z=1.959964):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def fisher_two_sided(a, n1, b, n2):
    """Two-sided Fisher exact p for a/n1 vs b/n2 successes."""
    total, k = a + b, n1
    def pmf(x):
        return math.comb(n1, x) * math.comb(n2, total - x) / math.comb(n1 + n2, total)
    lo, hi = max(0, total - n2), min(total, n1)
    obs = pmf(a)
    return min(1.0, sum(pmf(x) for x in range(lo, hi + 1) if pmf(x) <= obs * (1 + 1e-9)))


def perm_median_diff(x, y, rounds=20000, seed=20261103):
    """Permutation p-value for |median(x) - median(y)|."""
    if not x or not y:
        return None
    rng = random.Random(seed)
    obs = abs(statistics.median(x) - statistics.median(y))
    pool = list(x) + list(y)
    n1 = len(x)
    hits = 0
    for _ in range(rounds):
        rng.shuffle(pool)
        if abs(statistics.median(pool[:n1]) - statistics.median(pool[n1:])) >= obs - 1e-15:
            hits += 1
    return (hits + 1) / (rounds + 1)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def evaluate(batch, root, pairs, rule_bin):
    rows = []
    for pair in pairs:
        files = sorted((root / "trials" / pair).glob("t*.json"))
        if not files:
            continue
        out = subprocess.run([str(rule_bin), "--rule-eval", *map(str, files)],
                             capture_output=True, text=True).stdout
        for line in out.splitlines():
            r = json.loads(line)
            f = Path(r["file"])
            r.update(batch=batch, pair=pair, trial=int(f.stem[1:]), path=str(f),
                     bytes=f.stat().st_size)
            rows.append(r)
    return rows


def rate_block(k, n):
    cp, wl = clopper_pearson(k, n), wilson(k, n)
    return {"k": k, "n": n, "rate": (k / n) if n else None,
            "clopper_pearson_95": cp, "wilson_95": wl}


def two_stage(rows):
    """Pair consecutive trial indexes of one (batch, pair); returns (list of outcomes, dropped)."""
    by = {r["trial"]: r for r in rows}
    if not by:
        return [], 0
    first = min(by)
    pairs, dropped, k = [], 0, first
    last = max(by)
    while k + 1 <= last:
        a, b = by.get(k), by.get(k + 1)
        if a and b and a["valid"] and b["valid"]:
            ok = bool(a["faster"]) and bool(b["faster"])
            pairs.append({"accepted": ok, "kept_ratio": max(a["ratio"], b["ratio"]),
                          "trials": [k, k + 1]})
        else:
            dropped += 1
        k += 2
    return pairs, dropped


def quantile(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    pos = q * (len(xs) - 1)
    lo = int(math.floor(pos)); hi = int(math.ceil(pos))
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def summarize(rows, true_ratio, include_two_stage_from):
    valid = [r for r in rows if r.get("valid")]
    ratios = [r["ratio"] for r in valid]
    k = sum(1 for r in valid if r["faster"])
    s = {"attempted": len(rows), "valid": len(valid), "invalid": len(rows) - len(valid)}
    s["single"] = rate_block(k, len(valid))
    pairs, dropped = [], 0
    for grp in include_two_stage_from:
        p, d = two_stage(grp)
        pairs += p; dropped += d
    k2 = sum(1 for p in pairs if p["accepted"])
    s["two_stage"] = rate_block(k2, len(pairs))
    s["two_stage"]["dropped_pairs"] = dropped
    s["two_stage"]["median_kept_ratio_of_accepted"] = (
        statistics.median([p["kept_ratio"] for p in pairs if p["accepted"]]) if k2 else None)
    if ratios:
        med, mean = statistics.median(ratios), statistics.mean(ratios)
        s["true_ratio"] = true_ratio
        s["reported_ratio"] = {"median": med, "mean": mean, "sd": statistics.pstdev(ratios),
                               "min": min(ratios), "max": max(ratios),
                               "p05": quantile(ratios, .05), "p95": quantile(ratios, .95)}
        s["bias"] = {"median_abs": med - true_ratio, "mean_abs": mean - true_ratio,
                     "median_rel_pct": 100 * (med - true_ratio) / true_ratio,
                     "mean_rel_pct": 100 * (mean - true_ratio) / true_ratio}
        s["median_p_value"] = statistics.median([r["p_value"] for r in valid])
        s["median_ratio_spread"] = statistics.median([r["ratio_spread"] for r in valid])
        s["unstable_trials"] = sum(1 for r in valid if r["unstable"])
        s["reference_ms_median"] = statistics.median([r["reference_ms"] for r in valid])
        acs = [r["autocorr_lag1_median"] for r in valid]
        s["autocorr_lag1"] = {"median_of_trial_medians": statistics.median(acs),
                              "p05": quantile(acs, .05), "p95": quantile(acs, .95),
                              "min_over_processes": min(r["autocorr_lag1_min"] for r in valid),
                              "max_over_processes": max(r["autocorr_lag1_max"] for r in valid),
                              "share_trials_median_positive": sum(a > 0 for a in acs) / len(acs)}
        reasons = {}
        for r in valid:
            reasons[r["reason"] or "accepted as faster"] = reasons.get(r["reason"] or "accepted as faster", 0) + 1
        s["rule_outcomes"] = reasons
    return s


def fmt_ci(b):
    return f'{b["k"]}/{b["n"]} = {100*b["rate"]:.1f}% [{100*b["clopper_pearson_95"][0]:.1f}, {100*b["clopper_pearson_95"][1]:.1f}]' if b["n"] else "n/a"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--b1", required=True)
    ap.add_argument("--b2", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rule-bin", default="build/CanMehSearch")
    args = ap.parse_args()
    b1 = Path(args.b1)
    b2 = Path(args.b2) if args.b2 and Path(args.b2).exists() else None
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    rule_bin = Path(args.rule_bin)

    true = {}
    for pair in MAIN + SWEEPS:
        meta = json.load(open(Path("build/calibration") / pair / "meta.json"))["calibration"]
        true[pair] = meta["candidate_units"] / meta["reference_units"]

    rows = evaluate("batch1", b1, MAIN + SWEEPS, rule_bin)
    if b2:
        rows += evaluate("batch2", b2, MAIN, rule_bin)
    with open(out / "rule_rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    def sel(batches, pair):
        return [r for r in rows if r["pair"] == pair and r["batch"] in batches]

    result = {"rule_binary_sha256": sha256(rule_bin),
              "rule": {"alpha": 0.01, "min_effect": 0.02, "processes": 10, "unstable_spread": 0.25},
              "batches": {"batch1": str(b1), "batch2": str(b2) if b2 else None},
              "pairs": {}}
    for pair in MAIN + SWEEPS:
        entry = {"true_ratio": true[pair]}
        groups = {}
        for name, batches in (("batch1", ["batch1"]), ("batch2", ["batch2"]), ("combined", ["batch1", "batch2"])):
            rs = sel(batches, pair)
            if not rs:
                continue
            by_batch = [sel([b], pair) for b in batches if sel([b], pair)]
            groups[name] = summarize(rs, true[pair], by_batch)
        entry.update(groups)
        if "batch1" in groups and "batch2" in groups:
            r1 = [r["ratio"] for r in sel(["batch1"], pair) if r["valid"]]
            r2 = [r["ratio"] for r in sel(["batch2"], pair) if r["valid"]]
            s1, s2 = groups["batch1"]["single"], groups["batch2"]["single"]
            entry["batch_comparison"] = {
                "acceptance_fisher_p": fisher_two_sided(s1["k"], s1["n"], s2["k"], s2["n"]),
                "median_ratio_diff": statistics.median(r2) - statistics.median(r1),
                "median_ratio_permutation_p": perm_median_diff(r1, r2),
                "reference_ms_median": [groups["batch1"]["reference_ms_median"], groups["batch2"]["reference_ms_median"]],
            }
        result["pairs"][pair] = entry

    # Empirical detection threshold on the tested effect sizes (single-trial rule and two-stage).
    effects = sorted([p for p in MAIN if p.startswith("faster-")], key=lambda p: -true[p])  # weakest first
    thr = {}
    for label, key in (("single", "single"), ("two_stage", "two_stage")):
        found = None
        for i, p in enumerate(effects):
            rates = [result["pairs"][q]["combined" if "combined" in result["pairs"][q] else "batch1"][key]["rate"] for q in effects[i:]]
            if all(r is not None and r >= 0.9 for r in rates):
                c = result["pairs"][p]["combined" if "combined" in result["pairs"][p] else "batch1"][key]
                found = {"pair": p, "true_ratio": true[p], "rate": c["rate"], "cp_lower": c["clopper_pearson_95"][0]}
                break
        thr[label] = found
    result["empirical_detection_threshold_90pct"] = thr
    result["threshold_definition"] = ("weakest tested effect whose acceptance rate, and that of every stronger tested effect, "
                                      "is >= 90%; only the tested points 1%, 2%, 5%, 10% faster can be named")

    # Failures / interrupted measurements and raw index.
    failures = [{k: r.get(k) for k in ("batch", "pair", "trial", "path", "bytes", "error", "reason")}
                for r in rows if not r.get("valid")]
    (out / "failures.json").write_text(json.dumps(failures, indent=2))
    with open(out / "raw_index.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["batch", "pair", "trial", "path", "bytes", "sha256", "valid", "faster", "ratio", "p_value", "reason_or_error"])
        for r in sorted(rows, key=lambda r: (r["batch"], r["pair"], r["trial"])):
            w.writerow([r["batch"], r["pair"], r["trial"], r["path"], r["bytes"], sha256(r["path"]),
                        r.get("valid"), r.get("faster"), r.get("ratio"), r.get("p_value"), r.get("reason") or r.get("error")])
    (out / "phase0_final.json").write_text(json.dumps(result, indent=2))

    # Markdown report.
    L = ["# Phase 0 final summary", "",
         f"rule binary sha256 `{result['rule_binary_sha256'][:16]}…`; alpha=0.01, min effect 2%, 10 processes x 9 repetitions per trial.",
         f"batch 1: `{b1}`; batch 2: `{b2}`.", "",
         "| pair | true ratio | n | accepted (single) | rate, 95% CP | median reported | abs bias | rel err | two-stage accepted | lag-1 AC median |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for pair in MAIN + SWEEPS:
        e = result["pairs"][pair]; g = e.get("combined") or e["batch1"]
        if "reported_ratio" not in g:
            continue
        L.append(f'| {pair} | {e["true_ratio"]:.4f} | {g["valid"]} | {g["single"]["k"]} | {fmt_ci(g["single"]).split("= ")[1]} | '
                 f'{g["reported_ratio"]["median"]:.4f} | {g["bias"]["median_abs"]:+.4f} | {g["bias"]["median_rel_pct"]:+.2f}% | '
                 f'{g["two_stage"]["k"]}/{g["two_stage"]["n"]} | {g["autocorr_lag1"]["median_of_trial_medians"]:+.2f} |')
    L += ["", "## Per batch (single-trial acceptance)", "", "| pair | batch 1 | batch 2 | Fisher p | median-ratio shift | permutation p |", "|---|---|---|---|---|---|"]
    for pair in MAIN:
        e = result["pairs"][pair]
        if "batch_comparison" in e:
            c = e["batch_comparison"]
            L.append(f'| {pair} | {fmt_ci(e["batch1"]["single"])} | {fmt_ci(e["batch2"]["single"])} | {c["acceptance_fisher_p"]:.3f} | '
                     f'{c["median_ratio_diff"]:+.4f} | {c["median_ratio_permutation_p"]:.3f} |')
    L += ["", "Empirical detection threshold (90%): " + json.dumps(thr), "",
          f"Failed / interrupted measurements: {len(failures)} (see failures.json)."]
    (out / "phase0_final.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
