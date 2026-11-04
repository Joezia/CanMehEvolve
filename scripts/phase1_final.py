#!/usr/bin/env python3
"""Phase 1 final export.  Reads only raw run files; every number carries the file it came from.

Outputs (runs/phase1-final/):
  phase1_runs.csv / phase1_final.json   one row per run (Qwen matrix and DeepSeek seeds 1-5)
  common34.csv                          post-hoc common-budget analysis (first 34 HTTP requests)
  controls.csv                          C1 / C2 / inert control results
  STATS.md                              medians, ranges, group tests
Course metric (README): (best_confirmed_speedup - 1) / total_tokens, where best_confirmed_speedup is the median speedup of the
three independent re-measurements of the run's FIXED final patch if all three pass the frozen rule (alpha 0.01, >=2%), else 1.0.
Nothing in a run's own files (credits.csv, summary.json, results.jsonl) is edited or filtered.
"""
import csv, glob, hashlib, itertools, json, math, os, re, statistics as st, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "runs" / "phase1-final"
sys.path.insert(0, str(ROOT / "scripts"))
import aggregate as qwen_agg  # frozen Qwen-era row builder


def rel(p):
    return os.path.relpath(p, ROOT)


def load(p, default=None):
    try:
        return json.load(open(p))
    except Exception:
        return default


def jsonl(p):
    try:
        return [json.loads(l) for l in open(p) if l.strip()]
    except Exception:
        return []


def sha(p):
    try:
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    except Exception:
        return ""


def node_kv(p):
    d = {}
    try:
        for l in open(p):
            if "=" in l:
                k, v = l.strip().split("=", 1)
                d[k] = v
    except Exception:
        pass
    return d


def claim(ev):
    """best_confirmed_speedup from an evaluate-patch summary: median speedup if all measurements pass, else 1.0."""
    if ev and ev.get("valid_measurements") and ev.get("all_pass"):
        return ev["median_speedup"]
    return 1.0


# ---- exact two-group tests on 5 vs 5 --------------------------------------------------
def perm_median_p(x, y):
    allv, n = list(x) + list(y), len(x)
    obs = abs(st.median(x) - st.median(y))
    hit = tot = 0
    for idx in itertools.combinations(range(len(allv)), n):
        a = [allv[i] for i in idx]
        b = [allv[i] for i in range(len(allv)) if i not in idx]
        tot += 1
        hit += abs(st.median(a) - st.median(b)) >= obs - 1e-12
    return hit / tot


def mw_exact_p(x, y):
    def U(a, b):
        return sum((p > q) + 0.5 * (p == q) for p in a for q in b)
    allv, n = list(x) + list(y), len(x)
    mu, uo = len(x) * len(y) / 2, U(x, y)
    hit = tot = 0
    for idx in itertools.combinations(range(len(allv)), n):
        a = [allv[i] for i in idx]
        b = [allv[i] for i in range(len(allv)) if i not in idx]
        tot += 1
        hit += abs(U(a, b) - mu) >= abs(uo - mu) - 1e-12
    return hit / tot


