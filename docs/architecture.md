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

The shipped policies are examples of guarantees, and a campaign accepts any other that keeps the contract below. Different needs call for different statements: one bound per reason for skipping, one bound on any wrong skip, a conditional rate, a preference order between certificates.

**Contract.** A policy implements `decide(LevelData) -> PolicyDecision` and registers a name with `@register("name")`.

1. It may use the frozen scores of every site of the level, the indices of the calibration sites, and the bad labels of those sites only. Scores are frozen before the draw; the policy must not refit them.
2. Every family of thresholds it searches is fixed before the labels are seen. A path, a grid or a split of the budget is built from scores, settings or earlier levels, never from the calibration labels of this level.
3. It states its guarantees as `Guarantee(event, budget, confidence)`, with `event` either `R_<certificate>` or `R_E`, or returns an empty list. The records show an empty list as no guarantee.

**Acceptance.** Before a policy carries a claim, every guarantee it states is checked by Monte Carlo on fixed finite populations with `accountable.validate.check_coverage`, on uninformative and informative scores:

```python
from accountable.validate import check_coverage, population
scores, labels = population(271, {"interest": 0.30, "interp": 0.35}, informative=False)
print(check_coverage(MyPolicy(...), scores, labels, m=40, draws=2000))
```

The check counts, per stated guarantee, the draws in which the population rate exceeds its budget, and compares that frequency with `1 - confidence`. It flags rules that state more than they deliver; a plug-in rule on the empirical calibration rate fails it (`tests/test_validate.py`). Passing the check is evidence, and the finite-sample argument still belongs in `docs/theory.md`.

**Worked example.** `priority_path` admits certificates in a fixed order, interest first and interpolation second, under one budget. It subclasses `nested_path` and overrides only `entry_times`: certificate *i* in the order sweeps its own score quantiles over λ ∈ [i, i + 1]. The order is a setting, so the path is fixed before the draw and the single-budget argument applies as it stands. The legacy IR rule aimed at the same preference but chose its second threshold from the labels left over by the first, which breaks item 2 of the contract.

## Reproduction

The natural-neighbour code, criteria, features and logistic fits are carried over from the original scripts without numerical change, so decisions reproduce exactly in the same environment. `tests/test_reproduce.py` checks every site's decision against references produced by the original code. Section "Environment sensitivity" in `docs/reproduction.md` explains why archived numbers from another machine can differ.
