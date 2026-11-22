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
The plan is now certified for all levels together: it keeps the budget on every level with confidence c, the failure probability being divided among the levels when the plan is declared (Section 3.1, 3.3; Appendix A). New runs (Section 5.1; SI 5.3, Table S5.4):

| | per level: measured / campaigns over budget | all levels together: measured / campaigns over budget |
|---|---|---|
| IR, c = 0.75 | 295 / 19.6 % | 408 / 0 of 105 |
| NaCl, c = 0.80 | 614 / 38.4 % | 694 / 11 of 128 |
| synthetic, c = 0.80 | 334 / 49.6 % | 376 / 10 of 60 |

The cost of a campaign-level contract is 12 % to 38 % more measurements. On the synthetic map 10 of 360 level checks exceeded the budget against 5.5 expected (p ≈ 0.05); an attainment audit with 3000 draws on 20 recorded levels gave 1.01 times the picked failure probability. [Withdrawn in round 2: the claim that the union bound may count only levels on which the budget can be reached needs the full truth; see round 2.]

**3. "Certifies every action" overclaimed (R1 M2, R3 M1).**
An action is now defined as the decision on one level of the plan, taken once after the draw for all of its sites; its certificate is the level bound, as a lot is accepted on a sample. The plan is certified to keep the budget of the contract, and the record shows that it was followed (Section 3.1). Each site carries a reason, not a bound (Section 3.5, Conclusion). "Needed" is used only in its hindsight sense (Section 5.3). [Round 2: this was not yet true of the abstract, Discussion and Conclusion; corrected.]

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

- **A uniform sample of the same size, and practicality.** At equal cost, the final maps of the certified plans left 0.4 %, 16.6 % and 8.5 % of the certified-level sites outside tolerance, against 0.5 %, 21.9 % and 10.3 % for a uniform sample of the same size (Section 5.4; SI 5.3). The order of measurement within an action is free, so the remaining sites can follow the shortest path (Discussion). A beam-time model with move, settle and reduction times needs instrument numbers and is left to the deployment study. [Round 2: superseded by the 250-campaign values below.]
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


---

# Response to the referees, round 2

All three referees recommended minor revision. The required changes were consistency of the central vocabulary and claims, one statement that needed the full truth, SI 7, and the completeness of the new runs. Two statements of our round-1 response were wrong and are corrected above: "needed when the decision was made" had survived in the abstract, Discussion and Conclusion, and the joint IR confidence of 0.81 relied on knowing which levels can reach their budget.

## Shared points

- **"Needed" and "action" (R1 N4, R2 new 1, R3 M1/M5).** The abstract, Discussion and Conclusion now use "action" only for the decision on a level; a measured site carries its reason, and "needed" appears only in the hindsight sense of Section 5.3.
- **The message on model uncertainty (R1 N3, R2 M1, R3).** Section 5.2 is retitled "A model's own error rate is checked only against the full scan"; the Conclusion says the rate was "sometimes right and sometimes several times too low". Section 5.2 states that the predictive process was right while making no predictable skips (922 of 1071 measured), and that the certified Gaussian process measured about 150 fewer sites than it (745–777). The Fig. 1 title now reads "only the certified plan bounds its rate before any skip", and the caption gives the share of per-level campaigns over budget on some level (38 %).
- **Joint confidence (R1 N1, R2 new 2, R3 N1).** Section 3.3 and Appendix A sum over every certified level; Appendix A states that which levels can reach their budget is known only from the full truth, so a campaign claims the confidence its plan declares. A plan drawn up level by level fixes in advance how the failure probability is spent (Appendix A).
- **Completed runs (R1 N2, R2 6, R3 N2).** The partial runs of round 1 are kept unchanged in the repository as a record (stopped by hand for compute time, in seed order, independent of outcomes). All new configurations now have 250 campaigns: plans certified for all levels together measured 415 ± 82, 694 ± 58 and 377 ± 27 sites (41 %, 13 % and 13 % more than per level) and exceeded the budget on some level in 1, 24 and 20 of 250 campaigns, against the 25 %, 20 % and 20 % allowed. Their 1, 27 and 20 level checks over budget match the 30, 28 and 23 expected under the picked failure probabilities; the synthetic excess of the partial run (10 of 360 against 5.5) was chance, as the attainment audit (1.01) indicated. The abstract now reads "at least 90 %" and "13 % to 41 %".
- **SI 7 (R1 M6, R2 M1).** Rewritten to match Section 5.2: the stated probability of a wrong skip is defined (presence probability clipped to [0, 1]; log-normal width with latent or predictive standard deviation), Table S7.1 gives stated and realised shares, the uncertified rule is described as a skip rule on the fixed design, and the principal-component posterior of S7.2 is named as one construction among several.

## Referee 1

