# SI 5. The run record (draft 1)

Every configuration of Sections 5.1–5.3 was run as 250 independent campaigns, seeds 0 to 249; a seed fixes the calibration draws of a campaign and, for random scores, the score stream. 36 configurations give 9000 campaigns. Each campaign is logged in full: its configuration, every per-level record (thresholds, the allowed number of calibration failures under both the binomial and the exact finite-population tail, the stated guarantees, calibration counts, level and remainder rates, map bound), the decision and reason for every design site, the interest and interpolation labels of every site and the frozen score of each certificate. The record also holds the code version, the package versions and the wall time of each campaign. For the maximum-likelihood Gaussian-process configurations, the end-of-level and final-map labels, which need a refit on the full measured set and change no decision, were not computed. The record lives in the repository under results/record (one directory per configuration: a compressed line-per-campaign log and a compressed array file), with a manifest, the summary below and the audit table.

**Table S5.1.** Exceedances of every stated rate over all certified levels of all campaigns. "Allowed failure" is one minus the stated confidence; the interval is a 95 % Clopper–Pearson interval on the exceedance frequency (indicative, since levels of one campaign are not independent draws).

| Row | Runs | Measured (mean ± s.d.) | Event | Budget | Allowed failure | Exceedances / level checks | Rate | 95 % interval |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ir_separate_split_watson | 250 | 275 ± 51 | R_interest | 0.05 | 0.125 | 32/1000 | 0.032 | 0.022–0.045 |
| ir_separate_split_watson | 250 | 275 ± 51 | R_interp | 0.05 | 0.125 | 0/1000 | 0.000 | 0.000–0.004 |
| ir_separate_split_watson | 250 | 275 ± 51 | R_E | 0.10 | 0.250 | 0/1000 | 0.000 | 0.000–0.004 |
| ir_nested_watson | 250 | 297 ± 53 | R_E | 0.10 | 0.250 | 72/1000 | 0.072 | 0.057–0.090 |
| ir_priority_watson | 250 | 331 ± 79 | R_E | 0.10 | 0.250 | 72/1000 | 0.072 | 0.057–0.090 |
| ir_nested_gp_mle | 250 | 283 ± 36 | R_E | 0.10 | 0.250 | 72/1000 | 0.072 | 0.057–0.090 |
| ir_nested_gp_design | 250 | 290 ± 42 | R_E | 0.10 | 0.250 | 0/1000 | 0.000 | 0.000–0.004 |
| ir_nested_gp_nonstationary | 250 | 305 ± 45 | R_E | 0.10 | 0.250 | 33/1000 | 0.033 | 0.023–0.046 |
| nacl_fwhm_separate_watson | 250 | 719 ± 60 | R_interest | 0.10 | 0.100 | 64/1000 | 0.064 | 0.050–0.081 |
| nacl_fwhm_separate_watson | 250 | 719 ± 60 | R_interp | 0.10 | 0.100 | 57/1000 | 0.057 | 0.043–0.073 |
| nacl_fwhm_separate_watson | 250 | 719 ± 60 | R_E | 0.20 | 0.200 | 9/1000 | 0.009 | 0.004–0.017 |
| nacl_fwhm_nested_watson | 250 | 614 ± 56 | R_E | 0.20 | 0.200 | 112/1000 | 0.112 | 0.093–0.133 |
| nacl_fwhm_priority_watson | 250 | 678 ± 39 | R_E | 0.20 | 0.200 | 123/1000 | 0.123 | 0.103–0.145 |
| nacl_fwhm_nested_gp_mle | 250 | 745 ± 72 | R_E | 0.20 | 0.200 | 119/1000 | 0.119 | 0.100–0.141 |
| nacl_fwhm_nested_gp_design | 250 | 760 ± 70 | R_E | 0.20 | 0.200 | 110/1000 | 0.110 | 0.091–0.131 |
| nacl_fwhm_nested_gp_nonstationary | 250 | 778 ± 59 | R_E | 0.20 | 0.200 | 119/1000 | 0.119 | 0.100–0.141 |
| syn_peak_2cert_separate_watson | 250 | 338 ± 26 | R_interest | 0.10 | 0.100 | 73/1500 | 0.049 | 0.038–0.061 |
| syn_peak_2cert_separate_watson | 250 | 338 ± 26 | R_interp | 0.10 | 0.100 | 67/1500 | 0.045 | 0.035–0.056 |
| syn_peak_2cert_separate_watson | 250 | 338 ± 26 | R_E | 0.20 | 0.200 | 5/1500 | 0.003 | 0.001–0.008 |
| syn_peak_2cert_nested_watson | 250 | 334 ± 26 | R_E | 0.20 | 0.200 | 161/1500 | 0.107 | 0.092–0.124 |
| syn_peak_2cert_priority_watson | 250 | 628 ± 61 | R_E | 0.20 | 0.200 | 156/1500 | 0.104 | 0.089–0.121 |
| syn_peak_2cert_nested_gp_mle | 250 | 1139 ± 215 | R_E | 0.20 | 0.200 | 160/1500 | 0.107 | 0.091–0.123 |
| syn_peak_2cert_nested_gp_design | 250 | 1042 ± 201 | R_E | 0.20 | 0.200 | 184/1500 | 0.123 | 0.106–0.140 |
| syn_peak_2cert_nested_gp_nonstationary | 250 | 1447 ± 134 | R_E | 0.20 | 0.200 | 161/1500 | 0.107 | 0.092–0.124 |
| ir_tight_sibson | 250 | 665 ± 72 | R_E | 0.10 | 0.250 | 211/1000 | 0.211 | 0.186–0.238 |
| ir_tight_gp_mle | 250 | 770 ± 53 | R_E | 0.10 | 0.250 | 201/1000 | 0.201 | 0.177–0.227 |
| ir_tight_gp_design | 250 | 788 ± 51 | R_E | 0.10 | 0.250 | 190/1000 | 0.190 | 0.166–0.216 |
| ir_tight_gp_nonstationary | 250 | 794 ± 35 | R_E | 0.10 | 0.250 | 187/1000 | 0.187 | 0.163–0.213 |
| ir_tight_interp_sibson | 250 | 615 ± 65 | R_E | 0.10 | 0.250 | 189/1000 | 0.189 | 0.165–0.215 |
| ir_tight_interp_gp_mle | 250 | 800 ± 56 | R_E | 0.10 | 0.250 | 182/1000 | 0.182 | 0.159–0.207 |
| ir_tight_interp_gp_design | 250 | 815 ± 52 | R_E | 0.10 | 0.250 | 198/1000 | 0.198 | 0.174–0.224 |
| ir_tight_interp_gp_nonstationary | 250 | 846 ± 33 | R_E | 0.10 | 0.250 | 189/1000 | 0.189 | 0.165–0.215 |
| ir_separate_random | 250 | 364 ± 126 | R_interest | 0.05 | 0.125 | 77/1000 | 0.077 | 0.061–0.095 |
| ir_separate_random | 250 | 364 ± 126 | R_interp | 0.05 | 0.125 | 0/1000 | 0.000 | 0.000–0.004 |
| ir_separate_random | 250 | 364 ± 126 | R_E | 0.10 | 0.250 | 9/1000 | 0.009 | 0.004–0.017 |
| ir_nested_random | 250 | 711 ± 74 | R_E | 0.10 | 0.250 | 194/1000 | 0.194 | 0.170–0.220 |
| ir_priority_random | 250 | 808 ± 51 | R_E | 0.10 | 0.250 | 197/1000 | 0.197 | 0.173–0.223 |
| nacl_fwhm_separate_random | 250 | 928 ± 45 | R_interest | 0.10 | 0.100 | 67/1000 | 0.067 | 0.052–0.084 |
| nacl_fwhm_separate_random | 250 | 928 ± 45 | R_interp | 0.10 | 0.100 | 55/1000 | 0.055 | 0.042–0.071 |
| nacl_fwhm_separate_random | 250 | 928 ± 45 | R_E | 0.20 | 0.200 | 17/1000 | 0.017 | 0.010–0.027 |
| nacl_fwhm_nested_random | 250 | 861 ± 50 | R_E | 0.20 | 0.200 | 127/1000 | 0.127 | 0.107–0.149 |
| nacl_fwhm_priority_random | 250 | 874 ± 49 | R_E | 0.20 | 0.200 | 132/1000 | 0.132 | 0.112–0.155 |
| syn_peak_2cert_separate_random | 250 | 991 ± 286 | R_interest | 0.10 | 0.100 | 76/1500 | 0.051 | 0.040–0.063 |
| syn_peak_2cert_separate_random | 250 | 991 ± 286 | R_interp | 0.10 | 0.100 | 62/1500 | 0.041 | 0.032–0.053 |
| syn_peak_2cert_separate_random | 250 | 991 ± 286 | R_E | 0.20 | 0.200 | 7/1500 | 0.005 | 0.002–0.010 |
| syn_peak_2cert_nested_random | 250 | 1076 ± 187 | R_E | 0.20 | 0.200 | 161/1500 | 0.107 | 0.092–0.124 |
| syn_peak_2cert_priority_random | 250 | 1322 ± 185 | R_E | 0.20 | 0.200 | 161/1500 | 0.107 | 0.092–0.124 |
| ir_tight_random | 250 | 865 ± 29 | R_E | 0.10 | 0.250 | 164/1000 | 0.164 | 0.142–0.188 |


