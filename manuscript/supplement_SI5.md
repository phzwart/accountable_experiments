# SI 5. The run record (draft 1)

From round 3 the synthetic map carries the interpolation claim alone on the full profile (rtol = atol = 0.005) at a budget of 0.10 and confidence 0.80; with one claim the three forms of guarantee coincide, so one configuration stands for them. The two-claim configurations used before are kept in the record and in the archive of earlier results. Every configuration of Section 5 was run as 250 independent campaigns, random states 0 to 249, except the four Gaussian-process configurations of the synthetic map, run as 20 (random states 0 to 19) for their cost of one to three minutes each, and the NaCl process scored by its own failure probability, run as 50; a random state fixes the calibration draws of a campaign and, for random scores, the score stream. 34 configurations give 7380 campaigns; the comparisons of SI 5.3 add 250 campaigns each of three rules on three maps. Each campaign is logged in full: its configuration, every per-level record (thresholds, the allowed number of calibration failures under both the binomial and the exact finite-population tail, the stated guarantees, calibration counts, level and remainder rates, map bound), the decision and reason for every design site, the interest and interpolation labels of every site and the frozen score of each claim. The record also holds the code version, the package versions and the wall time of each campaign. For the maximum-likelihood Gaussian-process configurations, the end-of-level and final-map labels, which need a refit on the full measured set and change no decision, were not computed. The record lives in the repository under results/record (one directory per configuration: a compressed line-per-campaign log and a compressed array file), with a manifest, the summary below and the audit table.

**Table S5.1.** Exceedances of every stated rate over all guaranteed levels of all campaigns. "Allowed failure" is one minus the stated confidence; the interval is a 95 % Clopper–Pearson interval on the exceedance frequency (indicative, since levels of one campaign are not independent draws).

