# Clumped wrong skips on the synthetic map

Quantile path with natural-neighbour interpolation, budget 0.20 per level at confidence 0.80. The record has 250 campaigns. The score variants were run on the first 60 seeds.

## Findings

1. **The guarantee held.** There were 161 exceedances in 1,500 level checks, against 170 allowed by the picked levels. Exchangeability between the calibration draw and its level is untouched: the draw is uniform within each level, and the labels may be spatially correlated in any way.
2. **The count is set by the budget, the location by the score.** About 270 wrong skips per campaign occur with every interest score tried:

   | Interest score | Wrong skips per campaign | Sites measured | Exceedances |
   | --- | --- | --- | --- |
   | Logistic on absolute peak height above baseline (record) | 270 | 333 | 37 / 360 |
   | Logistic on prominence | 278 | 358 | 45 / 360 |
   | Predicted prominence (no model) | 273 | 358 | 41 / 360 |

   The quantile path raises the threshold until the calibration draw reaches its allowed failures. The budget is therefore spent; only the sites it is spent on change.
3. **The original score depends on signal shape.** The interest label is relative: prominence above the local baseline must reach at least 5. The logistic score uses absolute height above that baseline.
   - The broad, weak correlation peak of the micellar phase (L1) has high prominence but small absolute height: a median of 0.43, against 5.5 for the Bragg peaks of the ordered phases (FWHM 0.011 against 0.004 Å⁻¹).
   - The score ranks interesting L1 sites low (median 0.38, against 0.13 for non-interesting L1 sites and 1.0 for I1 and H1). Its AUC within L1 is 0.93, against 0.98 for the predicted prominence.
   - 75 % of the wrong interest skips fall in L1. Their true prominence has a median of 13 and reaches 67.
   - The interpolated spectrum itself predicted a prominence of at least 5 for 91 % of these sites. The interpolation is not at fault; the score is.
4. **A score matched to the label moves the errors to the margin.** With the prominence scores, the wrong skips are the least interesting of the interesting sites: median true prominence 8.4. The probability of a wrong skip falls with prominence: 0.72 for 5–8, 0.52 for 8–10, 0.36 for 10–15, 0.15 for 20–40 and 0.05 above 40. These sites form contiguous bands of composition, where the prominence varies slowly near the threshold, so the errors still clump.
5. **The denominator matters.** The rate is taken over all sites of a level, and only a third of the sites are of interest. A budget of 0.20 can therefore cost a large share of the interesting sites. Here 35 % of the interesting sites on certified levels were skipped wrongly, with the record's score. A guarantee on the share of interesting sites lost needs a label-conditional (recall) statement.

## Files

- `sites.json`: per-site truth descriptors, phase and wrong-skip frequencies.
- `decision_time.npz`: predictions at decision time.
- `score_swap_*.json`: the score variants.
- Scripts: `experiments/analysis/syn_clumps.py` and `syn_score_swap.py`.

## Interest certificate turned off (one run, seed 0)

The interpolation certificate alone, with the quantile path at 0.20 and confidence 0.80 (`interp_only_seed0.png`), compared with both certificates in the record's seed 0:

| | Both certificates (record) | Interpolation only |
| --- | --- | --- |
| Measured | 350 | 331 |
| Wrong skips | 215 (10.3 %) | 161 (7.7 %) |
| Interesting sites skipped | 539 of 719, 202 of them as not of interest | 611 of 719, all of them as predictable |

Level rates were 0.18, 0.14, 0.12, 0.13, 0.08 and 0.08 against the budget of 0.20.

- **Where the wrong skips lie.** They are now all interpolation failures of the peak position and FWHM, and they lie along lines.
- **Phase boundaries.** Sites with a design neighbour of another phase are 8.7 % of all sites but 44 % of the wrong skips.
- **Inside the micellar phase.** Most of the remaining wrong skips fall within L1 (81 of 91).
- **Signal shape again.** The FWHM tolerance is absolute (0.001 Å⁻¹). That is about 9 % of the broad L1 correlation peak (0.011 Å⁻¹), against about 25 % of the Bragg peaks (0.004 Å⁻¹). The same claim is therefore much stricter on broad peaks.
