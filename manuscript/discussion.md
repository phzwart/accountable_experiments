# 6 Discussion (draft 2)

## Scope of the guarantee

A map built under a guarantee serves its reader to the extent that the reader knows what the bound covers. The bound concerns the share of wrong skips among all design sites of a level, with probability over the calibration draw. Section 5.5 shows the two consequences: wrong skips gather in space, and when signal is rare a budget met on every level can still cost a large share of the sites of interest. A bound on the share of interesting sites lost calls for a label-conditional statement, calibrated on the calibration sites that hold signal [Vovk2005; Sadinle2019]. A uniform draw keeps those sites exchangeable with the interesting sites of the level, at the price of a calibration sample larger by the inverse of the share of interest; Appendix D gives the corresponding bound for the map. Calibration carries a fixed cost of 40 sites per certified level, up to a sixth of the IR map, a share that falls as maps grow, since the budget and the confidence alone set the sample size.

## What is certified shapes the campaign

A guarantee is stated for one acceptance metric, and the metric deserves the same care as the budget. The bound holds for any metric fixed before the calibration draw, and the metric decides the rest: which sites fail prediction, where measurements are taken and where wrong skips gather (Section 5.5). The same holds for any autonomous experiment: the quantity a model predicts, and the error its acquisition anticipates, decide where measurements are taken [Noack2019; Noack2020]. The guarantee delivers the claim as specified, and features outside that claim carry no protection. The metric is therefore best fixed from the scientific question before beam time, stated with the guarantee, and checked on a pilot scan for the cost it implies.

## Measured sites as data

The sites a campaign measures are also the data for a model of the process. A site is skipped under the interpolation claim when its neighbours predict it, and such a site adds little to a model that varies as smoothly as the response; on the calcination campaign the measured runs were nearly as informative as the full design (Section 5.6). A model identified by features outside the claim, such as a background or a weak minor phase, lies beyond this argument. The guarantee holds for any score frozen before the draw, so a score that ranks sites by the information they would add to the process model keeps the bound and steers measurements towards the model [Atkinson2007].

## Building other guarantees

The forms reported here answer three questions about wrong skips, and an instrument may face others: unequal budgets when one claim is riskier, a bound on the proportion of false skips among the skipped sites [Jin2023], or a path learned on part of the calibration draw [LauferGoldshtein2023]. Each follows the recipe of Section 3.4 and is accepted by the same Monte Carlo check (SI 4). Since the cheapest form changes between datasets (Section 5.2), a fully measured pilot scan is the place to price candidate forms before beam time is committed.

## Optimisation

Optimisation is the natural next case, and it differs from mapping in its population. An optimiser proposes its next experiments from the model it has just fitted, so calibration points from earlier rounds are no longer exchangeable with its proposals. Reweighting by the known selection mechanism restores a bound that widens where the optimiser concentrates [Tibshirani2019; Fannjiang2022; Barber2023], and online methods control a long-run rate instead [Gibbs2021]. Level sets offer a further route. A search for the maximum becomes a sequence of mapping problems, each asking where the response exceeds a threshold, which is the claim the interest certificate makes. When a fraction $s$ of the domain survives and contains the top set, the quantile $q$ of the whole response is the quantile $1 - (1 - q)/s$ of the surviving region, which the order statistics of a uniform draw from that region bound [DavidNagaraja2003]. With threshold and population fixed before each draw, the conditions of Appendix A hold stage by stage, as adaptive levels do in multilevel splitting [CerouGuyader2007] and thresholds in active level-set estimation [Gotovos2013]. Each stage then bounds the fraction of the top set eliminated in error, and the location of the single maximum stays open.

## Accountable experiments

An accountable instrument needs a reason for every site and a statement that a reviewer can check. The workflow leaves both in its record. Each site carries its level, its scores, and the claim that covered it or the reason it was measured; each level carries its calibration draw, its picked failure probability and its bound. The guarantee rests on the order of operations, so the record suffices: predictor and scores are frozen and recorded before each draw, the draw comes from a recorded seed, and every decision can be replayed and every bound recomputed (SI 5). Claims, metrics and budgets remain the experimenter's choice and enter the record as such. The guarantee then states, for each claim, how often a skip made under it was wrong.

---

## Notes for revision (not part of the text)

- Example sentences on practice replaced by statistical ones (agreed). Pilot-scan sentence kept (agreed).
- References for the optimisation paragraph: [Fannjiang2022] Fannjiang, Bates, Angelopoulos, Listgarten, Jordan (2022), Conformal prediction under feedback covariate shift for biomolecular design, PNAS 119(43), e2204569119, doi:10.1073/pnas.2204569119 (verified). [Tibshirani2019] Tibshirani, Barber, Candès, Ramdas (2019), Conformal prediction under covariate shift, NeurIPS 32, 2530–2540 (verified). [Barber2023] Barber, Candès, Ramdas, Tibshirani (2023), Conformal prediction beyond exchangeability, Ann. Stat. 51(2) (check). [Gibbs2021] Gibbs, Candès (2021), Adaptive conformal inference under distribution shift, NeurIPS 34 (check).
- Level-set paragraph: references to check, [CerouGuyader2007] Cérou, Guyader (2007), Adaptive multilevel splitting for rare event analysis, Stoch. Anal. Appl. 25(2), 417–443; [Gotovos2013] Gotovos, Casati, Hitz, Krause (2013), Active learning for level set estimation, IJCAI. Also related: Bryan et al. (2005), Active learning for identifying function threshold boundaries, NeurIPS.
- Draft 2: metric numbers moved to Results 5.5; optimisation and level-set paragraphs merged; closing paragraph on accountability added; the fixed-candidate-pool route dropped from the optimisation paragraph. Level sets: the threshold refers to the whole response (q/s rule); outlook only, no experiment. Reference to add: [DavidNagaraja2003] David, Nagaraja (2003), Order Statistics, 3rd ed., Wiley.
- Scope paragraph references to add: [Vovk2005] Vovk, Gammerman, Shafer (2005), Algorithmic Learning in a Random World, Springer (Mondrian/label-conditional); [Sadinle2019] Sadinle, Lei, Wasserman (2019), Least ambiguous set-valued classifiers with bounded error levels, JASA 114(525), 223–234.
- Numerical reproducibility of the interpolant (planned paragraph) not written; one sentence could go into the scope paragraph if wanted.

