# SI 3. Full tables per dataset, level and protocol (draft 2)

*Per-level tables for every configuration are in the run record (SI 5); the tables below summarise them. All entries: mean ± s.d. over 250 campaigns, 20 for the Gaussian-process protocols of the synthetic map.*

**Table S3.1.** Sites measured for each form of guarantee for the same stated bound on the shared skip-error rate: $R_E \le 0.10$ at confidence 0.75 for the IR map and $R_E \le 0.20$ at confidence 0.80 for the NaCl scan. The synthetic map carries one claim, so its three forms coincide; it is given once. Same data as Fig. S3, upper row.

| Dataset | Design sites | Per-claim budgets | Matched-quantile rule | Priority rule |
| --- | --- | --- | --- | --- |
| IR map | 959 | 262 ± 28 | 295 ± 53 | 327 ± 80 |
| NaCl scan | 1071 | 719 ± 60 | 614 ± 56 | 678 ± 39 |
| Synthetic map ($R_E \le 0.10$ at 0.80, one claim) | 2118 | 932 ± 223 | 932 ± 223 | 932 ± 223 |

**Table S3.2.** Sites measured for each interpolation protocol under the matched-quantile rule, at the same nominal guarantees. Same data as Fig. 6. The tight IR tolerance is ±(10 % + 0.01) absorbance with interest at 0.02; the last row uses the interpolation claim alone.

| Dataset | Design sites | Natural neighbour | GP, max. likelihood | GP, design spacing | GP, local spacing |
| --- | --- | --- | --- | --- | --- |
| IR map | 959 | 295 ± 53 | 273 ± 31 | 281 ± 34 | 291 ± 41 |
| IR map, tight | 959 | 621 ± 70 | 747 ± 56 | 753 ± 52 | 799 ± 40 |
| IR map, tight, interpolation only | 959 | 604 ± 65 | 792 ± 58 | 797 ± 56 | 854 ± 35 |
| NaCl scan | 1071 | 614 ± 56 | 745 ± 72 | 760 ± 70 | 777 ± 60 |
| Synthetic map (GP: 20 campaigns) | 2118 | 932 ± 223 | 1974 ± 55 | 1946 ± 50 | 2027 ± 39 |

**Table S3.3.** Sites measured with random scores for every claim, against informed scores (Fig. 6).

| Dataset | Form | Informed scores | Random scores |
| --- | --- | --- | --- |
| IR map | Per-claim budgets | 262 ± 28 | 335 ± 84 |
| IR map | Matched-quantile rule | 295 ± 53 | 716 ± 71 |
| IR map | Priority rule | 327 ± 80 | 817 ± 49 |
| IR map, tight | Matched-quantile rule | 621 ± 70 | 871 ± 31 |
| NaCl scan | Per-claim budgets | 719 ± 60 | 928 ± 45 |
| NaCl scan | Matched-quantile rule | 614 ± 56 | 861 ± 50 |
| NaCl scan | Priority rule | 678 ± 39 | 874 ± 49 |
| Synthetic map | One claim (all forms) | 932 ± 223 | 1578 ± 248 |

**Figure S3.** Forms of guarantee, 250 campaigns per configuration. Upper row: sites measured per form, mean ± s.d., with the design size dashed. Lower row: realised skip-error rate on every guaranteed level of every campaign, with the budget as a solid line; tick labels give the number of exceedances. Right: fraction of 4000 calibration draws in which $R_E$ exceeded 0.10 on a population with uninformative scores, for the sequential rule and the two single-budget paths; the band marks ±2 Monte Carlo standard errors around the allowed 0.25. File: `figures/fig3_forms.png`.

## Forms of guarantee and random scores compared

Every form of Table S4.3 kept its guarantee on the two maps with two claims at one nominal statement on the shared event, $R_E \le 0.10$ at confidence 0.75 for IR and $R_E \le 0.20$ at 0.80 for NaCl (Fig. S3; Table S3.1); with the one claim of the synthetic map the forms coincide. The shared rate exceeded its budget in 0, 49 and 49 of 1000 level checks for the per-claim form, the matched-quantile rule and the priority rule on IR, and in 9, 112 and 123 of 1000 on NaCl. No form was the least expensive on all three maps: the per-claim form measured 262 ± 28 of 959 sites on IR against 295 ± 53 for the matched-quantile rule, and the matched-quantile rule 614 ± 56 of 1071 on NaCl against 678 to 719. The sequential rule of an earlier analysis of the IR map, which sets the interpolation threshold on the calibration sites left uncovered by the interest threshold, exceeded $R_E = 0.10$ in 28.8 % of 4000 draws; the priority rule, which fixes the same preference in advance, did so in 20.5 %, at a picked failure probability of 20.6 %.

With random scores, an independent uniform weight per site and claim, the shared rate exceeded its budget in 168 of 1000 level checks on IR, 194 of 1000 on IR at the tight tolerance, 127 of 1000 on NaCl and 149 of 1500 on the synthetic map, at nominal failure probabilities of 0.25, 0.25, 0.20 and 0.20 (Table S3.3).
