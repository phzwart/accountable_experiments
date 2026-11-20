"""Natural-neighbour weights: exactness, continuity, and the legacy defect."""
import numpy as np
import pytest
from scipy.spatial import cKDTree

from accountable.sibson import neighbour_weights


def _dense(W, i, n):
    v = np.zeros(n)
    r = np.asarray(W.raw[i], float)
    v[W.keys[i]] = r / r.sum()
    return v


def _brute_force(P, q, rng, M=1_000_000, half=0.15):
    X = q + (rng.random((M, 2)) - 0.5) * 2 * half
    dP, iP = cKDTree(P).query(X)
    stolen = np.linalg.norm(X - q, axis=1) < dP
    v = np.zeros(len(P))
    ids, c = np.unique(iP[stolen], return_counts=True)
    v[ids] = c / c.sum()
    return v


def test_watson_matches_brute_force_stolen_areas():
    rng = np.random.default_rng(0)
    P = rng.random((200, 2))
    Q = rng.random((8, 2)) * 0.6 + 0.2
    W = neighbour_weights(P, Q, method="watson")
    for i, q in enumerate(Q):
        assert np.abs(_dense(W, i, len(P)) - _brute_force(P, q, rng)).max() < 0.01


@pytest.mark.parametrize("method", ["legacy", "watson"])
def test_linear_precision(method):
    rng = np.random.default_rng(1)
    P = rng.random((150, 2))
    Q = rng.random((100, 2)) * 0.8 + 0.1
    W = neighbour_weights(P, Q, method=method)
    assert np.abs(W.apply(P) - Q).max() < 1e-8


def _raster():
    g = np.linspace(0, 1, 15)
    X, Y = np.meshgrid(g, g)
    return np.column_stack([X.ravel(), Y.ravel()])


def test_watson_is_continuous_on_a_raster():
    rng = np.random.default_rng(2)
    R = _raster()
    meas = rng.random(len(R)) < 0.35
    meas[[0, 14, 210, 224]] = True
    P, Q = R[meas], R[~meas]
    Y = rng.random((len(P), 3))
    W0 = neighbour_weights(P, Q, method="watson")
    for s in range(3):
        J = np.random.default_rng(10 + s).normal(scale=1e-9, size=R.shape)
        W1 = neighbour_weights((R + J)[meas], (R + J)[~meas], method="watson")
        assert np.abs(W0.apply(Y) - W1.apply(Y)).max() < 1e-5


def test_watson_boundary_is_linear_along_the_edge():
    P = np.array([[0, 0], [0.3, 0], [1, 0], [0, 1], [1, 1], [0.5, 0.5]], float)
    W = neighbour_weights(P, np.array([[0.6, 0.0]]), method="watson")
    v = _dense(W, 0, len(P))
    assert v[1] == pytest.approx(4 / 7) and v[2] == pytest.approx(3 / 7)


def test_legacy_falls_back_to_triangle_weights():
    """
    Documented defect: the legacy clip assumes a counter-clockwise clip
    polygon; Qhull returns either orientation, and a clockwise cell clips to
    nothing and drops to barycentric weights on the enclosing triangle.
    """
    rng = np.random.default_rng(0)
    P = rng.random((200, 2))
    Q = rng.random((300, 2)) * 0.8 + 0.1
    Wl = neighbour_weights(P, Q, method="legacy")
    Ww = neighbour_weights(P, Q, method="watson")
    off = sum(np.abs(_dense(Wl, i, 200) - _dense(Ww, i, 200)).max() > 1e-6 for i in range(len(Q)))
    assert off > 0.2 * len(Q)


def test_delaunay_weights_linear_precision_4d():
    """Barycentric Delaunay weights reproduce linear functions in 4-D and sum to one."""
    from scipy.stats import qmc
    from accountable.sibson import neighbour_weights
    P = qmc.Sobol(4, scramble=True, seed=1).random(256)
    rng = np.random.default_rng(0)
    Q = 0.2 + 0.6 * rng.random((50, 4))
    a = np.array([0.3, -1.2, 2.0, 0.7])
    W = neighbour_weights(P, Q, method="delaunay")
    assert not W.fallback.any()
    y_hat = W.apply(P @ a + 0.5)
    assert np.allclose(y_hat, Q @ a + 0.5, atol=1e-9)
    assert all(abs(float(np.sum(r)) - 1.0) < 1e-12 for r in W.raw)
