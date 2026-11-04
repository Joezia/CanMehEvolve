#!/bin/bash
# Phase 0 batch 2: top the six main calibration pairs up to TARGET (100) complete
# trials in total, then write the combined summary. Nothing in the rule or in the
# measurement settings differs from batch 1 (scripts/phase0.sbatch): same
# harness binary, `measure-pair --repeat 10 --repetitions 9 --no-decision`, the
# per-pair --min-time taken from batch 1's calibration.json, same pair order and
# same round-robin. Sweep pairs keep their original 20-trial plan (no new runs).
#   sbatch --partition=normal --constraint="xcnc|xcnd" --nodelist=xcnc2 --nodes=1 \
#          --ntasks=1 --cpus-per-task=24 --mem=0 --time=2:30:00 --signal=B:USR1@600 \
#          --dependency=afterany:<batch-1 job> --job-name=canmeh-p0b \
#          --output=runs/slurm-%j.log --export=ALL,B1=runs/phase0-<batch-1 job> \
#          scripts/phase0b.sbatch
# A second copy of this job may be queued as a fallback (job name canmeh-p0b-fb,
# later --begin). The first copy to start claims runs/phase0b-claim with an
# atomic mkdir and cancels the other if still pending; a copy that finds the
# claim exits at once, so two jobs never write the same measurement directory.
# Orderly exit: before every pair we check (a) `touch $OUT/STOP`, (b) the USR1
# warning Slurm sends 10 min before the limit, (c) a wall-clock guard; the
# rounds already finished are kept and the summary is still written.
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
JOB=${SLURM_JOB_ID:-manual$$}
B1=${B1:-$PWD/runs/phase0-1068829}
TARGET=${TARGET:-100}
WALL=${WALL:-9000}               # seconds this job may use (sbatch --time=2:30:00)
OUT=$PWD/runs/phase0b-$JOB
PAIRS="null faster-1-percent faster-2-percent faster-5-percent faster-10-percent slower-10-percent"
START=$(date +%s)

if ! mkdir "$PWD/runs/phase0b-claim" 2>/dev/null; then
  echo "batch 2 already claimed by $(cat "$PWD/runs/phase0b-claim/job" 2>/dev/null); job $JOB exits"; exit 0
fi
echo "$JOB" > "$PWD/runs/phase0b-claim/job"
for n in canmeh-p0b canmeh-p0b-fb; do
  scancel --user "$USER" --state=PENDING --name="$n" 2>/dev/null   # never touches running jobs
done
mkdir -p "$OUT/trials"
STOP_REQUESTED=0
trap 'STOP_REQUESTED=1; echo "USR1 at $(date -Is): finishing the current pair, then summarising" >> "$OUT/progress.log"' USR1

# Freeze the configuration; refuse to measure with anything that differs from batch 1.
cp "$B1/calibration.json" "$OUT/calibration_batch1.json"
if ! cmp -s build/calibration/calibration.json "$B1/calibration.json"; then
  echo "build/calibration/calibration.json differs from batch 1; refusing to measure" | tee "$OUT/ABORTED.txt"; exit 1
fi
scripts/phase0_env.sh "$B1/calibration.json" > "$OUT/config_frozen.txt" 2>&1
[ -s "$B1/config_frozen.txt" ] && diff <(grep -E '^(sha256|min_time|rule:|measurement:)' "$B1/config_frozen.txt" | grep -v 'phase0b.sbatch\|phase0_final.py\|phase0_env' ) \
                                       <(grep -E '^(sha256|min_time|rule:|measurement:)' "$OUT/config_frozen.txt" | grep -v 'phase0b.sbatch\|phase0_final.py\|phase0_env') > "$OUT/config_diff_vs_batch1.txt"
