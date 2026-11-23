# 4 Experiments (draft 1)

## 4.1 Datasets

Every guarantee in this study can be checked, because each dataset is measured at every design site. Three datasets cover a simulation with known phase structure, a diffraction scan and a spectroscopic map.

*Synthetic small-angle scattering map.* A forward model of a surfactant–oil–water formulation maps a composition in the triangle $x + y \le 1$ to a scattering curve on 240 logarithmically spaced points between 0.005 and 0.32 Å⁻¹. The model has a micellar phase, an ordered cubic phase, a hexagonal phase and an oil-rich emulsion, with smoothed transitions. A hierarchical Poisson-disk design on the unit square with nine levels, restricted to the triangle, gives 2118 sites. The interpolant uses mirror images across the walls of the triangle.

*NaCl microdiffraction scan.* A raster of 3249 sites on a 0.25 mm stage grid, with curves of 1000 bins between 0.59 and 38.9 nm⁻¹ [ALSNaCl]. A seven-level design, snapped to the raster, gives 1071 sites.

*Infrared map.* A bioreef sample mapped on 29 × 42 pixels of 1 µm, with 1738 channels between 650 and 4000 cm⁻¹. Each spectrum is corrected for resonant Mie scattering pixel by pixel, and the window 1500–1850 cm⁻¹, which holds the amide and ester bands, is used. A seven-level design drawn on the physical rectangle and snapped to pixels gives 959 sites. SI 2 describes the correction and the design.

Figure 3 shows each dataset as a map, with a site its claim accepts and one it rejects.

**Figure 3.** The three datasets and how their claims judge a prediction; rows: IR map, NaCl scan, synthetic map. Left column, the quantity the claims test: (a) amide-I absorbance, maximum over 1620–1690 cm⁻¹ after scattering correction, 1 µm pixels; (d) height of the (200) line where it stands five times the noise above its baseline, grey where absent, the width varying from pixel to pixel by more than the tolerance of the width claim; (g) position of the dominant peak where its prominence reaches 5, grey elsewhere, white lines: phase boundaries of the forward model. Middle and right columns: one site of a certified level that the claim accepts and one it rejects, predicted from the measured sites of the coarser levels by natural-neighbour weights (grey: neighbours, line width by weight; orange: prediction; black: measurement; shaded: tolerance). IR envelope claim: within 10 % + 0.10 absorbance on average over channels above 0.02. NaCl width claim: widths at half maximum (bars) within 0.02 nm⁻¹. Synthetic profile claim, drawn as the deviation of each channel in units of the envelope 0.005 × intensity + 0.005 (shaded: ±1; inset: the measured profile on log–log axes); the claim holds when the mean over channels is at most one, so a few channels near a peak may lie outside. File: `figures/fig_datasets_claims.png`.

## 4.2 Claims and tolerances

The IR map and the NaCl scan each carry one interest claim and one interpolation claim, fixed before any run. On the synthetic map every site is of interest, and the interpolation claim alone is made, on the full profile.

**Table 2.** Claims, fixed before any run.

| Dataset | Interest: a site holds | Interpolation: the prediction from coarser levels meets |
| --- | --- | --- |
| Synthetic map | every site (no interest claim) | every point of the profile within 0.5 % + 0.005, on average over the 240 points |
| NaCl scan | the (200) line at 22.28 nm⁻¹, at least five times the noise above its local baseline | the (200) width within 0.02 nm⁻¹, the median width difference between neighbouring design sites |
| IR map | absorbance of 0.1 or more in some channel of the window | every channel within 10 % + 0.10 absorbance, on average over channels above 0.02 |

The NaCl tolerance was set from the widths measured over the full scan, without a model of what makes them vary: ten times above the precision of the width and at the median difference between neighbouring design sites (SI 2). A second setting of the IR map tightens the envelope to 10 % + 0.01, with interest at 0.02 and channels counted above 0.005. Under it, interpolation rather than interest decides the cost. The choice of claim shapes the campaign as much as the budget does; Section 5.5 and SI 6 compare six metrics on the three datasets.


## 4.3 Protocols

A protocol pairs a predictor with the scores it supplies, so a difference in cost between protocols reflects both.

**Natural-neighbour protocol.** Natural-neighbour (Sibson) coordinates [Sibson1981] predict the spectrum at a site as a weighted mean of the measured spectra around it. One set of weights per site serves every channel and every derived quantity. The weights are non-negative and sum to one, so a prediction from non-negative spectra is non-negative. The coordinates are computed exactly by clipping Voronoi cells (SI 1); outside the hull of the measured set, inverse-distance weights over the five nearest measured sites take over.

Both scores are probabilities from logistic regressions fitted on the measured set, the interpolation score on the disagreement between natural neighbours and on position, the interest score on the predicted signal and its spread among the nearest measured sites; on the IR map the interest score is the predicted maximum in the window, capped below the interest level (SI 1). The random scorer of Section 5.4 assigns every site an independent uniform weight.

**Gaussian-process protocols.** Gaussian-process regression is the interpolator of choice for autonomous scattering experiments [Noack2019; Noack2020], and it offers a reason for every measurement: the posterior standard deviation is large where the measured set is far away in units of the length scale. The GP protocols place an isotropic squared-exponential kernel on the coordinates of the hierarchical design and evaluate the process only at design sites [RasmussenWilliams2006]. The posterior mean, clipped at zero because every spectrum here is non-negative, predicts the full spectrum at a site, and the posterior standard deviation at unit output scale orders the sites for the interpolation claim. Both depend on the measured set through one set of linear weights, so the spectrum and any quantity derived from it come from the same fit, as with natural-neighbour coordinates. The interest claim keeps its score from the natural-neighbour protocol, which isolates the change of interpolator.

