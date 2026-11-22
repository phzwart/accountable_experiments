# SI 10. Checks beyond the level

The studies below extend the run record of SI 5 in four directions: a bound on the sites of interest lost, drift during a campaign, an audit of the finished map, and the cost of a contract against its calibration size and confidence. Every study uses the quantile path with natural-neighbour interpolation and the budgets of Table 4 unless stated otherwise.

## SI 10.1 A label-conditional bound for the sites of interest

**Rule.** The study uses the two-claim variant of the synthetic map (SI 6.2), where a third of the sites are of interest. On each level the shared budget is kept at 0.20 with confidence 0.80. In addition, the share of the level's sites of interest skipped under the no-interest claim is bounded by 0.20 with confidence 0.80. Given their number $m_Z$, the calibration sites of interest are a uniform sample without replacement from the $N_Z$ sites of interest of the level. $N_Z$ is unknown, but it lies between $m_Z$ and $N_L - (m - m_Z)$. The allowed number $k_Z$ of calibration sites of interest that the no-interest claim may cover is the largest $k$ for which

$$
\max_{N_Z} P\big(H_{N_Z,\ \lfloor 0.20 N_Z \rfloor + 1,\ m_Z} \le k\big) \le 0.20
$$

and the no-interest claim covers only sites whose entry time on the path lies below the $(k_Z + 1)$-th smallest entry time among the calibration sites of interest. With 12 to 20 such sites per level, $k_Z$ was 0, 1 or 2. Restricting the cover of one claim keeps the shared-event bound, which holds for any subset of the cover it certifies.

**Result.** Over 250 campaigns (Table S10.1), the plan lost 8.5 ± 4.4 % of the sites of interest on certified levels under the no-interest claim, against 34.7 ± 8.5 % without the conditional bound, and measured 359 ± 26 sites against 334 ± 26. Of 1500 level checks, 4.9 % exceeded the share of 0.20 that the conditional bound allows to fail at 20 %; without the conditional bound, 58.7 % did. The shared budget was exceeded on 2 of 1500 level checks, against 11.3 % expected under the picked failure probabilities: the restricted cover leaves the shared rate well below its budget.

On the NaCl scan, where about two thirds of the sites hold the line, the same rule over 250 campaigns lost 8.1 ± 3.0 % of the sites of interest, against 9.2 ± 3.2 % without it, at 630 ± 59 measurements against 614 ± 56; 1.4 % of level checks exceeded the share, against 2.2 % without the statement. Where signal is common, the shared budget already spares it, and the conditional bound changes little and costs little.

**Table S10.1.** Sites of interest lost under the no-interest claim on the synthetic map, per certified level (mean over 250 campaigns).

| Level | 3 | 4 | 5 | 6 | 7 | 8 |
| --- | --- | --- | --- | --- | --- | --- |
| Shared budget only | 0.0 % | 12.0 % | 25.1 % | 32.6 % | 35.4 % | 38.9 % |
| With the label-conditional bound | 0.0 % | 5.0 % | 6.8 % | 7.6 % | 9.3 % | 9.1 % |

## SI 10.2 Drift during a campaign

**Model.** The synthetic sample swells slowly while it is measured: a measurement at clock $t$, the number of sites measured before it, returns the profile of the sample as it was when the plan was declared, with $q$ scaled by $1 + s\,t/932$, so that every feature moves to lower $q$. Here 932 is the mean cost of the plan in the record, and $s$ takes the values 0, 0.05, 0.10 and 0.20. Claim and budget are those of the main text: the full profile within 0.5 % + 0.005 on average, $R_E \le 0.10$ at confidence 0.80 per level. Calibration labels compare the prediction with the drifted measurement, as a live campaign would; every rate is counted against the sample at the start. After each level, five seed sites fixed in advance are measured again and compared, under the claim's metric, with their first measurement; a failure flags the level. Re-measurement is not charged to the clock. At $s = 0$ the campaigns reproduce the record site for site. Fifty campaigns were run per value.

**Result.** Under the profile claim the bound broke (Table S10.2). At $s = 0.05$ and $0.10$ the levels exceeded their budget in 24 % of checks, against 9.5 % expected under the picked failure probabilities, although drifted calibration sites disagree with earlier predictions and the rule skipped less: the plan measured 1687 ± 76 and 1806 ± 51 sites against 966 ± 247 without drift. At $s = 0.20$ it measured almost every site, and the few skips met the budget. Most of the damage lay in the measured sites: 88 % to 96 % of the sites measured on certified levels returned a profile outside tolerance of the sample at the start, and those sites carry no claim. The repeated seed sites flagged no level without drift and flagged every drifted campaign, from the fourth level on at $s = 0.05$ and from the third at the larger values. The synthetic profiles carry no noise, so any failure of a repeated site signals drift; with noise, the threshold for a flag comes from repeated measurements, as for the NaCl scan in SI 2. The two-claim variant of the synthetic map (SI 6.2), with its peak-position tolerance of 0.005 Å⁻¹, absorbed a stretch of 5 % and kept its bound at every stretch, while 21 % to 79 % of its measurements went outside tolerance at stretches of 10 % and 20 %; the archive of SI 5 keeps those runs.

