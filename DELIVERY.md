# Submission guide

Project: LLM-driven patch search over the Garmin FIT SDK 21.201.0 (greedy chain vs best-of-N, model `deepseek-v4.1-flash`, five seeds per arm, compiler and human controls).
The FIT SDK is **not** in this repository (CMake fetches it while configuring). No API key is in the repository or in the logs.

## Where things are

| What | Where |
|---|---|
| Report (4 pages + references, one figure) | `Report.pdf` (repository root) |
| Patch series (12 patches, `0001`…`0012`, apply in order; each carries its description at the top) | `patches/` |
| Measurement rule and search loop (only `src/Search.cpp` was edited; the rest of `src/` is provided code) | `src/Search.cpp` |
| Run logs, one directory per run: `results.jsonl` (one row per generation), `credits.csv`, `summary.json`, `run.json`, `node.txt`, `patches/`, `llm/`, `measurements/`, `harness/` (compiler and benchmark output per candidate), `evaluate-best/` (3 independent re-measurements of the final patch) | `runs/deepseek/greedy-s{1..5}-*`, `runs/deepseek/bestofn-s{1..5}-*` |
| Completion of seed-1 greedy to 40 HTTP requests; post hoc 34-request re-measurements; preflight and smoke calls | `runs/deepseek/greedy-s1-1072019-resume-1072894/`, `runs/deepseek-common34/`, `runs/deepseek/preflight-1071764/`, `runs/deepseek-smoke/` |
| Phase 0 calibration (trials, final summary, audit) | `runs/phase0-1068829/`, `runs/phase0b-1069564/` (`audit/phase0_audit.md`, in Chinese) |
| Controls C1/C2/inert | `runs/controls-1068897/`, `runs/controls-native-1071478/`, `runs/human-control/`, `runs/inert-check/` |
| Frozen analysis export, recomputed statistics, hash manifests, checks | `runs/phase1-final/` (`README.md`, `phase1_runs.csv`, `phase1_final.json`, `common34.csv`, `controls.csv`, `recomputed_stats.md`, `autocorr.md`, `run_facts.json`, `node_hardware/`, `clean_build_check/`, `patch_series_check.txt`) |
| Earlier model's runs (qwen3-coder-next; archived, not analysed in the report) | `runs/main/`, `archive/qwen-experiment/` |
| Supporting patch records: other chains, each run's final patch with short descriptions | `experiments/patches/` |
| Report source (TeX, bib, figure, numbers) and talk material (slides, script, code map) | `report/`, `talk/` |
| Scripts: run jobs, analysis, figure, report, slides, checks | `scripts/` |

`runs/` is tracked. Left out on purpose: the profiler recordings (`perf.data*`, about 590 MB; the sampled line reports `sampling/sample.txt` are kept) and per-run `scratch/` directories.

## Checks (as in the submission instructions)

```sh
git ls-files Report.pdf patches/ runs/deepseek/greedy-s1-1072019/results.jsonl runs/deepseek/bestofn-s1-1072020/results.jsonl
git ls-files runs | grep -c results.jsonl            # every run's results.jsonl is tracked
git check-ignore -v runs/deepseek/greedy-s1-1072019/results.jsonl || echo "not ignored"
```

The submitted commit hash is given in the Canvas submission comment (it cannot be stored inside the commit it names).

## Build (clean checkout)

Needs CMake 3.20+, a C++17 compiler, libcurl, network access while configuring (CMake fetches the FIT SDK, Google Benchmark, nlohmann/json, CLI11) and `jq`. Use a compute node (the login node caps threads); bounded parallelism:

```sh
cmake -S . -B build
cmake --build build -j4 --target CanMehHarness CanMehCalibrate CanMehBench CanMehDecodeForSampler CanMehData CanMehSearch
```

`scripts/verify_clean_build.sbatch` builds from a clean copy and runs smoke checks (`--help` of four tools; the frozen rule replays three stored Phase 0 measurements; scan for an SDK directory and the API key).
The check on the committed tree (fresh clone, `git archive`) is recorded in `runs/phase1-final/clean_build_check/`.

## Run one search (needs `~/.config/canmeh/api-key`, mode 600, never committed)

