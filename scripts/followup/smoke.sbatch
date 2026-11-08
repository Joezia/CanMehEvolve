#!/bin/bash
# Smoke test of the follow-up tools at tiny scale (corpus of 16 files, 2 variants, stack K=1). Not part of the results.
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
JOB=${SLURM_JOB_ID:-manual$$}
W=$PWD/build/work-$JOB; C=$HOME/.corpus-$JOB; OUT=$PWD/runs/followup/smoke-$JOB
mkdir -p "$OUT"
./build/CanMehHarness init --work "$W" --repeat 10 > "$OUT/init.json" 2> "$OUT/init.stderr"
python3 scripts/followup/gen_corpus.py "$C" --per-file 3 --seed 1 > "$OUT/corpus.log" 2>&1
python3 scripts/followup/make_variants.py "$OUT/all_variants.json" > /dev/null
python3 - <<P
import json
v=json.load(open("$OUT/all_variants.json"))
keep=[x for x in v if x["name"] in ("final-bestofn-seed4","final-greedy-seed5")]
json.dump(keep,open("$OUT/variants.json","w"))
P
python3 scripts/followup/fuzz_diff.py --work "$W" --corpus "$C" --out "$OUT/fuzz" --variants "$OUT/variants.json" > "$OUT/fuzz.log" 2>&1
echo "fuzz_exit=$?" >> "$OUT/fuzz.log"
python3 scripts/followup/sanitize.py --corpus "$C" --variants "$OUT/variants.json" --out "$OUT/san" --jobs 12 > "$OUT/san.log" 2>&1
echo "san_exit=$?" >> "$OUT/san.log"
rm -rf "$W" "$C"
