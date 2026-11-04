#!/usr/bin/env python3
"""Phase 0 audit: exact true ratios, sweep bias table, rejection-reason partition,
single-trial vs offline-paired confirmation, batch comparison with a stated
correction, lag-1 autocorrelation with an iid reference, provenance and
self-check evidence. Uses ONLY saved data and the frozen rule binary; it changes
no threshold and drops no trial.

Usage: phase0_audit.py --b1 runs/phase0-A --b2 runs/phase0b-B --out DIR
"""
import argparse, csv, hashlib, importlib.util, json, math, random, statistics, subprocess
from pathlib import Path

spec = importlib.util.spec_from_file_location("p0f", Path(__file__).with_name("phase0_final.py"))
p0f = importlib.util.module_from_spec(spec); spec.loader.exec_module(p0f)

MAIN, SWEEPS = p0f.MAIN, p0f.SWEEPS
ALPHA, MIN_EFFECT = 0.01, 0.02
THRESH = 1.0 - MIN_EFFECT          # the same expression the rule uses


def pct(x, d=3):
    return "n/a" if x is None else f"{100 * x:.{d}f}%"


def ci_str(b, d=3):
    lo, hi = b["clopper_pearson_95"]
    return f'{b["k"]}/{b["n"]} = {pct(b["rate"], 1)} [{pct(lo, d)}, {pct(hi, d)}]'


def lag1(x):
    m = sum(x) / len(x)
    den = sum((v - m) ** 2 for v in x)
    return sum((x[i] - m) * (x[i + 1] - m) for i in range(len(x) - 1)) / den if den > 0 else 0.0


def ac_series(path):
    """lag-1 AC of every process's candidate_ns series in one measurement file."""
    try:
        d = json.load(open(path))
        procs = d["timings"]["process"]
        return [lag1(p["candidate_ns"]) for p in procs]
    except Exception:
        return None


def ac_summary(per_meas):
    """per_meas: list of lists (one list of process ACs per measurement)."""
    per_meas = [m for m in per_meas if m]
    flat = [a for m in per_meas for a in m]
    meds = [statistics.median(m) for m in per_meas]
    return {"measurements": len(per_meas), "series": len(flat),
            "per_measurement_median": {"median": statistics.median(meds), "min": min(meds), "max": max(meds)},
            "per_series": {"median": statistics.median(flat), "p05": p0f.quantile(flat, .05),
                           "p95": p0f.quantile(flat, .95), "min": min(flat), "max": max(flat),
                           "share_positive": sum(a > 0 for a in flat) / len(flat),
                           "share_above_0.33": sum(a > 0.33 for a in flat) / len(flat)}}


def holm(pvals):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj, running = [None] * len(pvals), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvals) - rank) * pvals[i]))
        adj[i] = running
    return adj


def boot_median_diff_ci(x, y, rounds=10000, seed=7):
    rng = random.Random(seed)
    diffs = sorted(statistics.median([rng.choice(y) for _ in y]) - statistics.median([rng.choice(x) for _ in x])
                   for _ in range(rounds))
    return diffs[int(0.025 * rounds)], diffs[int(0.975 * rounds)]


