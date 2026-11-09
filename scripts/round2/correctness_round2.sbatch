#!/bin/bash
# Round 2 extended correctness checks (NOT admission rules of the searches): legal encoder-written files + mutants, differential test vs the stock library, plain
# classification of how every file is handled, ASan/UBSan and TSan, for the round-2 final patches and the best-of-N stacks. Parts: DIFF0, DIFF1 (differential shards) or SAN.
#   sbatch ... --export=ALL,PART=DIFF0|DIFF1|SAN scripts/round2/correctness_round2.sbatch
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
PART=${PART:?}
JOB=${SLURM_JOB_ID:-manual$$}
OUT=$PWD/runs/round2/correctness/$PART-$JOB
C=$HOME/.corpus-r2-$JOB
mkdir -p "$OUT"
{ echo "host=$(hostname)"; echo "job=$JOB"; echo "start=$(date -Is)"; echo "part=$PART"; echo "gcc=$(g++ --version | head -1)"; echo "git_commit=$(git rev-parse HEAD)"; } > "$OUT/node.txt"
scripts/round2/build_corpus.sh "$C" 60 > "$OUT/corpus.log" 2>&1
cp "$C/index.json" "$C/valid_generation_"* "$OUT/" 2>/dev/null
python3 scripts/followup/make_variants.py "$OUT/variants.json" round2 > "$OUT/variants.log"
case $PART in
  DIFF0|DIFF1)
    W=$PWD/build/work-$JOB
    ./build/CanMehHarness init --work "$W" --repeat 10 > "$OUT/init.json" 2> "$OUT/init.stderr"
    SH=0/2; [ "$PART" = DIFF1 ] && SH=1/2
    python3 scripts/followup/fuzz_diff.py --work "$W" --corpus "$C" --out "$OUT" --variants "$OUT/variants.json" --shard "$SH" > "$OUT/console.log" 2>&1
    rm -rf "$W";;
  SAN)
    python3 scripts/round2/sanitize_v2.py --corpus "$C" --variants "$OUT/variants.json" --out "$OUT" --jobs 12 ${CONFIGS:+--configs $CONFIGS} > "$OUT/console.log" 2>&1;;
esac
echo "exit=$?" >> "$OUT/node.txt"; echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$C"
