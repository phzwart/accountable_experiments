# SI 7. Campaigns guided by Gaussian-process uncertainty

Section 5.2 sets the guaranteed plan beside campaigns that skip on the strength of a model's own uncertainty. The campaigns of S7.1 run on the fully measured NaCl scan with the claim on the width of the (200) line, so every skip of either can be checked afterwards. The rule without a guarantee is a skip rule on the same fixed design; campaigns driven by an acquisition function choose their sites differently and are tested in SI 10.3.

**Rule.** The campaign without a guarantee shares the hierarchical design and the seed sites of the guaranteed one. After each level from 3 on, two Gaussian processes are fitted to all sites measured so far, one to the logarithm of the width at sites with the line, one to the presence indicator at all sites; each has a squared-exponential kernel with a white-noise term, and the hyperparameters maximise the marginal likelihood [RasmussenWilliams2006]. A site of the next level is skipped as having no line when the predicted presence falls below 0.1, and skipped as predictable when the predicted presence exceeds 0.9 and the interval of $z$ standard deviations on the width lies within the tolerance of 0.02 nm⁻¹. Every other site is measured. The standard deviation is taken either for the latent function or for a new observation, which adds the fitted noise; the rule was run at $z$ = 1, 1.64, 1.96 and 2.58. The rule involves no random draw, so each setting gives one campaign. Skip errors are counted as for the guaranteed plan: a skip for want of a line is wrong where the line is present, a predictable skip is wrong where presence disagrees or the width misses by more than the tolerance.

**Stated rate.** The process states, for every skip, its own probability that the skip is wrong. With $p$ the predicted presence clipped to $[0, 1]$, a skip for want of a line is wrong with probability $p$. A predictable skip is right when the line is present and the width lies within the tolerance of the predicted width $\hat w$; with the logarithm of the width normal with mean $\mu$ and standard deviation $s$, latent or predictive, its probability of being wrong is

$$
1 - p \, [\Phi((\log(\hat w + t) - \mu)/s) - \Phi((\log(\hat w - t) - \mu)/s)]
$$

with $t$ the tolerance and $\Phi$ the standard normal distribution function. The stated share of a campaign is the sum of these probabilities over its skips on levels 3 to 6, divided by the number of sites on those levels, the quantity the guarantee bounds.

**Result.** Table S7.1 lists the eight settings. The latent standard deviation leaves out the noise that a single measurement carries, so it is the wrong quantity for a claim judged against one measurement; its rows are given for completeness. With the latent standard deviation and $z$ = 1 the campaign measured 658 of 1071 sites, stated 3.5 % of the sites of levels 3 to 6 wrong and skipped 10.4 % wrongly; the shortfall was largest on the last level, 6.4 % stated against 18 % realised. At $z$ of 1.64 to 2.58 it measured 893 to 903 sites, stated 0.4 % to 0.5 % and realised 1.0 % to 1.4 %. With the predictive standard deviation no interval of the width fell within the tolerance, so every skip was a skip for want of a line; the campaign measured 922 sites, stated 0.4 % and realised 0.3 %.

**Table S7.1.** Campaigns without a guarantee on the NaCl (200)-width map. Stated and realised shares are of the sites of levels 3 to 6.

| standard deviation | $z$ | measured | predictable skips | stated share wrong | realised share wrong |
|---|---|---|---|---|---|
| latent | 1.00 | 658 | 266 | 3.5 % | 10.4 % |
| latent | 1.64 | 893 | 31 | 0.5 % | 1.4 % |
| latent | 1.96 | 903 | 21 | 0.4 % | 1.0 % |
| latent | 2.58 | 903 | 21 | 0.4 % | 1.0 % |
| predictive | 1.00–2.58 | 922 | 0 | 0.4 % | 0.3 % |

