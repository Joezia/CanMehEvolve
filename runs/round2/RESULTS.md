# Round 2 results (raw numbers; interpretation is in the separate Chinese note)

## 1. Formal runs (all 20 listed, finished or not)

| run | state | ended | model id returned | HTTP requests | rows (no request) | tokens | trunc. | no-usage | segments | hosts | best confirmed (credits) | best retained | re-measured (3x) | final state |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ds-bestofn-s1 | complete | request budget reached | deepseek-v4.1-flash-1017 | 40 | 40 (0) | 278989 | 0 | 4 | 1 | xcnc14 | 1.0730 | 1.0730 | 1.0737 (pass 3/3) | re-measured |
| ds-bestofn-s2 | complete | request budget reached | deepseek-v4.1-flash-1017 | 40 | 40 (0) | 320397 | 0 | 1 | 1 | xcnc7 | 1.0735 | 1.0735 | 1.0731 (pass 3/3) | re-measured |
| ds-bestofn-s3 | complete | request budget reached | deepseek-v4.1-flash-1017 | 40 | 40 (0) | 266927 | 0 | 3 | 1 | xcnc33 | 1.0735 | 1.0735 | 1.0732 (pass 3/3) | re-measured |
| ds-bestofn-s4 | complete | request budget reached | deepseek-v4.1-flash-1017 | 40 | 40 (0) | 354938 | 0 | 2 | 1 | xcnc6 | 1.0726 | 1.0726 | 1.0733 (pass 3/3) | re-measured |
| ds-bestofn-s5 | complete | request budget reached | deepseek-v4.1-flash-1017 | 40 | 40 (0) | 366211 | 1 | 4 | 1 | xcnc8 | 1.0691 | 1.0691 | 1.0685 (pass 3/3) | re-measured |
| ds-population-s1 | complete | request budget reached | deepseek-v4.1-flash-1017 | 40 | 40 (0) | 305734 | 0 | 8 | 2 | xcnc30/xcnc4 | 1.1634 | 1.1634 | 1.1648 (pass 3/3) | re-measured |
| ds-population-s2 | complete | request budget reached | deepseek-v4.1-flash-1017 | 40 | 40 (0) | 421966 | 0 | 6 | 2 | xcnc3 | 1.1364 | 1.1364 | 1.1375 (pass 3/3) | re-measured |
| ds-population-s3 | complete | request budget reached | deepseek-v4.1-flash-1017 | 40 | 40 (0) | 366952 | 0 | 5 | 2 | xcnc19/xcnc6 | 1.1829 | 1.1829 | 1.1811 (pass 3/3) | re-measured |
| ds-population-s4 | complete | request budget reached | deepseek-v4.1-flash-1017 | 40 | 40 (0) | 362359 | 0 | 8 | 2 | xcnc1 | 1.1632 | 1.1632 | 1.1634 (pass 3/3) | re-measured |
| ds-population-s5 | complete | request budget reached | deepseek-v4.1-flash-1017 | 40 | 40 (0) | 380953 | 1 | 7 | 2 | xcnc1/xcnc4 | 1.1697 | 1.1697 | 1.1715 (pass 3/3) | re-measured |
| qwen-bestofn-s1 | complete | request budget reached | qwen3-coder-next | 40 | 40 (0) | 25201 | 0 | 0 | 1 | xcnc43 | 1.0402 | 1.0402 | 1.0389 (pass 3/3) | re-measured |
| qwen-bestofn-s2 | complete | request budget reached | qwen3-coder-next | 40 | 40 (0) | 24454 | 0 | 0 | 1 | xcnc3 | 1.0404 | 1.0404 | 1.0409 (pass 3/3) | re-measured |
| qwen-bestofn-s3 | complete | request budget reached | qwen3-coder-next | 40 | 40 (0) | 29363 | 0 | 0 | 1 | xcnc3 | 1.0629 | 1.0629 | 1.0622 (pass 3/3) | re-measured |
| qwen-bestofn-s4 | complete | request budget reached | qwen3-coder-next | 40 | 40 (0) | 26890 | 0 | 0 | 1 | xcnc6 | 1.0541 | 1.0541 | 1.0560 (pass 2/3) | re-measured |
| qwen-bestofn-s5 | complete | request budget reached | qwen3-coder-next | 40 | 40 (0) | 25361 | 0 | 0 | 1 | xcnc25 | 1.0713 | 1.0713 | 1.0727 (pass 3/3) | re-measured |
| qwen-population-s1 | complete | request budget reached | qwen3-coder-next | 40 | 56 (16) | 25788 | 0 | 0 | 1 | xcnc7 | 1.1235 | 1.1235 | 1.1237 (pass 3/3) | re-measured |
| qwen-population-s2 | complete | request budget reached | qwen3-coder-next | 40 | 40 (0) | 36748 | 0 | 0 | 1 | xcnc43 | 1.0582 | 1.0582 | 1.0586 (pass 3/3) | re-measured |
| qwen-population-s3 | complete | request budget reached | qwen3-coder-next | 40 | 40 (0) | 34796 | 1 | 0 | 1 | xcnc42 | 1.0801 | 1.0801 | 1.0828 (pass 3/3) | re-measured |
| qwen-population-s4 | complete | request budget reached | qwen3-coder-next | 40 | 40 (0) | 28414 | 0 | 0 | 1 | xcnc8 | 1.0313 | 1.0313 | 1.0307 (pass 3/3) | re-measured |
| qwen-population-s5 | complete | request budget reached | qwen3-coder-next | 40 | 40 (0) | 34230 | 1 | 0 | 1 | xcnc3 | 1.0739 | 1.0739 | 1.0745 (pass 3/3) | re-measured |

