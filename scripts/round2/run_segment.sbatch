#!/bin/bash
# Round 2: one SEGMENT of one search run. Self-managing chain: a run may need several segments (job time limit); when it is complete the segment submits the
# final-patch re-measurement job and the next run of the chain. Chains run in parallel, so at most (number of chains) LLM jobs run at once.
#   env: CHAIN (e.g. A), IDX (0-based line of runs/round2/chains/$CHAIN.txt), ATTEMPT (failed attempts so far)
# State lives in runs/round2/runs/<id>/ (state.json = checkpoint, segments/ = one record per segment). Nothing depends on a terminal being open.
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
CHAIN=${CHAIN:?}; IDX=${IDX:?}; ATTEMPT=${ATTEMPT:-0}
JOB=${SLURM_JOB_ID:-manual$$}
MANIFEST=runs/round2/chains/$CHAIN.txt
SPEC=$(sed -n "$((IDX + 1))p" "$MANIFEST")
[ -z "$SPEC" ] && { echo "chain $CHAIN finished at index $IDX"; exit 0; }
ID=$(jq -r .id <<< "$SPEC"); MKEY=$(jq -r .model_key <<< "$SPEC"); MODE=$(jq -r .mode <<< "$SPEC"); SEED=$(jq -r .seed <<< "$SPEC"); CLASS=$(jq -r .class <<< "$SPEC")
case $MKEY in
  ds)   MODEL=deepseek-v4.1-flash; EXPECT=deepseek-v4.1-flash-1017; MAXTOK=32768; TMO=600;;
  qwen) MODEL=qwen3-coder-next;    EXPECT=qwen3-coder-next;         MAXTOK=4096;  TMO=180;;
  *) echo "unknown model key $MKEY"; exit 2;;
esac
OUT=$PWD/runs/round2/runs/$ID
mkdir -p "$OUT/segments"
sub() {   # sub IDX_TO_RUN ATTEMPT [NODE]  -> submits a segment job for that chain index; the constraint comes from that run's own spec
  local i=$1 att=$2 node=${3:-} sp cls
  sp=$(sed -n "$((i + 1))p" "$MANIFEST"); [ -z "$sp" ] && return 0
  cls=$(jq -r .class <<< "$sp")
  sbatch --parsable --partition=normal --constraint="$cls" ${node:+--nodelist=$node} --nodes=1 --ntasks=1 --cpus-per-task=24 --mem=0 --time=3:00:00 \
         --job-name="r2-$CHAIN-$i" --output=runs/round2/slurm/%j.log --export=ALL,CHAIN=$CHAIN,IDX=$i,ATTEMPT=$att scripts/round2/run_segment.sbatch
}
advance() {   # the run is complete: final-patch re-measurement (independent job) and the next run of this chain, each submitted once
  if [ ! -e "$OUT/final_submitted" ]; then
    f=$(sbatch --parsable --partition=normal --constraint="$CLASS" --nodes=1 --ntasks=1 --cpus-per-task=24 --mem=0 --time=1:30:00 --job-name="r2-final-$ID" \
         --output=runs/round2/slurm/%j.log --export=ALL,ID=$ID scripts/round2/final_eval.sbatch) && echo "$f" > "$OUT/final_submitted"
  fi
  if [ ! -e "$OUT/next_submitted" ]; then n=$(sub $((IDX + 1)) 0) && echo "${n:-none}" > "$OUT/next_submitted"; fi
}
if [ -s "$OUT/summary.json" ]; then echo "$ID already complete" >> "$OUT/segments/$JOB.note"; advance; touch "$OUT/segments/$JOB.handoff"; exit 0; fi
# safety net: if this job ends without handing over (node failure, time-limit kill), the guard re-submits the same index
if [ "$ATTEMPT" -lt 6 ]; then
  sbatch --parsable --dependency=afterany:$JOB --partition=normal --nodes=1 --ntasks=1 --cpus-per-task=1 --mem=2G --time=0:10:00 --job-name="r2-guard-$CHAIN-$IDX" \
         --output=runs/round2/slurm/guard-%j.log --export=ALL,CHAIN=$CHAIN,IDX=$IDX,ATTEMPT=$((ATTEMPT + 1)),WATCH=$JOB,ID=$ID scripts/round2/chain_guard.sbatch > "$OUT/segments/$JOB.guard"
