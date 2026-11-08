#!/bin/bash
# Round-2 pre-check (billed separately, not part of any formal result): population search with a tiny budget, interrupted by a deadline and resumed,
# so that population, parent patches, failure feedback, request budget, logs and checkpoint/resume are exercised with the real harness and model.
#   sbatch --partition=normal --constraint="xcnd" --nodes=1 --ntasks=1 --cpus-per-task=24 --mem=0 --time=1:30:00 \
#          --export=ALL,MODEL=deepseek-v4.1-flash,EXPECT=deepseek-v4.1-flash-1017,MAXTOK=32768,TMO=600,BUDGET=10,DEADLINE1=900,SEED=7,MODE=search scripts/round2/preflight_search.sbatch
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
MODEL=${MODEL:?}; EXPECT=${EXPECT:?}; MAXTOK=${MAXTOK:?}; TMO=${TMO:-600}; BUDGET=${BUDGET:-10}; DEADLINE1=${DEADLINE1:-900}; SEED=${SEED:-7}; MODE=${MODE:-search}
JOB=${SLURM_JOB_ID:-manual$$}
W=$PWD/build/work-$JOB
OUT=$PWD/runs/round2/preflight/$MODE-$MODEL-s$SEED-$JOB
mkdir -p "$OUT"
{ echo "host=$(hostname)"; echo "job=$JOB"; echo "start=$(date -Is)"; echo "mode=$MODE model=$MODEL budget=$BUDGET deadline_segment1=$DEADLINE1";
  echo "binary_sha256=$(sha256sum build/CanMehSearch | cut -d' ' -f1)"; } > "$OUT/node.txt"
./build/CanMehHarness init --work "$W" --repeat 10 > "$OUT/init.json" 2> "$OUT/init.stderr"
if [ "$(jq -r .null_ok "$OUT/init.json")" != true ]; then echo "null run dirty" | tee -a "$OUT/node.txt"; exit 1; fi
cp "$W/meta.json" "$OUT/meta.json"
ARGS="--work $W --out $OUT --mode $MODE --seed $SEED --generations $BUDGET --request-budget $BUDGET --sample-seconds 20 --init-json $OUT/init.json --llm-model $MODEL --llm-expect-model $EXPECT --llm-max-tokens $MAXTOK --llm-timeout $TMO --llm-http-attempts 1 --llm-api-key-file $HOME/.config/canmeh/api-key"
./build/CanMehSearch $ARGS --deadline-seconds "$DEADLINE1" --segment-label seg1 > "$OUT/console-seg1.log" 2>&1
echo "seg1_exit=$?" >> "$OUT/node.txt"
./build/CanMehSearch $ARGS --resume --deadline-seconds 6000 --segment-label seg2 > "$OUT/console-seg2.log" 2>&1
echo "seg2_exit=$?" >> "$OUT/node.txt"
echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$W"
