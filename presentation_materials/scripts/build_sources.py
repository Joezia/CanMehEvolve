#!/usr/bin/env python3
"""sources.csv: every important number or conclusion -> the raw files, fields and the computation; values are read from the generated tables so they cannot drift."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from docs_lib import *
CS = {r["config"]: r for r in tab("config_summary.csv")}; fp = {r["group"]: r for r in tab("fpr_summary.csv")}; cal = {r["pair"]: r for r in tab("calibration_pairs.csv")}
ns = jt("null_search_summary.json"); ss = jt("stacking_summary.json"); cs = tab("controls_summary.csv"); tests = tab("within_model_tests.csv"); meta = jt("stock_classification_meta.json")
rows = []
def add(item, value, files, fields, comp, script): rows.append({"item": item, "value": value, "raw_files": files, "fields": fields, "computation": comp, "script": script})
# data
add("data bytes / messages / fields / checksum", "907007 / 34251 / 428714 / 92bebfd7f8978fc8", "runs/round2/runs/ds-population-s1/bench.err; runs/phase1-final/run_facts.json", "bench.err line 'the reference library read ...'", "copied", "build_environment.py")
add("regions indexed; with samples", "5514; 76-82 (I3 runs)", "runs/round2/runs/*/profile_samples.json", "values > 0", "count", "build_environment.py / build_regions.py")
add("baseline decode ms by node class", "xcnc ~358-360; xcnd ~480", "runs/*/run.json", "meta.baseline_ms", "see tables/run_baselines_and_parameters.csv", "build_environment.py")
# calibration
for p in ("null", "faster-1-percent", "faster-2-percent", "faster-5-percent", "faster-10-percent", "slower-10-percent"):
    r = cal[p]; add(f"calibration {p}: judged faster / valid, 95% CP", f"{r['judged_faster']}/{r['valid_trials']}; [{100*float(r['cp95_lo']):.3f}%, {100*float(r['cp95_hi']):.3f}%]; true {float(r['true_ratio_exact']):.5f}; median reported {float(r['median_reported_ratio']):.5f}",
                    "runs/phase0-1068829/trials/<pair>/t*.json; runs/phase0b-1069564/trials/<pair>/t*.json; runs/phase0-1068829/calibration.json", "timings.process[*].candidate_ns/reference_ns; reference_units, candidate_units", "pm_lib.rule() replay; k/n; exact Clopper-Pearson; true = candidate_units/reference_units", "build_calibration.py")
add("weakest tested effect with >=90% detection", "faster-5-percent (true reduction 4.765%, 99/100)", "same as above", "rate per pair", "min true reduction among pairs with rate >= 0.9", "build_calibration.py")
add("calibration replay agreement with stored decisions", "0 mismatches of 680 valid trials (681 files, 1 unreadable)", "runs/phase0b-1069564/final/rule_rows.jsonl", "faster, ratio, p_value", "compare replay vs stored", "build_calibration.py (tables/calibration_checks.json)")
add("two wrong calibration pairs", "broken-digest rejected at correctness; shared-install-name at load", "runs/phase0-1068829/calibration.json", "pairs[].stage", "copied", "build_calibration.py")
# FPR
for g in ("Synthetic null, all", "Synthetic null, extra batches, xcnd", "SDK inert, all batches, xcnc", "SDK inert, all batches, xcnd", "SDK inert, all batches, both classes"):
    r = fp[g]; add(f"false accepts: {g}", f"{r['false_accepts']}/{r['valid_measurements']}; upper {100*float(r['cp95_hi']):.3f}%; p<0.01 any direction {r['p_below_alpha_any_direction']}; blocked by 2% gate {r['p_pass_and_direction_ok_but_blocked_by_2pct_gate']}",
                    "runs/phase0*/trials/null; runs/round2/fpr/null-*/trials; runs/followup/sdk-inert-*/evaluate-inert; runs/round2/fpr/sdk-inert-*/evaluate-inert", "timings", "rule replay per measurement; exact Clopper-Pearson", "build_fpr.py")
add("no-op machine code check", "17/17 .text identical (inert patch + 16 null-search candidates)", "runs/round2/fpr/noop-verification-*/noop_verification.json", "results[].text_identical_to_stock", "count", "(existing job output)")
add("lag-1 autocorrelation definition and summaries", "synthetic null median -0.111; SDK xcnc 0.013; xcnd 0.150; search measurements 0.027", "timings.process[*].candidate_ns", "9-point series per process", "lag-1 per process, median over 10 processes = per-measurement value; median/range over measurements", "pm_lib.acf1; build_fpr.py; build_environment.py")
# null search
add("null search: updates, false progress, max single step", f"{ns['total_updates']} updates; median {ns['false_progress_median']:.3f}%, max {ns['false_progress_max']:.3f}%; max step {ns['max_single_update_pct']:.3f}%", "runs/followup/null-search-*/steps.jsonl, measurements/a*.m1/m2.json", "timings", "rank-rule replay: update if r1 stable and < record, r2 stable, R=max < record", "build_nullsearch.py")
add("real greedy updates compared", f"{ns['real_greedy_steps']} updates; <=0.063%: {ns['real_steps_leq_max_null_step']}; <=0.2%: {ns['real_steps_leq_0.2pct']}", "runs/deepseek/greedy-s*/summary.json; runs/followup/resume-greedy-s*/summary.json", "rank_updates[].R, previous_R", "100*(1-R/previous_R)", "build_nullsearch.py")
# controls
for r in cs:
    if r["valid_comparison"] == "True": add(f"{r['control']} {r['comparison']} ({r['batch']})", f"median speedup {float(r['median_speedup']):.4f}; range [{float(r['speedup_min']):.4f}, {float(r['speedup_max']):.4f}]; pass {r['passes_rule']}/{r['n_measurements']}; {r['node']}", "runs/controls-1068897, runs/controls-native-1071478 (m*.json)", "timings", "rule replay; median of 5 measurements", "build_controls.py")
# configs
for c, r in CS.items():
    add(f"{c}: independent re-measured speedup (median [min, max])", f"{float(r['remeasured_speedup_median']):.4f} [{float(r['remeasured_speedup_min']):.4f}, {float(r['remeasured_speedup_max']):.4f}]", "runs/**/evaluate-best/m*.json (or final/evaluate-best)", "timings", "rule replay per measurement; speedup = 1/median ratio of 3; median over 5 seeds", "build_runs.py, build_compare.py")
    add(f"{c}: total tokens (median)", f"{float(r['total_tokens_median']):.0f}", "runs/**/summary.json (+ resume summaries)", "prompt_tokens, completion_tokens", "prompt + completion (reasoning is a subset of completion); resume segments added; requests without usage not included", "build_runs.py")
for t in tests:
    if t["quantity"].startswith("remeasured"):
        add(f"test: {t['comparison']}", f"medians {float(t['median_A']):.4f} vs {float(t['median_B']):.4f}; permutation p {float(t['exact_permutation_p_two_sided_median_diff']):.4f}; Mann-Whitney p {float(t['exact_mannwhitney_p_two_sided']):.4f}", "tables/runs_all.csv", "remeasure_speedup_median3", "exact over all C(10,5)=252 splits, two-sided, unpaired, exploratory", "build_compare.py")
add("stacking K=2/3/5/best K medians", f"{ss['median_K2']:.4f} / {ss['median_K3']:.4f} / {ss['median_K5']:.4f} / {ss['median_bestK_posthoc']:.4f}", "runs/followup/stack-bestofn-s*/stack_results.json", "results[].median_speedup", "median over 5 seeds; best K chosen post hoc", "build_mechanism.py")
add("stacking cost", f"{ss['total_stacks']} stacks, {ss['total_independent_measurements']} measurements, 0 model calls", "runs/followup/stack-bestofn-s*/stack_results.json", "results[].valid_measurements", "sum", "build_mechanism.py")
# correctness
add("stock handling of the 404-file corpus", f"decoded 227; uncaught exception {meta['uncaught_exceptions']}; killed by signal {meta['killed_by_signal']}; ASan files {meta['stock_files_with_asan_error']}; UBSan files {meta['stock_files_with_ubsan_msg']}", "runs/round2/correctness/stock-classification-1094785/classification.csv", "outcome, detail, asan_error, ubsan_messages", "ids < 404", "build_correctness.py")
add("unified correctness table", "see tables/correctness_unified.csv", "runs/followup/correctness-*; runs/round2/correctness/{DIFF0,DIFF1,SAN}-*", "raw.jsonl per file; *-asan.err, *-tsan.err; summary.json", "per-file differential split by corpus kind; sanitizer messages normalised (numbers replaced) and compared with the stock run", "build_correctness.py")
add("code reading of final patches (shared mutable state)", "see tables/concurrency_patterns_by_patch.csv", "runs/**/best.patch; experiments/patches/final-cumulative/*; runs/deepseek/greedy-s3-*/patches/gen_*.patch", "added lines containing static", "regex + manual check of the TSan-clean objects", "build_concurrency.py")
add("earliest bad step in the seed-3 chain", "step 3 (request 12, Profile::GetFieldIndex): TSan 0 -> 3 locations; 36/48 concurrent mismatches", "runs/followup/correctness-sanitize-1088521/s3-step0*-tsan.err; runs/deepseek/greedy-s3-1072869/patches/gen_12.patch", "SUMMARY: ThreadSanitizer; digest_mismatches", "compare consecutive steps", "build_mechanism.py, build_correctness.py")
add("observed LLM job concurrency", "I1 max 4; I2 max 8; I3 max 4", "runs/main/*/run.json + summary.json (start/finish); runs/round2/runs/*/segments/*.node.txt; runs/deepseek/submission-s2-5.txt", "started, finished, start, end", "sweep over start/end times", "build_job_concurrency.py")
write_csv(PM / "sources.csv", rows); print(len(rows), "source rows")
