#!/bin/bash
# Compile the max-lines-600 experiment variant next to (not over) build/CanMehSearch, with the same flags.
#   sbatch --partition=normal --nodes=1 --ntasks=1 --cpus-per-task=2 --time=0:20:00 --output=runs/slurm-build-%j.log scripts/maxlines600/build.sbatch
set -eu
cd "${SLURM_SUBMIT_DIR:-$PWD}"
R=$PWD
DEF=$(grep '^CXX_DEFINES' build/CMakeFiles/CanMehSearch.dir/flags.make | sed 's/^CXX_DEFINES = //')
eval /usr/bin/c++ $DEF -I$R/src -isystem $R/build/deps/include -O3 -DNDEBUG -std=gnu++17 -pipe \
   scripts/maxlines600/Search_maxlines600.cpp -o build/CanMehSearch-maxlines600 /usr/lib/x86_64-linux-gnu/libcurl.so
sha256sum build/CanMehSearch-maxlines600 scripts/maxlines600/Search_maxlines600.cpp
