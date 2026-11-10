#!/bin/bash
# Max-lines-600 one-shot experiment (separate record: runs/maxlines600/). One DeepSeek modification of Decode::ReadByte (>250 lines, so
# invisible to the --max-lines 250 default) on top of the best DeepSeek patch of the round-2 formal runs (ds-population-s3).
# The search stops after the first candidate that COMPILES AND IS MEASURED; compile/link/other failures are fed back and retried, up to the request cap.
# Then the seed patch and the new patch are each re-measured 3 times in the SAME job (same node) against the original SDK (-O2 build).
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
JOB=${SLURM_JOB_ID:-manual$$}
EXP=$PWD/runs/maxlines600
OUT=$EXP/run-$JOB
SEED_PATCH=$PWD/runs/round2/runs/ds-population-s3/best.patch
BIN=$PWD/build/CanMehSearch-maxlines600
LABEL=${LABEL:-Decode::ReadByte}
MAXLINES=${MAXLINES:-600}
CAP=${CAP:-8}
mkdir -p "$OUT"
{ echo "job=$JOB"; echo "host=$(hostname)"; echo "start=$(date -Is)"; echo "cpu=$(lscpu | grep 'Model name' | sed 's/Model name: *//')";
  echo "git_commit=$(git rev-parse HEAD)"; echo "git_dirty_tracked=$(git status --porcelain --untracked-files=no | wc -l)";
  echo "variant_source_sha256=$(sha256sum scripts/maxlines600/Search_maxlines600.cpp | cut -d' ' -f1)"; echo "binary_sha256=$(sha256sum "$BIN" | cut -d' ' -f1)";
  echo "seed_patch=$SEED_PATCH"; echo "seed_patch_sha256=$(sha256sum "$SEED_PATCH" | cut -d' ' -f1)";
  echo "max_lines=$MAXLINES force_label=$LABEL request_cap=$CAP"; echo "cxx=$(c++ --version | head -1)"; } > "$OUT/node.txt"
W=$PWD/build/work-$JOB
./build/CanMehHarness init --work "$W" --repeat 10 > "$OUT/init.json" 2> "$OUT/init.stderr"
if [ "$(jq -r .null_ok "$OUT/init.json")" != true ]; then echo "null_ok false on this allocation; nothing was run (no model request sent)" | tee "$OUT/NULL_DIRTY"; rm -rf "$W"; exit 1; fi
cp "$W/meta.json" "$OUT/meta.json"
"$BIN" --work "$W" --out "$OUT/search" --mode search --seed 1 --generations "$CAP" --request-budget "$CAP" --population 6 --sample-seconds 20 --uniform-share 0.1 \
    --exploit-share 0 --init-json "$OUT/init.json" --deadline-seconds 7000 --max-lines "$MAXLINES" --force-label "$LABEL" --seed-patch "$SEED_PATCH" --stop-after-measured 1 \
    --llm-model deepseek-v4.1-flash --llm-expect-model deepseek-v4.1-flash-1017 --llm-max-tokens 32768 --llm-timeout 600 --llm-http-attempts 1 \
    --llm-api-key-file "$HOME/.config/canmeh/api-key" > "$OUT/search.console.log" 2>&1
echo "search_exit=$? search_end=$(date -Is)" >> "$OUT/node.txt"
CHILD=$(jq -r 'select(.ok==true) | .patch' "$OUT/search/results.jsonl" 2>/dev/null | head -1)
if [ -n "$CHILD" ] && [ -s "$CHILD" ]; then
  echo "child_patch=$CHILD" >> "$OUT/node.txt"; sha256sum "$CHILD" >> "$OUT/node.txt"
  "$BIN" --work "$W" --out "$OUT/eval-seed"  --evaluate-patch "$SEED_PATCH" --evaluate-count 3 > "$OUT/eval-seed.log" 2>&1
  "$BIN" --work "$W" --out "$OUT/eval-child" --evaluate-patch "$CHILD"      --evaluate-count 3 > "$OUT/eval-child.log" 2>&1
else
  echo "no candidate was compiled and measured within the request cap" | tee "$OUT/NO_MEASURED_CANDIDATE"
fi
echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$W"
