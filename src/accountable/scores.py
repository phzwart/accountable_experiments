"""
Scores order the sites of a level. They never set a guarantee.

A score is fitted on the measured set before a level's calibration draw
(``fit``), frozen for that level (``bind_level``), and read on any site of
the level (``score``). Larger means less safe to skip. Scores receive a
``MeasuredSet`` and nothing else, so they cannot see a label of the level
they score.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
from scipy.spatial import cKDTree

from .criteria import AccuracyCriterion, peak_descriptors
from .features import (
    fit_logistic_nc,
    fit_logistic_probability,
    loo_training_table,
    query_features,
)
from .sibson import ImageMap, interpolate, neighbour_weights


@dataclass
class MeasuredSet:
    """The data a score may use: measured positions, spectra and descriptors."""

    P: np.ndarray
    I: np.ndarray
    desc: Optional[dict]
    axis: np.ndarray
    criterion: AccuracyCriterion
    images: Optional[ImageMap] = None
    k_fallback: int = 5
    nn_method: str = "legacy"


class Score:
    name = "score"

    def fit(self, ms: MeasuredSet) -> None:
        self._ms = ms

    def bind_level(self, points: np.ndarray) -> None:
        pass

    def score(self, points: np.ndarray) -> np.ndarray:
        raise NotImplementedError


def _point_keys(points) -> list:
    return [tuple(np.round(p, 8)) for p in np.asarray(points, float)]


class RandomScore(Score):
    """Uniform scores from a stream independent of the calibration stream."""

    name = "random"

    def __init__(self, seed: int):
        self.rng = np.random.default_rng(int(seed))
        self._u = {}

    def bind_level(self, points):
        draws = self.rng.random(len(points))
        for key, u in zip(_point_keys(points), draws):
            self._u[key] = float(u)

    def score(self, points):
        return np.array([self._u[k] for k in _point_keys(points)], float)


class DisagreementScore(Score):
    """Neighbour disagreement in the units of the acceptance criterion."""

    name = "sibson_disagreement"

    def score(self, points):
        ms = self._ms
        X = query_features(ms.P, ms.I, points, ms.criterion, images=ms.images,
                           k_fallback=ms.k_fallback, desc_meas=ms.desc, method=ms.nn_method)
        return X[:, 0]


class LogisticInterpScore(Score):
    """
    1 − P(accept | features), fitted by leave-one-out on the measured set.
    ``loo_seed`` seeds the subsample of at most ``max_train`` training sites.
    """

    name = "logistic"

    def __init__(self, loo_seed: int, max_train: int = 120):
        self.loo_seed = int(loo_seed)
        self.max_train = int(max_train)
        self.kind = ""

    def fit(self, ms):
        self._ms = ms
        X, y = loo_training_table(
            ms.P, ms.I, ms.criterion, images=ms.images, k_fallback=ms.k_fallback,
            max_train=self.max_train, rng=np.random.default_rng(self.loo_seed),
            desc_train=ms.desc, method=ms.nn_method,
        )
        self._predict, info = fit_logistic_nc(X, y)
        self.kind = str(info.get("kind", ""))

    def score(self, points):
        ms = self._ms
        X = query_features(ms.P, ms.I, points, ms.criterion, images=ms.images,
                           k_fallback=ms.k_fallback, desc_meas=ms.desc, method=ms.nn_method)
        return np.asarray(self._predict(X), float).ravel()


class PredictedMaxScore(Score):
    """
    Interest score: the maximum of the predicted spectrum. Used where the
    interest predicate is a maximum over the spectrum reaching a level.
    """

    name = "predicted_max"

    def score(self, points):
        ms = self._ms
        I_hat = interpolate(ms.P, ms.I, points, images=ms.images, k_fallback=ms.k_fallback,
                            method=ms.nn_method)
        return I_hat.max(axis=1)


class LogisticInterestScore(Score):
    """
    P(interesting | features) for a peak, windowed when ``q_center`` is set.
    Features: predicted peak
    prominence in the window, its spread over the five nearest measured
    sites, and the distance to the nearest measured site. Trained by
    leave-one-out on the measured set.
    """

    name = "logistic_interest"

    def __init__(self, interest: Callable, q_center: Optional[float], q_half: Optional[float],
                 seed: int, max_train: int = 80):
        self.interest = interest
        self.q_center = None if q_center is None else float(q_center)
        self.q_half = None if q_half is None else float(q_half)
        self.seed = int(seed)
        self.max_train = int(max_train)

    def _prominence(self, I):
        desc = peak_descriptors(I, self._ms.axis, q_center=self.q_center,
                                q_halfwidth=self.q_half)
        hab = np.asarray(desc["height_above_base"], float)
        return np.where(np.isfinite(hab), hab, 0.0)

    def _features(self, P_src, hab_src, P_query, I_hat):
        P_query = np.asarray(P_query, float)
        prom = self._prominence(I_hat)
        tree = cKDTree(P_src)
        k = min(5, len(P_src))
        dist, nn = tree.query(P_query, k=max(k, 1))
        dist = np.asarray(dist, float)
        nn = np.asarray(nn, int)
        if dist.ndim == 1:
            dist, nn = dist[:, None], nn[:, None]
        spread = np.std(hab_src[nn], axis=1)
        return np.column_stack([prom, spread, dist[:, 0]])

    def fit(self, ms):
        self._ms = ms
        P, I = ms.P, ms.I
        self._hab = self._prominence(I)
        n = len(P)
        rng = np.random.default_rng(self.seed)
        order = np.arange(n)
        if n > self.max_train:
            order = np.sort(rng.choice(n, size=self.max_train, replace=False))
        labels = np.asarray(self.interest(I, ms.axis), bool).ravel()
        X, y = [], []
        for i in order:
            mask = np.ones(n, dtype=bool)
            mask[i] = False
            I_hat = interpolate(P[mask], I[mask], P[i:i + 1], images=ms.images,
                                k_fallback=ms.k_fallback, method=ms.nn_method)
            X.append(self._features(P[mask], self._hab[mask], P[i:i + 1], I_hat)[0])
            y.append(bool(labels[i]))
        self._clf = fit_logistic_probability(np.asarray(X, float), np.asarray(y, bool))

    def score(self, points):
        points = np.asarray(points, float)
        if len(points) == 0:
            return np.zeros(0, float)
        ms = self._ms
        I_hat = interpolate(ms.P, ms.I, points, images=ms.images, k_fallback=ms.k_fallback,
                            method=ms.nn_method)
        X = self._features(ms.P, self._hab, points, I_hat)
        return self._clf(X)


SCORES = {
    "random": RandomScore,
    "sibson_disagreement": DisagreementScore,
    "logistic": LogisticInterpScore,
    "predicted_max": PredictedMaxScore,
    "logistic_interest": LogisticInterestScore,
}
