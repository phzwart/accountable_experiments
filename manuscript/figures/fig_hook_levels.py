"""
Level by level, the campaign of Fig. 1 (NaCl (200) width, seed 44). Top: a GP fitted to every site
measured through level L (width where the line is present, a second GP on presence). Bottom: the certified
map at the spacing of level L, filled by nearest design site of levels <= L: measured widths, decision-time
predictions where skipped as predictable, grey where no line or certified as not of interest.
Exploratory figure, not in the manuscript.

    python manuscript/figures/fig_hook_levels.py
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
from fig_hook import ROOT, ROW, SEED, INK, INK2, final_map  # noqa: E402
from fig_datasets import nacl_fwhm  # noqa: E402
from experiments.record import OUT as REC, REASONS, build  # noqa: E402


def main(noise=True, design_ls=False):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2})
    z = np.load(REC / ROW / "sites.npz")
    i = int(np.flatnonzero(z["seeds"] == SEED)[0])
    ds, _, _ = build(ROW, SEED, {})
    xy = np.asarray(ds.meta["xy_mm"], float)[z["site_index"]]
    lv = np.asarray(z["levels"])
    reason = np.array(REASONS)[z["reason"][i]]
    measured, skipped = z["measured"][i].astype(bool), z["skipped"][i].astype(bool)
    e = np.load(ROOT / "results" / "hook" / "errors_s044.npz")

    img, pres, (xs, ys), _, _ = nacl_fwhm()
    ext = (xs[0], xs[-1], ys[0], ys[-1])
    XX, YY = np.meshgrid(xs, ys)
    Q = np.c_[XX.ravel(), YY.ravel()]
    ixs = np.searchsorted(xs, xy[:, 0].round(4).clip(xs[0], xs[-1]))
    iys = np.searchsorted(ys, xy[:, 1].round(4).clip(ys[0], ys[-1]))
    w_site, p_site = img[iys, ixs], pres[iys, ixs]
    nat_all = np.where(measured & p_site, w_site, np.nan)
    pr = skipped & (reason == "interpolable") & e["has_hat"]
    nat_all[pr] = e["fwhm_hat"][pr]

    wlo, whi = np.nanpercentile(img, 2), np.nanpercentile(img, 98)
    grey = ListedColormap(["#ecebe7"])
    Ls = list(range(2, int(lv.max()) + 1))
    fig, axs = plt.subplots(2, len(Ls) + 1, figsize=(2.0 * (len(Ls) + 1), 4.6), facecolor="white",
                            gridspec_kw=dict(left=0.04, right=0.99, top=0.80, bottom=0.08, wspace=0.06, hspace=0.32))

    def show(ax, w, p, title):
        ax.imshow(np.where(p, np.nan, 0.0), origin="lower", cmap=grey, extent=ext)
        im = ax.imshow(np.where(p, w, np.nan), origin="lower", cmap="Blues", vmin=wlo, vmax=whi, extent=ext,
                       interpolation="nearest")
        ax.contour(XX, YY, pres.astype(float), levels=[0.5], colors=INK, linewidths=0.4)
        ax.set_title(title, fontsize=7.2, loc="left")
        ax.set_xticks([]); ax.set_yticks([])
        return im

    im = show(axs[0, 0], img, pres, "truth")
    axs[1, 0].axis("off")
    rows = []
    for k, L in enumerate(Ls, start=1):
        upto = lv <= L
        m = measured & upto
        d, _ = cKDTree(xy[upto]).query(xy[upto], k=2)
        sp = np.median(d[:, 1])
        gw, gp, kern = final_map(xy[m], w_site[m], p_site[m], XX, YY, noise=noise,
                                 ls_min=sp if design_ls else 0.05)
        show(axs[0, k], gw, gp, f"GP through level {L}\n{int(m.sum())} measured")
        _, nn = cKDTree(xy[upto]).query(Q)
        nat = nat_all[upto][nn].reshape(XX.shape)
        show(axs[1, k], nat, np.isfinite(nat), f"certified, level {L}\n{int(upto.sum())} sites, {sp:.2f} mm")
        rows.append((L, int(m.sum()), int(upto.sum()), round(sp, 2), kern[0]))
    axs[0, 0].set_ylabel("GP display map", fontsize=7.5)
    axs[1, 1].set_ylabel("certified map", fontsize=7.5)
    cax = fig.add_axes([0.05, 0.27, 0.10, 0.025])
    cb = fig.colorbar(im, cax=cax, orientation="horizontal")
    cb.ax.tick_params(labelsize=6.2)
    cb.set_label("(200) width (nm$^{-1}$)\ngrey: no line", fontsize=6.5)
    fig.text(0.04, 0.95, "The campaign of Fig. 1, level by level (NaCl (200) width, seed 44)"
             + ("" if noise else "; GP without a noise term")
             + ("; length scale at least the level's site spacing" if design_ls else ""), fontsize=10,
             fontweight="bold", color=INK)
    fig.text(0.04, 0.91, "Top: GP fitted to the sites measured through each level.  Bottom: certified map at that "
             "level's spacing (measured or certified prediction).  Outline: edge of the true (200) signal.",
             fontsize=7.3, color=INK2)
    tag = ("" if noise else "_nonoise") + ("_designls" if design_ls else "")
    fig.savefig(FIG / f"fig_hook_levels{tag}.png", dpi=200)
    for r in rows:
        print(r)


if __name__ == "__main__":
    main(noise="--no-noise" not in sys.argv, design_ls="--design-ls" in sys.argv)
