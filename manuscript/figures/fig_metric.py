"""
Figure 6: where the certified metric sends the measurements. Synthetic map, tolerances matched
to equal difficulty, quantile path, 50 campaigns per metric: frequency with which each design
site of a certified level was measured because no claim covered it, under the peak metric
(left) and the profile metric (middle), and their difference (right). Thin lines: phase
boundaries of the forward model.

    python manuscript/figures/fig_metric.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.synthetic_saxs import adapter as S, forward  # noqa: E402

FIG = Path(__file__).resolve().parent
INK, INK2, GRID = "#0b0b0b", "#52514e", "#8a8984"
plt.rcParams.update({"font.size": 8, "font.family": "DejaVu Sans", "axes.edgecolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK})


def boundaries(ax):
    g = np.linspace(0, 1, 600)
    X, Y = np.meshgrid(g, g)
    lab = forward.classify(X, Y).astype(float)
    lab[lab < 0] = np.nan
    ax.contour(X, Y, lab, levels=[0.5, 1.5, 2.5], colors=GRID, linewidths=0.6)
    ax.plot([0, 1], [1, 0], color=INK2, lw=0.8)


def main():
    z = np.load(ROOT / "results/analysis/metric_sampling/synthetic_saxs.npz")
    ds = S.load()
    cand = np.flatnonzero(np.asarray(ds.candidate, bool))
    P = np.asarray(ds.points, float)[cand]
    cert = np.asarray(ds.levels)[cand] > 2
    peak, prof = z["meas_2"][cand], z["meas_3"][cand]
    vmax = max(peak[cert].max(), prof[cert].max())
    fig = plt.figure(figsize=(7.2, 2.75), facecolor="white")
    w, h, b = 0.22, 0.58, 0.17
    axs = [fig.add_axes([x, b, w, h]) for x in (0.075, 0.33, 0.66)]
    cax1 = fig.add_axes([0.555, b + 0.04, 0.010, h - 0.08])
    cax2 = fig.add_axes([0.885, b + 0.04, 0.010, h - 0.08])
    panels = [(peak, "(a) Peak claim", "Blues", 0, vmax),
              (prof, "(b) Profile claim", "Blues", 0, vmax)]
    for ax, (v, title, cmap, lo, hi) in zip(axs[:2], panels):
        sc = ax.scatter(P[cert, 0], P[cert, 1], c=v[cert], s=4, cmap=cmap, vmin=lo, vmax=hi, linewidths=0)
        ax.set_title(f"{title}\nno claim: {v[cert].sum():.0f} sites per campaign", loc="left", fontsize=8, color=INK)
    cb = fig.colorbar(sc, cax=cax1)
    cb.set_label("frequency measured", fontsize=6.5, labelpad=2)
    d = (prof - peak)[cert]
    lim = np.abs(d).max()
    sc = axs[2].scatter(P[cert, 0], P[cert, 1], c=d, s=4, cmap="RdBu_r", vmin=-lim, vmax=lim, linewidths=0)
    axs[2].set_title("(c) Profile − peak\nred: more under profile", loc="left", fontsize=8, color=INK)
    cb = fig.colorbar(sc, cax=cax2)
    cb.set_label("difference", fontsize=6.5, labelpad=2)
    for ax in axs:
        boundaries(ax)
        ax.set_xlim(-0.02, 1.02)
        ax.set_ylim(-0.02, 1.02)
        ax.set_aspect("equal")
        ax.set_xlabel("oil fraction $x$")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axs[0].set_ylabel("surfactant fraction $y$")
    for ax in axs[1:]:
        ax.set_yticklabels([])
    for c in (cax1, cax2):
        c.tick_params(labelsize=6)
    axs[0].text(0.08, 0.15, "L1", color=INK2, fontsize=7)
    axs[0].text(0.06, 0.55, "I1", color=INK2, fontsize=7)
    axs[0].text(0.03, 0.85, "H1", color=INK2, fontsize=7)
    axs[0].text(0.55, 0.12, "emulsion", color=INK2, fontsize=7)
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"fig6_metric.{ext}", dpi=300)
    print("wrote", FIG / "fig6_metric.png", peak[cert].sum(), prof[cert].sum())


if __name__ == "__main__":
    main()
