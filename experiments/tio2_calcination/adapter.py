"""
Dry-run of a 4-D calcination campaign on doped TiO2 (simulated; see forward.py).

Design: a scrambled Sobol sequence in the unit 4-cube (seed 42), cut into
consecutive power-of-two blocks that serve as levels L0-L6 with 16, 16, 32,
64, 128, 256 and 512 recipes (1024 in all). Levels 0-2 form the seed.

Truth: one synthesis realisation per recipe (rate jitter, furnace offset,
Poisson counts), reproducible from ``truth_seed``. With ``furnace="split"``
recipes share a furnace run when their rounded temperature and dwell agree.

Claims:
- interest: the site holds both anatase (101) and rutile (110) above
  5 x window noise (a mixed-phase sample);
- interpolation, ``size``: the anatase (101) width within ``FWHM_TOL`` deg
  (a crystallite-size claim), with agreement on the presence of the line;
- interpolation, ``pattern``: the whole pattern within rtol |I| + atol on
  average over channels.

Interpolation in 4-D: barycentric weights on a Delaunay triangulation
(``nn_method="delaunay"``) or a Gaussian process.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
from scipy.spatial import cKDTree
from scipy.stats import qmc

from accountable import (
    AccuracyCriterion, CampaignConfig, Certificate, Dataset, INTEREST, INTERP,
    LogisticInterpScore, RandomScore, StoredOracle, estimate_window_noise, make_policy,
    peak_descriptors,
)
from accountable.features import fit_logistic_probability
from accountable.scores import Score
from accountable.sibson import interpolate

from . import forward as F

A_HALF = R_HALF = 1.0
SMOOTH = 11               # Savitzky-Golay window (bins of 0.02 deg) before peak descriptors
PRESENCE_C = 5.0
FWHM_TOL = 0.08            # deg 2theta; above the noise floor of the width (q90 0.03 deg)
RTOL = 0.10
ATOL_SIGMA = 2.0
SIGNAL_MIN = 600.0        # counts; the pattern claim averages over channels with predicted signal above this
BLOCKS = (16, 16, 32, 64, 128, 256, 512)


def design(seed: int = 42):
    pts = qmc.Sobol(4, scramble=True, seed=seed).random(sum(BLOCKS))
    levels = np.concatenate([np.full(b, L) for L, b in enumerate(BLOCKS)])
    return pts, levels


def furnace_keys(u, mode: str):
    if mode == "per_sample":
        return None
    r = F.recipe(u)
    return np.column_stack([np.round(r["T"] / 25.0) * 25.0, np.round(np.log2(r["t"]))])


@lru_cache(maxsize=4)
def load(truth_seed: int = 0, furnace: str = "per_sample", design_seed: int = 42) -> Dataset:
    pts, levels = design(design_seed)
    I, st = F.realise(pts, seed=truth_seed, furnace_key=furnace_keys(pts, furnace))
    ds = Dataset(name="tio2_calcination", points=pts, levels=levels, oracle=StoredOracle(I),
                 axis=F.axis(), axis_unit="deg 2theta",
                 meta=dict(state=st, furnace=furnace, truth_seed=truth_seed))
    return ds


def noise_sigma(ds) -> float:
    """Counting noise from a reflection-free window (30-34 deg)."""
    I = ds.oracle.truth(np.arange(ds.n))
    return float(estimate_window_noise(I, ds.axis, 32.0, 2.0)["sigma"])


def _present(I, q, center, half, sigma):
    from scipy.signal import savgol_filter
    I = savgol_filter(np.atleast_2d(np.asarray(I, float)), SMOOTH, 2, axis=1)
    d = peak_descriptors(I, q, q_center=center, q_halfwidth=half)
    hab = np.asarray(d["height_above_base"], float)
    return np.asarray(d["has_peak"], bool) & np.isfinite(hab) & (hab > PRESENCE_C * sigma), np.where(np.isfinite(hab), hab, 0.0)


def rutile_fraction(I, q, sigma):
    """
    Rutile mass fraction estimated from the pattern: areas of anatase (101) and
    rutile (110) (height above baseline x width, smoothed data) with the
    intensity ratio per unit mass of the strongest reflections (1.375 from the
    structures used here; cf. the Spurr-Myers factor 1.265).
    """
    from scipy.signal import savgol_filter
    Is = savgol_filter(np.atleast_2d(np.asarray(I, float)), SMOOTH, 2, axis=1)
    out = []
    for c, h in ((F.A101, A_HALF), (F.R110, R_HALF)):
        d = peak_descriptors(Is, q, q_center=c, q_halfwidth=h)
        hab = np.asarray(d["height_above_base"], float)
        fw = np.asarray(d["fwhm"], float)
        ok = np.asarray(d["has_peak"], bool) & np.isfinite(hab) & (hab > PRESENCE_C * sigma) & np.isfinite(fw)
        out.append(np.where(ok, hab * np.where(np.isfinite(fw), fw, 0.0), 0.0))
    aA, aR = out
    with np.errstate(invalid="ignore", divide="ignore"):
        w = aR / (aR + aA / 1.375)
    return np.where(aA + aR > 0, w, np.nan)


def interest_predicate(sigma: float, lo: float = 0.10, hi: float = 0.90):
    """Mixed-phase window: estimated rutile fraction between lo and hi."""
    def interest(I, q):
        w = rutile_fraction(I, q, sigma)
        return np.isfinite(w) & (w >= lo) & (w <= hi)
    return interest


class TwoLineInterestScore(Score):
    """
    P(mixed phase | features) from a logistic regression trained by leave-one-out
    on the measured set. Features: predicted heights of anatase (101) and
    rutile (110) above baseline, in units of sigma, and the distance to the
    nearest measured site.
    """

    name = "two_line_interest"

    def __init__(self, interest, sigma, seed, max_train=80):
        self.interest, self.sigma, self.seed, self.max_train = interest, float(sigma), int(seed), int(max_train)

    def _feat(self, P_src, P_query, I_hat):
        _, ha = _present(I_hat, self._ms.axis, F.A101, A_HALF, self.sigma)
        _, hr = _present(I_hat, self._ms.axis, F.R110, R_HALF, self.sigma)
        d, _ = cKDTree(P_src).query(np.asarray(P_query, float), k=1)
        s = self.sigma * PRESENCE_C
        return np.column_stack([np.log1p(ha / s), np.log1p(hr / s), np.atleast_1d(d)])

    def fit(self, ms):
        self._ms = ms
        P, I = ms.P, ms.I
        n = len(P)
        rng = np.random.default_rng(self.seed)
        order = np.arange(n) if n <= self.max_train else np.sort(rng.choice(n, self.max_train, replace=False))
        y_all = np.asarray(self.interest(I, ms.axis), bool)
        X, y = [], []
        for i in order:
            m = np.ones(n, bool)
            m[i] = False
            I_hat = interpolate(P[m], I[m], P[i:i + 1], k_fallback=ms.k_fallback, method=ms.nn_method)
            X.append(self._feat(P[m], P[i:i + 1], I_hat)[0])
            y.append(bool(y_all[i]))
        self._clf = fit_logistic_probability(np.asarray(X, float), np.asarray(y, bool))

    def score(self, points):
        points = np.asarray(points, float)
        if len(points) == 0:
            return np.zeros(0)
        ms = self._ms
        I_hat = interpolate(ms.P, ms.I, points, k_fallback=ms.k_fallback, method=ms.nn_method)
        return self._clf(self._feat(ms.P, points, I_hat))


def criterion(target: str, q, sigma: float, fwhm_tol: float = FWHM_TOL, rtol: float = RTOL,
              atol_sigma: float = ATOL_SIGMA):
    if target == "size":
        return AccuracyCriterion(
            kind="peak", q=q, q_center=F.A101, q_halfwidth=A_HALF,
            include_position=False, include_width=True, fwhm_eps=fwhm_tol,
            tol_mode="absolute", presence_sigma=sigma, presence_multiple=PRESENCE_C, q_unit="deg",
            smooth_window=SMOOTH,
        )
    if target == "pattern":
        return AccuracyCriterion(kind="envelope", rtol=rtol, atol=atol_sigma * sigma, q_unit="deg",
                                 signal_min=SIGNAL_MIN)
    raise ValueError(target)


def config(ds, *, target="size", mode="2cert", policy="nested_path", eps=0.20, confidence=0.80,
           seed=0, score="logistic", interp_model="delaunay", cal_size=40, fwhm_tol=FWHM_TOL,
           rtol=RTOL, atol_sigma=ATOL_SIGMA, gp_kwargs=None) -> CampaignConfig:
    from accountable import SpectrumRoute
    sigma = noise_sigma(ds)
    crit = criterion(target, ds.axis, sigma, fwhm_tol, rtol, atol_sigma)
    interest = interest_predicate(sigma)
    s_seed = int(seed) + 10000
    predictor = SpectrumRoute(crit, images=None, nn_method="delaunay")
    if score == "random":
        sb = RandomScore(s_seed)
    else:
        sb = LogisticInterpScore(loo_seed=s_seed)
    if interp_model.startswith("gp_"):
        from accountable.gp import gp_protocol
        predictor, sb_gp = gp_protocol(ds, crit, interp_model[3:], **(gp_kwargs or {}))
        if score != "random":
            sb = sb_gp
    certs = []
    if mode == "2cert":
        sa = RandomScore(s_seed + 1) if score == "random" else TwoLineInterestScore(interest, sigma, s_seed)
        certs.append(Certificate(INTEREST, sa))
    certs.append(Certificate(INTERP, sb))
    names = [c.name for c in certs]
    if policy == "nested_path":
        pol = make_policy("nested_path", budget=eps, confidence=confidence)
    elif policy == "priority_path":
        pol = make_policy("priority_path", budget=eps, confidence=confidence, order=names)
    elif policy == "separate":
        pol = make_policy("separate", budgets={nm: eps / len(names) for nm in names},
                          confidence=1 - (1 - confidence) / len(names))
    else:
        raise ValueError(policy)
    return CampaignConfig(criterion=crit, predictor=predictor, certificates=certs, policy=pol,
                          interest=interest, seed_level=2, cal_size=cal_size, rng_seed=seed,
                          nn_method="delaunay")
