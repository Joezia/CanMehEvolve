# Phase 1 final statistics

best_confirmed_speedup = median speedup of the 3 independent re-measurements of the run's fixed final patch (1.0 if any fails the frozen rule).
Course metric = (best_confirmed_speedup - 1) / total_tokens (all tokens actually spent, truncated replies included). log-speedup per Mtok is supplementary.
Primary group test: exact two-sided permutation test of the difference of medians (all C(10,5)=252 splits), chosen to match the median-and-range
reporting of C4; the exact Mann-Whitney test and a paired sign test are given alongside, none replaces the primary. n = 5 seeds per arm, so none of these
removes selection effects or isolates inheritance, feedback or selection; the arms differ in more than one thing.

## Qwen3-coder-next matrix (search vs best-of-N), full runs
- **Qwen, full** — best_confirmed_speedup: search = median 1.0573, range [1.0266, 1.0804]; bestofn = median 1.0613, range [1.0384, 1.0843]. Permutation (median) p=0.7143; Mann-Whitney exact p=0.6905; search higher in 2/5 paired seeds, sign test p=1.0000.
- **Qwen, full** — course_metric: search = median 1.9843e-06, range [6.7311e-07, 2.7378e-06]; bestofn = median 2.3248e-06, range [1.2969e-06, 2.8717e-06]. Permutation (median) p=0.7143; Mann-Whitney exact p=0.5476; search higher in 2/5 paired seeds, sign test p=1.0000.

## DeepSeek (greedy vs best-of-N), full runs as executed

- **DeepSeek, full** — best_confirmed_speedup: greedy = median 1.1687, range [1.1574, 1.2155]; bestofn = median 1.0725, range [1.0667, 1.074]. Permutation (median) p=0.0476; Mann-Whitney exact p=0.0079; greedy higher in 5/5 paired seeds, sign test p=0.0625.
- **DeepSeek, full** — course_metric: greedy = median 3.6125e-07, range [2.533e-07, 4.8056e-07]; bestofn = median 2.2281e-07, range [1.4377e-07, 2.6824e-07]. Permutation (median) p=0.0476; Mann-Whitney exact p=0.0159; greedy higher in 4/5 paired seeds, sign test p=0.3750.
- **DeepSeek, full (supplementary)** — logspeed_per_Mtok: greedy = median 0.32714, range [0.23524, 0.44407]; bestofn = median 0.2151, range [0.13918, 0.25891]. Permutation (median) p=0.0476; Mann-Whitney exact p=0.0159; greedy higher in 4/5 paired seeds, sign test p=0.3750.

Actual HTTP attempts per run (greedy): [40, 40, 38, 34, 34]; (bestofn): [40, 40, 40, 40, 40].

## DeepSeek common-budget analysis (post hoc: best patch by the then-current ranking within the first 34 HTTP requests)

34 is the shortest run's attempt count (greedy seeds 4 and 5), fixed before looking at performance. Original full results remain the primary record.

- **DeepSeek, first 34 requests** — best_confirmed_speedup: greedy = median 1.1681, range [1.1522, 1.191]; bestofn = median 1.0726, range [1.0667, 1.074]. Permutation (median) p=0.0476; Mann-Whitney exact p=0.0079; greedy higher in 5/5 paired seeds, sign test p=0.0625.
- **DeepSeek, first 34 requests** — course_metric_budget: greedy = median 3.4308e-07, range [2.7623e-07, 5.1988e-07]; bestofn = median 2.509e-07, range [1.6616e-07, 3.3476e-07]. Permutation (median) p=0.0476; Mann-Whitney exact p=0.0317; greedy higher in 4/5 paired seeds, sign test p=0.3750.
