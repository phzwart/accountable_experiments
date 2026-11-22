# Observed exceedances against the picked failure probability

δ_L is the worst-case failure probability at the number of allowed calibration failures the rule picked on each level (the attainable level at or below the nominal δ). 'Allowed exceedances' is the sum of δ_L over all level checks; the p-value treats checks as independent (indicative). 'Reachable' checks are those on which covering every coverable site would exceed the budget.

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
