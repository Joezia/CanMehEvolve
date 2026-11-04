#!/bin/bash
# Model preflight on real SDK functions: no measurement, only replies are examined.
# Tries each max_tokens level in order and stops at the first level where every probed
# function produced a usable (finish_reason=stop, non-empty, spliceable) reply.
#   sbatch --partition=normal --constraint="xcnc|xcnd" --nodes=1 --ntasks=1 --cpus-per-task=24 --mem=0 \
#          --time=1:00:00 --job-name=canmeh-pf --output=runs/slurm-%j.log \
#          --export=ALL,MODEL=deepseek-v4.1-flash,LEVELS="8192 16384 32768" scripts/preflight.sbatch
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
MODEL=${MODEL:-deepseek-v4.1-flash}; LEVELS=${LEVELS:-"8192 16384"}; TIMEOUT=${TIMEOUT:-600}
JOB=${SLURM_JOB_ID:-manual$$}
OUT=$PWD/runs/deepseek/preflight-$JOB; W=$PWD/build/work-pf-$JOB
mkdir -p "$OUT"
{ echo "host=$(hostname)"; echo "job=$JOB"; echo "start=$(date -Is)"; echo "model_requested=$MODEL"; echo "levels=$LEVELS timeout=$TIMEOUT";
  echo "commit=$(git rev-parse HEAD)"; echo "search_cpp_sha256=$(sha256sum src/Search.cpp | cut -d' ' -f1)";
  echo "binary_sha256=$(sha256sum build/CanMehSearch | cut -d' ' -f1)"; } > "$OUT/node.txt"
./build/CanMehHarness init --work "$W" --repeat 10 > "$OUT/init.json" 2> "$OUT/init.stderr"
[ "$(jq -r .null_ok "$OUT/init.json")" = true ] || { echo "null run dirty" >> "$OUT/node.txt"; exit 1; }
for MT in $LEVELS; do
  ./build/CanMehSearch --mode preflight --work "$W" --out "$OUT/mt$MT" --init-json "$OUT/init.json" \
      --llm-model "$MODEL" --llm-max-tokens "$MT" --llm-timeout "$TIMEOUT" --llm-http-attempts 1 \
      --llm-api-key-file ~/.config/canmeh/api-key > "$OUT/mt$MT.stdout" 2> "$OUT/mt$MT.stderr"
  echo "level=$MT exit=$?" >> "$OUT/node.txt"
  if [ "$(jq '[.entries[] | select(.usable_reply != true or .llm.finish_reason != "stop")] | length' "$OUT/mt$MT/preflight/preflight.json" 2>/dev/null)" = 0 ]; then
    echo "all_usable_at=$MT" >> "$OUT/node.txt"; break
  fi
done
echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$W"