## 2. Five-seed summaries per configuration (never pooled across models)

| configuration | runs complete | best confirmed in credits.csv: median [min, max] | re-measured final patch | total tokens | HTTP requests | course quotient from credits.csv | extended-correctness status of final patches |
|---|---|---|---|---|---|---|---|
| ds population | 5/5 | 1.163 [1.136, 1.183] | 1.165 [1.137, 1.181] | 3.67e+05 [3.057e+05, 4.22e+05] | 40 [40, 40] | 4.504e-07 [3.232e-07, 5.343e-07] | see section 4 |
| ds best-of-N | 5/5 | 1.073 [1.069, 1.074] | 1.073 [1.069, 1.074] | 3.204e+05 [2.669e+05, 3.662e+05] | 40 [40, 40] | 2.295e-07 [1.886e-07, 2.752e-07] | see section 4 |
| qwen population | 5/5 | 1.074 [1.031, 1.123] | 1.074 [1.031, 1.124] | 3.423e+04 [2.579e+04, 3.675e+04] | 40 [40, 40] | 2.159e-06 [1.102e-06, 4.787e-06] | see section 4 |
| qwen best-of-N | 5/5 | 1.054 [1.04, 1.071] | 1.056 [1.039, 1.073] | 2.536e+04 [2.445e+04, 2.936e+04] | 40 [40, 40] | 2.013e-06 [1.596e-06, 2.81e-06] | see section 4 |

ds: population vs best-of-N, exploratory exact permutation test of the median difference p = 0.0476 (n = 5 vs 5; chosen before seeing these data but not a pre-registered primary test)

qwen: population vs best-of-N, exploratory exact permutation test of the median difference p = 0.2381 (n = 5 vs 5; chosen before seeing these data but not a pre-registered primary test)

## 3. False-accept rates (frozen rule: ratio <= 0.98, sign-flip p < 0.01, not unstable; 10 processes x 9 repetitions)

| measurement | valid trials | false accepts | 95% Clopper-Pearson | note |
|---|---|---|---|---|
| synthetic null, node class xcnc | 300 | 0 | [0.000%, 1.222%] |  |
| synthetic null, node class xcnd | 200 | 0 | [0.000%, 1.828%] |  |
| synthetic null, all valid trials | 500 | 0 | [0.000%, 0.735%] |  |
| SDK inert patch, node class xcnc | 402 | 0 | [0.000%, 0.913%] | ratio median 0.99997, range [0.99724, 1.00188], unstable 0 |
| SDK inert patch, node class xcnd | 402 | 0 | [0.000%, 0.913%] | ratio median 0.99989, range [0.99710, 1.00242], unstable 0 |

