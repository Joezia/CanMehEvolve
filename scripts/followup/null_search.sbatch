#!/bin/bash
# Follow-up 3 job: null search (greedy rank rule on no-op candidates). See null_search.py.
#   sbatch --partition=normal --constraint="xcnd" --nodes=1 --ntasks=1 --cpus-per-task=24 --mem=0 --time=3:00:00 \
#          --export=ALL,SEED=1,STEPS=40,LABEL=xcnd scripts/followup/null_search.sbatch
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
SEED=${SEED:?}; STEPS=${STEPS:-40}; LABEL=${LABEL:-x}
JOB=${SLURM_JOB_ID:-manual$$}
W=$PWD/build/work-$JOB
OUT=$PWD/runs/followup/null-search-$LABEL-s$SEED-$JOB
mkdir -p "$OUT"
{ echo "host=$(hostname)"; echo "job=$JOB"; echo "start=$(date -Is)"; echo "seed=$SEED steps=$STEPS";
  echo "binary_sha256=$(sha256sum build/CanMehSearch | cut -d' ' -f1)"; echo "script_sha256=$(sha256sum scripts/followup/null_search.py | cut -d' ' -f1)"; } > "$OUT/node.txt"
./build/CanMehHarness init --work "$W" --repeat 10 > "$OUT/init.json" 2> "$OUT/init.stderr"
if [ "$(jq -r .null_ok "$OUT/init.json")" != true ]; then echo "null run dirty" | tee -a "$OUT/node.txt"; exit 1; fi
cp "$W/meta.json" "$OUT/meta.json"
python3 scripts/followup/null_search.py --work "$W" --out "$OUT" --seed "$SEED" --steps "$STEPS" --deadline 9300 > "$OUT/console.log" 2>&1
echo "search_exit=$?" >> "$OUT/node.txt"
echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$W"
