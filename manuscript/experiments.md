# 4 Experiments (draft 1)

## 4.1 Datasets

Every guarantee in this study can be checked, because each dataset is measured at every design site. Three datasets cover a simulation with known phase structure, a diffraction scan and a spectroscopic map.

*Synthetic small-angle scattering map.* A forward model of a surfactant–oil–water formulation maps a composition in the triangle $x + y \le 1$ to a scattering curve on 240 logarithmically spaced points between 0.005 and 0.32 Å⁻¹. The model has a micellar phase, an ordered cubic phase, a hexagonal phase and an oil-rich emulsion, with smoothed transitions. A hierarchical Poisson-disk design on the unit square with nine levels, restricted to the triangle, gives 2118 sites. The interpolant uses mirror images across the walls of the triangle.

*NaCl microdiffraction scan.* A raster of 3249 sites on a 0.25 mm stage grid, with curves of 1000 bins between 0.59 and 38.9 nm⁻¹ [ALSNaCl]. A seven-level design, snapped to the raster, gives 1071 sites.

*Infrared map.* A bioreef sample mapped on 29 × 42 pixels of 1 µm, with 1738 channels between 650 and 4000 cm⁻¹. Each spectrum is corrected for resonant Mie scattering pixel by pixel, and the window 1500–1850 cm⁻¹, which holds the amide and ester bands, is used. A seven-level design drawn on the physical rectangle and snapped to pixels gives 959 sites. SI 2 describes the correction and the design.

## 4.2 Claims and tolerances

Each dataset carries one interest claim and one interpolation claim, fixed before any run.

| Dataset | Interest: a site holds | Interpolation: the prediction from coarser levels meets |
| --- | --- | --- |
| Synthetic map | a dominant peak rising above its local baseline by at least five times that baseline | the dominant-peak position within 0.005 Å⁻¹ and its width within 0.001 Å⁻¹ |
| NaCl scan | the (200) line at 22.28 nm⁻¹, at least five noise levels above its local baseline | the (200) width within 0.02 nm⁻¹, about half a detector bin |
| IR map | absorbance of 0.1 or more in some channel of the window | every channel within 10 % + 0.10 absorbance, on average over channels above 0.02 |

A second setting of the IR map tightens the envelope to 10 % + 0.01, with interest at 0.02 and channels counted above 0.005. Under it, interpolation rather than interest decides the cost. The choice of claim shapes the campaign as much as the budget does; Section 5.5 and SI 6 compare six metrics on the three datasets.

## 4.3 Protocols

**Natural-neighbour protocol.** Natural-neighbour (Sibson) coordinates [Sibson1981] predict the spectrum at a site as a weighted mean of the measured spectra around it. One set of weights per site serves every channel and every derived quantity. The coordinates are computed exactly by clipping Voronoi cells (SI 1); outside the hull of the measured set, inverse-distance weights over the five nearest measured sites take over.

The interpolation score is one minus the probability of acceptance from a logistic regression. The regression is fitted by leave-one-out on the measured set (at most 120 sites), on the disagreement between natural neighbours in units of the acceptance metric and on the position. The interest score depends on the dataset. On the IR map it is the predicted maximum in the window, capped below the interest level, so that a site predicted to be of interest is never covered. On the two scattering datasets it is the probability of interest from a logistic regression on the predicted peak height above its baseline, the spread of that height over the five nearest measured sites and the distance to the nearest of them. The random scorer of Section 5.1 assigns every site an independent uniform weight.

**Gaussian-process protocols.** Gaussian-process regression is the interpolator of choice for autonomous scattering experiments [Noack2019; Noack2020], and it offers a reason for every measurement: the posterior standard deviation is large where the measured set is far away in units of the length scale. The GP protocols place an isotropic squared-exponential kernel on the coordinates of the hierarchical design and evaluate the process only at design sites [RasmussenWilliams2006]. The posterior mean predicts the full spectrum at a site; the posterior standard deviation at unit output scale orders the sites for the interpolation certificate. Both depend on the measured set through one set of linear weights, so the spectrum and any quantity derived from it come from the same fit, as with natural-neighbour coordinates. The interest certificate keeps its score from the natural-neighbour protocol, which isolates the change of interpolator.

