#!/bin/bash
# Print the frozen Phase 0 configuration: rule parameters, measurement settings,
# per-pair min_time, binary/script/calibration-library hashes and host facts.
# Used at the batch-1 checkpoint and again at the start of batch 2 so the two
# records can be diffed. Prints to stdout; never touches build/ or runs/.
#   scripts/phase0_env.sh <calibration.json of batch 1>
set -u
cd "${SLURM_SUBMIT_DIR:-$PWD}"
CAL=${1:-build/calibration/calibration.json}
echo "date=$(date -Is)"
echo "host=$(hostname)"
echo "job=${SLURM_JOB_ID:-none}"
echo "commit=$(git rev-parse HEAD) dirty=$(git status --porcelain -- src scripts CMakeLists.txt 2>/dev/null | wc -l) changed files"
echo "cxx=$(c++ --version | head -1)"
echo "rule: alpha=0.01 min_effect=0.02 processes=10 unstable_spread=0.25 statistic=exact sign-flip on sum of 10 log process ratios"
echo "measurement: measure-pair --repeat 10 --repetitions 9 --no-decision, min_time per pair from $CAL"
jq -r '.pairs[] | select(.min_time != null) | "min_time \(.pair) \(.min_time) ref_units=\(.reference_units) cand_units=\(.candidate_units)"' "$CAL"
echo "sha256 $CAL: $(sha256sum "$CAL" | cut -d' ' -f1)"
for f in build/CanMehHarness build/CanMehCalibrate build/CanMehSearch build/CanMehBench \
         src/Search.cpp scripts/phase0.sbatch scripts/phase0b.sbatch scripts/phase0_final.py; do
  [ -e "$f" ] && echo "sha256 $f: $(sha256sum "$f" | cut -d' ' -f1) mtime=$(stat -c %y "$f")"
done
find build/calibration -type f \( -name '*.so' -o -name meta.json \) | sort | while read -r f; do
  echo "sha256 $f: $(sha256sum "$f" | cut -d' ' -f1)"
done
if [ -n "${SLURM_JOB_ID:-}" ]; then
  echo "--- host facts (compute node) ---"
  lscpu | grep -E 'Model name|^CPU\(s\)|Thread|Socket|MHz' | sed 's/  */ /g'
  echo "governor=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo n/a)"
  echo "uptime=$(uptime)"
  echo "my_other_processes=$(ps -u "$USER" -o pid=,comm= | grep -vE ' (bash|ps|grep|sed|awk|cut|sort|sha256sum|find|lscpu|jq|slurm_script|srun|sleep)$' | wc -l)"
  echo "top_cpu_now:"; ps -eo pcpu,user,comm --sort=-pcpu | head -4
  scontrol show job "$SLURM_JOB_ID" 2>/dev/null | tr ' ' '\n' | grep -E '^(Partition|Features|TimeLimit|NodeList|StartTime|JobName|Dependency)='
fi
