#!/usr/bin/env python3
"""Collect run-environment facts for the report from the actual logs (no re-measurement).

Per formal DeepSeek run: seed, node, node CPU (from runs/phase1-final/node_hardware/<node>.txt, recorded post hoc by scripts/node_facts.sh;
'not recorded' when that file is missing or empty), HTTP requests, search elapsed, job wall-clock (job start -> end in node.txt, which includes
init, null check, search and the three final re-measurements), null-run result (init.json) with node, baseline ms (meta.json), compiler line
(node.txt), SDK optimisation flags (meta.json).  Also the data identifiers from bench.err and the preflight summary.
Writes runs/phase1-final/run_facts.json.
"""
import json, re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DS = ROOT / "runs/deepseek"
HW = ROOT / "runs/phase1-final/node_hardware"


def kv(p):
    d = {}
    for l in open(p):
        if "=" in l:
            k, v = l.strip().split("=", 1)
            d[k] = v
    return d


def cpu(node):
    f = HW / (node + ".txt")
    if f.exists():
        m = re.search(r"Model name:\s*(.+)", f.read_text())
        if m:
            return m.group(1).strip()
    return "not recorded"


facts = {"runs": [], "data": {}, "preflight": {}}
for d in sorted(DS.glob("*-s[1-5]-[0-9]*")):
    if "resume" in d.name or not d.is_dir():
        continue
    arm, seed = re.match(r"(greedy|bestofn)-s(\d)-", d.name).groups()
    node = kv(d / "node.txt")
    meta = json.load(open(d / "meta.json"))
    init = json.load(open(d / "init.json"))
    summ = json.load(open(d / "summary.json"))
    run = json.load(open(d / "run.json"))
    t0, t1 = datetime.fromisoformat(node["start"]), datetime.fromisoformat(node["end"])
    bench = (d / "bench.err").read_text()
    m = re.search(r"read (\d+) bytes and decoded (\d+) messages, (\d+) fields, checksum (\w+)", bench)
    cpu_line = re.search(r"Run on \((\d+) X (\d+) MHz CPU s\)", bench)
    facts["data"].setdefault("identifiers", {"bytes": int(m.group(1)), "messages": int(m.group(2)), "fields": int(m.group(3)), "checksum": m.group(4)})
    assert facts["data"]["identifiers"] == {"bytes": int(m.group(1)), "messages": int(m.group(2)), "fields": int(m.group(3)), "checksum": m.group(4)}
    r = {"arm": arm, "seed": int(seed), "job": node["job"], "node": node["host"], "cpu": cpu(node["host"]),
         "benchmark_header": "%s CPUs x %s MHz (as printed by Google Benchmark)" % (cpu_line.group(1), cpu_line.group(2)),
         "search_elapsed_s": summ["elapsed_s"], "job_wallclock_s": (t1 - t0).total_seconds(), "ended_because": summ["ended_because"],
         "null_ok": init["null_ok"], "null_ratio": init["null_ratio"], "null_p": init["null_p"], "null_spread": init.get("null_spread"),
         "baseline_ms": meta["baseline_ms"], "opt": meta["opt"], "cxxstd": meta["cxxstd"], "min_time": meta["min_time"],
         "repeat": meta["repeat"], "repetitions": meta["repetitions"], "compiler": node["cxx"], "model_returned": (run.get("model_probe") or {}).get("model"),
         "evidence": {"node": str((d / "node.txt").relative_to(ROOT)), "init": str((d / "init.json").relative_to(ROOT)), "meta": str((d / "meta.json").relative_to(ROOT)),
                      "bench": str((d / "bench.err").relative_to(ROOT))}}
    res = sorted(d.parent.glob(d.name + "-resume-*"))
    if res:
        rn = kv(res[-1] / "node.txt")
        ri = json.load(open(res[-1] / "init.json"))
        r["resume"] = {"job": rn["job"], "node": rn["host"], "cpu": cpu(rn["host"]), "null_ok": ri["null_ok"], "null_ratio": ri["null_ratio"],
                       "wallclock_s": (datetime.fromisoformat(rn["end"]) - datetime.fromisoformat(rn["start"])).total_seconds()}
    facts["runs"].append(r)

pre = {}
for lv in ("mt8192", "mt16384", "mt32768"):
    p = json.load(open(DS / "preflight-1071764" / lv / "preflight/preflight.json"))
    e = p["entries"]
    fin = [(x.get("llm") or x).get("finish_reason") for x in e]
    mods = sorted({(x.get("llm") or x).get("model_returned") or (x.get("llm") or x).get("model") for x in e})
    pre[lv] = {"calls": len(e), "truncated": sum(1 for f in fin if f == "length"), "models": mods, "total_tokens": p["totals"]["total_tokens"]}
facts["preflight"] = pre
facts["preflight"]["total_tokens_all_levels"] = sum(v["total_tokens"] for v in pre.values() if isinstance(v, dict))
(ROOT / "runs/phase1-final/run_facts.json").write_text(json.dumps(facts, indent=2) + "\n")
for r in facts["runs"]:
    print(r["arm"], r["seed"], r["node"], r["cpu"], "wall %.2f h" % (r["job_wallclock_s"] / 3600), "null", r["null_ok"], round(r["null_ratio"], 4), "base", round(r["baseline_ms"], 1), r.get("resume", {}).get("node", ""))
print(facts["data"], json.dumps(facts["preflight"]))
