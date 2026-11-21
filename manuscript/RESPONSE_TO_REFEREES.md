# Response to the referees (mock panel, round 1)

All three referees recommended major revision. They agreed that the argument is correct and the validation honest, and asked for (i) a like-for-like comparison with Gaussian-process uncertainty, (ii) a campaign-level statement, (iii) a precise account of what is certified, and (iv) stronger baselines and a finished supplement. Changes are listed by issue; section, figure and table numbers refer to the revised manuscript.

## Shared issues

**1. The comparison with Gaussian-process uncertainty was not like-for-like (R1 M6, R2 M1, R3 M4).**
The rule now records its own probability that each skip is wrong, so its statement and its realised share are on the denominator of the guarantee (share of the certified-level sites). Fig. 1 shows the certified plan beside the latent and the predictive variant of the same process:

| NaCl scan | stated | realised | measured |
|---|---|---|---|
| certified plan | bound 20 % per level | 12.3 % (mean of 250) | 614 |
| GP, latent s.d., 68 % | 3.5 % | 10.4 % | 658 |
| GP, latent s.d., 90–99 % | 0.4–0.5 % | 1.0–1.4 % | 893–903 |
| GP, predictive s.d. | 0.4 % | 0.3 % | 922 |

With the predictive standard deviation the statement was right; with the latent one it was three times too low, and on the synthetic map even the predictive one was about ten times too low (Fig. 4). The message is now that a model's own rate can be right or wrong and nothing in a run shows which (Section 5.2, abstract). The former headline on 21–31 predictable skips is gone. The Gaussian process with an acquisition function refitted point by point (R2) is left to the follow-up work; the Discussion now states that certification can sit over any campaign whose proposals for a level are frozen before the draw.

**2. Campaign-level confidence (R1 M1, R2 M6, R3 M2).**
The contract now certifies the plan as a whole: its goal on every level holds with confidence c, the failure probability being divided among the levels when the plan is declared (Section 3.1, 3.3; Appendix A). New runs (Section 5.1; SI 5.3, Table S5.4):

| | per level: measured / campaigns over budget | plan as a whole: measured / campaigns over budget |
|---|---|---|
| IR, c = 0.75 | 295 / 19.6 % | 408 / 0 of 105 |
| NaCl, c = 0.80 | 614 / 38.4 % | 694 / 11 of 128 |
| synthetic, c = 0.80 | 334 / 49.6 % | 376 / 10 of 60 |

The cost of a campaign-level contract is 12 % to 38 % more measurements. On the synthetic map 10 of 360 level checks exceeded the budget against 5.5 expected (p ≈ 0.05); an attainment audit with 3000 draws on 20 recorded levels gave 1.01 times the picked failure probability. The union bound counts only levels on which the budget can be reached (R1's joint IR figure of 0.24 is therefore about 0.81).

**3. "Certifies every action" overclaimed (R1 M2, R3 M1).**
An action is now defined as the decision on one level of the plan, taken once after the draw for all of its sites; its certificate is the level bound, as a lot is accepted on a sample. The plan is certified to reach the goal of the contract, and the record shows that it was followed (Section 3.1). Each site carries a reason, not a bound (Section 3.5, Conclusion). "Needed" is used only in its hindsight sense (Section 5.3).

## Referee 1

- **Acceptance sampling and missing literature.** Added: Dodge and Romig (consumer's-risk sampling plan), Geifman and El-Yaniv (selective classification with guaranteed risk), Lindeman and Stark (risk-limiting audits), Särndal et al. (model-assisted sampling), Vovk (transductive conformal), Wieczorek (design-based conformal), Zrnic and Candès (active inference) (Section 2).
- **Conformal risk control as a baseline (M6d).** Run on the same draw: it measured 260, 541 and 301 sites, but its levels exceeded the budget in 5 %, 34 % and 33 % of checks and its campaigns in 20 %, 80 % and 93 % (Section 5.1).
- **Validation verifies an identity (M5).** Agreed in part: against a fixed truth the counts check the rule and its implementation. Section 5.1 now says so, and the Discussion names the conditions a retrospective study cannot break (drift within a level, measurement that disturbs neighbours) and proposes re-measuring seed sites within each level as a check in the record. Perturbation studies are left to future work.
- **Binomial versus hypergeometric k (M4).** The implementation refuses a binomial k above the hypergeometric one; a numerical check over N = 41–1300, ε = 0.05–0.30, δ = 0.05–0.25 at m = 40 found no exception (Appendix A; SI 4.4).
- **Sequential-rule and order-of-operations experiments (M3c, M3d).** Both are on simulated 399-site levels (uninformative and informative scores); 0.288 is now compared with the picked 0.206, and the score manipulation is described exactly (Section 5.1; Appendix B.3; SI 5.2).
- **Adaptive plans (M3b).** A plan drawn up level by level is a declared rule; Appendix A states that δ_L is then fixed before each draw and the union bound runs over the levels produced.
- **Confound between predictor and score (M6e).** Noted; "protocol" in Section 4.3 names predictor and score together.
- **Clopper–Pearson map bound, inverse-probability-weighted calibration.** The map bound moved to SI 9; weighting measured sites into calibration through known inclusion probabilities is named as a route in Section 2 and left to the follow-up.

## Referee 2

- **Uniform subsampling and practicality.** At equal cost, the final maps of the certified plans left 0.4 %, 16.6 % and 8.5 % of the certified-level sites outside tolerance, against 0.5 %, 21.9 % and 10.3 % for uniform subsampling (Section 5.4; SI 5.3). The order of measurement within an action is free, so the remaining sites can follow the shortest path (Discussion). A beam-time model with move, settle and reduction times needs instrument numbers and is left to the deployment study.
- **NaCl tolerance against noise (M3).** Section 3.5 and the Discussion state that labels compare with one noisy measurement and that on NaCl the width scatter is about the tolerance; a tolerance is best set against repeated measurements.
- **Inconsistencies.** Informative/uninformative scores and the comparator of the sequential rule fixed; SI section references updated; Fig. 5 shows the average-cost campaigns of SI 8 with consistent colours and an upright IR axis.

## Referee 3

- **Scope.** Section 3.5 lists what a guarantee covers: per level and per plan; share of the level against share of skips; count, not place; design sites only; one measurement as truth.
- **Readability.** Worked example in Section 3.3 (N = 399, m = 40, ε = 0.10 → k = 2, δ_L = 0.206); "certificate" replaced by "claim" throughout, including appendices and SI.
- **Reproducibility.** SI 4.4 describes the software, tests and reproduction, with a key from configuration names to protocols (Table S4.2); SI 2 gives every parameter of the synthetic forward model (Table S2.1).
- **Accountability framing (M1).** The governance citations remain in one paragraph of the Introduction; the record's properties are stated in the Discussion (deterministic replay, decisions logged before measurement). Tamper-evident records are not claimed.

## Still open

- Corresponding-author e-mail and the Zenodo DOI are placeholders.
- No live or time-replayed campaign, drift perturbation, or acquisition-driven GP baseline; these belong to the deployment and follow-up studies.
- Fig. 4 still pairs the certified bound with a mean; the caption says so.
