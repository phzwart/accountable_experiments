# SI 8. The record of measured sites

A certified skip carries its claim and its bound; a certified measurement can carry a record of equal standing. Every site of a certified level is decided from a frozen prediction, a score per claim and the certified cut of its level, so the reason for a measurement is fixed before the measurement is taken. The measurement then adds the outcome, and the record shows whether the site was needed.

**The record.** Table S8.1 lists the entries kept for each design site. The decision entries are written before the site is measured or skipped; the outcome entries follow from the measurement, for skipped sites from the full scan available in a retrospective study. The residual is the departure of the frozen prediction from the measurement in units of the tolerance, so that a skip under the interpolation claim fails above one; where the presence of the feature decides, agreed absence counts as zero and disagreement as infinite. The quantile of a residual is its randomised conformal p-value among the calibration residuals of the same level [Vovk2005]: the share of calibration residuals above it, with ties broken by a uniform draw. A p-value below 0.2 places a residual among the largest fifth of the calibration residuals of its level. Calibration sites are a uniform draw from their level, so each fifth would hold 20 % of the sites measured by choice if the score carried no information; the largest fifth holds more to the degree that the score finds the sites the prediction misses.

**Table S8.1.** Entries of the record of each design site.

| entry | written | content |
|---|---|---|
| level | before | level of the hierarchical design |
| action | before | measured as seed, as calibration draw or by choice (no claim covers the site); skipped as not of interest, as predictable or both |
| score, cut | before | score of each claim and the certified cut of the level; a claim covers the site when its score is at or below the cut |
| margin, rank | before | score minus cut; rank of the score within the level |
| prediction | before | frozen prediction of the feature (presence, width, peak position or band envelope) |
| measurement | after | measured feature |
| residual | after | departure of the prediction from the measurement, in tolerances |
| labels | after | the prediction fails (residual above one); the site is of interest |
| p-value | after | randomised conformal p-value of the residual among the calibration residuals of the level |

**Campaigns.** The record was written for one campaign of average cost per dataset, replayed with its recorded seed: for the NaCl scan the campaign of Fig. 1, for the IR map and the synthetic map the campaign whose number of measurements lies closest to the mean of 250, with ties broken by the number of wrong skips. Each replay reproduced the recorded actions site by site. The failure and interest labels are part of the record of all 250 campaigns per dataset, so the shares in Table S8.2 pool those campaigns; the p-values come from the replayed campaigns. A site measured by choice is needed when every claim would have skipped it wrongly, that is when it is of interest and its prediction fails.

**Table S8.2.** Measured sites at the certified levels. Sites: design sites of the certified levels; drawn, chosen: calibration draws and sites measured by choice per campaign; fails, of interest, needed: shares among sites drawn / chosen. Counts and shares pool 250 campaigns per dataset. The last column, the share of sites measured by choice whose residual lies among the largest fifth of the calibration residuals of its level, comes from the replayed campaign and equals 0.20 for a score without information.

| dataset | sites | drawn | chosen | fails | of interest | needed | largest fifth |
|---|---|---|---|---|---|---|---|
| NaCl width | 995 | 160 | 378 | 0.52/0.60 | 0.66/0.86 | 0.35/0.47 | 0.18 |
| IR amide I | 886 | 160 | 62 | 0.014/0.021 | 0.38/0.79 | 0.013/0.019 | 0.21 |
| synthetic peak | 2079 | 233 | 62 | 0.20/0.45 | 0.34/1.00 | 0.097/0.45 | 0.53 |

**What the record shows.** On the synthetic map the score finds the sites the prediction misses: 45 % of the sites measured by choice were needed, against 10 % of sites drawn at random, and half of their residuals lie among the largest fifth of the calibration residuals (Fig. S8c, f). On the NaCl scan the sites measured by choice were needed in 47 % of cases against 35 % at random, and their residuals spread evenly over the fifths of the calibration residuals (Fig. S8a, d). The width scatters from site to site by about the tolerance (SI 7), so half of all predictions fail whatever the score, and the cost of the guarantee falls on sites that the score cannot tell apart. On the IR map almost no prediction fails, 1.4 % at random; the sites measured by choice are mostly of interest (79 %) and predictable within tolerance (Fig. S8b, e). The certified cut of each level, set from a calibration draw of 40 sites, stopped short of them; their measurement is the price of a finite calibration draw, and a larger draw or a looser budget moves the cut outward.

**Table S8.3.** Excerpt of the record of the campaign of Fig. 1 (NaCl scan, level 5). Action: measured as calibration draw or by choice, skipped as predictable, as not of interest or both. Interest, interp.: scores of the two claims, against cuts of 0.22 and 0.28; rank of the interpolation score within the level in brackets. Predicted and measured (200) widths in nm⁻¹; "none" marks a predicted or measured absence of the line.

| site | action | interest | interp. (rank) | predicted | measured | residual | p | outcome |
|---|---|---|---|---|---|---|---|---|
| 510 | calibration | 0.58 | 0.25 (0.26) | 0.122 | 0.143 | 1.04 | 0.52 | fails |
| 338 | by choice | 1.00 | 0.53 (0.66) | 0.155 | 0.085 | 3.50 | 0.23 | needed |
| 363 | by choice | 1.00 | 0.38 (0.52) | 0.123 | 0.117 | 0.27 | 0.77 | not needed |
| 440 | predictable | 0.40 | 0.24 (0.24) | 0.115 | 0.105 | 0.48 | 0.66 | right |
| 390 | predictable | 0.98 | 0.27 (0.32) | 0.094 | 0.041 | 2.62 | 0.28 | wrong |
| 502 | not of interest | 0.13 | 0.42 (0.59) | none | none | 0 | 0.98 | right |
| 497 | both | 0.13 | 0.17 (0.02) | none | none | 0 | 0.81 | right |

**Use and limits.** The p-values of sites measured by choice judge the score; they carry no information on the guarantee, which rests on the calibration draw alone. Sites measured by choice are selected by their scores, so their residuals are not exchangeable with the calibration residuals of their level and cannot be added to that calibration after the fact. They enter the fit of the next level, whose calibration is a fresh uniform draw. Across campaigns, the record of measured sites points to where a better score would save measurements: on the synthetic map little is left to gain, on the NaCl scan the scatter of the width limits any score, and on the IR map the calibration draw sets the cost.

**Figure S8.** The record of measured sites for one campaign of average cost per dataset. (a–c) Error of the frozen prediction divided by the tolerance (NaCl: width error ÷ 0.02 nm⁻¹; synthetic map: the larger of peak-position error ÷ 0.005 and peak-width error ÷ 0.001; IR map: mean over channels of the absorbance error ÷ (0.10 × absorbance + 0.10)) at every site of the certified levels, grouped by action: skipped as predictable only, skipped under both claims (wrong only where the line is also of interest), measured as a random calibration draw, measured by choice. Red: one, a miss by exactly the tolerance; above it the prediction fails; ≈0: agreed absence or a residual below 0.013; ∞: presence predicted wrongly. Percentages give the share above the tolerance over 250 campaigns. (d–f) Residuals of the sites measured by choice, ranked among the calibration residuals of their level (randomised conformal p-value, SI 8 text): share falling in each fifth of the calibration residuals, from the largest to the smallest. Dashed: 20 %, expected if measuring by choice were no better than drawing at random. Titles give the share of sites needed among those measured by choice and among those drawn at random, over 250 campaigns. File: `figures/figS8_measured.png`.