def partition(r):
    d = not (r["geomean_ratio"] < 1.0)     # mean log-ratio not below zero  (direction)
    s = not (r["p_value"] < ALPHA)         # statistical gate failed
    m = not (r["ratio"] <= THRESH)         # magnitude gate failed
    return d, s, m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--b1", required=True); ap.add_argument("--b2", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rule-bin", default="build/CanMehSearch")
    args = ap.parse_args()
    b1, b2, out = Path(args.b1), Path(args.b2), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rule_bin = Path(args.rule_bin)

    meta = {p: json.load(open(Path("build/calibration") / p / "meta.json"))["calibration"] for p in MAIN + SWEEPS}
    true = {p: meta[p]["candidate_units"] / meta[p]["reference_units"] for p in meta}
    cal = {r["pair"]: r for r in json.load(open(b1 / "calibration.json"))["pairs"]}

    rows = p0f.evaluate("batch1", b1, MAIN + SWEEPS, rule_bin) + p0f.evaluate("batch2", b2, MAIN, rule_bin)
    # consistency with the summary written by the batch-2 job
    prev = {(r["batch"], r["pair"], r["trial"]): r
            for r in map(json.loads, open(b2 / "final" / "rule_rows.jsonl"))}
    mism = sum(1 for r in rows if (r["batch"], r["pair"], r["trial"]) not in prev or
               prev[(r["batch"], r["pair"], r["trial"])].get("faster") != r.get("faster") or
               prev[(r["batch"], r["pair"], r["trial"])].get("ratio") != r.get("ratio"))
    valid = [r for r in rows if r.get("valid")]
    inconsistent = sum(1 for r in valid if bool(r["faster"]) == any(partition(r)))
    R = {"rule_binary_sha256": p0f.sha256(rule_bin), "reevaluation_mismatches_vs_final_job": mism,
         "rule_flag_inconsistencies": inconsistent, "pairs": {}}

    def grp(pair, batches):
        return [r for r in rows if r["pair"] == pair and r["batch"] in batches]

    for pair in MAIN + SWEEPS:
        e = {"reference_units": meta[pair]["reference_units"], "candidate_units": meta[pair]["candidate_units"],
             "true_ratio": true[pair], "true_reduction_pct": 100 * (1 - true[pair]),
             "min_time": cal[pair]["min_time"]}
        batches = ["batch1", "batch2"] if pair in MAIN else ["batch1"]
        rs = grp(pair, batches)
        v = [r for r in rs if r["valid"]]
        ratios = [r["ratio"] for r in v]
        e["attempted"], e["valid"] = len(rs), len(v)
        e["single"] = p0f.rate_block(sum(1 for r in v if r["faster"]), len(v))
        p2, drop = [], 0
        for b in batches:
            p, d = p0f.two_stage(grp(pair, [b])); p2 += p; drop += d
        e["two_stage"] = p0f.rate_block(sum(1 for p in p2 if p["accepted"]), len(p2))
        e["two_stage"]["dropped_pairs"] = drop
        med, mean = statistics.median(ratios), statistics.mean(ratios)
        e["reported"] = {"median": med, "mean": mean, "sd": statistics.pstdev(ratios),
                         "abs_bias_median": med - true[pair], "rel_err_median_pct": 100 * (med - true[pair]) / true[pair],
                         "abs_bias_mean": mean - true[pair], "rel_err_mean_pct": 100 * (mean - true[pair]) / true[pair]}
        parts = {}
        for r in v:
            d, s, m = partition(r)
            key = "accepted" if not (d or s or m) else "+".join(n for n, f in (("direction", d), ("stat", s), ("magnitude", m)) if f)
            parts[key] = parts.get(key, 0) + 1
        e["rejection_partition"] = parts
        e["unstable_trials"] = sum(1 for r in v if r["unstable"])
        R["pairs"][pair] = e

    # batch comparison (main pairs): two families of six tests, Holm at family-wise 0.05
    fam_f, fam_p, cmp_ = [], [], {}
    for pair in MAIN:
        a, b = [r for r in grp(pair, ["batch1"]) if r["valid"]], [r for r in grp(pair, ["batch2"]) if r["valid"]]
        ka, kb = sum(r["faster"] for r in a), sum(r["faster"] for r in b)
        xa, xb = [r["ratio"] for r in a], [r["ratio"] for r in b]
        c = {"n": [len(a), len(b)], "accepted": [ka, kb],
             "fisher_p": p0f.fisher_two_sided(ka, len(a), kb, len(b)),
             "median_ratio": [statistics.median(xa), statistics.median(xb)],
             "median_shift_abs": statistics.median(xb) - statistics.median(xa),
             "median_shift_rel_pct": 100 * (statistics.median(xb) - statistics.median(xa)) / true[pair],
             "median_shift_boot95": boot_median_diff_ci(xa, xb),
             "perm_p": p0f.perm_median_diff(xa, xb),
             "ref_ms_median": [statistics.median([r["reference_ms"] for r in a]), statistics.median([r["reference_ms"] for r in b])]}
        cmp_[pair] = c; fam_f.append(c["fisher_p"]); fam_p.append(c["perm_p"])
    for pair, hf, hp in zip(MAIN, holm(fam_f), holm(fam_p)):
        cmp_[pair]["fisher_p_holm"], cmp_[pair]["perm_p_holm"] = hf, hp
    R["batch_comparison"] = cmp_

    # empirical thresholds by the course definition: observed rate >= 90%
    eff = sorted([p for p in MAIN if p.startswith("faster-")], key=lambda p: -true[p])  # weakest first
    R["empirical_threshold_observed_rate_ge_0.9"] = {
        k: next(({"pair": p, "true_ratio": true[p], "true_reduction_pct": 100 * (1 - true[p]), "rate": R["pairs"][p][k]["rate"]}
                 for p in eff if R["pairs"][p][k]["rate"] >= 0.9), None) for k in ("single", "two_stage")}

    # autocorrelation: calibration (all processes) vs iid reference vs SDK
    ac = {}
    for pair in MAIN + SWEEPS:
        per = [ac_series(r["path"]) for r in rows if r["pair"] == pair and r["valid"]]
        ac[pair] = ac_summary(per)
    rng = random.Random(11)
    sim = [lag1([rng.gauss(0, 1) for _ in range(9)]) for _ in range(100000)]
    ac["iid_normal_n9_reference"] = {"median": statistics.median(sim), "p05": p0f.quantile(sim, .05), "p95": p0f.quantile(sim, .95),
                                     "share_positive": sum(a > 0 for a in sim) / len(sim)}
    inert = [Path("runs/controls-1068897/eval-inert/evaluate-inert") / f"m{i}.json" for i in range(1, 6)] + [Path("runs/inert-check/measurement.json")]
    ac["sdk_inert_patch"] = ac_summary([ac_series(p) for p in inert if p.exists()])
    ac["sdk_inert_patch"]["files"] = [str(p) for p in inert if p.exists()]
    ac["sdk_main_matrix_candidates"] = ac_summary([ac_series(p) for p in sorted(Path("runs/main").glob("*/measurements/*.json"))])
    R["autocorrelation_lag1"] = ac

    # provenance and integrity
    def node(path):
        return dict(l.strip().split("=", 1) for l in open(path) if "=" in l and not l.startswith("sha"))
    n1, n2 = node(b1 / "node.txt"), node(b2 / "node.txt")
    files = [Path(r["path"]) for r in rows]
    hashes = {}
    for f in files:
        hashes.setdefault(p0f.sha256(f) if f.stat().st_size else "EMPTY:" + str(f), []).append(str(f))
    dup = {h: v for h, v in hashes.items() if len(v) > 1}
    idx = {}
    for r in rows:
        idx.setdefault((r["batch"], r["pair"]), []).append(r["trial"])
    t1 = max(Path(r["path"]).stat().st_mtime for r in rows if r["batch"] == "batch1" and r["valid"])
    t2 = min(Path(r["path"]).stat().st_mtime for r in rows if r["batch"] == "batch2")
    R["provenance"] = {
        "batch1": {"dir": str(b1), "job": n1.get("job"), "host": n1.get("host"), "cxx": n1.get("cxx"), "start": n1.get("start"),
                   "stopped_by": (b1 / "checkpoint_stop.txt").read_text().splitlines()[1] if (b1 / "checkpoint_stop.txt").exists() else None},
        "batch2": {"dir": str(b2), "job": n2.get("batch2_job"), "host": n2.get("batch2_host"), "same_node_as_batch1": n2.get("same_node"), "start": n2.get("start")},
        "measurement": "CanMehHarness measure-pair --repeat 10 --repetitions 9 --no-decision --min-time <per pair>",
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
        "git_dirty": bool(subprocess.run(["git", "status", "--porcelain", "--", "src", "scripts"], capture_output=True, text=True).stdout.strip()),
        "harness_sha256": p0f.sha256(Path("build/CanMehHarness")), "calibrate_sha256": p0f.sha256(Path("build/CanMehCalibrate")),
        "search_cpp_sha256": p0f.sha256(Path("src/Search.cpp")),
        "audit_script_sha256": p0f.sha256(Path(__file__)), "final_script_sha256": p0f.sha256(Path(p0f.__file__)),
        "duplicate_file_contents_across_all_trial_files": dup,
        "trial_indices_contiguous": {f"{b}/{p}": (sorted(set(i)) == list(range(min(i), max(i) + 1))) for (b, p), i in idx.items()},
        "batch2_files_all_written_after_last_valid_batch1_file": t2 > t1,
        "batch1_last_valid_mtime": t1, "batch2_first_mtime": t2,
        "invalid_files": [{k: r.get(k) for k in ("batch", "pair", "trial", "path", "bytes", "error")} for r in rows if not r["valid"]],
        "valid_per_main_pair": {p: R["pairs"][p]["valid"] for p in MAIN},
        "command": f"python3 -I scripts/phase0_audit.py --b1 {b1} --b2 {b2} --out {out}",
    }
    harness_mtime = __import__('datetime').datetime.fromtimestamp(Path('build/CanMehHarness').stat().st_mtime).isoformat(timespec='seconds')
    # twelve-pair device self-check
    cal_txt = (b1 / "calibrate.txt").read_text() if (b1 / "calibrate.txt").exists() else ""
    R["device_selfcheck"] = {
        "output": str(b1 / "calibrate.txt"), "json": str(b1 / "calibration.json"), "exit_line": [l for l in open(b1 / "node.txt") if "calibrate_exit" in l],
        "pairs_not_as_expected": json.load(open(b1 / "calibration.json"))["pairs_not_as_expected"],
        "stages": {p: {"expected": cal[p]["expected_stage"], "actual": cal[p]["stage"]} for p in ("broken-digest", "shared-install-name")},
        "required_rows": {p: {"measured": cal[p]["measured_ratio"], "true": cal[p]["true_ratio"],
                              "error_pct": 100 * (cal[p]["measured_ratio"] / cal[p]["true_ratio"] - 1), "limit_pct": 2 if p == "null" else 3,
                              "holds": cal[p]["holds"]} for p in ("null", "sweep-200", "sweep-400")}}
    (out / "phase0_audit.json").write_text(json.dumps(R, indent=2))

    # CSVs
    with open(out / "main_pairs.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pair", "ref_units", "cand_units", "true_ratio", "true_reduction_pct", "valid", "single_k", "single_rate", "single_cp_lo", "single_cp_hi",
                    "two_stage_k", "two_stage_n", "two_stage_cp_lo", "two_stage_cp_hi", "median_ratio", "abs_bias", "rel_err_pct", "min_time"])
        for p in MAIN + SWEEPS:
            e = R["pairs"][p]
            w.writerow([p, e["reference_units"], e["candidate_units"], e["true_ratio"], e["true_reduction_pct"], e["valid"], e["single"]["k"], e["single"]["rate"],
                        *e["single"]["clopper_pearson_95"], e["two_stage"]["k"], e["two_stage"]["n"], *e["two_stage"]["clopper_pearson_95"],
                        e["reported"]["median"], e["reported"]["abs_bias_median"], e["reported"]["rel_err_median_pct"], e["min_time"]])

    # Markdown
    P = R["pairs"]; L = []
    L += ["# Phase 0 审计（固定规则，现有数据）", "",
          f'规则二进制 sha256 `{R["rule_binary_sha256"][:16]}…`；重新评估与批次 2 作业汇总逐试验比对，不一致 {mism} 条；"判为更快"标记与三个门槛不一致 {inconsistent} 条。', "",
          "## 1. 主要校准对（单次判定）", "",
          "“判为更快”指**单次判定**：一次完整 `measure-pair`（10 进程×9 次重复）满足平均 log 比<0、符号翻转 p<0.01、报告比≤0.98。区间为 95% 双侧 Clopper–Pearson（单位 %，三位小数）。", "",
          "| 校准对 | 参考/候选工作量 | 精确真实比 | 真实降幅 | 有效试验 | 判为更快 | 95% CP | 中位报告比 | 绝对偏差 | 相对误差 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for p in MAIN:
        e = P[p]; s = e["single"]; r = e["reported"]
        L.append(f'| {p} | {e["reference_units"]}/{e["candidate_units"]} | {e["true_ratio"]:.5f} | {e["true_reduction_pct"]:.3f}% | {e["valid"]} | {s["k"]} | '
                 f'[{pct(s["clopper_pearson_95"][0])}, {pct(s["clopper_pearson_95"][1])}] | {r["median"]:.5f} | {r["abs_bias_median"]:+.5f} | {r["rel_err_median_pct"]:+.3f}% |')
    L += ["", "绝对偏差 = 中位报告比 − 精确真实比（无量纲）；相对误差 = 绝对偏差 ÷ 精确真实比。", "",
          "## 2. Sweep 对：比例估计随工作量缩放（仅批次 1 的 20 次独立试验）", "",
          "| 校准对 | 参考/候选工作量 | 精确真实比 | 有效试验 | 中位报告比 | 绝对偏差 | 相对误差 | 判为更快 |", "|---|---|---|---|---|---|---|---|"]
    for p in SWEEPS:
        e = P[p]; r = e["reported"]
        L.append(f'| {p} | {e["reference_units"]}/{e["candidate_units"]} | {e["true_ratio"]:.5f} | {e["valid"]} | {r["median"]:.5f} | {r["abs_bias_median"]:+.5f} | {r["rel_err_median_pct"]:+.3f}% | {e["single"]["k"]} |')
    L += ["", "sweep-110 与 slower-10-percent 工作量相同（22000），是同一配置的两个独立测量序列。", "",
          "## 3. 单次判定 vs 双次确认（离线配对评估）", "",
          "双次确认**不是**搜索中实际执行的确认流程，而是对已有单次试验的离线配对：在同一批次、同一校准对内，按试验序号连续配对 (t1,t2),(t3,t4)…，两个都通过单次规则才算接受（与实时流程“首次通过才复测、两次都通过才接受”的接受事件相同）。配对方式（相邻、不相交）早在 `scripts/analyze_phase0.py` 中写定，那时还没有任何 Phase 0 数据，`phase0_final.py` 原样沿用，未按结果挑选；实时流程在首次不稳定时也会复测，此处未模拟；两批都在节点 xcnc2 上，但同一对内相邻两次试验之间隔着其他校准对的测量（约 2 分钟），并非紧接复测；绝不跨批次配对；成员缺失的配对丢弃并计数（见 dropped）。", "",
          "| 校准对 | 单次判定 | 双次确认（离线配对） | dropped | 配对数 |", "|---|---|---|---|---|"]
    for p in MAIN:
        e = P[p]
        L.append(f'| {p} | {ci_str(e["single"])} | {ci_str(e["two_stage"])} | {e["two_stage"]["dropped_pairs"]} | {e["two_stage"]["n"]} |')
    th = R["empirical_threshold_observed_rate_ge_0.9"]
    L += ["", f'课程定义的经验检测阈值（已测点中观测检出率≥90% 的最弱效应）：单次 = {th["single"]["pair"]}（真实降幅 {th["single"]["true_reduction_pct"]:.3f}%，观测检出率 {100*th["single"]["rate"]:.0f}%）；双次 = {th["two_stage"]["pair"]}（观测检出率 {100*th["two_stage"]["rate"]:.0f}%）。分辨率只到已测的 1%、2%、5%、10% 四个点；上表同时列出各点的 CP 区间，课程定义只看观测检出率。', "",
          "## 4. 拒绝原因拆分（互斥分类）", "",
          "每个有效试验恰落入一类：direction=平均 log 比不小于 0；stat=符号翻转 p≥0.01；magnitude=中位比>0.98。多项同时未过则写成 a+b。每行相加等于有效试验数。", "",
          "| 校准对 | 有效 | 通过 | 仅 stat | 仅 magnitude | stat+magnitude | direction（含并发）|", "|---|---|---|---|---|---|---|"]
    for p in MAIN + SWEEPS:
        e = P[p]; pt = e["rejection_partition"]
        dire = sum(v for k, v in pt.items() if "direction" in k)
        L.append(f'| {p} | {e["valid"]} | {pt.get("accepted", 0)} | {pt.get("stat", 0)} | {pt.get("magnitude", 0)} | {pt.get("stat+magnitude", 0)} | {dire} |')
    L += ["", "## 5. 批次比较", "",
          "两个检验族（接受率的 Fisher 精确检验、中位比的置换检验，各 6 个对比），每族用 Holm 校正，族内显著性水平 0.05。p 值大只表示**未检出**差异，不证明两批等价；中位比平移同时给出绝对幅度和 bootstrap 95% 区间。", "",
          "| 校准对 | 接受数 批1/批2 | Fisher p（Holm） | 中位比 批1→批2 | 平移（绝对 / 相对） | bootstrap 95% | 置换 p（Holm） | 参考 ms 批1/批2 |", "|---|---|---|---|---|---|---|---|"]
    for p in MAIN:
        c = cmp_[p]
        L.append(f'| {p} | {c["accepted"][0]}/{c["accepted"][1]} | {c["fisher_p"]:.3f} ({c["fisher_p_holm"]:.3f}) | {c["median_ratio"][0]:.5f}→{c["median_ratio"][1]:.5f} | '
                 f'{c["median_shift_abs"]:+.5f} / {c["median_shift_rel_pct"]:+.3f}% | [{c["median_shift_boot95"][0]:+.5f}, {c["median_shift_boot95"][1]:+.5f}] | '
                 f'{c["perm_p"]:.3f} ({c["perm_p_holm"]:.3f}) | {c["ref_ms_median"][0]:.2f}/{c["ref_ms_median"][1]:.2f} |')
    L += ["", "## 6. lag-1 自相关（每条序列仅 9 个值，单值标准误约 0.33）", "",
          "| 对象 | 测量数/序列数 | 单次测量内进程中位数的 中位[最小,最大] | 单序列 中位 [p05,p95] | 单序列最小/最大 | 序列中>0 的比例 |", "|---|---|---|---|---|---|"]
    for k in MAIN + SWEEPS + ["sdk_inert_patch", "sdk_main_matrix_candidates"]:
        a = ac[k]; pm, ps = a["per_measurement_median"], a["per_series"]
        L.append(f'| {k} | {a["measurements"]}/{a["series"]} | {pm["median"]:+.2f} [{pm["min"]:+.2f}, {pm["max"]:+.2f}] | {ps["median"]:+.2f} [{ps["p05"]:+.2f}, {ps["p95"]:+.2f}] | {ps["min"]:+.2f}/{ps["max"]:+.2f} | {100 * ps["share_positive"]:.1f}% |')
    i = ac["iid_normal_n9_reference"]
    L += ["", f'独立同分布参照（正态，n=9，10 万次模拟，同一估计量）：中位 {i["median"]:+.2f}，[p05,p95]=[{i["p05"]:+.2f},{i["p95"]:+.2f}]，>0 的比例 {100 * i["share_positive"]:.1f}%。n=9 时该估计量对独立序列本身就偏负，因此校准中位数为负并不说明有或没有相关，只是未从中位数观察到正相关趋势。', "",
          f"SDK 侧：`sdk_inert_patch` 是 SDK 上 inert 补丁的 6 次测量（`--min-time` 0.25s，与校准对的约 0.061s 不同；5 次在 controls 作业 1068897 的 xcnd24，1 次在 `runs/inert-check`，节点 xcnc1）。这 6 次里 {100*ac["sdk_inert_patch"]["per_series"]["share_positive"]:.0f}% 的序列自相关为正，而独立参照约 {100*i["share_positive"]:.0f}%、校准对约 35–39%：SDK 上有正自相关的迹象，但样本只有 6 次测量、min-time 与节点都与校准不同，不能定量，也不能据此说校准的重复计时独立。`sdk_main_matrix_candidates` 是主矩阵中真实候选补丁的测量，仅作分布参考。规则不假设进程内重复独立：它只取每进程 9 次的中位数，并在 10 个进程的 log 比上做符号翻转；该检验假设各进程比相互独立、符号对称。", "",
          "## 7. 十二对装置自检（与规则评估分开）", ""]
    sc = R["device_selfcheck"]
    L += [f'输出：`{sc["output"]}`、`{sc["json"]}`；退出：{sc["exit_line"]}；未达预期的对：{sc["pairs_not_as_expected"]}。', "",
          f'故障库拒绝阶段：{json.dumps(sc["stages"], ensure_ascii=False)}。', "", "README 要求的三个比例行：", ""]
    for p, v in sc["required_rows"].items():
        L.append(f'- {p}: 测得 {v["measured"]:.5f}，真实 {v["true"]:.5f}，误差 {v["error_pct"]:+.3f}%（限 {v["limit_pct"]}%），{"满足" if v["holds"] else "未满足"}')
    L += ["", "这是校准装置自检（一次测量），不是对学生规则的验证。", "",
          "## 8. 数据来源与完整性", ""]
    pv = R["provenance"]
    L += [f'- 批次 1：job {pv["batch1"]["job"]}，节点 {pv["batch1"]["host"]}，起 {pv["batch1"]["start"]}；停止：{pv["batch1"]["stopped_by"]}',
          f'- 批次 2：job {pv["batch2"]["job"]}，节点 {pv["batch2"]["host"]}（与批次 1 同节点：{pv["batch2"]["same_node_as_batch1"]}），起 {pv["batch2"]["start"]}',
          f'- 测量命令：{pv["measurement"]}；repeat=10，repetitions=9；min_time 与工作量：' + '；'.join(f'{p} {P[p]["min_time"]} ({P[p]["reference_units"]}/{P[p]["candidate_units"]})' for p in MAIN + SWEEPS),
          f'- 规则二进制由 `--rule-eval` 对两批原始文件离线统一评估（哈希见上）。测量用的 harness 二进制修改时间 {harness_mtime}，早于批次 1 开始时间，批次 2 作业记录的哈希与现在一致（`runs/phase0b-*/node.txt`）；批次 1 作业本身没有记录哈希，这里只能用修改时间间接佐证。',
          f'- 代码：commit {pv["git_commit"]}（工作树有未提交改动：{pv["git_dirty"]}）；Search.cpp {pv["search_cpp_sha256"][:16]}…；harness {pv["harness_sha256"][:16]}…；规则二进制 {R["rule_binary_sha256"][:16]}…',
          f'- 各主要对有效试验：{pv["valid_per_main_pair"]}；试验序号连续：{all(pv["trial_indices_contiguous"].values())}；跨所有试验文件内容重复数：{len(pv["duplicate_file_contents_across_all_trial_files"])}；批次 2 全部晚于批次 1 有效文件：{pv["batch2_files_all_written_after_last_valid_batch1_file"]}',
          f'- 无效/中断文件（保留未删）：{json.dumps(pv["invalid_files"], ensure_ascii=False)}',
          f'- 汇总命令：`{pv["command"]}`', ""]
    n_null = P["null"]["single"]
    L += ["## 9. 适用范围与限制", "",
          "- 假设：符号翻转检验假设 10 个进程级 log 比相互独立，且在“无差异”下关于 0 对称；规则只用每进程 9 次重复的中位数，不使用进程内方差，也不要求进程内重复独立，但若进程之间有共同漂移，p 值会偏乐观。槽位交替能抵消慢漂移，不能抵消所有相关。",
          "- 校准工作循环与真实 SDK 不同：工作循环的计时近似平稳、不在计时区内分配、对全部工作量做均匀缩放；SDK 解码在计时区内分配并依赖数据分支，计时分布可能更重尾、相邻重复可能相关（上文 SDK inert 序列已显示正自相关迹象，样本有限）。真实补丁通常只加速解码的一部分，校准的检出率不能无条件推广到所有 SDK 补丁。",
          "- null 对 0/100 次单次接受：在该校准条件和二项模型假设下，误报率的 95% 双侧 CP 区间为 [0, " + pct(n_null["clopper_pearson_95"][1], 2) + "]。这些数据不足以独立证明误报率低于 1%。α=1% 是单次检验预设的显著性门槛，不是本批实验验证过的实际误报率，更不是整个搜索流程（多代、多候选、确认）的总体误报率。",
          "- 快 2% 对：真实比 " + f'{true["faster-2-percent"]:.5f}' + "（降幅 " + f'{100*(1-true["faster-2-percent"]):.3f}' + "%）略高于接受门槛 0.98，即真实降幅略小于 2%；测得中位比 " + f'{P["faster-2-percent"]["reported"]["median"]:.5f}' + "。接受 42/100 反映真实效应贴近门槛时，测量波动与估计偏差决定每次是否越过门槛；不能排除噪声的作用，也不能把 42/100 推广为规则对任何“真实 2% 加速”的检出能力。",
          "- 调参说明：α=0.01、2% 下限、10 进程、符号翻转统计量都在看到任何 Phase 0 数据前固定，没有用校准对调参，故这批试验是评估数据；规则二进制在批次 1 运行期间重新编译过（仅影响搜索采样器，规则代码未改），两批都由同一二进制离线评估。",
          "- 缺失项：未对 SDK 做与校准对同 min-time、同节点的 null 重复（只有 6 次 inert 测量）；双次确认只是离线配对评估；sweep 对每个只有 20 次试验。", ""]
    (out / "phase0_audit.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