**Table S10.2.** Drift on the synthetic map, 50 campaigns per value of $s$. Level checks over budget, against 9.5 % expected under the picked failure probabilities; measured sites outside tolerance of the sample at the start, as a share of the measured sites of certified levels; campaigns with at least one flagged level.

| $s$ | Sites measured | Level checks over budget | Measured sites off the sample | Campaigns flagged |
| --- | --- | --- | --- | --- |
| 0.00 | 966 ± 247 | 9.7 % | 0 % | 0 % |
| 0.05 | 1687 ± 76 | 23.7 % | 88 % | 100 % |
| 0.10 | 1806 ± 51 | 23.7 % | 93 % | 100 % |
| 0.20 | 1908 ± 45 | 4.0 % | 96 % | 100 % |

**Correction.** A drift detected in this way can be modelled from the repeated sites and removed from the measurements, or the calibration sites can be weighted by their age, which keeps a bound with a coverage loss that grows with the shift [Barber2023]; when the shift is known, as for covariate shift, likelihood-ratio weights restore exact coverage [Tibshirani2019]. Neither was simulated here.

## SI 10.3 The audit of the finished map

**Protocol.** After the last level, $n_a$ sites are drawn uniformly without replacement from the skipped sites of the certified levels, measured and kept out of the map. The map predicts every skipped site from all other measured sites with the protocol's predictor, as for the final maps of SI 5.3. With $N$ skipped sites, of which $K$ lie outside tolerance, and $f$ failing audit sites, the bound on $K$ is the exact hypergeometric limit of SI 9,

$$
u(f) = \max \{ K' : P(H_{N, K', n_a} \le f) > 1 - c \}
$$

reported as a share $u(f)/N_c$ of the $N_c$ sites of the certified levels. Coverage was estimated over the 250 campaigns of the record, with 200 audit draws per campaign on the IR and NaCl maps and 50 on the synthetic map. On the synthetic map the audit was also stratified by the claim of the skip, 50 sites under the no-interest claim and 50 under the interpolation claim alone, each stratum bounded at $1 - (1 - c)/2$ and the bounds summed. Within the no-interest stratum, 100 audit sites bound the number $K_Z$ of sites of interest skipped there; with $M_Z$ sites of interest measured on certified levels, the share of the sites of interest lost is at most $u_Z/(M_Z + u_Z)$, because that share grows with $K_Z$ and the sites of interest number at least $M_Z + K_Z$.

**Table S10.3.** Audit of the final maps of the record: true share of certified-level sites the final map predicts outside tolerance (mean over 250 campaigns), mean audit bound and coverage over the audit draws (250 × 200; synthetic 250 × 50).

| Map | True share | $n_a$ | Bound at 0.80 | Coverage at 0.80 | Bound at 0.95 | Coverage at 0.95 |
| --- | --- | --- | --- | --- | --- | --- |
| IR map | 0.4 % | 50 | 2.7 % | 100.0 % | 4.8 % | 100.0 % |
|  |  | 100 | 1.5 % | 100.0 % | 2.6 % | 100.0 % |
|  |  | 200 | 0.9 % | 95.5 % | 1.5 % | 100.0 % |
| NaCl scan | 18.0 % | 50 | 20.9 % | 84.1 % | 23.4 % | 96.4 % |
|  |  | 100 | 19.8 % | 83.0 % | 21.5 % | 96.1 % |
|  |  | 200 | 19.0 % | 82.5 % | 20.0 % | 96.0 % |
| Synthetic map | 8.4 % | 50 | 12.7 % | 86.7 % | 16.5 % | 97.6 % |
|  |  | 100 | 11.1 % | 85.4 % | 13.6 % | 96.8 % |
|  |  | 200 | 10.1 % | 84.1 % | 11.7 % | 96.5 % |

On the synthetic map the stratified audit of 100 sites bounded the share at 14.6 % at 0.80 (coverage 96.1 %) and 17.8 % at 0.95 (coverage 99.5 %). From 100 sites of the no-interest stratum, the share of the sites of interest lost under the no-interest claim, 34.7 % on average, was bounded at 66.6 % at 0.80 (coverage 100.0 %) and 69.9 % at 0.95 (coverage 100.0 %), a statement that needs no change to the campaign but is loose: the measured sites of interest are few, and the label-conditional rule of SI 10.1 bounds the same share at 0.20. Stratification cost more than it gained here, because each stratum carries half the confidence.

