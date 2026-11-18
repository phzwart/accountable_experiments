# 5 Results (draft 1: section 5.2)

*Sections 5.1 and 5.3–5.5 wait for the protocol matrix, the Gaussian-process protocol and the matched-budget study (plan, section 6).*

## 5.1 The assertion holds (C1)

*To draft.*

## 5.2 Forms of guarantee (C2)

A choice between forms of guarantee needs their costs on real data. Each form of Table 3 was therefore run on all three datasets at one nominal assertion on the shared event: $R_E \le 0.10$ at confidence 0.75 for the IR map, $R_E \le 0.20$ at confidence 0.80 for the NaCl scan and the synthetic map. The per-claim form reached that assertion through a split, 0.10 at confidence 0.90 per claim for NaCl and the synthetic map, 0.05 at confidence 0.875 for IR. Every configuration was repeated over 20 calibration seeds with exact natural-neighbour interpolation and the logistic scores of Section 4.

Every stated rate held (Fig. 3, lower row). Over all certified levels and seeds, the shared rate exceeded its budget in 0 of 80 checks for every IR form, in 0, 6 and 5 of 80 for the NaCl forms, and in 0, 5 and 7 of 120 for the synthetic forms, against 20 % allowed. The per-claim assertions of the split form exceeded their budgets in 3 of 80 (NaCl, interest), 0 of 80 (NaCl, interpolation), 0 of 120 and 1 of 120 (synthetic), against 10 % allowed.

The forms differ in cost, and the ordering changes between datasets (Fig. 3, upper row; Table 4). On IR, the split admits no threshold: a failure probability of 0.125 at $m = 40$ gives $\varepsilon_{\min} = 0.051$, just above the per-claim budget of 0.05, and every site is measured. That is the price of an assertion per reason at this calibration size. The two paths make the shared assertion with 282 ± 38 and 308 ± 66 of 949 sites measured. On NaCl, the quantile path is the least expensive form. On the synthetic map, the split costs 357 ± 19 of 2118 sites against 373 ± 29 for the quantile path, and its realised shared rates lie well below the budget, with a mean of 0.045 per level against 0.108. No form is the least expensive on all three datasets.

**Table 4.** Sites measured (mean ± s.d. over 20 calibration seeds) at the nominal assertion on $R_E$.

| Dataset | Design sites | Per-claim budgets | Quantile path | Priority path |
| --- | --- | --- | --- | --- |
| IR map | 949 | 949 ± 0 | 282 ± 38 | 308 ± 66 |
| NaCl scan | 1071 | 766 ± 50 | 651 ± 57 | 692 ± 40 |
| Synthetic map | 2118 | 357 ± 19 | 373 ± 29 | 670 ± 58 |

The priority path admitted the interest claim first, and the order shows in the reasons recorded for each skip. On NaCl and on the synthetic map, the interest claim took the whole budget: every skipped site was skipped as uninteresting, and the interpolation claim was never reached. On IR, the interest claim applies only below an intensity cap, so its sweep ends early and interpolation receives the rest of the budget; of the skipped sites, a mean of 76 were skipped as uninteresting, 213 as interpolable and 352 under both claims.

A rule that breaks the recipe loses its guarantee. The sequential rule of the original IR analysis chooses the interest threshold on the calibration draw and then the interpolation threshold on the calibration sites left uncovered, from the remaining budget. On a population with uninformative scores (399 sites; interest and failure labels at rates 0.5 and 0.1), it exceeded $R_E = 0.10$ in 1150 of 4000 draws, a frequency of 0.288 against 0.25 allowed (Monte Carlo standard error 0.007). The priority path expresses the same preference with the order fixed in advance and exceeded the bound in 581 of 4000 draws; the quantile path did so in 604 (Fig. 3, right).

**Figure 3.** Forms of guarantee. Upper row: sites measured per form, mean ± s.d. over 20 calibration seeds, with the design size dashed; on IR the per-claim split admits no threshold and every site is measured. Lower row: realised wrong-skip rate on each certified level and seed, with the budget as a solid line and the number of exceedances above each form. Right: fraction of 4000 calibration draws in which $R_E$ exceeded 0.10 on a population with uninformative scores, for the sequential rule and the two single-budget paths; the band marks ±2 Monte Carlo standard errors around the allowed 0.25. File: `figures/fig3_forms.png`.

## 5.3 Protocols change cost, not claims (C4)

*To draft.*

## 5.4 What a skip buys (C5)

*To draft.*

## 5.5 Maps

*To draft.*

---

## Notes for revision (not part of the text)

- Numbers come from the 20-seed replication in the repository's results (study summary) and from the figure script, which reruns the Monte Carlo panel.
- Table 4 duplicates the upper row of Fig. 3. Keep one in the main text; the other can go to SI 3.
- The NaCl and synthetic per-claim forms state each claim at 0.10 and the shared event at 0.20; the paths state the shared event only. The text says so in the first paragraph; check that the reader does not take the per-claim exceedances as a second test of the same assertion.
- Section 5.3 title: "Protocols change cost, not claims" is an antithesis pair. Proposed replacement: "The cost of an assertion across protocols".
