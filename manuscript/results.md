# 5 Results (draft 3)

*All numbers below come from the run record: 36 configurations, each run as 250 independent campaigns with their own calibration draws (SI 5).*


## 5.1 The guarantee holds

Checking a probability bound needs repeated campaigns against a known truth. Every certified level of every campaign was therefore checked against the fully measured truth (SI 5).

The picked failure probabilities $\delta_L$ (Section 3.3) averaged 0.19 against a nominal 0.25 for the IR map and 0.11 to 0.12 against 0.20 for the NaCl and synthetic maps. The observed exceedances are to be compared with $\delta_L$, and the four levels of a NaCl campaign hold together with probability at least about one half.

The record agrees with the guarantee at the picked failure probabilities: over the 32 statements whose budget can be exceeded on every level, observed exceedances lay between 0.88 and 1.11 times the number expected, and none exceeded it beyond chance (SI 5, Table S5.3). On the IR map at its original tolerance, three of the four levels hold too few failing sites for the budget to be reached. Repeating the calibration draw on the recorded level populations gives the same picture (Table S5.2). Against a fixed truth these counts check the rule and its implementation; Section 6 discusses the conditions a retrospective study cannot break.

A plan can be certified as a whole by dividing its failure probability among its levels when it is declared. Certified level by level, the plans missed their goal on at least one level in 20 %, 38 % and 50 % of campaigns on the IR, NaCl and synthetic maps. Certified as a whole, at confidence 0.75 for IR and 0.80 for the other two, they measured 408 ± 80, 694 ± 61 and 376 ± 29 sites, 38 %, 13 % and 12 % more, and missed the goal in 0 of 105, 11 of 128 and 10 of 60 campaigns, within the 25 % and 20 % the contracts allow (SI 5.3). On the synthetic map 10 of 360 level checks exceeded the budget where the picked failure probabilities lead one to expect 5.5; repeating the draw 3000 times on 20 recorded levels gave an attained exceedance probability 1.01 times the picked one.

Conformal risk control on the same draw bounds only the expected share of a level skipped wrongly [Angelopoulos2024]. It admitted more skips and measured 260, 541 and 301 sites; its levels exceeded the budget in 5 %, 34 % and 33 % of checks, and its campaigns on at least one level in 20 %, 80 % and 93 % (SI 5.3).

Table 4 gives one configuration per map: what was measured, why each site was skipped, and how the record compares with the guarantee. The guarantee bounds wrong skips as a share of all sites of a level; among the skipped sites alone the share is larger, up to 26.7 % on the NaCl scan.

**Table 4.** One guarantee per dataset: quantile path, natural-neighbour interpolation, 250 campaigns; counts are means per campaign. Wrong skips are given as a share of the sites on certified levels, the quantity the guarantee bounds, and as a share of the skipped sites. Expected exceedances are the sums of the picked failure probabilities over the level checks.

| Dataset | Guarantee | Sites | Measured: seed / calibration / no claim | Skipped: not of interest / predictable / both | Wrong skips: count (share of sites / of skips) | Exceedances: observed / expected |
| --- | --- | --- | --- | --- | --- | --- |
| IR map | $R_E \le 0.10$ at 0.75 | 959 | 73 / 160 / 62 | 37 / 228 / 399 | 34 (3.8 % / 5.1 %) | 49 / 190; reachable levels 49 / 56 |
| IR map, tight tolerance | $R_E \le 0.10$ at 0.75 | 959 | 73 / 160 / 388 | 8 / 257 / 73 | 54 (6.1 % / 15.9 %) | 193 / 190 |
| NaCl scan | $R_E \le 0.20$ at 0.80 | 1071 | 76 / 160 / 378 | 157 / 156 / 144 | 122 (12.3 % / 26.7 %) | 112 / 120 |
| Synthetic map | $R_E \le 0.20$ at 0.80 | 2118 | 39 / 233 / 62 | 321 / 319 / 1144 | 270 (13.0 % / 15.1 %) | 161 / 170 |

Breaking the order of operations breaks the guarantee (Section 3.1). On a simulated level of 399 sites with informative scores, a budget of 0.10 and a picked failure probability of 0.206, the calibration draw was repeated 4000 times under several rules. With scores frozen before a uniform draw the budget was exceeded in 20.5 % of draws, and so it was with a score that knew the true labels but was frozen before the draw: what the score knows changes the cost and leaves the guarantee intact. Rules that use the draw broke it. Raising the scores of the failing calibration sites after the draw, the extreme case of refitting on calibration labels, exceeded the budget in every draw, calibrating on the half of the level ranked least safe, as an active learner would, in 63 %, and keeping the best of five draws in 69 %. On a second simulated level of the same size with uninformative scores, and so the same picked failure probability, setting the interpolation threshold on the calibration sites the interest threshold left uncovered exceeded the budget in 28.8 % of draws, where the priority path, which fixes the same preference in advance, stayed at 20.5 %. Every form of Table 1 kept its guarantee, and none was the least expensive on all three maps (Fig. S3; Table S3.1).

