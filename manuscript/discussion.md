# 6 Discussion (draft 1: building other guarantees; optimisation and distribution shift)

*Other paragraphs follow the plan: scope of the claim, calibration overhead, conditional rates, use at an instrument, numerical reproducibility of the interpolant.*

## Building other guarantees

The forms reported here address three questions about wrong skips, and an instrument may face others. A bound per claim answers how often each reason for skipping failed; a bound on the shared event, how often any skip failed. Other needs call for other forms: unequal budgets when one claim is riskier than the other, a bound on the proportion of false skips among the skipped sites [Jin2023], or a path learned on part of the calibration draw [LauferGoldshtein2023]. Each follows the recipe of Section 3.4 and is accepted by the same Monte Carlo check (SI 4). The cost of a form on a given dataset is hard to predict in advance; Section 5.2 shows that the ordering of three forms changes between datasets. Running candidate forms on a fully measured pilot scan, as done here retrospectively, gives that cost before beam time is committed.

## Optimisation and distribution shift

Mapping lends itself to this construction because the population of interest is fixed before the experiment. Every design site is a site the map must cover, and a uniform draw from a level represents that level. Optimisation changes the picture. A Bayesian optimiser or a self-driving laboratory proposes its next experiments from the model it has just fitted, so the points it asks about are chosen by the data, and calibration points from earlier rounds are no longer exchangeable with them. This feedback covariate shift is characteristic of active learning, adaptive experimental design and Bayesian optimisation [Fannjiang2022]. Three routes keep a guarantee in that setting. When the selection mechanism is known, as it is to the optimiser that made the choice, calibration points can be reweighted by the likelihood ratio between proposed and calibration points [Tibshirani2019; Fannjiang2022; Barber2023]; the bound widens wherever the optimiser concentrates on regions the calibration sample seldom visits. A fixed candidate pool, audited by a uniform draw as in this work, restores exchangeability for statements about the pool while the optimiser chooses freely where to look; the statement then concerns the pool, which need not contain what the optimiser proposes next. Online methods control the long-run error rate without exchangeability and give up the finite-sample statement at each step [Gibbs2021]. This work covers mapping, with a fixed population and a uniform audit; optimisation is the natural next case.

---

## Notes for revision (not part of the text)

- Example sentences on practice replaced by statistical ones (agreed). Pilot-scan sentence kept (agreed).
- References for the optimisation paragraph: [Fannjiang2022] Fannjiang, Bates, Angelopoulos, Listgarten, Jordan (2022), Conformal prediction under feedback covariate shift for biomolecular design, PNAS 119(43), e2204569119, doi:10.1073/pnas.2204569119 (verified). [Tibshirani2019] Tibshirani, Barber, Candès, Ramdas (2019), Conformal prediction under covariate shift, NeurIPS 32, 2530–2540 (verified). [Barber2023] Barber, Candès, Ramdas, Tibshirani (2023), Conformal prediction beyond exchangeability, Ann. Stat. 51(2) (check). [Gibbs2021] Gibbs, Candès (2021), Adaptive conformal inference under distribution shift, NeurIPS 34 (check).
- The paragraph opens on why mapping works; if you want it to open on the opportunity instead, start with the second sentence's subject: "Self-driving laboratories increasingly optimise rather than map, …".

