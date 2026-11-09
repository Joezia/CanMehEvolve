# Check record

- All numbers are read from `data/*.csv` (copied from `presentation_materials/tables`), computed from the raw run files; no experiment was run.
- Slide 2 table check: Qwen population 1.0745 [1.0307, 1.1237] / 34,230; Qwen best-of-N 1.0560 [1.0389, 1.0727] / 25,361; DeepSeek population 1.1648 [1.1375, 1.1811] / 366,952; DeepSeek best-of-N 1.0732 [1.0685, 1.0737] / 320,397 (medians of per-run reported tokens). Token increase: 34,230/25,361 = +35%; 366,952/320,397 = +15% (ratio of medians, not a per-run efficiency).
- Re-measurement passes: 19 of 20 runs 3/3; Qwen best-of-N seed 4 is 2/3 (marked with a dagger).
- C1: -O3 = median of two batch medians (1.0911, 1.0898) = 1.090; -O3 -march=native 1.1084 (the earlier batch of that flag was invalid and is not used). C2: 1.0683 and 1.0821 (single batch, no formal timer).
- Slide 3 classes (mutually exclusive, 20 final patches): race report only 12; also output difference / crash / memory error 4; no new finding detected 4. 16/20 = 12 + 4. 3/20 differed on the 55 extra valid files (DeepSeek population seed 2: 1/55; Qwen population seed 3: 45/55; Qwen population seed 4: 4/55); the fourth in the red group crashed on mutated inputs only.
- 20/20 passed the supplied checks: every candidate is measured only after those checks, and every final patch was re-measured.
- No p-values, Holm correction, version labels, greedy, stacking or timeline appear on the slides.