The length scale is set in three ways, each fixed before the calibration draw of a level. In the first, it maximises the marginal likelihood of the leading three principal-component scores of the measured spectra, with one length scale shared by the components [Balandat2020]. In the second, it equals the median nearest-neighbour spacing of the design through the finest level already measured, a quantity known before the experiment starts. In the third, the length scale varies across the sample: a Gibbs kernel [Gibbs1997; PaciorekSchervish2004] takes as local length scale the distance to the third-nearest measured site. Measurements guided by the interest certificate cluster where the sample holds something of interest and thin out elsewhere, so the local length scale is short in the first regions and long in the second. Details, including the nugget and the bounds on the length scale, are in SI 1.

**Common settings.** Levels up to the second form the seed and are measured in full. Every finer level is calibrated on $m = 40$ sites, or on the whole level when it is smaller. The guarantee on the shared wrong-skip rate is $R_E \le 0.10$ at confidence 0.75 on the IR map and $R_E \le 0.20$ at confidence 0.80 on the NaCl and synthetic maps. The per-claim form splits it as in Section 5.2. Every rule uses the exact finite-population tail, and the threshold is placed at the score of the first calibration failure beyond those allowed.

**Table 1.** Exchangeable parts of a campaign.

| Part | Options used |
| --- | --- |
| Design | Hierarchical Poisson-disk design; seed of levels 0–2; 7 (NaCl, IR) or 9 (synthetic) levels |
| Interpolator | Natural-neighbour coordinates; Gaussian process with length scale by maximum likelihood, by design spacing or by local spacing |
| Interest score | Predicted maximum (IR); logistic on predicted peak height (NaCl, synthetic); random |
| Interpolation score | Logistic on neighbour disagreement; GP posterior standard deviation; random |
| Form of guarantee | Per-claim budgets; quantile path; priority path |
| Calibration | 40 sites per level, uniform without replacement, exact hypergeometric tail |

## 4.4 Evaluation

A guarantee about a probability needs repetition to be checked. Each of 36 configurations was run as 250 campaigns that differ only in their calibration draws and, for the random scorer, in the score stream. Every certified level of every campaign gives one level check: the realised wrong-skip rate, computed against the truth, is compared with the budget. The number of checks over budget is compared with the number allowed by the failure probability the rule picked on each level (Section 5.1). For the first five campaigns of each configuration, the calibration draw was also repeated 500 times on the recorded level populations, which isolates the randomness of the draw. The record, its format and the code are described in SI 4 and SI 5.

---

## Notes for revision (not part of the text)

- *Isotropy.* Done: the IR design is drawn on the physical rectangle and both interpolators use micrometres (divided by 41 µm, an isotropic rescaling); the scattering maps keep the unit square of their design. SI 2 describes the IR preparation.
- *Interest score.* Kept from the natural-neighbour protocol on purpose; only the interpolator and the interpolation score change. If a reviewer asks for a fully GP protocol, a GP-predicted maximum is a small addition.
- *Mirror images.* The synthetic map uses mirror images at the composition walls for natural-neighbour interpolation. The GP protocols use none.
- References to add: [Sibson1981] Sibson (1981), A brief description of natural neighbour interpolation, in Interpreting Multivariate Data, Wiley, 21–36. [RasmussenWilliams2006] Rasmussen, Williams (2006), Gaussian Processes for Machine Learning, MIT Press. [Balandat2020] Balandat et al. (2020), BoTorch, NeurIPS 33. [Gibbs1997] Gibbs (1997), PhD thesis, Cambridge. [PaciorekSchervish2004] Paciorek, Schervish (2004), NeurIPS 16. Consider Noack & Sethian (2022) on non-stationary kernels for autonomous experiments (check details).