The guarantee applies to the Gaussian process as it does to natural-neighbour prediction. With the posterior mean as the frozen predictor and the length scale set by maximum likelihood, by the design or by the nonstationary rule (SI 1), 250 guaranteed campaigns each skipped 12.3 % to 12.5 % of levels 3 to 6 wrongly on average and exceeded the budget on 111 to 123 of 1000 level runs, against 120 expected; they measured 745 to 777 sites, against 614 with natural-neighbour prediction, because the posterior mean shrinks toward the average where the width scatters from site to site. The guaranteed Gaussian process measured fewer sites than the one without a guarantee with the predictive standard deviation, 745 to 777 against 922, and its rate was fixed before any skip was checked; the campaigns without a guarantee learn their realised rate only from the full scan that a campaign exists to avoid.


The comparison can hold model and ranking fixed (Fig. S7b). With the process refitted after each level, predicting the full profile, and its own posterior probability of a skip error as the frozen score, a guaranteed plan measured 761 ± 68 of 1071 sites over 50 campaigns and exceeded the budget on 16 of 200 level checks, against 24 expected; skipping where that same probability was at most α, for α from 0.01 to 0.32, the process measured 1064 to 1070.

**Figure S7b.** One Gaussian process on the NaCl scan, claim on the width of the (200) line, 1071 design sites. (a) A guaranteed plan of average cost with the process as predictor and its own posterior probability of a skip error as the frozen score: at most 20 % of each level skipped in error, with confidence 0.80 for that level. (b) The same process skipping a site when that probability is at most α = 0.20. Crosses mark skip errors, found afterwards against the full scan. (c) Share of the sites on guaranteed levels skipped in error: stated in advance (bar) and realised (dot), with sites measured. For the process without a guarantee the statement is its own probability summed over its skips; for the guaranteed plans it is the bound, with the mean and 5–95 % range of 50 campaigns with the process and 250 with natural-neighbour prediction. File: `figures/fig_hook_three.png`.

## S7.2 The spectrum Gaussian process on all three maps

The rule of Section 5.2 uses the Gaussian process of the guaranteed campaigns (Section 4.3), which predicts the full spectrum or profile at a site from the measured set. After each level is measured, the process is refitted with the length scale set by maximum marginal likelihood, and every unmeasured site of the next level is assessed against both claims. The process places one length scale on all channels, so a posterior over the claims needs a model of how channels vary together; here posterior draws of the spectrum at a site are taken along the leading principal components of the measured spectra, which carry 99 % of the variance up to at most 20 components, with the component variances scaled by the posterior standard deviation at the site; 64 draws per site, clipped at zero. This construction is one choice among several, and the stated rates of Table S7.2 belong to it; another posterior over the claims would state other rates. The stated probability that a claim fails at a site is the share of draws for which it fails: for the interest claim, the share of draws that are of interest; for the interpolation claim, the share of draws that fail the acceptance metric against the posterior mean. A site is skipped under a claim when its stated probability is at most α, and a site skipped under both claims is stated to fail with probability $1 - (1 - p_a)(1 - p_b)$. The stated share of skip errors of a campaign is the sum of these probabilities over its skipped sites on guaranteed levels, divided by the number of sites on guaranteed levels.

Three standard deviations are used: the latent one, the predictive one, which adds the fitted noise variance, and the predictive one multiplied by a factor fixed on each level from the measured set, the 68 % quantile of the absolute leave-one-out residuals in units of their predictive standard deviation. A factor below one means the measured sites are predicted better than the process states, and the rescaled campaign then skips more.

**Table S7.2.** Spectrum Gaussian-process campaigns without a guarantee, ranges over α from 0.01 to 0.32. Shares are of the sites on guaranteed levels.

| map | standard deviation | stated share wrong | realised share wrong | measured |
|---|---|---|---|---|
| IR (959 sites) | latent | 0–7.4 % | 1.0–3.3 % | 73–191 |
| | predictive | 0–9.1 % | 0.7–2.3 % | 73–398 |
| | rescaled (factor 0.40) | 0–3.7 % | 1.6–4.5 % | 73–75 |
| NaCl (1071 sites) | latent | 0–0.7 % | 0.1–1.6 % | 1042–1070 |
| | predictive | 0–0.1 % | 0.1–0.4 % | 1064–1070 |
| | rescaled (factor 0.19–0.89) | 0–2.1 % | 0.1–5.8 % | 959–1070 |
| synthetic (2118 sites) | latent | 0–0.1 % | 0 % | 2109–2118 |
| | predictive | 0 % | 0 % | 2118 |
| | rescaled (factor 0.06–0.23) | 0–1.8 % | 0.3–2.1 % | 1506–1792 |

