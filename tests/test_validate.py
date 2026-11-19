"""
The acceptance check passes the shipped policies, a policy built by
subclassing, and flags a plug-in rule that states a guarantee it lacks.
"""
import numpy as np
import pytest

from accountable.policies import (Guarantee, LevelData, NestedPathPolicy, Policy,
                                  PolicyDecision, PriorityPathPolicy, SeparatePolicy, covers)
from accountable.validate import check_coverage, population

RATES = {"interest": 0.30, "interp": 0.35}


@pytest.mark.parametrize("informative", [False, True])
@pytest.mark.parametrize("make", [
    lambda: SeparatePolicy({"interest": 0.10, "interp": 0.10}, confidence=0.90),
    lambda: NestedPathPolicy(0.10, confidence=0.90),
    lambda: PriorityPathPolicy(0.10, confidence=0.90, order=["interest", "interp"]),
    lambda: PriorityPathPolicy(0.10, confidence=0.90, order=["interp", "interest"]),
    lambda: NestedPathPolicy(0.10, confidence=0.75, tail="hypergeometric", placement="boundary"),
])
def test_shipped_policies_pass(make, informative):
    s, y = population(271, RATES, informative=informative, seed=4)
    rep = check_coverage(make(), s, y, draws=1500, seed=1)
    assert rep.rows, "policy stated no guarantee"
    assert rep.passed, str(rep)


def test_priority_path_with_one_certificate_is_the_single_rule():
    s, y = population(271, {"interp": 0.35}, seed=2)
    rng = np.random.default_rng(0)
    for _ in range(50):
        cal = np.sort(rng.choice(271, 40, replace=False))
        lvl = LevelData(271, s, cal, {"interp": y["interp"][cal]})
        a = PriorityPathPolicy(0.10, 0.80, order=["interp"]).decide(lvl).covers["interp"]
        b = NestedPathPolicy(0.10, 0.80).decide(lvl).covers["interp"]
        assert np.array_equal(a, b)


class PlugInPolicy(Policy):
    """Largest threshold whose empirical calibration rate is within budget."""

    policy_name = "plug_in"

    def __init__(self, eps, confidence):
        self.eps, self.confidence = eps, confidence

    def decide(self, level):
        s = level.scores["interp"]
        sc = np.sort(s[level.cal])
        tau = -np.inf
        for t in sc:
            if np.sum(level.bad["interp"] & (s[level.cal] <= t)) / level.m <= self.eps:
                tau = t
        return PolicyDecision({"interp": covers(s, tau)}, {"interp": tau}, {"interp": -1},
                              [Guarantee("R_interp", self.eps, self.confidence)])


def test_plug_in_rule_is_flagged():
    s, y = population(271, {"interp": 0.35}, seed=3)
    rep = check_coverage(PlugInPolicy(0.10, 0.90), s, y, draws=1500, seed=0)
    assert not rep.passed
    assert rep.rows[0].observed > 0.3


def test_exact_tail_and_boundary_placement_reach_the_nominal_rate():
    """On a small level the exact tail allows k = 3 and the bound is attained."""
    s, y = population(65, RATES, informative=False, seed=4)
    rep = check_coverage(NestedPathPolicy(0.10, 0.75, tail="hypergeometric", placement="boundary"),
                         s, y, draws=3000, seed=1)
    assert rep.passed and rep.rows[0].observed > 0.20