| Row | Runs | Measured (mean ± s.d.) | Event | Budget | Allowed failure | Exceedances / level checks | Rate | 95 % interval |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ir_separate_split_watson | 250 | 262 ± 28 | R_interest | 0.05 | 0.125 | 37/1000 | 0.037 | 0.026–0.051 |
| ir_separate_split_watson | 250 | 262 ± 28 | R_interp | 0.05 | 0.125 | 0/1000 | 0.000 | 0.000–0.004 |
| ir_separate_split_watson | 250 | 262 ± 28 | R_E | 0.10 | 0.250 | 0/1000 | 0.000 | 0.000–0.004 |
| ir_nested_watson | 250 | 295 ± 53 | R_E | 0.10 | 0.250 | 49/1000 | 0.049 | 0.036–0.064 |
| ir_priority_watson | 250 | 327 ± 80 | R_E | 0.10 | 0.250 | 49/1000 | 0.049 | 0.036–0.064 |
| ir_nested_gp_mle | 250 | 273 ± 31 | R_E | 0.10 | 0.250 | 49/1000 | 0.049 | 0.036–0.064 |
| ir_nested_gp_design | 250 | 281 ± 34 | R_E | 0.10 | 0.250 | 49/1000 | 0.049 | 0.036–0.064 |
| ir_nested_gp_nonstationary | 250 | 291 ± 41 | R_E | 0.10 | 0.250 | 1/1000 | 0.001 | 0.000–0.006 |
| nacl_fwhm_separate_watson | 250 | 719 ± 60 | R_interest | 0.10 | 0.100 | 64/1000 | 0.064 | 0.050–0.081 |
| nacl_fwhm_separate_watson | 250 | 719 ± 60 | R_interp | 0.10 | 0.100 | 57/1000 | 0.057 | 0.043–0.073 |
| nacl_fwhm_separate_watson | 250 | 719 ± 60 | R_E | 0.20 | 0.200 | 9/1000 | 0.009 | 0.004–0.017 |
| nacl_fwhm_nested_watson | 250 | 614 ± 56 | R_E | 0.20 | 0.200 | 112/1000 | 0.112 | 0.093–0.133 |
| nacl_fwhm_priority_watson | 250 | 678 ± 39 | R_E | 0.20 | 0.200 | 123/1000 | 0.123 | 0.103–0.145 |
| nacl_fwhm_nested_gp_mle | 250 | 745 ± 72 | R_E | 0.20 | 0.200 | 119/1000 | 0.119 | 0.100–0.141 |
| nacl_fwhm_nested_gp_design | 250 | 760 ± 70 | R_E | 0.20 | 0.200 | 111/1000 | 0.111 | 0.092–0.132 |
| nacl_fwhm_nested_gp_nonstationary | 250 | 777 ± 60 | R_E | 0.20 | 0.200 | 123/1000 | 0.123 | 0.103–0.145 |
| syn_env_nested_watson | 250 | 932 ± 223 | R_E | 0.10 | 0.200 | 147/1500 | 0.098 | 0.083–0.114 |
| syn_env_nested_gp_mle | 20 | 1974 ± 55 | R_E | 0.10 | 0.200 | 13/120 | 0.108 | 0.059–0.178 |
| syn_env_nested_gp_design | 20 | 1946 ± 50 | R_E | 0.10 | 0.200 | 13/120 | 0.108 | 0.059–0.178 |
| syn_env_nested_gp_nonstationary | 20 | 2027 ± 39 | R_E | 0.10 | 0.200 | 8/120 | 0.067 | 0.029–0.127 |
| nacl_fwhm_nested_gpfail_mle | 50 | 761 ± 68 | R_E | 0.20 | 0.200 | 16/200 | 0.080 | 0.046–0.127 |
| syn_env_nested_gpfail_mle | 20 | 1991 ± 91 | R_E | 0.10 | 0.200 | 13/120 | 0.108 | 0.059–0.178 |
| ir_tight_sibson | 250 | 621 ± 70 | R_E | 0.10 | 0.250 | 193/1000 | 0.193 | 0.169–0.219 |
| ir_tight_gp_mle | 250 | 747 ± 56 | R_E | 0.10 | 0.250 | 179/1000 | 0.179 | 0.156–0.204 |
| ir_tight_gp_design | 250 | 753 ± 52 | R_E | 0.10 | 0.250 | 191/1000 | 0.191 | 0.167–0.217 |
| ir_tight_gp_nonstationary | 250 | 799 ± 40 | R_E | 0.10 | 0.250 | 192/1000 | 0.192 | 0.168–0.218 |
| ir_tight_interp_sibson | 250 | 604 ± 65 | R_E | 0.10 | 0.250 | 190/1000 | 0.190 | 0.166–0.216 |
| ir_tight_interp_gp_mle | 250 | 792 ± 58 | R_E | 0.10 | 0.250 | 170/1000 | 0.170 | 0.147–0.195 |
| ir_tight_interp_gp_design | 250 | 797 ± 56 | R_E | 0.10 | 0.250 | 200/1000 | 0.200 | 0.176–0.226 |
| ir_tight_interp_gp_nonstationary | 250 | 854 ± 35 | R_E | 0.10 | 0.250 | 194/1000 | 0.194 | 0.170–0.220 |
| ir_separate_random | 250 | 335 ± 84 | R_interest | 0.05 | 0.125 | 78/1000 | 0.078 | 0.062–0.096 |
| ir_separate_random | 250 | 335 ± 84 | R_interp | 0.05 | 0.125 | 0/1000 | 0.000 | 0.000–0.004 |
| ir_separate_random | 250 | 335 ± 84 | R_E | 0.10 | 0.250 | 8/1000 | 0.008 | 0.003–0.016 |
| ir_nested_random | 250 | 716 ± 71 | R_E | 0.10 | 0.250 | 168/1000 | 0.168 | 0.145–0.193 |
| ir_priority_random | 250 | 817 ± 49 | R_E | 0.10 | 0.250 | 170/1000 | 0.170 | 0.147–0.195 |
| nacl_fwhm_separate_random | 250 | 928 ± 45 | R_interest | 0.10 | 0.100 | 67/1000 | 0.067 | 0.052–0.084 |
| nacl_fwhm_separate_random | 250 | 928 ± 45 | R_interp | 0.10 | 0.100 | 55/1000 | 0.055 | 0.042–0.071 |
| nacl_fwhm_separate_random | 250 | 928 ± 45 | R_E | 0.20 | 0.200 | 17/1000 | 0.017 | 0.010–0.027 |
| nacl_fwhm_nested_random | 250 | 861 ± 50 | R_E | 0.20 | 0.200 | 127/1000 | 0.127 | 0.107–0.149 |
| nacl_fwhm_priority_random | 250 | 874 ± 49 | R_E | 0.20 | 0.200 | 132/1000 | 0.132 | 0.112–0.155 |
| syn_env_nested_random | 250 | 1578 ± 248 | R_E | 0.10 | 0.200 | 149/1500 | 0.099 | 0.085–0.116 |
| ir_tight_random | 250 | 871 ± 31 | R_E | 0.10 | 0.250 | 194/1000 | 0.194 | 0.170–0.220 |