**Table S5.2.** Attainment on fixed level populations: for the first five campaigns of each configuration and every certified level, the calibration draw was repeated 500 times on the recorded population and the exceedance frequency of each stated rate compared with the exact finite-population worst case at the allowed number of failures (Appendix A). The ratio is taken over levels where the budget can be exceeded. Union-bound statements of the per-claim form are omitted, since their worst case is not a single hypergeometric tail.

| Configuration | Event | Levels audited | Mean worst case | Mean attained | Attained / worst case | Levels where the budget cannot be exceeded |
| --- | --- | --- | --- | --- | --- | --- |
| ir_separate_split_watson | R_interest | 20 | 0.080 | 0.038 | 0.96 | 8 of 20 |
| ir_separate_split_watson | R_interp | 20 | 0.080 | 0.000 | – | 20 of 20 |
| ir_nested_watson | R_E | 20 | 0.201 | 0.062 | 0.99 | 15 of 20 |
| ir_priority_watson | R_E | 20 | 0.201 | 0.062 | 0.99 | 15 of 20 |
| ir_nested_gp_mle | R_E | 20 | 0.201 | 0.062 | 0.99 | 15 of 20 |
| ir_nested_gp_design | R_E | 20 | 0.201 | 0.000 | – | 20 of 20 |
| ir_nested_gp_nonstationary | R_E | 20 | 0.201 | 0.032 | 0.51 | 15 of 20 |
| nacl_fwhm_separate_watson | R_interest | 20 | 0.061 | 0.060 | 0.98 | 0 of 20 |
| nacl_fwhm_separate_watson | R_interp | 20 | 0.061 | 0.062 | 1.03 | 0 of 20 |
| nacl_fwhm_nested_watson | R_E | 20 | 0.120 | 0.119 | 0.99 | 0 of 20 |
| nacl_fwhm_priority_watson | R_E | 20 | 0.120 | 0.119 | 0.99 | 0 of 20 |
| nacl_fwhm_nested_gp_mle | R_E | 20 | 0.120 | 0.115 | 0.96 | 0 of 20 |
| nacl_fwhm_nested_gp_design | R_E | 20 | 0.120 | 0.116 | 0.96 | 0 of 20 |
| nacl_fwhm_nested_gp_nonstationary | R_E | 20 | 0.120 | 0.113 | 0.94 | 0 of 20 |
| syn_peak_2cert_separate_watson | R_interest | 30 | 0.054 | 0.055 | 1.02 | 0 of 30 |
| syn_peak_2cert_separate_watson | R_interp | 30 | 0.054 | 0.044 | 1.01 | 4 of 30 |
| syn_peak_2cert_nested_watson | R_E | 30 | 0.113 | 0.113 | 1.00 | 0 of 30 |
| syn_peak_2cert_priority_watson | R_E | 30 | 0.113 | 0.114 | 1.01 | 0 of 30 |
| syn_peak_2cert_nested_gp_mle | R_E | 30 | 0.113 | 0.112 | 0.99 | 0 of 30 |
| syn_peak_2cert_nested_gp_design | R_E | 30 | 0.113 | 0.114 | 1.01 | 0 of 30 |
| syn_peak_2cert_nested_gp_nonstationary | R_E | 30 | 0.113 | 0.118 | 1.04 | 0 of 30 |
| ir_tight_sibson | R_E | 20 | 0.201 | 0.198 | 0.98 | 0 of 20 |
| ir_tight_gp_mle | R_E | 20 | 0.201 | 0.202 | 1.00 | 0 of 20 |
| ir_tight_gp_design | R_E | 20 | 0.201 | 0.199 | 0.99 | 0 of 20 |
| ir_tight_gp_nonstationary | R_E | 20 | 0.201 | 0.197 | 0.98 | 0 of 20 |
| ir_tight_interp_sibson | R_E | 20 | 0.201 | 0.197 | 0.98 | 0 of 20 |
| ir_tight_interp_gp_mle | R_E | 20 | 0.201 | 0.206 | 1.02 | 0 of 20 |
| ir_tight_interp_gp_design | R_E | 20 | 0.201 | 0.203 | 1.01 | 0 of 20 |
| ir_tight_interp_gp_nonstationary | R_E | 20 | 0.201 | 0.197 | 0.98 | 0 of 20 |
| ir_separate_random | R_interest | 20 | 0.080 | 0.079 | 0.99 | 0 of 20 |
| ir_separate_random | R_interp | 20 | 0.080 | 0.000 | – | 20 of 20 |
| ir_nested_random | R_E | 20 | 0.201 | 0.205 | 1.02 | 0 of 20 |
| ir_priority_random | R_E | 20 | 0.201 | 0.202 | 1.01 | 0 of 20 |
| nacl_fwhm_separate_random | R_interest | 20 | 0.061 | 0.063 | 1.04 | 0 of 20 |
| nacl_fwhm_separate_random | R_interp | 20 | 0.061 | 0.060 | 0.99 | 0 of 20 |
| nacl_fwhm_nested_random | R_E | 20 | 0.120 | 0.121 | 1.01 | 0 of 20 |
| nacl_fwhm_priority_random | R_E | 20 | 0.120 | 0.128 | 1.06 | 0 of 20 |
| syn_peak_2cert_separate_random | R_interest | 30 | 0.054 | 0.053 | 0.98 | 0 of 30 |
| syn_peak_2cert_separate_random | R_interp | 30 | 0.054 | 0.032 | 0.94 | 8 of 30 |
| syn_peak_2cert_nested_random | R_E | 30 | 0.113 | 0.112 | 0.99 | 0 of 30 |
| syn_peak_2cert_priority_random | R_E | 30 | 0.113 | 0.114 | 1.01 | 0 of 30 |
| ir_tight_random | R_E | 20 | 0.201 | 0.195 | 0.97 | 0 of 20 |
