# SI 6. What the certified metric does to a campaign (draft 1)

A skip claims that a prediction meets an acceptance metric, and the choice of metric is part of the guarantee. This section measures how the metric changes the measurements spent, the attainment of the bound and the place where wrong skips fall. The guarantee itself does not depend on the metric (Appendix A).

**Set-up.**
- **Campaigns.** The interpolation claim alone, with the quantile path and natural-neighbour interpolation. Budgets as in Section 5: $R_E \le 0.10$ at confidence 0.75 for the IR map, $R_E \le 0.20$ at confidence 0.80 for the NaCl scan and the synthetic map. 50 campaigns per metric (seeds 0–49).
- **What changes.** Only the acceptance metric.
- **Signal sites.** Sites marked by the dataset's interest label: absorbance above 0.1 for IR, the (200) line present for NaCl, a dominant peak at least five times its local baseline for the synthetic map. The label distinguishes signal from background here and plays no part in the decisions.

**Metrics.**

| Metric | A skip claims that |
| --- | --- |
| Peak or line width, absolute | the width (and position) of the peak are within a fixed tolerance |
| Peak or line width, relative | the same, within a fraction of their true values |
| Profile, absolute + relative | every channel lies within $r\,\vert I \vert + a$ of the truth, on average over the channels |
| Profile, relative | the same with $a \approx 0$, so every channel counts in proportion to its intensity |
| Basis, plain SVD | the prediction error, expressed in the leading components of the seed spectra and divided by their spread, has an RMS within the tolerance |
| Basis, de-duplicated SVD | the same, with near-duplicate seed spectra merged before the decomposition, so that each spectral shape counts once whatever its abundance |

- **How the bases are built.** They use only the seed spectra, which are known before any decision, and stay frozen for the whole campaign. For the two scattering datasets they are built on log-intensity, since a linear basis is dominated by forward scattering.
- **Two settings of the tolerances.** *Default*: values a practitioner might choose; the IR row marked "record" is the setting of Section 5. *Matched*: each tolerance scaled so that 15 % of the sites on certified levels fail when predicted from all design sites of the coarser levels. That setting uses the truth of the design. It is a control for comparing metrics at equal difficulty, not a recipe for a campaign.
- **Measures reported.** "Sites failing prediction" is the share of certified-level sites whose prediction at decision time violates the metric. "Exceedances / allowed" compares the number of level checks with $R_E$ above the budget against the sum of the picked failure probabilities. "Clumping" is the share of wrong skips that have another wrong skip among their six nearest design neighbours, divided by the same share for wrong skips placed at random among the skipped sites.

**Table S6.1.** Default tolerances.

| Dataset | Metric | Sites failing prediction | Sites measured | Exceedances / allowed | Wrong skips on signal sites (signal share of skipped) | Clumping |
| --- | --- | --- | --- | --- | --- | --- |
| IR map | window profile, 0.10 + 10 % (record) | 1 % | 233 ± 2 of 959 | 0 / 38.0 | 83 % (37 %) | 22.7 |
| IR map | window profile, relative 10 % | 73 % | 804 ± 28 of 959 | 36 / 38.0 | 37 % (21 %) | 1.1 |
| IR map | basis, plain SVD (5 comp. from 73 spectra) | 76 % | 799 ± 29 of 959 | 34 / 38.0 | 7 % (2 %) | 1.0 |
| IR map | basis, de-duplicated SVD (5 comp. from 47 spectra) | 77 % | 810 ± 30 of 959 | 40 / 38.0 | 7 % (2 %) | 1.0 |
| NaCl scan | (200) FWHM, absolute (0.02 nm⁻¹) | 48 % | 655 ± 59 of 1071 | 19 / 24.0 | 97 % (61 %) | 1.2 |
| NaCl scan | (200) FWHM, relative (10 %) | 62 % | 727 ± 50 of 1071 | 26 / 24.0 | 99 % (53 %) | 1.2 |
| NaCl scan | profile, 0.01 + 1 % | 83 % | 811 ± 29 of 1071 | 19 / 24.0 | 42 % (20 %) | 1.0 |
| NaCl scan | profile, relative 5 % | 26 % | 412 ± 53 of 1071 | 15 / 24.0 | 81 % (58 %) | 1.4 |
| NaCl scan | log-intensity basis, plain SVD (10 comp. from 76 spectra) | 85 % | 821 ± 35 of 1071 | 33 / 24.0 | 34 % (18 %) | 1.0 |
| NaCl scan | log-intensity basis, de-duplicated SVD (10 comp. from 42 spectra) | 83 % | 810 ± 32 of 1071 | 19 / 24.0 | 43 % (20 %) | 1.0 |
| Synthetic map | peak, absolute (Δq 0.005, ΔFWHM 0.001 Å⁻¹) | 13 % | 312 ± 35 of 2118 | 6 / 34.0 | 60 % (34 %) | 2.1 |
| Synthetic map | peak, relative (Δq 5 %, ΔFWHM 10 %) | 15 % | 345 ± 53 of 2118 | 11 / 34.0 | 64 % (34 %) | 2.0 |
| Synthetic map | profile, 0.01 + 1 % | 19 % | 390 ± 52 of 2118 | 26 / 34.0 | 69 % (33 %) | 1.8 |
| Synthetic map | profile, relative 5 % | 25 % | 473 ± 55 of 2118 | 26 / 34.0 | 69 % (30 %) | 1.7 |
| Synthetic map | log-intensity basis, plain SVD (5 comp. from 39 spectra) | 21 % | 433 ± 65 of 2118 | 28 / 34.0 | 64 % (30 %) | 1.8 |
| Synthetic map | log-intensity basis, de-duplicated SVD (5 comp. from 10 spectra) | 19 % | 407 ± 63 of 2118 | 31 / 34.0 | 70 % (31 %) | 1.9 |

