# Key code locations (for preparing questions)

Line numbers refer to the frozen `src/Search.cpp` (sha256 `67935a2f…`, uncommitted edits on top of commit 0bce247) and the other files as of the freeze.
The measurement tools (`CanMehHarness`, `CanMehBench`, `CanMehCalibrate`) are teacher code; only `src/Search.cpp` was edited.

| Topic | Where |
|---|---|
| Frozen decision rule: 10 processes, spread limit 0.25 | `src/Search.cpp:279-280` (`kRequiredProcesses`, `kUnstableSpread`) |
| Exact sign-flip p-value (2^10 patterns) | `src/Search.cpp:356` `signFlipPValue` |
| Ratio, p, spread, "faster" / "unstable" verdict | `src/Search.cpp:376` `analyzeTimings` (spread → unstable at :440, faster at :446) |
| Faster at the ≥2% gate | `src/Search.cpp:473` `candidateIsFaster` |
| Null run must be clean before a search | `src/Search.cpp:863` `checkNullEvidence` |
| One candidate measurement (calls the harness) | `src/Search.cpp:817` `measureOnce` → `:481` `runHarnessCommand` |
| Reference/candidate in one process, alternating slots | `src/BenchmarkProcess.cpp:154-184` (`--swap`); `src/Harness.cpp:1602` `measure-pair`, `:1590` `measure-patch` |
| Harness subcommands: init, regions, show, splice, sampling-library | `src/Harness.cpp:1543, 1561, 1569, 1577, 1597` |
| Prompt given to the model | `src/Search.cpp:573` `systemPrompt`, `:593` `userPrompt` |
| Own HTTP adapter (content only, usage, no hidden retry) | `src/Search.cpp:668` `callModel`; failure classes (`truncated`, `llm_empty`, `model_mismatch`…) `:749` `llmFailure` |
| Code extraction from the reply | `src/Search.cpp:538` `splitReply` |
| Profile weighting (90% perf-weighted / 10% uniform) | `src/Search.cpp:1233-1273` (profile), `:1321` `pickRegion` (RNG `:1276`) |
| Greedy parent = current best; best-of-N parent = stock | `src/Search.cpp:1314` `pickParent` |
| Budget in HTTP requests, deadline, stop signal | `src/Search.cpp:1358-1363` |
| Rank rule R = max(r1, r2); update only if R < record | `src/Search.cpp:1456-1510` (`possiblyBetter` at `:1461`) |
| Fixed final patch, 3 independent re-measurements | `src/Search.cpp:908` `evaluatePatchMode`; invoked from `scripts/run_deepseek.sbatch` |
| Preflight (max_tokens / model check) | `src/Search.cpp:959` `preflightMode` |
| Resume of seed-1 greedy (separate file) | `scripts/resume/Search_resume.cpp` (adds `--resume-from`; replays draws, aborts on mismatch) |
| Per-run job: init → null check → search → re-measure | `scripts/run_deepseek.sbatch` |
| Cross-seed summary / Phase 1 export / figure / report / slides | `scripts/aggregate_deepseek.py`, `scripts/phase1_final.py`, `scripts/make_figure.py`, `scripts/make_report.py`, `scripts/make_slides.py` |
| Phase 0 trials and audit | `runs/phase0-1068829`, `runs/phase0b-1069564/audit/phase0_audit.md`, `scripts/phase0_audit.py` |

## Questions you may get, and where the answer is

- *Why is the ranking rule not a significance test?* It takes max of two measurements and updates when R is below the record, with no 2% gate; it only orders candidates. Significance and the 2% gate apply to the final patch's three re-measurements (`final-evaluation.log`, `evaluate-best/summary.json`). `src/Search.cpp:1456-1510`.
- *Are the arms comparable?* Same model, prompt template, `max_tokens` 32768, sampling code, budget of 40 HTTP requests. Differences: the text shown (stock vs current best) and memory. `runs/deepseek/*/run.json`.
- *Why do the function draws differ between the seed-1 arms?* Each run profiles independently (perf noise changes the weights); replaying each run's saved `sampling/sample.txt` reproduces all 40 draws (see report §4).
- *Why did three greedy runs stop early?* Job limit 3 h on the cluster; search deadline 9,300 s so init and the final re-measurement fit. Seed 1 hit 9,600 s at 39 requests and was completed by a resume job (`runs/deepseek/greedy-s1-1072019-resume-1072894`).
- *What is the 34-request analysis?* Post hoc: best patch by the then-current ranking within 34 requests; `runs/phase1-final/common34.csv`.
- *Is a patch correct?* Only the harness checks (output checksum, no crash, loads); see report §4 for the static-cache and endianness caveats.
- *Where is the human control?* `runs/human-control/c2-1058781` (attempt-1/2 patches), measured in `runs/controls-1068897`.
