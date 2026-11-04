#!/bin/bash
# Independent check of the delivered patch series: for every series directory, replay it with `git am` on a scratch copy of the stock
# SDK sources, compare the resulting tree with the run's final cumulative patch applied to stock (`git apply`), and count commit
# messages that carry the "What:"/"Why it might be faster:" explanation.  Scratch space: $HOME/.verify-series (NOT /tmp: 10 MB quota).
set -eu
ROOT=$(cd "$(dirname "$0")/.." && pwd)
STOCK=$ROOT/build/FITSDK-prefix/src/FITSDK/src
W=$HOME/.verify-series; rm -rf "$W"; mkdir -p "$W"
export GIT_AUTHOR_NAME=v GIT_AUTHOR_EMAIL=v@example.com GIT_COMMITTER_NAME=v GIT_COMMITTER_EMAIL=v@example.com
declare -A FINAL=( [experiments/patches/greedy-s1-unexplained]=greedy-seed1 [experiments/patches/greedy-s2-unexplained]=greedy-seed2 [patches]=greedy-seed3 [experiments/patches/greedy-s4-unexplained]=greedy-seed4 [experiments/patches/greedy-s5-unexplained]=greedy-seed5 )
for d in "${!FINAL[@]}"; do
  S=$ROOT/$d; F=$ROOT/experiments/patches/final-cumulative/${FINAL[$d]}.cumulative-vs-stock.patch
  for kind in series final; do
    rm -rf "$W/$kind"; mkdir -p "$W/$kind"; cp -r "$STOCK" "$W/$kind/src"
    ( cd "$W/$kind"; git init -q; git add -A; git commit -qm stock )
  done
  n=$(ls "$S"/*.patch | wc -l)
  ( cd "$W/series"; git am -q "$S"/*.patch )
  ( cd "$W/final"; git apply "$F"; git add -A; git commit -qm final )
  t1=$(git -C "$W/series" rev-parse 'HEAD^{tree}'); t2=$(git -C "$W/final" rev-parse 'HEAD^{tree}')
  expl=$(grep -l "^What:" "$S"/*.patch | wc -l)
  [ "$t1" = "$t2" ] && eq=IDENTICAL || eq=DIFFERENT
  echo "$d: $n patches applied in order with git am; tree vs final cumulative patch: $eq; messages with What:/Why explanation: $expl/$n"
done
rm -rf "$W"
