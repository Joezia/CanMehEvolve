#!/bin/bash
# Round 2: machine-code check of the no-op candidates (see verify_noop.py). No model, no timing of interest.
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
JOB=${SLURM_JOB_ID:-manual$$}
OUT=$PWD/runs/round2/fpr/noop-verification-$JOB
W=$PWD/build/work-$JOB
mkdir -p "$OUT"
{ echo "host=$(hostname)"; echo "job=$JOB"; echo "start=$(date -Is)"; } > "$OUT/node.txt"
./build/CanMehHarness init --work "$W" --repeat 10 > "$OUT/init.json" 2> "$OUT/init.stderr"
python3 scripts/round2/verify_noop.py --work "$W" --out "$OUT" > "$OUT/console.log" 2>&1
echo "exit=$?" >> "$OUT/node.txt"; echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$W"
