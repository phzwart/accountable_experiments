"""Tails, thresholds and policies: exact values and identities."""
import numpy as np
import pytest
from scipy.stats import binom

from accountable.policies import (
    LevelData, NestedPathPolicy, SeparatePolicy, covers, order_statistic_threshold,
    single_threshold,
)
from accountable.tails import (
    allowed_k, allowed_k_binomial, allowed_k_hypergeometric, clopper_pearson_upper, eps_min,
)


def test_allowed_k_matches_binomial_tail():
    # BRIEFING: m = 40, eps = 0.10 -> k = 2 at 0.75, k = 1 at 0.90, k = 0 at 0.975.
    assert allowed_k_binomial(0.10, 40, 0.25) == 2
    assert allowed_k_binomial(0.10, 40, 0.10) == 1
    assert allowed_k_binomial(0.10, 40, 0.025) == 0
    for eps, m, d in [(0.1, 40, 0.1), (0.05, 100, 0.1), (0.2, 25, 0.05)]:
        k = allowed_k_binomial(eps, m, d)
        assert binom.cdf(k, m, eps) <= d + 1e-12
        assert binom.cdf(k + 1, m, eps) > d


def test_infeasible_budget_gives_minus_one():
    assert allowed_k_binomial(0.02, 40, 0.10) == -1
    assert eps_min(0.90, 40) == pytest.approx(1 - 0.1 ** (1 / 40))


@pytest.mark.parametrize("N", [65, 98, 138, 271, 399, 521, 1052])
@pytest.mark.parametrize("conf", [0.75, 0.90, 0.975])
@pytest.mark.parametrize("eps", [0.05, 0.10, 0.20])
def test_binomial_never_looser_than_hypergeometric(N, conf, eps):
    kb = allowed_k_binomial(eps, 40, 1 - conf)
    kh = allowed_k_hypergeometric(eps, 40, 1 - conf, N)
    assert kb <= kh
    allowed_k(eps, 40, 1 - conf, N=N)  # does not raise


def test_order_statistic_threshold_semantics():
    s = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    bad = np.array([0, 1, 0, 1, 0, 1], bool)
    # k = 0: strictly below the first bad score (0.2) -> 0.1
    assert single_threshold(s, bad, 0) == 0.1
    # k = 1: strictly below the second bad score (0.4) -> 0.3
    assert single_threshold(s, bad, 1) == 0.3
    # k >= number of bad -> +inf; k < 0 -> -inf
    assert np.isposinf(single_threshold(s, bad, 3))
    assert np.isneginf(single_threshold(s, bad, -1))
    # at most k bad calibration sites are covered
    for k in range(3):
        tau = single_threshold(s, bad, k)
        assert (covers(s, tau) & bad).sum() <= k


def test_cap_only_shrinks_cover():
    s = np.array([0.01, 0.05, 0.09, 0.11])
    assert covers(s, np.inf, cap=0.1).tolist() == [True, True, True, False]


def _level(rng, N=200, m=40, two=True):
    sa, sb = rng.random(N), rng.random(N)
    Z = rng.random(N) < 0.3 * sa
    F = rng.random(N) < 0.4 * sb
    cal = np.sort(rng.choice(N, m, replace=False))
    scores = {"interp": sb}
    bad = {"interp": F[cal]}
    if two:
        scores["interest"] = sa
        bad["interest"] = Z[cal]
    return LevelData(N, scores, cal, bad), Z, F


def test_nested_path_equals_separate_for_one_certificate():
    rng = np.random.default_rng(1)
    for _ in range(200):
        lvl, _, _ = _level(rng, two=False)
        a = SeparatePolicy({"interp": 0.1}, 0.9).decide(lvl)
        b = NestedPathPolicy(0.1, 0.9).decide(lvl)
        assert np.array_equal(a.covers["interp"], b.covers["interp"])


def test_nested_path_calibration_count_within_k():
    rng = np.random.default_rng(2)
    for _ in range(200):
        lvl, Z, F = _level(rng)
        d = NestedPathPolicy(0.1, 0.9).decide(lvl)
        E = (d.covers["interest"] & Z) | (d.covers["interp"] & F)
        assert E[lvl.cal].sum() <= d.k["interp"]


def test_clopper_pearson_upper():
    assert clopper_pearson_upper(0, 40, 0.9) == pytest.approx(1 - 0.1 ** (1 / 40))
    assert clopper_pearson_upper(40, 40, 0.9) == 1.0