fi
W=$PWD/build/work-$JOB
{ echo "job=$JOB"; echo "host=$(hostname)"; echo "start=$(date -Is)"; echo "chain=$CHAIN idx=$IDX attempt=$ATTEMPT"; echo "run=$ID model=$MODEL expect=$EXPECT mode=$MODE seed=$SEED class=$CLASS";
  echo "git_commit=$(git rev-parse HEAD)"; echo "git_dirty_tracked=$(git status --porcelain --untracked-files=no | wc -l)";
  echo "search_cpp_sha256=$(sha256sum src/Search.cpp | cut -d' ' -f1)"; echo "binary_sha256=$(sha256sum build/CanMehSearch | cut -d' ' -f1)";
  echo "cxx=$(c++ --version | head -1)"; echo "cpu=$(lscpu | grep 'Model name' | sed 's/Model name: *//')"; } > "$OUT/segments/$JOB.node.txt"
./build/CanMehHarness init --work "$W" --repeat 10 > "$OUT/segments/$JOB.init.json" 2> "$OUT/segments/$JOB.init.stderr"
if [ "$(jq -r .null_ok "$OUT/segments/$JOB.init.json")" != true ]; then
  echo "null_ok false (attempt $ATTEMPT); not searching on this work directory" | tee -a "$OUT/segments/$JOB.node.txt"
  rm -rf "$W"
  n=$(sub "$IDX" $((ATTEMPT + 1))) ; echo "$n" > "$OUT/segments/$JOB.handoff"; exit 0     # same run again on another allocation
fi
cp "$W/meta.json" "$OUT/segments/$JOB.meta.json"; cp "$W/scratch/bench.err" "$OUT/segments/$JOB.bench.err" 2>/dev/null
RES=""; [ -s "$OUT/state.json" ] && RES="--resume"
./build/CanMehSearch --work "$W" --out "$OUT" --mode "$MODE" --seed "$SEED" --generations 40 --request-budget 40 --population 6 --sample-seconds 20 --uniform-share 0.1 \
    --exploit-share 0.25 --init-json "$OUT/segments/$JOB.init.json" --deadline-seconds 9300 --segment-label "job$JOB" $RES \
    --llm-model "$MODEL" --llm-expect-model "$EXPECT" --llm-max-tokens "$MAXTOK" --llm-timeout "$TMO" --llm-http-attempts 1 \
    --llm-api-key-file "$HOME/.config/canmeh/api-key" > "$OUT/segments/$JOB.console.log" 2>&1
RC=$?
echo "search_exit=$RC end=$(date -Is)" >> "$OUT/segments/$JOB.node.txt"
cp "$W/scratch/bench.err" "$OUT/bench.err" 2>/dev/null
rm -rf "$W"
if [ $RC -eq 0 ]; then advance
elif [ $RC -eq 75 ]; then c=$(sub "$IDX" 0); echo "continuation $c (any xcnc/xcnd node; population scores are re-measured if the host changes)" >> "$OUT/segments/$JOB.node.txt"
else
  echo "search failed with exit $RC (attempt $ATTEMPT)" >> "$OUT/segments/$JOB.node.txt"
  if [ "$ATTEMPT" -lt 3 ]; then sub "$IDX" $((ATTEMPT + 1)) > /dev/null; else echo "abandoned after $ATTEMPT failed attempts" > "$OUT/ABANDONED"; advance; fi
fi
touch "$OUT/segments/$JOB.handoff"
