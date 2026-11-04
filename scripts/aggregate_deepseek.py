#!/usr/bin/env python3
"""Cross-seed summary of the DeepSeek greedy-vs-best-of-N experiment.

Reads every runs/deepseek/{greedy,bestofn}-s<seed>-<job>/ directory, whatever its state
(finished, cut by the deadline, failed, still running) and writes
  runs/deepseek/summary_runs.csv   one row per run
  runs/deepseek/summary.md         per-seed pairs plus per-arm medians and full ranges
Nothing is filtered: unfinished, short, or unfavourable runs stay in the table.
Safe to run concurrently (flock + atomic rename), and idempotent.
Token efficiency = log(speedup of the fixed best patch, median of its 3 independent
re-measurements) per million total tokens; also per million reasoning tokens.
"""
import csv, fcntl, json, math, os, re, statistics, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "runs" / "deepseek"


def load(path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return default


def rows_of(path):
    out = []
    try:
        for line in Path(path).read_text().splitlines():
            if line.strip():
                out.append(json.loads(line))
    except Exception:
        pass
    return out


def node_value(node, key):
    m = re.search(r"^%s=(.*)$" % re.escape(key), node, re.M)
    return m.group(1).strip() if m else ""


def run_row(d):
    m = re.match(r"(greedy|bestofn)-s(\d+)-(\d+)$", d.name)
    mode, seed, job = m.group(1), int(m.group(2)), m.group(3)
    node = (d / "node.txt").read_text() if (d / "node.txt").exists() else ""
    summ = load(d / "summary.json", {}) or {}
    rows = rows_of(d / "results.jsonl")
    ev = load(d / "evaluate-best" / "summary.json", {}) or {}
    stages = Counter()
    attempts = 0
    for r in rows:
        stages["valid" if r.get("ok") else (r.get("stage") or "other")] += 1
        attempts += int((r.get("llm") or {}).get("http_attempts", 0) or 0)
    resumes = sorted(d.parent.glob(d.name + "-resume-*"))
    resume_note = ""
    if resumes:
        # Continuation of a run that hit its deadline short of the 40-attempt budget: add the continuation's
        # attempts, tokens and outcomes; the fixed best patch is the continuation's final one (re-measured 3x there).
        rd = resumes[-1]
        rs = load(rd / "summary.json", {}) or {}
        rrows = rows_of(rd / "results.jsonl")
        for r in rrows:
            stages["valid" if r.get("ok") else (r.get("stage") or "other")] += 1
            attempts += int((r.get("llm") or {}).get("http_attempts", 0) or 0)
        rows = rows + rrows
        for k in ("prompt_tokens", "completion_tokens", "reasoning_tokens", "total_tokens", "truncated_replies", "llm_seconds", "elapsed_s"):
            summ[k] = (summ.get(k, 0) or 0) + (rs.get(k, 0) or 0)
        rev = load(rd / "evaluate-best" / "summary.json", {}) or {}
        if rev:
            ev = rev
        resume_note = rd.name
    ratios = [m_["analysis"]["ratio"] for m_ in ev.get("measurements", []) if m_.get("analysis", {}).get("valid")]
    done = "end=" in node
    state = "finished" if done else ("running" if rows or node else "pending")
    if done and not ev:
        state = "finished-no-final-eval"
    speed_fixed = ev.get("median_speedup")
    tot, rea = summ.get("total_tokens", 0) or 0, summ.get("reasoning_tokens", 0) or 0
    eff_tot = math.log(speed_fixed) / (tot / 1e6) if speed_fixed and tot else None
    eff_rea = math.log(speed_fixed) / (rea / 1e6) if speed_fixed and rea else None
    null_ok = ""
    init = load(d / "init.json", {}) or {}
    if "null_ok" in init:
        null_ok = init["null_ok"]
    return {
        "mode": mode, "seed": seed, "job": job, "resumed_by": resume_note, "state": state, "host": node_value(node, "host"),
        "null_ok": null_ok, "http_attempts": attempts, "generations_rows": len(rows),
        "rows_without_call": sum(1 for r in rows if not r.get("llm")),
        "ended_because": summ.get("ended_because", ""),
        "prompt_tokens": summ.get("prompt_tokens", ""), "completion_tokens": summ.get("completion_tokens", ""),
        "reasoning_tokens": rea if summ else "", "total_tokens": tot if summ else "",
        "truncated": summ.get("truncated_replies", ""), "llm_seconds": round(summ.get("llm_seconds", 0), 1) if summ else "",
        "elapsed_s": round(summ.get("elapsed_s", 0), 1) if summ else "",
        "valid_candidates": stages["valid"], "failures": json.dumps({k: v for k, v in stages.items() if k != "valid"}, sort_keys=True),
        "rank_updates": len((load(d / "summary.json", {}) or {}).get("rank_updates", [])) if summ else "",
        "best_ranked_speedup": round(summ["best_ranked_speedup"], 4) if "best_ranked_speedup" in summ else "",
        "fixed_patch_ratios": ";".join("%.4f" % x for x in ratios),
        "fixed_patch_pass": ev.get("measurements_passing_rule", ""), "fixed_patch_valid": ev.get("valid_measurements", ""),
        "fixed_patch_median_speedup": round(speed_fixed, 4) if speed_fixed else "",
        "logspeed_per_Mtok_total": round(eff_tot, 4) if eff_tot is not None else "",
        "logspeed_per_Mtok_reasoning": round(eff_rea, 4) if eff_rea is not None else "",
    }


def fmt_range(vals):
    vals = [v for v in vals if isinstance(v, (int, float))]
    if not vals:
        return "n/a"
    return "median %.4f, range [%.4f, %.4f], n=%d" % (statistics.median(vals), min(vals), max(vals), len(vals))


def main():
    dirs = sorted(p for p in ROOT.glob("*-s*-*") if re.match(r"(greedy|bestofn)-s\d+-\d+$", p.name))
    table = [run_row(d) for d in dirs]
    table.sort(key=lambda r: (r["seed"], r["mode"]))
    lock = open(ROOT / ".aggregate.lock", "w")
    fcntl.flock(lock, fcntl.LOCK_EX)
    tmp = ROOT / "summary_runs.csv.tmp"
    if table:
        with open(tmp, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(table[0].keys()))
            w.writeheader()
            w.writerows(table)
        os.replace(tmp, ROOT / "summary_runs.csv")

    L = ["# DeepSeek greedy vs best-of-N: all runs (nothing filtered)", "",
         "Model deepseek-v4.1-flash (returned id deepseek-v4.1-flash-1017), max_tokens 32768, budget 40 HTTP attempts per run,",
         "no hidden retries. Seed 1 used a 9600 s search deadline; seeds 2-5 use 9300 s. Speedups are old/new (>1 is faster).",
         "'fixed' = the arm's fixed best patch, median of its 3 independent re-measurements (alpha 0.01, >=2% rule).", ""]
    L.append("| seed | arm | state | attempts | ended | fixed speedup (3 re-meas.) | rule pass | search R-speedup | updates | valid | trunc | reasoning tok | total tok | elapsed s | logspeed/Mtok |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in table:
        L.append("| %s | %s | %s | %s | %s | %s | %s/%s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["seed"], r["mode"], r["state"], r["http_attempts"], r["ended_because"] or "-",
            r["fixed_patch_median_speedup"] or "-", r["fixed_patch_pass"] if r["fixed_patch_pass"] != "" else "-",
            r["fixed_patch_valid"] if r["fixed_patch_valid"] != "" else "-", r["best_ranked_speedup"] or "-",
            r["rank_updates"], r["valid_candidates"], r["truncated"], r["reasoning_tokens"], r["total_tokens"],
            r["elapsed_s"], r["logspeed_per_Mtok_total"] or "-"))
    L += ["", "## Per arm (finished runs with a final evaluation only; every seed above is listed regardless)", ""]
    for mode in ("greedy", "bestofn"):
        rs = [r for r in table if r["mode"] == mode and r["fixed_patch_median_speedup"] != ""]
        L.append("**%s** (%d runs): fixed speedup %s" % (mode, len(rs), fmt_range([r["fixed_patch_median_speedup"] for r in rs])))
        for key, label in (("http_attempts", "attempts"), ("total_tokens", "total tokens"), ("reasoning_tokens", "reasoning tokens"),
                           ("elapsed_s", "elapsed s"), ("truncated", "truncated"), ("logspeed_per_Mtok_total", "log-speedup per Mtok")):
            vals = [r[key] for r in rs if r[key] != ""]
            L.append("  - %s: %s" % (label, fmt_range(vals)))
    pairs = {}
    for r in table:
        if r["fixed_patch_median_speedup"] != "":
            pairs.setdefault(r["seed"], {})[r["mode"]] = r["fixed_patch_median_speedup"]
    both = {s: v for s, v in pairs.items() if len(v) == 2}
    L += ["", "## Paired by seed (seeds with both arms evaluated)", ""]
    if both:
        L.append("| seed | greedy | bestofn | greedy/bestofn |")
        L.append("|---|---|---|---|")
        for s, v in sorted(both.items()):
            L.append("| %d | %.4f | %.4f | %.4f |" % (s, v["greedy"], v["bestofn"], v["greedy"] / v["bestofn"]))
        wins = sum(1 for v in both.values() if v["greedy"] > v["bestofn"])
        L.append("")
        L.append("greedy higher in %d of %d paired seeds. This is descriptive: with at most five seeds no significance is claimed, "
                 "and model and strategy both differ from the Qwen experiment (whose data is kept separately)." % (wins, len(both)))
    else:
        L.append("(none yet)")
    (ROOT / "summary.md.tmp").write_text("\n".join(L) + "\n")
    os.replace(ROOT / "summary.md.tmp", ROOT / "summary.md")
    fcntl.flock(lock, fcntl.LOCK_UN)
    print("\n".join(L))


if __name__ == "__main__":
    main()
