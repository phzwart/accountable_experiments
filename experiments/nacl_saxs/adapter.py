"""
ALS BL7.3.3 NaCl scan (doi:10.5061/dryad.p2ngf1w4t).

3249 raster sites on a 0.25 mm stage grid, q from 0.589 to 38.94 nm⁻¹ in
1000 bins. The HiPoSa design (r 0.2 → 0.025 in the unit square) is
snapped to unique raster sites: 1071 sites, levels L0–L6. No symmetry:
these are stage coordinates.

Targets:
- ``envelope``: full profile, rtol = atol = 0.01;
- ``integral``: total intensity, rtol = atol = 0.01;
- ``qpeak``: dominant-peak position, tolerance one detector bin or ``peak_eps``;
- ``fwhm``: width of NaCl (200) at 22.28 nm⁻¹ ± 0.40, |ΔFWHM| ≤ 0.02 nm⁻¹,
  presence at 5 × window noise.

Interest: the (200) line is present (5 × noise above a local baseline).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from accountable import (
    AccuracyCriterion, CampaignConfig, Certificate, Dataset, INTEREST, INTERP,
    LogisticInterestScore, LogisticInterpScore, RandomScore, DisagreementScore,
    SpectrumRoute, StoredOracle, estimate_window_noise, make_policy, peak_descriptors,
)

from .._paths import data_root

# NaCl (200): q = 2π·2 / 5.6402 Å⁻¹ = 22.28 nm⁻¹.
Q200 = 22.280
Q200_HALF = 0.40
FWHM_TOL = 0.02
PRESENCE_C = 5.0
RTOL = ATOL = 0.01
P75_EPS = 9.492458504457112
MED_EPS = 3.784


def load(root: Path | None = None) -> tuple[Dataset, dict]:
    root = Path(root or data_root())
    z = np.load(root / "real_als" / "nacl_grid.npz")
    grid = {k: z[k] for k in z.files}
    d = np.load(root / "real_als" / "hiposa_nacl_unit.npz")
    pts, lv = np.asarray(d["points"], float), np.asarray(d["levels"], int)
    xy = grid["xy_mm"]
    lo = xy.min(axis=0)
    span = np.maximum(xy.max(axis=0) - lo, 1e-9)
    grid_u = (xy - lo) / span
    dist, nn = cKDTree(grid_u).query(pts)
    best = {}
    for i, g in enumerate(nn):
        cand = (int(lv[i]), float(dist[i]), i)
        if int(g) not in best or cand < best[int(g)]:
            best[int(g)] = cand
    order = sorted(best, key=lambda g: (best[g][0], g))
    idx = np.asarray(order, int)
    levels = np.asarray([best[g][0] for g in order], int)
    I = np.asarray(grid["intensity"][idx], float)
    ds = Dataset(
        name="nacl_saxs", points=grid_u[idx], levels=levels, oracle=StoredOracle(I),
        axis=np.asarray(grid["q"], float), axis_unit="nm^-1",
        meta=dict(raster_index=idx, xy_mm=xy[idx], lo=lo, span=span),
    )
    return ds, grid


def noise_sigma(ds: Dataset) -> float:
    I = ds.oracle.truth(np.arange(ds.n))
    return float(estimate_window_noise(I, ds.axis, Q200, Q200_HALF)["sigma"])


def interest_predicate(sigma: float):
    def interest(I, q):
        desc = peak_descriptors(I, q, q_center=Q200, q_halfwidth=Q200_HALF)
        hab = np.asarray(desc["height_above_base"], float)
        return np.asarray(desc["has_peak"], bool) & np.isfinite(hab) & (hab > PRESENCE_C * sigma)
    return interest


def criterion(target: str, q: np.ndarray, sigma: float, peak_eps: float | None = None, tol: float | None = None):
    if target == "envelope":
        return AccuracyCriterion(kind="envelope", rtol=RTOL, atol=ATOL, q_unit="nm^-1")
    if target == "integral":
        return AccuracyCriterion(kind="integral", rtol=RTOL, atol=ATOL, q=q, q_unit="nm^-1")
    if target == "qpeak":
        eps = float(peak_eps) if peak_eps is not None else float(np.median(np.diff(q)))
        return AccuracyCriterion(kind="peak", q=q, peak_eps=eps, include_width=False, q_unit="nm^-1")
    if target == "fwhm":
        return AccuracyCriterion(
            kind="peak", q=q, q_center=Q200, q_halfwidth=Q200_HALF,
            include_position=False, include_width=True, fwhm_eps=FWHM_TOL if tol is None else float(tol),
            tol_mode="absolute", presence_sigma=sigma, presence_multiple=PRESENCE_C,
            q_unit="nm^-1",
        )
    raise ValueError(f"unknown target {target!r}")


def config(ds: Dataset, *, target="fwhm", mode="2cert", confidence=0.90, seed=0,
           score="logistic", policy="separate", eps=0.10, peak_eps=None,
           cal_size=40, policy_kwargs=None, nn_method="watson", interp_model="sibson", gp_kwargs=None,
           tol=None) -> CampaignConfig:
    """
    The NaCl campaign as specified in BRIEFING.md: seed ≤ L2, 40
    calibration sites per level, joint budget 0.10 per certificate.
    ``mode`` is ``interp`` (interpolation certificate only) or ``2cert``.
    """
    sigma = noise_sigma(ds)
    crit = criterion(target, ds.axis, sigma, peak_eps, tol)
    interest = interest_predicate(sigma)
    s_seed = int(seed) + 10000
    if score == "random":
        sb = RandomScore(s_seed)
    elif score == "sibson_disagreement":
        sb = DisagreementScore()
    elif score == "logistic":
        sb = LogisticInterpScore(loo_seed=s_seed)
    elif score == "gp_fail" and interp_model.startswith("gp_"):
        sb = None   # set with the GP below
    else:
        raise ValueError(f"unknown score {score!r}")
    predictor = SpectrumRoute(crit, images=None, nn_method=nn_method)
    if interp_model.startswith("gp_"):
        from accountable.gp import gp_protocol
        predictor, sb = gp_protocol(ds, crit, interp_model[3:], **(gp_kwargs or {}))
        if score == "gp_fail":
            from accountable.gp import GPFailProbScore
            sb = GPFailProbScore(predictor.engine, crit, seed=int(seed) + 20000)
    certs = []
    if mode == "2cert":
        sa = RandomScore(s_seed + 1) if score == "random" else \
            LogisticInterestScore(interest, Q200, Q200_HALF, seed=s_seed)
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
    elif policy == "ltt_conditional":
        pol = make_policy("ltt_conditional", certificate=INTERP, alpha=eps, confidence=confidence, **kw)
    else:
        pol = make_policy(policy, **kw)
    return CampaignConfig(
        criterion=crit, predictor=predictor,
        certificates=certs, policy=pol,
        interest=interest, seed_level=2, cal_size=cal_size, rng_seed=seed, nn_method=nn_method,
    )
