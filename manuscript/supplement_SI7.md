# SI 7. Campaigns guided by Gaussian-process uncertainty

Fig. 1 sets the certified campaign beside a campaign that skips on the strength of a model's own uncertainty, the rule most often used in autonomous mapping. Both run on the fully measured NaCl scan with the claim on the width of the (200) line, so every skip of either can be checked afterwards.

**Rule.** The uncertified campaign shares the hierarchical design and the seed sites of the certified one. After each level from 3 on, two Gaussian processes are fitted to all sites measured so far, one to the logarithm of the width at sites with the line, one to the presence indicator at all sites; each has a squared-exponential kernel with a white-noise term, and the hyperparameters maximise the marginal likelihood [RasmussenWilliams2006]. A site of the next level is skipped as having no line when the predicted presence falls below 0.1, and skipped as predictable when the predicted presence exceeds 0.9 and the interval of $z$ standard deviations on the width lies within the tolerance of 0.02 nm⁻¹. Every other site is measured. The standard deviation is taken either for the latent function or for a new observation, which adds the fitted noise; the rule was run at $z$ = 1, 1.64, 1.96 and 2.58. The rule involves no random draw, so each setting gives one campaign. Wrong skips are counted as for the certified campaign: a skip for want of a line is wrong where the line is present, a predictable skip is wrong where presence disagrees or the width misses by more than the tolerance.

**Result.** Table S7.1 lists the eight settings. With the latent standard deviation and $z$ = 1, the campaign measured 658 of 1071 sites and skipped 10 % of the sites of levels 3 to 6 wrongly, inside the spread of the 250 certified campaigns (mean 614 measured, 12 % wrong). The rate was uneven over the levels, 18 % at level 6 and none at levels 4 and 5, and the campaign itself carries no statement of it. Intervals of 90 % or wider allowed at most 31 predictable skips, and between 29 % and 32 % of those were wrong, against the 1 % to 10 % the intervals imply. With the predictive standard deviation, no interval of the width fell within the tolerance, and the campaign measured 922 sites.

**Table S7.1.** Uncertified campaigns on the NaCl (200)-width map.

| standard deviation | $z$ | implied miss rate | measured | predictable skips | of those wrong | wrong, levels 3–6 |
|---|---|---|---|---|---|---|
| latent | 1.00 | 0.32 | 658 | 266 | 0.37 | 0.10 |
| latent | 1.64 | 0.10 | 893 | 31 | 0.32 | 0.014 |
| latent | 1.96 | 0.05 | 903 | 21 | 0.29 | 0.010 |
| latent | 2.58 | 0.01 | 903 | 21 | 0.29 | 0.010 |
| predictive | 1.00–2.58 | 0.32–0.01 | 922 | 0 | — | 0.003 |

Certification applies to the Gaussian process as it does to natural-neighbour prediction. With the posterior mean as the frozen predictor and the length scale set by maximum likelihood, by the design or by the nonstationary rule (SI 1), 250 certified campaigns each skipped 12.3 % to 12.5 % of levels 3 to 6 wrongly on average and exceeded the budget on 111 to 123 of 1000 level runs, against 120 allowed; they measured 745 to 777 sites, against 614 with natural-neighbour prediction, because the posterior mean shrinks toward the average where the width scatters from site to site. The difference between the two kinds of campaign lies in what each knows. At equal cost the realised error is about equal; the certified campaign states its rate before any skip is checked, and the uncertified one learns its rate only from the full scan that a campaign exists to avoid.


## S7.2 The spectrum Gaussian process on all three maps

The rule of Section 5.3 uses the Gaussian process of the certified campaigns (Section 4.3), which predicts the full spectrum or profile at a site from the measured set. After each level is measured, the process is refitted with the length scale set by maximum marginal likelihood, and every unmeasured site of the next level is assessed against both claims. Posterior draws of the spectrum at a site are taken along the leading principal components of the measured spectra, which carry 99 % of the variance up to at most 20 components, with the component variances scaled by the posterior standard deviation at the site; 64 draws per site, clipped at zero. The stated probability that a claim fails at a site is the share of draws for which it fails: for the interest claim, the share of draws that are of interest; for the interpolation claim, the share of draws that fail the acceptance metric against the posterior mean. A site is skipped under a claim when its stated probability is at most α, and a site skipped under both claims is stated to fail with probability $1 - (1 - p_a)(1 - p_b)$. The stated share of wrong skips of a campaign is the sum of these probabilities over its skipped certified-level sites, divided by the number of certified-level sites.