**Table S6.2.** Tolerances matched to equal difficulty.

| Dataset | Metric | Sites failing prediction | Sites measured | Exceedances / allowed | Wrong skips on signal sites (signal share of skipped) | Clumping |
| --- | --- | --- | --- | --- | --- | --- |
| IR map | window profile, absolute + relative | 17 % | 368 ± 38 of 959 | 32 / 38.0 | 72 % (30 %) | 2.2 |
| IR map | window profile, relative | 16 % | 453 ± 78 of 959 | 34 / 38.0 | 37 % (35 %) | 2.0 |
| IR map | basis, plain SVD | 16 % | 338 ± 38 of 959 | 37 / 38.0 | 81 % (31 %) | 2.8 |
| IR map | basis, de-duplicated SVD | 17 % | 343 ± 32 of 959 | 30 / 38.0 | 83 % (31 %) | 3.0 |
| NaCl scan | (200) FWHM, absolute | 18 % | 287 ± 28 of 1071 | 7 / 24.0 | 6 % (66 %) | 1.8 |
| NaCl scan | (200) FWHM, relative | 18 % | 287 ± 28 of 1071 | 7 / 24.0 | 6 % (66 %) | 1.8 |
| NaCl scan | profile, absolute + relative | 18 % | 336 ± 46 of 1071 | 17 / 24.0 | 83 % (61 %) | 1.6 |
| NaCl scan | profile, relative | 18 % | 332 ± 43 of 1071 | 16 / 24.0 | 83 % (61 %) | 1.6 |
| NaCl scan | log-intensity basis, plain SVD | 18 % | 367 ± 60 of 1071 | 11 / 24.0 | 92 % (61 %) | 1.5 |
| NaCl scan | log-intensity basis, de-duplicated SVD | 18 % | 349 ± 72 of 1071 | 6 / 24.0 | 90 % (61 %) | 1.5 |
| Synthetic map | peak, absolute | 21 % | 447 ± 75 of 2118 | 21 / 34.0 | 59 % (33 %) | 1.7 |
| Synthetic map | peak, relative | 21 % | 461 ± 82 of 2118 | 15 / 34.0 | 61 % (32 %) | 1.8 |
| Synthetic map | profile, absolute + relative | 20 % | 405 ± 56 of 2118 | 24 / 34.0 | 68 % (33 %) | 1.8 |
| Synthetic map | profile, relative | 21 % | 398 ± 49 of 2118 | 29 / 34.0 | 72 % (32 %) | 1.8 |
| Synthetic map | log-intensity basis, plain SVD | 21 % | 436 ± 70 of 2118 | 30 / 34.0 | 64 % (30 %) | 1.8 |
| Synthetic map | log-intensity basis, de-duplicated SVD | 21 % | 423 ± 54 of 2118 | 30 / 34.0 | 65 % (30 %) | 1.8 |

