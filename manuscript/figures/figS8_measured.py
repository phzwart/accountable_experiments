"""
SI figure: the record of measured sites. One replayed campaign of average cost per dataset (for NaCl, the
campaign of Fig. 1). Top: every site of the certified levels, residual of the frozen prediction (units of the
tolerance) against the margin of its interpolation score above the level's certified cut; sites left of the
cut were covered by the interpolation claim. Bottom: conformal p-values of the residuals of sites measured by
choice among the calibration residuals of their level; a score without information gives a flat histogram.

    python -m experiments.measurement_record && python manuscript/figures/figS8_measured.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

FIG = Path(__file__).resolve().parent
ROOT = FIG.parents[1]
sys.path.insert(0, str(ROOT))
from experiments.measurement_record import ROWS  # noqa: E402

INK, INK2, GRID, RED = "#1f1e1d", "#5c5b58", "#c9c8c4", "#c0392b"
COL = {"calibration": "#3d3c39", "chosen": "#2a78d6", "pred": "#1baf7a", "noint": "#eda100"}
LO, HI = 1e-2, 1e2


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2})
    S = json.loads((ROOT / "results/measurement_record/SUMMARY.json").read_text())
    fig, axs = plt.subplots(2, 3, figsize=(7.2, 5.0), facecolor="white",
                            gridspec_kw=dict(left=0.08, right=0.98, top=0.89, bottom=0.12, wspace=0.28, hspace=0.75,
                                             height_ratios=[1.25, 1]))
    rng = np.random.default_rng(0)
    for k, (row, name) in enumerate(ROWS.items()):
        d = np.load(ROOT / "results/measurement_record" / f"{row}.npz")
        c = d["level"] >= 3
        R = d["reason"]
        grp = {"pred": c & ~d["is_cal"] & np.isin(R, ["interpolable", "not_interesting+interpolable"]),
               "noint": c & (R == "not_interesting"),
               "calibration": c & d["is_cal"],
               "chosen": c & (R == "no_certificate")}
        r = d["residual"].copy()
        r = np.where(np.isinf(r), HI * 0.75, np.clip(r, LO * 1.3, HI * 0.75))
        r = r * np.exp(rng.normal(0, 0.04, len(r)))
        P = S[row]["pooled"]
        order = [("pred", "skipped as\npredictable", P["skipped_pred"]["fail"]),
                 ("calibration", "drawn at\nrandom", P["calibration"]["fail"]),
                 ("chosen", "measured\nby choice", P["chosen"]["fail"])]
        ax = axs[0, k]
        for j, (g, lab, share) in enumerate(order):
            m = grp[g]
            ax.scatter(j + rng.uniform(-0.3, 0.3, m.sum()), r[m], s=3.5, c=COL[g], linewidths=0, alpha=0.6)

        ax.axhline(1.0, color=RED, lw=0.9, zorder=1)
        ax.set_yscale("log"); ax.set_ylim(LO, HI * 2)
        ax.set_yticks([LO * 1.3, 0.1, 1, 10, HI * 0.75])
        ax.set_yticklabels(["≈0", "0.1", "1", "10", "∞"])
        ax.minorticks_off()
        ax.set_xticks(range(3)); ax.set_xticklabels([f"{o[1]}\n{100 * o[2]:.0f} % above" if o[2] >= 0.01 else f"{o[1]}\n<1 % above"
                            for o in order], fontsize=6.5)
        ax.set_xlim(-0.6, 2.6)
        if k == 0:
            ax.set_ylabel("residual (tolerances)", fontsize=7)
        ax.tick_params(labelsize=6.3)
        ax.set_title(f"({'abc'[k]}) {name}", loc="left", fontsize=7.8)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)

        # bottom: p-values of chosen sites among calibration residuals of their level
        ax = axs[1, k]
        p = d["p_resid"][grp["chosen"]]
        pc = d["p_resid"][grp["calibration"]]
        bins = np.linspace(0, 1, 11)
        ax.hist(pc, bins=bins, density=True, histtype="step", color=COL["calibration"], lw=1.0)
        ax.hist(p, bins=bins, density=True, color=COL["chosen"], alpha=0.75)
        ax.axhline(1.0, color=INK2, lw=0.6, ls=":")
        ax.set_title(f"({'def'[k]}) needed: {100 * P['chosen']['needed']:.0f} % chosen,\n"
                     f"     {100 * P['calibration']['needed']:.0f} % drawn at random", loc="left", fontsize=7.4)
        ax.set_xlabel("p-value of the residual", fontsize=7)
        if k == 0:
            ax.set_ylabel("density", fontsize=7)
        ax.tick_params(labelsize=6.3)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)

    handles = [Line2D([], [], color=RED, lw=1, label="tolerance"),
               plt.Rectangle((0, 0), 1, 1, color=COL["chosen"], alpha=0.75, label="p-values, measured by choice"),
               Line2D([], [], color=COL["calibration"], lw=1, label="p-values, drawn at random (calibration)")]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=6.3, frameon=False, bbox_to_anchor=(0.5, 0.0),
               columnspacing=1.0, handletextpad=0.4)
    fig.text(0.08, 0.965, "The record of measured sites: why each was measured, and whether it was needed",
             fontsize=9.5, fontweight="bold", color=INK)
    fig.savefig(FIG / "figS8_measured.png", dpi=200)
    fig.savefig(FIG / "figS8_measured.pdf")
    print("wrote", FIG / "figS8_measured.png")


if __name__ == "__main__":
    main()
