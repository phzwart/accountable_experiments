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
| ir_nested_gp_design | R_E | 0.250 | 1000 | 0.190 | 190.2 | 50 | 0.26 | 1.000 | 250 | 55.6 | 50 |
| ir_nested_gp_nonstationary | R_E | 0.250 | 1000 | 0.190 | 190.2 | 2 | 0.01 | 1.000 | 11 | 1.7 | 2 |
| nacl_fwhm_separate_watson | R_E | 0.200 | 1000 | 0.121 | 121.3 | 9 | 0.07 | 1.000 | 1000 | 121.3 | 9 |
| nacl_fwhm_separate_watson | R_interest | 0.100 | 1000 | 0.061 | 60.6 | 64 | 1.06 | 0.346 | 1000 | 60.6 | 64 |
| nacl_fwhm_separate_watson | R_interp | 0.100 | 1000 | 0.061 | 60.6 | 57 | 0.94 | 0.703 | 1000 | 60.6 | 57 |
| nacl_fwhm_nested_watson | R_E | 0.200 | 1000 | 0.120 | 120.1 | 112 | 0.93 | 0.798 | 1000 | 120.1 | 112 |
| nacl_fwhm_priority_watson | R_E | 0.200 | 1000 | 0.120 | 120.1 | 123 | 1.02 | 0.404 | 1000 | 120.1 | 123 |
| nacl_fwhm_nested_gp_mle | R_E | 0.200 | 1000 | 0.120 | 120.1 | 119 | 0.99 | 0.558 | 1000 | 120.1 | 119 |
| nacl_fwhm_nested_gp_design | R_E | 0.200 | 1000 | 0.120 | 120.1 | 110 | 0.92 | 0.850 | 1000 | 120.1 | 110 |
| nacl_fwhm_nested_gp_nonstationary | R_E | 0.200 | 1000 | 0.120 | 120.1 | 119 | 0.99 | 0.558 | 1000 | 120.1 | 119 |
| syn_peak_2cert_separate_watson | R_E | 0.200 | 1500 | 0.108 | 161.9 | 5 | 0.03 | 1.000 | 1500 | 161.9 | 5 |
| syn_peak_2cert_separate_watson | R_interest | 0.100 | 1500 | 0.054 | 80.9 | 73 | 0.90 | 0.834 | 1500 | 80.9 | 73 |
| syn_peak_2cert_separate_watson | R_interp | 0.100 | 1500 | 0.054 | 80.9 | 67 | 0.83 | 0.955 | 1325 | 67.9 | 67 |
| syn_peak_2cert_nested_watson | R_E | 0.200 | 1500 | 0.113 | 169.8 | 161 | 0.95 | 0.779 | 1500 | 169.8 | 161 |
| syn_peak_2cert_priority_watson | R_E | 0.200 | 1500 | 0.113 | 169.8 | 156 | 0.92 | 0.883 | 1500 | 169.8 | 156 |
| syn_peak_2cert_nested_gp_mle | R_E | 0.200 | 1500 | 0.113 | 169.8 | 160 | 0.94 | 0.803 | 1500 | 169.8 | 160 |
| syn_peak_2cert_nested_gp_design | R_E | 0.200 | 1500 | 0.113 | 169.8 | 184 | 1.08 | 0.130 | 1500 | 169.8 | 184 |
| syn_peak_2cert_nested_gp_nonstationary | R_E | 0.200 | 1500 | 0.113 | 169.8 | 161 | 0.95 | 0.779 | 1500 | 169.8 | 161 |
| ir_tight_sibson | R_E | 0.250 | 1000 | 0.190 | 190.2 | 193 | 1.01 | 0.424 | 1000 | 190.2 | 193 |
| ir_tight_gp_mle | R_E | 0.250 | 1000 | 0.190 | 190.2 | 179 | 0.94 | 0.828 | 1000 | 190.2 | 179 |
| ir_tight_gp_design | R_E | 0.250 | 1000 | 0.190 | 190.2 | 190 | 1.00 | 0.520 | 1000 | 190.2 | 190 |
| ir_tight_gp_nonstationary | R_E | 0.250 | 1000 | 0.190 | 190.2 | 191 | 1.00 | 0.488 | 1000 | 190.2 | 191 |
| ir_tight_interp_sibson | R_E | 0.250 | 1000 | 0.190 | 190.2 | 190 | 1.00 | 0.520 | 1000 | 190.2 | 190 |
| ir_tight_interp_gp_mle | R_E | 0.250 | 1000 | 0.190 | 190.2 | 172 | 0.90 | 0.936 | 1000 | 190.2 | 172 |
| ir_tight_interp_gp_design | R_E | 0.250 | 1000 | 0.190 | 190.2 | 194 | 1.02 | 0.393 | 1000 | 190.2 | 194 |
| ir_tight_interp_gp_nonstationary | R_E | 0.250 | 1000 | 0.190 | 190.2 | 187 | 0.98 | 0.616 | 1000 | 190.2 | 187 |
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
| syn_peak_2cert_separate_random | R_E | 0.200 | 1500 | 0.108 | 161.9 | 7 | 0.04 | 1.000 | 1500 | 161.9 | 7 |
| syn_peak_2cert_separate_random | R_interest | 0.100 | 1500 | 0.054 | 80.9 | 76 | 0.94 | 0.730 | 1500 | 80.9 | 76 |
| syn_peak_2cert_separate_random | R_interp | 0.100 | 1500 | 0.054 | 80.9 | 62 | 0.77 | 0.990 | 1104 | 51.9 | 62 |
| syn_peak_2cert_nested_random | R_E | 0.200 | 1500 | 0.113 | 169.8 | 161 | 0.95 | 0.779 | 1500 | 169.8 | 161 |
| syn_peak_2cert_priority_random | R_E | 0.200 | 1500 | 0.113 | 169.8 | 161 | 0.95 | 0.779 | 1500 | 169.8 | 161 |
| ir_tight_random | R_E | 0.250 | 1000 | 0.190 | 190.2 | 194 | 1.02 | 0.393 | 1000 | 190.2 | 194 |
