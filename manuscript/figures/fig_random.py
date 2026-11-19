"""
Figure 2: the "stock-picking chicken". Every certificate ordered by a
uniformly random score, against the informed scores, quantile path, all
recorded calibration seeds. Upper row: sites measured. Lower row:
realised wrong-skip rate on each certified level and seed.

    python manuscript/figures/fig_random.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fig_protocols import INK, INK2, OUT, SURF, load, style  # noqa: E402

COL = {"informed": "#2a78d6", "random": "#8a8984"}
LAB = {"informed": "Informed\nscores", "random": "Random\nscores"}
DATASETS = [
    ("IR map, original tolerance", "ir_nested_watson", "ir_nested_random", 949, 0.10, 0.25),
    ("IR map, tight tolerance", "ir_tight_sibson", "ir_tight_random", 949, 0.10, 0.25),
    ("NaCl scan", "nacl_fwhm_nested_watson", "nacl_fwhm_nested_random", 1071, 0.20, 0.20),
    ("Synthetic SAXS", "syn_peak_2cert_nested_watson", "syn_peak_2cert_nested_random", 2118, 0.20, 0.20),
]


def main():
    by = load()
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
    fig, axs = plt.subplots(2, 4, figsize=(11.0, 5.2), facecolor=SURF, constrained_layout=True)
    for j, (title, inf, rnd, n_design, eps, fail) in enumerate(DATASETS):
        a, b = axs[0, j], axs[1, j]
        style(a), style(b)
        exc = []
        for i, (key, row) in enumerate([("informed", inf), ("random", rnd)]):
            rs = by[row]
            meas = np.array([r["n_measured"] for r in rs])
            a.bar(i, meas.mean(), width=0.6, color=COL[key], zorder=2)
            a.errorbar(i, meas.mean(), yerr=meas.std(ddof=1), color=INK, lw=0.9, capsize=3, zorder=3)
            a.text(i, meas.mean() + meas.std(ddof=1) + n_design * 0.03, f"{meas.mean():.0f}",
                   ha="center", va="bottom", color=INK, fontsize=7.5)
            E = np.array([v for r in rs for v in r["level_E"] if np.isfinite(v)])
            jit = np.random.default_rng(i + 10 * j).uniform(-0.22, 0.22, len(E))
            b.scatter(i + jit, E, s=3, color=COL[key], alpha=0.5, linewidths=0, zorder=2)
            exc.append(f"{int(np.sum(E > eps + 1e-12))}/{len(E)}")
        a.axhline(n_design, color=INK2, lw=0.9, ls=(0, (4, 3)), zorder=1)
        a.text(-0.55, n_design, f"design {n_design}", ha="left", va="bottom", color=INK2, fontsize=7)
        a.set_ylim(0, n_design * 1.18)
        a.set_xlim(-0.6, 1.6)
        a.set_xticks([0, 1], [LAB["informed"], LAB["random"]], fontsize=7)
        a.set_title(f"{title}\n$R_E \\leq {eps:.2f}$ at confidence {1 - fail:.2f}", color=INK, fontsize=9)
        b.axhline(eps, color=INK, lw=1.0, zorder=1)
        b.text(-0.55, eps, " budget", ha="left", va="bottom", color=INK, fontsize=7)
        b.set_ylim(-0.01, eps * 1.8)
        b.set_xlim(-0.6, 1.6)
        b.set_xticks([0, 1], [f"{LAB[k]}\n{e} over" for k, e in zip(("informed", "random"), exc)], fontsize=7)
        if j == 0:
            a.set_ylabel("Sites measured (mean ± s.d.)", color=INK)
            b.set_ylabel("Wrong-skip rate on a level", color=INK)
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"fig2_random.{ext}", dpi=250, facecolor=SURF)


if __name__ == "__main__":
    main()
