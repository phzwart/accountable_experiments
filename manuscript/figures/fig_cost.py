"""
Figure 6: what a guarantee costs under different models. Quantile path, 250 campaigns per configuration.
Bars: sites measured (mean ± s.d.) with random scores and with four interpolation protocols. Under each bar:
level checks over budget on the shared rate, observed / expected under the picked failure probabilities.

    python manuscript/figures/fig_cost.py
"""
import collections
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

FIG = Path(__file__).resolve().parent
ROOT = FIG.parents[1]
sys.path.insert(0, str(FIG))
from fig_protocols import INK, INK2, GRID, load  # noqa: E402

SURF = "white"
ARMS = ["random", "nn", "gp_mle", "gp_design", "gp_nonstationary"]
COL = {"random": "#a5a49f", "nn": "#2a78d6", "gp_mle": "#eb6834", "gp_design": "#1baf7a", "gp_nonstationary": "#eda100"}
LAB = {"random": "random\nscores", "nn": "natural\nneighbour", "gp_mle": "GP, max.\nlikelihood",
       "gp_design": "GP, design\nspacing", "gp_nonstationary": "GP, local\nspacing"}
DATASETS = [
    ("(a) IR map, original tolerance", "ir_nested_{}", "ir_nested_watson", "ir_nested_random", 959, 0.10, 0.75),
    ("(b) IR map, tight tolerance", "ir_tight_{}", "ir_tight_sibson", "ir_tight_random", 959, 0.10, 0.75),
    ("(c) NaCl scan", "nacl_fwhm_nested_{}", "nacl_fwhm_nested_watson", "nacl_fwhm_nested_random", 1071, 0.20, 0.80),
    ("(d) Synthetic map", "syn_peak_2cert_nested_{}", "syn_peak_2cert_nested_watson", "syn_peak_2cert_nested_random",
     2118, 0.20, 0.80),
]


def picked():
    obs, exp = collections.Counter(), collections.Counter()
    for r in json.loads((ROOT / "results/record/PICKED.json").read_text()):
        if r["event"] == "R_E":
            obs[r["row"]] += int(r["exceeded"])
            exp[r["row"]] += float(r["picked"])
    return obs, exp


def main():
    by = load()
    obs, exp = picked()
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
    fig, axs = plt.subplots(1, 4, figsize=(7.2, 2.9), facecolor=SURF,
                            gridspec_kw=dict(left=0.075, right=0.995, top=0.83, bottom=0.30, wspace=0.32))
    x = np.arange(len(ARMS))
    for ax, (title, pat, nn, rnd, n_design, eps, conf) in zip(axs, DATASETS):
        ticks = []
        for i, a in enumerate(ARMS):
            row = rnd if a == "random" else nn if a == "nn" else pat.format(a)
            meas = np.array([r["n_measured"] for r in by[row]])
            ax.bar(i, meas.mean(), width=0.7, color=COL[a], zorder=2)
            ax.errorbar(i, meas.mean(), yerr=meas.std(ddof=1), color=INK, lw=0.7, capsize=2, zorder=3)
            ticks.append(f"{obs[row]}/{exp[row]:.0f}")
        ax.axhline(n_design, color=INK2, lw=0.8, ls=(0, (4, 3)), zorder=1)
        ax.text(4.45, n_design, f"all {n_design}", ha="right", va="bottom", color=INK2, fontsize=6)
        ax.set_ylim(0, n_design * 1.15)
        ax.set_xlim(-0.6, 4.6)
        ax.set_xticks(x, ticks, fontsize=6.2, rotation=90)
        ax.tick_params(axis="x", length=0, pad=2)
        ax.tick_params(axis="y", labelsize=6.3, colors=INK2)
        ax.set_title(f"{title}\n$R_E \\leq {eps:.2f}$, confidence {conf:.2f}", loc="left", fontsize=7, color=INK)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.yaxis.grid(True, color=GRID, lw=0.5)
        ax.set_axisbelow(True)
    axs[0].set_ylabel("sites measured (mean ± s.d.)", fontsize=7, color=INK)
    fig.text(0.075, 0.105, "under each bar: level checks over budget, observed / expected", fontsize=6.3, color=INK2)
    handles = [plt.Rectangle((0, 0), 1, 1, color=COL[a]) for a in ARMS]
    fig.legend(handles, [LAB[a].replace("\n", " ") for a in ARMS], loc="lower center", ncol=5, fontsize=6.3,
               frameon=False, bbox_to_anchor=(0.53, -0.02), columnspacing=1.0, handlelength=1.0)
    fig.text(0.075, 0.95, "The model sets the cost of a guarantee", fontsize=9, fontweight="bold", color=INK)
    fig.savefig(FIG / "fig_cost.png", dpi=250, facecolor=SURF)
    fig.savefig(FIG / "fig_cost.pdf", facecolor=SURF)
    print("wrote", FIG / "fig_cost.png")


if __name__ == "__main__":
    main()
