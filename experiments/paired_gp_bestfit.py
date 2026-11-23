"""Best-effort interpolation of each measured set from experiments/paired_gp_maps.py.

The sites measured by each protocol (kernel x driving cut, one design) are refitted with one common interpolator (BESTFIT_NU=0.5 fixes the smoothness):
presence by a Gaussian-process classifier, log width by a Gaussian-process regression with fitted white noise; both
with a Matern kernel whose smoothness (nu = 1/2, 3/2, 5/2) is chosen by log marginal likelihood. Reference: the same
fit on every design site. Output: results/revision2/paired_gp_bestfit_d<D>.npz

    PYTHONPATH=$PWD:$PWD/src python experiments/paired_gp_bestfit.py DESIGN
"""
import os
import sys
from pathlib import Path

import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier, GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel as C, Matern, WhiteKernel

from experiments.uncertified_gp import TOL

NUS = tuple(float(v) for v in os.environ.get("BESTFIT_NU", "0.5,1.5,2.5").split(","))
SUFFIX = "" if len(NUS) > 1 else f"_nu{NUS[0]:g}"
TAGS = [f"{k}_{d}" for k in ("fitted", "nugget", "smooth") for d in ("uq", "contract")]


def best_presence(X, y, Xf):
    if y.all() or (~y).all():
        return np.full(len(Xf), float(y[0])), None
    best = None
    for nu in NUS:
        g = GaussianProcessClassifier(C(1.0) * Matern(0.5, (0.05, 20.0), nu=nu), n_restarts_optimizer=2,
                                      random_state=0).fit(X, y)
        if best is None or g.log_marginal_likelihood_value_ > best.log_marginal_likelihood_value_:
            best = g
    return best.predict_proba(Xf)[:, 1], best


def best_width(X, lw, Xf):
    best = None
    for nu in NUS:
        k = C(1.0) * Matern(0.5, (0.05, 20.0), nu=nu) + WhiteKernel(0.1, (1e-5, 10.0))
        g = GaussianProcessRegressor(k, normalize_y=True, n_restarts_optimizer=3, random_state=0).fit(X, lw)
        if best is None or g.log_marginal_likelihood_value_ > best.log_marginal_likelihood_value_:
            best = g
    return np.exp(best.predict(Xf)), best


def main(design):
    sys.path.insert(0, "manuscript/figures")
    from fig_datasets import nacl_fwhm
    from experiments.nacl_saxs.adapter import load
    _, grid = load()
    xy_all = np.asarray(grid["xy_mm"], float)
    img, pres, (xs, ys), _, _ = nacl_fwhm()
    R = dict(np.load(f"results/revision2/paired_gp_maps_d{design}.npz"))
    ix, iy, ridx = R["ix"], R["iy"], R["raster_idx"]
    w_all, p_all = img[iy, ix], pres[iy, ix]
    xy, w, p = xy_all[ridx], w_all[ridx], p_all[ridx]
    out = dict(R)
    sets = {t: R[f"{t}_measured"] for t in TAGS}
    sets["all"] = np.ones(len(ridx), bool)
    for t, meas in sets.items():
        ph, gc = best_presence(xy[meas], p[meas], xy_all)
        ok = meas & p & np.isfinite(w)
        wh, gr = best_width(xy[ok], np.log(w[ok]), xy_all)
        out[f"{t}_bph"], out[f"{t}_bwh"] = ph, wh
        line = ph >= 0.5
        err = np.where(line, (~p_all) | (np.abs(wh - np.nan_to_num(w_all, nan=1e9)) > TOL), p_all)
        out[f"{t}_bkern"] = np.array([str(gc.kernel_) if gc else "", str(gr.kernel_)])
        print(t, int(meas.sum()), "raster off", round(float(err.mean()), 3),
              "| presence", gc.kernel_ if gc else "-", "| width", gr.kernel_, flush=True)
    np.savez_compressed(f"results/revision2/paired_gp_bestfit_d{design}{SUFFIX}.npz", **out)


if __name__ == "__main__":
    main(int(sys.argv[1]))
