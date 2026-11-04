#!/bin/bash
# One full search (MODE=search) or best-of-N control (MODE=bestofn) as one job.
#   sbatch --partition=normal --constraint="xcnc|xcnd" --nodes=1 --ntasks=1 \
#          --cpus-per-task=24 --mem=0 --time=3:00:00 --job-name=canmeh-$MODE \
#          --output=runs/slurm-%j.log \
#          --export=ALL,MODE=search,SEED=1,GENS=40,TAG=main scripts/run_search.sbatch
# Extra CanMehSearch flags can be passed in EXTRA. No secret is written anywhere.
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
MODE=${MODE:?}; SEED=${SEED:?}; GENS=${GENS:-40}; TAG=${TAG:-main}
DEADLINE=${DEADLINE:-8400}   # seconds after which no new generation starts
EXTRA=${EXTRA:-}
JOB=${SLURM_JOB_ID:-manual$$}
W=$PWD/build/work-$JOB
OUT=$PWD/runs/$TAG/$MODE-s$SEED-$JOB
mkdir -p "$OUT"
{ echo "host=$(hostname)"; echo "job=$JOB"; echo "nodelist=${SLURM_JOB_NODELIST:-}";
  echo "start=$(date -Is)"; echo "cxx=$(c++ --version | head -1)";
  echo "commit=$(git rev-parse HEAD)"; echo "mode=$MODE seed=$SEED gens=$GENS deadline=$DEADLINE";
  scontrol show job "$JOB" 2>/dev/null | tr ' ' '\n' | grep -E '^(Partition|Features|TimeLimit|NodeList|StartTime)=' ; } > "$OUT/node.txt"
./build/CanMehHarness init --work "$W" --repeat 10 > "$OUT/init.json" 2> "$OUT/init.stderr"
if [ "$(jq -r .null_ok "$OUT/init.json")" != true ]; then echo "null run dirty" | tee -a "$OUT/node.txt"; exit 1; fi
cp "$W/meta.json" "$OUT/meta.json"; cp "$W/scratch/bench.err" "$OUT/bench.err" 2>/dev/null
./build/CanMehSearch --work "$W" --out "$OUT" --mode "$MODE" --seed "$SEED" --generations "$GENS" \
    --sample-seconds 20 --init-json "$OUT/init.json" --deadline-seconds "$DEADLINE" \
    --llm-api-key-file ~/.config/canmeh/api-key $EXTRA > "$OUT/console.log" 2>&1
echo "search_exit=$?" >> "$OUT/node.txt"
# Independent re-measurement of the best confirmed patch, in the same work dir
# and on the same node, after the search has stopped selecting on it.
if [ -s "$OUT/best.patch" ]; then
  ./build/CanMehSearch --work "$W" --out "$OUT" --evaluate-patch "$OUT/best.patch" --evaluate-count 3 \
      > "$OUT/final-evaluation.log" 2>&1
fi
echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$W"
