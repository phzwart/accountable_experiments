"""
Monte Carlo check of each policy's stated guarantee on finite populations.

For a fixed population of scores and labels, the calibration draw is the
only randomness. Over many draws the frequency with which the population
rate exceeds its budget must not exceed the stated failure probability
(up to Monte Carlo error). Uninformative scores are the hard case: the
covered bad rate grows with the threshold as fast as it can.
"""
import numpy as np
import pytest

from accountable.policies import LevelData, NestedPathPolicy, SeparatePolicy

T = 3000


def _tol(p):
    return 3.0 * np.sqrt(p * (1 - p) / T) + 1e-3


def _population(seed, N, rate_a, rate_b, informative):
    rng = np.random.default_rng(seed)
    sa, sb = rng.random(N), rng.random(N)
    if informative:
        Z = rng.random(N) < 2 * rate_a * sa
        F = rng.random(N) < 2 * rate_b * sb
    else:
        Z = rng.random(N) < rate_a
        F = rng.random(N) < rate_b
    return sa, sb, Z, F


@pytest.mark.parametrize("informative", [False, True])
@pytest.mark.parametrize("N", [65, 271])
def test_separate_policy_coverage(informative, N):
    sa, sb, Z, F = _population(10 + N, N, 0.3, 0.35, informative)
    pol = SeparatePolicy({"interest": 0.10, "interp": 0.10}, confidence=0.90)
    rng = np.random.default_rng(0)
    ex_a = ex_b = ex_E = 0
    for _ in range(T):
        cal = np.sort(rng.choice(N, 40, replace=False))
        d = pol.decide(LevelData(N, {"interest": sa, "interp": sb}, cal,
                                 {"interest": Z[cal], "interp": F[cal]}))
        Ra = (d.covers["interest"] & Z).mean()
        Rb = (d.covers["interp"] & F).mean()
        RE = ((d.covers["interest"] & Z) | (d.covers["interp"] & F)).mean()
        ex_a += Ra > 0.10
        ex_b += Rb > 0.10
        ex_E += RE > 0.20
    assert ex_a / T <= 0.10 + _tol(0.10)
    assert ex_b / T <= 0.10 + _tol(0.10)
    assert ex_E / T <= 0.20 + _tol(0.20)


@pytest.mark.parametrize("informative", [False, True])
@pytest.mark.parametrize("weights", [None, {"interest": 0.5, "interp": 1.0}])
@pytest.mark.parametrize("N", [65, 271])
def test_nested_path_coverage(informative, weights, N):
    sa, sb, Z, F = _population(20 + N, N, 0.3, 0.35, informative)
    pol = NestedPathPolicy(0.10, confidence=0.90, weights=weights)
    rng = np.random.default_rng(1)
    ex = 0
    for _ in range(T):
        cal = np.sort(rng.choice(N, 40, replace=False))
        d = pol.decide(LevelData(N, {"interest": sa, "interp": sb}, cal,
                                 {"interest": Z[cal], "interp": F[cal]}))
        RE = ((d.covers["interest"] & Z) | (d.covers["interp"] & F)).mean()
        ex += RE > 0.10
    assert ex / T <= 0.10 + _tol(0.10)


def test_uninformative_scores_are_near_tight():
    """With random scores the separate bound is not wildly conservative."""
    N = 271
    sa, sb, Z, F = _population(5, N, 0.3, 0.35, informative=False)
    pol = SeparatePolicy({"interp": 0.10}, confidence=0.75)
    rng = np.random.default_rng(3)
    ex = 0
    for _ in range(T):
        cal = np.sort(rng.choice(N, 40, replace=False))
        d = pol.decide(LevelData(N, {"interp": sb}, cal, {"interp": F[cal]}))
        ex += (d.covers["interp"] & F).mean() > 0.10
    assert 0.05 < ex / T <= 0.25 + _tol(0.25)


def test_legacy_sequential_exceeds_its_nominal_rate():
    """
    The original IR rule picks two thresholds from one sample along a
    data-dependent route. On this population its shared wrong-skip rate
    exceeds 0.10 in more than 25% of draws; the nested path does not.
    """
    pytest.importorskip("ssbc")
    from accountable.policies import LegacySequentialPolicy

    N, T2 = 399, 2000
    rng = np.random.default_rng(7)
    sa, sb = rng.random(N) * 0.09, rng.random(N)
    Z, F = rng.random(N) < 0.5, rng.random(N) < 0.1
    out = {}
    for pol in (LegacySequentialPolicy(0.10, 0.25), NestedPathPolicy(0.10, 0.75)):
        r = np.random.default_rng(0)
        ex = 0
        for _ in range(T2):
            cal = np.sort(r.choice(N, 40, replace=False))
            d = pol.decide(LevelData(N, {"interest": sa, "interp": sb}, cal,
                                     {"interest": Z[cal], "interp": F[cal]},
                                     caps={"interest": 0.1}))
            ex += ((d.covers["interest"] & Z) | (d.covers["interp"] & F)).mean() > 0.10
        out[pol.policy_name] = ex / T2
    se = np.sqrt(0.25 * 0.75 / T2)
    assert out["legacy_sequential"] > 0.25 + 2 * se
    assert out["nested_path"] <= 0.25 + 3 * se