On IR, 73 sites form the seed, so a campaign at 73 measured sites skipped every guaranteed-level site. On the synthetic map the claim is on the full profile at 0.5 % + 0.005; the process judged every site too uncertain to skip at every α, and only the rescaled process skipped. The two-claim variant of SI 6.2, with its peak claim, gave stated shares of at most 4 % against realised shares of 11 % to 41 %; those runs are kept in the archive of SI 5. On NaCl the fitted white-noise variance, about three quarters of the variance of the width, makes the predictive process unwilling to skip; it describes site-to-site scatter that the smooth part of the process does not follow, far above the counting noise of a measurement (SI 2).

**The same process, guaranteed.** The frozen interpolation score of a guaranteed plan can be the process's own posterior probability of a skip error, computed as above with the predictive standard deviation before each calibration draw, from the measured set only and with a fixed random stream; ties among the 64-draw probabilities are broken by the mean deviation of the draws. The predictor is the process's posterior mean, the length scale set by maximum likelihood, the budget that of Table 3. On NaCl, 50 campaigns measured 761 ± 68 of 1071 sites, with 16 of 200 level checks over budget against 24.0 expected under the picked failure probabilities; the rule without a guarantee, with the same process and the same probability measured 1064 to 1070 (Table S7.2). On the synthetic map, 20 campaigns measured 1991 ± 91 of 2118, with 13 of 120 level checks over budget against 11.4 expected, against 2118 without a guarantee. The ranking saved nothing over the positional standard deviation of Section 4.3 (745 to 777 on NaCl, 1946 to 2027 on the synthetic map). The process mean failed at 74 % and 77 % of the calibration sites of the two maps, against 52 % and 40 % for natural-neighbour prediction.

## S7.3 Guaranteed campaigns at several budgets

For Fig. 4 the matched-quantile rule was run at budgets $\varepsilon$ of 0.05, 0.10, 0.20 and 0.30 on the shared skip-error rate, at the confidences of Section 4.3, with natural-neighbour prediction (20 campaigns per budget) and Gaussian-process prediction with the length scale by maximum likelihood (8 campaigns per budget, 4 on the synthetic map).

**Table S7.3.** Guaranteed campaigns by budget: sites measured (mean ± standard deviation) and, in brackets, the mean realised share of the sites on guaranteed levels skipped in error. NN, natural-neighbour prediction; GP, Gaussian-process prediction.

| map | predictor | ε = 0.05 | ε = 0.10 | ε = 0.20 | ε = 0.30 |
|---|---|---|---|---|---|
| IR | NN | 473 ± 70 (1.5 %) | 312 ± 58 (3.4 %) | 233 ± 1 (4.1 %) | 233 ± 0 (4.1 %) |
| | GP | 410 ± 66 (1.5 %) | 271 ± 31 (3.7 %) | 233 ± 1 (4.3 %) | 233 ± 0 (4.3 %) |
| NaCl | NN | 898 ± 52 (1.9 %) | 806 ± 69 (4.5 %) | 631 ± 69 (11.5 %) | 484 ± 47 (19.9 %) |
| | GP | 1022 ± 23 (2.2 %) | 963 ± 54 (4.2 %) | 767 ± 69 (11.5 %) | 624 ± 65 (18.3 %) |
| synthetic | NN | 1128 ± 229 (2.2 %) | 918 ± 219 (4.5 %) | 542 ± 83 (12.5 %) | 392 ± 57 (20.3 %) |
| | GP | 2061 ± 24 (1.8 %) | 1940 ± 95 (5.8 %) | 1673 ± 138 (14.3 %) | 1460 ± 122 (22.4 %) |

