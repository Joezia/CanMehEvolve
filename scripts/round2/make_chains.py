#!/usr/bin/env python3
"""Round 2 formal matrix -> chain manifests (one JSON line per run) and protocol.json.

Matrix: model {deepseek, qwen} x arm {population search (mode search), matched best-of-N (mode bestofn-confirmed)} x seeds 1-5 = 20 runs.
Four chains run in parallel (at most four LLM jobs at any time); each chain runs its runs one after another.
Nodes: any node of xcnc|xcnd (treated as equivalent by instruction); the actual host and CPU of every segment are recorded, and the node class is reported per run.
"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "runs/round2"
(OUT / "chains").mkdir(parents=True, exist_ok=True)
EST = {"ds": 2.9, "qwen": 2.0}          # hours per run, from earlier runs, used only to balance the chains
runs = []
for mk in ("ds", "qwen"):
    for seed in range(1, 6):
        pop_class = bo_class = "xcnc|xcnd"        # all nodes of both families are treated as equivalent (instruction of 2026-11-08); the real node is recorded per segment
        runs.append({"id": "%s-population-s%d" % (mk, seed), "model_key": mk, "mode": "search", "seed": seed, "class": pop_class})
        runs.append({"id": "%s-bestofn-s%d" % (mk, seed), "model_key": mk, "mode": "bestofn-confirmed", "seed": seed, "class": bo_class})
# Latin-square style assignment: every chain mixes models, arms and seeds, so no chain carries only one arm
ORDER = {"A": ["ds-population-s1", "ds-bestofn-s2", "qwen-population-s3", "qwen-bestofn-s4", "ds-population-s5"],
         "B": ["ds-bestofn-s1", "ds-population-s2", "qwen-bestofn-s3", "qwen-population-s4", "ds-bestofn-s5"],
         "C": ["ds-population-s3", "ds-bestofn-s4", "qwen-population-s1", "qwen-bestofn-s2", "qwen-population-s5"],
         "D": ["ds-bestofn-s3", "ds-population-s4", "qwen-bestofn-s1", "qwen-population-s2", "qwen-bestofn-s5"]}
byid = {r["id"]: r for r in runs}
assert sorted(i for v in ORDER.values() for i in v) == sorted(byid), "every run exactly once"
chains = {c: [byid[i] for i in ids] for c, ids in ORDER.items()}
load = {c: sum(EST[r["model_key"]] for r in rs) for c, rs in chains.items()}
for c, rs in chains.items():
    (OUT / "chains" / (c + ".txt")).write_text("".join(json.dumps(r) + "\n" for r in rs))
    print(c, [r["id"] + ":" + r["class"] for r in rs], "est %.1f h" % load[c])
protocol = {
    "round": 2, "purpose": "README-conformant population search and matched best-of-N, DeepSeek and Qwen, five seeds each, 40 actual HTTP requests per run",
    "models": {"ds": {"requested": "deepseek-v4.1-flash", "expected_returned_id": "deepseek-v4.1-flash-1017", "max_tokens": 32768, "timeout_s": 600},
               "qwen": {"requested": "qwen3-coder-next", "expected_returned_id": "qwen3-coder-next", "max_tokens": 4096, "timeout_s": 180}},
    "common": {"temperature": 0.8, "http_attempts_per_call": 1, "request_budget": 40, "population": 6, "sample_seconds": 20, "uniform_share": 0.1,
               "exploit_share_population_only": 0.25, "repeat": 10, "repetitions": 9, "alpha": 0.01, "min_effect": 0.02, "segment_deadline_s": 9300,
               "region_draws": "profile-proportional (perf, 20 s) with 10% uniform; population arm additionally sends 25% of draws to the best-credited region; best-of-N uses no history"},
    "arms": {"search": "population of 6 (every measured candidate retained, worst evicted), tournament of two, cumulative child patches, one failure-feedback retry for compile/correctness-type failures",
             "bestofn-confirmed": "every call starts from stock, no history, no failure feedback; candidates judged by the same confirmation rule as the population arm"},
    "confirmation": "best_confirmed = best candidate for which two measurements each pass the frozen rule against stock (ratio <= 0.98, sign-flip p < 0.01, not unstable); not required to improve on its parent by 2%",
    "final_check": "best.patch fixed at the end of the search, then 3 independent re-measurements in a separate job; failures recorded, no re-picking",
    "runs": runs, "chains": {c: [r["id"] for r in rs] for c, rs in chains.items()},
}
(OUT / "protocol.json").write_text(json.dumps(protocol, indent=1) + "\n")
