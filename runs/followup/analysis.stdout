# Follow-up analysis (computed)

## 2. SDK inert patch, frozen rule

- measurements pooled over both node families: 240; judged faster: 0; 95% CI of the false-accept rate: [0.00%, 1.53%]
- reported ratio: median 0.99997, sd 0.00076, range [0.99774, 1.00212] (the gate needs <= 0.98)
- p-values below 0.01: 4 of 240; unstable: 0
- lag-1 autocorrelation (median over processes of each measurement): median 0.063, range [-0.255, 0.440] over 240 measurements

## 3. Null search (8 runs x 36 no-op candidates)

- accepted updates per run (of 36 no-op candidates): [2, 2, 3, 3, 3, 3, 4, 4]
- single update size from noise alone: median 0.024%, max 0.063% (n=24 updates)
- total record drift (1 - final record) over the 8 runs: median 0.080%, max 0.109%
- real greedy chains (5 runs, 50 accepted steps): steps no larger than the largest noise step (0.063%): 4; no larger than 0.2%: 15; no larger than 0.5%: 21

## 6. Stacking best-of-N's own candidates vs greedy

| seed | best-of-N final | greedy final (40 req.) | stack K=2 | K=3 | K=5 | best K (oracle) | best K speedup | last K |
|---|---|---|---|---|---|---|---|---|
| 1 | 1.0730 | 1.1574 | 1.1304 | 1.1427 | 1.1421 | 9 | 1.1632 | 1.1557 |
| 2 | 1.0688 | 1.2155 | 1.1217 | 1.1358 | 1.1922 | 6 | 1.1977 | 1.1924 |
| 3 | 1.0740 | 1.1758 | 1.1272 | 1.1363 | 1.1464 | 10 | 1.1579 | 1.1574 |
| 4 | 1.0725 | 1.1919 | 1.1310 | 1.1499 | 1.1578 | 7 | 1.1870 | 1.1769 |
| 5 | 1.0667 | 1.1661 | 1.1167 | 1.1462 | 1.1880 | 6 | 1.2095 | 1.2093 |

medians over 5 seeds: best-of-N final 1.0725; greedy 1.1758; stack K=2 1.1272; K=3 1.1427; K=5 1.1578; best K per seed (oracle) 1.1870; last K 1.1769

## 1. All five greedy runs at 40 HTTP requests

greedy final speedups: [1.1574, 1.2155, 1.1758, 1.1919, 1.1661] (median 1.1758, range 1.1574-1.2155); best-of-N median 1.0725; greedy higher in 5/5 seeds; exact permutation test of the median difference p = 0.0476 (exploratory)