- **CRC (M6d).** Run to 250 campaigns on all three maps (260, 542 and 305 sites measured). Its mean share of a level skipped wrongly, 5.7 %, 18.8 % and 18.3 %, stays below ε as its guarantee promises, while single levels exceeded the budget in 4.9 %, 34.7 % and 31.6 % of checks and campaigns on some level in 19.6 %, 80.8 % and 91.6 % (Section 5.1, Table S5.4).
- **No drift, adaptive plans (M3a, M3b).** (A6) is now "Fixed truth": the measurement a site would return depends neither on which sites are drawn nor on order or time; drift and damage break it (Appendix A.1, A.3). Plans drawn up level by level need a spending schedule fixed in advance (Appendix A.2).
- **Refitting bullet (M3d).** Appendix A.3 now names the manipulation exactly.
- **Binomial p-values (M4).** Appendix C states that only the hypergeometric p-value carries the guarantee and that no result of Section 5 rests on the conditional rate.
- **Map bound (M4).** SI 9 now uses the exact hypergeometric upper limit; recomputed over the 250 campaigns of each main configuration it held on 95.8 %, 84.4 % and 89.5 % of certified levels against confidences 0.75, 0.80 and 0.80, with tighter limits than Clopper–Pearson.
- **Leftover "certificate", "picked failure probability" (minor).** Replaced in Appendix A.2; defined in Section 3.3.

## Referee 2

- **Noise against tolerance (M3).** Adding the estimated window noise twice, independently, to every NaCl profile, the second copy fails the width claim against the first at 1.1 % ± 0.3 % of sites (SI 2.2). The scatter that makes about half of all predictions fail therefore lies above the counting noise, in the sample or in variation the counting noise leaves out, such as grain statistics; the Discussion says so and that repeated measurements would set the tolerance.
- **Practicality (M4, M5).** The Discussion states that costs are counted in sites, that each level adds a second pass at an instrument (calibration measured and reduced before the rest is decided), that a fast raster may compete, and that the record can tell chance from drift once seed sites are re-measured within each level.
- **GP score (M1).** Section 5.4 states that the GP score depends on positions and length scale only, which is why the GP protocols measured as many sites as random scores on the synthetic map. The abstract now reads "The model and its scores set only the cost".
- **Uniform sample.** Run to 250 campaigns: a uniform sample of the same size left 0.5 ± 0.2 %, 22.0 ± 1.0 % and 10.6 ± 1.0 % of certified-level sites outside tolerance; the final maps of the certified plans left 0.4 ± 0.3 %, 18.0 ± 3.8 % and 8.4 ± 1.4 % (Section 5.4, Table S5.4).

## Referee 3

- **Kernel and calibration.** A new Discussion paragraph answers the expected objection that a better kernel would make the process honest: whether it did can be checked only on sites the model did not choose, drawn uniformly before the decision, and that sample is the calibration step of the plan.
- **"Plan".** The plan is the design sites; the plan together with its rule is what is certified (Section 3.1).
- **"Seed".** "Seed" now means the coarse levels only; the random-number state is "random state" in the main text and SI.
- **Cost against m and δ (M3, recommended).** Not added; the cost against the budget is in Table S7.3 and against the confidence in Table S5.4.



---

# Changes since round 2 (for the referees)

These changes extend the paper beyond the round-2 requests; they answer points the referees raised as limitations or future work.

- **Calibration is checked outside the model (Discussion).** A coherent Bayesian model expects its own forecasts to prove calibrated [Dawid1982], so the check has to use sites the model did not choose. A new sentence separates cross-validation, which estimates the error of a model on sites it selected, from the calibration draw, which bounds the error of a decision.
- **Label-conditional bound (R2, R3; Sections 3.4, 5.5; SI 10.1).** Implemented and run on the synthetic map, 250 campaigns. Calibrated on the 12 to 20 calibration sites of interest per level, with the worst case over their unknown total, it cut the interesting sites lost under the no-interest claim from 34.7 ± 8.5 % to 8.5 ± 4.4 %, at 359 ± 26 measurements against 334 ± 26; 4.9 % of level checks exceeded the share of 0.20 (allowed 20 %).
- **Audit of the finished map (new Section 3.6, 5.6; SI 10.3).** An R-free analogue [Brunger1992]: after the last level, a uniform sample of the skipped sites is measured, kept out of the map, and bounds the map's error with the exact hypergeometric limit. With 100 sites at 0.80 it bounded the final-map error at 1.5 %, 19.8 % and 11.1 % (true 0.4 %, 18.0 %, 8.4 %), holding in 100 %, 83 % and 85 % of draws. It needs no division of the confidence among levels.
- **GP acquisition campaign with the audit on top (R3; Section 5.6; SI 10.3).** On NaCl, a GP measured where it judged a skip most likely wrong. At 614 sites its map was wrong at 9.0 % of sites; it stated 11.2 % (predictive) or 3.9 % (latent); the audit bounded the share at 10.6 % (coverage 80.5 %).
- **Drift (R1 M3a, R2; Section 5.6; SI 10.2).** A slow swelling of the synthetic sample, 50 campaigns per rate. The bound on the skips held; the campaign measured more (468 ± 79 against 330 ± 26 at a 10 % stretch) and the error moved into the measured sites (21 % off the sample). Five repeated seed sites flagged 98 % of those campaigns and none without drift. Weighted conformal correction is discussed [Barber2023; Tibshirani2019], not simulated.
- **Cost against m and confidence (R3 M3; SI 10.4).** Table S10.5, IR map, 100 campaigns per cell.
- **Future work** now names a model of beam time and a live pilot campaign explicitly.
- **Length.** The main text grew to about 9,150 words. Suggestions on where to cut are welcome.

## Still open

- Zenodo DOI at submission; deposited sources will be stripped of revision notes then.
