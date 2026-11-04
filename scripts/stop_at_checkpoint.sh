#!/bin/bash
# Orderly stop of Phase 0 batch 1: cancel the job exactly when round N has
# finished for every pair (progress.txt is written right after the last pair of
# a round), so no completed trial is lost and at most the first measurement of
# round N+1 is left half-written. If the job is already past round N when this
# starts, the checkpoint moves to the round that is current.
#   scripts/stop_at_checkpoint.sh <jobid> <phase0 dir> <N>
set -u
JOB=$1; DIR=$2; N=$3
LAST=slower-10-percent          # last pair of every round in phase0.sbatch
LOG=$DIR/checkpoint_stop.txt
cur=$(ls "$DIR/trials/$LAST"/t*.json 2>/dev/null | wc -l)
[ "$cur" -gt "$N" ] && N=$cur
target=$(printf '%s/trials/%s/t%03d.json' "$DIR" "$LAST" "$N")
echo "watching job $JOB for round $N ($target); started $(date -Is)" > "$LOG"
i=0
while :; do
  if [ -f "$target" ] && [ "$(stat -c %.9Y "$DIR/progress.txt" | tr -d .)" -ge "$(stat -c %.9Y "$target" | tr -d .)" ]; then
    out=$(scancel "$JOB" 2>&1)
    {
      echo "round $N complete for every pair; scancel $JOB at $(date -Is) ($out)"
      for p in null faster-1-percent faster-2-percent faster-5-percent faster-10-percent slower-10-percent; do
        echo "$p files_at_stop=$(ls "$DIR/trials/$p"/t*.json | wc -l)"
      done
      echo "A t$(printf %03d $((N + 1))) file for the first pair may be half-written; it is an interrupted measurement and is listed as such by phase0_final.py."
    } >> "$LOG"
    exit 0
  fi
  i=$((i + 1))
  if [ $((i % 40)) -eq 0 ] && ! squeue -h -j "$JOB" 2>/dev/null | grep -q .; then
    echo "job $JOB ended on its own before round $N at $(date -Is)" >> "$LOG"; exit 0
  fi
  sleep 0.25
done