## 5.2 A model's own uncertainty misstates its wrong skips

Decisions resting on a model's stated error rate need that rate to hold. On the NaCl scan, a Gaussian process refitted after each level skipped a site when it was sure the line was absent, or when its 68 % interval on the width lay within the tolerance (Fig. 1; SI 7). Its statement, the model's own probability of a wrong skip summed over its skips, can be set against the realised share on the denominator of the guarantee. With the latent standard deviation it measured 658 of 1071 sites, stated 3.5 % of the certified-level sites wrong and skipped 10.4 % wrongly; at 90 % to 99 % intervals it stated 0.4 % to 0.5 % and realised 1.0 % to 1.4 %. With the predictive standard deviation, which adds the fitted noise, it stated 0.4 % and realised 0.3 %, at 922 measurements. The certified plan measured 614 ± 56 sites with natural-neighbour interpolation and 745 to 777 with the Gaussian process as predictor, and its bound held at the stated confidence (Fig. S7); certifying the Gaussian process cost about 100 measurements more than trusting its latent intervals.

The comparison was repeated on all three maps with the Gaussian process of the certified campaigns in Section 5.4, which predicts the whole profile. A site was skipped under a claim when the posterior probability of a wrong skip was at most α, for α from 0.01 to 0.32, with the latent standard deviation, the predictive one, or the predictive one rescaled to the leave-one-out residuals of the measured sites (SI 7). Stated and realised shares of wrong skips disagreed in either direction (Fig. 4). On the synthetic map the process stated at most 4 % and skipped 11 % to 41 % of the certified-level sites wrongly. Rescaling made it worse, and the reason is the one a uniform draw removes: the sites the process chose to measure were easier for it to predict than those it left out, and the scale fell to between 0.23 and 0.87 of its value. On IR the stated shares stayed below 10 % and the realised ones below 5 %, with 73 to 398 of 959 sites measured. On NaCl the process judged almost every site too uncertain to skip and measured 959 to 1070 of 1071.

The misstatement lay in the interpolation claim. On the synthetic map, sites skipped only because the line was judged absent were almost never wrong, 0 to 2 of 293 to 509; every other wrong skip failed the tolerance (SI 7). A rate stated by the model was right in one setting and three to ten times too low in others, and nothing in a run shows which. The certified campaigns at budgets from 0.05 to 0.30 realised on average less than their bound on every map; certified points pair a bound with a mean, uncertified points a stated expectation with a realisation.

**Figure 4.** What an agent states about its wrong skips, and what happens. Stated against realised share of certified-level sites skipped wrongly, for certified campaigns with natural-neighbour (blue) and Gaussian-process (purple) prediction at budgets 0.05 to 0.30 (the bound against the mean over 20 or 8 campaigns) and for uncertified Gaussian-process campaigns at α from 0.01 to 0.32 with latent, predictive or rescaled standard deviation; shares below 10⁻³ are drawn at 10⁻³; grey: equality. File: `figures/fig_stated.png`.

## 5.3 Every action certified

An instrument record becomes useful once every site of a map carries its reason. Figure 5 shows one campaign of average cost per dataset under the quantile path with natural-neighbour interpolation, with every design site marked by the reason recorded for it and every wrong skip found against the fully measured truth.

In the campaigns shown, the wrong skips were 3.8 % of the sites on certified levels of the IR map, against a budget of 0.10 per level, and 11.8 % on NaCl and 11.6 % on the synthetic map, against 0.20. The wrong skips of the synthetic map gather in two compact regions of the composition triangle; the guarantee bounds their rate on each level and leaves their location open (Section 5.5; SI 6).

In hindsight, the record shows which measurements every claim would have skipped wrongly (SI 8): 45 % of the sites measured for want of a claim on the synthetic map, against 10 % of sites drawn at random, and 47 % against 35 % on NaCl, where the width scatters from site to site by about the tolerance.

**Figure 5.** Maps with reasons, one campaign of average cost per dataset (quantile path, natural-neighbour interpolation; NaCl: the campaign of Fig. 1a; the same campaigns as SI 8). Measured sites: seed (black diamonds), calibration (dark grey squares) and sites without a claim (light grey squares). Skipped sites: not of interest (yellow), predictable (green) and both (blue). Crosses: wrong skips against the fully measured truth. IR in micrometres, NaCl in stage millimetres, synthetic map in composition fractions. File: `figures/fig5_maps.png`.

