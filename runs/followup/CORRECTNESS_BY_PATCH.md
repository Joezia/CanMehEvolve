# Follow-up correctness results per patch and test condition

Corpus: the 4 standard files plus 400 mutants with recomputed CRCs (not legal files). The stock library itself dies on 177 of the 404 files (uncaught exception), so the differential comparison covers 227 files.
UBSan: messages that do NOT also occur with the stock library (the stock library has 1 of its own: src/fit_field_base.cpp left shift of negative value N).

| patch | differential vs stock: compared / identical / differing | crash in both (same input) | crash only in patch | crash only in stock | ASan errors | UBSan messages not in stock | ASan-run digest differences | TSan distinct race locations | TSan digest mismatches (4 threads) | TSan run result |
|---|---|---|---|---|---|---|---|---|---|---|
| final-bestofn-seed1 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | completed with race reports (exit 66) |
| final-bestofn-seed2 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | completed |
| final-bestofn-seed3 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | completed with race reports (exit 66) |
| final-bestofn-seed4 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | completed with race reports (exit 66) |
| final-bestofn-seed5 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | completed with race reports (exit 66) |
| final-greedy-seed1 | 216 / 216 / 0 | 177 | 11 | 0 | 1 | 2 | 0 | 3 | - | did not finish (exit 66, no digest line) |
| final-greedy-seed2 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | completed with race reports (exit 66) |
| final-greedy-seed3 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 4 | - | did not finish (exit 66, no digest line) |
| final-greedy-seed4 | 227 / 223 / 4 | 177 | 0 | 0 | 0 | 0 | 1 | 2 | 0 | completed with race reports (exit 66) |
| final-greedy-seed5 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | completed with race reports (exit 66) |
| human-attempt-1 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | completed |
| human-attempt-2 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | completed |
| s3-step01-gen6 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | completed |
| s3-step02-gen11 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | completed |
| s3-step03-gen12 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 3 | 36 | completed with race reports (exit 66) |
| s3-step04-gen13 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 2 | 38 | completed with race reports (exit 66) |
| s3-step05-gen17 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 3 | - | did not finish (exit 66, no digest line) |
| s3-step06-gen18 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 3 | - | did not finish (exit 66, no digest line) |
| s3-step07-gen20 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 3 | - | did not finish (exit 66, no digest line) |
| s3-step08-gen21 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 3 | 39 | completed with race reports (exit 66) |
| s3-step09-gen28 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 3 | 39 | completed with race reports (exit 66) |
| s3-step10-gen31 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 2 | 38 | completed with race reports (exit 66) |
| s3-step11-gen34 | 227 / 227 / 0 | 177 | 0 | 0 | 0 | 0 | 0 | 4 | - | did not finish (exit 66, no digest line) |
