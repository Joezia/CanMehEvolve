#!/bin/bash
# Follow-up 4b job: stock and patch variants under AddressSanitizer+UBSan (single thread) and ThreadSanitizer (4 threads). See sanitize.py. No model call, no timing.
#   sbatch --partition=normal --nodes=1 --ntasks=1 --cpus-per-task=24 --mem=0 --time=3:00:00 scripts/followup/correctness_sanitize.sbatch
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
JOB=${SLURM_JOB_ID:-manual$$}
C=$HOME/.corpus-$JOB
OUT=$PWD/runs/followup/correctness-sanitize-${SET:+$SET-}$JOB
mkdir -p "$OUT"
{ echo "host=$(hostname)"; echo "job=$JOB"; echo "start=$(date -Is)"; echo "gcc=$(g++ --version | head -1)"; } > "$OUT/node.txt"
python3 scripts/followup/gen_corpus.py "$C" --per-file 100 --seed 1 > "$OUT/corpus.log" 2>&1
cp "$C/index.json" "$OUT/corpus_index.json"
python3 scripts/followup/make_variants.py "$OUT/variants.json" ${SET:-} > "$OUT/variants.log"
python3 scripts/followup/sanitize.py --corpus "$C" --variants "$OUT/variants.json" --out "$OUT" --jobs 12 > "$OUT/console.log" 2>&1
echo "sanitize_exit=$?" >> "$OUT/node.txt"
echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$C"
