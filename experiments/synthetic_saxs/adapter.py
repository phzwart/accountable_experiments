"""
Synthetic SAXS mixture on the composition triangle.

The design is the HiPoSa unit-square grid with forced corners
(``hiposa_unit_square_corners.npz``, levels L0–L8), restricted to the
triangle x + y <= 1. Spectra come from the forward model on
``default_q(240)`` (Å⁻¹). The interpolant sees mirror images across the
three triangle walls and the origin corner, each carrying its preimage's
spectrum.

Targets:
- ``envelope``: full profile, rtol = atol = 0.01;
- ``peak``: dominant-peak position and FWHM, 0.005 / 0.001 Å⁻¹ absolute.

Interest (illustrative): the dominant peak stands at least 5 times its
local baseline above that baseline. That predicate is read off the
spectrum. In the forward model it selects most ordered-phase (I1, H1)
compositions.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from accountable import (
    AccuracyCriterion, CampaignConfig, Certificate, Dataset, DisagreementScore, INTEREST, INTERP,
    LogisticInterestScore, LogisticInterpScore, RandomScore, SpectrumRoute,
    StoredOracle, make_policy, peak_descriptors,
)

from .._paths import data_root
from . import forward

RTOL = ATOL = 0.01
PEAK_EPS, FWHM_EPS = 0.005, 0.001
PROMINENCE = 5.0


def wall_images(P: np.ndarray) -> np.ndarray:
    """Reflections across y = 0, x = 0, x + y = 1, and the origin corner."""
    P = np.asarray(P, float)
    if len(P) == 0:
        return np.zeros((0, 2))
    return np.vstack([
        np.column_stack([P[:, 0], -P[:, 1]]),
        np.column_stack([-P[:, 0], P[:, 1]]),
        np.column_stack([1.0 - P[:, 1], 1.0 - P[:, 0]]),
        np.column_stack([-P[:, 0], -P[:, 1]]),
    ])


def load(root: Path | None = None, n_q: int = 240) -> Dataset:
    root = Path(root or data_root())
    d = np.load(root / "hiposa_unit_square_corners.npz")
    P = np.asarray(d["points"], float)
    levels = np.asarray(d["levels"], int)
    q = forward.default_q(n_q)
    I = forward.saxs(P[:, 0], P[:, 1], q)
    tri = (P[:, 0] + P[:, 1]) <= 1.0 + 1e-9
    return Dataset(
        name="synthetic_saxs", points=P, levels=levels, oracle=StoredOracle(I),
        axis=q, axis_unit="A^-1", candidate=tri, images=wall_images,
        meta=dict(phase=forward.classify(P[:, 0], P[:, 1])),
    )


def interest_predicate(prominence: float = PROMINENCE):
    def interest(I, q):
        d = peak_descriptors(I, q)
        pr = np.asarray(d["prominence"], float)
        return np.asarray(d["has_peak"], bool) & np.isfinite(pr) & (pr >= prominence)
    return interest


def criterion(target: str, q: np.ndarray, tol: float | None = None) -> AccuracyCriterion:
    if target == "envelope":
        t = RTOL if tol is None else float(tol)
        return AccuracyCriterion(kind="envelope", rtol=t, atol=t)
    if target == "peak":
        return AccuracyCriterion(kind="peak", q=q, peak_eps=PEAK_EPS, fwhm_eps=FWHM_EPS,
                                 tol_mode="absolute")
    raise ValueError(f"unknown target {target!r}")


def config(ds: Dataset, *, target="envelope", mode="interp", confidence=0.90, seed=0,
           score="logistic", policy="separate", eps=0.10, cal_size=40, seed_level=2,
           policy_kwargs=None, nn_method="watson", interp_model="sibson", gp_kwargs=None,
           tol=None) -> CampaignConfig:
    crit = criterion(target, ds.axis, tol)
    interest = interest_predicate()
    s_seed = int(seed) + 10000
    if score == "random":
        sb = RandomScore(s_seed)
    elif score == "sibson_disagreement":
        sb = DisagreementScore()
    else:
        sb = LogisticInterpScore(loo_seed=s_seed)
    predictor = SpectrumRoute(crit, images=wall_images, nn_method=nn_method)
    if interp_model.startswith("gp_"):
        from accountable.gp import gp_protocol
        predictor, sb = gp_protocol(ds, crit, interp_model[3:], **(gp_kwargs or {}))
        if score == "gp_fail":
            from accountable.gp import GPFailProbScore
            sb = GPFailProbScore(predictor.engine, crit, seed=int(seed) + 20000)
    certs = []
    if mode == "2cert":
        sa = RandomScore(s_seed + 1) if score == "random" else \
            LogisticInterestScore(interest, None, None, seed=s_seed)
        certs.append(Certificate(INTEREST, sa))
    certs.append(Certificate(INTERP, sb))
    names = [c.name for c in certs]
    kw = dict(policy_kwargs or {})
    if policy == "separate":
        pol = make_policy("separate", budgets={nm: eps for nm in names}, confidence=confidence, **kw)
    elif policy == "nested_path":
        pol = make_policy("nested_path", budget=eps, confidence=confidence, **kw)
    elif policy == "priority_path":
        kw.setdefault("order", names)
        pol = make_policy("priority_path", budget=eps, confidence=confidence, **kw)
    else:
        pol = make_policy(policy, **kw)
    return CampaignConfig(
        criterion=crit, predictor=predictor,
        certificates=certs, policy=pol, interest=interest,
        seed_level=seed_level, cal_size=cal_size, rng_seed=seed, nn_method=nn_method,
    )