On IR, 233 sites is the floor: 73 seed sites and 160 calibration draws. Above a budget of 0.10 every predicted skip is admitted, and the realised share stays at the rate the predictor makes.

**Figure S7.** The NaCl scan, levels 3 to 6. (a) Sites measured against the share of sites skipped in error: 250 guaranteed campaigns with natural-neighbour prediction (grey; diamond: random state 44), 3 × 250 guaranteed campaigns with the Gaussian-process mean as predictor (purple; length scale by maximum likelihood, by design spacing or by local spacing), and the Gaussian-process rule without a guarantee at intervals of 68 % to 99 % (open symbols). (b) Realised share of each level skipped in error in the 250 guaranteed campaigns of natural-neighbour prediction, against the budget of 20 %; numbers give level runs over budget against the number expected under the picked failure probabilities. File: `figures/figS7_cost.png`.

## S7.4 The paired comparison of Fig. 1

The comparison of Fig. 1 holds design, model, ranking and calibration sample fixed and varies only the cut on the sites left after calibration (Section 4.3). Designs are drawn with the hierarchical Poisson-disk sampler at radii 0.2/√2^l mm for levels l = 0 to 6, corners forced, and snapped to the NaCl raster (seeds 1000 to 1079); levels 0 to 3 form the seed. Each round fits two Gaussian processes on all sites measured so far: presence of the (200) line, regressed as 0 or 1 and clipped to [0, 1], and the logarithm of its width at measured sites that hold the line. Both use a squared-exponential kernel with an output scale and a white-noise term, outputs standardised, two restarts of the optimiser. A site is predicted to hold the line when the presence prediction is at least 0.5. Its probability of a skip error is one minus the product of the presence prediction and the predictive probability that the width lies within the tolerance when the line is predicted, and the presence prediction otherwise. The calibration sample of 40 sites is drawn with its own random stream, identical in both cuts of a design.

The uncertainty of the model is turned into a statement on the number of skip errors by 2000 joint draws: presence is drawn site by site with the predicted probability, and log width jointly over the remaining sites from the full predictive covariance. The cut is the longest prefix of the ranking for which at least 80 % of the draws stay within $\lfloor 0.2 N \rfloor$ skip errors, $N$ the size of the round, and the stated rate is the 80 % quantile of the draws at that prefix, divided by $N$. The conformal cut scans thresholds on the same probability in increasing order and keeps the largest for which the exact hypergeometric upper limit at confidence 0.80 on the number of failures in the round, given the calibration failures below the threshold, less those failures, is at most $\lfloor 0.2 N \rfloor$; the stated rate is that difference divided by $N$. A cut keeps its rate in a campaign when the realised skip errors among the sites it skips, divided by $N$, are at most its stated rate. Presence is regressed on 0 and 1 for speed; a classifier would change the ranking and the model's statement and leave the conformal guarantee unchanged.

The three kernels differ only in two settings. With the noise level fitted, the white-noise term is optimised between 10⁻⁴ and 10 of the standardised variance. With the noise fixed, the term is held at 10⁻⁴. With the long length scale, the term is held at 10⁻⁴ and the length scale bounded below by 1 mm; maximum likelihood with the noise fitted gives about 0.23 mm. The random predictor copies, for each site of a round, the presence and width of a measured site chosen uniformly at random and ranks the sites by independent uniform numbers.

**Table S7.4.** The paired comparison, 80 designs per row. Drive: the cut whose skips decide what is measured next; cut: the cut evaluated on the same states. Within rate: share of campaigns (%) whose realised skip errors stayed within the rate stated before the round, rounds 1 / 2 / 3, against a target of 80 % (a method meeting it exactly gives 71 % to 89 % in 95 of 100 such sets). Skip errors: mean skip errors of mean skips per round. Measured: mean sites measured by the driven campaign, seed and calibration included, of about 1075.

