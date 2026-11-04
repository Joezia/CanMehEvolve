#!/bin/bash
# DeepSeek experiment: one greedy chain (MODE=greedy) or one best-of-N control (MODE=bestofn)
# as one job. Both arms use the same model, max_tokens, timeout, region sampling, rank rule
# and call budget; they differ only in where each call starts from.
#   sbatch --partition=normal --constraint="xcnc|xcnd" --nodes=1 --ntasks=1 --cpus-per-task=24 --mem=0 \
#          --time=3:00:00 --job-name=canmeh-ds-$MODE --output=runs/slurm-%j.log \
#          --export=ALL,MODE=greedy,SEED=1,GENS=40,MAXTOK=32768 scripts/run_deepseek.sbatch
# No secret is written anywhere.
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
MODE=${MODE:?}; SEED=${SEED:?}; GENS=${GENS:-40}; MAXTOK=${MAXTOK:?}
MODEL=${MODEL:-deepseek-v4.1-flash}; EXPECT=${EXPECT:-deepseek-v4.1-flash-1017}
TIMEOUT=${TIMEOUT:-600}; DEADLINE=${DEADLINE:-9600}; TAG=${TAG:-deepseek}
JOB=${SLURM_JOB_ID:-manual$$}
W=$PWD/build/work-$JOB
OUT=$PWD/runs/$TAG/$MODE-s$SEED-$JOB
mkdir -p "$OUT"
{ echo "host=$(hostname)"; echo "job=$JOB"; echo "nodelist=${SLURM_JOB_NODELIST:-}";
  echo "start=$(date -Is)"; echo "cxx=$(c++ --version | head -1)";
  echo "commit=$(git rev-parse HEAD)"; echo "mode=$MODE seed=$SEED gens=$GENS deadline=$DEADLINE";
  echo "model=$MODEL expect=$EXPECT max_tokens=$MAXTOK timeout=$TIMEOUT";
  echo "search_cpp_sha256=$(sha256sum src/Search.cpp | cut -d' ' -f1)";
  echo "binary_sha256=$(sha256sum build/CanMehSearch | cut -d' ' -f1)";
  scontrol show job "$JOB" 2>/dev/null | tr ' ' '\n' | grep -E '^(Partition|Features|TimeLimit|NodeList|StartTime)=' ; } > "$OUT/node.txt"
./build/CanMehHarness init --work "$W" --repeat 10 > "$OUT/init.json" 2> "$OUT/init.stderr"
if [ "$(jq -r .null_ok "$OUT/init.json")" != true ]; then echo "null run dirty" | tee -a "$OUT/node.txt"; exit 1; fi
cp "$W/meta.json" "$OUT/meta.json"; cp "$W/scratch/bench.err" "$OUT/bench.err" 2>/dev/null
./build/CanMehSearch --work "$W" --out "$OUT" --mode "$MODE" --seed "$SEED" --generations "$GENS" \
    --sample-seconds 20 --init-json "$OUT/init.json" --deadline-seconds "$DEADLINE" \
    --llm-model "$MODEL" --llm-expect-model "$EXPECT" --llm-max-tokens "$MAXTOK" --llm-timeout "$TIMEOUT" \
    --llm-http-attempts 1 --llm-api-key-file ~/.config/canmeh/api-key > "$OUT/console.log" 2>&1
echo "search_exit=$?" >> "$OUT/node.txt"
# Three independent re-measurements of the FIXED final patch under the calibrated rule
# (alpha 0.01, at least 2% cumulative reduction). Reported as they come out.
if [ -s "$OUT/best.patch" ]; then
  ./build/CanMehSearch --work "$W" --out "$OUT" --evaluate-patch "$OUT/best.patch" --evaluate-count 3 \
      > "$OUT/final-evaluation.log" 2>&1
fi
echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$W"
# Refresh the cross-seed summary (reads every finished run; harmless if it fails).
[ -f scripts/aggregate_deepseek.py ] && python3 scripts/aggregate_deepseek.py > "$OUT/aggregate.log" 2>&1 || true
