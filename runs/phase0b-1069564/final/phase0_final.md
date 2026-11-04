# Phase 0 final summary

rule binary sha256 `c3f796adf1d24485…`; alpha=0.01, min effect 2%, 10 processes x 9 repetitions per trial.
batch 1: `runs/phase0-1068829`; batch 2: `/home/z/zhouzia/Workspace/CanMehEvolve/runs/phase0b-1069564`.

| pair | true ratio | n | accepted (single) | rate, 95% CP | median reported | abs bias | rel err | two-stage accepted | lag-1 AC median |
|---|---|---|---|---|---|---|---|---|---|
| null | 1.0000 | 100 | 0 | 0.0% [0.0, 3.6] | 1.0004 | +0.0004 | +0.04% | 0/50 | -0.09 |
| faster-1-percent | 0.9900 | 100 | 1 | 1.0% [0.0, 5.4] | 0.9897 | -0.0003 | -0.03% | 0/50 | -0.12 |
| faster-2-percent | 0.9804 | 100 | 42 | 42.0% [32.2, 52.3] | 0.9808 | +0.0005 | +0.05% | 10/50 | -0.09 |
| faster-5-percent | 0.9524 | 100 | 99 | 99.0% [94.6, 100.0] | 0.9538 | +0.0014 | +0.15% | 49/50 | -0.10 |
| faster-10-percent | 0.9091 | 100 | 100 | 100.0% [96.4, 100.0] | 0.9093 | +0.0002 | +0.02% | 50/50 | -0.11 |
| slower-10-percent | 1.1000 | 100 | 0 | 0.0% [0.0, 3.6] | 1.1009 | +0.0009 | +0.08% | 0/50 | -0.10 |
| sweep-105 | 1.0500 | 20 | 0 | 0.0% [0.0, 16.8] | 1.0520 | +0.0020 | +0.19% | 0/10 | -0.09 |
| sweep-110 | 1.1000 | 20 | 0 | 0.0% [0.0, 16.8] | 1.1005 | +0.0005 | +0.04% | 0/10 | -0.07 |
| sweep-200 | 2.0000 | 20 | 0 | 0.0% [0.0, 16.8] | 2.0076 | +0.0076 | +0.38% | 0/10 | -0.13 |
| sweep-400 | 4.0000 | 20 | 0 | 0.0% [0.0, 16.8] | 4.0256 | +0.0256 | +0.64% | 0/10 | -0.15 |

## Per batch (single-trial acceptance)

| pair | batch 1 | batch 2 | Fisher p | median-ratio shift | permutation p |
|---|---|---|---|---|---|
| null | 0/50 = 0.0% [0.0, 7.1] | 0/50 = 0.0% [0.0, 7.1] | 1.000 | -0.0009 | 0.110 |
| faster-1-percent | 0/50 = 0.0% [0.0, 7.1] | 1/50 = 2.0% [0.1, 10.6] | 1.000 | +0.0000 | 0.989 |
| faster-2-percent | 22/50 = 44.0% [30.0, 58.7] | 20/50 = 40.0% [26.4, 54.8] | 0.840 | +0.0009 | 0.521 |
| faster-5-percent | 49/50 = 98.0% [89.4, 99.9] | 50/50 = 100.0% [92.9, 100.0] | 1.000 | -0.0014 | 0.154 |
| faster-10-percent | 50/50 = 100.0% [92.9, 100.0] | 50/50 = 100.0% [92.9, 100.0] | 1.000 | +0.0003 | 0.753 |
| slower-10-percent | 0/50 = 0.0% [0.0, 7.1] | 0/50 = 0.0% [0.0, 7.1] | 1.000 | +0.0025 | 0.014 |

Empirical detection threshold (90%): {"single": {"pair": "faster-5-percent", "true_ratio": 0.95235, "rate": 0.99, "cp_lower": 0.9455406146079193}, "two_stage": {"pair": "faster-5-percent", "true_ratio": 0.95235, "rate": 0.98, "cp_lower": 0.8935304542885001}}

Failed / interrupted measurements: 1 (see failures.json).
