#!/bin/bash
# Final submission check on the COMMITTED tree, as the course's "Download ZIP" would deliver it (git archive HEAD): layout, tracked logs,
# no SDK and no API key, bounded-parallel build (-j4) from that archive, smoke checks, and the patch series replayed with `git am` on the
# freshly fetched stock SDK sources. Runs no experiment and no timing.
#   sbatch --partition=normal --nodes=1 --ntasks=1 --cpus-per-task=4 --time=0:45:00 --output=runs/slurm-verify-%j.log scripts/verify_submission.sbatch
set -eu
SRC="${SLURM_SUBMIT_DIR:-$PWD}"
JOB=${SLURM_JOB_ID:-manual$$}
DST=$HOME/.submission-check-$JOB
OUT=$SRC/runs/phase1-final/clean_build_check
mkdir -p "$OUT" "$DST"
COMMIT=$(git -C "$SRC" rev-parse HEAD)
git -C "$SRC" archive HEAD | tar -x -C "$DST"
cd "$DST"
{ echo "job=$JOB host=$(hostname) start=$(date -Is)"; echo "archived_commit=$COMMIT"; echo "cmake=$(cmake --version | head -1)"; echo "cxx=$(c++ --version | head -1)";
  echo "files_in_archive=$(find . -type f | wc -l)";
  echo "Report.pdf in root: $([ -f Report.pdf ] && echo yes || echo NO)";
  echo "patches/*.patch: $(ls patches/*.patch | wc -l)";
  echo "results.jsonl files: $(find runs -name results.jsonl | wc -l); deepseek runs among them: $(find runs/deepseek -maxdepth 2 -name results.jsonl | wc -l)";
  echo "perf.data files (expected 0): $(find . -name 'perf.data*' | wc -l)";
  echo "SDK dirs or fit_*.cpp/hpp in archive (expected 0): $(find . \( -name FITSDK -o -name sdk -o -name 'fit_*.cpp' -o -name 'fit_*.hpp' \) | wc -l)";
  echo "files containing the API key (expected 0): $(grep -rIlF -f <(tr -d '\n\r' < ~/.config/canmeh/api-key) . 2>/dev/null | wc -l)"; } > "$OUT/check.txt"
cmake -S . -B build > "$OUT/configure.log" 2>&1
cmake --build build -j4 --target CanMehHarness CanMehCalibrate CanMehBench CanMehDecodeForSampler CanMehData CanMehSearch > "$OUT/build.log" 2>&1
echo "build_exit=0 end_build=$(date -Is)" >> "$OUT/check.txt"
for t in CanMehHarness CanMehSearch CanMehBench CanMehCalibrate; do
  ./build/$t --help > /dev/null 2>&1 && echo "$t --help: ok" >> "$OUT/check.txt" || echo "$t --help: FAILED" >> "$OUT/check.txt"
done
T=$(ls runs/phase0b-1069564/trials/faster-5-percent/t05[1-3].json 2>/dev/null | tr '\n' ' ')
./build/CanMehSearch --rule-eval $T > "$OUT/rule_eval_smoke.jsonl" 2>&1 && echo "rule-eval on 3 stored trials: ok" >> "$OUT/check.txt"
# patch series on the SDK sources CMake just fetched
SDKSRC=build/FITSDK-prefix/src/FITSDK/src
export GIT_AUTHOR_NAME=v GIT_AUTHOR_EMAIL=v@example.com GIT_COMMITTER_NAME=v GIT_COMMITTER_EMAIL=v@example.com
mkdir -p ps && cp -r "$SDKSRC" ps/src && ( cd ps && git init -q && git add -A && git commit -qm stock && git am -q ../patches/*.patch ) \
  && echo "patches/ applied in order with git am on the fetched stock SDK: ok ($(git -C ps log --oneline | wc -l) commits incl. stock)" >> "$OUT/check.txt" \
  || echo "patches/ git am: FAILED" >> "$OUT/check.txt"
mkdir -p fs && cp -r "$SDKSRC" fs/src && ( cd fs && git init -q && git add -A && git commit -qm stock && git apply ../experiments/patches/final-cumulative/greedy-seed3.cumulative-vs-stock.patch && git add -A && git commit -qm final ) \
  && [ "$(git -C ps rev-parse 'HEAD^{tree}')" = "$(git -C fs rev-parse 'HEAD^{tree}')" ] \
  && echo "series result == greedy-seed3 final cumulative patch: IDENTICAL" >> "$OUT/check.txt" || echo "series vs final cumulative: DIFFERENT or failed" >> "$OUT/check.txt"
echo "end=$(date -Is)" >> "$OUT/check.txt"
cd "$SRC"; rm -rf "$DST"
