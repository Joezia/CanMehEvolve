#!/bin/bash
# Follow-up 1: complete a greedy run that stopped at its job-limit deadline to 40 HTTP requests (like seed 1 was).
# Replays the saved region draws (aborts before any call if they do not match), restores the saved best patch, sends only the missing requests,
# then re-fixes the best patch and re-measures it 3 times. Output goes to runs/followup/ (the frozen runs/deepseek/ is not touched).
#   sbatch --partition=normal --constraint="xcnd" --nodes=1 --ntasks=1 --cpus-per-task=24 --mem=0 --time=1:30:00 \
#          --export=ALL,SEED=3,FROM=runs/deepseek/greedy-s3-1072869 scripts/followup/run_resume.sbatch
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
SEED=${SEED:?}; FROM=$(realpath "${FROM:?}")
JOB=${SLURM_JOB_ID:-manual$$}
W=$PWD/build/work-$JOB
OUT=$PWD/runs/followup/resume-greedy-s$SEED-$JOB
mkdir -p "$OUT"
{ echo "host=$(hostname)"; echo "job=$JOB"; echo "start=$(date -Is)"; echo "resumed_from=$FROM"; echo "seed=$SEED";
  echo "binary_sha256=$(sha256sum build/CanMehSearch-resume | cut -d' ' -f1)";
  echo "resume_source_sha256=$(sha256sum scripts/resume/Search_resume.cpp | cut -d' ' -f1)"; } > "$OUT/node.txt"
./build/CanMehHarness init --work "$W" --repeat 10 > "$OUT/init.json" 2> "$OUT/init.stderr"
if [ "$(jq -r .null_ok "$OUT/init.json")" != true ]; then echo "null run dirty" | tee -a "$OUT/node.txt"; exit 1; fi
cp "$W/meta.json" "$OUT/meta.json"; cp "$W/scratch/bench.err" "$OUT/bench.err" 2>/dev/null
./build/CanMehSearch-resume --work "$W" --out "$OUT" --mode greedy --seed "$SEED" --generations 40 --resume-from "$FROM" \
    --init-json "$OUT/init.json" --llm-model deepseek-v4.1-flash --llm-expect-model deepseek-v4.1-flash-1017 \
    --llm-max-tokens 32768 --llm-timeout 600 --llm-http-attempts 1 --llm-api-key-file ~/.config/canmeh/api-key \
    > "$OUT/console.log" 2>&1
echo "search_exit=$?" >> "$OUT/node.txt"
BEST=$OUT/best.patch; [ -s "$BEST" ] || BEST=$FROM/best.patch
echo "fixed_best_patch=$BEST" >> "$OUT/node.txt"
./build/CanMehSearch-resume --work "$W" --out "$OUT" --evaluate-patch "$BEST" --evaluate-count 3 > "$OUT/final-evaluation.log" 2>&1
echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$W"
