#!/bin/bash
# Round 2: build the correctness corpus = the 4 standard files + deterministic mutants (kind data/defs/trunc: NOT legal inputs, stress only)
# + legal files written by the ORIGINAL SDK encoder (kind valid). Writes $1 (corpus dir). The generator is compiled against the stock SDK sources.
set -eu
cd "${SLURM_SUBMIT_DIR:-$PWD}"
C=$1; NVALID=${2:-60}
SDK=$PWD/build/FITSDK-prefix/src/FITSDK/src
G=$HOME/.gen-valid-$$
mkdir -p "$G/obj" "$G/files"
for f in "$SDK"/*.cpp; do g++ -std=c++17 -O1 -I "$SDK" -c "$f" -o "$G/obj/$(basename "$f" .cpp).o" & done; wait
g++ -std=c++17 -O1 -I "$SDK" -c scripts/round2/gen_valid_fit.cpp -o "$G/gen.o"
g++ "$G/gen.o" "$G"/obj/*.o -o "$G/gen_valid_fit"
"$G/gen_valid_fit" "$G/files" "$NVALID" 1
# keep only files the stock decoder accepts completely (status 0): a legal file the stock SDK cannot decode would not be a usable comparison input
g++ -std=c++17 -O1 -I src -I "$SDK" -c scripts/followup/driver.cpp -o "$G/driver.o"
g++ "$G/driver.o" "$G"/obj/*.o -o "$G/driver" -lpthread
mkdir -p "$G/ok"; kept=0; dropped=0
"$G/driver" classify "$G/files" > "$G/classify.txt"
while read -r path status rest; do
  if [ "$status" = 0 ]; then cp "$path" "$G/ok/"; kept=$((kept + 1)); else dropped=$((dropped + 1)); echo "dropped $(basename "$path"): status $status $rest" >> "$G/dropped.txt"; fi
done < "$G/classify.txt"
python3 scripts/followup/gen_corpus.py "$C" --per-file 100 --seed 1 --valid-dir "$G/ok"
cp "$G/classify.txt" "$C/valid_generation_classify.txt"; cp -f "$G/dropped.txt" "$C/valid_generation_dropped.txt" 2>/dev/null || true
echo "valid files kept=$kept dropped=$dropped" > "$C/valid_generation_summary.txt"
cat "$C/valid_generation_summary.txt"
rm -rf "$G"
