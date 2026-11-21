"""
Figure 6: what an agent states about its wrong skips, what happens, and what the difference costs.
Top: stated against realised share of certified-level sites skipped wrongly, for certified campaigns (bound
against mean realised rate, one point per budget) and uncertified GP campaigns (one point per alpha).
Bottom: excess cost over the cheapest available operating point, against the cost ratio r of a wrong skip to a
measurement, when each agent chooses its operating point by the cost it believes.

    python -m experiments.uncertified_all && python -m experiments.certified_budgets && \
    python -m experiments.price_of_uncertainty && python manuscript/figures/fig_price.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

FIG = Path(__file__).resolve().parent
ROOT = FIG.parents[1]
INK, INK2, GRID = "#1f1e1d", "#5c5b58", "#c9c8c4"
STYLE = {
    "certified, natural neighbour": dict(c="#2a78d6", m="D", ls="-"),
    "certified, GP": dict(c="#8e6cc8", m="s", ls="-"),
    "uncertified GP, latent sd": dict(c="#d4572a", m="o", ls="--"),
    "uncertified GP, predictive sd": dict(c="#e8a33d", m="^", ls="--"),
    "uncertified GP, recalibrated": dict(c="#9b2d1f", m="v", ls=":"),
}
NAMES = {"ir": "(a) IR amide I", "nacl": "(b) NaCl (200) width", "syn": "(c) synthetic SAXS peak"}
LO = 1e-3


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2})
    res = json.loads((ROOT / "results/uncertified/price.json").read_text())
    unc = {k: json.loads((ROOT / f"results/uncertified/{k}.json").read_text()) for k in NAMES}
    fig, axs = plt.subplots(2, 3, figsize=(7.2, 5.0), facecolor="white",
                            gridspec_kw=dict(left=0.08, right=0.98, top=0.91, bottom=0.17, wspace=0.3, hspace=0.45))
    for j, key in enumerate(NAMES):
        R = res[key]
        n_cert = unc[key][0]["n_cert"]
        ax = axs[0, j]
        ax.plot([LO, 1], [LO, 1], color=GRID, lw=0.8, zorder=0)
        for name, pts in R["points"].items():
            st = STYLE[name]
            x = np.array([max(p["S"] / n_cert, LO) for p in pts])
            y = np.array([max(p["W"] / n_cert, LO) for p in pts])
            o = np.argsort(x)
            ax.plot(x[o], y[o], color=st["c"], ls=st["ls"], lw=0.9, marker=st["m"], ms=3.5, mec="white", mew=0.4)
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlim(LO, 0.6); ax.set_ylim(LO, 0.6)
        ax.set_xlabel("stated share skipped wrongly", fontsize=7)
        if j == 0:
            ax.set_ylabel("realised share", fontsize=7)
        ax.set_title(NAMES[key], loc="left", fontsize=7.8)
        ax.tick_params(labelsize=6.3)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)

        ax = axs[1, j]
        r = np.array(R["ratios"])
        for name, c in R["curves"].items():
            st = STYLE[name]
            ax.plot(r, 1 + np.array(c["excess"]), color=st["c"], ls=st["ls"], lw=1.1)
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_ylim(0.9, 300)
        ax.axhline(1, color=GRID, lw=0.8, zorder=0)
        ax.set_xlabel("cost ratio, wrong skip : measurement", fontsize=7)
        if j == 0:
            ax.set_ylabel("cost paid / cheapest option", fontsize=7)
        ax.tick_params(labelsize=6.3)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)
    handles = [Line2D([], [], color=st["c"], ls=st["ls"], marker=st["m"], ms=4, mec="white", label=name)
               for name, st in STYLE.items()]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=6.4, frameon=False, bbox_to_anchor=(0.5, 0.0),
               columnspacing=1.2)
    fig.text(0.08, 0.965, "What an agent states about its wrong skips, what happens, and what the difference costs",
             fontsize=9, fontweight="bold", color=INK)
    fig.savefig(FIG / "fig_price.png", dpi=200)
    fig.savefig(FIG / "fig_price.pdf")
    print("wrote", FIG / "fig_price.png")


if __name__ == "__main__":
    main()
