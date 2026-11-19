# SI 6. What the certified metric does to a campaign (draft 1)

A skip asserts that a prediction meets an acceptance metric, and the choice of metric is part of the guarantee. This section measures how the metric changes the measurements spent, the attainment of the bound and the place where wrong skips fall. The guarantee itself does not depend on the metric (Appendix A).

**Set-up.**
- **Campaigns.** The interpolation certificate alone, with the quantile path and natural-neighbour interpolation. Budgets as in Section 5: $R_E \le 0.10$ at confidence 0.75 for the IR map, $R_E \le 0.20$ at confidence 0.80 for the NaCl scan and the synthetic map. 50 campaigns per metric (seeds 0–49).
- **What changes.** Only the acceptance metric.
- **Signal sites.** Sites marked by the dataset's interest label: absorbance above 0.1 for IR, the (200) line present for NaCl, a dominant peak at least five times its local baseline for the synthetic map. The label distinguishes signal from background here and plays no part in the decisions.

**Metrics.**

| Metric | A skip asserts that |
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

Scripts and data: SI 4; summary in the run record, under the analysis of the metric study.
