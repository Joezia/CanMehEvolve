#!/usr/bin/env python3
"""List the patch variants used by the correctness follow-up: the 10 final patches of the runs and the cumulative states of the submitted seed-3 chain.
usage: make_variants.py OUT.json [human]   ("human": only the two human C2 patches, attempt-1 and attempt-2)"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent
if len(sys.argv) > 2 and sys.argv[2] == "human":
    hv = [{"name": "human-" + n, "patch": str(ROOT / "runs/human-control/c2-1058781" / (n + ".patch"))} for n in ("attempt-1", "attempt-2")]
    for x in hv:
        assert Path(x["patch"]).exists(), x
    Path(sys.argv[1]).write_text(json.dumps(hv, indent=1))
    print(len(hv), "variants (human)")
    sys.exit(0)
v = []
for p in sorted((ROOT / "experiments/patches/final-cumulative").glob("*.patch")):
    v.append({"name": "final-" + p.name.split(".")[0], "patch": str(p)})
run = [d for d in (ROOT / "runs/deepseek").glob("greedy-s3-*") if "resume" not in d.name][0]
ups = json.load(open(run / "summary.json"))["rank_updates"]
for i, u in enumerate(ups[:-1], 1):          # the last state equals final-greedy-seed3
    v.append({"name": "s3-step%02d-gen%d" % (i, u["generation"]), "patch": str(run / "patches" / ("gen_%d.patch" % u["generation"]))})
for x in v:
    assert Path(x["patch"]).exists(), x
Path(sys.argv[1]).write_text(json.dumps(v, indent=1))
print(len(v), "variants")
