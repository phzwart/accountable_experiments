# Architecture

The package separates what is claimed from how a campaign earns it. The claim lives in one place: the policy. Everything else is replaceable without touching it.

## Pieces

| Piece | Module | Role | Extension point |
| --- | --- | --- | --- |
| Dataset and oracle | `dataset.py` | design positions, levels, axis, symmetry images, candidate mask; `measure(idx)` | live instrument oracle; any design |
| Criterion | `criteria.py` | target and acceptance score, `s <= 1` accepts: envelope, peak descriptors, integral | new `kind` |
| Predictor | `predictors.py` | prediction from the measured set and the label `F = 1{s > 1}`; spectrum route and scalar route on shared natural-neighbour weights | GP, factor models, any regressor with `label()` |
| Interest predicate | adapter | `interest(I, axis) -> bool` on the truth | any measurable predicate |
| Score | `scores.py` | fitted on the measured set, frozen per level, orders sites | `Score` subclass |
| Policy | `policies.py` | thresholds from frozen scores and calibration labels, plus the guarantee it states | `@register("name")` |
| Campaign | `campaign.py` | seed → per level: fit → freeze → draw → label → decide → record | — |
| Tails | `tails.py` | allowed k (binomial, checked against hypergeometric), Clopper–Pearson | — |

## Information flow at one level

1. The measured set before the level is fixed. Every score is fitted on it and frozen.
2. Scores are read on every site of the level. This happens before the draw, so a label-free path or a quantile grid can use them.
3. The calibration sample is drawn uniformly without replacement from the campaign RNG.
4. Calibration sites are measured. Their labels come from the frozen predictor and the truth.
5. The policy returns one cover per certificate on the level and its guarantee.
6. Remainder sites are skipped when any certificate covers them. Otherwise they are measured.

No score or policy sees a remainder label. In retrospective runs, remainder labels are computed afterwards, for bookkeeping only.

## Records

Each level record carries, per certificate: threshold, allowed k with both tails, calibration bad count, covered counts, level and remainder joint rates, remainder conditional rate, and the expected skip fraction of a uniform score. It also carries the shared wrong-skip rate `E` on the level and on the remainder, the guarantees, and the map certificate. `post` repeats the remainder accounting with labels from the end-of-level measured set; the original IR run reported that quantity.

## Adding a scheme

A new budget policy implements `decide(LevelData) -> PolicyDecision` and registers a name. It returns either guarantees stated on `R_<certificate>` or `R_E`, or an empty list, which the records show as no guarantee. Before such a policy is used for a claim, it should get a Monte Carlo coverage test in `tests/test_coverage_mc.py` on uninformative scores.

## Reproduction

The natural-neighbour code, criteria, features and logistic fits are carried over from the original scripts without numerical change, so decisions reproduce exactly in the same environment. `tests/test_reproduce.py` checks every site's decision against references produced by the original code. Section "Environment sensitivity" in `docs/reproduction.md` explains why archived numbers from another machine can differ.
