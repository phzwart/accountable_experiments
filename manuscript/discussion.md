# 6 Discussion (draft 2)

## Scope of the guarantee

A map built under a guarantee serves its reader to the extent that the reader knows what the bound covers. The bound concerns the share of wrong skips among all design sites of a level, with probability over the calibration draw. Section 5.5 shows the two consequences: wrong skips gather in space, and when signal is rare a budget met on every level can still cost a large share of the sites of interest. A bound on the share of interesting sites lost calls for a label-conditional statement, calibrated on the calibration sites that hold signal [Vovk2005; Sadinle2019]. A uniform draw keeps those sites exchangeable with the interesting sites of the level, at the price of a calibration sample larger by the inverse of the share of interest; Appendix D gives the corresponding bound for the map. Calibration carries a fixed cost of 40 sites per certified level, up to a sixth of the IR map, a share that falls as maps grow, since the budget and the confidence alone set the sample size.

## What is certified shapes the campaign

A guarantee is stated for one acceptance metric, and the metric deserves the same care as the budget. The bound holds for any metric fixed before the calibration draw, and the metric decides the rest: which sites fail prediction, where measurements are taken and where wrong skips gather (Section 5.5). The same holds for any autonomous experiment: the quantity a model predicts, and the error its acquisition anticipates, decide where measurements are taken [Noack2019; Noack2020]. The guarantee delivers the claim as specified, and features outside that claim carry no protection. The metric is therefore best fixed from the scientific question before beam time, stated with the guarantee, and checked on a pilot scan for the cost it implies.

## Measured sites as data

The sites a campaign measures are also the data for a model of the process. A site is skipped under the interpolation claim when its neighbours predict it, and such a site adds little to a model that varies as smoothly as the response. The guarantee holds for any score frozen before the draw, so a score that ranks sites by the information they would add to a process model keeps the bound and steers measurements towards the model [Atkinson2007]; a synthesis campaign with a kinetic model is the natural test.

## Building other guarantees

The mechanism leaves wide freedom in the rules it certifies. Selection may follow any score, path or claim combination, and certification may bound any rate that counts sites: the share of a level skipped wrongly, the share of interesting sites lost, or either within groups of sites. Ratios such as the share of skips that are wrong, twice the share of the level on the NaCl scan (Table 4), are controlled through conformal p-values [Jin2023] and deserve their own bound where skipped sites are reused one by one. Two conditions carry every such statement. First, the calibration sites are an exchangeable draw from the population the statement concerns; a Mondrian category fixed by features known before the draw, such as a region or a predicted class, takes the place of the level and needs its own calibration sites [Vovk2005]. Second, the rule is non-anticipating: scores, claims, budgets and the family of thresholds are fixed before the draw, which enters only through that rule (Section 3.1). Each new form follows Section 3.4 and passes the Monte Carlo check of SI 4. Since the cheapest form changes between datasets (Section 5.1), a fully measured pilot scan is the place to compare candidate forms before beam time. A loss graded by the size of an error is not a count; for a bounded loss, confidence sequences for sampling without replacement [WaudbySmith2020] give a bound of the same kind, and they would let calibration stop as soon as the bound is settled, on counts as well.

## Optimisation

Optimisation is the natural next case. Its proposals come from the model just fitted, so earlier calibration sites lose exchangeability with them; reweighting by the known selection mechanism [Tibshirani2019; Fannjiang2022; Barber2023], online control of a long-run rate [Gibbs2021] and level sets, each a mapping problem with a threshold fixed before its draw [CerouGuyader2007; Gotovos2013], offer routes to a bound.

## The value of a stated rate

A stated rate is worth most where decisions rest on it: a budget chosen in advance holds at its confidence, and a model's own statement missed by a factor of ten or more (Section 5.3). Accountability costs measurements; on the NaCl scan, certifying the Gaussian process took about 100 more in exchange for a rate fixed in advance and kept. The record adds a second value in failure. A level over budget is either chance at the stated rate or a sign that a condition of Section 3.1 failed, through drift, beam damage or a draw that was not uniform, and the record tells which to examine. An uncertified agent leaves its errors unapportioned between model, data and chance.

## Accountable experiments

An accountable experiment certifies every action: each skip by its claim and bound, each measurement by the reason it was needed when the decision was made. The workflow leaves both in its record. Each site carries its level, scores and certified action; each level carries its calibration draw, picked failure probability and bound. The guarantee rests on the order of operations, so the record suffices: predictor and scores are frozen and recorded before each draw, the draw comes from a recorded seed, and every decision can be replayed, every bound recomputed (SI 5) and every measurement checked for whether it was needed (SI 8). Claims, tolerances and budgets form the contract, remain the experimenter's choice and enter the record as such. The guarantee then bounds, at the stated confidence, the share of each level skipped under a false claim.

---

## Notes for revision (not part of the text)

- Example sentences on practice replaced by statistical ones (agreed). Pilot-scan sentence kept (agreed).
- References for the optimisation paragraph: [Fannjiang2022] Fannjiang, Bates, Angelopoulos, Listgarten, Jordan (2022), Conformal prediction under feedback covariate shift for biomolecular design, PNAS 119(43), e2204569119, doi:10.1073/pnas.2204569119 (verified). [Tibshirani2019] Tibshirani, Barber, Candès, Ramdas (2019), Conformal prediction under covariate shift, NeurIPS 32, 2530–2540 (verified). [Barber2023] Barber, Candès, Ramdas, Tibshirani (2023), Conformal prediction beyond exchangeability, Ann. Stat. 51(2) (check). [Gibbs2021] Gibbs, Candès (2021), Adaptive conformal inference under distribution shift, NeurIPS 34 (check).
- Level-set paragraph: references to check, [CerouGuyader2007] Cérou, Guyader (2007), Adaptive multilevel splitting for rare event analysis, Stoch. Anal. Appl. 25(2), 417–443; [Gotovos2013] Gotovos, Casati, Hitz, Krause (2013), Active learning for level set estimation, IJCAI. Also related: Bryan et al. (2005), Active learning for identifying function threshold boundaries, NeurIPS.
- Draft 2: metric numbers moved to Results 5.5; optimisation and level-set paragraphs merged; closing paragraph on accountability added; the fixed-candidate-pool route dropped from the optimisation paragraph. Level sets: the threshold refers to the whole response (q/s rule); outlook only, no experiment. Reference to add: [DavidNagaraja2003] David, Nagaraja (2003), Order Statistics, 3rd ed., Wiley.
- Scope paragraph references to add: [Vovk2005] Vovk, Gammerman, Shafer (2005), Algorithmic Learning in a Random World, Springer (Mondrian/label-conditional); [Sadinle2019] Sadinle, Lei, Wasserman (2019), Least ambiguous set-valued classifiers with bounded error levels, JASA 114(525), 223–234.
- Numerical reproducibility of the interpolant (planned paragraph) not written; one sentence could go into the scope paragraph if wanted.

