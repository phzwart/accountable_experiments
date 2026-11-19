# SI 3. Full tables per dataset, level and protocol (draft 2)

*Per-level tables for every configuration are in the run record (SI 5); the tables below summarise them. All entries: mean ± s.d. over 250 campaigns.*

**Table S3.1.** Sites measured for each form of guarantee for the same stated bound on the shared wrong-skip rate: $R_E \le 0.10$ at confidence 0.75 for the IR map, $R_E \le 0.20$ at confidence 0.80 for the NaCl scan and the synthetic map. Same data as Fig. 3, upper row.

| Dataset | Design sites | Per-claim budgets | Quantile path | Priority path |
| --- | --- | --- | --- | --- |
| IR map | 949 | 275 ± 51 | 297 ± 53 | 331 ± 79 |
| NaCl scan | 1071 | 719 ± 60 | 614 ± 56 | 678 ± 39 |
| Synthetic map | 2118 | 338 ± 26 | 334 ± 26 | 628 ± 61 |

**Table S3.2.** Sites measured for each interpolation protocol under the quantile path, at the same nominal guarantees. Same data as Fig. 4, upper row. The tight IR tolerance is ±(10 % + 0.01) absorbance with interest at 0.02; the last row uses the interpolation certificate alone.

| Dataset | Design sites | Natural neighbour | GP, max. likelihood | GP, design spacing | GP, local spacing |
| --- | --- | --- | --- | --- | --- |
| IR map | 949 | 297 ± 53 | 283 ± 36 | 290 ± 42 | 305 ± 45 |
| IR map, tight | 949 | 665 ± 72 | 770 ± 53 | 788 ± 51 | 794 ± 35 |
| IR map, tight, interpolation only | 949 | 615 ± 65 | 800 ± 56 | 815 ± 52 | 846 ± 33 |
| NaCl scan | 1071 | 614 ± 56 | 745 ± 72 | 760 ± 70 | 778 ± 59 |
| Synthetic map | 2118 | 334 ± 26 | 1139 ± 215 | 1042 ± 201 | 1447 ± 134 |

**Table S3.3.** Sites measured with random scores for every certificate, against informed scores (Fig. 2).

| Dataset | Form | Informed scores | Random scores |
| --- | --- | --- | --- |
| IR map | Per-claim budgets | 275 ± 51 | 364 ± 126 |
| IR map | Quantile path | 297 ± 53 | 711 ± 74 |
| IR map | Priority path | 331 ± 79 | 808 ± 51 |
| IR map, tight | Quantile path | 665 ± 72 | 865 ± 29 |
| NaCl scan | Per-claim budgets | 719 ± 60 | 928 ± 45 |
| NaCl scan | Quantile path | 614 ± 56 | 861 ± 50 |
| NaCl scan | Priority path | 678 ± 39 | 874 ± 49 |
| Synthetic map | Per-claim budgets | 338 ± 26 | 991 ± 286 |
| Synthetic map | Quantile path | 334 ± 26 | 1076 ± 187 |
| Synthetic map | Priority path | 628 ± 61 | 1322 ± 185 |
