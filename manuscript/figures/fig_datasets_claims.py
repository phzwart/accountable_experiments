"""
Figure 3: the three datasets and what their claims accept and reject.
Each row is one dataset: the map of the quantity the claims speak to, a site whose prediction the claim
accepts, and one it rejects (black: measured truth; orange dashed: prediction from the coarser levels;
grey: the natural neighbours that enter it; blue band: the tolerance).

    python manuscript/figures/fig_datasets_claims.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm

FIG = Path(__file__).resolve().parent
sys.path.insert(0, str(FIG))
import fig_claims as FC  # noqa: E402
import fig_datasets as FD  # noqa: E402

INK, INK2 = FD.INK, FD.INK2


def main():
    fig, axs = plt.subplots(3, 3, figsize=(7.2, 7.4), facecolor="white",
                            gridspec_kw=dict(hspace=0.62, wspace=0.62, left=0.07, right=0.99, top=0.95,
                                             bottom=0.07, width_ratios=[1.05, 1, 1]))

    def bar(im, ax, label):
        cb = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.03)
        cb.set_label(label, fontsize=6.5)
        cb.ax.tick_params(labelsize=6)

    # IR
    img, _ = FD.ir_amide()
    ax = axs[0, 0]
    im = ax.imshow(img, origin="lower", cmap="viridis", extent=(-0.5, img.shape[1] - 0.5, -0.5, img.shape[0] - 0.5),
                   vmin=0, vmax=np.nanpercentile(img, 99.5))
    ax.set_xlabel("x (µm)"); ax.set_ylabel("y (µm)")
    ax.set_title("(a) IR map: amide I", loc="left", fontsize=8)
    bar(im, ax, "absorbance")
    FC.ir_panels(axs[0, 1:])

    # NaCl
    _, pres, (xs, ys), _, h = FD.nacl_fwhm()
    ext = (xs[0], xs[-1], ys[0], ys[-1])
    ax = axs[1, 0]
    ax.imshow(np.where(pres, np.nan, 0.0), origin="lower", cmap="Greys", vmin=-1, vmax=3, extent=ext)
    im = ax.imshow(h, origin="lower", cmap="Blues", extent=ext,
                   norm=LogNorm(vmin=np.nanpercentile(h, 2), vmax=np.nanpercentile(h, 99.5)))
    ax.set_xlabel("stage x (mm)"); ax.set_ylabel("stage y (mm)")
    ax.set_title("(d) NaCl scan: (200) line height", loc="left", fontsize=8)
    bar(im, ax, "counts")
    FC.nacl_panels(axs[1, 1:])

    # synthetic
    _, img, _, X, Y = FD.saxs_map()
    ax = axs[2, 0]
    ax.imshow(np.where(np.isnan(img) & (X + Y <= 1), 0.0, np.nan), origin="lower", cmap="Greys", vmin=-1, vmax=3,
              extent=(0, 1, 0, 1))
    im = ax.imshow(img, origin="lower", cmap="plasma", extent=(0, 1, 0, 1))
    lab = FD.SF.classify(X, Y).astype(float)
    lab[lab < 0] = np.nan
    ax.contour(X, Y, lab, levels=[0.5, 1.5, 2.5], colors="white", linewidths=0.6)
    ax.plot([0, 1], [1, 0], color=INK2, lw=0.8)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("oil fraction x"); ax.set_ylabel("surfactant fraction y")
    ax.set_title("(g) Synthetic map: dominant peak", loc="left", fontsize=8)
    bar(im, ax, "q* (Å$^{-1}$)")
    FC.saxs_panels(axs[2, 1:])

    titles = {(0, 1): "(b) accepted: within\n     the envelope", (0, 2): "(c) rejected: outside\n     the envelope",
              (1, 1): "(e) accepted: width\n     within tolerance", (1, 2): "(f) rejected: width off\n     by twice the tolerance",
              (2, 1): "(h) accepted: peak\n     within tolerance", (2, 2): "(i) rejected: peak width\n     outside tolerance"}
    for (r, c), t in titles.items():
        axs[r, c].set_title(t, loc="left", fontsize=8)
        axs[r, c].tick_params(labelsize=6.5)
        axs[r, c].xaxis.label.set_size(7); axs[r, c].yaxis.label.set_size(7)
        if c == 2:
            axs[r, c].set_ylabel("")
    for r in range(3):
        axs[r, 0].tick_params(labelsize=6.5)
        axs[r, 0].xaxis.label.set_size(7); axs[r, 0].yaxis.label.set_size(7)
    leg = axs[0, 1].get_legend()
    if leg is not None:
        for t in leg.get_texts():
            t.set_fontsize(6)
    fig.savefig(FIG / "fig_datasets_claims.png", dpi=200)
    fig.savefig(FIG / "fig_datasets_claims.pdf")
    print("wrote", FIG / "fig_datasets_claims.png")


if __name__ == "__main__":
    main()
