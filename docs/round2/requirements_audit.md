# Round 2: requirements audit

Branch `round2`, started from the submitted commit `d5aa9e7` (kept unchanged). New experiments live under `runs/round2/`, new scripts under `scripts/round2/`.
Sources: the course `README.md` (full text: Architecture / Provided code, Phase 0, Phase 1, Phase 2, Controls, Cluster, Deliverables, Marking, Measurement discipline, Defaults, Glossary).

Legend for **Type**: **R** = explicit requirement in the README; **D** = default parameter the README states; **O** = our own choice (not required by the README).
Legend for **Status**: **met** = implemented and evidenced; **partly** = see note; **missing** = not done; **round 2** = this round adds it.

## 1. The README is explicit that the loop is OURS to write, population included

`README.md` (Architecture): *"read every later sentence about what `CanMehSearch` does as a requirement on the program you write rather than as behavior you inherit. The files under `--out`,
the population, the profiling pass before the first generation and the `null_ok` check are all described in this document because your implementation has to produce them."*
The Glossary then defines population (at most `--population` patches, sorted by ratio, worst evicted, every *measured* candidate retained), tournament of two for the parent, parent patch / lineage
(child inherits every rewrite above it), `improved_on_parent`, `retained`. Consequently the round-1 DeepSeek arms ("greedy" = population of one, no failure feedback; best-of-N under a ranking rule)
were **not** the README loop, and the "reference design" argument for skipping population or failure feedback does not hold. Round 2 therefore runs the README population search with DeepSeek.

## 2. Requirement checklist

