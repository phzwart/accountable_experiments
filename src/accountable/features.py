"""
Label-free features of a query site, computed from the measured set alone.

The neighbour-disagreement feature measures how much the natural
neighbours of a site disagree with their own weighted mean, in the units
of the acceptance criterion. Leave-one-out tables on the measured set
supply training pairs (feature, accepted) for a logistic score.
"""
from __future__ import annotations

import numpy as np

from .criteria import AccuracyCriterion, slice_desc
from .sibson import NeighbourWeights, neighbour_weights

PEAK_MISMATCH_PENALTY = 10.0


def disagreement_from_weights(
    W: NeighbourWeights, I_meas: np.ndarray, crit: AccuracyCriterion, desc_meas=None,
):
    """Criterion-normalised weighted neighbour disagreement. Returns (scores, I_hat)."""
    I_meas = np.asarray(I_meas, float)
    n_q = len(W.keys)
    n_bins = I_meas.shape[1]
    scores = np.zeros(n_q, float)
    out = np.zeros((n_q, n_bins), float)
    if W.n_measured == 0 or n_q == 0:
        return scores, out
    if crit.is_peak and desc_meas is None:
        desc_meas = crit.descriptors(I_meas)
    integral = crit.kind == "integral"
    T_meas = np.trapezoid(I_meas, np.asarray(crit.q, float), axis=1) if integral else None

    def _peak_score(keys, ww, I_hat):
        d_hat = crit.descriptors(I_hat[None, :])
        hp_i = desc_meas["has_peak"][keys]
        if not bool(d_hat["has_peak"][0]):
            return float(PEAK_MISMATCH_PENALTY * ww[hp_i].sum())
        q_hat = float(d_hat["q_peak"][0])
        w_hat = float(d_hat["fwhm"][0])
        q_i = desc_meas["q_peak"][keys]
        w_i = desc_meas["fwhm"][keys]
        den_q, den_w = crit.denominators(q_hat, w_hat)
        term = np.full(len(keys), PEAK_MISMATCH_PENALTY)
        if crit.include_position:
            t_q = np.abs(q_i - q_hat) / max(float(den_q), 1e-30)
            term[hp_i] = t_q[hp_i]
        if not crit.include_width:
            return float((ww * np.minimum(term, PEAK_MISMATCH_PENALTY)).sum())
        if np.isfinite(w_hat) and w_hat > 0:
            t_w = np.abs(w_i - w_hat) / max(float(den_w), 1e-30)
            usable = hp_i & np.isfinite(w_i)
            if crit.include_position:
                term[usable] = np.maximum(term[usable], t_w[usable])
            else:
                term[usable] = t_w[usable]
        return float((ww * np.minimum(term, PEAK_MISMATCH_PENALTY)).sum())

    def _score_from_weights(keys, ww):
        ww = np.asarray(ww, float)
        ww = ww / ww.sum()
        I_hat = (ww[:, None] * I_meas[keys]).sum(axis=0)
        if crit.kind == "blocks":
            # generic: each neighbour scored against the weighted prediction by the criterion itself
            s = np.asarray(crit.stats(I_meas[keys], np.repeat(I_hat[None, :], len(keys), axis=0))["score"], float)
            return I_hat, float((ww * np.minimum(s, PEAK_MISMATCH_PENALTY)).sum())
        if crit.is_peak:
            return I_hat, _peak_score(keys, ww, I_hat)
        if integral:
            t_i = T_meas[keys]
            t_hat = float(ww @ t_i)
            spread = float(ww @ np.abs(t_i - t_hat))
            denom_t = crit.rtol * abs(t_hat) + crit.atol
            return I_hat, spread / max(denom_t, 1e-30)
        denom = crit.rtol * np.abs(I_hat) + crit.atol
        mad = np.zeros(n_bins, float)
        for j, kidx in enumerate(keys):
            mad += ww[j] * np.abs(I_meas[kidx] - I_hat)
        rho = mad / np.maximum(denom, 1e-30)
        if crit.signal_min is None:
            return I_hat, float(np.mean(rho))
        use = I_hat >= float(crit.signal_min)
        if not np.any(use):
            return I_hat, 0.0
        return I_hat, float(np.mean(rho[use]))

    for i, (keys, raw) in enumerate(zip(W.keys, W.raw)):
        out[i], scores[i] = _score_from_weights(keys, raw)
    return scores, out


