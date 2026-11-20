"""
Figure: the three datasets as maps of the quantity each claim speaks to.
(a) IR map: amide-I absorbance (maximum over 1620-1690 cm^-1, after Mie correction), 1 um pixels.
(b) NaCl scan: width (FWHM) of the (200) line, where the line is present; grey where absent.
(d) Synthetic small-angle scattering map: position of the dominant peak where a peak stands out
    (prominence of at least 5); grey elsewhere; lines: phase boundaries of the forward model.

    python manuscript/figures/fig_datasets.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from accountable import peak_descriptors  # noqa: E402
from experiments._paths import data_root  # noqa: E402
from experiments.ir_bioreef import adapter as IR  # noqa: E402
from experiments.nacl_saxs import adapter as NA  # noqa: E402
from experiments.synthetic_saxs import adapter as SA, forward as SF  # noqa: E402

FIG = Path(__file__).resolve().parent
INK, INK2 = "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 8, "font.family": "DejaVu Sans", "axes.edgecolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK})


def ir_amide():
    z = np.load(data_root() / "IR_data" / "interest_gate_um" / "prepared.npz")
    wn, C = z["wn_display"], z["corr_display"]
    m = (wn > 1620) & (wn < 1690)
    ny, nx = int(z["ny"]), int(z["nx"])
    img = np.full((ny, nx), np.nan)
    img[z["rows"], z["cols"]] = C[:, m].max(1)
    ds = IR.load()
    return img, ds


def nacl_fwhm():
    ds, grid = NA.load()
    q, I, xy = grid["q"], grid["intensity"], grid["xy_mm"]
    sigma = NA.noise_sigma(ds)
    d = peak_descriptors(I, q, q_center=NA.Q200, q_halfwidth=NA.Q200_HALF)
    hab = np.asarray(d["height_above_base"], float)
    present = np.asarray(d["has_peak"], bool) & np.isfinite(hab) & (hab > NA.PRESENCE_C * sigma)
    fw = np.where(present, np.asarray(d["fwhm"], float), np.nan)
    xs, ys = np.unique(xy[:, 0].round(4)), np.unique(xy[:, 1].round(4))
    img = np.full((len(ys), len(xs)), np.nan)
    pres = np.zeros((len(ys), len(xs)), bool)
    ix = np.searchsorted(xs, xy[:, 0].round(4))
    iy = np.searchsorted(ys, xy[:, 1].round(4))
    img[iy, ix] = fw
    pres[iy, ix] = present
    h = np.full((len(ys), len(xs)), np.nan)
    h[iy, ix] = np.where(present, hab, np.nan)
    return img, pres, (xs, ys), ds, h


def saxs_map(n=161):
    g = np.linspace(0, 1, n)
    X, Y = np.meshgrid(g, g)
    feas = X + Y <= 1
    q = SF.default_q(240)
    I = SF.saxs(X[feas], Y[feas], q)
    d = peak_descriptors(I, q)
    pr = np.asarray(d["prominence"], float)
    ok = np.asarray(d["has_peak"], bool) & np.isfinite(pr) & (pr >= SA.PROMINENCE)
    img = np.full(X.shape, np.nan)
    img[feas] = np.where(ok, np.asarray(d["q_peak"], float), np.nan)
    flat = np.full(X.shape, np.nan)
    flat[feas & ~np.isnan(img) == False] = 0.0
    flat[~feas] = np.nan
    return g, img, flat, X, Y


def main():
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.6), facecolor="white",
                            gridspec_kw=dict(wspace=0.42, hspace=0.42, left=0.08, right=0.92, top=0.94, bottom=0.08))
    axs = axs.ravel()

    def bar(im, ax, label):
        cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
        cb.set_label(label, fontsize=7)
        cb.ax.tick_params(labelsize=7)

    img, ds = ir_amide()
    ax = axs[0]
    im = ax.imshow(img, origin="lower", cmap="viridis", extent=(-0.5, img.shape[1] - 0.5, -0.5, img.shape[0] - 0.5),
                   vmin=0, vmax=np.nanpercentile(img, 99.5))
    ax.set_xlabel("x (µm)")
    ax.set_ylabel("y (µm)")
    ax.set_title("(a) IR map: amide I", loc="left", fontsize=8.5)
    bar(im, ax, "absorbance")

    img, pres, (xs, ys), ds, h = nacl_fwhm()
    ext = (xs[0], xs[-1], ys[0], ys[-1])
    for ax, data, cmap, title, lab, log in ((axs[1], h, "Blues", "(b) NaCl scan: (200) line height", "height (counts)", True),
                                            (axs[2], img, "magma_r", "(c) NaCl scan: (200) line width", "FWHM (nm$^{-1}$)", False)):
        ax.imshow(np.where(pres, np.nan, 0.0), origin="lower", cmap="Greys", vmin=-1, vmax=3, extent=ext)
        if log:
            from matplotlib.colors import LogNorm
            im = ax.imshow(data, origin="lower", cmap=cmap, extent=ext,
                           norm=LogNorm(vmin=np.nanpercentile(data, 2), vmax=np.nanpercentile(data, 99.5)))
        else:
            lo, hi = np.nanpercentile(data, [2, 98])
            im = ax.imshow(data, origin="lower", cmap=cmap, extent=ext, vmin=lo, vmax=hi)
        ax.set_xlabel("stage x (mm)")
        ax.set_ylabel("stage y (mm)")
        ax.set_title(title, loc="left", fontsize=8.5)
        bar(im, ax, lab)

    g, img, flat, X, Y = saxs_map()
    ax = axs[3]
    ax.imshow(np.where(np.isnan(img) & (X + Y <= 1), 0.0, np.nan), origin="lower", cmap="Greys", vmin=-1, vmax=3,
              extent=(0, 1, 0, 1))
    im = ax.imshow(img, origin="lower", cmap="plasma", extent=(0, 1, 0, 1))
    lab = SF.classify(X, Y).astype(float)
    lab[lab < 0] = np.nan
    ax.contour(X, Y, lab, levels=[0.5, 1.5, 2.5], colors="white", linewidths=0.6)
    ax.plot([0, 1], [1, 0], color=INK2, lw=0.8)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("oil fraction x")
    ax.set_ylabel("surfactant fraction y")
    ax.set_title("(d) Synthetic map: dominant peak", loc="left", fontsize=8.5)
    bar(im, ax, "q* (Å$^{-1}$)")
    fig.savefig(FIG / "fig_datasets.png", dpi=200)
    fig.savefig(FIG / "fig_datasets.pdf")
    print("wrote", FIG / "fig_datasets.png")


if __name__ == "__main__":
    main()
