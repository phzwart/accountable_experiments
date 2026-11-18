"""
Predictors and the interpolation-failure label.

A predictor maps a measured set to predictions at query sites. The label
F = 1{s > 1} is the acceptance score of that prediction against the truth.
Two routes share one set of natural-neighbour weights (theory §6):

- ``SpectrumRoute``: interpolate the spectra, then apply the criterion
  (full profile, dominant peak, or integrated intensity) to the prediction;
- ``ScalarRoute``: interpolate a scalar target derived from each measured
  spectrum, then score it against the true scalar.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np

from .criteria import AccuracyCriterion
from .sibson import ImageMap, neighbour_weights


class Predictor:
    """Interface. ``label`` returns (s, fail) at the query sites."""

    name = "predictor"

    def label(self, P_src, I_src, P_query, I_true, desc_true=None):
        raise NotImplementedError


@dataclass
class SpectrumRoute(Predictor):
    criterion: AccuracyCriterion
    images: Optional[ImageMap] = None
    k_fallback: int = 5
    name: str = "sibson_spectrum"
    nn_method: str = "legacy"

    def predict(self, P_src, I_src, P_query):
        W = neighbour_weights(P_src, P_query, images=self.images, k_fallback=self.k_fallback,
                              method=self.nn_method)
        return W.apply(I_src)

    def label(self, P_src, I_src, P_query, I_true, desc_true=None):
        if len(np.atleast_2d(P_query)) == 0 or np.asarray(P_query).size == 0:
            return np.zeros(0), np.zeros(0, bool)
        I_hat = self.predict(P_src, I_src, P_query)
        env = self.criterion.stats(I_true, I_hat, desc_true=desc_true)
        return np.asarray(env["score"], float), np.asarray(env["outside_mean"], bool)


@dataclass
class ScalarTarget:
    """
    A scalar derived from a spectrum, with presence. ``fn(I, axis)`` returns
    (values, present). Absent values may be NaN. Tolerance is
    ``rtol |y| + atol``; a presence disagreement scores +inf and agreed
    absence scores 0.
    """

    fn: Callable
    rtol: float = 0.0
    atol: float = 1.0
    name: str = "scalar"


@dataclass
class ScalarRoute(Predictor):
    target: ScalarTarget
    axis: np.ndarray
    images: Optional[ImageMap] = None
    k_fallback: int = 5
    name: str = "sibson_scalar"
    nn_method: str = "legacy"

    def predict(self, P_src, I_src, P_query):
        v, present = self.target.fn(np.asarray(I_src, float), self.axis)
        v = np.asarray(v, float)
        present = np.asarray(present, bool)
        W = neighbour_weights(P_src, P_query, images=self.images, k_fallback=self.k_fallback,
                              method=self.nn_method)
        p_hat = W.apply(present.astype(float))
        vals = np.where(present, v, 0.0)
        num = W.apply(vals)
        den = W.apply(present.astype(float))
        with np.errstate(invalid="ignore", divide="ignore"):
            v_hat = np.where(den > 0, num / den, np.nan)
        return v_hat, p_hat >= 0.5

    def label(self, P_src, I_src, P_query, I_true, desc_true=None):
        P_query = np.atleast_2d(np.asarray(P_query, float))
        if P_query.size == 0:
            return np.zeros(0), np.zeros(0, bool)
        v_hat, p_hat = self.predict(P_src, I_src, P_query)
        v, p = self.target.fn(np.asarray(I_true, float), self.axis)
        v = np.asarray(v, float)
        p = np.asarray(p, bool)
        s = np.zeros(len(v))
        both = p & p_hat
        den = self.target.rtol * np.abs(v[both]) + self.target.atol
        s[both] = np.abs(v_hat[both] - v[both]) / np.maximum(den, 1e-30)
        s[p != p_hat] = np.inf
        return s, s > 1.0
