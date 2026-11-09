#!/usr/bin/env python3
"""Per-run table of all 40 search runs (8 configurations x 5 seeds), recomputed from results.jsonl / credits.csv / summary.json / measurements / evaluate-best.
Output: tables/runs_all.csv, tables/runs_stage_counts.csv, figure_data/run_updates.csv, tables/patch_scope.csv (lineage and files per final patch)."""
import sys, re, datetime; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pm_lib import *
from runsets import *

def rows_of(dirs):
    rows = []
    for d in dirs:
        rows += jl(d / "results.jsonl")
    return rows

def last_credit(d):
    p = d / "credits.csv"
    if not p.exists():
        return {}
    lines = list(csv.DictReader(open(p)))
    return lines[-1] if lines else {}

def parse_utc(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc).timestamp()
    except Exception:
        return None

def lineage(rows, gen):
    by = {r["id"]: r for r in rows}
    chain, cur, seen = [], gen, set()
    while cur and cur in by and cur not in seen:
        seen.add(cur); chain.append(by[cur]); cur = by[cur].get("parent")
    return list(reversed(chain))

def patch_stats(path):
    t = Path(path).read_text(errors="replace") if path and Path(path).exists() else ""
    return {"files": sorted(set(re.findall(r"^\+\+\+ b/(\S+)", t, re.M))), "hunks": len(re.findall(r"^@@", t, re.M)),
            "added": sum(1 for l in t.splitlines() if l.startswith("+") and not l.startswith("+++")),
            "removed": sum(1 for l in t.splitlines() if l.startswith("-") and not l.startswith("---"))}

