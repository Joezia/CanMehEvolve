#!/usr/bin/env python3
"""Follow-up 6 (attribution control): what if best-of-N could STACK its single-function candidates?

Best-of-N keeps only the single best candidate, so its result is one function's rewrite. Greedy accumulates edits across functions. To separate
"greedy found better rewrites" from "greedy simply keeps and adds independent wins", this script takes the SAME candidates a best-of-N run produced
(no new model call): per function (region label) the candidate with the lowest search-time ratio below 1.0, ordered by that ratio, and builds cumulative
patches of the top 1, 2, 3, ... candidates (a candidate that does not apply cleanly on top of the stack is skipped and logged). Each stack is built and
measured by the frozen instrument (`CanMehSearch --evaluate-patch`, 3 independent measurements; the harness also applies its correctness checks).
usage: stack_bestofn.py --run-dir runs/deepseek/bestofn-sN-... --work W --out OUT [--kmax 12]
"""
import argparse, json, os, shutil, subprocess, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--run-dir", required=True)
ap.add_argument("--work", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--kmax", type=int, default=12)
ap.add_argument("--search", default="build/CanMehSearch")
ap.add_argument("--stock-src", default="build/FITSDK-prefix/src/FITSDK/src")
ap.add_argument("--scratch", default=str(Path.home() / ".stack-scratch"))
a = ap.parse_args()
OUT = Path(a.out)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "stacks").mkdir(exist_ok=True)
env = dict(os.environ, GIT_AUTHOR_NAME="s", GIT_AUTHOR_EMAIL="s@x", GIT_COMMITTER_NAME="s", GIT_COMMITTER_EMAIL="s@x")


def git(repo, *args, check=True):
    return subprocess.run(["git", "-C", str(repo), *args], env=env, capture_output=True, text=True, check=check)


rows = [json.loads(l) for l in open(Path(a.run_dir) / "results.jsonl") if l.strip()]
cands = {}
for r in rows:
    if r.get("ok") and r.get("patch") and r.get("ratio") is not None and r["ratio"] < 1.0:
        lab = r["label"]
        if lab not in cands or r["ratio"] < cands[lab]["ratio"]:
            cands[lab] = r
order = sorted(cands.values(), key=lambda r: r["ratio"])
(OUT / "candidates.json").write_text(json.dumps([{"label": r["label"], "generation": r["generation"], "ratio": r["ratio"], "speedup": 1 / r["ratio"],
                                                  "rule_pass_1": r.get("rule_pass_1"), "rule_pass_2": r.get("rule_pass_2"), "patch": r["patch"]} for r in order], indent=1) + "\n")
print("candidates (best per function, ratio < 1):", len(order), flush=True)

repo = Path(a.scratch) / ("stack-" + Path(a.run_dir).name)
shutil.rmtree(repo, ignore_errors=True)
repo.mkdir(parents=True)
shutil.copytree(a.stock_src, repo / "src")
git(repo, "init", "-q"); git(repo, "add", "-A"); git(repo, "commit", "-qm", "stock")

accepted, skipped, results = [], [], []
for r in order:
    if len(accepted) >= a.kmax:
        break
    p = subprocess.run(["git", "-C", str(repo), "apply", r["patch"]], env=env, capture_output=True, text=True)
    if p.returncode:
        skipped.append({"label": r["label"], "generation": r["generation"], "reason": p.stderr[:200]})
        print("skip", r["label"], flush=True)
        continue
    git(repo, "add", "-A")
    accepted.append(r)
    k = len(accepted)
    diff = git(repo, "diff", "--cached", "--no-color").stdout
    patch = OUT / "stacks" / ("stack_%02d.patch" % k)
    patch.write_text(diff)
    sub = OUT / ("eval-%02d" % k)
    log = subprocess.run([a.search, "--work", a.work, "--out", str(sub), "--evaluate-patch", str(patch), "--evaluate-count", "3"], capture_output=True, text=True)
    summ_path = sub / ("evaluate-stack_%02d" % k) / "summary.json"
    s = json.load(open(summ_path)) if summ_path.exists() else {}
    entry = {"k": k, "added": r["label"], "added_generation": r["generation"], "added_individual_speedup": 1 / r["ratio"], "functions": [x["label"] for x in accepted],
             "valid_measurements": s.get("valid_measurements"), "passes": s.get("measurements_passing_rule"), "median_speedup": s.get("median_speedup"),
             "ratios": [m["analysis"]["ratio"] for m in s.get("measurements", []) if m["analysis"].get("valid")],
             "stages": [m.get("stage") for m in s.get("measurements", [])], "errors": [m.get("error") for m in s.get("measurements", []) if m.get("error")][:1]}
    results.append(entry)
    (OUT / "stack_results.json").write_text(json.dumps({"run_dir": a.run_dir, "results": results, "skipped": skipped}, indent=1) + "\n")
    print("K=%d +%s -> median speedup %s (valid %s, pass %s)" % (k, r["label"], entry["median_speedup"], entry["valid_measurements"], entry["passes"]), flush=True)
    if not s.get("valid_measurements"):
        print("stack failed at the harness (e.g. compile or correctness); stopping", flush=True)
        break
shutil.rmtree(repo, ignore_errors=True)
print("done")
