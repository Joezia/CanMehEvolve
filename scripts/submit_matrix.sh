#!/bin/bash
# Submit the main matrix: search and best-of-N, seeds 1..5, equal API-call budget
# (GENS calls each). Four chains of jobs run at once (the model endpoint serves
# four requests at full speed); each job is a whole node, and a job starts only
# after the previous one in its chain has ended.
#   scripts/submit_matrix.sh [GENS] [TAG]
set -u
cd "$(dirname "$0")/.."
GENS=${1:-40}; TAG=${2:-main}
lane() {  # lane "mode:seed" ...
  local prev=""
  for spec in "$@"; do
    local mode=${spec%%:*} seed=${spec##*:}
    local dep=(); [ -n "$prev" ] && dep=(--dependency=afterany:$prev)
    prev=$(sbatch --parsable "${dep[@]}" --partition=normal --constraint="xcnc|xcnd" --nodes=1 --ntasks=1 \
        --cpus-per-task=24 --mem=0 --time=3:00:00 --job-name=canmeh-$mode-s$seed \
        --output=runs/slurm-%j.log --export=ALL,MODE=$mode,SEED=$seed,GENS=$GENS,TAG=$TAG scripts/run_search.sbatch)
    echo "$mode seed=$seed job=$prev"
  done
}
lane search:1 bestofn:1 search:5
lane bestofn:2 search:2 bestofn:5
lane search:3 bestofn:3
lane bestofn:4 search:4
