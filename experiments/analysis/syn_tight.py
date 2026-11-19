"""
Synthetic map, interpolation certificate only, with tighter peak tolerances (position and FWHM
scaled by 1, 1/2 and 1/4). Quantile path, budget 0.20 at confidence 0.80, natural neighbour, seed 0.
Writes results/analysis/syn_clumps/interp_tight_seed0.png and .json.

    python -m experiments.analysis.syn_tight
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from scipy.spatial import cKDTree

from accountable import run_campaign
from experiments.analysis.syn_interp_only import INK, ORDER, STYLE, SURF, OUTD
from experiments.study import _load

SCALES = (1.0, 0.5, 0.25)


def main():
    A, ds = _load("synthetic_saxs")
    p0, f0 = A.PEAK_EPS, A.FWHM_EPS
    cand = np.flatnonzero(ds.candidate)
    P = np.asarray(ds.points, float)[cand]
    ph = np.asarray(ds.meta["phase"])[cand]
    _, nn = cKDTree(P).query(P, k=7)
    bnd = (ph[nn[:, 1:]] != ph[:, None]).any(1)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
    fig, axs = plt.subplots(1, len(SCALES), figsize=(14.5, 5.8), facecolor=SURF)
    out = []
    for ax, s in zip(axs, SCALES):
        A.PEAK_EPS, A.FWHM_EPS = p0 * s, f0 * s
        try:
            cfg = A.config(ds, target="peak", mode="interp", policy="nested_path", eps=0.20,
                           confidence=0.80, seed=0, nn_method="watson")
            res = run_campaign(ds, cfg)
        finally:
            A.PEAK_EPS, A.FWHM_EPS = p0, f0
        reason = np.asarray(res.reason)[cand].astype(str)
        sk = np.asarray(res.skipped)[cand]
        F = np.asarray(res.fail_prior)[cand]
        wrong = sk & (reason == "interpolable") & F
        for k in ORDER:
            m = reason == k
            if m.any():
                c, mk, sz, _ = STYLE[k]
                ax.scatter(P[m, 0], P[m, 1], s=sz, c=c, marker=mk, linewidths=0, zorder=2)
        ax.scatter(P[wrong, 0], P[wrong, 1], s=28, marker="x", c=INK, linewidths=0.9, zorder=3)
        n_lev = int((reason != "seed").sum())
        rates = [round(pl["level"]["E_rate"], 2) for pl in res.per_level]
        ax.set_title(f"Δq ≤ {p0 * s:.4f}, ΔFWHM ≤ {f0 * s:.5f} Å⁻¹\n"
                     f"{int((~sk).sum())} of {len(P)} measured; wrong skips {int(wrong.sum())} "
                     f"({100 * wrong.sum() / n_lev:.1f} %)\n"
                     f"outside tolerance (prediction): {100 * F[reason != 'seed'].mean():.0f} % of sites\n"
                     f"wrong skips at phase boundaries: {100 * bnd[wrong].mean():.0f} %; level rates {rates}",
                     fontsize=8, loc="left", color=INK)
        ax.set_aspect("equal")
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.set_xlabel("fraction of component 1")
        out.append(dict(scale=s, peak_eps=p0 * s, fwhm_eps=f0 * s, measured=int((~sk).sum()),
                        wrong=int(wrong.sum()), wrong_share=float(wrong.sum() / n_lev),
                        fail_share=float(F[reason != "seed"].mean()), boundary_share=float(bnd[wrong].mean()) if wrong.any() else None,
                        level_rates=rates))
    axs[0].set_ylabel("fraction of component 2")
    h = [Line2D([], [], ls="", marker=STYLE[k][1], color=STYLE[k][0], ms=6, label=STYLE[k][3])
         for k in ["seed", "calibration", "no_certificate", "interpolable"]]
    h.append(Line2D([], [], ls="", marker="x", color=INK, ms=6, label="Wrong skip"))
    fig.legend(handles=h, loc="lower center", ncol=5, frameon=False, fontsize=7.5)
    fig.subplots_adjust(left=0.05, right=0.99, top=0.80, bottom=0.15, wspace=0.18)
    fig.savefig(OUTD / "interp_tight_seed0.png", dpi=200, facecolor=SURF)
    (OUTD / "interp_tight_seed0.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