## 5.4 The model sets the cost

Freedom in the choice of model has a price, paid in measurements. The quantile path was run with four interpolation protocols on each dataset at the nominal guarantees of Section 5.1: natural-neighbour interpolation with the logistic score, and Gaussian-process interpolation with the posterior standard deviation as score and three rules for the length scale (Section 4.3). At the original IR tolerance almost every site is interpolable and the interest claim alone sets the cost; at the tight tolerance interpolation decides.

A score that carries no information still yields a valid guarantee, at a price. A random scorer, an independent uniform weight per site and claim, exceeded the budget no more often than expected on every map and cost 1.4 to 3.2 times as many measurements as informed scores, 716 ± 71 against 295 ± 53 of 959 sites on IR (Fig. 6). The guarantee comes from the calibration draw; the score decides what it costs.

Every guarantee held, with exceedance counts on each map close to those the picked failure probabilities lead one to expect and none beyond chance (Fig. 6; Table S5.3).

The cost depends on the protocol and on the data (Fig. 6; Table S3.2). At the original IR tolerance the four protocols measured 273 ± 31 to 295 ± 53 of 959 sites with skipped sets overlapping by about 90 %; at the tight tolerance they measured 621 ± 70 to 799 ± 40, and the Gaussian-process protocols shared a quarter to a third of their skips with natural-neighbour interpolation. On NaCl, the Gaussian-process protocols measured 745 to 777 of 1071 sites, against 614 ± 56. On the synthetic map they measured between 1040 ± 202 and 1443 ± 133 of 2118 sites, against 334 ± 26. The difference arises in the calibration draws: more failing calibration sites admit fewer skips at the same budget, and the guarantee is unchanged.

A certified plan also has to earn its place against the simplest alternative, a uniform sample of the same size. Uniform subsampling to the number of sites the certified plan measured, with every other site predicted from all measured sites, left 0.5 %, 21.9 % and 10.3 % of the certified-level sites outside tolerance on the IR, NaCl and synthetic maps; the final maps of the certified plans, predicted in the same way, left 0.4 %, 16.6 % and 8.5 % (SI 5.3).

**Figure 6.** What a guarantee costs under different models: sites measured (mean ± s.d. over 250 campaigns, quantile path) with random scores and with four interpolation protocols, against the number of design sites (dashed). Under each bar: level checks over budget on the shared rate, observed against expected under the picked failure probabilities. GP: Gaussian process with isotropic squared-exponential kernel; length scale by maximum likelihood, by design spacing, or by local spacing of measured sites. File: `figures/fig_cost.png`.

## 5.5 The claim decides what is protected

Each claim protects what it states, so its choice deserves a record. Six acceptance metrics were compared on the three maps with the interpolation claim alone (SI 6). Every metric kept its guarantee, and the metric set the cost: at tolerances a practitioner might pick, the IR map needed between 233 and 810 measurements. At tolerances matched to equal difficulty the metric still decided where measurements went, with the peak claim on the synthetic map measuring where the peak drifts with composition and the profile claim along the phase boundaries (Fig. S6), and it decided where wrong skips fell. The rate counts wrong skips over all sites of a level; on the synthetic map 35 % of the interesting sites on certified levels were skipped in error while every level met its budget (SI 6.2).

## Notes for revision (not part of the text)

- The calcination study (former Section 5.6, Fig. 7, SI 7) moved to experiments/tio2_calcination/PILOT.md as the design of a real synthesis campaign (20 Nov 2026).
- All numbers are from results/record (SUMMARY.md for counts, PICKED.md for the comparison with the picked levels, AUDIT.json for attainment). Level checks pool levels and campaigns; levels within one campaign are not independent draws, so the Clopper–Pearson intervals are indicative.
- On the IR map at the original tolerance, level 3 has the same population in every campaign (its scores depend only on the seed design), so its 49 exceedances in 250 campaigns are 250 draws on one population; it is the only IR level on which the budget can be exceeded.
- IR overlaps are recomputed from the record (mean per-campaign Jaccard index of the skipped sets against natural neighbour).
- The IR rows were rerun on 19 Nov 2026 with the per-pixel Mie correction and the design in micrometres (SI 2); all IR numbers in this section come from that record.
- Decided: the random-score arm stays, described as a random scorer (independent uniform weights); the informal name is dropped.
- The order-of-operations Monte Carlo is in results/anticipation_demo.json (script experiments/anticipation_demo.py); it could become a small panel of Fig. 2 or a table in SI 5.
