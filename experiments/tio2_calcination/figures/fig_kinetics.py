"""
Figure 7: what the measured runs still teach. Simulated calcination campaign, 30 worlds.
(a) D-efficiency of the measured runs relative to the full design, per world and arm.
(b) Standard errors of the four activation energies relative to the full design.
(c, d) How often each run of the certified levels was measured, by the size-claim campaign and by
the kinetics-optimal subset; lines: temperature of half conversion of the native powder and of
the powder with 10 wt% alumina.

    python manuscript/figures/fig_kinetics.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from experiments.tio2_calcination import furnace as FU  # noqa: E402
from experiments.tio2_calcination import forward_v2 as V  # noqa: E402
from experiments.tio2_calcination import inverse as INV  # noqa: E402
from experiments.tio2_calcination.inverse_uniform import t50  # noqa: E402
import experiments.tio2_calcination.inverse_uniform as IU  # noqa: E402

FIG = Path(__file__).resolve().parent
INK, INK2, GRID = "#0b0b0b", "#52514e", "#8a8984"
BLUE, ORANGE, AQUA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#7b5cc4"
plt.rcParams.update({"font.size": 8, "font.family": "DejaVu Sans", "axes.edgecolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK})
ARMS = [("random", "random\nsubset", INK2), ("size", "size\nclaim", BLUE), ("pattern", "pattern\nclaim", ORANGE),
        ("oracle", "kinetics-\noptimal", AQUA)]
EIDX = (1, 3, 6, 8)
ENAMES = ["surface\nnucleation", "contact\ngrowth", "anatase\ncoarsening", "rutile\ncoarsening"]


def main():
    R = [json.loads(p.read_text()) for p in sorted((ROOT / "results/tio2/kinetics_worlds").glob("w*.json"))]
    v, levels = FU.run_design(7, (8, 8, 16, 32))
    T = 500 + 500 * v[:, 0]
    dwell = 2.0 ** (FU.DWELL_MAX_LOG2 * v[:, 1])
    fig = plt.figure(figsize=(7.2, 4.9), facecolor="white")
    gs = fig.add_gridspec(2, 2, left=0.08, right=0.90, top=0.94, bottom=0.08, wspace=0.28, hspace=0.42)
    rng = np.random.default_rng(1)

    # (a) D-efficiency
    ax = fig.add_subplot(gs[0, 0])
    for i, (a, lab, col) in enumerate(ARMS):
        d = np.array([r["arms"][a]["d_eff"] for r in R])
        ax.plot(i + rng.uniform(-0.16, 0.16, len(d)), d, "o", ms=2.8, color=col, alpha=0.75, mec="none")
        ax.plot([i - 0.28, i + 0.28], [np.median(d)] * 2, color=INK, lw=1.4)
    rd = np.array([r["arms"]["random"]["d_eff"] for r in R])
    sd = np.array([r["arms"]["size"]["d_eff"] for r in R])
    for x0, x1 in zip(rd, sd):
        ax.plot([0, 1], [x0, x1], color=GRID, lw=0.4, alpha=0.5, zorder=0)
    n = [np.mean([r["arms"][a]["n"] for r in R]) for a, _, _ in ARMS]
    ax.set_xticks(range(len(ARMS)))
    ax.set_xticklabels([f"{lab}\n{k:.0f} runs" for (_, lab, _), k in zip(ARMS, n)], fontsize=7)
    ax.set_ylabel("D-efficiency relative to all 64 runs")
    ax.set_ylim(0.4, 1.02)
    ax.set_title("(a) Information in the measured runs", loc="left", fontsize=8.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    # (b) error of the activation energies against the truth over the worlds
    ax = fig.add_subplot(gs[0, 1])
    truth = INV.theta_of(V.P)
    w = 0.16
    arms_b = [("full", "full design", GRID)] + ARMS
    for j, (a, lab, col) in enumerate(arms_b):
        err = np.array([[r["arms"][a]["theta"][k] - truth[k] for k in EIDX] for r in R])
        rmse = np.sqrt((err ** 2).mean(0))
        boot = np.array([np.sqrt((err[rng.integers(0, len(err), len(err))] ** 2).mean(0)) for _ in range(400)])
        lo, hi = np.percentile(boot, [16, 84], axis=0)
        x = np.arange(4) + (j - 2) * w
        ax.errorbar(x, rmse, yerr=[rmse - lo, hi - rmse], fmt="o", ms=3.5, color=col, lw=1.0, capsize=0,
                    label=lab.replace("-\n", "-").replace("\n", " "))
    ax.set_xticks(range(4))
    ax.set_xticklabels(ENAMES, fontsize=7)
    ax.set_ylabel("RMS error over worlds (kJ/mol)")
    ax.set_ylim(0, 48)
    ax.set_title("(b) Activation energies against the truth", loc="left", fontsize=8.5)
    ax.legend(fontsize=6.5, frameon=False, ncol=3, loc="upper left", columnspacing=0.8, handletextpad=0.2)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    # (c, d) measurement frequency on the certified levels, with the transformation front
    dw = np.geomspace(1, 4, 25)
    IU.DWELL = dw
    truth = INV.theta_of(V.P)
    fronts = [(t50(truth, 0.0), "-", "0 wt% alumina"), (t50(truth, 0.10), "--", "10 wt% alumina")]
    cert = levels >= 2
    for k, (a, title) in enumerate((("size", "(c) Measured by the size-claim campaign"),
                                    ("oracle", "(d) Chosen for the kinetics"))):
        ax = fig.add_subplot(gs[1, k])
        f = np.array([np.isin(np.arange(64), r["arms"][a]["runs"]) for r in R]).mean(0)
        sc = ax.scatter(T[cert], dwell[cert], c=f[cert], cmap="Blues", vmin=0, vmax=1, s=26,
                        edgecolors=INK2, linewidths=0.4)
        ax.scatter(T[~cert], dwell[~cert], marker="D", s=14, facecolors="none", edgecolors=INK2, linewidths=0.6)
        for tt, ls, lab in fronts:
            ax.plot(tt, dw, ls, color=ORANGE, lw=1.0)
            ax.text(tt[-1], 4.25, lab.split(" wt")[0] + " %", color=ORANGE, fontsize=6.5, va="bottom", ha="center")
        ax.set_yscale("log", base=2)
        ax.set_ylim(0.9, 4.9)
        ax.set_yticks([1, 2, 4])
        ax.set_yticklabels(["1", "2", "4"])
        ax.set_xlim(495, 1005)
        ax.set_xlabel("temperature (°C)")
        ax.set_ylabel("dwell (h)")
        ax.set_title(title, loc="left", fontsize=8.5)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    cax = fig.add_axes([0.915, 0.08, 0.012, 0.33])
    cb = fig.colorbar(sc, cax=cax)
    cb.set_label("share of worlds measured", fontsize=7)
    cb.ax.tick_params(labelsize=7)
    fig.savefig(FIG / "fig7_kinetics.png", dpi=200)
    fig.savefig(FIG / "fig7_kinetics.pdf")
    print("wrote", FIG / "fig7_kinetics.png")


if __name__ == "__main__":
    main()