**Table S5.2.** Attainment on fixed level populations: for the first 20 campaigns of each configuration and every guaranteed level, the calibration draw was repeated 1000 times on the recorded population and the exceedance frequency of each stated rate compared with the exact finite-population worst case at the allowed number of failures (Appendix A). The ratio is taken over levels where the budget can be exceeded. Union-bound statements of the per-claim form are omitted, since their worst case is not a single hypergeometric tail.

| Configuration | Event | Levels audited | Mean worst case | Mean attained | Attained / worst case | Levels where the budget cannot be exceeded |
| --- | --- | --- | --- | --- | --- | --- |
| ir_separate_split_watson | R_interest | 80 | 0.075 | 0.028 | 1.01 | 40 of 80 |
| ir_separate_split_watson | R_interp | 80 | 0.075 | 0.000 | – | 80 of 80 |
| ir_nested_watson | R_E | 80 | 0.190 | 0.056 | 1.01 | 60 of 80 |
| ir_priority_watson | R_E | 80 | 0.190 | 0.056 | 1.01 | 60 of 80 |
| ir_nested_gp_mle | R_E | 80 | 0.190 | 0.056 | 1.01 | 60 of 80 |
| ir_nested_gp_design | R_E | 80 | 0.190 | 0.056 | 1.01 | 60 of 80 |
| ir_nested_gp_nonstationary | R_E | 80 | 0.190 | 0.000 | – | 80 of 80 |
| nacl_fwhm_separate_watson | R_interest | 80 | 0.061 | 0.062 | 1.02 | 0 of 80 |
| nacl_fwhm_separate_watson | R_interp | 80 | 0.061 | 0.060 | 1.00 | 0 of 80 |
| nacl_fwhm_nested_watson | R_E | 80 | 0.120 | 0.116 | 0.97 | 0 of 80 |
| nacl_fwhm_priority_watson | R_E | 80 | 0.120 | 0.119 | 0.99 | 0 of 80 |
| nacl_fwhm_nested_gp_mle | R_E | 80 | 0.120 | 0.117 | 0.97 | 0 of 80 |
| nacl_fwhm_nested_gp_design | R_E | 80 | 0.120 | 0.117 | 0.98 | 0 of 80 |
| nacl_fwhm_nested_gp_nonstationary | R_E | 80 | 0.120 | 0.119 | 0.99 | 0 of 80 |
| syn_env_nested_watson | R_E | 120 | 0.095 | 0.095 | 0.99 | 0 of 120 |
| ir_tight_sibson | R_E | 80 | 0.190 | 0.193 | 1.02 | 0 of 80 |
| ir_tight_gp_mle | R_E | 80 | 0.190 | 0.191 | 1.00 | 0 of 80 |
| ir_tight_gp_design | R_E | 80 | 0.190 | 0.192 | 1.01 | 0 of 80 |
| ir_tight_gp_nonstationary | R_E | 80 | 0.190 | 0.192 | 1.01 | 0 of 80 |
| ir_tight_interp_sibson | R_E | 80 | 0.190 | 0.192 | 1.01 | 0 of 80 |
| ir_tight_interp_gp_mle | R_E | 80 | 0.190 | 0.192 | 1.01 | 0 of 80 |
| ir_tight_interp_gp_design | R_E | 80 | 0.190 | 0.194 | 1.02 | 0 of 80 |
| ir_tight_interp_gp_nonstationary | R_E | 80 | 0.190 | 0.192 | 1.01 | 0 of 80 |
| ir_separate_random | R_interest | 80 | 0.075 | 0.076 | 1.02 | 0 of 80 |
| ir_separate_random | R_interp | 80 | 0.075 | 0.000 | – | 80 of 80 |
| ir_nested_random | R_E | 80 | 0.190 | 0.190 | 1.00 | 0 of 80 |
| ir_priority_random | R_E | 80 | 0.190 | 0.193 | 1.02 | 0 of 80 |
| nacl_fwhm_separate_random | R_interest | 80 | 0.061 | 0.061 | 1.01 | 0 of 80 |
| nacl_fwhm_separate_random | R_interp | 80 | 0.061 | 0.060 | 0.99 | 0 of 80 |
| nacl_fwhm_nested_random | R_E | 80 | 0.120 | 0.116 | 0.97 | 0 of 80 |
| nacl_fwhm_priority_random | R_E | 80 | 0.120 | 0.121 | 1.01 | 0 of 80 |
| syn_env_nested_random | R_E | 120 | 0.095 | 0.097 | 1.01 | 0 of 120 |
| ir_tight_random | R_E | 80 | 0.190 | 0.179 | 0.94 | 0 of 80 |

