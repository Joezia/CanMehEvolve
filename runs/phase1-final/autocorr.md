# Lag-1 autocorrelation of candidate_ns series (recomputed from raw timings)

Per measurement: median and range across its 10 processes (9 repetitions each); groups summarise measurements. SE of one series is about 0.33.

| group | measurements | series | median of per-measurement medians | range of per-measurement medians | pooled single series: median [min, max] |
|---|---|---|---|---|---|
| calibration main pairs (6 pairs, both batches) | 600 | 6000 | -0.104 | [-0.411, +0.264] | -0.108 [-0.93, +0.77] |
| calibration null pair | 100 | 1000 | -0.093 | [-0.368, +0.264] | -0.104 [-0.90, +0.72] |
| calibration sweep pairs (batch 1 only) | 80 | 800 | -0.114 | [-0.376, +0.145] | -0.114 [-0.83, +0.67] |
| SDK inert patch (stock vs no-op patch) | 6 | 60 | +0.238 | [+0.117, +0.395] | +0.233 [-0.62, +0.75] |
| SDK DeepSeek search candidates (all measurements) | 338 | 3380 | +0.048 | [-0.312, +0.404] | +0.049 [-0.84, +0.78] |
| SDK fixed final patches (3 re-measurements each, 10 runs) | 30 | 300 | +0.042 | [-0.178, +0.298] | +0.019 [-0.71, +0.70] |

Cross-check: {"files_compared": 399, "max_abs_difference": 1.0113437864944785e-14}