The length scale is set in three ways, each fixed before the calibration draw of a level: by maximum marginal likelihood on the leading principal-component scores of the measured spectra [Balandat2020], by the median nearest-neighbour spacing of the design through the finest level measured, or locally, through a Gibbs kernel whose length scale is the distance to the third-nearest measured site [Gibbs1997; PaciorekSchervish2004]. SI 1 gives the details.

**Common settings.** Levels up to the second form the seed and are measured in full. Every finer level is calibrated on $m = 40$ sites, or on the whole level when it is smaller. The guarantee on the shared wrong-skip rate is $R_E \le 0.10$ at confidence 0.75 on the IR map, $R_E \le 0.20$ at confidence 0.80 on the NaCl scan and $R_E \le 0.10$ at confidence 0.80 on the synthetic map. The per-claim form gives each claim half the budget at half the failure probability, so the union bound returns the same statement; with the one claim of the synthetic map the three forms coincide. Every rule uses the exact finite-population tail, and the threshold is placed at the score of the first calibration failure beyond those allowed.

**Paired comparison (Fig. 1).** One question needs model, ranking and calibration sample held fixed: does the model's own uncertainty, or a threshold set from the calibration sample, keep a rate stated before the round? On the NaCl scan, 80 fresh hierarchical designs over the raster, about 1075 sites each, measure levels up to the third as the seed, about 143 sites, and decide the three finer levels in three rounds of about 135, 268 and 528 sites. Before a round, two Gaussian processes with a squared-exponential kernel, one regressing presence of the (200) line on position and one the logarithm of its width, are fitted on the measured sites and frozen. They give at every site of the round a probability that a skip is wrong, the line predicted present with a width off by more than the tolerance or its presence predicted wrongly, and this probability ranks the sites. A uniform sample of 40 sites is then measured. On the remaining sites both cuts are computed on the identical state, with one target: at most a fifth of the round skipped wrongly, with probability 0.80. The uncertainty of the model sets the longest prefix of the ranking whose number of wrong skips meets the target under 2000 joint draws from the processes, presence drawn site by site and log width jointly from the full predictive covariance. Conformal thresholds set the largest threshold whose exact hypergeometric upper limit from the calibration labels, less the calibration failures already seen, meets the target. One of the two cuts decides which sites are measured and enter the next fit. Three kernels are run: noise level fitted by marginal likelihood; noise fixed at 10⁻⁴ of the variance, a common interpolating choice; and noise fixed with the length scale held at 1 mm or more, the assumption that the width varies smoothly at the spacing of the design, where maximum likelihood gives about 0.23 mm. A stock-picking chicken replaces the model by a measured site chosen at random for each prediction and by a random ranking; it states nothing about its own errors and runs under the conformal thresholds only. SI 7.4 gives the details.

**Table 3.** Exchangeable parts of a campaign.

| Part | Options used |
| --- | --- |
| Design | Hierarchical Poisson-disk design; seed of levels 0–2; 7 (NaCl, IR) or 9 (synthetic) levels |
| Interpolator | Natural-neighbour coordinates; Gaussian process with length scale by maximum likelihood, by design spacing or by local spacing |
| Interest score | Predicted maximum (IR); logistic on predicted peak height (NaCl); random; none on the synthetic map |
| Interpolation score | Logistic on neighbour disagreement; GP posterior standard deviation; random |
| Form of guarantee | Per-claim budgets; quantile path; priority path |
| Calibration | 40 sites per level, uniform without replacement, exact hypergeometric tail |

## 4.4 Evaluation

A guarantee about a probability needs repetition to be checked. Each of 34 configurations was run as 250 campaigns, 20 for the four Gaussian-process configurations of the synthetic map and 50 for one on NaCl, that differ only in their calibration draws and, for the random scorer, in the score stream. Every certified level of every campaign gives one level check against the budget, and the checks over budget are compared with the number expected under the picked failure probabilities (Section 3.3). For the first 20 campaigns of each configuration, the calibration draw was also repeated 1000 times on the recorded level populations, which isolates the randomness of the draw (SI 4, SI 5). Four studies extend the record (SI 10): a label-conditional bound, drift, an audit of finished maps and the cost of a plan against its calibration size and confidence.

---

## Notes for revision (not part of the text)

- *Isotropy.* Done: the IR design is drawn on the physical rectangle and both interpolators use micrometres (divided by 41 µm, an isotropic rescaling); the scattering maps keep the unit square of their design. SI 2 describes the IR preparation.
- *Interest score.* Kept from the natural-neighbour protocol on purpose; only the interpolator and the interpolation score change. If a reviewer asks for a fully GP protocol, a GP-predicted maximum is a small addition.
- *Mirror images.* The synthetic map uses mirror images at the composition walls for natural-neighbour interpolation. The GP protocols use none.
- References to add: [Sibson1981] Sibson (1981), A brief description of natural neighbour interpolation, in Interpreting Multivariate Data, Wiley, 21–36. [RasmussenWilliams2006] Rasmussen, Williams (2006), Gaussian Processes for Machine Learning, MIT Press. [Balandat2020] Balandat et al. (2020), BoTorch, NeurIPS 33. [Gibbs1997] Gibbs (1997), PhD thesis, Cambridge. [PaciorekSchervish2004] Paciorek, Schervish (2004), NeurIPS 16. Consider Noack & Sethian (2022) on non-stationary kernels for autonomous experiments (check details).