**Table S5.3.** Observed exceedances against the picked failure probability. On each level the rule picks the largest attainable worst-case failure probability $\delta_L$ at or below the nominal $\delta$; the guarantee made on that level is $P(R > \varepsilon) \le \delta_L$. "Allowed exceedances" is the sum of $\delta_L$ over all level checks of a configuration; the probability of the observed count treats checks as independent Bernoulli trials with success probabilities $\delta_L$ and is indicative. For the union-bound statement of the per-claim form, $\delta_L$ is the sum of the two per-claim picked levels. "Reachable" checks are those on which covering every coverable site would exceed the budget.

| Configuration | Event | Nominal δ | Checks | Mean picked δ_L | Allowed exceedances (Σ δ_L) | Observed | Observed / allowed | P(≥ observed) under δ_L | Reachable checks | Allowed on reachable | Observed on reachable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ir_separate_split_watson | R_E | 0.250 | 1000 | 0.150 | 149.6 | 0 | 0.00 | 1.000 | 250 | 16.2 | 0 |
| ir_separate_split_watson | R_interest | 0.125 | 1000 | 0.075 | 74.8 | 37 | 0.49 | 1.000 | 548 | 31.8 | 37 |
| ir_separate_split_watson | R_interp | 0.125 | 1000 | 0.075 | 74.8 | 0 | 0.00 | 1.000 | 0 | 0.0 | 0 |
| ir_nested_watson | R_E | 0.250 | 1000 | 0.190 | 190.2 | 49 | 0.26 | 1.000 | 250 | 55.6 | 49 |
| ir_priority_watson | R_E | 0.250 | 1000 | 0.190 | 190.2 | 49 | 0.26 | 1.000 | 250 | 55.6 | 49 |
| ir_nested_gp_mle | R_E | 0.250 | 1000 | 0.190 | 190.2 | 49 | 0.26 | 1.000 | 250 | 55.6 | 49 |
| ir_nested_gp_design | R_E | 0.250 | 1000 | 0.190 | 190.2 | 49 | 0.26 | 1.000 | 250 | 55.6 | 49 |
| ir_nested_gp_nonstationary | R_E | 0.250 | 1000 | 0.190 | 190.2 | 1 | 0.01 | 1.000 | 3 | 0.4 | 1 |
| nacl_fwhm_separate_watson | R_E | 0.200 | 1000 | 0.121 | 121.3 | 9 | 0.07 | 1.000 | 1000 | 121.3 | 9 |
| nacl_fwhm_separate_watson | R_interest | 0.100 | 1000 | 0.061 | 60.6 | 64 | 1.06 | 0.346 | 1000 | 60.6 | 64 |
| nacl_fwhm_separate_watson | R_interp | 0.100 | 1000 | 0.061 | 60.6 | 57 | 0.94 | 0.703 | 1000 | 60.6 | 57 |
| nacl_fwhm_nested_watson | R_E | 0.200 | 1000 | 0.120 | 120.1 | 112 | 0.93 | 0.798 | 1000 | 120.1 | 112 |
| nacl_fwhm_priority_watson | R_E | 0.200 | 1000 | 0.120 | 120.1 | 123 | 1.02 | 0.404 | 1000 | 120.1 | 123 |
| nacl_fwhm_nested_gp_mle | R_E | 0.200 | 1000 | 0.120 | 120.1 | 119 | 0.99 | 0.558 | 1000 | 120.1 | 119 |
| nacl_fwhm_nested_gp_design | R_E | 0.200 | 1000 | 0.120 | 120.1 | 111 | 0.92 | 0.825 | 1000 | 120.1 | 111 |
| nacl_fwhm_nested_gp_nonstationary | R_E | 0.200 | 1000 | 0.120 | 120.1 | 123 | 1.02 | 0.404 | 1000 | 120.1 | 123 |
| syn_env_nested_watson | R_E | 0.200 | 1500 | 0.095 | 143.0 | 147 | 1.03 | 0.372 | 1500 | 143.0 | 147 |
| syn_env_nested_gp_mle | R_E | 0.200 | 120 | 0.095 | 11.4 | 13 | 1.14 | 0.355 | 120 | 11.4 | 13 |
| syn_env_nested_gp_design | R_E | 0.200 | 120 | 0.095 | 11.4 | 13 | 1.14 | 0.355 | 120 | 11.4 | 13 |
| syn_env_nested_gp_nonstationary | R_E | 0.200 | 120 | 0.095 | 11.4 | 8 | 0.70 | 0.900 | 120 | 11.4 | 8 |
| nacl_fwhm_nested_gpfail_mle | R_E | 0.200 | 200 | 0.120 | 24.0 | 16 | 0.67 | 0.974 | 200 | 24.0 | 16 |
| syn_env_nested_gpfail_mle | R_E | 0.200 | 120 | 0.095 | 11.4 | 13 | 1.14 | 0.355 | 120 | 11.4 | 13 |
| ir_tight_sibson | R_E | 0.250 | 1000 | 0.190 | 190.2 | 193 | 1.01 | 0.424 | 1000 | 190.2 | 193 |
| ir_tight_gp_mle | R_E | 0.250 | 1000 | 0.190 | 190.2 | 179 | 0.94 | 0.828 | 1000 | 190.2 | 179 |
| ir_tight_gp_design | R_E | 0.250 | 1000 | 0.190 | 190.2 | 191 | 1.00 | 0.488 | 1000 | 190.2 | 191 |
| ir_tight_gp_nonstationary | R_E | 0.250 | 1000 | 0.190 | 190.2 | 192 | 1.01 | 0.456 | 1000 | 190.2 | 192 |
| ir_tight_interp_sibson | R_E | 0.250 | 1000 | 0.190 | 190.2 | 190 | 1.00 | 0.520 | 1000 | 190.2 | 190 |
| ir_tight_interp_gp_mle | R_E | 0.250 | 1000 | 0.190 | 190.2 | 170 | 0.89 | 0.955 | 1000 | 190.2 | 170 |
| ir_tight_interp_gp_design | R_E | 0.250 | 1000 | 0.190 | 190.2 | 200 | 1.05 | 0.226 | 1000 | 190.2 | 200 |
| ir_tight_interp_gp_nonstationary | R_E | 0.250 | 1000 | 0.190 | 190.2 | 194 | 1.02 | 0.393 | 1000 | 190.2 | 194 |
| ir_separate_random | R_E | 0.250 | 1000 | 0.150 | 149.6 | 8 | 0.05 | 1.000 | 1000 | 149.6 | 8 |
| ir_separate_random | R_interest | 0.125 | 1000 | 0.075 | 74.8 | 78 | 1.04 | 0.366 | 1000 | 74.8 | 78 |
| ir_separate_random | R_interp | 0.125 | 1000 | 0.075 | 74.8 | 0 | 0.00 | 1.000 | 0 | 0.0 | 0 |
| ir_nested_random | R_E | 0.250 | 1000 | 0.190 | 190.2 | 168 | 0.88 | 0.968 | 1000 | 190.2 | 168 |
| ir_priority_random | R_E | 0.250 | 1000 | 0.190 | 190.2 | 170 | 0.89 | 0.955 | 1000 | 190.2 | 170 |
| nacl_fwhm_separate_random | R_E | 0.200 | 1000 | 0.121 | 121.3 | 17 | 0.14 | 1.000 | 1000 | 121.3 | 17 |
| nacl_fwhm_separate_random | R_interest | 0.100 | 1000 | 0.061 | 60.6 | 67 | 1.11 | 0.216 | 1000 | 60.6 | 67 |
| nacl_fwhm_separate_random | R_interp | 0.100 | 1000 | 0.061 | 60.6 | 55 | 0.91 | 0.790 | 1000 | 60.6 | 55 |
| nacl_fwhm_nested_random | R_E | 0.200 | 1000 | 0.120 | 120.1 | 127 | 1.06 | 0.265 | 1000 | 120.1 | 127 |
| nacl_fwhm_priority_random | R_E | 0.200 | 1000 | 0.120 | 120.1 | 132 | 1.10 | 0.134 | 1000 | 120.1 | 132 |
| syn_env_nested_random | R_E | 0.200 | 1500 | 0.095 | 143.0 | 149 | 1.04 | 0.306 | 1500 | 143.0 | 149 |
| ir_tight_random | R_E | 0.250 | 1000 | 0.190 | 190.2 | 194 | 1.02 | 0.393 | 1000 | 190.2 | 194 |

