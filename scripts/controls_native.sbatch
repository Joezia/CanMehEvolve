#!/bin/bash
# C1 re-run for `-O3 -march=native` (the first attempt in controls.sbatch failed because
# `--opt "-O3 -march=native"` reaches gcc as a single argument). Everything is rebuilt on
# the one allocated node, and -O3 is re-measured in the same job so the three settings
# share a node and a time window.
#   sbatch --partition=normal --constraint="xcnc|xcnd" --nodelist=xcnd24 --nodes=1 --ntasks=1 \
#          --cpus-per-task=24 --mem=0 --time=1:30:00 --job-name=canmeh-c1n \
#          --output=runs/slurm-%j.log --export=ALL,REPS=5 scripts/controls_native.sbatch
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
REPS=${REPS:-5}
JOB=${SLURM_JOB_ID:-manual$$}
OUT=$PWD/runs/controls-native-$JOB
WRAP=$PWD/scripts/cxx-march-native.sh
mkdir -p "$OUT"
{ echo "host=$(hostname)"; echo "job=$JOB"; echo "start=$(date -Is)"; echo "cxx=$(c++ --version | head -1)";
  echo "commit=$(git rev-parse HEAD)"; echo "reps_per_comparison=$REPS";
  echo "wrapper_sha256=$(sha256sum "$WRAP" | cut -d' ' -f1)";
  echo "march_native_resolves_to=$(c++ -march=native -Q --help=target 2>/dev/null | awk '$1=="-march="{print $2}')";
  scontrol show job "$JOB" 2>/dev/null | tr ' ' '\n' | grep -E '^(Partition|Features|TimeLimit|NodeList|StartTime)=' ; } > "$OUT/node.txt"

W2=$PWD/build/work-c1n-$JOB-O2; W3=$PWD/build/work-c1n-$JOB-O3; WN=$PWD/build/work-c1n-$JOB-O3native
./build/CanMehHarness --opt -O2 init --work "$W2" --repeat 10 > "$OUT/init-O2.json" 2> "$OUT/init-O2.stderr"
./build/CanMehHarness --opt -O3 init --work "$W3" --repeat 10 > "$OUT/init-O3.json" 2> "$OUT/init-O3.stderr"
./build/CanMehHarness --cxx "$WRAP" --opt -O3 init --work "$WN" --repeat 10 > "$OUT/init-O3native.json" 2> "$OUT/init-O3native.stderr"
for t in O2:$W2 O3:$W3 O3native:$WN; do cp "${t#*:}/meta.json" "$OUT/meta-${t%%:*}.json" 2>/dev/null; done

# pair NAME REFERENCE_WORKDIR CANDIDATE_WORKDIR: libfit_ref.so of each work dir, timed in one process by measure-pair.
pair() {
  local name=$1 ref=$2 cand=$3 P=$PWD/build/c1npair-$JOB-$1
  mkdir -p "$P" "$OUT/pair-$name"
  cp "$ref/meta.json" "$P/meta.json"; cp "$ref/libfit_ref.so" "$P/libfit_ref.so"; cp "$cand/libfit_ref.so" "$P/libfit_cand.so"
  for i in $(seq -w 1 "$REPS"); do
    ./build/CanMehHarness measure-pair --work "$P" --no-decision > "$OUT/pair-$name/m$i.json" 2> "$OUT/pair-$name/m$i.err"
  done
  ./build/CanMehSearch --rule-eval "$OUT"/pair-$name/m*.json > "$OUT/rule-$name.jsonl"
  rm -rf "$P"
}
pair O3native-vs-O2 "$W2" "$WN"
pair O3-vs-O2 "$W2" "$W3"
pair O3native-vs-O3 "$W3" "$WN"      # extra: what -march=native adds on top of -O3
echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$W2" "$W3" "$WN"
