#!/bin/bash
# Round 2: classify how the stock SDK handles every corpus file (the 177 files that the stock decoder does not decode are kept and classified, not discarded).
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
JOB=${SLURM_JOB_ID:-manual$$}
OUT=$PWD/runs/round2/correctness/stock-classification-$JOB
C=$HOME/.corpus-cls-$JOB
mkdir -p "$OUT"
{ echo "host=$(hostname)"; echo "job=$JOB"; echo "start=$(date -Is)"; } > "$OUT/node.txt"
scripts/round2/build_corpus.sh "$C" 60 > "$OUT/corpus.log" 2>&1
cp "$C/index.json" "$OUT/"
python3 scripts/round2/classify_stock.py --corpus "$C" --out "$OUT" --jobs 12 > "$OUT/console.log" 2>&1
echo "exit=$?" >> "$OUT/node.txt"; echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$C"
