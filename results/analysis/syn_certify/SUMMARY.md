# Is the certification correct? Synthetic map, interpolation certificate only

The interpolation certificate alone, with the quantile path, budget 0.20 per level, confidence 0.80 and natural-neighbour interpolation. 100 campaigns per claim (seeds 0–99) and 6 certified levels each, so 600 level checks per claim.

On each level the rule allows k calibration failures. The picked failure probability δ_L is the worst-case probability of exceeding the budget at that k. It depends only on the calibration size, the level size, the budget and the confidence, not on the claim, so the allowed number of exceedances is the same for every claim: Σ δ_L = 67.9 over 600 checks (mean δ_L 0.113).

| Claim | Sites measured (mean) | Mean wrong-skip rate on a level | Levels over budget | Allowed (Σ δ_L) | Observed / allowed |
| --- | --- | --- | --- | --- | --- |
| Peak, Δq ≤ 0.005, ΔFWHM ≤ 0.001 Å⁻¹ | 313 | 0.137 | 16 / 600 | 67.9 | 0.24 |
| Peak, half tolerance | 393 | 0.143 | 26 / 600 | 67.9 | 0.38 |
| Peak, quarter tolerance | 533 | 0.149 | 48 / 600 | 67.9 | 0.71 |
| Full spectrum, 0.01 + 1 % | 391 | 0.150 | 48 / 600 | 67.9 | 0.71 |
| Full spectrum, 0.05 + 5 % | 274 | 0.095 | 0 / 600 | 67.9 | 0 |
| Both certificates, peak (the record, 250 campaigns) | 334 | – | 161 / 1500 | 169.8 | 0.95 |

## Findings

1. The certification is correct for every claim. The observed number of levels over budget never exceeds the number the picked failure probabilities allow; the largest ratio is 0.71.
2. The bound becomes tight as the claim fails more often. With a claim that rarely fails, most levels cannot exceed the budget even if every coverable site is skipped, so exceedances are rare. As the tolerance tightens, failures become plentiful and the exceedance count rises towards Σ δ_L. The two-certificate record, where the interest claim supplies many failures, sits at 0.95.
3. The mean wrong-skip rate per level stays below the budget (0.10–0.15 against 0.20). The rule spends part of the budget, not all of it, because the threshold is set conservatively from 40 calibration sites.

The per-level reachability flag in `summary.json` is wrong for this run (it averaged over sites outside the triangle). The script is fixed; the counts above do not depend on it.