def query_features(P_meas, I_meas, P_query, crit, *, images=None, k_fallback=5,
                   desc_meas=None, weights: NeighbourWeights = None, method="legacy"):
    """Features (disagreement, log1p disagreement, x, y) at query sites."""
    P_query = np.atleast_2d(np.asarray(P_query, float))
    if P_query.size == 0:
        return np.zeros((0, 2 + np.asarray(P_meas).shape[1]))
    W = weights if weights is not None else neighbour_weights(
        P_meas, P_query, images=images, k_fallback=k_fallback, method=method,
    )
    dis, _ = disagreement_from_weights(W, I_meas, crit, desc_meas)
    return np.column_stack([dis, np.log1p(np.maximum(dis, 0.0)), P_query])


def loo_training_table(P_train, I_train, crit, *, images=None, k_fallback=5,
                       max_train=120, rng=None, desc_train=None, method="legacy"):
    """(features, accepted) on the measured set by leave-one-out."""
    if rng is None:
        rng = np.random.default_rng(0)
    P_train = np.asarray(P_train, float)
    I_train = np.asarray(I_train, float)
    n = len(P_train)
    if n < 3:
        return np.zeros((0, 2 + P_train.shape[1])), np.zeros(0, dtype=bool)
    order = np.arange(n)
    if n > max_train:
        order = np.sort(rng.choice(n, size=max_train, replace=False))
    if crit.is_peak and desc_train is None:
        desc_train = crit.descriptors(I_train)
    feats, labels = [], []
    for i in order:
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        P_loo, I_loo = P_train[mask], I_train[mask]
        q = P_train[i:i + 1]
        W_interp = neighbour_weights(P_loo, q, images=images, k_fallback=k_fallback, method=method)
        I_hat = W_interp.apply(I_loo)
        env = crit.stats(I_train[i:i + 1], I_hat, desc_true=slice_desc(desc_train, slice(i, i + 1)))
        dis, _ = disagreement_from_weights(W_interp, I_loo, crit, slice_desc(desc_train, mask))
        d = float(dis[0])
        feats.append([d, np.log1p(d), *map(float, P_train[i])])
        labels.append(bool(env["score"][0] <= 1.0))
    return np.asarray(feats, float), np.asarray(labels, bool)


def fit_logistic_nc(X_train, y_safe):
    """
    Fit P(accept | x). Returns (predict_nc, info) with nc = 1 − P(accept).
    Falls back to raw disagreement when the table cannot support a fit.
    """
    from sklearn.linear_model import LogisticRegression

    X_train = np.asarray(X_train, float)
    y_safe = np.asarray(y_safe, bool)
    info = dict(kind="disagreement", n_train=len(y_safe), n_safe=int(y_safe.sum()))

    def nc_from_disagreement(X):
        return np.maximum(np.asarray(X, float)[:, 0], 0.0)

    if len(y_safe) < 8 or y_safe.sum() < 2 or (~y_safe).sum() < 2:
        return nc_from_disagreement, info
    clf = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=0)
    try:
        clf.fit(X_train, y_safe.astype(int))
    except Exception:
        return nc_from_disagreement, info
    info["kind"] = "logistic"

    def nc_from_clf(X):
        return 1.0 - clf.predict_proba(np.asarray(X, float))[:, 1]

    return nc_from_clf, info


def fit_logistic_probability(X, y):
    """P(y | x) by balanced logistic regression, constant when unfit."""
    from sklearn.linear_model import LogisticRegression

    X = np.asarray(X, float)
    y = np.asarray(y, bool)

    def constant(value):
        def predict(Z):
            return np.full(len(Z), float(value))
        return predict

    if len(y) < 8 or y.sum() < 2 or (~y).sum() < 2:
        return constant(float(y.mean()) if len(y) else 0.5)
    clf = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=0)
    try:
        clf.fit(X, y.astype(int))
    except Exception:
        return constant(float(y.mean()))

    def predict(Z):
        return clf.predict_proba(np.asarray(Z, float))[:, 1]

    return predict