## SI 5.2 Further detail on the record

For the 32 stated rates (configuration and statement) whose budget can be exceeded on every level, union-bound statements excluded, the observed number of exceedances lay between 0.88 and 1.11 times the number expected under the picked failure probabilities; the smallest one-sided probability of the observed count was 0.10 (Table S5.3). On the IR map at its original tolerance, three of the four levels hold too few failing sites for the budget to be reached, and the record shows no exceedance there. The union-bound statement of the per-claim form is exceeded far less often than its picked failure probability permits, since two claims seldom approach their budgets on the same level. Repeating the calibration draw on the recorded level populations, the attained exceedance probability, pooled over the levels of each configuration, lay between 0.94 and 1.02 times $\delta_L$ wherever the budget could be exceeded (Table S5.2).

**Order of operations.** On a simulated level of 399 sites with informative scores, a budget of 0.10 and a picked failure probability of 0.206, the calibration draw was repeated 4000 times. Scores frozen before a uniform draw: 822 exceedances (0.205). Scores that knew the true labels, frozen before the draw: 819 (0.205). Scores of the failing calibration sites raised after the draw and thresholded on the same labels: 4000 (1.00). Calibration sample taken from the half of the level ranked least safe: 2502 (0.63). Most favourable of five draws kept: 2771 (0.69). On a simulated level of the same size with uninformative scores (Fig. S3), the sequential rule, which sets the interpolation threshold on the calibration sites the interest threshold left uncovered: 28.8 %; the priority rule, which fixes the same preference in advance: 20.5 %, at the same picked failure probability of 0.206.

