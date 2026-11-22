# SI 4. Software: adding a form of guarantee (draft 1)



## SI 4.1 Contract for a form of guarantee

A form of guarantee is a budget policy in the `accountable` package. It implements `decide(LevelData) -> PolicyDecision` and registers a name with `@register("name")`. The forms in the main text are the policies `separate` (per-claim budgets), `nested_path` (quantile path) and `priority_path` (priority path); `ltt_conditional` gives the conditional rate of Appendix C.

A policy keeps three conditions.

1. **Inputs.** It uses the frozen scores of every site of the level, the indices of the calibration sites and the bad labels of those sites only. Scores are frozen before the draw and are not refitted by the policy.
2. **Fixed family.** Every family of thresholds it searches (a path, a grid, a split of the budget) is built from scores, settings or earlier levels, and from no calibration label of the current level.
3. **Stated guarantee.** It returns its guarantees as `Guarantee(event, budget, confidence)`, with `event` equal to `R_E` or `R_<claim>`, or an empty list. Campaign records show an empty list as "no guarantee".

Condition 2 carries the proof of Appendix B. The sequential rule of Section 5.1 violates it.

The campaign loop enforces the order of operations of Section 3.1 structurally: a score receives only the measured set (`MeasuredSet`) when it is fitted and is frozen with `bind_level` before the draw; the calibration indices come from a generator that nothing else uses; and a policy receives the labels of the calibration sites only. A policy or score written against these interfaces cannot see the labels of the level it is deciding before the draw.

## SI 4.2 Acceptance check

Before a policy carries a claim, each guarantee it states is checked by Monte Carlo on fixed finite populations (`accountable.validate.check_coverage`). The population is fixed, so the calibration draw is the only randomness. For each stated guarantee, the check counts the draws in which the population rate exceeds the budget and compares that frequency with $1 - \text{confidence}$, allowing three Monte Carlo standard errors. Scores are drawn uniform on $[0, 1]$; labels are independent of the scores (uninformative, the hard case) or have a bad probability rising linearly with the score at the same mean (informative).

**Table S4.1.** Acceptance check on a population of 271 sites, $m = 40$, 2000 draws; interest and interpolation labels at mean rates 0.30 and 0.35. Entries are the fraction of draws in which the stated rate exceeded its budget.

| Policy | Stated guarantee | Allowed | Uninformative | Informative |
| --- | --- | --- | --- | --- |
| Per-claim budgets | $R_{\mathrm{interest}} \le 0.10$ | 0.10 | 0.039 | 0.047 |
| | $R_{\mathrm{interp}} \le 0.10$ | 0.10 | 0.036 | 0.027 |
| | $R_E \le 0.20$ | 0.20 | 0.010 | 0.004 |
| Quantile path | $R_E \le 0.10$ | 0.10 | 0.047 | 0.045 |
| Priority path, interest first | $R_E \le 0.10$ | 0.10 | 0.039 | 0.047 |
| Priority path, interpolation first | $R_E \le 0.10$ | 0.10 | 0.036 | 0.027 |
| Plug-in rule (counterexample) | $R_{\mathrm{interp}} \le 0.10$ | 0.10 | 0.554 | 0.515 |

The plug-in rule takes the largest threshold whose empirical calibration rate stays within the budget, with no order-statistic correction, and states a guarantee at confidence 0.90. The check rejects it. Passing the check is evidence for a policy; the finite-sample argument still has to be written down, as in Appendix B.

## SI 4.3 Worked example: the priority path

The priority path subclasses the quantile path and replaces only the entry times: claim $i$ in the order sweeps its own score quantiles over $\lambda \in (i, i + 1]$ (Appendix B.2). The order is a setting, so the family is fixed before the draw and Proposition B.2 applies without change. The implementation is about thirty lines. Unit tests check that the priority path with one claim gives the same covers as the single-claim rule, and that both orders pass the acceptance check.

## SI 4.4 Software, tests and reproduction

**Functionality.** The workflow is a Python package with four parts: (i) the campaign loop, which runs the five steps of Section 3.1 on any dataset that supplies design sites, levels and an oracle for the measurement at a site; (ii) the forms of guarantee of Section 3.4 as budget policies, with exact hypergeometric and binomial tails; (iii) predictors and scores, natural-neighbour interpolation with mirror images at boundaries and Gaussian-process interpolation under three length-scale rules; (iv) the record, which writes every site's level, scores, action and reason and every level's calibration draw, thresholds and picked failure probability, together with the random state, so that each campaign can be replayed and every bound recomputed.

**Tests.** The test suite checks the geometry of the natural-neighbour weights, the Gaussian-process engine, the acceptance check of Table S4.1 for every policy, the coverage of every stated guarantee by Monte Carlo on fixed populations (including that the sequential rule exceeds its nominal rate), and that recorded campaigns replay to identical decisions. The implementation refuses a binomial allowance $k$ larger than the hypergeometric one; no such case arose in this study.

**Reproduction.** Each figure and table of the main text and of this supplement is produced by a script that reads only the run record; the record is produced by re-running the configurations of Table S4.2 with random states 0 to 249. A campaign takes 3 to 12 s on one core.

**Table S4.2.** Configuration names in the record and the protocols of the main text.

| Name element | Meaning |
| --- | --- |
| `ir`, `ir_tight`, `nacl_fwhm`, `syn_env`, `syn_peak_2cert` | IR map at the original and the tight tolerance; NaCl scan, width claim; synthetic map, full-profile claim alone (main text); synthetic map, peak and interest claims (variant of SI 6.2) |
| `separate`, `nested`, `priority` | per-claim budgets, quantile path, priority path (Section 3.4) |
| `watson`, `sibson` | natural-neighbour (Sibson) interpolation with the logistic score; `watson` names the construction of the weights |
| `gp_mle`, `gp_design`, `gp_nonstationary` | Gaussian-process interpolation, length scale by maximum likelihood, by design spacing, by local spacing |
| `random` | random scores for every claim |
| `legacy_sequential` | the sequential rule of the original IR analysis (Appendix B.3) |