| # | Requirement | Type | Where implemented | Evidence | Status / what is needed |
|---|---|---|---|---|---|
| 1 | `CanMehSearch` is written by us; only `src/Search.cpp` is edited; provided measurement programs, workload and checks are not changed | R | `src/Search.cpp` (diff vs `0bce247` in `runs/phase1-final/Search.cpp.diff-vs-HEAD.patch`; round-2 edit by `scripts/round2/patch_search_cpp.py`) | `git diff --stat 0bce247 -- src` shows only `src/Search.cpp` | met |
| 2 | Rule reads `timings` from `measure-patch --no-decision` and computes its own statistics | R | `analyzeTimings`, `signFlipPValue`, `candidateIsFaster` | Phase 0 replay of 681 trials with 0 mismatches (`runs/phase0b-1069564/audit`) | met |
| 3 | Phase 0 calibrated the rule that is actually run; false-positive rate with CI, detection rate per effect, bias; trial count and `--repeat/--repetitions/--min-time/work count` | R | `scripts/phase0*.sbatch`, `CanMehCalibrate` pairs | `runs/phase0b-1069564/final`, `audit/phase0_audit.md` | met: 100 phase-0 trials + 400 new round-2 trials (xcnc 200, xcnd 200) = 500 valid, 0 false accepts, 95% upper bound 0.74% (xcnd alone: 200 trials, bound 1.83%, below the per-class 400 target) |
| 4 | Lag-1 autocorrelation (median and range per measurement) for calibration and for the SDK decode; state whether the rule assumes independent repetitions | R | `scripts/autocorr_report.py` | `runs/phase1-final/autocorr.md` | met (round 2 adds the new SDK measurements) |
| 5 | An inert patch spliced into the SDK and evaluated by hand | R | `runs/inert-check` | `runs/controls-1068897/eval-inert` (5 measurements); `runs/followup/sdk-inert-*` (240); round 2 tops up per node class (`runs/round2/fpr/sdk-inert-*`) | met: 402 valid trials per node class (120 follow-up + 282 round 2), 0 false accepts, 95% upper bound 0.91% each |
| 6 | `null_ok` from `CanMehHarness init` checked before every search, node recorded | R | `scripts/round2/run_segment.sbatch`, `scripts/run_deepseek.sbatch` | `runs/round2/runs/*/segments/*.init.json`, `*.node.txt` | met (round 2: checked in every segment) |
| 7 | Loop steps: regions -> region draw -> `show` under the parent patch -> prompt -> model -> splice -> `measure-patch --no-decision` -> own rule -> feed compile and correctness failures into the next prompt -> log every candidate | R | `main` in `src/Search.cpp` (`--mode search`: repair attempt after a repairable failure) | round-1 old Qwen `search`; round 2 DeepSeek `search` | round 1 DeepSeek: **missing** (no feedback); round 2: met |
| 8 | Population: capacity `--population` (default 6), every measured candidate retained, sorted by ratio, worst evicted | R/D | `population` vector, `stable_sort`, `pop_back` | `state.json` records the population after every generation (round 2) | round 1 DeepSeek: **missing**; round 2: met |
| 9 | Parent chosen by a tournament of two; child patch is applied on top of the parent (cumulative) | R | `pickParent`; `splice --patch <parent>` | `results.jsonl` `parent`, `parent_ratio`; `patches/gen_N.patch` | round 1 DeepSeek: **missing** (parent = best only); round 2: met |
| 10 | Profile one decode first (`--sample-seconds`), draw regions in proportion to samples; `--uniform-share` (default 0.1) draws ignore the profile | R/D | profiling block in `main`; `pickRegion` | `profile.json`, `profile_samples.json` (all region weights), `sampling/sample.txt` | met |
| 11 | Region credit: the region with the largest improvement over its parent receives more draws (`improved_on_parent`, `regions_tried.json`) | R (mechanism), O (share 0.25) | `exploitShare` (now `--exploit-share`, default 0.25), `regionStats` | `regions_tried.json` | met for the population arm; best-of-N does not use it (README C3: no memory) |
| 12 | Files under `--out`: `results.jsonl` (fields listed in the README), `credits.csv` with exactly `generation,calls,prompt_tokens,completion_tokens,total_tokens,best_confirmed_speedup,best_retained_speedup,elapsed_s`, `regions_tried.json`, `best.patch`, `patches/gen_N.patch`, `patches/gen_N.repl` | R | search / bestofn-confirmed modes | round-2 run directories | round 1 DeepSeek `credits.csv`: **deviated** (ranked column instead of confirmed); round 2: exact columns (+ `credits_extra.csv`) |
| 13 | `best_confirmed_speedup` counts only candidates that cleared the rule twice; `best_retained_speedup` every kept candidate; the bonus quotient reads `best_confirmed_speedup` from the last `credits.csv` row | R | non-rank branch of `main` | `credits.csv` last row | round 1 DeepSeek: **missing** (replaced by derived metrics); round 2: met |
| 14 | `--generations` counts model calls; compare runs by calls, not generations | R | `--request-budget` (HTTP requests) | `summary.json` `http_attempts` | met (round 2: budget counts HTTP requests sent) |
| 15 | Population search vs best-of-N at an equal call budget (C3): same model, same prompt, every call from stock, no feedback, no population, no memory | R | `--mode bestofn-confirmed` | `scripts/round2/make_chains.py` | round 1 DeepSeek best-of-N used a different (ranking) evaluation -> not matched; round 2 reran: 10 matched pairs (5 seeds x 2 models), 40 HTTP requests each, all complete |
| 16 | At least five seeds per configuration; median and full range (C4) | R | `scripts/round2/make_chains.py` | `runs/round2/protocol.json` | round 1: met for greedy/best-of-N; round 2: met, 5 seeds x 4 configurations, 20/20 complete, medians and ranges in `runs/round2/RESULTS.md` |
| 17 | C1 compiler control at -O2 / -O3 / -O3 -march=native | R | `scripts/controls*.sbatch` | `runs/controls-native-1071478` | met |
| 18 | C2 human control: one timed hour, before looking at any search output; report patch and time | R | `runs/human-control` | file times only; no timer | **cannot be completed after the fact**; stays "time not recorded" |
| 19 | Model id that answered (not always the requested id); tokens from `credits.csv` beside the claimed speedup | R | `callModel`, `llmFailure` (`--llm-expect-model`) | `results.jsonl` `llm.model_returned` per request | met |
| 20 | Machine, compiler version, model and version string, seeds, calls, wall-clock; abandoned/failed runs; which node every baseline came from | R | per-segment `node.txt`, `init.json` | `runs/round2/runs/*/segments/` | met: `runs/round2/TRACEABILITY.md` (jobs, hosts, commits, hashes per run) |
| 21 | Submit at most four LLM jobs at a time (the endpoint serves four at full speed) | R (advice) | four self-managing chains (`scripts/round2/run_segment.sbatch`) | `runs/round2/chains/` | met: four chains; the "all nodes may run in parallel" instruction was applied to non-LLM jobs only, LLM jobs stayed at 4 |
| 22 | Timing only on compute nodes of the calibrated family (`xcnc|xcnd`), whole node (`--mem=0 --cpus-per-task=24`), work directory named after the job | R | all scripts | `node.txt` | met |
| 23 | `--repeat` > 1 (default 1 is unsafe), `--min-effect` 0.02, `--min-time` as init recorded | D | `scripts/*.sbatch` use `init --repeat 10` | `meta.json` | met |
| 24 | Patch series: best patches, each applying cleanly in order, each with a message saying what it changes and why it is faster | R (Deliverables) | `patches/` on `main` | `runs/phase1-final/patch_series_check.txt` | submitted series exists; round 2 adds patches only if the new runs produce a better candidate |
| 25 | Report and talk | R | out of scope for this round | | not touched |