Failed, unreadable or interrupted trials are NOT counted as valid trials: synthetic null 0, SDK inert 0 (files without a valid analysis). Reaching 400 valid trials per stratum is a target; a shortfall is reported as it is.

- null-xcnc-a-1094696: host xcnc14, cpu Intel(R) Xeon(R) CPU E5-2620 v3 @ 2.40GHz, start 2026-11-08T09:54:33+08:00, end 2026-11-08T10:11:04+08:00
- null-xcnc-b-1094697: host xcnc19, cpu Intel(R) Xeon(R) CPU E5-2620 v3 @ 2.40GHz, start 2026-11-08T09:54:32+08:00, end 2026-11-08T10:11:12+08:00
- null-xcnc-c-1094698: host xcnc30, cpu Intel(R) Xeon(R) CPU E5-2620 v3 @ 2.40GHz, start 2026-11-08T09:54:33+08:00, end 2026-11-08T10:09:31+08:00
- null-xcnc-d-1094699: host xcnc1, cpu Intel(R) Xeon(R) CPU E5-2620 v3 @ 2.40GHz, start 2026-11-08T11:07:13+08:00, end 2026-11-08T11:24:13+08:00
- null-xcnd-a-1094706: host xcnd0, cpu Intel(R) Xeon(R) CPU E5-2620 v3 @ 2.40GHz, start 2026-11-08T12:43:42+08:00, end 2026-11-08T12:57:56+08:00
- null-xcnd-b-1094707: host xcnd2, cpu Intel(R) Xeon(R) CPU E5-2620 v3 @ 2.40GHz, start 2026-11-08T12:43:47+08:00, end 2026-11-08T12:58:02+08:00
- null-xcnd-c-1094708: host xcnd4, cpu Intel(R) Xeon(R) CPU E5-2620 v3 @ 2.40GHz, start 2026-11-08T12:43:46+08:00, end 2026-11-08T12:58:00+08:00
- null-xcnd-d-1094709: host xcnd1, cpu Intel(R) Xeon(R) CPU E5-2620 v3 @ 2.40GHz, start 2026-11-08T12:43:47+08:00, end 2026-11-08T12:58:02+08:00
- sdk-inert-xcnc-r2-1-1094690: host xcnc1, cpu , start 2026-11-08T09:54:30+08:00, end 2026-11-08T11:07:12+08:00
- sdk-inert-xcnc-r2-2-1094691: host xcnc3, cpu , start 2026-11-08T09:54:29+08:00, end 2026-11-08T11:07:22+08:00
- sdk-inert-xcnc-r2-3-1094692: host xcnc4, cpu , start 2026-11-08T09:54:34+08:00, end 2026-11-08T11:07:22+08:00
- sdk-inert-xcnc-r2-4-1094693: host xcnc6, cpu , start 2026-11-08T09:54:32+08:00, end 2026-11-08T11:07:24+08:00
- sdk-inert-xcnc-r2-5-1094694: host xcnc7, cpu , start 2026-11-08T09:54:32+08:00, end 2026-11-08T11:07:25+08:00
- sdk-inert-xcnc-r2-6-1094695: host xcnc8, cpu , start 2026-11-08T09:54:33+08:00, end 2026-11-08T11:07:26+08:00
- sdk-inert-xcnd-r2-1-1094700: host xcnd0, cpu , start 2026-11-08T11:07:25+08:00, end 2026-11-08T12:43:40+08:00
- sdk-inert-xcnd-r2-2-1094701: host xcnd1, cpu , start 2026-11-08T11:07:25+08:00, end 2026-11-08T12:43:45+08:00
- sdk-inert-xcnd-r2-3-1094702: host xcnd2, cpu , start 2026-11-08T11:07:26+08:00, end 2026-11-08T12:43:45+08:00
- sdk-inert-xcnd-r2-4-1094703: host xcnd3, cpu , start 2026-11-08T11:07:27+08:00, end 2026-11-08T12:43:48+08:00
- sdk-inert-xcnd-r2-5-1094704: host xcnd4, cpu , start 2026-11-08T11:07:28+08:00, end 2026-11-08T12:43:45+08:00
- sdk-inert-xcnd-r2-6-1094705: host xcnd5, cpu , start 2026-11-08T11:24:14+08:00, end 2026-11-08T13:00:35+08:00

