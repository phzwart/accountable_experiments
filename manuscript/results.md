# 5 Results (draft 2: sections 5.1–5.3)

*Sections 5.4 and 5.5 wait for the matched-budget study and the maps (plan, section 6). All numbers below come from the run record: 36 configurations, each run as 250 independent campaigns with their own calibration draws (SI 5).*

## 5.1 The assertion holds (C1)

An assertion is worth only as much as its record of being kept. Every configuration in this study was therefore run 250 times, and every certified level of every campaign was checked against the fully measured truth (SI 5).

The failure probability a level actually carries is set by the calibration sample. The rule allows $k$ failing calibration sites, and the worst-case probability of exceeding the budget at that $k$ takes only a few values: with 40 calibration sites and a budget of 0.10 on a level of 399 sites, allowing 2 failures gives 0.206 and allowing 3 gives 0.411. The rule picks the largest of these values at or below the nominal $\delta$, and that picked value $\delta_L$ is the failure probability the level asserts. On the levels of this study, $\delta_L$ averaged 0.20 against a nominal 0.25 for the IR map and 0.11 to 0.12 against 0.20 for the NaCl and synthetic maps. The observed exceedances are to be compared with $\delta_L$.

Measured against the picked levels, the record agrees with the assertion. For the 32 stated rates (configuration and statement) whose budget can be exceeded on every level, union-bound statements excluded, the observed number of exceedances lay between 0.82 and 1.11 times the number the picked levels allow, and none exceeded it beyond chance: the smallest one-sided probability of the observed count under the picked levels was 0.13 (SI 5, Table S5.3). The IR map at its tight tolerance, for instance, allowed 201 exceedances in 1000 level checks and showed 211 with natural-neighbour interpolation and 182 to 201 with the Gaussian-process protocols. On the IR map at its original tolerance, three of the four levels hold too few failing sites for the budget to be reached: skipping every site that a certificate may cover leaves the wrong-skip rate below 0.10, so no exceedance is possible there and the record shows none. The union-bound statement of the per-claim form is exceeded far less often than its picked level allows, since two claims seldom approach their budgets on the same level. Repeating the calibration draw on the recorded level populations gives the same picture level by level: the attained exceedance probability lay between 0.94 and 1.07 times $\delta_L$ wherever the budget could be exceeded (SI 5, Table S5.2).

A score that carries no information leaves the assertion intact. In a further set of configurations, every certificate ordered the sites by an independent uniform random number, in the spirit of a stock-picking chicken. The shared rate exceeded its budget in 194 of 1000 level checks on IR, 164 of 1000 on IR at the tight tolerance, 127 of 1000 on NaCl and 161 of 1500 on the synthetic map, against 25 %, 25 %, 20 % and 20 % allowed (Fig. 2, lower row). The random order cost measurements: 711 ± 74 of 949 sites on IR against 297 ± 53 with informed scores, 865 ± 29 against 665 ± 72 at the tight tolerance, 861 ± 50 of 1071 against 614 ± 56 on NaCl, and 1076 ± 187 of 2118 against 334 ± 26 on the synthetic map (Fig. 2, upper row). The guarantee comes from the calibration draw; the score decides what it costs.

**Figure 2.** Informed against random scores, quantile path, 250 campaigns per configuration. Upper row: sites measured, mean ± s.d., with the design size dashed. Lower row: realised wrong-skip rate on every certified level of every campaign, with the budget as a solid line; tick labels give the number of exceedances. File: `figures/fig2_random.png`.

## 5.2 Forms of guarantee (C2)

A choice between forms of guarantee needs their costs on real data. Each form of Table 3 was run on all three datasets at one nominal assertion on the shared event: $R_E \le 0.10$ at confidence 0.75 for the IR map, $R_E \le 0.20$ at confidence 0.80 for the NaCl scan and the synthetic map. The per-claim form reached that assertion through a split, 0.10 at confidence 0.90 per claim for NaCl and the synthetic map, 0.05 at confidence 0.875 for IR. All runs used exact natural-neighbour interpolation and the logistic scores of Section 4.

Every stated rate held (Fig. 3, lower row). The shared rate exceeded its budget in 0, 72 and 72 of 1000 level checks for the three IR forms, in 9, 112 and 123 of 1000 for NaCl, and in 5, 161 and 156 of 1500 for the synthetic map. The per-claim assertions of the split form exceeded their budgets in 32 and 0 of 1000 checks on IR (12.5 % allowed), 64 and 57 of 1000 on NaCl and 73 and 67 of 1500 on the synthetic map (10 % allowed). The shared assertion of the split form, obtained through the union bound, was almost never exceeded: two claims seldom approach their budgets on the same level.

The forms differ in cost, and the ordering changes between datasets (Fig. 3, upper row; Table S3.1). On IR the per-claim form measured 275 ± 51 of 949 sites, the quantile path 297 ± 53 and the priority path 331 ± 79. The per-claim split is feasible on IR only through the exact finite-population tail: on levels of 65 to 399 sites, a draw of 40 without replacement admits zero failures at a budget of 0.05 and confidence 0.875, where the binomial approximation admits none. On NaCl, the quantile path was the least expensive form (614 ± 56 of 1071 sites, against 719 ± 60 and 678 ± 39). On the synthetic map, the per-claim form and the quantile path cost the same within their spread (338 ± 26 and 334 ± 26 of 2118), and the priority path almost twice as much (628 ± 61). No form is the least expensive on all three datasets.

