"""
Figures for forward model v2: calibration anchors, phase maps over the furnace variables,
and simulated patterns.

    python -m experiments.tio2_calcination.figure_v2
"""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from . import calibrate_v2 as CAL
from . import forward_v2 as V

OUT = Path("results/tio2")
INK, INK2 = "#0b0b0b", "#52514e"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"


def main():
    plt.rcParams.update({"font.size": 8, "font.family": "DejaVu Sans"})
    p = V.P
    fig = plt.figure(figsize=(7.2, 7.4))
    gs = fig.add_gridspec(3, 3, hspace=0.55, wspace=0.42)

    # (a) anchors
    ax = fig.add_subplot(gs[0, :2])
    cols = {"A1": BLUE, "A2": ORANGE, "A4": AQUA}
    labels = {"A1": "coarse anatase, 4 % rutile, 6 h", "A2": "P25, 3 h", "A4": "8-nm anatase, 2 h"}
    for name, kw, tgt in CAL.ANCHORS:
        Tg = np.linspace(min(kw["T"]) - 60, max(kw["T"]) + 40, 40)
        kw2 = dict(kw)
        kw2["T"] = Tg
        f = CAL.run(p, **kw2)["f_R"]
        ax.plot(Tg, f, color=cols[name], lw=1.6, label=labels[name])
        ax.plot(kw["T"], tgt, "o", color=cols[name], ms=4, mec="white", mew=0.6)
    f3 = CAL.run(p, [700.0], 8.0, 20.0, 0.0, 5.0)["f_R"][0]
    ax.plot([700], [f3], "s", color=YELLOW, ms=5, label="20-nm anatase, 8 h, 700 °C (target ≤ 5 %)")
    ax.set_xlabel("hold temperature (°C)")
    ax.set_ylabel("rutile fraction")
    ax.set_title("(a) Anchors: literature (points), model (lines)", loc="left")
    ax.legend(frameon=False, fontsize=6.3, loc="upper left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    # (b) rutile size vs temperature
    ax = fig.add_subplot(gs[0, 2])
    Tg = np.arange(600, 1001, 25)
    st = V.integrate(Tg, 4.0, 0.0, 0.0)
    ax.plot(Tg, st["D_A"], color=BLUE, label="anatase")
    ax.plot(Tg, st["D_R"], color=ORANGE, label="rutile")
    ax.set_yscale("log")
    ax.set_xlabel("temperature (°C)")
    ax.set_ylabel("crystallite size (nm)")
    ax.set_title("(b) Sizes, 4 h", loc="left")
    ax.legend(frameon=False, fontsize=6.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    # (c) phase maps temperature x dwell for four tray positions
    combos = [(0.0, 0.0), (0.10, 0.0), (0.0, 0.3), (0.10, 0.3)]
    T = np.linspace(500, 1000, 41)
    lt = np.linspace(0, 2, 13)
    for k, (c, b) in enumerate(combos):
        ax = fig.add_subplot(gs[1, k] if k < 3 else gs[2, 0])
        TT, LL = np.meshgrid(T, lt)
        u = np.column_stack([(TT.ravel() - 500) / 500, LL.ravel() / 4.0, np.full(TT.size, c / 0.10), np.full(TT.size, b / 0.5)])
        r = V.recipe(u)
        stn = V.integrate(r["T"], r["t"], r["c"], 0.0)
        f = stn["f_R"]
        if b > 0:
            q = dataclasses.replace(p, D0_A=25.0, D_seed=40.0, r_impurity=0.17, phi_contact=1.0)
            sp = V.integrate(r["T"], r["t"], r["c"], 0.0, None, q)
            f = (1 - b) * f + b * sp["f_R"]
        im = ax.pcolormesh(T, 2 ** lt, f.reshape(TT.shape), cmap="Blues", vmin=0, vmax=1, shading="auto")
        ax.contour(T, 2 ** lt, f.reshape(TT.shape), levels=[0.1, 0.9], colors=INK2, linewidths=0.7, linestyles="--")
        ax.set_yscale("log", base=2)
        ax.set_title(f"({'cdef'[k]}) alumina {int(c * 100)} %, P25 {int(b * 100)} %", loc="left", fontsize=7.5)
        ax.set_xlabel("temperature (°C)")
        ax.set_ylabel("dwell (h)")
        if k == 3:
            fig.colorbar(im, ax=ax, label="rutile fraction", orientation="horizontal", pad=0.32, shrink=0.9)

    # (g) patterns
    ax = fig.add_subplot(gs[2, 1:])
    us = [[0.3, 0.5, 0, 0], [0.5, 0.5, 0, 0], [0.6, 0.5, 0, 0], [0.5, 0.5, 1.0, 0]]
    labs = ["650 °C", "750 °C", "800 °C", "750 °C, 10 % alumina"]
    I, st = V.realise(np.array(us), seed=3)
    x = V.axis()
    for i, (y, lab) in enumerate(zip(I, labs)):
        ax.plot(x, y + 2500 * i, lw=0.6, color=[BLUE, AQUA, ORANGE, YELLOW][i], label=f"{lab}: rutile {st['f_R'][i]:.2f}")
    ax.set_xlabel("2θ (°), Cu Kα")
    ax.set_ylabel("counts (offset)")
    ax.set_title("(g) Simulated patterns, 4 h", loc="left")
    ax.legend(frameon=False, fontsize=6.3, loc="upper right")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(OUT / "model_v2.png", dpi=200, bbox_inches="tight")
    print("wrote", OUT / "model_v2.png")


if __name__ == "__main__":
    main()
