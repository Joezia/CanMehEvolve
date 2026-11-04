#!/bin/bash
# C1 (compiler flags) and the C2/inert evaluations, all on ONE node, sequentially.
#   sbatch --partition=normal --constraint="xcnc|xcnd" --nodes=1 --ntasks=1 \
#          --cpus-per-task=24 --mem=0 --time=3:00:00 --job-name=canmeh-ctl \
#          --output=runs/slurm-%j.log --export=ALL,REPS=5 scripts/controls.sbatch
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
REPS=${REPS:-5}
JOB=${SLURM_JOB_ID:-manual$$}
OUT=$PWD/runs/controls-$JOB
mkdir -p "$OUT"
{ echo "host=$(hostname)"; echo "job=$JOB"; echo "start=$(date -Is)"; echo "cxx=$(c++ --version | head -1)";
  echo "commit=$(git rev-parse HEAD)"; echo "reps_per_comparison=$REPS";
  scontrol show job "$JOB" 2>/dev/null | tr ' ' '\n' | grep -E '^(Partition|Features|TimeLimit|NodeList|StartTime)=' ; } > "$OUT/node.txt"

# ---- C1: one work directory per compiler setting -------------------------
declare -A OPTS=( [O2]="-O2" [O3]="-O3" [O3native]="-O3 -march=native" )
for tag in O2 O3 O3native; do
  W=$PWD/build/work-c1-$JOB-$tag
  ./build/CanMehHarness --opt "${OPTS[$tag]}" init --work "$W" --repeat 10 > "$OUT/init-$tag.json" 2> "$OUT/init-$tag.stderr"
  cp "$W/meta.json" "$OUT/meta-$tag.json"
done
# Direct paired comparison: ref library = -O2 build, candidate = other flags,
# measured in the same process by CanMehBench through measure-pair.
for tag in O3 O3native; do
  P=$PWD/build/c1pair-$JOB-$tag
  mkdir -p "$P"
  cp "build/work-c1-$JOB-O2/meta.json" "$P/meta.json"
  cp "build/work-c1-$JOB-O2/libfit_ref.so" "$P/libfit_ref.so"
  cp "build/work-c1-$JOB-$tag/libfit_ref.so" "$P/libfit_cand.so"
  mkdir -p "$OUT/pair-$tag"
  for i in $(seq -w 1 "$REPS"); do
    ./build/CanMehHarness measure-pair --work "$P" --no-decision > "$OUT/pair-$tag/m$i.json" 2> "$OUT/pair-$tag/m$i.err"
  done
  ./build/CanMehSearch --rule-eval "$OUT"/pair-$tag/m*.json > "$OUT/rule-$tag-vs-O2.jsonl"
  rm -rf "$P"
done

# ---- C2 and inert patch: evaluated against the -O2 reference -----------------
W=$PWD/build/work-c1-$JOB-O2
for name in inert attempt-1 attempt-2; do
  case $name in
    inert) PATCH=$PWD/runs/inert-check/inert.patch;;
    *) PATCH=$PWD/runs/human-control/c2-1058781/$name.patch;;
  esac
  mkdir -p "$OUT/eval-$name"
  ./build/CanMehSearch --work "$W" --out "$OUT/eval-$name" --evaluate-patch "$PATCH" --evaluate-count "$REPS" \
      > "$OUT/eval-$name/console.log" 2>&1
done
cp "$W/scratch/bench.err" "$OUT/bench.err" 2>/dev/null
echo "end=$(date -Is)" >> "$OUT/node.txt"
for tag in O2 O3 O3native; do rm -rf "$PWD/build/work-c1-$JOB-$tag"; done
