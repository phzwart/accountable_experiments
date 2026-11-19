"""
IR map of a bioreef sample (``BP-area.npz``), 29 × 42 pixels.

Spectra are Mie-corrected (stage-1 resonant ME-EMSC) and cut to the
certificate window 1500–1850 cm⁻¹; the corrected window is cached in
``prepared.npz`` by the original experiment. The HiPoSa design
(r 0.2 → 0.025, seed 42, corners forced) is snapped to pixels, keeping the
coarsest level on a collision: 949 unique sites, levels L0–L6.

Interest: some channel in the window reaches absorbance 0.1.
Interpolation target: the rtol = atol = 0.10 envelope, averaged over
channels with absorbance ≥ 0.02.
Interest score: the maximum of the predicted spectrum, capped below 0.1, so
a site predicted to reach the interest level is never certified dark.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from accountable import (
    AccuracyCriterion, CampaignConfig, Certificate, Dataset, INTEREST, INTERP,
    DisagreementScore, LogisticInterpScore, PredictedMaxScore, RandomScore, SpectrumRoute, StoredOracle, make_policy,
)

from .._paths import data_root

INTEREST_LEVEL = 0.10
FLOOR = 0.02
RTOL = ATOL = 0.10


def load(root: Path | None = None) -> Dataset:
    root = Path(root or data_root())
    z = np.load(root / "IR_data" / "interest_gate_1500_1850" / "prepared.npz")
    pix = np.asarray(z["pix"], int)
    return Dataset(
        name="ir_bioreef", points=np.asarray(z["points"], float)[pix],
        levels=np.asarray(z["levels"], int), oracle=StoredOracle(z["spectra"]),
        axis=np.asarray(z["wn_check"], float), axis_unit="cm^-1",
        meta=dict(pix=pix, ny=int(z["ny"]), nx=int(z["nx"])),
    )


def interest_predicate(level: float = INTEREST_LEVEL):
    def interest(I, axis):
        return np.asarray(I, float).max(axis=1) >= level
    return interest


def criterion():
    return AccuracyCriterion(kind="envelope", rtol=RTOL, atol=ATOL, signal_min=FLOOR)


def _interp_score(score, seed):
    if score == "logistic":
        return LogisticInterpScore(loo_seed=0, max_train=120)
    if score == "random":
        return RandomScore(int(seed) + 10000)
    if score == "sibson_disagreement":
        return DisagreementScore()
    raise ValueError(f"unknown score {score!r}")


def config(ds: Dataset, *, policy="legacy_sequential", eps=0.10, confidence=0.75,
           seed=0, cal_size=40, final_level=6, score="logistic", policy_kwargs=None, nn_method="watson",
           interp_model="sibson", gp_kwargs=None) -> CampaignConfig:
    """
    ``legacy_sequential`` reproduces the original run (one budget ε = 0.10,
    δ = 0.25, interest first). ``separate`` gives each certificate ε/2 at
    confidence 1 − δ/2, so the shared statement is ε at confidence 1 − δ.
    ``nested_path`` puts the single budget ε on the shared event directly.
    ``interp_model`` ``gp_mle``, ``gp_design`` or ``gp_nonstationary`` replaces
    the natural-neighbour predictor and the interpolation score by a GP
    (posterior mean and posterior standard deviation); the interest score
    is unchanged.
    """
    crit = criterion()
    predictor = SpectrumRoute(crit, images=None, nn_method=nn_method)
    sb = None
    if interp_model.startswith("gp_"):
        from accountable.gp import gp_protocol
        predictor, sb = gp_protocol(ds, crit, interp_model[3:], **(gp_kwargs or {}))
    if score == "random":
        # Totally random ordering for both certificates: no cap on a uniform score.
        interest_cert = Certificate(INTEREST, RandomScore(int(seed) + 20000), cap=None)
    else:
        interest_cert = Certificate(INTEREST, PredictedMaxScore(), cap=INTEREST_LEVEL)
    certs = [
        interest_cert,
        Certificate(INTERP, sb if sb is not None else _interp_score(score, seed)),
    ]
    kw = dict(policy_kwargs or {})
    delta = 1.0 - confidence
    if policy == "legacy_sequential":
        pol = make_policy("legacy_sequential", eps=eps, delta=delta, **kw)
    elif policy == "separate":
        pol = make_policy("separate", budgets={INTEREST: eps / 2, INTERP: eps / 2},
                          confidence=1.0 - delta / 2, **kw)
    elif policy == "nested_path":
        pol = make_policy("nested_path", budget=eps, confidence=confidence, **kw)
    elif policy == "priority_path":
        kw.setdefault("order", [INTEREST, INTERP])
        pol = make_policy("priority_path", budget=eps, confidence=confidence, **kw)
    else:
        pol = make_policy(policy, **kw)
    return CampaignConfig(
        criterion=crit, predictor=predictor,
        certificates=certs, policy=pol, interest=interest_predicate(),
        seed_level=2, final_level=final_level, cal_size=cal_size, rng_seed=seed, nn_method=nn_method,
        map_confidence=confidence,
    )
