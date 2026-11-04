# Patch material that is not the submitted series

**The submitted patch series is `patches/` at the repository root** (12 patches, greedy seed 3, the median seed by final speedup; numbered `0001`…`0012`, applied in order,
each with its description — what it changes, why it might be faster, risks, provenance — at the top). Nothing else is in `patches/`, so `git am patches/*.patch` applies it.

This directory holds the supporting records:

| Path | What |
|---|---|
| `messages-greedy-s3.json` | The explanations used for the commit messages of `patches/`. |
| `greedy-s{1,2,4,5}-unexplained/` | The other four greedy chains rebuilt as incremental series: they apply in order and reproduce their final patches, but their messages carry provenance only (experiment records, not submitted). |
| `final-cumulative/*.cumulative-vs-stock.patch` + `README.md` | Each run's fixed final patch (5 greedy, 5 best-of-N) as one cumulative diff against stock, with an index: functions changed, re-measured speedup, short description. Apply **one** of them to stock, never several. |

## Cumulative versus incremental (do not mix them)

The search saves, for every candidate, a **cumulative** patch: the diff of the whole patched library against stock (`runs/deepseek/<run>/patches/gen_N.patch`). A later cumulative patch already contains every earlier accepted change,
so applying them one after another would apply the same hunks twice and fail. The series were rebuilt as **incremental** patches (`git format-patch`, one commit per accepted step) by `scripts/make_patch_series.py`;
it checks that replaying a whole series with `git am` on stock gives exactly the tree of the run's final cumulative patch (`scripts/verify_patch_series.sh`, output in `runs/phase1-final/patch_series_check.txt`).

## How to apply

```sh
git init sdk-work && cp -r <FITSDK>/src sdk-work/ && cd sdk-work && git add -A && git commit -qm stock   # stock sources only; the SDK itself is not in this repository
git am /path/to/repo/patches/*.patch                                                                    # the submitted series, in order
# or one cumulative patch:  git apply /path/to/repo/experiments/patches/final-cumulative/greedy-seed3.cumulative-vs-stock.patch
```

## What the numbers in the messages mean

The ratio steps (R, candidate/stock, below 1 is faster) are the search's own ranking values (max of two measurements). Only each run's **final** patch was re-measured independently (three measurements under the frozen rule);
intermediate steps were not, and steps below about 0.3% cannot be told apart from noise. Edits with unsynchronised lazily built tables (`Profile::GetMesg`, `Profile::GetFieldIndex`) or a little-endian assumption (`FieldBase::GetValue`)
were not tested for thread safety or other platforms. The commit author in the patches is a placeholder (`CanMehEvolve <noreply@example.com>`).