## 4. Machine-code check of the no-op candidates, extended correctness, stock failures

No-op check: 17 candidate libraries built; .text identical to stock in 17; dynamic symbols identical in 17.

### Extended checks per patch and test condition (not ranked; counts of warnings are not a severity measure)

| patch | legal encoder files: differential (compared/identical) | mutants (not legal): differential (compared/identical, crash in both, crash only in candidate) | how files are handled, vs stock (plain build) | ASan | UBSan: messages not in stock | TSan (4 threads): distinct race locations, digest mismatches, run result |
|---|---|---|---|---|---|---|
| r2-ds-bestofn-s1 | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 2 locations; mismatches 0; returncode 66 |
| r2-ds-bestofn-s2 | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 2 locations; mismatches 0; returncode 66 |
| r2-ds-bestofn-s3 | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 2 locations; mismatches 0; returncode 66 |
| r2-ds-bestofn-s4 | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 2 locations; mismatches 0; returncode 66 |
| r2-ds-bestofn-s5 | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 2 locations; mismatches 0; returncode 66 |
| r2-ds-population-s1 | 55/55 | 216/216, both-crash 177, cand-only crash 11 | 21 of 459 files handled differently (21 newly killed by a signal) | 1 ASan errors, 0 digest differences | 2: src/fit_decode.cpp index N out of bounds for type 'unsigned char [N]'; src/fit_decode.cpp load of address NxNcNdNcNddf with insufficient space for an object of  | 4 locations; mismatches n/a (no output); returncode 66 |
| r2-ds-population-s2 | 55/54 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 1 digest differences | 0 | 2 locations; mismatches 0; returncode 66 |
| r2-ds-population-s3 | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 2 locations; mismatches 0; returncode 66 |
| r2-ds-population-s4 | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 2 locations; mismatches 0; returncode 66 |
| r2-ds-population-s5 | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 2 locations; mismatches 0; returncode 66 |
| r2-qwen-bestofn-s1 | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 0 locations; mismatches 0; returncode 66 |
| r2-qwen-bestofn-s2 | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 1 locations; mismatches 0; returncode 66 |
| r2-qwen-bestofn-s3 | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 1 locations; mismatches 0; returncode 66 |
| r2-qwen-bestofn-s4 | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 0 locations; mismatches 0; returncode 0 |
| r2-qwen-bestofn-s5 | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 1 locations; mismatches 0; returncode 66 |
| r2-qwen-population-s1 | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 0 locations; mismatches 0; returncode 0 |
| r2-qwen-population-s2 | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 0 locations; mismatches 0; returncode 0 |
| r2-qwen-population-s3 | 55/10 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 45 digest differences | 0 | 3 locations; mismatches n/a (no output); returncode 66 |
| r2-qwen-population-s4 | 55/51 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 4 digest differences | 0 | 0 locations; mismatches 0; returncode 0 |
| r2-qwen-population-s5 | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 2 locations; mismatches 0; returncode 66 |
| stack-s1-K2-fixed | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 2 locations; mismatches 0; returncode 66 |
| stack-s1-K3-fixed | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 3 locations; mismatches 2; returncode 66 |
| stack-s1-K5-fixed | 55/55 | 216/216, both-crash 177, cand-only crash 11 | 21 of 459 files handled differently (21 newly killed by a signal) | 1 ASan errors, 0 digest differences | 2: src/fit_decode.cpp index N out of bounds for type 'unsigned char [N]'; src/fit_decode.cpp load of address NxNdNfNeNf with insufficient space for an object of ty | 4 locations; mismatches n/a (no output); returncode 66 |
| stack-s1-bestK9-posthoc | 55/55 | 216/216, both-crash 177, cand-only crash 11 | 21 of 459 files handled differently (21 newly killed by a signal) | 1 ASan errors, 0 digest differences | 2: src/fit_decode.cpp index N out of bounds for type 'unsigned char [N]'; src/fit_decode.cpp load of address NxNcceNf with insufficient space for an object of type | 4 locations; mismatches n/a (no output); returncode 66 |
| stack-s2-K2-fixed | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 0 locations; mismatches 0; returncode 0 |
| stack-s2-K3-fixed | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 4 locations; mismatches n/a (no output); returncode 66 |
| stack-s2-K5-fixed | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 3 locations; mismatches n/a (no output); returncode 66 |
| stack-s2-bestK6-posthoc | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 4 locations; mismatches n/a (no output); returncode 66 |
| stack-s3-K2-fixed | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 2 locations; mismatches 0; returncode 66 |
| stack-s3-K3-fixed | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 2 locations; mismatches 0; returncode 66 |
| stack-s3-K5-fixed | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 2 locations; mismatches 0; returncode 66 |
| stack-s3-bestK10-posthoc | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 2 locations; mismatches 0; returncode 66 |
| stack-s4-K2-fixed | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 2 locations; mismatches 0; returncode 66 |
| stack-s4-K3-fixed | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 3 locations; mismatches 3; returncode 66 |
| stack-s4-K5-fixed | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 3 locations; mismatches 5; returncode 66 |
| stack-s4-bestK7-posthoc | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 3 locations; mismatches 8; returncode 66 |
| stack-s5-K2-fixed | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 2 locations; mismatches 0; returncode 66 |
| stack-s5-K3-fixed | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 3 locations; mismatches 0; returncode 66 |
| stack-s5-K5-fixed | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 3 locations; mismatches 3; returncode 66 |
| stack-s5-bestK6-posthoc | 55/55 | 227/227, both-crash 177, cand-only crash 0 | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, 0 digest differences | 0 | 3 locations; mismatches 2; returncode 66 |
| stock | - | - | 0 of 459 files handled differently (0 newly killed by a signal) | 0 ASan errors, None digest differences | 0 | 0 locations; mismatches n/a (no output); returncode 0 |

