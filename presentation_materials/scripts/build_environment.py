#!/usr/bin/env python3
"""Data / software / machine / model facts per run family, with the file each value comes from; per-run baseline times (not comparable across nodes)."""
import sys, collections; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pm_lib import *
from runsets import *
rows = []
def add(item, value, source): rows.append({"item": item, "value": value, "source": source})
add("FIT SDK version", "21.201.0", "runs/phase1-final/VERSIONS.txt (fit_sdk=21.201.0)")
add("workload", "decode the 4 activity files with the SDK decoder; every decoded field value folded into a 64-bit checksum; timed with CanMehBench (reference vs candidate library in one process pair)", "README.md Architecture; src/workloads/SdkDecode.cpp")
add("data: total bytes", 907007, "runs/round2/runs/ds-population-s1/bench.err; runs/phase1-final/run_facts.json data.identifiers")
add("data: messages decoded", 34251, "same")
add("data: fields decoded", 428714, "same")
add("data: checksum (CanMehBench fold)", "92bebfd7f8978fc8", "same")
import hashlib
per = {"intervals.fit": (3626, 46984), "long_run.fit": (14410, 187256), "ride.fit": (10809, 140448), "treadmill.fit": (5406, 54026)}
for f, (m, fl) in per.items():
    p = ROOT / "build/data" / f
    add(f"data file {f}", f"{p.stat().st_size} bytes; {m} messages; {fl} fields; sha256 {hashlib.sha256(p.read_bytes()).hexdigest()[:16]}...", "build/data/*.fit; counts from the stock decoder (scripts/followup/driver.cpp 'single' mode on the 4 originals); sums equal the CanMehBench totals")
add("regions (functions / units the search can rewrite)", len(jload(ROOT / "runs/round2/runs/ds-population-s1/profile_samples.json")), "profile_samples.json (round-2 runs)")
add("regions with profile samples (per run, 20 s perf)", "76 (ds-population-s1); ~70-80 in other runs", "runs/*/profile.json, profile_samples.json")
add("compiler", "c++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0 (GCC)", "runs/*/run.json compiler_version")
add("compiler options for stock and candidates", "-std=c++17 -O2 (C1 controls: -O3, -O3 -march=native which resolves to haswell)", "runs/*/run.json (opt, cxxstd); runs/controls-native-1071478/node.txt")
add("measurement parameters", "10 processes x 9 repetitions per measurement (--repeat 10 --repetitions 9), min-time 0.25 s, alpha 0.01, minimum effect 2%, unstable if ratio spread > 0.25", "runs/*/run.json meta, rule; src/Search.cpp constants")
add("machine", "NUS cluster compute nodes xcnc*/xcnd*: 2 x Intel Xeon E5-2620 v3 @ 2.40 GHz (6 cores, 2 threads each, 24 logical CPUs, max 3.2 GHz, 64 GB, 30 MiB L3), governor schedutil, Linux 6.8.0-1xx; whole node per job", "runs/phase1-final/node_hardware/*.txt; runs/*/node.txt")
add("models: Qwen", "requested qwen3-coder-next, returned qwen3-coder-next (server fingerprint vllm-0.26.0-1cf708c9); temperature 0.8; max_tokens 4096", "runs/setup/llm-check.json; runs/main/*/run.json; runs/round2/runs/qwen-*/results.jsonl llm.model_returned")
add("models: DeepSeek", "requested deepseek-v4.1-flash, every response returned deepseek-v4.1-flash-1017 (expected id enforced); temperature 0.8; max_tokens 32768; request timeout 600 s", "runs/deepseek/*/run.json; results.jsonl llm.model_returned")
add("endpoint", "https://soclaas-api.comp.nus.edu.sg/v1 (chat completions); one HTTP request per model call in code I2/I3", "runs/*/run.json base_url")
write_csv(PM / "tables/data_and_environment.csv", rows)
# per-run baselines and node classes
base = []
for r in runs():
    for d in r["dirs"][:1]:
        j = jload(d / "run.json", {}); m = j.get("meta", {})
        base.append({"run": r["id"], "node": j.get("hostname"), "baseline_ms_stock_decode": m.get("baseline_ms"), "null_ratio": m.get("null_ratio"), "null_p": m.get("null_p"), "null_ok": (j.get("null_evidence") or {}).get("null_ok", m.get("null_ok")),
                     "reference_cv": m.get("reference_cv"), "temperature": j.get("temperature"), "max_tokens": j.get("max_tokens"), "population": j.get("population"), "sample_seconds": j.get("sample_seconds"), "uniform_share": j.get("uniform_share")})
write_csv(PM / "tables/run_baselines_and_parameters.csv", base)
bm = [float(b["baseline_ms_stock_decode"]) for b in base if b["baseline_ms_stock_decode"]]
ac = []
for r in runs():
    for d in r["dirs"]:
        for x in jl(d / "results.jsonl"):
            if x.get("ok") and x.get("autocorr_lag1_median") is not None: ac.append(x["autocorr_lag1_median"])
json.dump({"baseline_ms_min": min(bm), "baseline_ms_max": max(bm), "baseline_ms_median": median(bm), "n_runs_with_baseline": len(bm),
           "search_measurements_autocorr_n": len(ac), "search_autocorr_median": median(ac), "search_autocorr_min": min(ac), "search_autocorr_max": max(ac)}, open(PM / "tables/environment_summary.json", "w"), indent=1)
if __name__ == "__main__":
    print(open(PM / "tables/environment_summary.json").read())
    print(collections.Counter((b["node"] or "")[:4] for b in base))