| kernel | drive | cut | within rate | skip errors | measured |
|---|---|---|---|---|---|
| noise level fitted | model | model | 87.5 / 98.8 / 100.0 | 21 of 68 / 40 of 150 / 76 of 314 | 543 |
|  | model | thresholds | 77.5 / 85.0 / 81.2 | 20 of 65 / 38 of 143 / 66 of 287 | 543 |
|  | thresholds | model | 87.5 / 97.5 / 100.0 | 21 of 68 / 40 of 150 / 77 of 316 | 580 |
|  | thresholds | thresholds | 77.5 / 83.8 / 82.5 | 20 of 65 / 38 of 144 / 66 of 286 | 580 |
| noise fixed at 10⁻⁴ | model | model | 73.8 / 68.8 / 88.8 | 24 of 75 / 50 of 165 / 93 of 336 | 500 |
|  | model | thresholds | 82.5 / 81.2 / 88.8 | 19 of 61 / 37 of 132 / 66 of 269 | 500 |
|  | thresholds | model | 73.8 / 77.5 / 85.0 | 24 of 75 / 49 of 163 / 94 of 338 | 619 |
|  | thresholds | thresholds | 82.5 / 88.8 / 88.8 | 19 of 61 / 35 of 129 / 65 of 266 | 619 |
| length scale ≥ 1 mm | model | model | 0.0 / 0.0 / 0.0 | 42 of 93 / 102 of 222 / 204 of 443 | 317 |
|  | model | thresholds | 87.5 / 77.5 / 83.8 | 19 of 53 / 38 of 108 / 69 of 206 | 317 |
|  | thresholds | model | 0.0 / 0.0 / 0.0 | 42 of 93 / 104 of 222 / 229 of 447 | 723 |
|  | thresholds | thresholds | 87.5 / 81.2 / 77.5 | 19 of 53 / 36 of 103 / 72 of 196 | 723 |
| random predictor | thresholds | thresholds | 80.0 / 78.8 / 82.5 | 21 of 31 / 38 of 56 / 67 of 97 | 891 |

Map quality was compared on 20 designs with the noise level fitted and with the long length scale. Each measured set, and a control of the seed plus a uniform random draw of the other design sites of equal size, was refitted with a Gaussian-process classifier for presence and a Gaussian-process regression for the log width with fitted white noise, both with a Matérn kernel of smoothness ½; on the seven sets of design 0, marginal likelihood preferred smoothness 5/2 on every set, which predicted the raster worse by 0.4 to 6 percentage points. The error is the share of the 3249 raster sites at which presence is predicted wrongly or the width is off by more than the tolerance.

**Table S7.5.** Map quality after round 3, mean over 20 designs: share of the raster outside tolerance (%), with presence wrong in brackets.

| kernel | drive | sites measured | measured set | random set of equal size |
|---|---|---|---|---|
| noise level fitted | model | 538 | 25.9 (5.3) | 26.9 (6.2) |
| | thresholds | 562 | 26.0 (5.3) | 27.3 (6.1) |
| length scale ≥ 1 mm | model | 312 | 29.9 (7.7) | 30.5 (8.2) |
| | thresholds | 720 | 24.0 (4.7) | 25.3 (5.1) |

**Figure S7c.** Maps after round 3 of one paired design (design 0), refitted with the Matérn model of Table S7.5. Rows: the kernel that steered the campaign; columns: the cut that drove it, with the interpolated width and its error against the raster. Crosses mark the campaign's skip errors. Measuring every site of this design leaves 19 % of the raster outside tolerance. File: `figures/figS_paired_maps_matern.png`.

Code and records: `experiments/paired_gp.py`, `experiments/chicken.py`, `experiments/paired_gp_fitquality.py`, `experiments/paired_gp_maps.py`, `experiments/paired_gp_bestfit.py`; `results/revision2/paired_gp.jsonl`, `paired_chicken.jsonl`, `paired_gp_fitquality.jsonl`, `paired_gp_summary.json`. Fig. 1 is drawn by `manuscript/figures/fig_hook4.py`.
