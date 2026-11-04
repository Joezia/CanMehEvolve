# Recomputed statistics (exploratory; unrounded raw inputs)

| quantity | greedy median [range] | best-of-N median [range] | permutation (median) p | Mann-Whitney p | greedy higher | sign p |
|---|---|---|---|---|---|---|
| full speedup (re-measured) | 1.169 [1.157, 1.216] | 1.073 [1.067, 1.074] | 0.0476 | 0.0079 | 5/5 | 0.0625 |
| full search-time confirmed metric | 3.597e-07 [2.505e-07, 4.792e-07] | 2.216e-07 [1.441e-07, 2.691e-07] | 0.0476 | 0.0159 | 4/5 | 0.3750 |
| full re-measured metric | 3.613e-07 [2.533e-07, 4.806e-07] | 2.228e-07 [1.438e-07, 2.682e-07] | 0.0476 | 0.0159 | 4/5 | 0.3750 |
| 34-request speedup (re-measured) | 1.168 [1.152, 1.191] | 1.073 [1.067, 1.074] | 0.0476 | 0.0079 | 5/5 | 0.0625 |
| 34-request search-time confirmed metric | 3.459e-07 [2.748e-07, 5.179e-07] | 2.493e-07 [1.665e-07, 3.358e-07] | 0.0476 | 0.0317 | 4/5 | 0.3750 |
| 34-request re-measured metric | 3.431e-07 [2.762e-07, 5.199e-07] | 2.509e-07 [1.662e-07, 3.348e-07] | 0.0476 | 0.0317 | 4/5 | 0.3750 |

Token accounting: {"note": "requests without a usage object (HTTP 502) consumed an UNKNOWN number of tokens; they are not included, so totals may underestimate cost and overstate efficiency", "requests_without_usage_object": [["bestofn-s2-1072868", 40, 502, ""], ["greedy-s1-1072019", 25, 502, ""], ["greedy-s2-1072867", 39, 502, ""], ["greedy-s3-1072869", 15, 502, ""], ["greedy-s3-1072869", 25, 502, ""], ["greedy-s3-1072869", 27, 502, ""], ["greedy-s3-1072869", 36, 502, ""], ["greedy-s4-1072871", 33, 502, ""], ["greedy-s5-1072873", 10, 502, ""], ["greedy-s5-1072873", 23, 502, ""]], "truncated_requests": 13, "truncated_total_tokens": 432991, "total_tokens_all_runs": 4233676}
Cross-check vs phase1_final.json (max abs diff): 0.0