## SI 5.3 Plans guaranteed for all levels together, and two baselines

**Plans guaranteed for all levels together.** The failure probability $1 - c$ of the specification is divided equally among the guaranteed levels when the plan is declared, four on the IR and NaCl maps and six on the synthetic map, so each level runs at confidence $1 - (1 - c)/n$ and, by the union bound, every level holds together with probability at least $c$. Random states, scores, predictor and budget are those of the plans guaranteed level by level of Table 3.

**Conformal risk control.** Along the same path and on the same calibration draw, the threshold admits the largest number $k$ of failing calibration sites with $(k + 1)/(m + 1) \le \varepsilon$ [Angelopoulos2024]. This bounds the expected share of the level skipped in error, averaged over draws, and makes no statement about a single level. At $m = 40$ it allows $k = 3$ at $\varepsilon = 0.10$ and $k = 7$ at $\varepsilon = 0.20$.

**A uniform sample of the same size.** The seed levels and a uniform random sample of the remaining sites, to the mean number measured by the plan guaranteed level by level; every other site is predicted from all measured sites with the same natural-neighbour predictor and counted when the prediction fails the claim's metric. The final maps of the plans guaranteed level by level are scored in the same way: skipped sites predicted from all sites measured by the end of the campaign.

**Table S5.4.** Plans guaranteed level by level and for all levels together, conformal risk control and a uniform sample of the same size. Exceedances on the shared rate: share of level checks over budget and share of campaigns with at least one level over budget. Last column: share of sites on guaranteed levels whose prediction from all measured sites fails the metric (final map).