Provided-code note: the README provides `utilities::requestModelReply` (which retries up to three times internally). Our `callModel` in `src/Search.cpp` replaces it **on purpose**: it sends exactly one HTTP request per attempt, logs the returned model id,
finish reason and usage, and counts every request (a hidden retry would make "40 requests" unverifiable). Only `src/Search.cpp` was edited.

## 3. Audit of the old Qwen runs (`runs/main`, 10 runs, 3 Nov 2026) against the README loop and the round-2 rules

Code: `archive/qwen-experiment/Search.cpp` (sha256 `ce80cd7b...`; the run's `git_commit` is `0bce247` with uncommitted `src/Search.cpp`, `git_dirty: true`).

| Question | Finding | Evidence |
|---|---|---|
| Is a population kept, a parent selected, the parent's patch inherited? | **Yes**: `search` mode keeps `--population 6`, tournament of two (`pickParent`), `show`/`splice` under the parent patch, worst evicted | archive Search.cpp lines 1055-1060, 1236-1241; `results.jsonl` fields `parent`, `parent_ratio` |
| Are compile and correctness failures fed back? | **Yes** (search arm): one repair attempt for compile, link, correctness, profile, load, threading, crash, patch, splice failures; **not** in the best-of-N arm | archive Search.cpp lines 1090-1100, 1255-1260; `results.jsonl` `repair_attempt` |
| Are functions chosen by a performance profile? | **Yes**: 20 s `perf` sampling, 10% uniform; in the search arm 25% of draws additionally go to the best-credited region (our choice) | `run.json` `sample_seconds: 20`, `uniform_share: 0.1`; `profile.json` |
| Is every candidate measured with `measure-patch --no-decision` and judged by our own statistics? | **Yes** | `measurements/`, `results.jsonl` `p_value`, `ratio_1`, `ratio_2` |
| Is `null_ok` checked before the run? | **Yes** (`checkNullEvidence`; all 10 runs `null_ok: true`) | `run.json` `null_evidence` |
| Is there a best-of-N with the same model/prompt/budget? | **Yes**: `bestofn` mode starts every call from stock, no population, no repair, no region credit (`!bestOfN` guards), prompt shows 1.0 | archive Search.cpp lines 1055-1062, 1142-1143 |
| Seeds and calls | **5 seeds per arm, 40 model calls per run** (`calls` 40 = results rows 40) | `runs/main/*/summary.json` |
| Are code version, returned model id, parameters, tokens, time, logs traceable? | Mostly: `qwen3-coder-next` returned `qwen3-coder-next` (one probe call, no per-call id); temperature 0.8, max_tokens 4096; tokens and elapsed in `summary.json`; code archived by hash | `run.json`, `summary.json` |
| **Actual HTTP requests per run** | **Not verifiable**: the provided client retries up to 3 times inside one call and the old log counts calls, not HTTP attempts. "40 calls" may hide extra requests after 429/5xx/transport errors | `src/utilities/ChatClient.hpp` (`retries = 3`), archive Search.cpp line 1146-1147 |
| Node balance and class | Mixed and unbalanced (search: 4 xcnc + 1 xcnd; best-of-N: 2 xcnc + 3 xcnd) | `run.json` `hostname` |

Verdict: no defect that changes the search path was found (population, repair, region choice and best-of-N isolation are implemented as the README describes), but the old runs cannot certify
"40 actual HTTP requests" and used one code version and node mix that the new protocol does not. Round 2 therefore **keeps the old Qwen runs unchanged as a separate historical set** and
**re-runs both Qwen arms under the frozen round-2 protocol** (same model `qwen3-coder-next`, temperature 0.8, max_tokens 4096; the HTTP timeout stays 180 s but there is no hidden retry).
Old and new Qwen results are never pooled.

## 4. Round-1 DeepSeek experiment: what it is and is not

Greedy chain and rank-rule best-of-N (`runs/deepseek`, commit `d5aa9e7`) remain as a **different, additional experiment**: population of one, no failure feedback, ranking rule for updates,
different `credits.csv` columns. They are not the README loop and are not mixed with round-2 results. Their `best_confirmed_speedup` in `credits.csv` does not exist; the report's derived metrics stay derived.

## 5. Deviations that round 2 keeps on purpose (and why)

* Own HTTP adapter instead of the provided client (no hidden retries; per-request model id, finish reason and usage).
* `--exploit-share 0.25` for the population arm: our choice, not a README number; the README only says that region credit exists. Best-of-N never uses it (README C3: no memory).
* Request budget 40 counts HTTP requests including repair attempts, 502s and truncated replies; a failure before any request (region draw, `show`, `splice`) is recorded and is not a request.
* A candidate is "confirmed" when two measurements each pass the frozen rule against stock; it does not have to improve on its parent by 2% (README: `improved_on_parent` is separate).

## 6. Final evidence status (after the runs)

* 20/20 formal runs complete, each ended on `request budget reached` at exactly 40 HTTP requests; returned model ids match the requested ones; every final patch re-measured three times in separate jobs (`runs/round2/RESULTS.md` section 1, `TRACEABILITY.md`).
* False-accept rates: section 3 of `RESULTS.md`. 0 false accepts in 500 synthetic-null and 2 x 402 SDK-inert trials. 17 no-op candidates: `.text` and dynamic symbols identical to stock.
* Extended correctness: section 4 of `RESULTS.md`. Legal encoder files (55): all best-of-N finals identical to stock; population finals `qwen-population-s3` (10/55 identical), `qwen-population-s4` (51/55), `ds-population-s2` (54/55) differ. `ds-population-s1` (and the follow-up stacks that contain it) is killed by a signal on 21 hostile definition mutants where stock throws an exception. 16 of 20 finals show TSan reports in `fit_profile.cpp` `GetMesg`.
* Not done / not possible: C2 original timing; stacks of the round-2 best-of-N candidates (the stacks checked are the follow-up ones); the per-class 400 target for synthetic null on xcnd (200 trials).
* Two infrastructure faults in the post-processing were found and fixed after the first attempt: a wrong driver path and a UTF-8 decode error in `sanitize_v2.py`, and a whole-corpus `classify` run that stopped at the first signal-killed file (now one process per file). The fixed script is what produced the committed sanitizer results; the failed attempts (`SAN-1096974`, `SAN-1097084`) are kept for the record.
