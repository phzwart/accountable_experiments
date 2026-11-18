## Seed 0

| Row | Measured | Skipped | Statement on R_E | Remainder R_E by level |
| --- | --- | --- | --- | --- |
| ir_legacy_sequential | 285 / 949 | 664 | none | 0.080, 0.041, 0.048, 0.045 |
| ir_nested_legacy | 321 / 949 | 628 | ≤ 0.10 at 0.75 | 0.040, 0.031, 0.048, 0.050 |
| ir_nested_watson | 269 / 949 | 680 | ≤ 0.10 at 0.75 | 0.040, 0.020, 0.065, 0.059 |
| ir_priority_watson | 294 / 949 | 655 | ≤ 0.10 at 0.75 | 0.040, 0.020, 0.061, 0.053 |
| ir_separate_split_watson | 949 / 949 | 0 | ≤ 0.10 at 0.75 | 0.000, 0.000, 0.000, 0.000 |
| nacl_envelope_separate_watson | 800 / 1071 | 271 | ≤ 0.20 at 0.80 | 0.000, 0.092, 0.165, 0.091 |
| nacl_fwhm_nested_legacy | 578 / 1071 | 493 | ≤ 0.20 at 0.80 | 0.160, 0.102, 0.212, 0.175 |
| nacl_fwhm_nested_watson | 631 / 1071 | 440 | ≤ 0.20 at 0.80 | 0.080, 0.122, 0.264, 0.079 |
| nacl_fwhm_priority_watson | 668 / 1071 | 403 | ≤ 0.20 at 0.80 | 0.040, 0.143, 0.247, 0.121 |
| nacl_fwhm_separate_legacy | 684 / 1071 | 387 | ≤ 0.20 at 0.80 | 0.040, 0.112, 0.113, 0.141 |
| nacl_fwhm_separate_watson | 762 / 1071 | 309 | ≤ 0.20 at 0.80 | 0.000, 0.102, 0.156, 0.042 |
| nacl_qpeak_nested_watson | 588 / 1071 | 483 | ≤ 0.20 at 0.80 | 0.040, 0.133, 0.260, 0.085 |
| nacl_qpeak_separate_legacy | 631 / 1071 | 440 | ≤ 0.20 at 0.80 | 0.080, 0.041, 0.130, 0.042 |
| nacl_qpeak_separate_watson | 630 / 1071 | 441 | ≤ 0.20 at 0.80 | 0.080, 0.082, 0.147, 0.029 |
| syn_envelope_interp_legacy | 511 / 2118 | 1607 | ≤ 0.10 at 0.90 | nan, 0.312, 0.031, 0.023, 0.062, 0.093 |
| syn_envelope_interp_watson | 637 / 2118 | 1481 | ≤ 0.10 at 0.90 | nan, 0.031, 0.042, 0.073, 0.025, 0.038 |
| syn_peak_2cert_nested_watson | 440 / 2118 | 1678 | ≤ 0.20 at 0.80 | nan, 0.062, 0.094, 0.142, 0.045, 0.010 |
| syn_peak_2cert_priority_watson | 702 / 2118 | 1416 | ≤ 0.20 at 0.80 | nan, 0.094, 0.094, 0.128, 0.105, 0.095 |
| syn_peak_2cert_separate_watson | 358 / 2118 | 1760 | ≤ 0.20 at 0.80 | nan, 0.000, 0.031, 0.087, 0.025, 0.044 |
| syn_peak_interp_watson | 503 / 2118 | 1615 | ≤ 0.10 at 0.90 | nan, 0.000, 0.021, 0.032, 0.010, 0.036 |

## Replication over calibration seeds (level rates)

| Row | Seeds | Mean measured | Event | Budget | Nominal failure | Exceedances / trials | 95% interval |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ir_legacy_sequential | 20 | 282 | R_E (intended) | 0.10 | 0.25 | 0/80 | 0.000–0.045 |
| ir_nested_watson | 20 | 282 | R_E | 0.10 | 0.25 | 0/80 | 0.000–0.045 |
| ir_priority_watson | 20 | 308 | R_E | 0.10 | 0.25 | 0/80 | 0.000–0.045 |
| ir_separate_split_watson | 20 | 949 | R_interest | 0.05 | 0.12 | 0/80 | 0.000–0.045 |
| ir_separate_split_watson | 20 | 949 | R_interp | 0.05 | 0.12 | 0/80 | 0.000–0.045 |
| ir_separate_split_watson | 20 | 949 | R_E | 0.10 | 0.25 | 0/80 | 0.000–0.045 |
| nacl_fwhm_nested_watson | 20 | 651 | R_E | 0.20 | 0.20 | 6/80 | 0.028–0.156 |
| nacl_fwhm_priority_watson | 20 | 692 | R_E | 0.20 | 0.20 | 5/80 | 0.021–0.140 |
| nacl_fwhm_separate_legacy | 20 | 743 | R_interest | 0.10 | 0.10 | 2/80 | 0.003–0.087 |
| nacl_fwhm_separate_legacy | 20 | 743 | R_interp | 0.10 | 0.10 | 2/80 | 0.003–0.087 |
| nacl_fwhm_separate_legacy | 20 | 743 | R_E | 0.20 | 0.20 | 0/80 | 0.000–0.045 |
| nacl_fwhm_separate_watson | 20 | 766 | R_interest | 0.10 | 0.10 | 3/80 | 0.008–0.106 |
| nacl_fwhm_separate_watson | 20 | 766 | R_interp | 0.10 | 0.10 | 0/80 | 0.000–0.045 |
| nacl_fwhm_separate_watson | 20 | 766 | R_E | 0.20 | 0.20 | 0/80 | 0.000–0.045 |
| nacl_qpeak_nested_watson | 20 | 581 | R_E | 0.20 | 0.20 | 5/80 | 0.021–0.140 |
| syn_peak_2cert_nested_watson | 20 | 373 | R_E | 0.20 | 0.20 | 5/120 | 0.014–0.095 |
| syn_peak_2cert_priority_watson | 20 | 670 | R_E | 0.20 | 0.20 | 7/120 | 0.024–0.116 |
| syn_peak_2cert_separate_watson | 20 | 357 | R_interest | 0.10 | 0.10 | 0/120 | 0.000–0.030 |
| syn_peak_2cert_separate_watson | 20 | 357 | R_interp | 0.10 | 0.10 | 1/120 | 0.000–0.046 |
| syn_peak_2cert_separate_watson | 20 | 357 | R_E | 0.20 | 0.20 | 0/120 | 0.000–0.030 |
