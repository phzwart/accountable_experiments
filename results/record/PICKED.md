# Observed exceedances against the picked failure probability

δ_L is the worst-case failure probability at the number of allowed calibration failures the rule picked on each level (the attainable level at or below the nominal δ). 'Allowed exceedances' is the sum of δ_L over all level checks; the p-value treats checks as independent (indicative). 'Reachable' checks are those on which covering every coverable site would exceed the budget.

| Configuration | Event | Nominal δ | Checks | Mean picked δ_L | Allowed exceedances (Σ δ_L) | Observed | Observed / allowed | P(≥ observed) under δ_L | Reachable checks | Allowed on reachable | Observed on reachable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ir_separate_split_watson | R_E | 0.250 | 1000 | 0.160 | 159.6 | 0 | 0.00 | 1.000 | 250 | 9.3 | 0 |
| ir_separate_split_watson | R_interest | 0.125 | 1000 | 0.080 | 79.8 | 32 | 0.40 | 1.000 | 608 | 40.7 | 32 |
| ir_separate_split_watson | R_interp | 0.125 | 1000 | 0.080 | 79.8 | 0 | 0.00 | 1.000 | 0 | 0.0 | 0 |
| ir_nested_watson | R_E | 0.250 | 1000 | 0.201 | 201.2 | 72 | 0.36 | 1.000 | 250 | 62.5 | 72 |
| ir_priority_watson | R_E | 0.250 | 1000 | 0.201 | 201.2 | 72 | 0.36 | 1.000 | 250 | 62.5 | 72 |
| ir_nested_gp_mle | R_E | 0.250 | 1000 | 0.201 | 201.2 | 72 | 0.36 | 1.000 | 250 | 62.5 | 72 |
| ir_nested_gp_design | R_E | 0.250 | 1000 | 0.201 | 201.2 | 0 | 0.00 | 1.000 | 0 | 0.0 | 0 |
| ir_nested_gp_nonstationary | R_E | 0.250 | 1000 | 0.201 | 201.2 | 33 | 0.16 | 1.000 | 259 | 64.1 | 33 |
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
| ir_tight_sibson | R_E | 0.250 | 1000 | 0.201 | 201.2 | 211 | 1.05 | 0.230 | 1000 | 201.2 | 211 |
| ir_tight_gp_mle | R_E | 0.250 | 1000 | 0.201 | 201.2 | 201 | 1.00 | 0.519 | 1000 | 201.2 | 201 |
| ir_tight_gp_design | R_E | 0.250 | 1000 | 0.201 | 201.2 | 190 | 0.94 | 0.823 | 1000 | 201.2 | 190 |
| ir_tight_gp_nonstationary | R_E | 0.250 | 1000 | 0.201 | 201.2 | 187 | 0.93 | 0.878 | 1000 | 201.2 | 187 |
| ir_tight_interp_sibson | R_E | 0.250 | 1000 | 0.201 | 201.2 | 189 | 0.94 | 0.843 | 1000 | 201.2 | 189 |
| ir_tight_interp_gp_mle | R_E | 0.250 | 1000 | 0.201 | 201.2 | 182 | 0.90 | 0.942 | 1000 | 201.2 | 182 |
| ir_tight_interp_gp_design | R_E | 0.250 | 1000 | 0.201 | 201.2 | 198 | 0.98 | 0.613 | 1000 | 201.2 | 198 |
| ir_tight_interp_gp_nonstationary | R_E | 0.250 | 1000 | 0.201 | 201.2 | 189 | 0.94 | 0.843 | 1000 | 201.2 | 189 |
| ir_separate_random | R_E | 0.250 | 1000 | 0.160 | 159.6 | 9 | 0.06 | 1.000 | 1000 | 159.6 | 9 |
| ir_separate_random | R_interest | 0.125 | 1000 | 0.080 | 79.8 | 77 | 0.97 | 0.646 | 1000 | 79.8 | 77 |
| ir_separate_random | R_interp | 0.125 | 1000 | 0.080 | 79.8 | 0 | 0.00 | 1.000 | 0 | 0.0 | 0 |
| ir_nested_random | R_E | 0.250 | 1000 | 0.201 | 201.2 | 194 | 0.96 | 0.727 | 1000 | 201.2 | 194 |
| ir_priority_random | R_E | 0.250 | 1000 | 0.201 | 201.2 | 197 | 0.98 | 0.643 | 1000 | 201.2 | 197 |
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
| ir_tight_random | R_E | 0.250 | 1000 | 0.201 | 201.2 | 164 | 0.82 | 0.999 | 1000 | 201.2 | 164 |