| Dataset | Rule | Campaigns | Sites measured | Levels over budget | Campaigns over budget | Final-map share outside |
| --- | --- | --- | --- | --- | --- | --- |
| IR map (ε = 0.10) | per level at 0.75 | 250 | 295 ± 53 | 4.9 % | 19.6 % | 0.4 % |
| | plan at 0.75 (δ = 0.062 per level) | 250 | 415 ± 82 | 0.1 % | 0.4 % | |
| | conformal risk control | 250 | 260 | 4.9 % | 19.6 % | |
| | uniform sample | 250 | 295 | — | — | 0.5 % |
| NaCl scan (ε = 0.20) | per level at 0.80 | 250 | 614 ± 56 | 11.2 % | 38.4 % | 18.0 % |
| | plan at 0.80 (δ = 0.050 per level) | 250 | 694 ± 58 | 2.7 % | 9.6 % | |
| | conformal risk control | 250 | 542 | 34.7 % | 80.8 % | |
| | uniform sample | 250 | 614 | — | — | 22.0 % |
| Synthetic map (ε = 0.10) | per level at 0.80 | 250 | 932 ± 223 | 9.8 % | 46.0 % | 3.6 % |
| | plan at 0.80 (δ = 0.033 per level) | 250 | 1189 ± 286 | 1.1 % | 6.4 % | |
| | conformal risk control | 250 | 673 | 32.3 % | 89.6 % | |
| | uniform sample | 250 | 932 | — | — | 10.4 % |

Plans guaranteed for all levels together exceeded the budget on 1, 27 and 16 level checks of 1000, 1000 and 1500, against 30.2, 27.5 and 13.2 expected under the picked failure probabilities. Conformal risk control kept its mean share of a level skipped in error at 5.7 %, 18.8 % and 8.8 % against budgets of 10 %, 20 % and 10 %. Uniform samples left 0.5 ± 0.2 %, 22.0 ± 1.0 % and 10.4 ± 0.7 % of sites on guaranteed levels outside tolerance; the final maps of the plans guaranteed level by level left 0.4 ± 0.3 %, 18.0 ± 3.8 % and 3.6 ± 1.8 %.
