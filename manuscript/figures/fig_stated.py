"""
Figure 7: what an agent states about its wrong skips and what happens.
Stated against realised share of certified-level sites skipped wrongly, for certified campaigns (the bound
against the mean realised share, one point per budget) and uncertified GP campaigns (one point per alpha).

    python -m experiments.uncertified_all && python -m experiments.certified_budgets && \
    python manuscript/figures/fig_stated.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

FIG = Path(__file__).resolve().parent
ROOT = FIG.parents[1]
RES = ROOT / "results/uncertified"
INK, INK2, GRID = "#1f1e1d", "#5c5b58", "#c9c8c4"
STYLE = {
    "certified, natural neighbour": dict(c="#2a78d6", m="D", ls="-"),
    "certified, Gaussian process": dict(c="#8e6cc8", m="s", ls="-"),
    "uncertified, predictive sd": dict(c="#e8a33d", m="^", ls="--"),
    "uncertified, rescaled sd": dict(c="#9b2d1f", m="v", ls=":"),
}
CERT = {"sibson": "certified, natural neighbour", "gp": "certified, Gaussian process"}
UNC = {"latent": "uncertified, latent sd", "predictive": "uncertified, predictive sd", "loo": "uncertified, rescaled sd"}
NAMES = {"ir": "(a) IR amide I", "nacl": "(b) NaCl (200) width", "syn": "(c) synthetic SAXS profile"}
LO = 1e-3


def series(key):
    out = {}
    for c in json.loads((RES / f"certified_{key}.json").read_text()):
        n = c["runs"][0]["n_cert"]
        out.setdefault(CERT[c["predictor"]], []).append((c["eps"], np.mean([r["wrong"] / n for r in c["runs"]])))
    for u in json.loads((RES / f"{key}.json").read_text()):
        if u["kind"] == "latent":   # leaves out the noise of a single measurement; SI 7 only
            continue
        out.setdefault(UNC[u["kind"]], []).append((u["stated_rate"], u["wrong_rate"]))
    return out


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2})
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 3.0), facecolor="white",
                            gridspec_kw=dict(left=0.08, right=0.98, top=0.84, bottom=0.30, wspace=0.3))
    for ax, key in zip(axs, NAMES):
        ax.plot([LO, 1], [LO, 1], color=GRID, lw=0.8, zorder=0)
        for name, pts in series(key).items():
            st = STYLE[name]
            x = np.array([max(p[0], LO) for p in pts]); y = np.array([max(p[1], LO) for p in pts])
            o = np.argsort(x)
            ax.plot(x[o], y[o], color=st["c"], ls=st["ls"], lw=0.9, marker=st["m"], ms=3.5, mec="white", mew=0.4)
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlim(LO, 0.6); ax.set_ylim(LO, 0.6)
        ax.set_xlabel("stated share skipped wrongly", fontsize=7)
        if key == "ir":
            ax.set_ylabel("realised share skipped wrongly", fontsize=7)
        ax.set_title(NAMES[key], loc="left", fontsize=7.8)
        ax.tick_params(labelsize=6.3)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)
    handles = [Line2D([], [], color=st["c"], ls=st["ls"], marker=st["m"], ms=4, mec="white", label=name)
               for name, st in STYLE.items()]
    fig.legend(handles=handles, loc="lower center", ncol=2, fontsize=6.4, frameon=False, bbox_to_anchor=(0.5, 0.0),
               columnspacing=1.2)
    fig.text(0.08, 0.93, "What an agent states about its wrong skips, and what happens",
             fontsize=9, fontweight="bold", color=INK)
    fig.savefig(FIG / "fig_stated.png", dpi=200)
    fig.savefig(FIG / "fig_stated.pdf")
    print("wrote", FIG / "fig_stated.png")


if __name__ == "__main__":
    main()
