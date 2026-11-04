# Phase 1 final (frozen 2026-11-04)

Files
- `phase1_runs.csv`, `phase1_final.json`: 20 runs (Qwen matrix 10, DeepSeek seeds 1-5 x 2 arms). The JSON gives, per run, an `evidence` block of
  raw files (summary.json, results.jsonl, credits.csv, run.json, node.txt, final evaluation) and `field_sources` for the main numbers.
- `common34.csv`: post-hoc common-budget analysis (best patch by the then-current ranking within the first 34 HTTP requests; 34 = shortest run).
- `controls.csv`: C1 compiler flags, C2 human patches, inert check. Batch 1068897 O3native rows are INVALID (init failed) and superseded by 1071478.
- `STATS.md`: medians, ranges, group tests (primary: exact permutation test of median difference; Mann-Whitney exact and paired sign test alongside).
- `MANIFEST-raw.sha256` (+ `.sha256`): hashes of all code, binaries, configs, raw logs, patches before the post-hoc re-measurements; `MANIFEST-analysis.sha256`: hashes of what was added afterwards.
- `VERSIONS.txt`, `Search.cpp.diff-vs-HEAD.patch`: versions; uncommitted Search.cpp changes relative to the last commit.

Definitions
- best_confirmed_speedup = median speedup of the 3 independent re-measurements of the run's fixed final patch (1.0 if any fails alpha 0.01 / >=2%).
- course metric = (best_confirmed_speedup - 1) / total_tokens; total_tokens counts everything spent (truncated replies, errors; seed-1 greedy includes its resume call).
  credits.csv and summary.json are untouched.
- Probe/preflight/smoke calls are outside the per-run totals (preflight job 1071764, smoke jobs 1071941/1071942, one 13-token probe per run).
- Seed-1 greedy hit its deadline at 39 HTTP attempts and was completed to 40 by resume job 1072894 (replayed draws matched 40/40); the resume ran on another node.

Note (final layout): `MANIFEST-raw.sha256` lists the freeze-time hashes of the files that remain in the submitted tree (code, scripts, runs). Its original also covered `review-package/` (Qwen-era review copies), caches, profiler recordings (`perf.data*`) and `scratch/` directories, none of which is part of the submission; those lines were removed; `sha256sum -c MANIFEST-raw.sha256` reports all OK.
`MANIFEST-analysis.sha256` covers the analysis, report, patches and talk files under their final paths.
