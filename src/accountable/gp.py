"""
Gaussian-process interpolation on the design, with BoTorch.

The GP is an alternative to natural-neighbour weights (theory §6). It is
evaluated only at design sites, with an isotropic squared-exponential
kernel in design coordinates (the unit square of the hierarchical
design). The posterior mean is linear in the measured data,

    ŷ(x) = ȳ + w(x)ᵀ (Y − ȳ),   w(x) = (K + ν I)⁻¹ k(x),

so one set of weights serves full spectra and derived scalars alike, as
the natural-neighbour weights do. The posterior standard deviation at
unit output scale,

    σ(x)² = k(x, x) − k(x)ᵀ (K + ν I)⁻¹ k(x),

depends only on the positions, the length scale and the nugget ν. Used as
a score, it states why a site is measured: it lies far, in units of the
length scale, from what has been measured.

Three ways to set the length scale:

- ``mle``: maximise the marginal likelihood (BoTorch ``SingleTaskGP`` and
  ``fit_gpytorch_mll``) of the leading principal-component scores of the
  measured spectra, with one length scale shared by all components and a
  noise variance per component;
- ``design``: the median nearest-neighbour spacing of the design through
  the finest level present in the measured set, known before any
  measurement;
- ``nonstationary``: a Gibbs kernel whose local length scale is the
  distance to the k-th nearest measured site. An interest-driven campaign
  leaves uninteresting regions sparsely measured, so the length scale is
  long there and short where measurements cluster.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from scipy.spatial import cKDTree

MODES = ("mle", "design", "nonstationary")


def _torch():
    import torch
    torch.set_default_dtype(torch.float64)
    return torch


def design_spacing(points: np.ndarray, levels: np.ndarray, candidate: Optional[np.ndarray] = None) -> dict:
    """Median nearest-neighbour distance of the design through each level."""
    points = np.asarray(points, float)
    levels = np.asarray(levels, int)
    cand = np.ones(len(points), bool) if candidate is None else np.asarray(candidate, bool)
    out = {}
    for L in range(int(levels[cand].max()) + 1):
        P = points[cand & (levels <= L)]
        if len(P) < 2:
            continue
        d, _ = cKDTree(P).query(P, k=2)
        out[L] = float(np.median(d[:, 1]))
    return out


def gibbs_kernel(A, B, la, lb):
    """Gibbs (1997) non-stationary squared exponential in 2D, torch tensors."""
    torch = _torch()
    d2 = torch.cdist(A, B).pow(2)
    s = la[:, None].pow(2) + lb[None, :].pow(2)
    pref = 2.0 * la[:, None] * lb[None, :] / s          # (·)^{d/2} with d = 2
    return pref * torch.exp(-d2 / s)


def rbf_kernel(A, B, ell):
    torch = _torch()
    return torch.exp(-0.5 * torch.cdist(A, B).pow(2) / float(ell) ** 2)


@dataclass
class GPEngine:
    """
    Fits a GP to a measured set and returns posterior-mean weights and
    posterior standard deviations at query sites. ``fit`` caches on the
    source positions, so the predictor and the score of one level share
    one fit.
    """

    mode: str = "mle"
    design_points: Optional[np.ndarray] = None
    design_levels: Optional[np.ndarray] = None
    design_candidate: Optional[np.ndarray] = None
    nugget: float = 1e-3          # ν for the fixed modes, relative to unit output scale
    n_pc: int = 3                 # principal components used for the marginal likelihood
    k_nn: int = 3                 # neighbour rank for the non-stationary length scale
    ell_scale: float = 1.0        # multiplier on the design or local length scale
    info: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}")
        self._key = None
        if self.design_points is not None:
            self._spacing = design_spacing(self.design_points, self.design_levels, self.design_candidate)
            self._dtree = cKDTree(np.asarray(self.design_points, float))
        else:
            self._spacing = {}

    # ---------------------------------------------------------------- fit
    def _source_level(self, P_src):
        if self.design_levels is None:
            raise ValueError("design mode needs design_points and design_levels")
        d, i = self._dtree.query(P_src)
        return int(np.asarray(self.design_levels)[i].max())

    def _fit_mle(self, P_src, Y_src):
        torch = _torch()
        from botorch.optim.closures import get_loss_closure_with_grads
        from botorch.optim.fit import fit_gpytorch_mll_scipy
        from botorch.models import SingleTaskGP
        from botorch.models.transforms.outcome import Standardize
        from gpytorch.constraints import Interval
        from gpytorch.kernels import RBFKernel, ScaleKernel
        from gpytorch.mlls import ExactMarginalLogLikelihood

        Y = np.asarray(Y_src, float)
        Y = Y[:, None] if Y.ndim == 1 else Y
        Yc = Y - Y.mean(0)
        if Y.shape[1] > 1:
            U, S, _ = np.linalg.svd(Yc, full_matrices=False)
            q = int(min(self.n_pc, np.sum(S > 1e-12 * S[0]) if S[0] > 0 else 1))
            T = U[:, :q] * S[:q]
        else:
            T = Yc
        X = torch.as_tensor(P_src)
        Tt = torch.as_tensor(T)
        d_nn, _ = cKDTree(P_src).query(P_src, k=2)
        lo, hi = float(np.min(d_nn[:, 1])) / 4, 2.0
        # No batch shape on the kernel: one length scale shared by all components.
        base = RBFKernel(lengthscale_constraint=Interval(lo, hi))
        base.lengthscale = float(np.clip(np.median(d_nn[:, 1]) * 2, lo * 1.01, hi * 0.99))
        model = SingleTaskGP(X, Tt, covar_module=ScaleKernel(base),
                             outcome_transform=Standardize(m=Tt.shape[-1]))
        mll = ExactMarginalLogLikelihood(model.likelihood, model)
        # Joint (non-batched) optimisation: the length scale is shared across outputs.
        mll.train()
        params = {n: p for n, p in mll.named_parameters() if p.requires_grad}
        closure = get_loss_closure_with_grads(mll, parameters=params)
        res = fit_gpytorch_mll_scipy(mll, parameters=params, closure=closure)
        mll.eval()
        ell = float(model.covar_module.base_kernel.lengthscale.detach().reshape(-1)[0])
        os_ = model.covar_module.outputscale.detach().reshape(-1)
        noise = model.likelihood.noise.detach().reshape(-1)
        ratio = (noise / os_.expand_as(noise)).cpu().numpy()
        nu = float(np.clip(np.median(ratio), 1e-6, 1e2))
        self.info = dict(mode="mle", lengthscale=ell, nugget=nu, n_pc=int(T.shape[1]),
                         noise_to_signal=ratio.tolist(), optimiser=str(getattr(res, "status", "")))
        return ell, nu

    def fit(self, P_src, Y_src):
        P_src = np.asarray(P_src, float)
        key = (len(P_src), float(np.round(P_src.sum(), 10)), float(np.round((P_src ** 2).sum(), 10)))
        if key == self._key:
            return self
        torch = _torch()
        self._P = P_src
        self._X = torch.as_tensor(P_src)
        if self.mode == "mle":
            ell, nu = self._fit_mle(P_src, Y_src)
            self._ell = ell
            self._lfun = None
        elif self.mode == "design":
            Ls = self._source_level(P_src)
            ell = self._spacing[Ls] * self.ell_scale
            nu = self.nugget
            self._ell, self._lfun = ell, None
            self.info = dict(mode="design", lengthscale=ell, nugget=nu, source_level=Ls)
        else:
            tree = cKDTree(P_src)
            k = int(min(self.k_nn, len(P_src)))
            spacing = self._spacing or {0: float(np.median(tree.query(P_src, k=2)[0][:, 1]))}
            l_min = min(spacing.values()) * self.ell_scale
            l_max = 0.5 * float(np.sqrt(2.0))

            def lfun(Q):
                d, _ = tree.query(np.asarray(Q, float), k=k)
                d = np.asarray(d, float).reshape(len(Q), -1)[:, -1]
                return np.clip(d * self.ell_scale, l_min, l_max)

            self._lfun = lfun
            self._ell = None
            nu = self.nugget
            ls = lfun(P_src)
            self.info = dict(mode="nonstationary", nugget=nu, k_nn=k, l_min=l_min, l_max=l_max,
                             lengthscale_median=float(np.median(ls)),
                             lengthscale_range=[float(ls.min()), float(ls.max())])
        self._nu = nu
        Kss = self._k(self._X, self._X, P_src, P_src)
        n = len(P_src)
        A = Kss + nu * torch.eye(n)
        self._L = torch.linalg.cholesky(A + 1e-10 * torch.eye(n))
        self._key = key
        return self

    def _k(self, A, B, PA, PB):
        torch = _torch()
        if self._lfun is None:
            return rbf_kernel(A, B, self._ell)
        return gibbs_kernel(A, B, torch.as_tensor(self._lfun(PA)), torch.as_tensor(self._lfun(PB)))

    # ------------------------------------------------------------ queries
    def _cross(self, P_query):
        torch = _torch()
        P_query = np.atleast_2d(np.asarray(P_query, float))
        Q = torch.as_tensor(P_query)
        return self._k(Q, self._X, P_query, self._P)

    def weights(self, P_query) -> np.ndarray:
        """Posterior-mean weights, shape (n_query, n_measured)."""
        torch = _torch()
        Kqs = self._cross(P_query)
        W = torch.cholesky_solve(Kqs.T, self._L).T
        return W.cpu().numpy()

    def predict(self, Y_src, P_query) -> np.ndarray:
        Y = np.asarray(Y_src, float)
        mu = Y.mean(0)
        return mu + self.weights(P_query) @ (Y - mu)

    def std(self, P_query) -> np.ndarray:
        """Posterior standard deviation of the latent function at unit output scale."""
        torch = _torch()
        Kqs = self._cross(P_query)
        V = torch.linalg.solve_triangular(self._L, Kqs.T, upper=False)
        var = 1.0 - V.pow(2).sum(0)
        return var.clamp_min(0.0).sqrt().cpu().numpy()


# ------------------------------------------------------------ campaign parts
from .criteria import AccuracyCriterion  # noqa: E402
from .predictors import Predictor  # noqa: E402
from .scores import Score  # noqa: E402


@dataclass
class GPSpectrumRoute(Predictor):
    """Spectrum route with GP posterior-mean weights in place of natural-neighbour weights."""

    criterion: AccuracyCriterion
    engine: GPEngine
    name: str = "gp_spectrum"
    nn_method: str = "watson"   # unused; kept so the campaign can set it
    floor: float | None = 0.0   # physical lower bound; the posterior mean is clipped to it

    def predict(self, P_src, I_src, P_query):
        self.engine.fit(P_src, I_src)
        out = self.engine.predict(I_src, P_query)
        # Spectra are non-negative; clipping can only bring a prediction closer to a non-negative truth.
        return out if self.floor is None else np.maximum(out, self.floor)

    def label(self, P_src, I_src, P_query, I_true, desc_true=None):
        if np.asarray(P_query).size == 0:
            return np.zeros(0), np.zeros(0, bool)
        I_hat = self.predict(P_src, I_src, P_query)
        env = self.criterion.stats(I_true, I_hat, desc_true=desc_true)
        return np.asarray(env["score"], float), np.asarray(env["outside_mean"], bool)


class GPStdScore(Score):
    """Interpolation score: GP posterior standard deviation at unit output scale."""

    name = "gp_std"

    def __init__(self, engine: GPEngine):
        self.engine = engine

    def fit(self, ms):
        self._ms = ms
        self.engine.fit(ms.P, ms.I)

    def score(self, points):
        points = np.asarray(points, float)
        if len(points) == 0:
            return np.zeros(0, float)
        return self.engine.std(points)

    def fit_info(self) -> dict:
        return dict(self.engine.info)


def gp_protocol(ds, criterion: AccuracyCriterion, mode: str, **engine_kwargs):
    """Predictor and interpolation score sharing one GP engine on the design of ``ds``."""
    eng = GPEngine(mode=mode, design_points=ds.points, design_levels=ds.levels,
                   design_candidate=ds.candidate, **engine_kwargs)
    pred = GPSpectrumRoute(criterion, eng, name=f"gp_{mode}_spectrum")
    sc = GPStdScore(eng)
    sc.name = f"gp_{mode}_std"
    return pred, sc
