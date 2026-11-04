#!/bin/bash
# Post-hoc common-budget analysis: three independent re-measurements of the best-ranked patch as of the
# 34th HTTP request, for runs whose best at request 34 differs from their final best. No model calls.
#   sbatch --partition=normal --constraint="xcnc|xcnd" --nodes=1 --ntasks=1 --cpus-per-task=24 --mem=0 --time=1:00:00 \
#          --export=ALL,PATCH=/abs/gen_N.patch,NAME=greedy-s2-gen33 scripts/common34_remeasure.sbatch
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
PATCH=${PATCH:?}; NAME=${NAME:?}
JOB=${SLURM_JOB_ID:-manual$$}
W=$PWD/build/work-$JOB
OUT=$PWD/runs/deepseek-common34/$NAME-$JOB
mkdir -p "$OUT"
{ echo "host=$(hostname)"; echo "job=$JOB"; echo "start=$(date -Is)"; echo "patch=$PATCH";
  echo "patch_sha256=$(sha256sum "$PATCH" | cut -d' ' -f1)"; echo "binary_sha256=$(sha256sum build/CanMehSearch | cut -d' ' -f1)"; } > "$OUT/node.txt"
./build/CanMehHarness init --work "$W" --repeat 10 > "$OUT/init.json" 2> "$OUT/init.stderr"
if [ "$(jq -r .null_ok "$OUT/init.json")" != true ]; then echo "null run dirty" | tee -a "$OUT/node.txt"; exit 1; fi
cp "$W/meta.json" "$OUT/meta.json"
./build/CanMehSearch --work "$W" --out "$OUT" --evaluate-patch "$PATCH" --evaluate-count 3 > "$OUT/final-evaluation.log" 2>&1
echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$W"
