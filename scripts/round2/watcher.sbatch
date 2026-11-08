#!/bin/bash
# Round 2 watcher: persistent, resubmits itself every 20 minutes until all 20 runs are finished (re-measurement done or no confirmed patch, or abandoned),
# then submits the post-processing jobs once (extended correctness checks, then the aggregation). Nothing depends on a terminal.
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
TICK=${TICK:-0}
done_n=0; total=0
for spec in runs/round2/chains/[A-D].txt; do
  while read -r line; do
    [ -z "$line" ] && continue
    id=$(jq -r .id <<< "$line"); total=$((total + 1)); d=runs/round2/runs/$id
    if [ -s "$d/final/evaluate-best/summary.json" ] || [ -e "$d/final/NO_CONFIRMED_PATCH" ] || [ -e "$d/ABANDONED" ]; then done_n=$((done_n + 1)); fi
  done < "$spec"
done
echo "$(date -Is) tick $TICK: $done_n of $total runs finished" >> runs/round2/watcher.log
# health check: a chain with no job in the queue and unfinished runs is restarted at its first unfinished run (a segment normally submits its successor itself)
if [ "$done_n" -lt "$total" ]; then
  queued=$(squeue -u "$USER" -h -o "%j")
  for c in A B C D; do
    if ! grep -q "^r2-$c-" <<< "$queued"; then
      i=0; n=0; found=-1
      while read -r line; do
        [ -z "$line" ] && continue
        id=$(jq -r .id <<< "$line"); d=runs/round2/runs/$id
        if [ "$found" -lt 0 ] && [ ! -s "$d/summary.json" ] && [ ! -e "$d/ABANDONED" ]; then found=$i; fi
        i=$((i + 1))
      done < runs/round2/chains/$c.txt
      if [ "$found" -ge 0 ]; then
        j=$(sbatch --parsable --partition=normal --constraint="xcnc|xcnd" --nodes=1 --ntasks=1 --cpus-per-task=24 --mem=0 --time=3:00:00 --job-name="r2-$c-$found" \
              --output=runs/round2/slurm/%j.log --export=ALL,CHAIN=$c,IDX=$found,ATTEMPT=0 scripts/round2/run_segment.sbatch)
        echo "$(date -Is) health check: chain $c had no job; restarted index $found as job $j" >> runs/round2/watcher.log
      fi
    fi
  done
fi
if [ "$done_n" -ge "$total" ] && [ ! -e runs/round2/post_submitted ]; then
  touch runs/round2/post_submitted
  ids=""
  for part in DIFF0 DIFF1 SAN; do
    j=$(sbatch --parsable --partition=normal --nodes=1 --ntasks=1 --cpus-per-task=12 --mem=32G --time=3:00:00 --job-name=r2-corr-$part --output=runs/round2/slurm/%j.log --export=ALL,PART=$part scripts/round2/correctness_round2.sbatch)
    ids="$ids:$j"; echo "post: correctness $part job $j" >> runs/round2/watcher.log
  done
  a=$(sbatch --parsable --dependency=afterany$ids --partition=normal --nodes=1 --ntasks=1 --cpus-per-task=1 --mem=4G --time=0:30:00 --job-name=r2-aggregate --output=runs/round2/slurm/%j.log --wrap="cd $PWD && python3 scripts/round2/aggregate_round2.py > runs/round2/aggregate.stdout 2>&1")
  echo "post: aggregation job $a" >> runs/round2/watcher.log
  exit 0
fi
[ "$done_n" -lt "$total" ] && [ "$TICK" -lt 160 ] && sbatch --parsable --begin=now+20minutes --partition=normal --nodes=1 --ntasks=1 --cpus-per-task=1 --mem=1G --time=0:05:00 --job-name=r2-watcher \
    --output=runs/round2/slurm/watcher-%j.log --export=ALL,TICK=$((TICK + 1)) scripts/round2/watcher.sbatch > /dev/null
exit 0
