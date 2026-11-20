"""
Few-days pilot: the furnace run is the unit of decision.

A furnace run is one temperature and one dwell time, and it carries a fixed tray of
eight crucibles (A-Lab trays hold up to eight samples). The tray is the same in every
run: dopant fraction {0, 0.02, 0.05, 0.10} x rutile seed {0, 0.03}. The design is over
the two furnace variables only, so the exact two-dimensional natural-neighbour
interpolant of the paper applies, and a skip saves a whole furnace run.

Design: scrambled Sobol in (temperature, dwell), 128 runs in power-of-two blocks used as
levels L0-L4 with 8, 8, 16, 32, 64 runs; L0-L1 are the seed. Temperature 500-1000 degC,
dwell 1-4 h (log scale), 1024 recipes in all.

A site's "spectrum" is the eight patterns of its tray side by side. Claims at run level:
- interest: some crucible of the run is mixed phase (rutile fraction 0.1-0.9);
- size: every crucible's anatase (101) width is predicted within tolerance;
- pattern: every crucible's whole pattern is predicted within tolerance.

``schedule`` turns a campaign into furnace waves and days.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
from scipy.spatial import cKDTree
from scipy.stats import qmc

from accountable import (
    AccuracyCriterion, CampaignConfig, Certificate, Dataset, INTEREST, INTERP,
    LogisticInterpScore, RandomScore, StoredOracle, make_policy,
)
from accountable.features import fit_logistic_probability
from accountable.scores import Score
from accountable.sibson import interpolate

from . import adapter as A
from . import forward as F

TRAY = [(c, s) for s in (0.0, 0.03) for c in (0.0, 0.02, 0.05, 0.10)]
N_SLOTS = len(TRAY)
BLOCKS = (8, 8, 16, 32, 64)
DWELL_MAX_LOG2 = 2.0          # 1-4 h
SIZE_TOL = 0.12               # deg; about 25 % of last-level runs fail prediction from coarser levels
PATTERN_RTOL, PATTERN_ATOL_SIGMA = 0.15, 3.0


def run_design(seed: int = 7, blocks_=BLOCKS):
    v = qmc.Sobol(2, scramble=True, seed=seed).random(sum(blocks_))
    levels = np.concatenate([np.full(b, L) for L, b in enumerate(blocks_)])
    return v, levels


def recipes(v):
    """Unit-cube recipes (n_runs * 8, 4) for run coordinates v (n_runs, 2)."""
    n = len(v)
    u = np.zeros((n * N_SLOTS, 4))
    for i in range(n):
        for j, (c, s) in enumerate(TRAY):
            u[i * N_SLOTS + j] = [v[i, 0], v[i, 1] * DWELL_MAX_LOG2 / 4.0, c / 0.10, s / 0.05]
    return u


TRAY_V2 = [(c, b) for b in (0.0, 0.3) for c in (0.0, 0.02, 0.05, 0.10)]   # alumina x P25 blend


@lru_cache(maxsize=4)
def load(truth_seed: int = 0, design_seed: int = 7, blocks_=BLOCKS, model: str = "v1") -> Dataset:
    v, levels = run_design(design_seed, tuple(blocks_))
    run_id = np.repeat(np.arange(len(v)), N_SLOTS)
    if model == "v2":
        from . import forward_v2 as V2
        u = np.zeros((len(v) * N_SLOTS, 4))
        for i in range(len(v)):
            for j, (c, b) in enumerate(TRAY_V2):
                u[i * N_SLOTS + j] = [v[i, 0], v[i, 1] * DWELL_MAX_LOG2 / 4.0, c / 0.10, b / 0.5]
        slot = np.tile(np.arange(N_SLOTS), len(v))
        I, st = V2.realise(u, seed=truth_seed, furnace_key=run_id, slot=slot)
    else:
        u = recipes(v)
        I, st = F.realise(u, seed=truth_seed, furnace_key=run_id)
    C = I.shape[1]
    spectra = I.reshape(len(v), N_SLOTS * C)
    x = F.axis()
    axis = np.concatenate([x + 100.0 * j for j in range(N_SLOTS)])
    return Dataset(name="tio2_furnace_runs", points=v, levels=levels, oracle=StoredOracle(spectra),
                   axis=axis, axis_unit="deg 2theta (blocks)",
                   meta=dict(state=st, recipes=u, n_channels=C, truth_seed=truth_seed, model=model))


def blocks(I, n_channels):
    I = np.atleast_2d(np.asarray(I, float))
    return I.reshape(len(I), N_SLOTS, n_channels)


def noise_sigma(ds) -> float:
    C = ds.meta["n_channels"]
    I = blocks(ds.oracle.truth(np.arange(ds.n)), C).reshape(-1, C)
    from accountable import estimate_window_noise
    return float(estimate_window_noise(I, F.axis(), 32.0, 2.0)["sigma"])


def interest_predicate(sigma, n_channels):
    one = A.interest_predicate(sigma)
    x = F.axis()

    def interest(I, q=None):
        B = blocks(I, n_channels)
        return np.asarray(one(B.reshape(-1, n_channels), x), bool).reshape(len(B), N_SLOTS).any(axis=1)
    return interest


class TrayInterestScore(Score):
    """
    P(some crucible is mixed phase | features), logistic, trained by leave-one-out on
    the measured runs. Features: the largest predicted min(w, 1 - w) over the tray,
    w the rutile fraction estimated from the interpolated pattern, and the distance
    to the nearest measured run.
    """

    name = "tray_interest"

    def __init__(self, interest, sigma, n_channels, seed, max_train=60):
        self.interest, self.sigma, self.C, self.seed, self.max_train = interest, sigma, n_channels, int(seed), max_train

    def _feat(self, P_src, P_q, I_hat):
        B = blocks(I_hat, self.C)
        w = A.rutile_fraction(B.reshape(-1, self.C), F.axis(), self.sigma).reshape(len(B), N_SLOTS)
        mix = np.nanmax(np.where(np.isfinite(w), np.minimum(w, 1 - w), -1.0), axis=1)
        d, _ = cKDTree(P_src).query(np.asarray(P_q, float), k=1)
        return np.column_stack([mix, np.atleast_1d(d)])

    def fit(self, ms):
        self._ms = ms
        P, I = ms.P, ms.I
        n = len(P)
        rng = np.random.default_rng(self.seed)
        order = np.arange(n) if n <= self.max_train else np.sort(rng.choice(n, self.max_train, replace=False))
        y_all = np.asarray(self.interest(I), bool)
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


def criterion(target, sigma, size_tol=SIZE_TOL, rtol=PATTERN_RTOL, atol_sigma=PATTERN_ATOL_SIGMA):
    sub = A.criterion(target, F.axis(), sigma, fwhm_tol=size_tol, rtol=rtol, atol_sigma=atol_sigma)
    return AccuracyCriterion(kind="blocks", sub=sub, n_blocks=N_SLOTS, q_unit="deg")


def config(ds, *, target="size", mode="2cert", eps=0.20, confidence=0.80, seed=0, score="logistic",
           cal_size=12, size_tol=SIZE_TOL, rtol=PATTERN_RTOL, atol_sigma=PATTERN_ATOL_SIGMA,
           policy="nested_path") -> CampaignConfig:
    from accountable import SpectrumRoute
    sigma = noise_sigma(ds)
    C = ds.meta["n_channels"]
    crit = criterion(target, sigma, size_tol, rtol, atol_sigma)
    interest = interest_predicate(sigma, C)
    s_seed = int(seed) + 10000
    sb = RandomScore(s_seed) if score == "random" else LogisticInterpScore(loo_seed=s_seed, max_train=60)
    certs = []
    if mode == "2cert":
        sa = RandomScore(s_seed + 1) if score == "random" else TrayInterestScore(interest, sigma, C, s_seed)
        certs.append(Certificate(INTEREST, sa))
    certs.append(Certificate(INTERP, sb))
    pol = make_policy(policy, budget=eps, confidence=confidence)
    return CampaignConfig(criterion=crit, predictor=SpectrumRoute(crit, images=None, nn_method="watson"),
                          certificates=certs, policy=pol, interest=interest, seed_level=1,
                          cal_size=cal_size, rng_seed=seed, nn_method="watson")


# --------------------------------------------------------------------------- schedule
def cycle_hours(T_C, dwell_h, slow_ramp=True, tau_cool=1.8, handling_h=0.5):
    """
    One box-furnace run following the A-Lab methods: 2 degC/min to 300 degC (``slow_ramp``;
    needed when precursors decompose, not for oxide precursors), 15 degC/min to T, hold,
    natural cooling to 100 degC (Newton cooling, time constant ``tau_cool`` h: an
    assumption to be measured on the actual furnaces), plus loading and unloading.
    """
    if slow_ramp:
        up = (300.0 - 25.0) / 2.0 / 60.0 + max(T_C - 300.0, 0.0) / 15.0 / 60.0
    else:
        up = (T_C - 25.0) / 15.0 / 60.0
    cool = tau_cool * np.log((T_C - 25.0) / 75.0)
    return up + dwell_h + cool + handling_h


def waves(res, ds, pipelined=True):
    """
    Furnace waves of one campaign. Sequential: seed, then per level its calibration runs
    and afterwards the runs measured for want of a claim. Pipelined: the calibration draws
    are uniform and independent of everything measured, so every level's calibration runs
    are fired with the seed and their patterns are held back, unread, until the predictor
    and scores of that level are frozen; only the runs measured for want of a claim wait
    for the previous level.
    """
    reason = np.asarray(res.reason).astype(str)
    lv = np.asarray(ds.levels)
    s = int(res.config["seed_level"])
    Ls = range(s + 1, int(lv.max()) + 1)
    nc = [np.flatnonzero((lv == L) & (reason == "no_certificate")) for L in Ls]
    cal = [np.flatnonzero((lv == L) & (reason == "calibration")) for L in Ls]
    seed = np.flatnonzero(lv <= s)
    if pipelined:
        return [np.concatenate([seed] + cal)] + nc
    out = [seed]
    for c, n in zip(cal, nc):
        out += [c, n]
    return out


def schedule(res, ds, n_furnaces=4, pipelined=True, slow_ramp=True):
    """Total hours of one campaign: waves run one after another; within a wave, runs are
    packed onto the furnaces longest first; each wave ends with the XRD of its last tray."""
    v = np.asarray(ds.points)
    T = 500.0 + 500.0 * v[:, 0]
    t = 2.0 ** (DWELL_MAX_LOG2 * v[:, 1])
    cyc = np.array([cycle_hours(a, b, slow_ramp) for a, b in zip(T, t)])
    total, detail = 0.0, []
    for w in waves(res, ds, pipelined):
        if len(w) == 0:
            continue
        loads = np.zeros(n_furnaces)
        for c in sorted(cyc[w], reverse=True):
            loads[np.argmin(loads)] += c
        span = float(loads.max()) + N_SLOTS * 5 / 60.0
        total += span
        detail.append(dict(runs=int(len(w)), hours=round(span, 1)))
    return total, detail
