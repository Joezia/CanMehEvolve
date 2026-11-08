#!/bin/bash
# Follow-up 4a job: differential test (patched vs stock library) on a corpus of mutated FIT files. See fuzz_diff.py. No model call.
#   sbatch --partition=normal --constraint="xcnd|xcnc" --nodes=1 --ntasks=1 --cpus-per-task=24 --mem=0 --time=3:00:00 \
#          --export=ALL,SHARD=0/2,PERFILE=100 scripts/followup/correctness_diff.sbatch
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
SHARD=${SHARD:-0/1}; PERFILE=${PERFILE:-100}
JOB=${SLURM_JOB_ID:-manual$$}
W=$PWD/build/work-$JOB
C=$HOME/.corpus-$JOB
OUT=$PWD/runs/followup/correctness-diff-${SET:+$SET-}${SHARD/\//of}-$JOB
mkdir -p "$OUT"
{ echo "host=$(hostname)"; echo "job=$JOB"; echo "start=$(date -Is)"; echo "shard=$SHARD per_file=$PERFILE corpus_seed=1";
  echo "binary_sha256=$(sha256sum build/CanMehHarness | cut -d' ' -f1)"; } > "$OUT/node.txt"
./build/CanMehHarness init --work "$W" --repeat 10 > "$OUT/init.json" 2> "$OUT/init.stderr"
if [ "$(jq -r .null_ok "$OUT/init.json")" != true ]; then echo "null run dirty" | tee -a "$OUT/node.txt"; exit 1; fi
python3 scripts/followup/gen_corpus.py "$C" --per-file "$PERFILE" --seed 1 > "$OUT/corpus.log" 2>&1
cp "$C/index.json" "$OUT/corpus_index.json"
python3 scripts/followup/make_variants.py "$OUT/variants.json" ${SET:-} > "$OUT/variants.log"
python3 scripts/followup/fuzz_diff.py --work "$W" --corpus "$C" --out "$OUT" --variants "$OUT/variants.json" --shard "$SHARD" > "$OUT/console.log" 2>&1
echo "fuzz_exit=$?" >> "$OUT/node.txt"
echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$W" "$C"
