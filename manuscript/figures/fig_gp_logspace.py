"""
Display map of the Fig. 1 campaign two ways, noise-free GP with the length scale bounded below by the design
spacing. Linear: GP on the width over measured sites with the line, and a GP on the 0/1 presence indicator,
thresholded at one half (hard mask from an indicator). Log space: GP on log width over measured sites with
the line, and a GP on log height above base over all measured sites; the line is drawn where the predicted
height clears the presence threshold. Exploratory figure, not in the manuscript.

    python manuscript/figures/fig_gp_logspace.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from scipy.spatial import cKDTree

FIG = Path(__file__).resolve().parent
sys.path.insert(0, str(FIG))
from fig_hook import ROW, SEED, INK, INK2, final_map  # noqa: E402
from fig_datasets import nacl_fwhm, NA  # noqa: E402
from accountable.criteria import peak_descriptors  # noqa: E402
from experiments.record import OUT as REC, build  # noqa: E402


def gp(xy_m, y, Q, ls_min):
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
    mu, sd = y.mean(), y.std()
    g = GaussianProcessRegressor(C(1.0) * RBF(1.5 * ls_min, (ls_min, 20.0)), alpha=1e-4, n_restarts_optimizer=2,
                                 random_state=0).fit(xy_m, (y - mu) / sd)
    m, s = g.predict(Q, return_std=True)
    return m * sd + mu, s * sd, str(g.kernel_)


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": INK2})
    z = np.load(REC / ROW / "sites.npz")
    i = int(np.flatnonzero(z["seeds"] == SEED)[0])
    ds, _, _ = build(ROW, SEED, {})
    xy = np.asarray(ds.meta["xy_mm"], float)[z["site_index"]]
    measured = z["measured"][i].astype(bool)
    spacing = float(np.median(cKDTree(xy).query(xy, k=2)[0][:, 1]))

    img, pres, (xs, ys), dsn, _ = nacl_fwhm()
    _, grid = NA.load()
    d = peak_descriptors(grid["intensity"], grid["q"], q_center=NA.Q200, q_halfwidth=NA.Q200_HALF)
    hab_all = np.asarray(d["height_above_base"], float)
    thr = NA.PRESENCE_C * NA.noise_sigma(dsn)
    H = np.full(img.shape, np.nan)
    ix = np.searchsorted(xs, grid["xy_mm"][:, 0].round(4)); iy = np.searchsorted(ys, grid["xy_mm"][:, 1].round(4))
    H[iy, ix] = hab_all
    ext = (xs[0], xs[-1], ys[0], ys[-1])
    XX, YY = np.meshgrid(xs, ys)
    Q = np.c_[XX.ravel(), YY.ravel()]
    ixs = np.searchsorted(xs, xy[:, 0].round(4).clip(xs[0], xs[-1]))
    iys = np.searchsorted(ys, xy[:, 1].round(4).clip(ys[0], ys[-1]))
    w_s, p_s, h_s = img[iys, ixs], pres[iys, ixs], H[iys, ixs]
    M = measured

    lin_w, lin_p, kl = final_map(xy[M], w_s[M], p_s[M], XX, YY, noise=False, ls_min=spacing)
    ok = M & p_s & np.isfinite(w_s)
    lw, lw_sd, kw = gp(xy[ok], np.log(w_s[ok]), Q, spacing)
    lh, lh_sd, kh = gp(xy[M], np.log(np.maximum(h_s[M], 1e-3)), Q, spacing)
    log_w = np.exp(lw).reshape(XX.shape)
    log_p = (lh > np.log(thr)).reshape(XX.shape)

    tw, tp = img, pres
    def score(wm, pm):
        agree = np.mean(pm[np.isfinite(H)] == tp[np.isfinite(H)])
        both = tp & pm & np.isfinite(tw)
        rel = np.abs(wm[both] - tw[both]) / tw[both]
        return agree, np.median(rel), np.nanmin(np.where(pm, wm, np.nan)), np.nanmax(np.where(pm, wm, np.nan))
    s_lin, s_log = score(lin_w, lin_p), score(log_w, log_p)

    wlo, whi = np.nanpercentile(img, 2), np.nanpercentile(img, 98)
    grey = ListedColormap(["#ecebe7"])
    fig, axs = plt.subplots(2, 3, figsize=(7.6, 5.6), facecolor="white",
                            gridspec_kw=dict(left=0.03, right=0.97, top=0.82, bottom=0.12, wspace=0.08, hspace=0.3))
    def show(ax, w, p, title):
        ax.imshow(np.where(p, np.nan, 0.0), origin="lower", cmap=grey, extent=ext)
        im = ax.imshow(np.where(p, w, np.nan), origin="lower", cmap="Blues", vmin=wlo, vmax=whi, extent=ext,
                       interpolation="nearest")
        ax.contour(XX, YY, pres.astype(float), levels=[0.5], colors=INK, linewidths=0.4)
        ax.set_title(title, fontsize=7.4, loc="left"); ax.set_xticks([]); ax.set_yticks([])
        return im
    im = show(axs[0, 0], tw, tp, "truth: (200) width")
    show(axs[0, 1], lin_w, lin_p, f"linear width, indicator mask\nrange {s_lin[2]:.3f}–{s_lin[3]:.3f}, "
         f"median error {100 * s_lin[1]:.0f} %")
    show(axs[0, 2], log_w, log_p, f"log width, log-height mask\nrange {s_log[2]:.3f}–{s_log[3]:.3f}, "
         f"median error {100 * s_log[1]:.0f} %")
    # presence evidence
    hl = np.log(H)
    vlo, vhi = np.nanpercentile(hl, 2), np.nanpercentile(hl, 98)
    a = axs[1, 0]; im2 = a.imshow(hl, origin="lower", cmap="Greys", vmin=vlo, vmax=vhi, extent=ext)
    a.contour(XX, YY, hl, levels=[np.log(thr)], colors="#c0392b", linewidths=0.6)
    a.set_title("truth: log height above base\nred: presence threshold", fontsize=7.4, loc="left")
    a = axs[1, 1]
    from sklearn.gaussian_process import GaussianProcessRegressor  # noqa: F401
    a.imshow(lin_p.astype(float), origin="lower", cmap="Greys", vmin=-0.2, vmax=1.2, extent=ext)
    a.contour(XX, YY, pres.astype(float), levels=[0.5], colors=INK, linewidths=0.4)
    a.set_title(f"indicator GP > 1/2\nagreement with truth {100 * s_lin[0]:.1f} %", fontsize=7.4, loc="left")
    a = axs[1, 2]
    a.imshow(lh.reshape(XX.shape), origin="lower", cmap="Greys", vmin=vlo, vmax=vhi, extent=ext)
    a.contour(XX, YY, lh.reshape(XX.shape), levels=[np.log(thr)], colors="#c0392b", linewidths=0.6)
    a.contour(XX, YY, pres.astype(float), levels=[0.5], colors=INK, linewidths=0.4)
    a.set_title(f"GP on log height, red: threshold\nagreement with truth {100 * s_log[0]:.1f} %", fontsize=7.4,
                loc="left")
    for a in axs[1]:
        a.set_xticks([]); a.set_yticks([])
    cax = fig.add_axes([0.35, 0.06, 0.3, 0.018])
    cb = fig.colorbar(im, cax=cax, orientation="horizontal"); cb.ax.tick_params(labelsize=6.2)
    cb.set_label("(200) width, nm$^{-1}$ (top row); grey: no line; black outline: true edge", fontsize=6.6)
    fig.text(0.03, 0.95, f"Display map of the Fig. 1 campaign, noise-free GP, length scale ≥ {spacing:.2f} mm",
             fontsize=9.5, fontweight="bold", color=INK)
    fig.text(0.03, 0.91, f"{int(M.sum())} measured sites.  Kernels: linear {kl[0]}; log width {kw}; log height {kh}",
             fontsize=6.4, color=INK2)
    fig.savefig(FIG / "fig_gp_logspace.png", dpi=200)
    print("linear", s_lin, "\nlog", s_log, "\n", kl, kw, kh)


if __name__ == "__main__":
    main()