OUT, STAGES, UPD, PATCH = [], [], [], []
for r in runs():
    cfg = CFG[r["cfg"]]; dirs = r["dirs"]; fd = r["final_dir"]; d0 = dirs[0]
    rows = rows_of(dirs)
    sums = [jload(d / "summary.json", {}) for d in dirs]
    runj = jload(d0 / "run.json", {})
    algo = cfg[2]
    # ---- requests, tokens, failures
    http = sum((x.get("llm") or {}).get("http_attempts", 0) for x in rows if x.get("llm"))
    has_llm = any(x.get("llm") for x in rows)
    api_calls = (sums[0].get("api_calls") or 0) + sum((s.get("api_calls") or 0) for s in sums[1:])
    prompt = sum(s.get("prompt_tokens", 0) for s in sums); comp = sum(s.get("completion_tokens", 0) for s in sums)
    reas = sum(s.get("reasoning_tokens", 0) or 0 for s in sums)
    total = prompt + comp                        # reasoning tokens are a subset of completion tokens
    no_usage = sum(1 for x in rows if x.get("llm") and not x["llm"].get("usage_seen")) if has_llm else None
    trunc = sum(1 for x in rows if x.get("llm") and x["llm"].get("finish_reason") == "length") if has_llm else None
    models = sorted({x["llm"].get("model_returned") for x in rows if x.get("llm") and x["llm"].get("model_returned")}) if has_llm else []
    sc = {}
    for x in rows:
        st = "measured" if x.get("ok") else (x.get("stage") or "unknown")
        sc[st] = sc.get(st, 0) + 1
    STAGES.append({"run": r["id"], **sc})
    confirmed_rows = [x for x in rows if x.get("ok") and x.get("confirmed")]
    best_conf = max((x["speedup"] for x in confirmed_rows), default=1.0)
    best_conf_gen = max(confirmed_rows, key=lambda x: x["speedup"])["generation"] if confirmed_rows else 0
    last_s = sums[-1]
    best_rank = last_s.get("best_ranked_speedup") if cfg[4] == "I2" else None
    cr = last_credit(fd)
    credits_conf = float(cr["best_confirmed_speedup"]) if "best_confirmed_speedup" in cr else None
    credits_calls = int(cr["calls"]) if cr.get("calls") else None
    # ---- independent re-measurement of the fixed final patch (rule replay)
    evd = fd / "evaluate-best" if (fd / "evaluate-best").exists() else fd / "final/evaluate-best"
    ev = [rule(jload(f)) for f in sorted(evd.glob("m*.json"))]
    ev = [e for e in ev if e]
    ev_sp = 1 / median([e["ratio"] for e in ev]) if ev else None
    ev_pass = sum(1 for e in ev if e["faster"])
    es = jload(evd / "summary.json", {})
    p_sum = evd / "summary.json"
    s_sum = fd / "summary.json"
    ev_secs = (p_sum.stat().st_mtime - s_sum.stat().st_mtime) if (p_sum.exists() and s_sum.exists() and p_sum.stat().st_mtime > s_sum.stat().st_mtime) else None   # file times: end of search -> end of 3rd re-measurement
    fn = fd / "final/node.txt"
    if fn.exists():
        k = kv(fn)
        try:
            a = datetime.datetime.fromisoformat(k["start"]); b = datetime.datetime.fromisoformat(k["end"]); ev_secs = (b - a).total_seconds()
        except Exception:
            pass
    # ---- final patch scope and lineage
    final_gen = best_conf_gen if algo != "greedy" and not (cfg[0].endswith("I2")) else (last_s.get("best_ranked_generation") or 0)
    if cfg[0].endswith("I2"):
        final_gen = last_s.get("best_ranked_generation") or 0
    else:
        final_gen = last_s.get("best_confirmed_generation") or 0
    chain = lineage(rows, final_gen) if final_gen else []
    labels = [c.get("label") for c in chain]
    ps = patch_stats(fd / "best.patch")
    rec_upd = len(last_s.get("rank_updates", [])) if cfg[4] == "I2" else None      # rank-rule record updates (best-of-N: records, not cumulative)
    nupd = 1 if algo == "best-of-N" else (rec_upd if cfg[4] == "I2" else sum(1 for c in chain if c.get("improved_on_parent")))
    nodes = []
    for d in dirs:
        cand = [kv(d / "node.txt").get("host")] + [kv(f).get("host") for f in sorted(d.glob("segments/*.node.txt"))]
        for h in cand:
            if h and h not in nodes:
                nodes.append(h)
    elapsed = sum(s.get("elapsed_s", 0) for s in sums)
    llm_secs = sum((x.get("llm") or {}).get("llm_seconds", 0) for x in rows) if has_llm else None
    ended = last_s.get("ended_because")
    OUT.append({
        "run": r["id"], "config": r["cfg"], "algorithm": algo, "model_requested": runj.get("model_requested"), "model_returned": ";".join(models) if models else "probe only: " + str(runj.get("model_probe", {}).get("model", "") if isinstance(runj.get("model_probe"), dict) else ""),
        "impl": cfg[4], "seed": r["seed"], "git_commit": (runj.get("git_commit") or "")[:7], "temperature": runj.get("temperature"), "max_tokens": runj.get("max_tokens"),
        "nodes": "/".join(nodes), "http_requests": http if has_llm else None, "api_calls_summary": api_calls, "requests_counted_as": "HTTP requests (llm.http_attempts)" if has_llm else "model calls (HTTP attempts not recorded)",
        "result_rows": len(rows), "ended_because": ended, "prompt_tokens": prompt, "completion_tokens": comp, "reasoning_tokens_subset_of_completion": reas, "total_tokens": total,
        "no_usage_requests": no_usage, "truncated_replies": trunc, "search_elapsed_s": elapsed, "llm_seconds": llm_secs, "remeasure_elapsed_s": ev_secs,
        "measured_candidates": sc.get("measured", 0), "compile_fail": sc.get("compile", 0), "check_fail": sum(sc.get(k, 0) for k in ("correctness", "crash", "load", "profile", "CanMehHarness")),
        "unchanged": sc.get("unchanged", 0), "http_fail": sc.get("llm_http", 0), "truncated_stage": sc.get("truncated", 0), "no_code": sc.get("llm_nocode", 0) + sc.get("llm", 0), "no_request_rows": sc.get("show", 0),
        "confirmed_candidates": len(confirmed_rows), "improved_on_parent_rows": sum(1 for x in rows if x.get("improved_on_parent")),
        "search_best_confirmed_speedup": best_conf, "search_best_ranked_speedup": best_rank, "credits_last_best_confirmed": credits_conf,
        "remeasure_speedup_median3": ev_sp, "remeasure_passes": f"{ev_pass}/{len(ev)}", "remeasure_ratios": json.dumps([round(e['ratio'], 6) for e in ev]),
        "final_patch_generation": final_gen, "final_patch_files": ";".join(ps["files"]), "final_patch_hunks": ps["hunks"], "final_patch_added": ps["added"], "final_patch_removed": ps["removed"],
        "lineage_depth": len(chain), "cumulative_updates": nupd, "record_updates_rank_rule": rec_upd, "functions_in_final_patch": ";".join(dict.fromkeys(labels)) if labels else "",
        "course_metric_search": ((credits_conf if credits_conf else (best_rank if best_rank else best_conf)) - 1) / total if total else None,
        "course_metric_remeasured": ((ev_sp - 1) / total) if ev_sp and total else None,
        "dirs": ";".join(str(d.relative_to(ROOT)) for d in dirs)})
    for u in last_s.get("rank_updates", []):
        UPD.append({"run": r["id"], "generation": u["generation"], "label": u["label"], "previous_R": u["previous_R"], "R": u["R"], "step_pct": 100 * (1 - u["R"] / u["previous_R"]),
                    "speedup_after": 1 / u["R"]})
    for c in chain:
        PATCH.append({"run": r["id"], "generation": c["generation"], "label": c.get("label"), "region": c.get("region"), "parent": c.get("parent"), "ratio": c.get("ratio"),
                      "ratio_vs_parent": c.get("ratio_vs_parent"), "improved_on_parent": c.get("improved_on_parent"), "confirmed": c.get("confirmed"),
                      "updated": c.get("updated"), "file": c.get("file")})
write_csv(PM / "tables/runs_all.csv", OUT)
write_csv(PM / "tables/runs_stage_counts.csv", STAGES)
write_csv(PM / "figure_data/run_updates.csv", UPD)
write_csv(PM / "tables/lineage_of_final_patches.csv", PATCH)
src("runs-1", "per-run requests/tokens/failures/speedups", "runs/main, runs/deepseek, runs/followup/resume-greedy-*, runs/round2/runs", "results.jsonl, summary.json, credits.csv, evaluate-best/m*.json",
    "see build_runs.py; speedup=1/median ratio of three independent re-measurements (rule replay)")
if __name__ == "__main__":
    for o in OUT:
        print(f"{o['run']:18s} req={o['http_requests']} calls={o['api_calls_summary']} tok={o['total_tokens']:7d} nousage={o['no_usage_requests']} trunc={o['truncated_replies']} meas={o['measured_candidates']:2d} comp={o['compile_fail']:2d} chk={o['check_fail']} unch={o['unchanged']:2d} http={o['http_fail']} conf={o['confirmed_candidates']:2d} best_conf={o['search_best_confirmed_speedup']:.4f} rank={o['search_best_ranked_speedup']} rem={o['remeasure_speedup_median3']:.4f} {o['remeasure_passes']} depth={o['lineage_depth']} upd={o['cumulative_updates']} fin_gen={o['final_patch_generation']} rem_s={o['remeasure_elapsed_s']}")
