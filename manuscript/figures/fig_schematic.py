"""
Figure 1: schematic of the workflow.
(a) hierarchical design of the IR map, one colour step per level;
(b) order of operations on one level;
(c) the two claims and the shared wrong-skip event.

    python manuscript/figures/fig_schematic.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments._paths import data_root  # noqa: E402

FIG = Path(__file__).resolve().parent
INK, INK2, SURF, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e3df"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
# sequential blue ramp, light -> dark, for levels 3..6 (seed levels drawn in ink)
RAMP = ["#b9d3f2", "#86b2e8", "#4f8fdc", "#1f5fae"]

plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "font.family": "DejaVu Sans"})


def panel_design(ax):
    z = np.load(Path(data_root()) / "IR_data" / "interest_gate_um" / "prepared.npz")
    P, lev = z["points_um"][z["pix"]], z["levels"]
    for L in range(int(lev.max()) + 1):
        m = lev == L
        if L <= 2:
            ax.scatter(P[m, 0], P[m, 1], s=16, marker="D", c=INK, lw=0, zorder=5,
                       label="Levels 0–2 (seed)" if L == 0 else None)
        else:
            ax.scatter(P[m, 0], P[m, 1], s=[14, 10, 7, 5][L - 3], c=RAMP[L - 3],
                       edgecolors=SURF, linewidths=0.4, zorder=4 - L / 10, label=f"Level {L}")
    ax.set_aspect("equal")
    ax.set_xlabel("x (µm)")
    ax.set_ylabel("y (µm)")
    ax.set_title("(a) Hierarchical design", loc="left", color=INK, fontsize=9)
    ax.legend(frameon=False, fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3,
              handletextpad=0.2, columnspacing=0.8, labelcolor=INK)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def box(ax, xy, w, h, text, fc, ec=INK2):
    b = FancyBboxPatch((xy[0] - w / 2, xy[1] - h / 2), w, h, boxstyle="round,pad=0.01,rounding_size=0.03",
                       fc=fc, ec=ec, lw=0.8)
    ax.add_patch(b)
    ax.text(xy[0], xy[1], text, ha="center", va="center", fontsize=7, color=INK, wrap=True)


def arrow(ax, a, b, **kw):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=8, color=INK2, lw=0.9, **kw))


def panel_order(ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("(b) Order of operations on level $L$", loc="left", color=INK, fontsize=9)
    steps = [
        ("1 Fit: predictor and scores\non levels $< L$", "#eef3fb"),
        ("2 Freeze: scores, predictor, rule", "#eef3fb"),
        ("3 Draw: $m$ sites of level $L$,\nuniformly", "#fdeee7"),
        ("4 Calibrate: measure the draw,\nlabels $Z$, $F$ set thresholds", "#fdeee7"),
        ("5 Decide: skip covered sites,\nmeasure the rest", "#e8f6f0"),
    ]
    ys = np.linspace(0.90, 0.10, len(steps))
    h = [0.12, 0.09, 0.12, 0.12, 0.16]
    for (t, fc), y, hh in zip(steps, ys, h):
        box(ax, (0.44, y), 0.76, hh, t, fc)
    for i in range(len(ys) - 1):
        arrow(ax, (0.44, ys[i] - h[i] / 2), (0.44, ys[i + 1] + h[i + 1] / 2))
    # loop back to the next level, routed outside the boxes
    xr = 0.90
    ax.plot([0.82, xr, xr], [ys[-1], ys[-1], ys[0]], color=INK2, lw=0.9, ls="--")
    arrow(ax, (xr, ys[0]), (0.82, ys[0]))
    ax.text(xr + 0.02, 0.5, "next level", ha="left", va="center", fontsize=6.5, color=INK2, rotation=90)


def panel_event(ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("(c) Shared wrong-skip event", loc="left", color=INK, fontsize=9)
    ax.add_patch(Ellipse((0.33, 0.58), 0.58, 0.46, fc=YELLOW, alpha=0.30, ec=YELLOW, lw=1.2))
    ax.add_patch(Ellipse((0.67, 0.58), 0.58, 0.46, fc=AQUA, alpha=0.30, ec=AQUA, lw=1.2))
    ax.text(0.20, 0.62, "$A$\nnot of\ninterest", ha="center", va="center", fontsize=6.8, color=INK)
    ax.text(0.80, 0.62, "$B$\npredictable", ha="center", va="center", fontsize=6.8, color=INK)
    ax.text(0.5, 0.60, "both", ha="center", va="center", fontsize=6.8, color=INK)
    ax.text(0.20, 0.47, "wrong if\n$Z=1$", ha="center", va="center", fontsize=6.3, color=INK2)
    ax.text(0.80, 0.47, "wrong if\n$F=1$", ha="center", va="center", fontsize=6.3, color=INK2)
    ax.text(0.5, 0.18, r"$E = (A \wedge Z) \vee (B \wedge F)$", ha="center", va="center", fontsize=8.5, color=INK)
    ax.text(0.5, 0.07, "bound: share of level-$L$ sites with $E$", ha="center", va="center",
            fontsize=6.8, color=INK2)


def main():
    fig = plt.figure(figsize=(7.2, 3.0), facecolor="white")
    panel_design(fig.add_axes([0.065, 0.30, 0.32, 0.58]))
    panel_order(fig.add_axes([0.42, 0.04, 0.29, 0.84]))
    panel_event(fig.add_axes([0.73, 0.04, 0.26, 0.84]))
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"fig1_schematic.{ext}", dpi=300)
    print("wrote", FIG / "fig1_schematic.png")


if __name__ == "__main__":
    main()
