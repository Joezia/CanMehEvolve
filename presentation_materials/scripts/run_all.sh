#!/bin/bash
# Rebuilds every table, figure and document of presentation_materials/ from the raw files under runs/ (no experiment is started, no raw file is modified).
# usage: bash presentation_materials/scripts/run_all.sh        (from the repository root; ~2-3 minutes; needs numpy, scipy, pandas, matplotlib)
set -eu
cd "$(dirname "$0")/../.."
export MPLCONFIGDIR=${MPLCONFIGDIR:-$HOME/.mplconfig}
S=presentation_materials/scripts
for s in build_calibration build_fpr build_nullsearch build_controls build_runs build_compare build_regions build_funnel build_mechanism build_correctness build_concurrency \
         build_correctness_by_config build_environment build_checklist build_job_concurrency make_figures doc_part_a doc_part_b doc_part_c doc_part_d doc_overview doc_qa build_sources assemble_evidence; do
  echo "== $s"; python3 $S/$s.py > /dev/null
done
echo done