echo "config_diff_vs_batch1_lines=$(wc -l < "$OUT/config_diff_vs_batch1.txt" 2>/dev/null)" >> "$OUT/config_frozen.txt"
B1HOST=$(grep -m1 '^host=' "$B1/node.txt" | cut -d= -f2)
{ echo "batch1_host=$B1HOST"; echo "batch2_host=$(hostname)"; echo "same_node=$([ "$B1HOST" = "$(hostname)" ] && echo yes || echo NO)";
  echo "batch1_job=$(grep -m1 '^job=' "$B1/node.txt" | cut -d= -f2)"; echo "batch2_job=$JOB"; echo "start=$(date -Is)"; echo "target_per_pair=$TARGET";
  echo "binary sha256: $(sha256sum build/CanMehHarness | cut -d' ' -f1) build/CanMehHarness"; } > "$OUT/node.txt"

declare -A MT N F
for p in $PAIRS; do
  MT[$p]=$(jq -r --arg p "$p" '.pairs[] | select(.pair==$p) | .min_time' "$B1/calibration.json")
  # batch 1 contributes its complete trials (a half-written last file is not counted)
  N[$p]=$(./build/CanMehSearch --rule-eval "$B1"/trials/$p/t*.json 2>/dev/null | jq -s '[.[]|select(.valid)]|length')
  case "${N[$p]}" in ''|*[!0-9]*) echo "cannot count batch-1 trials for $p" | tee "$OUT/ABORTED.txt"; exit 1;; esac
  F[$p]=0
  mkdir -p "$OUT/trials/$p"
  echo "$p batch1_valid=${N[$p]} min_time=${MT[$p]}" >> "$OUT/node.txt"
done

round=0; last=120
while :; do
  todo=0; for p in $PAIRS; do [ "${N[$p]}" -lt "$TARGET" ] && todo=$((todo + 1)); done
  [ "$todo" -eq 0 ] && { echo "target reached" >> "$OUT/progress.log"; break; }
  round=$((round + 1)); r0=$(date +%s)
  for p in $PAIRS; do
    [ "${N[$p]}" -ge "$TARGET" ] && continue
    elapsed=$(( $(date +%s) - START ))
    if [ -e "$OUT/STOP" ] || [ "$STOP_REQUESTED" -eq 1 ] || [ $((elapsed + 2 * last)) -gt $((WALL - 600)) ]; then
      echo "orderly stop before $p (elapsed ${elapsed}s, stop_file=$([ -e "$OUT/STOP" ] && echo 1 || echo 0) usr1=$STOP_REQUESTED)" >> "$OUT/progress.log"
      break 2
    fi
    f=$(printf 't%03d' "$((${N[$p]} + ${F[$p]} + 1))")
    ./build/CanMehHarness measure-pair --work "build/calibration/$p" --repeat 10 --repetitions 9 \
        --min-time "${MT[$p]}" --no-decision > "$OUT/trials/$p/$f.json" 2> "$OUT/trials/$p/$f.err"
    rc=$?
    if jq -e '.ok == true and ((.timings.process | length) == 10)' "$OUT/trials/$p/$f.json" > /dev/null 2>&1; then
      N[$p]=$((${N[$p]} + 1)); status=valid
    else
      F[$p]=$((${F[$p]} + 1)); status=INVALID    # kept on disk, listed by phase0_final.py, not counted
      if [ "${F[$p]}" -ge 3 ]; then echo "$p: 3 invalid measurements, giving up on this pair" >> "$OUT/progress.log"; N[$p]=$TARGET; fi
    fi
    echo "$(date -Is) round=$round $p $f exit=$rc $status valid_total=${N[$p]}" >> "$OUT/progress.log"
  done
  last=$(( $(date +%s) - r0 )); date +%s > "$OUT/progress.txt"
done
echo "measure_end=$(date -Is)" >> "$OUT/node.txt"
for p in $PAIRS; do echo "$p final_index=${N[$p]}" >> "$OUT/node.txt"; done

# Combined summary (cheap, offline; reads only the saved timings).
python3 -I scripts/phase0_final.py --b1 "$B1" --b2 "$OUT" --out "$OUT/final" > "$OUT/final.stdout" 2> "$OUT/final.stderr"
echo "final_exit=$? end=$(date -Is)" >> "$OUT/node.txt"