The priority path admitted the interest claim first, and the order shows in the reasons recorded for each skip. On NaCl and on the synthetic map, the interest claim took the whole budget: in every campaign, every skipped site was skipped as uninteresting. On IR, the interest claim applies only below an intensity cap, so its sweep ends early and interpolation receives the rest of the budget.

A rule that breaks the recipe loses its guarantee. The sequential rule of the original IR analysis chooses the interest threshold on the calibration draw and then the interpolation threshold on the calibration sites left uncovered, from the remaining budget. On a population with uninformative scores (399 sites; interest and failure labels at rates 0.5 and 0.1), it exceeded $R_E = 0.10$ in 1150 of 4000 draws, a frequency of 0.288 against 0.25 allowed (Monte Carlo standard error 0.007). The priority path expresses the same preference with the order fixed in advance and exceeded the bound in 819 of 4000 draws; the quantile path did so in 832 (Fig. 3, right).

**Figure 3.** Forms of guarantee, 250 campaigns per configuration. Upper row: sites measured per form, mean ± s.d., with the design size dashed. Lower row: realised wrong-skip rate on every certified level of every campaign, with the budget as a solid line; tick labels give the number of exceedances. Right: fraction of 4000 calibration draws in which $R_E$ exceeded 0.10 on a population with uninformative scores, for the sequential rule and the two single-budget paths; the band marks ±2 Monte Carlo standard errors around the allowed 0.25. File: `figures/fig3_forms.png`.

## 5.3 The cost of an assertion across protocols (C4)

An assertion is of use only if it holds whichever interpolator proposes the skips. The quantile path was therefore run with four interpolation protocols on each dataset, at the nominal assertions of Section 5.2: natural-neighbour interpolation with the logistic score, and Gaussian-process interpolation with the posterior standard deviation as score and the length scale set by maximum likelihood, by the design spacing or by the local spacing of measured sites (Section 4.3). The IR map was run at two tolerances. At its original tolerance of ±(10 % + 0.10) absorbance almost every site is interpolable by any method, and the interest claim alone sets the cost; at ±(10 % + 0.01), with interest at 0.02, interpolation decides.

Every assertion held (Fig. 4, lower row). In the order listed, the shared rate exceeded its budget in 72, 72, 0 and 33 of 1000 level checks on IR at the original tolerance, in 211, 201, 190 and 187 of 1000 at the tight tolerance (25 % allowed), in 112, 119, 110 and 119 of 1000 on NaCl, and in 161, 160, 184 and 161 of 1500 on the synthetic map (20 % allowed).

The cost depends on the protocol and on the data (Fig. 4, upper row; Table S3.2). At the original IR tolerance the four protocols measured 297 ± 53, 283 ± 36, 290 ± 42 and 305 ± 45 of 949 sites, and their skipped sets overlapped by about 95 %. At the tight tolerance they measured 665 ± 72, 770 ± 53, 788 ± 51 and 794 ± 35, and the Gaussian-process protocols shared under a third of their skips with natural-neighbour interpolation. On NaCl, the Gaussian-process protocols measured 745 to 778 of 1071 sites, against 614 ± 56. On the synthetic map they measured between 1042 ± 201 and 1447 ± 134 of 2118 sites, against 334 ± 26. In every case the difference arises in the calibration draws: the Gaussian-process predictions missed the tolerance at more calibration sites, and more failures among the calibration sites admit fewer skips at the same budget. The assertion itself is unchanged.

The three length-scale rules lead to visibly different reasons for measuring a site (Fig. S1). The design-spacing rule gives the shortest length scale and the most structured standard deviation, high in every gap between measured sites. Maximum likelihood on IR assigned much of the variance to noise and returned a nearly uniform standard deviation. The local-spacing rule lengthens the kernel where measurements are sparse and lowers the standard deviation there. Fitted length scales and nuggets are listed in SI 1.

**Figure 4.** The cost of one assertion across interpolation protocols, quantile path, 250 campaigns per configuration. Columns: IR map at the original and at the tight tolerance, NaCl scan, synthetic map. Upper row: sites measured, mean ± s.d., with the design size dashed. Lower row: realised wrong-skip rate on every certified level of every campaign, with the budget; tick labels give the number of exceedances. GP: Gaussian process with isotropic squared-exponential kernel; length scale by maximum likelihood, by design spacing, or by local spacing of measured sites. File: `figures/fig4_protocols.png`.

## 5.4 What a skip buys (C5)

*To draft.*

## 5.5 Maps

*To draft.*

---

## Notes for revision (not part of the text)

- All numbers are from results/record (SUMMARY.md for counts, PICKED.md for the comparison with the picked levels, AUDIT.json for attainment). Level checks pool levels and campaigns; levels within one campaign are not independent draws, so the Clopper–Pearson intervals are indicative.
- On the IR map at the original tolerance, level 3 has the same population in every campaign (its scores depend only on the seed design), so its 72 exceedances in 250 campaigns are 250 draws on one population; the repeated-draw audit gives 0.247 for that level against a worst case of 0.250.
- The 95 % overlap and "under a third" statements for IR come from the 20-seed comparison earlier (Jaccard 0.95 and 0.28–0.30); recompute them from the record before submission.
- "Stock-picking chicken" is informal; keep it or drop it.