```sh
sbatch --partition=normal --constraint="xcnc|xcnd" --nodes=1 --ntasks=1 --cpus-per-task=24 --mem=0 --time=3:00:00 \
       --job-name=canmeh-ds-greedy --output=runs/slurm-%j.log \
       --export=ALL,MODE=greedy,SEED=2,GENS=40,MAXTOK=32768,TAG=deepseek,DEADLINE=9300 scripts/run_deepseek.sbatch   # MODE=greedy|bestofn
```

Each job: `CanMehHarness init` (null check must be clean) → `CanMehSearch` → three re-measurements of the fixed final patch → summary refresh. Timings belong on compute nodes only, one job per node.
Other jobs: `scripts/phase0*.sbatch` (calibration), `controls.sbatch`, `controls_native.sbatch` (C1/C2/inert), `preflight.sbatch`, `common34_remeasure.sbatch`, `node_facts.sh`; `scripts/resume/` holds the variant used to complete seed-1 greedy.

## Regenerate the analysis, figure, report, slides (no experiments)

```sh
python3 scripts/aggregate_deepseek.py; python3 scripts/phase1_final.py; python3 scripts/recompute_stats.py
python3 scripts/autocorr_report.py; python3 scripts/collect_run_facts.py
MPLCONFIGDIR=$HOME/.mplconfig python3 scripts/make_figure.py
pip install --target $HOME/.pylib-deliver python-pptx reportlab                     # once; not part of the project build
PYTHONPATH=$HOME/.pylib-deliver python3 scripts/build_report.py                     # Report.pdf, report/report.tex, report/references.bib
PYTHONPATH=$HOME/.pylib-deliver python3 scripts/make_slides.py                      # talk/talk.pptx
scripts/verify_patch_series.sh                                                      # replays every patch series with git am
```

`Report.pdf` is rendered with reportlab from the same content blocks as `report/report.tex`; the TeX source was never compiled (no TeX engine on the cluster; not required).

## Code version and freeze

`runs/phase1-final/VERSIONS.txt` and `MANIFEST-raw.sha256` (hashes of data and code at freeze), `MANIFEST-analysis.sha256` (analysis files added afterwards); `runs/phase1-final/Search.cpp.diff-vs-HEAD.patch` is the diff of `src/Search.cpp` against the project's first commit.
The seed-1 greedy completion used `scripts/resume/Search_resume.cpp`; every other run used the frozen `src/Search.cpp` (sha256 `67935a2f31355932a25f305e6e46fcb78d76105dcb99526d9fe80d42e2eb54ea`).

## Open items (stated plainly)

- **C2 time.** No stopwatch or timer record exists for the one-hour human optimisation; only file timestamps (10:20–11:11 on 2 Nov). The author-reported time is not in the repository and is not stated in the report. Who typed which C2 lines is not recorded (human-directed, AI-assisted).
- **Patch series scope.** `patches/` is the explained median-seed (seed 3) greedy chain. The other four chains are experiment records with provenance-only messages (`experiments/patches/`); every run's final patch has a short description there.
- **Course quotient.** The README reads `best_confirmed_speedup` from the last `credits.csv` row; our rank-mode `credits.csv` has no such column and `summary.json` keeps an unused default of 1.0 (read literally it would give 0). The report computes metric A from `results.jsonl` (best candidate whose two measurements both passed the frozen rule) and metric B from the independent re-measurement; raw logs are unchanged.
- **Unknown token use.** Ten HTTP-502 requests returned no usage object; their consumption is unknown and not in the totals.
- **Budgets.** Three of five greedy runs stopped before 40 HTTP requests (job time limit); the 34-request comparison is post hoc and exploratory.
- **Correctness** rests on the harness checks only (digest, profile digest over all message/field numbers, single-thread check); no concurrent-use, big-endian or wider-input tests.
- **Slides** were built programmatically and not rendered (no PowerPoint/LibreOffice on the cluster); open once and check the layout. Report, slides and script are English only.
- **CPU facts** were recorded after the runs (`runs/phase1-final/node_hardware/`); node xcnd24 (controls) was not recorded.

## AI assistance

Code, analysis scripts, figure, report, slides and patch commit messages were prepared with Claude Code (Anthropic) under the author's direction; the patches of the automated search were generated by `deepseek-v4.1-flash`;
the C2 patches are human-directed and AI-assisted. The author remains responsible for checking every claim against `runs/phase1-final/`.