def sign_p(diffs):
    n = sum(1 for d in diffs if d != 0)
    k = sum(1 for d in diffs if d > 0)
    tail = sum(math.comb(n, i) for i in range(max(k, n - k), n + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def rng(v):
    return {"median": st.median(v), "min": min(v), "max": max(v), "n": len(v)} if v else None


# ---- DeepSeek runs --------------------------------------------------------------------
def ds_row(d):
    m = re.match(r"(greedy|bestofn)-s(\d+)-(\d+)$", d.name)
    arm, seed, job = m.group(1), int(m.group(2)), m.group(3)
    summ = load(d / "summary.json", {})
    rows = jsonl(d / "results.jsonl")
    node = node_kv(d / "node.txt")
    run = load(d / "run.json", {})
    ev = load(d / "evaluate-best" / "summary.json", {})
    resumes = sorted(d.parent.glob(d.name + "-resume-*"))
    attempts = sum(int((r.get("llm") or {}).get("http_attempts", 0) or 0) for r in rows)
    tok = {k: summ.get(k, 0) for k in ("prompt_tokens", "completion_tokens", "reasoning_tokens", "total_tokens", "truncated_replies", "llm_seconds", "elapsed_s")}
    fail = sum(1 for r in rows if not r.get("ok"))
    ended = summ.get("ended_because", "")
    src = {"api_calls": rel(d / "results.jsonl") + "::sum(llm.http_attempts)", "total_tokens": rel(d / "summary.json") + "::total_tokens",
           "final_eval": rel(d / "evaluate-best" / "summary.json")}
    resume_info = None
    if resumes:
        rd = resumes[-1]
        rs = load(rd / "summary.json", {})
        rrows = jsonl(rd / "results.jsonl")
        attempts += sum(int((r.get("llm") or {}).get("http_attempts", 0) or 0) for r in rrows)
        fail += sum(1 for r in rrows if not r.get("ok"))
        for k in tok:
            tok[k] += rs.get(k, 0) or 0
        rev = load(rd / "evaluate-best" / "summary.json", {})
        resume_info = {"dir": rel(rd), "job": node_kv(rd / "node.txt").get("job"), "host": node_kv(rd / "node.txt").get("host"),
                       "extra_http_attempts": sum(int((r.get("llm") or {}).get("http_attempts", 0) or 0) for r in rrows),
                       "extra_total_tokens": rs.get("total_tokens", 0), "second_eval_ratios": [x["analysis"]["ratio"] for x in rev.get("measurements", [])],
                       "second_eval_median_speedup": rev.get("median_speedup"), "second_eval_all_pass": rev.get("all_pass"),
                       "evidence": [rel(rd / "summary.json"), rel(rd / "results.jsonl"), rel(rd / "evaluate-best" / "summary.json"), rel(rd / "resume.json")]}
        ended = ended + " -> completed to 40 HTTP attempts by resume job " + str(resume_info["job"])
        src["api_calls"] += " + " + rel(rd / "results.jsonl")
        src["total_tokens"] += " + " + rel(rd / "summary.json") + "::total_tokens"
    best_patch = d / "best.patch"
    speed = claim(ev)
    updates = summ.get("rank_updates", [])
    return {
        "experiment": "deepseek", "arm": arm, "seed": seed, "job": job, "host": node.get("host", ""),
        "node_family": node.get("host", "")[:4], "model_returned": (run.get("model_probe") or {}).get("model", ""),
        "http_attempts": attempts, "generations_rows": len(rows) + (len(jsonl(resumes[-1] / "results.jsonl")) if resumes else 0),
        "ended_because": ended, "prompt_tokens": tok["prompt_tokens"], "completion_tokens": tok["completion_tokens"],
        "reasoning_tokens": tok["reasoning_tokens"], "total_tokens": tok["total_tokens"], "truncated_replies": tok["truncated_replies"],
        "search_elapsed_s": round(tok["elapsed_s"], 1), "llm_seconds": round(tok["llm_seconds"], 1),
        "job_start": node.get("start", ""), "job_end": node.get("end", ""),
        "failed_rows": fail, "rank_updates": len(updates), "update_generations": [u["generation"] for u in updates],
        "search_best_ranked_speedup": summ.get("best_ranked_speedup"),
        "final_patch": rel(best_patch), "final_patch_sha256": sha(best_patch),
        "final_ratios": [x["analysis"]["ratio"] for x in ev.get("measurements", [])],
        "final_passes": ev.get("measurements_passing_rule"), "final_median_speedup": ev.get("median_speedup"),
        "best_confirmed_speedup": speed, "course_metric": (speed - 1.0) / tok["total_tokens"] if tok["total_tokens"] else None,
        "logspeed_per_Mtok": math.log(speed) / (tok["total_tokens"] / 1e6) if tok["total_tokens"] else None,
        "resume": resume_info,
        "evidence": {"summary": rel(d / "summary.json"), "results": rel(d / "results.jsonl"), "credits": rel(d / "credits.csv"),
                     "run": rel(d / "run.json"), "node": rel(d / "node.txt"), "init": rel(d / "init.json"),
                     "final_evaluation": rel(d / "evaluate-best" / "summary.json"), "final_evaluation_log": rel(d / "final-evaluation.log"),
                     "profile": rel(d / "profile.json"), "field_sources": src},
    }


def qwen_row(d):
    r = qwen_agg.run_row(d)
    if not r:
        return None
    node = node_kv(d / "node.txt")
    ev = load(d / "evaluate-best" / "summary.json", {})
    speed = r["final_confirmed_speedup"]
    return {
        "experiment": "qwen", "arm": r["arm"], "seed": r["seed"], "job": r["job"], "host": r["host"], "node_family": r["host"][:4],
        "model_returned": r["model_returned"], "http_attempts": r["api_calls"], "generations_rows": None, "ended_because": r["ended_because"],
        "prompt_tokens": r["prompt_tokens"], "completion_tokens": r["completion_tokens"], "reasoning_tokens": None,
        "total_tokens": r["total_tokens"], "truncated_replies": None, "search_elapsed_s": round(r["elapsed_min"] * 60, 1), "llm_seconds": None,
        "job_start": node.get("start", ""), "job_end": node.get("end", ""),
        "failed_rows": sum(v for k, v in r["stages"].items() if k != "measured"), "rank_updates": None, "update_generations": None,
        "search_best_ranked_speedup": r["search_best_confirmed_speedup"],
        "final_patch": rel(d / "best.patch"), "final_patch_sha256": sha(d / "best.patch"),
        "final_ratios": r.get("final_ratios", []), "final_passes": r.get("final_passes"), "final_median_speedup": r.get("final_median_speedup"),
        "best_confirmed_speedup": speed, "course_metric": r["bonus_quotient"],
        "logspeed_per_Mtok": math.log(speed) / (r["total_tokens"] / 1e6) if r["total_tokens"] else None, "resume": None,
        "evidence": {"summary": rel(d / "summary.json"), "results": rel(d / "results.jsonl"), "credits": rel(d / "credits.csv"),
                     "run": rel(d / "run.json"), "node": rel(d / "node.txt"), "final_evaluation": rel(d / "evaluate-best" / "summary.json"),
                     "field_sources": {"http_attempts": rel(d / "summary.json") + "::api_calls", "total_tokens": rel(d / "summary.json") + "::total_tokens"}},
    }


# ---- common-budget (first K HTTP requests) analysis ------------------------------------
def common_budget(K=34):
    out = []
    jobs = {}  # patch path -> re-measurement summary dir (post-hoc jobs)
    for sj in glob.glob(str(ROOT / "runs" / "deepseek-common34" / "*" / "evaluate-*" / "summary.json")):
        s = load(sj, {})
        jobs[s.get("patch")] = (sj, s)
    for d in sorted((ROOT / "runs" / "deepseek").glob("*-s[1-5]-[0-9]*")):
        if not d.is_dir() or "resume" in d.name:
            continue
        rows = jsonl(d / "results.jsonl")
        credits = {int(l.split(",")[0]): l.strip().split(",") for l in open(d / "credits.csv").read().splitlines()[1:] if l.strip()}
        cum, best, last, tok = 0, None, None, 0
        for r in rows:
            a = int((r.get("llm") or {}).get("http_attempts", 0) or 0)
            if cum + a > K:
                break
            cum += a
            last = r["generation"]
            tok += (r.get("llm") or {}).get("total_tokens", 0) or 0
            if r.get("updated"):
                best = r
        final_ev = load(d / "evaluate-best" / "summary.json", {})
        fin_gen = load(d / "summary.json", {})["rank_updates"][-1]["generation"] if load(d / "summary.json", {}).get("rank_updates") else None
        row = {"arm": d.name.split("-s")[0], "seed": int(re.search(r"-s(\d)-", d.name).group(1)), "run": rel(d), "attempts_counted": cum,
               "last_generation_within_budget": last, "tokens_through_budget": tok,
               "credits_row_total_tokens_at_last_gen": int(credits[last][5]) if last in credits else None}
        if best is None:
            row.update({"patch_generation": None, "status": "no update within budget (baseline)", "best_confirmed_speedup": 1.0})
        else:
            patch = d / "patches" / ("gen_%d.patch" % best["generation"])
            row.update({"patch_generation": best["generation"], "search_R": best["rank_R"], "search_speedup": 1.0 / best["rank_R"],
                        "patch": rel(patch), "patch_sha256": sha(patch), "same_as_final_patch": best["generation"] == fin_gen})
            if best["generation"] == fin_gen:
                row.update({"status": "same patch as final; reused its independent re-measurement",
                            "remeasure_evidence": rel(d / "evaluate-best" / "summary.json"),
                            "ratios": [x["analysis"]["ratio"] for x in final_ev.get("measurements", [])],
                            "passes": final_ev.get("measurements_passing_rule"), "best_confirmed_speedup": claim(final_ev)})
            else:
                hit = jobs.get(str(patch))
                if hit:
                    sj, s = hit
                    row.update({"status": "different patch; 3 independent re-measurements run post hoc", "remeasure_evidence": rel(sj),
                                "ratios": [x["analysis"]["ratio"] for x in s.get("measurements", [])],
                                "passes": s.get("measurements_passing_rule"), "best_confirmed_speedup": claim(s)})
                else:
                    row.update({"status": "UNCONFIRMED: re-measurement not completed", "best_confirmed_speedup": None})
        bc = row.get("best_confirmed_speedup")
        row["course_metric_budget"] = (bc - 1.0) / tok if bc is not None and tok else None
        out.append(row)
    return out


# ---- controls --------------------------------------------------------------------------
def controls():
    rows = []

    def rule(path, label, note="", valid=True):
        rs = jsonl(path)
        ratios = [x.get("ratio") for x in rs]
        node = node_kv(Path(path).parent / "node.txt")
        rows.append({"control": label, "kind": "compiler" , "n": len(rs), "ratios": ratios,
                     "median_speedup": 1.0 / st.median(ratios) if ratios else None, "range_speedup": [1.0 / max(ratios), 1.0 / min(ratios)] if ratios else None,
                     "passes_rule": sum(1 for x in rs if x.get("faster")), "host": node.get("host"), "job": node.get("job"),
                     "valid": valid, "note": note, "evidence": rel(path)})

    c1, c2 = ROOT / "runs" / "controls-1068897", ROOT / "runs" / "controls-native-1071478"
    rule(c1 / "rule-O3-vs-O2.jsonl", "C1 -O3 vs -O2 (batch 1068897)")
    rule(c2 / "rule-O3-vs-O2.jsonl", "C1 -O3 vs -O2 (batch 1071478)")
    rule(c1 / "rule-O3native-vs-O2.jsonl", "C1 -O3 -march=native vs -O2 (batch 1068897)",
         "INVALID, superseded by batch 1071478: init-O3native.json in this batch reports ok=false (the -march=native init failed), so the ratios of exactly 1.0 are not a comparison", valid=False)
    rule(c2 / "rule-O3native-vs-O2.jsonl", "C1 -O3 -march=native vs -O2 (rerun 1071478)")
    rule(c2 / "rule-O3native-vs-O3.jsonl", "C1 -O3 -march=native vs -O3 (rerun 1071478)", "native's increment over -O3; below the 2% gate")
    for name, label in (("inert", "inert patch (null check)"), ("attempt-1", "C2 human patch attempt-1"), ("attempt-2", "C2 human patch attempt-2")):
        sj = c1 / ("eval-" + name) / ("evaluate-" + name) / "summary.json"
        s = load(sj, {})
        ratios = [x["analysis"]["ratio"] for x in s.get("measurements", [])]
        node = node_kv(c1 / "node.txt")
        rows.append({"control": label + " vs -O2 (batch 1068897)", "kind": "patch", "n": len(ratios), "ratios": ratios,
                     "median_speedup": s.get("median_speedup"), "range_speedup": [1.0 / max(ratios), 1.0 / min(ratios)] if ratios else None,
                     "passes_rule": s.get("measurements_passing_rule"), "host": node.get("host"), "job": node.get("job"), "valid": True,
                     "note": "", "evidence": rel(sj)})
    return rows


def write_csv(path, rows, cols):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: (json.dumps(r.get(k)) if isinstance(r.get(k), (list, dict)) else r.get(k)) for k in cols})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    qrows = [r for r in (qwen_row(d) for d in sorted((ROOT / "runs" / "main").glob("*-s*-*")) if d.is_dir()) if r]
    drows = [ds_row(d) for d in sorted((ROOT / "runs" / "deepseek").glob("*-s[1-5]-[0-9]*")) if d.is_dir() and "resume" not in d.name]
    allrows = sorted(qrows + drows, key=lambda r: (r["experiment"], r["arm"], r["seed"]))
    cb = common_budget(34)
    ctl = controls()

    stats = {}
    L = ["# Phase 1 final statistics", "",
         "best_confirmed_speedup = median speedup of the 3 independent re-measurements of the run's fixed final patch (1.0 if any fails the frozen rule).",
         "Course metric = (best_confirmed_speedup - 1) / total_tokens (all tokens actually spent, truncated replies included). log-speedup per Mtok is supplementary.",
         "Primary group test: exact two-sided permutation test of the difference of medians (all C(10,5)=252 splits), chosen to match the median-and-range",
         "reporting of C4; the exact Mann-Whitney test and a paired sign test are given alongside, none replaces the primary. n = 5 seeds per arm, so none of these",
         "removes selection effects or isolates inheritance, feedback or selection; the arms differ in more than one thing.", ""]

    def block(name, rows, a_arm, b_arm, key, label, unit=""):
        a = [r[key] for r in rows if r["arm"] == a_arm and r.get(key) is not None]
        b = [r[key] for r in rows if r["arm"] == b_arm and r.get(key) is not None]
        if len(a) < 2 or len(b) < 2:
            L.append("- %s %s: not enough finished runs" % (name, label))
            return
        pairs = {}
        for r in rows:
            if r.get(key) is not None:
                pairs.setdefault(r["seed"], {})[r["arm"]] = r[key]
        diffs = [v[a_arm] - v[b_arm] for v in pairs.values() if a_arm in v and b_arm in v]
        s = {"a": rng(a), "b": rng(b), "perm_median_p": perm_median_p(a, b), "mw_exact_p": mw_exact_p(a, b),
             "paired_a_higher": sum(1 for d in diffs if d > 0), "paired_n": len(diffs), "paired_sign_p": sign_p(diffs)}
        stats["%s|%s|%s" % (name, label, key)] = s
        f = lambda v: "median %.5g, range [%.5g, %.5g]" % (v["median"], v["min"], v["max"])
        L.append("- **%s, %s** — %s: %s = %s; %s = %s. Permutation (median) p=%.4f; Mann-Whitney exact p=%.4f; %s higher in %d/%d paired seeds, sign test p=%.4f."
                 % (name, label, key, a_arm, f(s["a"]), b_arm, f(s["b"]), s["perm_median_p"], s["mw_exact_p"], a_arm, s["paired_a_higher"], s["paired_n"], s["paired_sign_p"]))

    qr = [r for r in qrows]
    dr = [r for r in drows]
    L.append("## Qwen3-coder-next matrix (search vs best-of-N), full runs")
    block("Qwen", qr, "search", "bestofn", "best_confirmed_speedup", "full")
    block("Qwen", qr, "search", "bestofn", "course_metric", "full")
    L += ["", "## DeepSeek (greedy vs best-of-N), full runs as executed", ""]
    block("DeepSeek", dr, "greedy", "bestofn", "best_confirmed_speedup", "full")
    block("DeepSeek", dr, "greedy", "bestofn", "course_metric", "full")
    block("DeepSeek", dr, "greedy", "bestofn", "logspeed_per_Mtok", "full (supplementary)")
    L.append("")
    L.append("Actual HTTP attempts per run (greedy): %s; (bestofn): %s." % (
        [r["http_attempts"] for r in sorted(dr, key=lambda r: r["seed"]) if r["arm"] == "greedy"],
        [r["http_attempts"] for r in sorted(dr, key=lambda r: r["seed"]) if r["arm"] == "bestofn"]))
    L += ["", "## DeepSeek common-budget analysis (post hoc: best patch by the then-current ranking within the first 34 HTTP requests)", "",
          "34 is the shortest run's attempt count (greedy seeds 4 and 5), fixed before looking at performance. Original full results remain the primary record.", ""]
    if all(r.get("best_confirmed_speedup") is not None for r in cb):
        block("DeepSeek", cb, "greedy", "bestofn", "best_confirmed_speedup", "first 34 requests")
        block("DeepSeek", cb, "greedy", "bestofn", "course_metric_budget", "first 34 requests")
    else:
        L.append("- UNCONFIRMED: at least one 34-request patch has no completed independent re-measurement yet; no budget-matched result is claimed.")
    (OUT / "STATS.md").write_text("\n".join(L) + "\n")

    cols = ["experiment", "arm", "seed", "job", "host", "node_family", "model_returned", "http_attempts", "generations_rows", "ended_because",
            "prompt_tokens", "completion_tokens", "reasoning_tokens", "total_tokens", "truncated_replies", "search_elapsed_s", "llm_seconds",
            "job_start", "job_end", "failed_rows", "rank_updates", "update_generations", "search_best_ranked_speedup", "final_patch",
            "final_patch_sha256", "final_ratios", "final_passes", "final_median_speedup", "best_confirmed_speedup", "course_metric", "logspeed_per_Mtok"]
    write_csv(OUT / "phase1_runs.csv", [dict(r, **{"evidence_summary": r["evidence"]["summary"]}) for r in allrows], cols + ["evidence_summary"])
    ccols = ["arm", "seed", "run", "attempts_counted", "last_generation_within_budget", "tokens_through_budget", "credits_row_total_tokens_at_last_gen",
             "patch_generation", "search_R", "search_speedup", "patch", "patch_sha256", "same_as_final_patch", "status", "remeasure_evidence", "ratios",
             "passes", "best_confirmed_speedup", "course_metric_budget"]
    write_csv(OUT / "common34.csv", cb, ccols)
    write_csv(OUT / "controls.csv", ctl, ["control", "kind", "n", "ratios", "median_speedup", "range_speedup", "passes_rule", "host", "job", "valid", "note", "evidence"])
    (OUT / "phase1_final.json").write_text(json.dumps({"runs": allrows, "common_budget_34": cb, "controls": ctl, "stats": stats,
                                                       "freeze": {"manifest": rel(OUT / "MANIFEST-raw.sha256"), "versions": rel(OUT / "VERSIONS.txt")}}, indent=2) + "\n")
    print((OUT / "STATS.md").read_text())


if __name__ == "__main__":
    main()
