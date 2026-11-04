#!/bin/bash
# Phase 0: calibrate the decision rule on the 12 calibration pairs.
#   sbatch --partition=normal --constraint="xcnc|xcnd" --nodes=1 --ntasks=1 \
#          --cpus-per-task=24 --mem=0 --time=3:00:00 --job-name=canmeh-p0 \
#          --output=runs/slurm-%j.log --export=ALL,TRIALS=60 scripts/phase0.sbatch
# Everything runs sequentially on the one allocated node; nothing else may run
# on it. The rule is FIXED before this job (alpha=0.01, min_effect=0.02, 10
# processes), so every trial below is evaluation data, not tuning data.
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
TRIALS=${TRIALS:-100}
SWEEP_TRIALS=${SWEEP_TRIALS:-20}
OUT=$PWD/runs/phase0-${SLURM_JOB_ID:-manual}
mkdir -p "$OUT/trials"
{ echo "host=$(hostname)"; echo "job=${SLURM_JOB_ID:-}"; echo "nodelist=${SLURM_JOB_NODELIST:-}";
  echo "start=$(date -Is)"; echo "cxx=$(c++ --version | head -1)";
  echo "commit=$(git rev-parse HEAD)"; echo "trials_per_pair=$TRIALS";
  scontrol show job "${SLURM_JOB_ID:-0}" 2>/dev/null | tr ' ' '\n' | grep -E '^(Partition|Features|TimeLimit|NodeList|StartTime)=' ; } > "$OUT/node.txt"
./build/CanMehCalibrate --repeat 10 > "$OUT/calibrate.txt" 2> "$OUT/calibrate.stderr"
echo "calibrate_exit=$?" >> "$OUT/node.txt"
cp build/calibration/calibration.json "$OUT/calibration.json"
PAIRS="null faster-1-percent faster-2-percent faster-5-percent faster-10-percent slower-10-percent"
SWEEPS="sweep-105 sweep-110 sweep-200 sweep-400"
declare -A MT
for p in $PAIRS $SWEEPS; do MT[$p]=$(jq -r --arg p "$p" '.pairs[] | select(.pair==$p) | .min_time' "$OUT/calibration.json"); mkdir -p "$OUT/trials/$p"; done
# Round-robin over pairs so slow drift in the node hits every arm equally.
for i in $(seq -w 1 "$TRIALS"); do
  for p in $PAIRS; do
    ./build/CanMehHarness measure-pair --work "build/calibration/$p" --repeat 10 --repetitions 9 \
        --min-time "${MT[$p]}" --no-decision > "$OUT/trials/$p/t$i.json" 2> "$OUT/trials/$p/t$i.err"
  done
  if [ "$((10#$i))" -le "$SWEEP_TRIALS" ]; then
    for p in $SWEEPS; do
      ./build/CanMehHarness measure-pair --work "build/calibration/$p" --repeat 10 --repetitions 9 \
          --min-time "${MT[$p]}" --no-decision > "$OUT/trials/$p/t$i.json" 2> "$OUT/trials/$p/t$i.err"
    done
  fi
  date +%s > "$OUT/progress.txt"
done
for p in $PAIRS $SWEEPS; do
  ./build/CanMehSearch --rule-eval "$OUT"/trials/$p/t*.json > "$OUT/rule-$p.jsonl"
done
echo "end=$(date -Is)" >> "$OUT/node.txt"
