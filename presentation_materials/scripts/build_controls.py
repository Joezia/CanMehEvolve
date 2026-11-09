#!/usr/bin/env python3
"""C1 (compiler flags) and C2 (human patches): per-measurement rule replay from the raw timings. ratio = candidate/reference (<1 = faster); speedup = 1/ratio;
time reduction % = 100*(1-ratio)."""
import sys, re; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pm_lib import *

C = ROOT / "runs/controls-1068897"; N = ROOT / "runs/controls-native-1071478"
comps = [
    ("C1", "-O3 vs stock -O2", "batch 1068897 (xcnd24)", C / "pair-O3", C, True),
    ("C1", "-O3 vs stock -O2", "batch 1071478 (xcnd24)", N / "pair-O3-vs-O2", N, True),
    ("C1", "-O3 -march=native vs stock -O2", "batch 1068897 (xcnd24)", C / "pair-O3native", C, False),
    ("C1", "-O3 -march=native vs stock -O2", "batch 1071478 (xcnd24)", N / "pair-O3native-vs-O2", N, True),
    ("C1", "-O3 -march=native vs -O3 (native's own increment)", "batch 1071478 (xcnd24)", N / "pair-O3native-vs-O3", N, True),
    ("C2", "human patch attempt 1 (fit_profile.cpp: GetMesg table) vs stock -O2", "batch 1068897 (xcnd24)", C / "eval-attempt-1/evaluate-attempt-1", C, True),
    ("C2", "human patch attempt 2 (GetMesg + GetFieldIndex tables) vs stock -O2", "batch 1068897 (xcnd24)", C / "eval-attempt-2/evaluate-attempt-2", C, True),
    ("inert", "inert patch (comment) vs stock -O2", "batch 1068897 (xcnd24)", C / "eval-inert/evaluate-inert", C, True),
]
rows, per = [], []
for ctl, name, batch, d, jobdir, valid in comps:
    res = []
    for f in sorted(d.glob("m*.json")):
        r = rule(jload(f))
        if r:
            res.append(r)
            per.append({"control": ctl, "comparison": name, "batch": batch, "measurement": f.name, "ratio": r["ratio"], "speedup": 1 / r["ratio"], "p": r["p"], "spread": r["spread"],
                        "passes_rule": r["faster"], "cand_ms": r["cand_ms"], "ref_ms": r["ref_ms"], "valid_comparison": valid})
    if not res:
        continue
    rat = [r["ratio"] for r in res]
    node = kv(jobdir / "node.txt")
    rows.append({"control": ctl, "comparison": name, "batch": batch, "node": node.get("host"), "job": node.get("job"), "n_measurements": len(res),
                 "median_ratio": median(rat), "median_speedup": 1 / median(rat), "speedup_min": 1 / max(rat), "speedup_max": 1 / min(rat),
                 "time_reduction_pct_median": 100 * (1 - median(rat)), "passes_rule": sum(1 for r in res if r["faster"]), "valid_comparison": valid,
                 "note": "" if valid else "INVALID: init of this batch failed for -march=native, ratios of exactly 1.0 are not a comparison",
                 "median_ref_ms": median([r["ref_ms"] for r in res]), "median_cand_ms": median([r["cand_ms"] for r in res])})
write_csv(PM / "tables/controls_summary.csv", rows)
write_csv(PM / "figure_data/controls_measurements.csv", per)
# C2 extra: facts about the human patches read from the actual patch files
hp = {}
for k in (1, 2):
    t = (ROOT / f"runs/human-control/c2-1058781/attempt-{k}.patch").read_text()
    hp[f"attempt-{k}"] = {"files": sorted(set(re.findall(r"^\+\+\+ b/(\S+)", t, re.M))), "hunks": len(re.findall(r"^@@", t, re.M)),
                         "added_lines": sum(1 for l in t.splitlines() if l.startswith("+") and not l.startswith("+++")),
                         "removed_lines": sum(1 for l in t.splitlines() if l.startswith("-") and not l.startswith("---"))}
sdk = (ROOT / "build/FITSDK-prefix/src/FITSDK/src/fit_profile.cpp").read_text()
m = re.search(r"const Profile::MESG Profile::mesgs\[MESGS\] =\s*\{(.*?)\n\};", sdk, re.S)
n_mesgs = len(re.findall(r"^\s*\{ \w+, \"", m.group(1), re.M)) if m else None
hp["MESGS_entries_in_fit_profile.cpp"] = n_mesgs
json.dump(hp, open(PM / "tables/human_patch_facts.json", "w"), indent=1)
src("c1-1", "C1 compiler-flag ratios/speedups", "runs/controls-1068897, runs/controls-native-1071478", "m*.json timings", "rule replay, median over 5 measurements")
src("c2-1", "C2 human patch results", "runs/controls-1068897/eval-attempt-*/evaluate-attempt-*/m*.json", "timings", "rule replay, 5 measurements; patch text in runs/human-control/c2-1058781/attempt-*.patch")
if __name__ == "__main__":
    for r in rows:
        print(f"{r['control']:5s} {r['comparison'][:62]:62s} {r['batch'][:20]:20s} n={r['n_measurements']} med speedup {r['median_speedup']:.4f} [{r['speedup_min']:.4f},{r['speedup_max']:.4f}] pass {r['passes_rule']}/{r['n_measurements']} {r['node']} ref {r['median_ref_ms']:.1f}ms")
    print(hp)