**Findings.**
1. **Every metric kept its guarantee.** The observed exceedances stayed at or below the allowance within chance. The largest ratio, 1.37 (log-intensity basis, plain SVD, on NaCl at the default tolerance), has a one-sided probability of 0.04 under the picked levels; it is one row in 32. All other ratios are at most 1.08.
2. **At default tolerances, the metric sets the cost.** The share of sites a prediction fails ranged from 1 % to 85 %, and the measurements from 233 to 821 sites on the same IR map. A relative tolerance of 10 % fails 73 % of the IR sites, while the record setting (0.10 + 10 %) fails 1 %, because absorbances in the window are mostly below 0.1 and the absolute term dominates.
3. **At equal difficulty, the cost differences shrink.** The spread became 338–453 sites on IR, 287–367 on NaCl and 398–461 on the synthetic map. What remains is where the wrong skips fall:
   - On IR, metrics with an absolute term, and the bases, put 72–83 % of the wrong skips on signal sites, which are 30 % of the skipped sites. The relative profile spreads them in proportion (37 % against 35 %).
   - On NaCl, the width claim puts only 6 % of its wrong skips on sites with the (200) line, against 66 % of the skipped sites. Its failures sit where the line is weak or absent. The profile and basis metrics put 83–92 % on the line.
4. **Wrong skips cluster under every metric.** At equal difficulty the clumping index lies between 1.5 and 3.0. Interpolation errors are spatially correlated, and the rate guarantee does not constrain their location.
5. **De-duplicating the basis changed little on these data.** At equal difficulty the plain and de-duplicated bases differ by at most 5 % in cost and 3 points in the share of wrong skips on signal. The seed designs are spatially uniform, and the merged sets (12–47 spectra) span nearly the same components as the full ones.


## SI 6.1 Where each metric sends the measurements

A metric decides which predictions fail, and so which sites the campaign measures. For the synthetic map and the NaCl scan, the peak or line-width metric was compared with the whole-profile metric, at default and at matched tolerances: 50 campaigns each, interpolation claim only. For each site, the frequency of being measured because no claim covered it was recorded; seed and calibration sites are left out, since they are the same under both metrics (Fig. S6).

**Synthetic map.**
- **Default tolerances.** The peak metric measured 40 sites per campaign and the profile metric 118.
- **Matched tolerances.** The peak metric measured 175 and the profile metric 133.
- **Little overlap.** The two metrics put only 16 % (default) and 31 % (matched) of their measurements on the same sites.
- **The peak metric** sends measurements to bands where the peak position and width drift with composition: the micellar interior (76 of 175 at matched tolerance) and the lower-left corner of the triangle.
- **The profile metric** sends them to phase boundaries. 45–46 % of its measurements fall on the 8.8 % of sites that border another phase, against 32 % for the peak metric. The boundary between the micellar phase and the emulsion is measured almost only under the profile metric.
- **Each metric follows its own sensitivity.** The frequency of measurement under the peak metric correlates with the local change in the peak descriptors (Spearman 0.72 at matched tolerance), and only weakly with the local change in the profile (0.15). Under the profile metric, the order of the two correlations reverses (0.41 and 0.49).

**NaCl scan.**
- **Default tolerances.** The width metric measured 419 sites per campaign and the profile metric 575, with 50 % overlap. The profile metric measures the whole grain.
- **Matched tolerances.** 51 and 100 sites, with 11 % overlap.
  - The width metric concentrates on the rim of the grain, where the (200) line appears and disappears and the claim fails on presence rather than on width.
  - The profile metric concentrates in the interior of the grain.
- **Correlations.** Measurement under the profile metric correlates with the local profile change (0.50–0.63). Measurement under the width metric shows little correlation with the local width change (0.34 and −0.03), since its failures are dominated by the presence of the line.

**Figure S6.** Frequency of measurement because no claim applied, over 50 campaigns, for the peak or line-width metric (left) and the profile metric (middle), and their difference (right; red: measured more under the profile metric). Rows: synthetic map at default and matched tolerances; NaCl scan at default and matched tolerances. File: `figures/figS6_sampling.png`.

Scripts and data: SI 4; summary in the run record, under the analysis of the metric study.

## SI 6.2 Where wrong interest skips fall on the synthetic map

The wrong skips of the synthetic map cluster in composition. The analysis below uses the quantile path with natural-neighbour interpolation at a budget of 0.20 and confidence 0.80; the score variants were run on the first 60 campaigns.

