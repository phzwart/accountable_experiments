# SI 4. Software: adding a form of guarantee (draft 1)

*The rest of SI 4 (functionality, tests, reproduction procedure) is still to be drafted. Code and module names belong here and stay out of the main text.*

## SI 4.x Contract for a form of guarantee

A form of guarantee is a budget policy in the `accountable` package. It implements `decide(LevelData) -> PolicyDecision` and registers a name with `@register("name")`. The forms in the main text are the policies `separate` (per-claim budgets), `nested_path` (quantile path) and `priority_path` (priority path); `ltt_conditional` gives the conditional rate of Appendix C.

A policy keeps three conditions.

1. **Inputs.** It uses the frozen scores of every site of the level, the indices of the calibration sites and the bad labels of those sites only. Scores are frozen before the draw and are not refitted by the policy.
2. **Fixed family.** Every family of thresholds it searches (a path, a grid, a split of the budget) is built from scores, settings or earlier levels, and from no calibration label of the current level.
3. **Stated guarantee.** It returns its guarantees as `Guarantee(event, budget, confidence)`, with `event` equal to `R_E` or `R_<certificate>`, or an empty list. Campaign records show an empty list as "no guarantee".

Condition 2 carries the proof of Appendix B. The sequential rule of Section 5.2 violates it.

## SI 4.y Acceptance check

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

## SI 4.z Worked example: the priority path

The priority path subclasses the quantile path and replaces only the entry times: certificate $i$ in the order sweeps its own score quantiles over $\lambda \in (i, i + 1]$ (Appendix B.2). The order is a setting, so the family is fixed before the draw and Proposition B.2 applies without change. The implementation is about thirty lines. Unit tests check that the priority path with one certificate gives the same covers as the single-certificate rule, and that both orders pass the acceptance check.
