#!/bin/bash
# Delivery check: build the project from a clean copy of the sources (no build/, no runs/, no SDK, no key) with BOUNDED
# parallelism (-j4), then run cheap smoke checks. Runs no experiment and no timing.
#   sbatch --partition=normal --nodes=1 --ntasks=1 --cpus-per-task=4 --time=0:45:00 \
#          --output=runs/slurm-verify-%j.log scripts/verify_clean_build.sbatch
set -eu
SRC="${SLURM_SUBMIT_DIR:-$PWD}"
JOB=${SLURM_JOB_ID:-manual$$}
DST=$HOME/.clean-build-check-$JOB
OUT=$SRC/runs/phase1-final/clean_build_check
mkdir -p "$OUT" "$DST"
cd "$SRC"
tar --exclude='__pycache__' -cf - CMakeLists.txt cmake src scripts patches report talk Report.pdf README.md .gitignore | tar -xf - -C "$DST"
cd "$DST"
{ echo "job=$JOB host=$(hostname) start=$(date -Is)"; echo "cmake=$(cmake --version | head -1)"; echo "cxx=$(c++ --version | head -1)";
  echo "source_files_copied=$(find . -type f | wc -l)"; } > "$OUT/check.txt"
cmake -S . -B build > "$OUT/configure.log" 2>&1
cmake --build build -j4 --target CanMehHarness CanMehCalibrate CanMehBench CanMehDecodeForSampler CanMehData CanMehSearch > "$OUT/build.log" 2>&1
echo "build_exit=0 end_build=$(date -Is)" >> "$OUT/check.txt"
for t in CanMehHarness CanMehSearch CanMehBench CanMehCalibrate; do
  ./build/$t --help > /dev/null 2>&1 && echo "$t --help: ok" >> "$OUT/check.txt" || echo "$t --help: FAILED" >> "$OUT/check.txt"
done
# the frozen decision rule replays a stored Phase 0 measurement (no timing is done here)
T=$(ls "$SRC"/runs/phase0b-1069564/trials/faster-5-percent/t05[1-3].json 2>/dev/null | head -3 | tr '\n' ' ')
if [ -n "$T" ]; then ./build/CanMehSearch --rule-eval $T > "$OUT/rule_eval_smoke.jsonl" 2>&1 && echo "rule-eval on 3 stored trials: ok" >> "$OUT/check.txt"; fi
echo "tracked-file scan: SDK dirs present in copy: $(find . -path ./build -prune -o -type d \( -name sdk -o -name FITSDK \) -print | wc -l)" >> "$OUT/check.txt"
# the key file ends with a blank line, which GNU grep -f may treat as an empty pattern matching everything on some nodes; strip newlines first
echo "key scan: files containing the key in copy: $(grep -rIlF -f <(tr -d '\n\r' < ~/.config/canmeh/api-key) . --exclude-dir=build 2>/dev/null | wc -l)" >> "$OUT/check.txt"
echo "end=$(date -Is)" >> "$OUT/check.txt"
cd "$SRC"; rm -rf "$DST"
