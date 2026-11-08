#!/bin/bash
# Round 2 (top-up of the follow-up measurement): false-accept rate of the FROZEN decision rule on the real SDK decode. An inert (no-op) patch has a true ratio of 1.000, so every measurement
# that the rule calls "faster" is a false accept. Same instrument as the formal runs: init (null check) then CanMehSearch --evaluate-patch with N measurements
# (10 processes x 9 repetitions, SDK min-time), one node, nothing else on it.
#   sbatch --partition=normal --constraint="xcnd" --nodes=1 --ntasks=1 --cpus-per-task=24 --mem=0 --time=3:00:00 \
#          --export=ALL,N=60,LABEL=xcnd-a scripts/followup/sdk_inert_fpr.sbatch
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
N=${N:-60}; LABEL=${LABEL:-x}
JOB=${SLURM_JOB_ID:-manual$$}
W=$PWD/build/work-$JOB
OUT=$PWD/runs/round2/fpr/sdk-inert-$LABEL-$JOB
mkdir -p "$OUT"
{ echo "host=$(hostname)"; echo "job=$JOB"; echo "start=$(date -Is)"; echo "n=$N"; echo "patch=runs/inert-check/inert.patch";
  echo "patch_sha256=$(sha256sum runs/inert-check/inert.patch | cut -d' ' -f1)"; echo "binary_sha256=$(sha256sum build/CanMehSearch | cut -d' ' -f1)"; } > "$OUT/node.txt"
./build/CanMehHarness init --work "$W" --repeat 10 > "$OUT/init.json" 2> "$OUT/init.stderr"
if [ "$(jq -r .null_ok "$OUT/init.json")" != true ]; then echo "null run dirty" | tee -a "$OUT/node.txt"; exit 1; fi
cp "$W/meta.json" "$OUT/meta.json"; cp "$W/scratch/bench.err" "$OUT/bench.err" 2>/dev/null
./build/CanMehSearch --work "$W" --out "$OUT" --evaluate-patch "$PWD/runs/inert-check/inert.patch" --evaluate-count "$N" > "$OUT/evaluation.log" 2>&1
echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$W"