### How the stock library handles the corpus (plain build, exceptions caught)

| file kind | outcome | files |
|---|---|---|
| data | decoded | 129 |
| data | exception: FIT decode error: Architecture ? not supported. Error at byte: N | 7 |
| data | exception: FIT decode error: Decoder not in correct state after last data byte in file. Check message definitions. Error at byte: N | 1 |
| data | exception: FIT decode error: Missing FIT message definition for local message number N. Error at byte: N | 13 |
| defs | decoded | 91 |
| defs | exception: FIT decode error: Architecture . not supported. Error at byte: N | 1 |
| defs | exception: FIT decode error: Architecture < not supported. Error at byte: N | 1 |
| defs | exception: FIT decode error: Architecture ? not supported. Error at byte: N | 6 |
| defs | exception: FIT decode error: Architecture m not supported. Error at byte: N | 1 |
| defs | exception: FIT decode error: Invalid Field Size  | 12 |
| defs | exception: FIT decode error: Missing FIT message definition for local message number N. Error at byte: N | 39 |
| defs | exception: Invalid developer data index in FieldDescriptionMesg | 1 |
| defs | exception: Invalid developer field definition number in FieldDescriptionMesg | 4 |
| defs | killed/timeout: returncode_-N | 1 |
| original | decoded | 4 |
| trunc | decoded | 3 |
| trunc | exception: FIT decode error: Decoder not in correct state after last data byte in file. Check message definitions. Error at byte: N | 90 |
| valid | decoded | 55 |