**A Gaussian-process acquisition campaign.** On the NaCl scan a campaign was steered by the process of SI 7: presence and log width each modelled by a Gaussian process with RBF and white-noise kernel, maximum likelihood, from the seed sites on. In batches of 25, it measured the unmeasured sites with the largest posterior probability that skipping them would be wrong, the probability being the presence probability for a predicted absent line and one minus the probability of presence within tolerance otherwise (SI 7), with the predictive standard deviation. At 614, 694 and 800 sites measured, the map predicted every other site, and 100 audit sites drawn uniformly from the unmeasured sites bounded its errors at confidence 0.80; the campaign is deterministic, so coverage is over 2000 audit draws (Table S10.4).

**Table S10.4.** Gaussian-process acquisition campaign on the NaCl scan: share of the 995 certified-level sites the map gets wrong, the process's own stated share with predictive and latent standard deviation, and the audit bound from 100 sites at confidence 0.80 (mean, 10 % and 90 % quantiles over 2000 draws, coverage).

| Sites measured | True share | Stated, predictive | Stated, latent | Audit bound (10–90 %) | Coverage |
| --- | --- | --- | --- | --- | --- |
| 614 | 9.0 % | 11.2 % | 3.9 % | 10.6 % (8.4–12.8 %) | 80.5 % |
| 694 | 6.1 % | 7.2 % | 3.3 % | 7.3 % (5.6–8.8 %) | 80.2 % |
| 800 | 1.6 % | 2.2 % | 2.1 % | 2.2 % (1.6–2.8 %) | 91.0 % |

At the cost of the certified plan, the acquisition campaign left fewer wrong sites than the certified plan's final map, 9.0 % against 18.0 %, with a different predictor and no stated bound. Its own statement held with the predictive standard deviation and was 2.3 times too low with the latent one, and nothing within the campaign told the two apart; the audit did, at a cost of 100 measurements.

**A Gaussian-process campaign told to meet a budget.** The same campaign was run 30 times with a stopping rule: after every batch the process stated its share of certified-level sites predicted wrongly, the sum of its per-site probabilities of a wrong skip, and stopped once the statement reached 0.20. Each batch was chosen among a random 80 % of the unmeasured sites, so runs differ; acquisition used the predictive probability, and the stopping point of the latent rule was read off the same trajectories. With the predictive standard deviation the runs stopped after 451 to 501 measurements (mean 467) at 14.6 ± 0.6 %, all within the budget. An audit of 100 unmeasured sites at confidence 0.80, taken at the stopping point, bounded the share at or below 0.20 in 89 % of draws. With the latent standard deviation, which leaves out the noise of a single measurement, the statement was 11.6 % before any site beyond the seed was measured, so every run would have stopped at the 76 seed sites, with 36.8 % of the certified-level sites predicted wrongly. For comparison, the plans certified level by level measured 614 ± 56 sites; their wrong skips, the quantity they bound, exceeded 20 % of the certified-level sites in 1.2 % of campaigns, and their final maps, which carry no statement, in 30 %.

## SI 10.4 Cost against calibration size and confidence

**Table S10.5.** Plans certified level by level on the IR map at $\varepsilon = 0.10$, 100 campaigns per setting: allowed numbers $k$ of failing calibration sites, sites measured of 959, and level checks over budget against the share expected under the picked failure probabilities.

| $m$ | Confidence | $k$ | Sites measured | Level checks over budget | Expected |
| --- | --- | --- | --- | --- | --- |
| 20 | 0.80 | 0 | 340 ± 90 | 0.8 % | 9.2 % |
| 20 | 0.90 | none, 0 | 851 ± 30 | 0.8 % | 3.7 % |
| 20 | 0.95 | none | 959 ± 0 | 0.0 % | 0.0 % |
| 40 | 0.80 | 1, 2 | 337 ± 63 | 0.5 % | 11.7 % |
| 40 | 0.90 | 1, 2 | 359 ± 65 | 0.5 % | 5.8 % |
| 40 | 0.95 | 0, 1 | 430 ± 78 | 0.0 % | 1.8 % |
| 80 | 0.80 | 5, 6, 7 | 393 ± 22 | 0.0 % | 10.0 % |
| 80 | 0.90 | 4, 5, 7 | 408 ± 36 | 0.0 % | 4.1 % |
| 80 | 0.95 | 3, 4, 7 | 436 ± 46 | 0.0 % | 2.1 % |

At $m = 20$ the smallest budget the draw can certify, $1 - \delta^{1/m}$ in the binomial approximation, is 0.08 at confidence 0.80 and exceeds 0.10 at 0.90 and 0.95, so most levels at 0.90 and all at 0.95 have no threshold ("none") and are measured in full. At $m = 80$ every threshold exists, and the calibration sample itself, 320 sites over four certified levels, sets most of the cost on a map of 959 sites. On the IR map few calibration failures occur, so the exceedances lie far below the expected share at every setting.
