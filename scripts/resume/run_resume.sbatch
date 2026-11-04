#!/bin/bash
# Complete the seed-1 greedy run (39 of 40 HTTP attempts when its deadline hit) with the missing call(s).
# Replays the saved region draws (aborts before any call if they do not match), restores the best patch,
# makes only the missing HTTP attempt(s), then re-fixes the best patch and re-measures it 3 times.
#   sbatch --partition=normal --constraint="xcnc|xcnd" --nodes=1 --ntasks=1 --cpus-per-task=24 --mem=0 --time=1:30:00 \
#          --job-name=canmeh-ds-resume --output=runs/slurm-%j.log scripts/resume/run_resume.sbatch
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
FROM=$PWD/runs/deepseek/greedy-s1-1072019
JOB=${SLURM_JOB_ID:-manual$$}
W=$PWD/build/work-$JOB
OUT=$PWD/runs/deepseek/greedy-s1-1072019-resume-$JOB
mkdir -p "$OUT"
{ echo "host=$(hostname)"; echo "job=$JOB"; echo "start=$(date -Is)"; echo "resumed_from=$FROM";
  echo "binary_sha256=$(sha256sum build/CanMehSearch-resume | cut -d' ' -f1)";
  echo "resume_source_sha256=$(sha256sum scripts/resume/Search_resume.cpp | cut -d' ' -f1)"; } > "$OUT/node.txt"
./build/CanMehHarness init --work "$W" --repeat 10 > "$OUT/init.json" 2> "$OUT/init.stderr"
if [ "$(jq -r .null_ok "$OUT/init.json")" != true ]; then echo "null run dirty" | tee -a "$OUT/node.txt"; exit 1; fi
cp "$W/meta.json" "$OUT/meta.json"
./build/CanMehSearch-resume --work "$W" --out "$OUT" --mode greedy --seed 1 --generations 40 --resume-from "$FROM" \
    --init-json "$OUT/init.json" --llm-model deepseek-v4.1-flash --llm-expect-model deepseek-v4.1-flash-1017 \
    --llm-max-tokens 32768 --llm-timeout 600 --llm-http-attempts 1 --llm-api-key-file ~/.config/canmeh/api-key \
    > "$OUT/console.log" 2>&1
echo "search_exit=$?" >> "$OUT/node.txt"
BEST=$OUT/best.patch; [ -s "$BEST" ] || BEST=$FROM/best.patch
echo "fixed_best_patch=$BEST" >> "$OUT/node.txt"
./build/CanMehSearch-resume --work "$W" --out "$OUT" --evaluate-patch "$BEST" --evaluate-count 3 > "$OUT/final-evaluation.log" 2>&1
echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$W"
