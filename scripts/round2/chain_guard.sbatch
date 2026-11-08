#!/bin/bash
# Safety net for a chain segment: runs after the segment job ended. If the segment did not hand over (no .handoff file: node failure, time-limit kill),
# submit the same chain index again (the segment script then resumes from state.json, or advances if the run turned out to be complete).
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
OUT=runs/round2/runs/$ID
if [ -e "$OUT/segments/$WATCH.handoff" ]; then echo "segment $WATCH handed over"; exit 0; fi
echo "segment $WATCH ended without handing over; resubmitting index $IDX (attempt $ATTEMPT)" | tee -a "$OUT/segments/$WATCH.node.txt"
MANIFEST=runs/round2/chains/$CHAIN.txt
cls=$(jq -r .class <<< "$(sed -n "$((IDX + 1))p" "$MANIFEST")")
sbatch --parsable --partition=normal --constraint="$cls" --nodes=1 --ntasks=1 --cpus-per-task=24 --mem=0 --time=3:00:00 --job-name="r2-$CHAIN-$IDX" \
       --output=runs/round2/slurm/%j.log --export=ALL,CHAIN=$CHAIN,IDX=$IDX,ATTEMPT=$ATTEMPT scripts/round2/run_segment.sbatch
