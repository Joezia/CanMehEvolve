"""Registry of every search run used in the comparison: configuration, seed, directories (original + resume directories of the same chain), final directory."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pm_lib import *

# implementation (code) versions -- experimental conditions, not a timeline
IMPL = {
    "I1": "population search + best-of-N with the two-measurement confirmation rule; provided HTTP client (up to 3 hidden retries per call); budget = 40 model calls (archive/qwen-experiment/Search.cpp, sha256 ce80cd7b...)",
    "I2": "rank-rule heuristic: greedy single chain / best-of-N, one HTTP request per call (no hidden retry), budget = 40 HTTP requests, deadline per job (src/Search.cpp at d5aa9e7, sha256 67935a2f...)",
    "I3": "README loop: population <= 6 + tournament + failure feedback + region credit, or matched best-of-N (confirmation rule); budget = 40 HTTP requests exactly, checkpoint/resume (src/Search.cpp at 527c5d0, sha256 9431cd44...)",
}
CONFIGS = [
    # id, label, algorithm, model, impl
    ("qwen_pop_I1", "Qwen3-coder-next, population search", "population", "qwen3-coder-next", "I1"),
    ("qwen_bon_I1", "Qwen3-coder-next, best-of-N", "best-of-N", "qwen3-coder-next", "I1"),
    ("qwen_pop_I3", "Qwen3-coder-next, population search", "population", "qwen3-coder-next", "I3"),
    ("qwen_bon_I3", "Qwen3-coder-next, best-of-N", "best-of-N", "qwen3-coder-next", "I3"),
    ("ds_greedy_I2", "DeepSeek-v4.1-flash, greedy single chain", "greedy", "deepseek-v4.1-flash-1017", "I2"),
    ("ds_bon_I2", "DeepSeek-v4.1-flash, best-of-N (rank rule)", "best-of-N", "deepseek-v4.1-flash-1017", "I2"),
    ("ds_pop_I3", "DeepSeek-v4.1-flash, population search", "population", "deepseek-v4.1-flash-1017", "I3"),
    ("ds_bon_I3", "DeepSeek-v4.1-flash, best-of-N (confirmation rule)", "best-of-N", "deepseek-v4.1-flash-1017", "I3"),
]
CFG = {c[0]: c for c in CONFIGS}


def one(pattern):
    m = sorted(ROOT.glob(pattern))
    return m[0] if m else None


def runs():
    out = []
    for s in range(1, 6):
        out.append({"cfg": "qwen_pop_I1", "seed": s, "dirs": [one(f"runs/main/search-s{s}-*")]})
        out.append({"cfg": "qwen_bon_I1", "seed": s, "dirs": [one(f"runs/main/bestofn-s{s}-*")]})
        out.append({"cfg": "qwen_pop_I3", "seed": s, "dirs": [one(f"runs/round2/runs/qwen-population-s{s}")]})
        out.append({"cfg": "qwen_bon_I3", "seed": s, "dirs": [one(f"runs/round2/runs/qwen-bestofn-s{s}")]})
        g = one(f"runs/deepseek/greedy-s{s}-[0-9]*")
        res = sorted(ROOT.glob(f"runs/deepseek/greedy-s{s}-*-resume-*")) + sorted(ROOT.glob(f"runs/followup/resume-greedy-s{s}-*"))
        out.append({"cfg": "ds_greedy_I2", "seed": s, "dirs": [g] + res})
        out.append({"cfg": "ds_bon_I2", "seed": s, "dirs": [one(f"runs/deepseek/bestofn-s{s}-*")]})
        out.append({"cfg": "ds_pop_I3", "seed": s, "dirs": [one(f"runs/round2/runs/ds-population-s{s}")]})
        out.append({"cfg": "ds_bon_I3", "seed": s, "dirs": [one(f"runs/round2/runs/ds-bestofn-s{s}")]})
    for r in out:
        r["final_dir"] = r["dirs"][-1]
        r["id"] = f"{r['cfg']}_s{r['seed']}"
    return out
