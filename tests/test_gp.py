"""GP interpolation on the design: weights, standard deviations and length scales."""
import numpy as np
import pytest

pytest.importorskip("botorch")

from accountable.gp import GPEngine, design_spacing, gibbs_kernel  # noqa: E402


def _cloud(seed=0, n=60):
    rng = np.random.default_rng(seed)
    P = rng.random((n, 2))
    Y = np.column_stack([np.sin(3 * P[:, 0]) + P[:, 1], np.cos(2 * P[:, 1]), P[:, 0] * P[:, 1]])
    return P, Y


def _levels(P):
    # Three nested pseudo-levels by index.
    lv = np.zeros(len(P), int)
    lv[20:40] = 1
    lv[40:] = 2
    return lv


def test_weights_match_botorch_posterior_mean():
    import torch
    from botorch.models import SingleTaskGP
    from gpytorch.kernels import RBFKernel, ScaleKernel
    from gpytorch.likelihoods import GaussianLikelihood

    P, Y = _cloud()
    eng = GPEngine(mode="design", design_points=P, design_levels=_levels(P), nugget=1e-2).fit(P[:40], Y[:40, 0])
    ell = eng.info["lengthscale"]
    X = torch.as_tensor(P[:40])
    y = torch.as_tensor(Y[:40, :1] - Y[:40, :1].mean())
    k = ScaleKernel(RBFKernel())
    k.base_kernel.lengthscale = ell
    k.outputscale = 1.0
    lik = GaussianLikelihood()
    lik.noise = 1e-2
    m = SingleTaskGP(X, y, covar_module=k, likelihood=lik, outcome_transform=None)
    m.mean_module.constant.data.fill_(0.0)
    m.eval()
    Q = torch.as_tensor(P[40:])
    post = m.posterior(Q)
    mean_b = post.mean.detach().numpy().ravel() + Y[:40, 0].mean()
    var_b = post.variance.detach().numpy().ravel()
    assert np.allclose(eng.predict(Y[:40, 0], P[40:]), mean_b, atol=1e-8)
    assert np.allclose(eng.std(P[40:]) ** 2, var_b, atol=1e-8)


def test_design_lengthscale_follows_source_level():
    P, Y = _cloud()
    lv = _levels(P)
    sp = design_spacing(P, lv)
    eng = GPEngine(mode="design", design_points=P, design_levels=lv)
    eng.fit(P[:20], Y[:20])
    assert eng.info["source_level"] == 0 and np.isclose(eng.info["lengthscale"], sp[0])
    eng.fit(P[:40], Y[:40])
    assert eng.info["source_level"] == 1 and np.isclose(eng.info["lengthscale"], sp[1])
    assert sp[1] < sp[0]


def test_gibbs_kernel_is_positive_semidefinite_and_reduces_to_rbf():
    import torch
    P, _ = _cloud(1, 80)
    X = torch.as_tensor(P)
    ell = torch.as_tensor(0.05 + 0.3 * P[:, 0])
    K = gibbs_kernel(X, X, ell, ell).numpy()
    assert np.allclose(K, K.T) and np.linalg.eigvalsh(K).min() > -1e-10
    c = torch.full((80,), 0.2)
    Kc = gibbs_kernel(X, X, c, c).numpy()
    d2 = ((P[:, None] - P[None]) ** 2).sum(-1)
    assert np.allclose(Kc, np.exp(-0.5 * d2 / 0.04))


def test_nonstationary_lengthscale_is_long_where_points_are_sparse():
    rng = np.random.default_rng(3)
    dense = rng.random((80, 2)) * [0.3, 1.0]
    sparse = 0.5 + rng.random((8, 2)) * 0.5
    P = np.vstack([dense, sparse])
    eng = GPEngine(mode="nonstationary", design_points=P, design_levels=np.zeros(len(P), int)).fit(P, P[:, 0])
    ell_dense = eng._lfun(np.array([[0.15, 0.5]]))[0]
    ell_sparse = eng._lfun(np.array([[0.75, 0.75]]))[0]
    assert ell_sparse > 2 * ell_dense


def test_mle_fits_one_shared_lengthscale_and_std_vanishes_at_data():
    P, Y = _cloud(2, 70)
    eng = GPEngine(mode="mle").fit(P, Y)
    assert 0 < eng.info["lengthscale"] < 2 and eng.info["n_pc"] == 3
    assert np.all(eng.std(P) < np.sqrt(eng.info["nugget"]) + 1e-6)
    assert np.all(np.diff(eng.std(np.array([[0.5, 0.5], [2.0, 2.0], [5.0, 5.0]]))) >= -1e-12)
