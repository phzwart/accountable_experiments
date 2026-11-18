"""Fast end-to-end campaigns on a small smooth field, for every policy and both routes."""
import numpy as np
import pytest

from accountable import (
    AccuracyCriterion, CampaignConfig, Certificate, Dataset, INTEREST, INTERP,
    LogisticInterpScore, PredictedMaxScore, RandomScore, ScalarRoute, ScalarTarget,
    SpectrumRoute, StoredOracle, make_policy, run_campaign,
)


def _dataset(seed=0):
    rng = np.random.default_rng(seed)
    pts, lv = [], []
    for L, n in enumerate([9, 12, 24, 48, 90]):
        pts.append(rng.random((n, 2)))
        lv.append(np.full(n, L))
    P = np.vstack(pts)
    levels = np.concatenate(lv)
    axis = np.linspace(0, 1, 30)
    centre = 0.3 + 0.4 * P[:, :1]
    I = np.exp(-((axis[None, :] - centre) ** 2) / 0.01) * (0.5 + P[:, 1:2])
    return Dataset("toy", P, levels, StoredOracle(I), axis)


def _interest(I, axis):
    return np.asarray(I).max(axis=1) >= 1.0


def _config(policy, two=True, route="spectrum"):
    crit = AccuracyCriterion(kind="envelope", rtol=0.1, atol=0.05)
    certs = [Certificate(INTERP, RandomScore(3))]
    if two:
        certs.insert(0, Certificate(INTEREST, PredictedMaxScore(), cap=1.0))
    if route == "spectrum":
        pred = SpectrumRoute(crit)
    else:
        target = ScalarTarget(lambda I, a: (np.asarray(I).max(axis=1), np.ones(len(I), bool)),
                              rtol=0.1, atol=0.05, name="max")
        pred = ScalarRoute(target, axis=np.linspace(0, 1, 30))
    return CampaignConfig(criterion=crit, predictor=pred, certificates=certs, policy=policy,
                          interest=_interest, seed_level=1, cal_size=10, rng_seed=0)


POLICY_SPECS = [
    ("separate", dict(budgets={INTEREST: 0.2, INTERP: 0.2}, confidence=0.75)),
    ("nested_path", dict(budget=0.2, confidence=0.75)),
]


@pytest.mark.parametrize("name,kw", POLICY_SPECS)
@pytest.mark.parametrize("route", ["spectrum", "scalar"])
def test_campaign_runs_and_accounts(name, kw, route):
    ds = _dataset()
    res = run_campaign(ds, _config(make_policy(name, **kw), route=route))
    # Every site is accounted for exactly once.
    assert set(np.unique(res.reason)) <= {
        "seed", "calibration", "no_certificate", "interpolable",
        "not_interesting", "not_interesting+interpolable"}
    assert res.measured.sum() + res.skipped.sum() == ds.n
    assert not (res.measured & res.skipped).any()
    # Skips only ever come from certificates; seed and calibration are measured.
    assert res.measured[res.is_seed].all() and res.measured[res.is_cal].all()
    for r in res.per_level:
        if r.get("empty"):
            continue
        assert r["guarantees"], "sound policies state a guarantee"


def test_ltt_policy_single_certificate():
    ds = _dataset(1)
    pol = make_policy("ltt_conditional", certificate=INTERP, alpha=0.2, confidence=0.75)
    res = run_campaign(ds, _config(pol, two=False))
    assert res.measured.sum() + res.skipped.sum() == ds.n


def test_logistic_score_campaign():
    ds = _dataset(2)
    cfg = _config(make_policy("separate", budgets={INTERP: 0.2}, confidence=0.75), two=False)
    cfg.certificates = [Certificate(INTERP, LogisticInterpScore(loo_seed=0, max_train=30))]
    res = run_campaign(ds, cfg)
    assert res.n_measured >= int((ds.levels <= 1).sum())


def test_save_round_trip(tmp_path):
    ds = _dataset()
    res = run_campaign(ds, _config(make_policy("nested_path", budget=0.2, confidence=0.75)))
    out = res.save(tmp_path / "run")
    assert (out / "result.json").exists() and (out / "sites.npz").exists()