Three standard deviations are used: the latent one, the predictive one, which adds the fitted noise variance, and the predictive one multiplied by a factor fixed on each level from the measured set, the 68 % quantile of the absolute leave-one-out residuals in units of their predictive standard deviation. A factor below one means the measured sites are predicted better than the process states, and the rescaled campaign then skips more.

**Table S7.2.** Uncertified spectrum Gaussian-process campaigns, ranges over α from 0.01 to 0.32. Shares are of the certified-level sites.

| map | standard deviation | stated share wrong | realised share wrong | measured |
|---|---|---|---|---|
| IR (959 sites) | latent | 0–7.4 % | 1.0–3.3 % | 73–191 |
| | predictive | 0–9.1 % | 0.7–2.3 % | 73–398 |
| | rescaled (factor 0.40) | 0–3.7 % | 1.6–4.5 % | 73–75 |
| NaCl (1071 sites) | latent | 0–0.7 % | 0.1–1.6 % | 1042–1070 |
| | predictive | 0–0.1 % | 0.1–0.4 % | 1064–1070 |
| | rescaled (factor 0.19–0.89) | 0–2.1 % | 0.1–5.8 % | 959–1070 |
| synthetic (2118 sites) | latent | 0–4.0 % | 13.8–38.7 % | 289–550 |
| | predictive | 0–3.5 % | 10.9–30.5 % | 368–580 |
| | rescaled (factor 0.23–0.87) | 0–3.8 % | 16.1–41.0 % | 340–503 |

On IR, 73 sites form the seed, so a campaign at 73 measured sites skipped every certified-level site. On the synthetic map, sites skipped under the interest claim alone were wrong 0 to 2 times out of 293 to 509; the wrong skips failed the tolerance, 166 to 261 of the 548 to 632 sites skipped under the interpolation claim alone and 59 to 591 of the 572 to 832 skipped under both. On NaCl the noise variance, about three quarters of the variance of the width, makes the predictive process unwilling to skip.

## S7.3 Certified campaigns at several budgets

For Fig. 7 the quantile path was run at budgets $\varepsilon$ of 0.05, 0.10, 0.20 and 0.30 on the shared wrong-skip rate, at the confidences of Section 4.3, with natural-neighbour prediction (20 campaigns per budget) and Gaussian-process prediction with the length scale by maximum likelihood (8 campaigns per budget).

**Table S7.3.** Certified campaigns by budget: sites measured (mean ± standard deviation) and, in brackets, the mean realised share of the certified-level sites skipped wrongly. NN, natural-neighbour prediction; GP, Gaussian-process prediction.

| map | predictor | ε = 0.05 | ε = 0.10 | ε = 0.20 | ε = 0.30 |
|---|---|---|---|---|---|
| IR | NN | 473 ± 70 (1.5 %) | 312 ± 58 (3.4 %) | 233 ± 1 (4.1 %) | 233 ± 0 (4.1 %) |
| | GP | 410 ± 66 (1.5 %) | 271 ± 31 (3.7 %) | 233 ± 1 (4.3 %) | 233 ± 0 (4.3 %) |
| NaCl | NN | 898 ± 52 (1.9 %) | 806 ± 69 (4.5 %) | 631 ± 69 (11.5 %) | 484 ± 47 (19.9 %) |
| | GP | 1022 ± 23 (2.2 %) | 963 ± 54 (4.2 %) | 767 ± 69 (11.5 %) | 624 ± 65 (18.3 %) |
| synthetic | NN | 461 ± 16 (2.2 %) | 415 ± 22 (4.9 %) | 334 ± 25 (12.8 %) | 285 ± 12 (21.5 %) |
| | GP | 1900 ± 148 (2.7 %) | 1678 ± 178 (5.5 %) | 1140 ± 302 (13.2 %) | 752 ± 188 (21.0 %) |

On IR, 233 sites is the floor: 73 seed sites and 160 calibration draws. Above a budget of 0.10 every predicted skip is admitted, and the realised share stays at the rate the predictor makes.
