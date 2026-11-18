# 5 Results (draft 1: section 5.2)

*Sections 5.1, 5.4 and 5.5 wait for the protocol matrix and the matched-budget study (plan, section 6). Section 5.3 covers the natural-neighbour and Gaussian-process protocols; the scalar route and the random score are still to be added.*

## 5.1 The assertion holds (C1)

*To draft.*

## 5.2 Forms of guarantee (C2)

A choice between forms of guarantee needs their costs on real data. Each form of Table 3 was therefore run on all three datasets at one nominal assertion on the shared event: $R_E \le 0.10$ at confidence 0.75 for the IR map, $R_E \le 0.20$ at confidence 0.80 for the NaCl scan and the synthetic map. The per-claim form reached that assertion through a split, 0.10 at confidence 0.90 per claim for NaCl and the synthetic map, 0.05 at confidence 0.875 for IR. Every configuration was repeated over 20 calibration seeds with exact natural-neighbour interpolation and the logistic scores of Section 4.

Every stated rate held (Fig. 3, lower row). Over all certified levels and seeds, the shared rate exceeded its budget in 0 of 80 checks for every IR form, in 0, 6 and 5 of 80 for the NaCl forms, and in 0, 5 and 7 of 120 for the synthetic forms, against 20 % allowed. The per-claim assertions of the split form exceeded their budgets in 3 of 80 (NaCl, interest), 0 of 80 (NaCl, interpolation), 0 of 120 and 1 of 120 (synthetic), against 10 % allowed.

The forms differ in cost, and the ordering changes between datasets (Fig. 3, upper row; Table S3.1). On IR, the split admits no threshold: a failure probability of 0.125 at $m = 40$ gives $\varepsilon_{\min} = 0.051$, just above the per-claim budget of 0.05, and every site is measured. That is the price of an assertion per reason at this calibration size. The two paths make the shared assertion with 282 ± 38 and 308 ± 66 of 949 sites measured. On NaCl, the quantile path is the least expensive form. On the synthetic map, the split costs 357 ± 19 of 2118 sites against 373 ± 29 for the quantile path, and its realised shared rates lie well below the budget, with a mean of 0.045 per level against 0.108. No form is the least expensive on all three datasets.

The priority path admitted the interest claim first, and the order shows in the reasons recorded for each skip. On NaCl and on the synthetic map, the interest claim took the whole budget: every skipped site was skipped as uninteresting, and the interpolation claim was never reached. On IR, the interest claim applies only below an intensity cap, so its sweep ends early and interpolation receives the rest of the budget; of the skipped sites, a mean of 76 were skipped as uninteresting, 213 as interpolable and 352 under both claims.

A rule that breaks the recipe loses its guarantee. The sequential rule of the original IR analysis chooses the interest threshold on the calibration draw and then the interpolation threshold on the calibration sites left uncovered, from the remaining budget. On a population with uninformative scores (399 sites; interest and failure labels at rates 0.5 and 0.1), it exceeded $R_E = 0.10$ in 1150 of 4000 draws, a frequency of 0.288 against 0.25 allowed (Monte Carlo standard error 0.007). The priority path expresses the same preference with the order fixed in advance and exceeded the bound in 581 of 4000 draws; the quantile path did so in 604 (Fig. 3, right).

**Figure 3.** Forms of guarantee. Upper row: sites measured per form, mean ± s.d. over 20 calibration seeds, with the design size dashed; on IR the per-claim split admits no threshold and every site is measured. Lower row: realised wrong-skip rate on each certified level and seed, with the budget as a solid line and the number of exceedances above each form. Right: fraction of 4000 calibration draws in which $R_E$ exceeded 0.10 on a population with uninformative scores, for the sequential rule and the two single-budget paths; the band marks ±2 Monte Carlo standard errors around the allowed 0.25. File: `figures/fig3_forms.png`.

## 5.3 The cost of an assertion across protocols (C4)

An assertion is of use only if it holds whichever interpolator proposes the skips. The quantile path was therefore run with four interpolation protocols on each dataset, at the nominal assertions of Section 5.2: natural-neighbour interpolation with the logistic score, and Gaussian-process interpolation with the posterior standard deviation as score and the length scale set by maximum likelihood, by the design spacing or by the local spacing of measured sites (Section 4.3). Each configuration was repeated over 20 calibration seeds.

Every assertion held (Fig. 4, lower row). In the order just listed, the shared rate exceeded its budget in 0 of 80 level checks for each IR protocol, in 6, 7, 6 and 10 of 80 for NaCl, and in 5, 11, 11 and 7 of 120 for the synthetic map, against 25 % allowed for IR and 20 % for the other two.

The cost depends on the protocol and on the data (Fig. 4, upper row; Table S3.2). On IR, the four protocols measured 282 ± 38, 277 ± 38, 279 ± 36 and 298 ± 41 of 949 sites. On NaCl, the Gaussian-process protocols measured 780 to 791 of 1071 sites, against 651 ± 57 with natural-neighbour interpolation. On the synthetic map they measured between 1085 ± 181 and 1488 ± 156 of 2118 sites, against 373 ± 29. The calibration draws show where the difference arises. At the first certified level of the synthetic map, the Gaussian-process prediction with the fitted length scale missed the peak tolerance at 29 of 40 calibration sites for seed 0, natural-neighbour interpolation at 13. More failures among the calibration sites admit fewer skips at the same budget; the assertion itself is unchanged.

The three length-scale rules lead to visibly different reasons for measuring a site (Fig. S1). The design-spacing rule gives the shortest length scale and the most structured standard deviation, high in every gap between measured sites. Maximum likelihood on IR assigned much of the variance to noise and returned a nearly uniform standard deviation. The local-spacing rule lengthens the kernel where measurements are sparse and lowers the standard deviation there. Fitted length scales and nuggets are listed in SI 1.

**Figure 4.** The cost of one assertion across interpolation protocols, quantile path, 20 calibration seeds. Upper row: sites measured, mean ± s.d., with the design size dashed. Lower row: realised wrong-skip rate on each certified level and seed, with the budget and the number of exceedances. GP: Gaussian process with isotropic squared-exponential kernel; length scale by maximum likelihood, by design spacing, or by local spacing of measured sites. File: `figures/fig4_protocols.png`.

## 5.4 What a skip buys (C5)

*To draft.*

## 5.5 Maps

*To draft.*

---

## Notes for revision (not part of the text)

- Section 5.3: the 29-versus-13 comparison is from seed 0 only. If it stays, report the mean over seeds instead (one more pass over the replication records).
- Section 5.3, third paragraph: "Maximum likelihood on IR assigned much of the variance to noise" is a description of the fit (median nugget 0.12, up to 0.61). Any statement on why the GP costs more on the synthetic map (non-convex weights on sharp peaks, no mirror images at the walls) stays out of Results; it may go to the Discussion if you want it.
- Numbers come from the 20-seed replication in the repository's results (study summary) and from the figure script, which reruns the Monte Carlo panel.
- The cost table moved to SI 3 (Table S3.1); Fig. 3 carries the numbers in the main text.
- The NaCl and synthetic per-claim forms state each claim at 0.10 and the shared event at 0.20; the paths state the shared event only. The text says so in the first paragraph; check that the reader does not take the per-claim exceedances as a second test of the same assertion.
