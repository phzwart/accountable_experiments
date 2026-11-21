# SI 7. A campaign guided by Gaussian-process uncertainty

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

The difference between the two kinds of campaign lies in what each knows. At equal cost the realised error is about equal; the certified campaign states its rate before any skip is checked, and the uncertified one learns its rate only from the full scan that a campaign exists to avoid.
