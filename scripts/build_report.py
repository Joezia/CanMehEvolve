#!/usr/bin/env python3
"""Build the report from ONE source of prose and numbers: writes report/report.tex, report/references.bib and the PDF Report.pdf (repository root).

Why two outputs: report.tex (article, one column, Times-like 10 pt, booktabs) is the primary deliverable, but the cluster has no TeX engine
and downloading one was not permitted, so the PDF here is rendered with reportlab from the SAME blocks with matching page geometry
(A4, 10 pt serif, same margins, same tables and figure).  Compile report.tex with pdflatex+bibtex to get the TeX-typeset PDF.
Numbers come from scripts/report_numbers.py (raw/recomputed files); nothing numeric is typed into the prose by hand.
Usage:  PYTHONPATH=$HOME/.pylib-deliver MPLCONFIGDIR=$HOME/.mplconfig python3 scripts/build_report.py
"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import report_numbers

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "report"
N = report_numbers.load()
P0, ST, FA, CT, RUNS, C34, AC, C2 = N["phase0"], N["stats"], N["facts"], N["controls"], N["runs"], N["common34"], N["autocorr"], N["c2"]
T = ST["tests"]
PR = ST["per_run"]

f3 = lambda x: "%.3f" % x
f4 = lambda x: "%.4f" % x
e7 = lambda x: "%.2f" % (x * 1e7)
pct = lambda x: "%.1f" % (100 * x)
rng3 = lambda t, k: "%s (%s–%s)" % (f3(t[k + "_median"]), f3(t[k + "_range"][0]), f3(t[k + "_range"][1]))
sg = lambda x: ("%+.2f" % x).replace("-", "−")


def runrow(arm, seed):
    return next(r for r in RUNS if r["arm"] == arm and r["seed"] == seed)


def fact(arm, seed):
    return next(r for r in FA["runs"] if r["arm"] == arm and r["seed"] == seed)


def pair(arm, seed):
    return PR["%s-s%d" % (arm, seed)]


S_FULL, S_34 = T["full speedup (re-measured)"], T["34-request speedup (re-measured)"]
A_FULL, B_FULL = T["full search-time confirmed metric"], T["full re-measured metric"]
A_34, B_34 = T["34-request search-time confirmed metric"], T["34-request re-measured metric"]
tok_g = sorted(pair("greedy", s)["tokens"] for s in range(1, 6))
tok_b = sorted(pair("bestofn", s)["tokens"] for s in range(1, 6))
med = lambda v: sorted(v)[len(v) // 2]
O3, O3N, N3 = CT["C1 -O3 vs -O2 (batch 1071478)"], CT["C1 -O3 -march=native vs -O2 (rerun 1071478)"], CT["C1 -O3 -march=native vs -O3 (rerun 1071478)"]
H1, H2 = CT["C2 human patch attempt-1 vs -O2 (batch 1068897)"], CT["C2 human patch attempt-2 vs -O2 (batch 1068897)"]
INERT = CT["inert patch (null check) vs -O2 (batch 1068897)"]
ACm = {k: v for k, v in AC.items() if not k.startswith("_")}
acg = lambda key: ACm[key]
ac_fmt = lambda key: "%s [%s, %s]" % (sg(acg(key)["median_of_per_measurement_process_medians"]), sg(acg(key)["range_of_per_measurement_process_medians"][0]), sg(acg(key)["range_of_per_measurement_process_medians"][1]))
usage_missing = len(ST["token_accounting"]["requests_without_usage_object"])
TA = ST["token_accounting"]
tr_total = sum(v["truncated_replies"] for v in RUNS)
node_of = lambda arm, s: fact(arm, s)["node"]
hours = lambda arm, s: "%.2f" % (fact(arm, s)["job_wallclock_s"] / 3600)
nodes_used = sorted({r["node"] for r in FA["runs"]})
pre = FA["preflight"]
base_c = [r["baseline_ms"] for r in FA["runs"] if r["node"].startswith("xcnc")]
base_d = [r["baseline_ms"] for r in FA["runs"] if r["node"].startswith("xcnd")]
DATA = FA["data"]["identifiers"]
HW_DIR = ROOT / "runs/phase1-final/node_hardware"
HW_REC = sorted(f.stem for f in HW_DIR.glob("*.txt") if "Model name" in f.read_text()) + (["xcnc2"] if "Model name: Intel" in (ROOT / "runs/phase0b-1069564/config_frozen.txt").read_text() else [])
HW_MISS = [n for n in nodes_used if n not in HW_REC]
HW_NOTE = ("all formal nodes Xeon E5-2620 v3, xcnc2 from the Phase 0 log" if not HW_MISS else "recorded for " + ", ".join(HW_REC) + "; not recorded for " + ", ".join(HW_MISS))

BLOCKS = []
add = lambda *a: BLOCKS.append(a)

add("ABS", "We test whether LLM-guided patch search speeds up full-file decode in the Garmin FIT SDK (21.201.0) and whether any gain exceeds repeated independent sampling of the same model. "
           "With deepseek-v4.1-flash we compare a *greedy* chain (each call edits the current best patch) with *best-of-N* (each call starts from stock): 40 HTTP requests per run, five seeds per arm, "
           "plus compiler-flag (C1) and human-patch (C2) controls. A frozen decision rule (alpha = 0.01, at least a 2%% reduction) was calibrated on synthetic pairs: %d/%d false accepts on the null pair, "
           "%d/%d detections at a 4.8%% reduction, %d/%d at 1.965%%. Re-measuring each run's fixed final patch three times, greedy reached a median speedup of %s (range %s–%s) and best-of-N %s (%s–%s); "
           "greedy was higher in all five seed pairs, used more tokens (median %dk versus %dk) but had the higher speedup per token. "
           "*Limits:* best-of-N stays below -O3 (%s) and near the human patches (%s, %s); only greedy exceeds -O3 -march=native (%s). The call budgets are unequal (three greedy runs stopped at 38, 34 and 34 of 40 requests "
           "at the cluster job limit), and the 34-request comparison, which agrees, was added after the full results were seen. With five seeds, one model, one library and arms that differ in several respects, "
           "these exploratory results do not show an advantage of greedy at equal resources and cannot be attributed to selection, feedback or inheritance alone."
    % (P0["null"]["accepted"], P0["null"]["trials"], P0["faster-5-percent"]["accepted"], P0["faster-5-percent"]["trials"], P0["faster-2-percent"]["accepted"], P0["faster-2-percent"]["trials"],
       f3(S_FULL["greedy_median"]), f3(S_FULL["greedy_range"][0]), f3(S_FULL["greedy_range"][1]), f3(S_FULL["bestofn_median"]), f3(S_FULL["bestofn_range"][0]), f3(S_FULL["bestofn_range"][1]),
       round(med(tok_g) / 1000), round(med(tok_b) / 1000), f3(O3["median_speedup"]), f3(H1["median_speedup"]), f3(H2["median_speedup"]), f3(O3N["median_speedup"])))

# 1 ------------------------------------------------------------------------------------------------------------------------------
add("H1", "Problem and method")
add("P", "**Question.** Claims that an LLM inside a search loop finds better code than people or compilers [@romera2024; @novikov2025] usually rest on a few case studies. The course brief asks for the missing control: "
         "the same number of model calls without feedback or selection. On one library we ask whether LLM search speeds up the full decode of stock FIT SDK 21.201.0 [@garminfit], and whether it beats best-of-N at the same number of calls. "
         "Every candidate is a unified diff of `src/`; we report what our modification changed, not a comparison with a vendor product.")
add("P", "**Search.** One call picks one function (of 5,514 indexed, at most 250 lines each): 90%% of draws are proportional to *perf* samples of a 20 s profile of the stock decode, 10%% are uniform. "
         "The model receives the function's text and the stock decode time and returns a replacement body (final `message.content` only). The patch is built, checked (Section 2.3) and timed. "
         "**Greedy** shows the function as it is under the current best patch and continues from an accepted candidate; a rejected call changes nothing. **Best-of-N** (control C3) always shows stock and never sees a score, "
         "an earlier patch or an error. Both arms use the same model (`deepseek-v4.1-flash`, always answered as `deepseek-v4.1-flash-1017`), prompt template, `max_tokens` 32768, sampling code and rank rule, "
         "and a budget of 40 HTTP requests per run: every request sent counts (truncated replies and 502 errors included), a failure before any request is recorded but not counted, a reply cut at the token limit is never a candidate, and there are no hidden retries.")
add("P", "**Rank rule and confirmation.** A candidate is measured once; if its ratio r₁ is below the current record and the measurement is stable it is measured again, R = max(r₁, r₂), and the record is replaced only if R is below it. "
         "This is an *ordering heuristic* for small gains, not the decision rule of Section 2 and not a significance test. Only each run's final patch is a confirmed result: "
         "it is fixed and re-measured three times, independently, under the frozen decision rule. Intermediate steps were never independently confirmed.")
add("P", "**Chronology and environment.** On 3 November we ran a different model (qwen3-coder-next) with a population search and best-of-N (`runs/main/`); on 4 November we changed both model and strategy (greedy). "
         "The two experiments differ in two ways; the earlier model runs are archived and not analysed here, except the compiler and human controls (C1, C2), which involve no model. "
         "Also kept: a model preflight (21 calls, %d tokens; %d/7, %d/7, %d/7 replies truncated at 8192, 16384, 32768 tokens, so `max_tokens` = 32768; one reply at 8192 came from another model, `glm-5.3-flash`, so the returned id is checked), "
         "smoke runs, and an invalid first-batch -O3 -march=native control (rerun used). "
         "Workload: four generated FIT files, %s bytes, %s messages, %s fields, output checksum `%s` (`bench.err`, identical in all runs). Each formal run used one compute node (%s; 24 logical CPUs, Xeon E5-2620 v3, see Section 4), "
         "c++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0, SDK flags `-O2 -std=c++17 -fPIC -fvisibility=hidden` (tools: Release `-O3 -DNDEBUG`), Google Benchmark 1.9.1, `--repeat 10 --repetitions 9`, SDK `--min-time` 0.25 s. "
         "Only ratios are compared across node families."
    % (int(pre["total_tokens_all_levels"]), pre["mt8192"]["truncated"], pre["mt16384"]["truncated"], pre["mt32768"]["truncated"],
       format(DATA["bytes"], ","), format(DATA["messages"], ","), format(DATA["fields"], ","), DATA["checksum"], ", ".join(nodes_used)))

# 2 ------------------------------------------------------------------------------------------------------------------------------
add("H1", "Measurement and calibration")
add("H2", "Decision rule")
add("P", "One measurement runs stock and candidate in the same process (the candidate loaded first in half of the processes), 10 fresh processes × 9 repetitions. The rule reads each process's `candidate_ns` and `reference_ns` (`timings`), "
         "takes ratio = median over processes of median(candidate)/median(reference), and applies an exact two-sided sign-flip test to the ten process-level log ratios (2¹⁰ patterns). "
         "*Faster* means mean log ratio below 0, p < 0.01 (alpha) and ratio ≤ 0.98; *unstable* means a spread of process ratios above 0.25. The unit of analysis is the process-level log ratio; the test assumes the ten processes are independent "
         "and, under no difference, symmetric about 0. Repetitions inside a process are not assumed independent (only their median is used). Thresholds were fixed before any calibration data. "
         "The null run of `CanMehHarness init` was clean in all 10 runs (null ratio %s–%s, on each run's own node)."
    % (f4(min(r["null_ratio"] for r in FA["runs"])), f4(max(r["null_ratio"] for r in FA["runs"]))))
add("H2", "Phase 0 calibration")
add("P", "Synthetic pairs differ only in work units, so the true ratio is known by construction. They were measured with `--repeat 10 --repetitions 9` and each pair's own recorded `--min-time` (about 0.06 s for the main pairs, larger for sweeps; "
         "the SDK uses 0.25 s, so calibration and SDK differ). Main pairs: 100 valid trials (two batches of 50, node xcnc2, Xeon E5-2620 v3); sweep pairs: 20 trials (batch 1 only). {tab:calib} gives the single-measurement outcomes; "
         "bias is the median reported ratio minus the true ratio.")
add("TABLE", dict(id="tab:calib", small=True, spec="lrrrrcrr", widths=[2.3, 2.5, 1.5, 1.7, 1.1, 2.9, 1.9, 1.6],
                  head=["Pair", "Work ref/cand", "min-time", "True ratio", "Trials", "Accepted (95% CI)", "Reported", "Bias"],
                  rows=[[n.replace("-percent", "%"), "%d/%d" % (P0[n]["reference_units"], P0[n]["candidate_units"]), P0[n]["min_time"].rstrip("s"), "%.5f" % P0[n]["true_ratio"], str(P0[n]["trials"]),
                         "%d (%s–%s%%)" % (P0[n]["accepted"], pct(P0[n]["cp95"][0]), pct(P0[n]["cp95"][1])), "%.5f" % P0[n]["median_reported_ratio"], "%+.5f" % P0[n]["bias"]]
                        for n in ["null", "faster-1-percent", "faster-2-percent", "faster-5-percent", "faster-10-percent", "slower-10-percent", "sweep-105", "sweep-110", "sweep-200", "sweep-400"]],
                  rule_before=[6],
                  caption="Phase 0, single-measurement decisions of the frozen rule. min-time in seconds. Reported = median reported ratio; bias = reported − true ratio. CI: 95%% Clopper–Pearson [@clopper1934]. Above the rule: main pairs (100 trials); below: sweep pairs (20 trials, batch 1). "
                          "Source: `runs/phase0b-1069564/final/rule_rows.jsonl`."))
add("P", "The null pair accepted %d of %d (95%% upper bound %s%%): alpha = 1%% is the test's threshold, not a measured rate, and 100 null trials cannot show a false-accept rate below 1%%. "
         "The weakest tested effect accepted in at least 90%% of trials is the 4.8%% reduction (%d/%d). The 2%% pair (true reduction 1.965%%, just below the 2%% gate) was accepted %d/%d times, which reflects an effect near the magnitude gate "
         "together with measurement fluctuation; noise cannot be excluded. Bias was at most %s of the true ratio at the main pairs. The sweep pairs (true ratios 1.05–4.00) check that the reported ratio scales with the work count "
         "(bias at most %s, %s%% at 4.0). In the 12-pair self-check `broken-digest` was refused at stage `correctness` and `shared-install-name` at stage `load`. "
         "The calibration is of the *final decision rule*, not of the greedy ranking heuristic, and it scales a whole synthetic workload, whereas a real patch speeds up one part of a decode."
    % (P0["null"]["accepted"], P0["null"]["trials"], pct(P0["null"]["cp95"][1]), P0["faster-5-percent"]["accepted"], P0["faster-5-percent"]["trials"], P0["faster-2-percent"]["accepted"], P0["faster-2-percent"]["trials"],
       "%.2f%%" % (100 * max(abs(P0[n]["bias"]) / P0[n]["true_ratio"] for n in ["null", "faster-1-percent", "faster-2-percent", "faster-5-percent", "faster-10-percent", "slower-10-percent"])),
       "%.3f" % max(abs(P0[n]["bias"]) for n in ["sweep-105", "sweep-110", "sweep-200", "sweep-400"]), "%.2f" % (100 * abs(P0["sweep-400"]["bias"]) / 4.0)))
add("P", "**Repetition independence.** Lag-1 autocorrelation of each process's 9-value `candidate_ns` series (standard error about 0.33 per series), recomputed from raw timings by `scripts/autocorr_report.py` (it reproduces the rule's stored values to 1e-14). "
         "Median across a measurement's processes, summarised as median [range of those medians] over measurements: calibration main pairs %s (600 measurements); SDK inert patch %s (6); SDK search candidates %s (%d); fixed final patches %s (30). "
         "Calibration is slightly negative, SDK slightly positive: SDK repetitions are not known to be independent, which the rule does not assume."
    % (ac_fmt("calibration main pairs (6 pairs, both batches)"), ac_fmt("SDK inert patch (stock vs no-op patch)"), ac_fmt("SDK DeepSeek search candidates (all measurements)"),
       ACm["SDK DeepSeek search candidates (all measurements)"]["n_measurements"], ac_fmt("SDK fixed final patches (3 re-measurements each, 10 runs)")))
add("H2", "Correctness checks and the inert patch")
add("P", "Before timing, `CanMehBench` requires that (i) both libraries fold the decoded values to the same 64-bit digest, unchanged on a second decode; (ii) a *profile digest* agrees, which calls `Profile::GetMesg` for every message number 0–65535 and "
         "`GetFieldIndex`/`GetField` for every field number 0–255 (nine probes for absent messages); and (iii) neither library works on a second thread (processor over wall time at most 1.15), which rejects candidates that start threads but does not test concurrent callers. "
         "These checks do not prove semantic equivalence on all inputs or platforms. An inert patch spliced into the SDK and evaluated by hand gave a median speedup of %s (5 measurements, 0/5 accepted), so speedups near 1.00 carry no information." % f4(INERT["median_speedup"]))

# 3 ------------------------------------------------------------------------------------------------------------------------------
add("H1", "Results")
add("P", "**Two analyses, not one experiment.** *Full runs* are what was executed. All best-of-N runs sent 40 requests; greedy seeds 1 and 2 sent 40 (seed 1 stopped at its 9,600 s deadline after 39 requests and was completed by a resume job on another node, tokens included); greedy seeds 3, 4 and 5 stopped at their search deadline (9,300 s, set to fit the three-hour job limit) after 38, 34 and 34 requests. "
         "The *34-request analysis* is **post hoc**: for each run, the best patch under the then-current ranking within its first 34 HTTP requests. The value 34 is the shortest run's request count, taken after the full results were known; "
         "it was not chosen by performance but was not specified in advance. Six of the ten 34-request patches equal the final patch and reuse its re-measurement; four differ and were re-measured three times each. "
         "The 20 analysis entries (10 final, 10 at 34 requests) therefore rest on 14 distinct patches, and all 20 passed the frozen rule in 3 of 3 re-measurements.")
rows = []
for s in range(1, 6):
    for arm, lab in (("greedy", "greedy"), ("bestofn", "best-of-N")):
        r, f, p = runrow(arm, s), fact(arm, s), pair(arm, s)
        rows.append([str(s) if arm == "greedy" else "", lab, f["node"] + ("→" + f["resume"]["node"] if f.get("resume") else ""), str(p["attempts"]), hours(arm, s), "%d" % round(p["tokens"] / 1000),
                     str(r["truncated_replies"]), f3(p["speed"]), e7(p["A"]), e7(p["B"])])
add("TABLE", dict(id="tab:runs", small=True, spec="llllrrrrrr", widths=[0.9, 2.4, 2.4, 1.0, 1.3, 1.4, 1.3, 1.7, 1.6, 1.6],
                  head=["Seed", "Arm", "Node", "Req.", "Wall (h)", "Tok. (k)", "Trunc.", "Speedup", "Metric A", "Metric B"], rows=rows,
                  caption="Full runs, one node each. Req. = HTTP requests sent; Wall = job start to end (init, null check, search, final re-measurements); Tok. = all tokens spent (seed-1 greedy includes its resume call); "
                          "Trunc. = replies cut at 32,768 tokens; Speedup = median of three independent re-measurements of the fixed final patch. Metric = (speedup − 1)/tokens × 10⁻⁷, A with the best search-time confirmed speedup "
                          "(two measurements, both passing the frozen rule), B with the re-measured speedup. Source: `runs/phase1-final/recomputed_stats.md`."))
add("FIG", dict(id="fig:main", path="report/main_figure.pdf", png="report/main_figure.png",
                caption="Per-seed results (one marker per seed; left to right = seeds 1–5), median (thick bar) and full range. A: full runs as executed. B: post hoc, best patch within the first 34 requests. "
                        "C: metric B on both bases (filled: full; open: first 34 requests). All plotted values passed the frozen rule in 3/3 re-measurements. Dashed/dotted lines: C1 controls (separate batch and node)."))
add("P", "**Speedup.** Median (range) over five seeds, full runs: greedy %s, best-of-N %s; first 34 requests (post hoc): greedy %s, best-of-N %s. Greedy was higher in %d of 5 paired seeds in both analyses. "
         "Exploratory exact two-sided tests (chosen after the data were seen, nothing was pre-specified): permutation test of the difference of medians p = %.3f (both analyses), Mann–Whitney [@mann1947] p = %.3f (full) and %.3f (34 requests), sign test p = %.4f. "
         "With five seeds per arm these p-values are coarse (the smallest possible Mann–Whitney p is 0.008)."
    % (rng3(S_FULL, "greedy"), rng3(S_FULL, "bestofn"), rng3(S_34, "greedy"), rng3(S_34, "bestofn"), S_FULL["greedy_higher_pairs"], S_FULL["perm_median_p"], S_FULL["mannwhitney_p"], S_34["mannwhitney_p"], S_FULL["sign_p"]))
add("P", "**Tokens.** Full runs count all tokens of every request sent; the 34-request analysis counts the first 34 requests' cumulative tokens. Truncated replies (%d requests, %s tokens) are counted. "
         "%d requests returned HTTP 502 without a usage object: their consumption is unknown and not included, so token totals (%s over all runs) may underestimate cost and overstate efficiency. "
         "The course quotient is (best_confirmed_speedup − 1)/total_tokens from the last row of `credits.csv`; our rank-mode `credits.csv` has no confirmed column and `summary.json` keeps an unused default (1.0), "
         "so metric A is computed from `results.jsonl`: the best speedup among candidates whose two measurements both passed the frozen rule (it equals the search's best ranked value in all 10 runs, which is not itself used as the confirmed value). "
         "Metric B uses the independent re-measurement; they differ by under 2%% and the logs are unchanged. "
         "Median metric A, full runs: greedy %s vs best-of-N %s ×10⁻⁷ (greedy higher in %d/5 seeds; permutation p = %.3f, Mann–Whitney p = %.3f); first 34 requests: %s vs %s. Metric B agrees; all exploratory."
    % (TA["truncated_requests"], format(TA["truncated_total_tokens"], ","), usage_missing, format(TA["total_tokens_all_runs"], ","),
       e7(A_FULL["greedy_median"]), e7(A_FULL["bestofn_median"]), A_FULL["greedy_higher_pairs"], A_FULL["perm_median_p"], A_FULL["mannwhitney_p"], e7(A_34["greedy_median"]), e7(A_34["bestofn_median"])))
add("P", "**Controls.** C1 (compiler), C2 (human) and the inert patch are five repeated measurements each on node xcnd24, from a different batch than the DeepSeek runs ({tab:ctl}). "
         "The -O3 gain (speedup − 1) is %s of the greedy median gain; -O3 -march=native adds only %s over -O3, below the 2%% gate (0/5 accepted). C3 is the best-of-N arm and C4 the five seeds per arm. "
         "**C2 (human-directed, AI-assisted).** Attempt 1 replaces the linear scan in `Profile::GetMesg` by a 65,536-entry table built once by a function-local static object; attempt 2 adds a table for `Profile::GetFieldIndex` (message type × 256 field numbers, built on first call). "
         "Both are likely faster because these lookups run for every message and field of the decode. They were made by the author with AI assistance (Claude Code); no per-line authorship is recorded. "
         "The README asks for a timed hour before looking at any search output. **There is no stopwatch or timer record.** File modification times in the C2 directory span %s–%s on 2 November (%d minutes); the earliest search results file in `runs/` is %s on 3 November. This is consistent with, but does not verify, a timed hour before any search output; **the author-reported time is not available to us and is not stated.**")
add("TABLE", dict(id="tab:ctl", small=True, spec="lrrr", widths=[6.0, 3.3, 3.0, 2.0], head=["Control (vs stock -O2 unless stated)", "Speedup, median of 5", "Range", "Accepted"],
                  rows=[["C1 -O3", f3(O3["median_speedup"]), "%s–%s" % tuple(f3(x) for x in O3["range_speedup"]), "5/5"],
                        ["C1 -O3 -march=native", f3(O3N["median_speedup"]), "%s–%s" % tuple(f3(x) for x in O3N["range_speedup"]), "5/5"],
                        ["C1 -O3 -march=native vs -O3", f3(N3["median_speedup"]), "%s–%s" % tuple(f3(x) for x in N3["range_speedup"]), "0/5"],
                        ["C2 human patch, attempt 1", f3(H1["median_speedup"]), "%s–%s" % tuple(f3(x) for x in H1["range_speedup"]), "5/5"],
                        ["C2 human patch, attempt 2", f3(H2["median_speedup"]), "%s–%s" % tuple(f3(x) for x in H2["range_speedup"]), "5/5"],
                        ],
                  caption="Non-LLM references; five repeated measurements each (not independent seeds), node xcnd24. Source: `runs/phase1-final/controls.csv`."))
add("P", "**What the search patches are.** All five best-of-N winners rewrite `Profile::GetMesg` (a table lookup, the idea of human attempt 1); their speedups (%s–%s) are close to attempt 1 (%s). "
         "`Profile::GetMesg` and `FieldBase::FieldBase` (copy constructor with member-initialiser list) were accepted in every greedy chain (7 to 12 accepted steps each). The submitted patch series is the median-seed greedy chain (seed 3), explained patch by patch in `patches/`; the other chains are experiment records, and each run's final patch has a short description in `experiments/patches/final-cumulative/README.md`. In the seed-3 chain "
         "four steps gave most of the search-time gain (`GetMesg` 6.1%%, `FieldBase` copy 4.4%%, `GetFieldIndex` 1.5%%, `AddField` 1.4%%) and six were below 0.3%%; none was independently confirmed."
    % (f3(S_FULL["bestofn_range"][0]), f3(S_FULL["bestofn_range"][1]), f3(H1["median_speedup"])))

# 4 ------------------------------------------------------------------------------------------------------------------------------
add("H1", "Limitations and conclusion")
add("P", "**Budget and analysis.** Unequal budgets and the post hoc 34-request analysis are described in Section 3. "
         "All 10 runs and all failures are kept (%d truncated requests are in the token counts, %d HTTP-502 requests have unknown token use and are not; compile, correctness and crash failures are in each `results.jsonl`)."
    % (TA["truncated_requests"], usage_missing))
add("P", "**Measurement.** Calibration used a synthetic, stationary workload on one node with min-time about 0.06 s; the SDK was measured with 0.25 s on two node families, so the calibrated detection rates (reliable near a 5%% change, partial at 2%%) transfer only loosely. Ratios reduce, but do not remove, node differences: the same CPU model string gives about %d ms on xcnc and %d ms on xcnd, and we did not test whether a patch's effect depends on the node. "
         "CPU model recorded after the runs (%s)."
    % (round(sum(base_c) / len(base_c)), round(sum(base_d) / len(base_d)), HW_NOTE))
add("P", "**Correctness.** We ran only the harness checks of Section 2.3. Lookup tables built lazily behind a plain `bool` appear in four of the five best-of-N winners (seeds 1, 3, 4, 5; seed 2 initialises through a function-local static, which C++11 makes thread-safe), "
         "and the seed-3 greedy chain also caches the last queried message in mutable statics in `GetFieldIndex`; concurrent callers could race on this unsynchronised shared state. The human patches use function-local static objects and do not. "
         "`FieldBase::GetValue` in that chain assumes a little-endian host. Nothing was tested beyond single-threaded benchmark inputs; no patch is claimed ready for upstream.")
add("P", "**Conclusion.** *Observed:* greedy chains reached a higher final speedup than best-of-N in all five seeds (median %s vs %s), with higher token cost per run but a higher median speedup per token; best-of-N never exceeded -O3, and only greedy exceeded -O3 -march=native. "
         "*Not established:* that greedy is better at equal resources in general; that the gap comes from selection, feedback or inheritance (the arms differ in start point, memory and token use; no ablation was run); "
         "or that the patches are correct beyond the checks listed."
    % (f3(S_FULL["greedy_median"]), f3(S_FULL["bestofn_median"])))
add("P", "**AI assistance.** Code, scripts, this report and patch commit messages were prepared with Claude Code (Anthropic) under the author's direction, who remains responsible for the claims. The patches of the automated search were generated by deepseek-v4.1-flash; "
         "the C2 patches are human-directed and AI-assisted. Build and run commands, file index and open items: `DELIVERY.md`.")

BIB = {
    "romera2024": "@article{romera2024,\n  author = {Romera-Paredes, Bernardino and others},\n  title = {Mathematical discoveries from program search with large language models},\n  journal = {Nature},\n  volume = {625},\n  pages = {468--475},\n  year = {2024}\n}",
    "novikov2025": "@techreport{novikov2025,\n  author = {Novikov, Alexander and others},\n  title = {{AlphaEvolve}: A coding agent for scientific and algorithmic discovery},\n  institution = {Google DeepMind},\n  year = {2025}\n}",
    "garminfit": "@misc{garminfit,\n  author = {{Garmin International}},\n  title = {{FIT} {SDK}, release 21.201.0},\n  howpublished = {\\url{https://developer.garmin.com/fit/}},\n  note = {Fetched at configure time; not redistributed here}\n}",
    "clopper1934": "@article{clopper1934,\n  author = {Clopper, C. J. and Pearson, E. S.},\n  title = {The use of confidence or fiducial limits illustrated in the case of the binomial},\n  journal = {Biometrika},\n  volume = {26},\n  pages = {404--413},\n  year = {1934}\n}",
    "mann1947": "@article{mann1947,\n  author = {Mann, H. B. and Whitney, D. R.},\n  title = {On a test of whether one of two random variables is stochastically larger than the other},\n  journal = {Annals of Mathematical Statistics},\n  volume = {18},\n  pages = {50--60},\n  year = {1947}\n}",
}
REFS = ["Garmin International. *FIT SDK*, release 21.201.0. https://developer.garmin.com/fit/ (fetched at configure time; not redistributed here).",
        "Romera-Paredes, B. et al. Mathematical discoveries from program search with large language models. *Nature* 625, 468–475 (2024).",
        "Novikov, A. et al. AlphaEvolve: a coding agent for scientific and algorithmic discovery. Google DeepMind (2025).",
        "Clopper, C. J. and Pearson, E. S. The use of confidence or fiducial limits illustrated in the case of the binomial. *Biometrika* 26, 404–413 (1934).",
        "Mann, H. B. and Whitney, D. R. On a test of whether one of two random variables is stochastically larger than the other. *Ann. Math. Stat.* 18, 50–60 (1947)."]
CITE_ORDER = ["garminfit", "romera2024", "novikov2025", "clopper1934", "mann1947"]

# fix the controls paragraph numbers (needs O3 vs greedy median): computed here to keep prose readable
for i, b in enumerate(BLOCKS):
    if b[0] == "P" and b[1].startswith("**Controls.**"):
        share = (O3["median_speedup"] - 1) / (S_FULL["greedy_median"] - 1)
        _txt = b[1] % ("%.0f%%" % (100 * share), "%.3f" % N3["median_speedup"], C2["first_file"][0][11:16], C2["last_file"][0][11:16], round(C2["span_min"]), C2["earliest_search_results_file"][11:16])
        _a, _b = _txt.split("**C2 (human-directed, AI-assisted).**")
        BLOCKS[i] = ("P", _a.rstrip())
        BLOCKS.insert(i + 1, ("P", "**C2 (human-directed, AI-assisted).**" + _b))
        break

def _fix(b):
    if b[0] in ("P", "ABS"):
        return (b[0], b[1].replace("%%", "%"))
    if b[0] == "TABLE":
        d = dict(b[1]); d["caption"] = d["caption"].replace("%%", "%"); return (b[0], d)
    return b


BLOCKS = [_fix(b) for b in BLOCKS]
# ============================================================================================================================ LaTeX
UNI = {"×": r"$\times$", "−": r"$-$", "≤": r"$\le$", "≥": r"$\ge$", "≈": r"$\approx$", "α": r"$\alpha$", "→": r"$\rightarrow$", "₁": r"$_1$", "₂": r"$_2$", "⁻": r"$^{-}$", "⁷": r"$^{7}$",
       "¹": r"$^{1}$", "⁰": r"$^{0}$", "²": r"$^{2}$", "–": "--", "—": "---", "’": "'", "·": r"$\cdot$"}


def tex_inline(t):
    out, i = [], 0
    tokens = re.split(r"(\*\*.+?\*\*|\*.+?\*|`.+?`|\[@[^\]]+\]|\{(?:tab|fig):[a-z0-9]+\})", t)
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith("**"):
            out.append(r"\textbf{%s}" % tex_inline(tok[2:-2]))
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            out.append(r"\emph{%s}" % tex_inline(tok[1:-1]))
        elif tok.startswith("`") and "/" in tok and " " not in tok and "%" not in tok and "::" not in tok:
            out.append(r"\path{%s}" % tok[1:-1])
        elif tok.startswith("`"):
            s = tok[1:-1]
            s = "".join(UNI.get(c, c) for c in s)
            for a, b in (("\\", r"\textbackslash{}"), ("_", r"\_"), ("%", r"\%"), ("&", r"\&"), ("#", r"\#"), ("{", r"\{"), ("}", r"\}"), ("$", r"\$"), ("^", r"\^{}"), ("~", r"\~{}")):
                s = s.replace(a, b) if a != "\\" else s.replace(a, b)
            out.append(r"\texttt{%s}" % s.replace("→", "->"))
        elif tok.startswith("[@"):
            out.append(r"\cite{%s}" % tok[2:-1].replace("; @", ","))
        elif tok.startswith("{tab:") or tok.startswith("{fig:"):
            kind = "Table" if tok.startswith("{tab") else "Figure"
            out.append(r"%s~\ref{%s}" % (kind, tok[1:-1]))
        else:
            s = tok
            for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("$", r"\$"), ("~", r"\textasciitilde{}")):
                s = s.replace(a, b)
            s = s.replace("⁻⁷", "$^{-7}$").replace("¹⁰", "$^{10}$")
            s = "".join(UNI.get(c, c) for c in s)
            out.append(s)
    return "".join(out)


def tex_table(d):
    spec = d.get("spec_override") or d["spec"]
    L = [r"\begin{table}[t]", r"\centering", r"\small" if d.get("small") else "", r"\setlength{\tabcolsep}{3.5pt}", r"\begin{tabular}{%s}" % spec, r"\toprule",
         " & ".join(tex_inline(h) for h in d["head"]) + r" \\", r"\midrule"]
    for i, r in enumerate(d["rows"]):
        if i in d.get("rule_before", []):
            L.append(r"\midrule")
        L.append(" & ".join(tex_inline(c) for c in r) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}", r"\caption{%s}" % tex_inline(d["caption"]), r"\label{%s}" % d["id"], r"\end{table}"]
    return "\n".join(x for x in L if x != "")


def build_tex():
    L = [r"\documentclass[10pt,a4paper]{article}", r"\usepackage[T1]{fontenc}", r"\usepackage[utf8]{inputenc}", r"\usepackage{mathptmx}", r"\usepackage{microtype}",
         r"\usepackage[margin=2.3cm]{geometry}", r"\usepackage{booktabs}", r"\usepackage{graphicx}", r"\usepackage[font=small,labelfont=bf]{caption}", r"\usepackage{xcolor}",
         r"\usepackage[hidelinks]{hyperref}", r"\usepackage{url}", r"\urlstyle{tt}", r"\usepackage{titlesec}", r"\titlespacing*{\section}{0pt}{9pt}{3pt}", r"\titlespacing*{\subsection}{0pt}{6pt}{2pt}",
         r"\setlength{\parindent}{1.2em}", r"\setlength{\parskip}{0pt}", r"\clubpenalty=10000", r"\widowpenalty=10000", r"\raggedbottom",
         r"\title{\vspace{-1.2cm}Does LLM-guided patch search speed up the Garmin FIT SDK decoder?\\\large A greedy-chain versus best-of-$N$ study}",
         r"\author{Zhou Ziang (A0359536N)\\CS6219 project}", r"\date{November 2026}", r"\begin{document}", r"\maketitle\vspace{-0.6cm}"]
    for b in BLOCKS:
        k = b[0]
        if k == "ABS":
            L += [r"\begin{abstract}\noindent", tex_inline(b[1]), r"\end{abstract}"]
        elif k == "H1":
            L.append(r"\section{%s}" % tex_inline(b[1]))
        elif k == "H2":
            L.append(r"\subsection{%s}" % tex_inline(b[1]))
        elif k == "P":
            L.append(tex_inline(b[1]) + "\n")
        elif k == "TABLE":
            L.append(tex_table(b[1]))
        elif k == "FIG":
            d = b[1]
            L += [r"\begin{figure}[t]", r"\centering", r"\includegraphics[width=\textwidth]{%s}" % Path(d["path"]).name, r"\caption{%s}" % tex_inline(d["caption"]), r"\label{%s}" % d["id"], r"\end{figure}"]
    L += [r"\bibliographystyle{plain}", r"\bibliography{references}", r"\end{document}"]
    return "\n".join(L) + "\n"


(OUT).mkdir(parents=True, exist_ok=True)
(OUT / "report.tex").write_text(build_tex())
(OUT / "references.bib").write_text("\n\n".join(BIB[k] for k in CITE_ORDER) + "\n")
import shutil
print("wrote report.tex, references.bib")

# ============================================================================================================================ PDF fallback (reportlab)
if "--no-pdf" in sys.argv:
    sys.exit(0)
import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

FONTS = Path(matplotlib.get_data_path()) / "fonts/ttf"
for n, f in (("Body", "STIXGeneral.ttf"), ("Body-B", "STIXGeneralBol.ttf"), ("Body-I", "STIXGeneralItalic.ttf"), ("Body-BI", "STIXGeneralBolIta.ttf"), ("Mono", "DejaVuSansMono.ttf")):
    pdfmetrics.registerFont(TTFont(n, str(FONTS / f)))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-B", italic="Body-I", boldItalic="Body-BI")
FS = 10.0
base = ParagraphStyle("b", fontName="Body", fontSize=FS, leading=12.0, alignment=TA_JUSTIFY, firstLineIndent=12, spaceAfter=0)
h1 = ParagraphStyle("h1", parent=base, fontName="Body-B", fontSize=12, leading=14, firstLineIndent=0, spaceBefore=6, spaceAfter=2, alignment=0, keepWithNext=1)
h2 = ParagraphStyle("h2", parent=h1, fontSize=10.5, leading=12.5, spaceBefore=3, spaceAfter=1)
ttl = ParagraphStyle("t", parent=base, fontName="Body-B", fontSize=15, leading=18, alignment=TA_CENTER, firstLineIndent=0, spaceAfter=3)
auth = ParagraphStyle("a", parent=base, fontSize=11, leading=13.5, alignment=TA_CENTER, firstLineIndent=0, spaceAfter=6)
absst = ParagraphStyle("abs", parent=base, fontSize=9.2, leading=11.0, firstLineIndent=0, leftIndent=18, rightIndent=18, spaceAfter=4)
cap = ParagraphStyle("c", parent=base, fontSize=9, leading=10.6, firstLineIndent=0, spaceAfter=5, spaceBefore=2)
cell = ParagraphStyle("cell", parent=base, fontSize=8.6, leading=10, firstLineIndent=0, alignment=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Body-B")
refst = ParagraphStyle("r", parent=base, fontSize=9.4, leading=11.2, firstLineIndent=0, leftIndent=16, alignment=0, spaceAfter=2)
TABNO, FIGNO = {}, {}
for b in BLOCKS:
    if b[0] == "TABLE":
        TABNO[b[1]["id"]] = len(TABNO) + 1
    if b[0] == "FIG":
        FIGNO[b[1]["id"]] = len(FIGNO) + 1
CITENO = {k: i + 1 for i, k in enumerate(CITE_ORDER)}


SUBSUP = {"₁": "<sub>1</sub>", "₂": "<sub>2</sub>", "⁻⁷": "<super>-7</super>", "²¹⁰": "<super>10</super>", "¹⁰": "<super>10</super>"}


def rl_inline(t):
    def esc(s):
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        for k, v in sorted(SUBSUP.items(), key=lambda kv: -len(kv[0])):
            s = s.replace(k, v)
        return s
    out = []
    for tok in re.split(r"(\*\*.+?\*\*|\*.+?\*|`.+?`|\[@[^\]]+\]|\{(?:tab|fig):[a-z0-9]+\})", t):
        if not tok:
            continue
        if tok.startswith("**"):
            out.append("<b>%s</b>" % rl_inline(tok[2:-2]))
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            out.append("<i>%s</i>" % rl_inline(tok[1:-1]))
        elif tok.startswith("`"):
            out.append("<font name='Mono' size='8.4'>%s</font>" % esc(tok[1:-1]))
        elif tok.startswith("[@"):
            out.append("[%s]" % ", ".join(str(CITENO[k]) for k in tok[2:-1].replace("; @", ",").split(",")))
        elif tok.startswith("{tab:"):
            out.append("Table %d" % TABNO[tok[1:-1]])
        elif tok.startswith("{fig:"):
            out.append("Figure %d" % FIGNO[tok[1:-1]])
        else:
            out.append(esc(tok))
    return "".join(out)


def rl_table(d):
    rows = [[Paragraph(rl_inline(h), cellb) for h in d["head"]]] + [[Paragraph(rl_inline(c), cell) for c in r] for r in d["rows"]]
    W = A4[0] - 4.6 * cm
    n = len(d["head"])
    cw = [w * cm for w in d["widths"]] if d.get("widths") else None
    if cw:
        sc = min(1.0, W / sum(cw))
        cw = [w * sc for w in cw]
    t = Table(rows, colWidths=cw, repeatRows=1, hAlign="CENTER")
    st_ = [("LINEABOVE", (0, 0), (-1, 0), 1.0, colors.black), ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black), ("LINEBELOW", (0, -1), (-1, -1), 1.0, colors.black),
           ("TOPPADDING", (0, 0), (-1, -1), 1.3), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.3), ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]
    for i in d.get("rule_before", []):
        st_.append(("LINEABOVE", (0, i + 1), (-1, i + 1), 0.5, colors.black))
    t.setStyle(TableStyle(st_))
    return KeepTogether([t, Paragraph("<b>Table %d.</b> %s" % (TABNO[d["id"]], rl_inline(d["caption"])), cap)])


story = [Paragraph("Does LLM-guided patch search speed up the Garmin FIT SDK decoder?<br/>A greedy-chain versus best-of-N study", ttl),
         Paragraph("Zhou Ziang (A0359536N)<br/>CS6219 project · November 2026", auth)]
for b in BLOCKS:
    k = b[0]
    if k == "ABS":
        story += [Paragraph("<b>Abstract</b>", ParagraphStyle("ah", parent=absst, alignment=TA_CENTER, spaceAfter=2)), Paragraph(rl_inline(b[1]), absst)]
    elif k == "H1":
        story.append(Paragraph("%d&nbsp;&nbsp;%s" % (sum(1 for x in story if getattr(x, "style", None) is h1) + 1, rl_inline(b[1])), h1))
    elif k == "H2":
        cnt1 = sum(1 for x in story if getattr(x, "style", None) is h1)
        cnt2 = 1 + sum(1 for x in story[max(i for i, x in enumerate(story) if getattr(x, "style", None) is h1):] if getattr(x, "style", None) is h2)
        story.append(Paragraph("%d.%d&nbsp;&nbsp;%s" % (cnt1, cnt2, rl_inline(b[1])), h2))
    elif k == "P":
        story.append(Paragraph(rl_inline(b[1]), base))
    elif k == "TABLE":
        story += [Spacer(1, 3), rl_table(b[1])]
    elif k == "FIG":
        d = b[1]
        W = A4[0] - 4.6 * cm
        im = Image(str(ROOT / d["png"]), width=W, height=W * 825 / 2010)
        story += [Spacer(1, 3), KeepTogether([im, Paragraph("<b>Figure %d.</b> %s" % (FIGNO[d["id"]], rl_inline(d["caption"])), cap)])]
story.append(Paragraph("References", h1))
for i, r in enumerate(REFS):
    story.append(Paragraph("[%d]&nbsp;&nbsp;%s" % (i + 1, rl_inline(r)), refst))


def footer(c, doc):
    c.saveState()
    c.setFont("Body", 9)
    c.drawCentredString(A4[0] / 2, 1.2 * cm, str(doc.page))
    c.restoreState()


pdf = ROOT / "Report.pdf"
doc = SimpleDocTemplate(str(pdf), pagesize=A4, leftMargin=2.3 * cm, rightMargin=2.3 * cm, topMargin=2.0 * cm, bottomMargin=2.0 * cm,
                        title="Greedy chain vs best-of-N LLM patch search on the FIT SDK decoder", author="Zhou Ziang")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(pdf)
