"""
Budget policies: frozen scores and calibration labels in, thresholds and
a stated guarantee out.

Every policy sees the same ``LevelData`` and returns the same
``PolicyDecision``: one boolean cover per certificate on every site of the
level, the thresholds that produced it, and a list of ``Guarantee``
statements. A policy without a finite-sample argument says so with an
empty list. See docs/theory.md, sections 2–4.

New schemes register with ``@register("name")``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

import numpy as np
from scipy.stats import binom, hypergeom

from .tails import allowed_k

POLICIES: Dict[str, Callable] = {}


def register(name: str):
    def deco(cls):
        POLICIES[name] = cls
        cls.policy_name = name
        return cls
    return deco


def make_policy(name: str, **kwargs):
    if name not in POLICIES:
        raise KeyError(f"unknown policy {name!r}; known: {sorted(POLICIES)}")
    return POLICIES[name](**kwargs)


# ---------------------------------------------------------------- data types
@dataclass
class LevelData:
    """
    What a policy may use at one level.

    ``scores[name]`` is the frozen score of certificate ``name`` on every
    site of the level, computed before the calibration draw. ``cal`` indexes
    the calibration sites within the level. ``bad[name]`` is the bad-event
    label of that certificate on the calibration sites only.
    """

    n_level: int
    scores: Dict[str, np.ndarray]
    cal: np.ndarray
    bad: Dict[str, np.ndarray]
    caps: Dict[str, Optional[float]] = field(default_factory=dict)
    extra: Dict[str, object] = field(default_factory=dict)

    @property
    def m(self) -> int:
        return int(len(self.cal))


@dataclass
class Guarantee:
    """``rate <= budget`` holds with probability at least ``confidence``."""

    event: str          # e.g. "R_interp", "R_interest", "R_E"
    budget: float
    confidence: float
    note: str = ""

    def as_dict(self):
        return dict(event=self.event, budget=float(self.budget),
                    confidence=float(self.confidence), note=self.note)


@dataclass
class PolicyDecision:
    covers: Dict[str, np.ndarray]
    thresholds: Dict[str, float]
    k: Dict[str, int]
    guarantees: List[Guarantee]
    notes: Dict[str, str] = field(default_factory=dict)
    tails: Dict[str, dict] = field(default_factory=dict)


# ------------------------------------------------------------- primitives
def covers(score, tau: float, cap: Optional[float] = None) -> np.ndarray:
    """Sites covered at threshold tau (+inf covers every site), below an optional cap."""
    score = np.asarray(score, float).ravel()
    if np.isposinf(tau):
        out = np.ones(len(score), dtype=bool)
    elif not np.isfinite(tau):
        out = np.zeros(len(score), dtype=bool)
    else:
        out = np.isfinite(score) & (score <= float(tau))
    if cap is not None:
        out &= np.isfinite(score) & (score < float(cap))
    return out


def order_statistic_threshold(cover_scores, bad_entry, k: int, bad_mask=None) -> float:
    """
    Largest calibration cover score strictly below the (k+1)-th smallest
    bad entry. +inf when there are at most k finite bad entries; −inf when
    k < 0 or nothing lies below the boundary.

    For one certificate, ``bad_entry`` is the cover score of the bad
    calibration sites and +inf elsewhere.
    """
    cover_scores = np.asarray(cover_scores, float).ravel()
    bad_entry = np.asarray(bad_entry, float).ravel()
    k = int(k)
    if k < 0 or len(cover_scores) == 0:
        return float("-inf")
    sel = np.isfinite(bad_entry) if bad_mask is None else np.asarray(bad_mask, bool).ravel()
    fail = np.sort(bad_entry[sel])
    if len(fail) <= k:
        return float("inf")
    boundary = float(fail[k])
    below = cover_scores[cover_scores < boundary]
    if len(below) == 0:
        return float("-inf")
    return float(np.max(below))


def single_threshold(scores, bad, k):
    scores = np.asarray(scores, float)
    bad = np.asarray(bad, bool)
    return order_statistic_threshold(scores, scores, k, bad_mask=bad)


# ---------------------------------------------------------------- policies
class Policy:
    policy_name = "base"

    def decide(self, level: LevelData) -> PolicyDecision:
        raise NotImplementedError

    def describe(self) -> dict:
        return dict(policy=self.policy_name)


@register("separate")
class SeparatePolicy(Policy):
    """
    Each certificate on its own label, one shared draw (theory §4.1).

    ``budgets[name]`` is ε for that certificate. ``confidence`` applies to
    each certificate; the joint statement holds at 1 − Σ(1 − confidence).
    """

    def __init__(self, budgets: Dict[str, float], confidence: float, tail: str = "binomial"):
        self.budgets = {k: float(v) for k, v in budgets.items()}
        self.confidence = float(confidence)
        self.tail = tail

    def describe(self):
        return dict(policy=self.policy_name, budgets=self.budgets,
                    confidence=self.confidence, tail=self.tail)

    def decide(self, level: LevelData) -> PolicyDecision:
        delta = 1.0 - self.confidence
        cov, thr, ks, gs, tails = {}, {}, {}, [], {}
        for name, eps in self.budgets.items():
            td = allowed_k(eps, level.m, delta, N=level.n_level, tail=self.tail)
            s_all = level.scores[name]
            s_cal = s_all[level.cal]
            tau = single_threshold(s_cal, level.bad[name], td.k)
            cov[name] = covers(s_all, tau, level.caps.get(name))
            thr[name], ks[name], tails[name] = tau, td.k, td.as_dict()
            gs.append(Guarantee(f"R_{name}", eps, self.confidence))
        if len(self.budgets) > 1:
            gs.append(Guarantee(
                "R_E", sum(self.budgets.values()),
                1.0 - len(self.budgets) * delta,
                "union bound over the per-certificate statements",
            ))
        return PolicyDecision(cov, thr, ks, gs, tails=tails)


@register("nested_path")
class NestedPathPolicy(Policy):
    """
    One budget on the shared wrong-skip event along a label-free path
    (theory §4.2). Entry time of a site for certificate j is
    ECDF_j(S_j) / w_j over the level's frozen scores.
    """

    def __init__(self, budget: float, confidence: float,
                 weights: Optional[Dict[str, float]] = None, tail: str = "binomial"):
        self.budget = float(budget)
        self.confidence = float(confidence)
        self.weights = dict(weights or {})
        self.tail = tail

    def describe(self):
        return dict(policy=self.policy_name, budget=self.budget,
                    confidence=self.confidence, weights=self.weights, tail=self.tail)

    def entry_times(self, level: LevelData) -> Dict[str, np.ndarray]:
        out = {}
        for name, s in level.scores.items():
            s = np.asarray(s, float)
            w = float(self.weights.get(name, 1.0))
            if not (0.0 < w <= 1.0):
                raise ValueError("path weights must lie in (0, 1]")
            finite = np.isfinite(s)
            srt = np.sort(s[finite])
            ecdf = np.searchsorted(srt, s, side="right") / max(len(s), 1)
            lam = np.where(finite, ecdf / w, np.inf)
            cap = level.caps.get(name)
            if cap is not None:
                lam = np.where(finite & (s < cap), lam, np.inf)
            out[name] = lam
        return out

    def decide(self, level: LevelData) -> PolicyDecision:
        delta = 1.0 - self.confidence
        td = allowed_k(self.budget, level.m, delta, N=level.n_level, tail=self.tail)
        lam = self.entry_times(level)
        names = list(lam)
        lam_cov = np.min(np.stack([lam[n] for n in names]), axis=0)
        cal = level.cal
        lam_E_cal = np.full(len(cal), np.inf)
        for n in names:
            lam_E_cal = np.minimum(lam_E_cal, np.where(level.bad[n], lam[n][cal], np.inf))
        lam_hat = order_statistic_threshold(lam_cov[cal], lam_E_cal, td.k)
        cov = {}
        for n in names:
            if np.isposinf(lam_hat):
                cov[n] = np.isfinite(lam[n])
            elif np.isfinite(lam_hat):
                cov[n] = lam[n] <= lam_hat
            else:
                cov[n] = np.zeros(level.n_level, bool)
        # Report each certificate's threshold in its own score units.
        thr = {}
        for n in names:
            s = np.asarray(level.scores[n], float)
            c = cov[n]
            thr[n] = float(np.max(s[c])) if c.any() else float("-inf")
        return PolicyDecision(
            cov, thr, {n: td.k for n in names},
            [Guarantee("R_E", self.budget, self.confidence, "single budget, nested label-free path")],
            notes=dict(lambda_hat=str(lam_hat)),
            tails={"E": td.as_dict()},
        )


@register("ltt_conditional")
class LTTConditionalPolicy(Policy):
    """
    Fixed-sequence Learn-then-Test on the conditional rate of one
    certificate (theory §4.3). The grid is level-score quantiles from
    q0 = N_min / m, rounded up to a multiple of 0.05.
    """

    def __init__(self, certificate: str, alpha: float, confidence: float,
                 finite_population: bool = False):
        self.certificate = certificate
        self.alpha = float(alpha)
        self.confidence = float(confidence)
        self.finite_population = bool(finite_population)

    def describe(self):
        return dict(policy=self.policy_name, certificate=self.certificate,
                    alpha=self.alpha, confidence=self.confidence)

    @staticmethod
    def n_min(alpha, confidence):
        n = 1
        while (1.0 - alpha) ** n > (1.0 - confidence) + 1e-15:
            n += 1
        return n

    def decide(self, level: LevelData) -> PolicyDecision:
        name = self.certificate
        level_scores = np.asarray(level.scores[name], float)
        scores = level_scores[level.cal]
        y = np.asarray(level.bad[name], bool)
        m = len(scores)
        n_min = self.n_min(self.alpha, self.confidence)
        tau, stop = float("-inf"), "n_below_nmin"
        if m and n_min <= m:
            q0 = float(min(1.0, max(0.05, np.ceil((n_min / m) / 0.05 - 1e-12) * 0.05)))
            qs, q = [], q0
            while q < 1.0 - 1e-9:
                qs.append(float(np.round(q, 10)))
                q = float(q + 0.05)
            qs.append(1.0)
            last, stop = None, "first_not_rejected"
            for q in qs:
                t = float(np.quantile(level_scores, q))
                cert = scores <= t
                n_cert, n_false = int(cert.sum()), int((cert & y).sum())
                if n_cert < n_min:
                    stop = "n_below_nmin"
                    break
                if self.finite_population:
                    m_pop = max(level.n_level, n_cert)
                    k_fail = min(int(np.floor(self.alpha * m_pop)) + 1, m_pop)
                    p = float(hypergeom.cdf(n_false, m_pop, k_fail, n_cert))
                else:
                    p = float(binom.cdf(n_false, n_cert, self.alpha))
                if p <= (1.0 - self.confidence) + 1e-15:
                    last, stop = t, "certified_through_1"
                else:
                    stop = "first_not_rejected" if last is None else "stopped"
                    break
            tau = float("-inf") if last is None else float(last)
        cov = {n: np.zeros(level.n_level, bool) for n in level.scores}
        cov[name] = covers(level_scores, tau, level.caps.get(name))
        return PolicyDecision(
            cov, {name: tau}, {name: -1},
            [Guarantee(f"P(bad | covered)_{name}", self.alpha, self.confidence,
                       "fixed-sequence LTT, conditional rate")],
            notes={name: stop},
        )


@register("legacy_sequential")
class LegacySequentialPolicy(Policy):
    """
    The original IR rule (theory §4.4). One SSBC-corrected budget; the
    interest threshold is chosen first and the interpolation threshold
    spends what is left, on calibration sites the interest certificate
    did not cover. Thresholds are calibration scores, never ±inf, and the
    interest threshold stays below its cap. No finite-sample guarantee.
    """

    def __init__(self, eps: float, delta: float, first: str = "interest",
                 second: str = "interp", min_cal: int = 10):
        self.eps = float(eps)
        self.delta = float(delta)
        self.first, self.second = first, second
        self.min_cal = int(min_cal)

    def describe(self):
        return dict(policy=self.policy_name, eps=self.eps, delta=self.delta,
                    order=[self.first, self.second])

    @staticmethod
    def _largest_tau(scores, eligible, y_bad, rate, n_full, tau_cap=None):
        scores = np.asarray(scores, float)
        eligible = np.asarray(eligible, bool)
        y_bad = np.asarray(y_bad, bool)
        pool = scores[eligible]
        if tau_cap is not None:
            pool = pool[pool < tau_cap]
        best = None
        for tau in np.unique(pool):
            cert = eligible & (scores <= float(tau))
            n_false = int((cert & y_bad).sum())
            if n_full and n_false / n_full <= rate + 1e-15:
                best = (float(tau), n_false, int(cert.sum()))
        return best

    def decide(self, level: LevelData) -> PolicyDecision:
        from ssbc import ssbc_correct

        a, b = self.first, self.second
        sa_all = np.asarray(level.scores[a], float)
        sb_all = np.asarray(level.scores[b], float)
        cal = level.cal
        sa, sb = sa_all[cal], sb_all[cal]
        n = len(cal)
        tau_a = tau_b = float("-inf")
        note, alpha_corr = "measure_all", float("nan")
        if n >= self.min_cal:
            alpha_corr = float(ssbc_correct(alpha_target=self.eps, n=int(n),
                                            delta=self.delta, mode="beta").alpha_corrected)
            ra = self._largest_tau(sa, np.ones(n, bool), level.bad[a], alpha_corr, n,
                                   tau_cap=level.caps.get(a))
            if ra is None:
                note, left = "no_first_tau", alpha_corr
            else:
                tau_a, n_false_a, _ = ra
                left = alpha_corr - n_false_a / n
                note = "ok"
            rb = self._largest_tau(sb, sa > tau_a, level.bad[b], max(left, 0.0), n)
            if rb is None:
                note += "+no_second_tau"
            else:
                tau_b = rb[0]
        cov_a = sa_all <= tau_a
        cov_b = (~cov_a) & (sb_all <= tau_b)
        return PolicyDecision(
            {a: cov_a, b: cov_b}, {a: tau_a, b: tau_b}, {a: -1, b: -1}, [],
            notes=dict(ssbc=note, alpha_corrected=str(alpha_corr)),
        )