- **The guarantee held.** The record shows 161 exceedances in 1,500 level checks, against 170 allowed by the picked failure probabilities. The calibration draw is uniform within each level, so spatial correlation of the labels leaves it exchangeable with its level.
- **The budget sets the count, the score the location.** Three interest scores gave about the same number of wrong skips per campaign (Table S6.3). The quantile path raises its threshold until the calibration draw reaches its allowed failures, so the budget is spent whatever the score; only the sites it is spent on change.
- **The recorded score depends on signal shape.** The interest label asks for a dominant peak rising above its local baseline by at least five times that baseline, a relative criterion; call the height above baseline divided by the baseline the peak-to-baseline ratio. The recorded score uses the absolute height above baseline. The broad correlation peak of the micellar phase has a high ratio to its baseline and a small absolute height (median 0.43, against 5.5 for the Bragg peaks of the ordered phases). The score therefore ranks interesting micellar sites low, and 75 % of the wrong interest skips fall in that phase. The interpolated spectrum predicted a peak of at least five times baseline at 91 % of these sites: the prediction was right and the score misread it.
- **A score matched to the label moves the errors to the margin.** With scores based on the predicted peak-to-baseline ratio, the wrong skips are the least interesting of the interesting sites (median true ratio 8.4). The probability of a wrong skip falls from 0.72 at ratios of 5–8 to 0.05 above 40. Such sites form contiguous bands of composition where the ratio changes slowly near the threshold, so the errors still cluster.
- **The denominator matters.** The rate is taken over all sites of a level, and a third of the sites are of interest. With the recorded score, 35 % of the interesting sites on certified levels were skipped in error while every level met its budget. A bound on the share of interesting sites lost requires a label-conditional statement (Section 6, Scope of the guarantee).

**Table S6.3.** Interest scores on the synthetic map (60 campaigns, 360 level checks).

| Interest score | Wrong skips per campaign | Sites measured | Exceedances |
| --- | --- | --- | --- |
| Logistic on absolute peak height above baseline (recorded) | 270 | 333 | 37 / 360 |
| Logistic on peak-to-baseline ratio | 278 | 358 | 45 / 360 |
| Predicted peak-to-baseline ratio | 273 | 358 | 41 / 360 |

The record keeps the original score. It meets its guarantee, and the misranking it shows is the point of this section: a score decides where the budget is spent.

## SI 6.3 Summary of the metric study

Six acceptance metrics were compared on the three maps with the interpolation claim alone and 50 campaigns per metric: peak or line descriptors with absolute or relative tolerance, two forms of profile envelope, and the error in a basis of the seed spectra, plain or with near-duplicate spectra merged (SI 6). Every metric kept its guarantee. Over 32 combinations of metric, dataset and tolerance, the largest ratio of observed to expected exceedances was 1.37, with a one-sided probability of 0.04 under the picked failure probabilities, the smallest of 32 such probabilities and consistent with chance; all other ratios were at most 1.08.

The metric set the cost. At tolerances a practitioner might pick, the share of certified-level sites that a prediction fails ranged from 1 % to 85 %, and the IR map needed between 233 and 810 measurements. Scaling every tolerance so that 15 % of the sites fail, a control that uses the truth, brought the costs close: 338–453 sites on IR, 287–367 on NaCl and 398–461 on the synthetic map.

At equal difficulty the metric still decided where measurements go (Fig. S6). On the synthetic map the peak claim measured where the peak position and width drift with composition, in the micellar phase and in a band of the emulsion. The profile claim measured along the phase boundaries: 45–46 % of its measurements fell on the 8.8 % of sites next to another phase, against 32 % for the peak claim. The two claims placed 31 % of their measurements on the same sites, and 16 % at the default tolerances.

The metric also decided where wrong skips fall. Metrics with an absolute term put 72–83 % of the IR wrong skips on sites with signal, 30 % of the skipped sites, and the NaCl line-width claim put 6 % of its wrong skips on sites holding the line, 66 % of the skipped sites. Under every metric the wrong skips clustered, with another wrong skip among the six nearest neighbours 1.5 to 3.0 times as often as for wrong skips placed at random among the skipped sites. The rate also counts wrong skips over all sites of a level. On the synthetic map, where a third of the sites are of interest, 35 % of the interesting sites on certified levels were skipped in error while every level met its budget (SI 6.2).
