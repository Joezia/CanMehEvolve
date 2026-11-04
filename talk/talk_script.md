# Five-minute talk script (English)

Slides: `talk/talk.pptx` (5 slides). Timing marks are approximate; numbers are from `runs/phase1-final/` (frozen).

## Slide 1

(About 45 s.) Papers say an LLM in a search loop finds faster systems code. The missing control is the same number of model calls with no feedback and no selection. We test that on one real library: the Garmin FIT SDK decoder, measured as a full decode of four files. Every candidate is a unified diff against stock, so a result is a patch someone can review. We compare a greedy chain, which keeps and builds on its best patch, with best-of-N, which starts from stock every time. Same model, same prompt, same budget of 40 requests, five seeds each. Compiler flags and two human patches are the non-LLM references. I report every seed.

## Slide 2

(About 60 s.) Each call: pick one function, weighting by perf samples from a 20-second profile with ten percent uniform draws. Show the model that function's text and the stock decode time. It returns a replacement body. We splice it in, compile, check the decoded output checksum, and time it against stock: ten fresh processes, nine repetitions each. The only difference between the arms is the text shown. Greedy shows the function as it is under the current best patch, so earlier edits are inherited. Best-of-N always shows stock and never sees scores or errors. Both rank candidates the same way: measure, re-measure if it might beat the record, take the worse of the two. That orders candidates; it is not a significance test. The final patch is re-measured three more times independently. Every request counts against the budget of 40, including truncated replies and server errors.

## Slide 3

(About 60 s.) Before trusting any speedup we calibrated the instrument on pairs where we know the true ratio. One measurement runs the stock and candidate in the same process, alternating order, ten processes by nine repetitions. The rule says faster if the ratio is below 0.98 and an exact sign-flip test gives p under one percent. The rule and thresholds were fixed before any calibration data. On 100 null trials nothing was accepted, but that only bounds the false-accept rate by about 3.6 percent. Changes of about 5 percent were found 99 times in 100; the 2 percent pair, whose true change is 1.965 percent and so sits just under the gate, was accepted 42 times. So the instrument is reliable near 5 percent and above, and that does not carry over unconditionally to every SDK patch: six SDK measurements of an inert patch showed positive autocorrelation.

## Slide 4

(About 80 s.) Here are all ten runs. Each marker is a seed; the speedup is the median of three independent re-measurements of that run's fixed final patch, and every one passed the rule. Greedy has a median of 1.169, range 1.157 to 1.216. Best-of-N has 1.073, range 1.067 to 1.074. Greedy is higher in all five paired seeds. The primary permutation test on the median difference gives p about 0.048 and the Mann-Whitney test 0.008; with five seeds I treat these as coarse. For reference, -O3 gives 1.09 and -O3 with march native 1.11, measured in a separate batch: every greedy seed beats both, and best-of-N is below -O3. Panel B is post hoc: three greedy runs stopped at the deadline after 38, 34 and 34 requests, so we also compare each run's best patch within the first 34 requests, re-measured. Same picture. Panel C is the course metric, speedup minus one per token: greedy spends more tokens but its median is still higher, 3.6 versus 2.2 times ten to the minus seven.

## Slide 5

(About 55 s.) What the data support: both arms beat stock, and greedy beat best-of-N in all five seeds, in the full runs and in the 34-request view. Every best-of-N winner is the same one-function change, a lookup table in Profile GetMesg; the greedy chains kept it and added four to ten more accepted edits, and only greedy went past -O3 with march native. What we cannot say: five seeds and one model do not isolate selection, feedback or inheritance, since the arms differ in several ways and we ran no ablation. Three greedy runs did not reach 40 requests because of the three-hour job limit, and the 34-request analysis was added after seeing results. Many accepted steps are under 0.3 percent, which is noise; only the final patches were re-measured independently. Correctness checking is only the output checksum, and some edits use unsynchronised static caches, so none is upstream-ready without review. Thank you; questions.

Total: 739 words, about 5.3 minutes at 140 words per minute. If time is short, drop the last two sentences of slide 4.
