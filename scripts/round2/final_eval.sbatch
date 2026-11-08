#!/bin/bash
# Round 2: three independent re-measurements of the run's FIXED final patch (best.patch = best candidate confirmed during the search) under the frozen rule.
# A failed re-measurement is recorded as it is; there is no re-picking and no repeat-until-pass.
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
ID=${ID:?}
OUT=$PWD/runs/round2/runs/$ID/final
mkdir -p "$OUT"
JOB=${SLURM_JOB_ID:-manual$$}
{ echo "job=$JOB"; echo "host=$(hostname)"; echo "start=$(date -Is)"; echo "cpu=$(lscpu | grep 'Model name' | sed 's/Model name: *//')"; echo "binary_sha256=$(sha256sum build/CanMehSearch | cut -d' ' -f1)"; } > "$OUT/node.txt"
if [ ! -s "$PWD/runs/round2/runs/$ID/best.patch" ]; then echo "no confirmed patch in this run; nothing to re-measure" | tee "$OUT/NO_CONFIRMED_PATCH"; exit 0; fi
sha256sum "$PWD/runs/round2/runs/$ID/best.patch" >> "$OUT/node.txt"
W=$PWD/build/work-$JOB
./build/CanMehHarness init --work "$W" --repeat 10 > "$OUT/init.json" 2> "$OUT/init.stderr"
if [ "$(jq -r .null_ok "$OUT/init.json")" != true ]; then echo "null_ok false on this allocation; the final evaluation must be rerun (it is NOT counted as a failed re-measurement)" | tee "$OUT/NULL_DIRTY"; rm -rf "$W"; exit 1; fi
./build/CanMehSearch --work "$W" --out "$OUT" --evaluate-patch "$PWD/runs/round2/runs/$ID/best.patch" --evaluate-count 3 > "$OUT/final-evaluation.log" 2>&1
echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$W"
