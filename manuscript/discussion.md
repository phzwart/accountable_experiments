# 6 Discussion (draft 1: building other guarantees)

*Other paragraphs follow the plan: scope of the claim, calibration overhead, conditional rates, use at an instrument, numerical reproducibility of the interpolant.*

## Building other guarantees

The forms reported here answer three questions about wrong skips, and an instrument may face others. A beamline that must report how many skipped sites were uninteresting in error needs the per-claim form, whatever its cost. A mapping campaign judged on the final map needs only the shared rate and gains from spending the whole budget on it. Other needs call for other forms: unequal budgets when one claim is riskier than the other, a bound on the proportion of false skips among the skipped sites [Jin2023], or a path learned on part of the calibration draw [LauferGoldshtein2023]. Each follows the recipe of Section 3.4 and is accepted by the same Monte Carlo check (SI 4). The cost of a form on a given dataset is hard to predict in advance; Section 5.2 shows that the ordering of three forms changes between datasets. Running candidate forms on a fully measured pilot scan, as done here retrospectively, gives that cost before beam time is committed.

---

## Notes for revision (not part of the text)

- "A beamline that must report…" is an example of practice. If you prefer to keep the framing on statistical claims, replace the two example sentences with: "A bound per claim answers how often each reason failed; a bound on the shared event answers how often any skip failed."
- The pilot-scan sentence turns a limitation (retrospective study) into a recommendation. Drop it if that reads as overreach.
