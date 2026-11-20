# SI 3. Full tables per dataset, level and protocol (draft 2)

*Per-level tables for every configuration are in the run record (SI 5); the tables below summarise them. All entries: mean ± s.d. over 250 campaigns.*

**Table S3.1.** Sites measured for each form of guarantee for the same stated bound on the shared wrong-skip rate: $R_E \le 0.10$ at confidence 0.75 for the IR map, $R_E \le 0.20$ at confidence 0.80 for the NaCl scan and the synthetic map. Same data as Fig. 5, upper row.

| Dataset | Design sites | Per-claim budgets | Quantile path | Priority path |
| --- | --- | --- | --- | --- |
| IR map | 959 | 262 ± 28 | 295 ± 53 | 327 ± 80 |
| NaCl scan | 1071 | 719 ± 60 | 614 ± 56 | 678 ± 39 |
| Synthetic map | 2118 | 338 ± 26 | 334 ± 26 | 628 ± 61 |

**Table S3.2.** Sites measured for each interpolation protocol under the quantile path, at the same nominal guarantees. Same data as Fig. 6, upper row. The tight IR tolerance is ±(10 % + 0.01) absorbance with interest at 0.02; the last row uses the interpolation certificate alone.

| Dataset | Design sites | Natural neighbour | GP, max. likelihood | GP, design spacing | GP, local spacing |
| --- | --- | --- | --- | --- | --- |
| IR map | 959 | 295 ± 53 | 273 ± 31 | 283 ± 34 | 295 ± 42 |
| IR map, tight | 959 | 621 ± 70 | 750 ± 55 | 757 ± 53 | 804 ± 37 |
| IR map, tight, interpolation only | 959 | 604 ± 65 | 796 ± 58 | 803 ± 55 | 857 ± 33 |
| NaCl scan | 1071 | 614 ± 56 | 745 ± 72 | 760 ± 70 | 778 ± 59 |
| Synthetic map | 2118 | 334 ± 26 | 1139 ± 215 | 1042 ± 201 | 1447 ± 134 |

**Table S3.3.** Sites measured with random scores for every certificate, against informed scores (Fig. 4).

| Dataset | Form | Informed scores | Random scores |
| --- | --- | --- | --- |
| IR map | Per-claim budgets | 262 ± 28 | 335 ± 84 |
| IR map | Quantile path | 295 ± 53 | 716 ± 71 |
| IR map | Priority path | 327 ± 80 | 817 ± 49 |
| IR map, tight | Quantile path | 621 ± 70 | 871 ± 31 |
| NaCl scan | Per-claim budgets | 719 ± 60 | 928 ± 45 |
| NaCl scan | Quantile path | 614 ± 56 | 861 ± 50 |
| NaCl scan | Priority path | 678 ± 39 | 874 ± 49 |
| Synthetic map | Per-claim budgets | 338 ± 26 | 991 ± 286 |
| Synthetic map | Quantile path | 334 ± 26 | 1076 ± 187 |
| Synthetic map | Priority path | 628 ± 61 | 1322 ± 185 |
