#!/bin/bash
# Follow-up 6 job: stack best-of-N's own single-function candidates (see stack_bestofn.py). No model call.
#   sbatch --partition=normal --constraint="xcnd" --nodes=1 --ntasks=1 --cpus-per-task=24 --mem=0 --time=3:00:00 \
#          --export=ALL,SEED=1,RUN=runs/deepseek/bestofn-s1-1072020 scripts/followup/stack_bestofn.sbatch
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
SEED=${SEED:?}; RUN=$(realpath "${RUN:?}"); KMAX=${KMAX:-12}
JOB=${SLURM_JOB_ID:-manual$$}
W=$PWD/build/work-$JOB
OUT=$PWD/runs/followup/stack-bestofn-s$SEED-$JOB
mkdir -p "$OUT"
{ echo "host=$(hostname)"; echo "job=$JOB"; echo "start=$(date -Is)"; echo "source_run=$RUN"; echo "kmax=$KMAX";
  echo "binary_sha256=$(sha256sum build/CanMehSearch | cut -d' ' -f1)"; } > "$OUT/node.txt"
./build/CanMehHarness init --work "$W" --repeat 10 > "$OUT/init.json" 2> "$OUT/init.stderr"
if [ "$(jq -r .null_ok "$OUT/init.json")" != true ]; then echo "null run dirty" | tee -a "$OUT/node.txt"; exit 1; fi
cp "$W/meta.json" "$OUT/meta.json"
python3 scripts/followup/stack_bestofn.py --run-dir "$RUN" --work "$W" --out "$OUT" --kmax "$KMAX" > "$OUT/console.log" 2>&1
echo "stack_exit=$?" >> "$OUT/node.txt"
echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$W"
