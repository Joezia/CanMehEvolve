#!/bin/bash
# Round 2: more trials of the SYNTHETIC null calibration pair, same instrument and settings as Phase 0 (measure-pair --repeat 10 --repetitions 9 --no-decision,
# the pair's own recorded --min-time), on one node class, one node, nothing else on it. Each trial is judged by the frozen rule afterwards (CanMehSearch --rule-eval).
# Works on a private copy of build/calibration/null so that no two jobs ever write the same calibration directory.
#   sbatch --partition=normal --constraint="xcnc" --nodes=1 --ntasks=1 --cpus-per-task=24 --mem=0 --time=3:00:00 --nice=100 \
#          --export=ALL,N=200,LABEL=xcnc-a scripts/round2/null_trials.sbatch
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
N=${N:-200}; LABEL=${LABEL:-x}; WALL=${WALL:-9600}
JOB=${SLURM_JOB_ID:-manual$$}
OUT=$PWD/runs/round2/fpr/null-$LABEL-$JOB
mkdir -p "$OUT/trials"
START=$(date +%s)
MT=$(jq -r '.pairs[] | select(.pair=="null") | .min_time' runs/phase0-1068829/calibration.json)
{ echo "host=$(hostname)"; echo "job=$JOB"; echo "start=$(date -Is)"; echo "cpu=$(lscpu | grep 'Model name' | sed 's/Model name: *//')"; echo "target_trials=$N min_time=$MT";
  echo "harness_sha256=$(sha256sum build/CanMehHarness | cut -d' ' -f1)"; echo "search_binary_sha256=$(sha256sum build/CanMehSearch | cut -d' ' -f1)";
  echo "calibration_json_sha256=$(sha256sum build/calibration/calibration.json | cut -d' ' -f1)"; echo "phase0_calibration_json_sha256=$(sha256sum runs/phase0-1068829/calibration.json | cut -d' ' -f1)"; } > "$OUT/node.txt"
W=$HOME/.null-trials-$JOB
rm -rf "$W"; cp -r build/calibration/null "$W"
for i in $(seq 1 "$N"); do
  if [ $(( $(date +%s) - START )) -gt "$WALL" ]; then echo "wall guard reached after $((i - 1)) trials" >> "$OUT/node.txt"; break; fi
  f=$(printf 't%03d' "$i")
  ./build/CanMehHarness measure-pair --work "$W" --repeat 10 --repetitions 9 --min-time "$MT" --no-decision > "$OUT/trials/$f.json" 2> "$OUT/trials/$f.err"
  echo "$f exit=$?" >> "$OUT/progress.log"
done
./build/CanMehSearch --rule-eval "$OUT"/trials/t*.json > "$OUT/rule_rows.jsonl" 2> "$OUT/rule_eval.stderr"
echo "valid=$(jq -s '[.[]|select(.valid)]|length' "$OUT/rule_rows.jsonl") faster=$(jq -s '[.[]|select(.valid and .faster)]|length' "$OUT/rule_rows.jsonl")" >> "$OUT/node.txt"
echo "end=$(date -Is)" >> "$OUT/node.txt"
rm -rf "$W"
