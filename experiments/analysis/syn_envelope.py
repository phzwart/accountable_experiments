"""
Synthetic map, interpolation certificate only: full-spectrum envelope claim against the peak claim.
Quantile path, budget 0.20 at confidence 0.80, natural neighbour, seed 0.

    python -m experiments.analysis.syn_envelope
"""
from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from scipy.spatial import cKDTree

from accountable import run_campaign
from experiments.analysis.syn_interp_only import INK, ORDER, STYLE, SURF, OUTD
from experiments.study import _load

RUNS = [("peak", None, "Peak: Δq ≤ 0.005, ΔFWHM ≤ 0.001 Å⁻¹"),
        ("envelope", 0.01, "Full spectrum: |ΔI| ≤ 0.01 + 1 % of I"),
        ("envelope", 0.05, "Full spectrum: |ΔI| ≤ 0.05 + 5 % of I")]


def main():
    A, ds = _load("synthetic_saxs")
    cand = np.flatnonzero(ds.candidate)
    P = np.asarray(ds.points, float)[cand]
    ph = np.asarray(ds.meta["phase"])[cand]
    _, nn = cKDTree(P).query(P, k=7)
    bnd = (ph[nn[:, 1:]] != ph[:, None]).any(1)
    r0 = (A.RTOL, A.ATOL)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
    fig, axs = plt.subplots(1, len(RUNS), figsize=(14.5, 6.0), facecolor=SURF)
    out = []
    for ax, (target, tol, label) in zip(axs, RUNS):
        if tol is not None:
            A.RTOL = A.ATOL = tol
        try:
            cfg = A.config(ds, target=target, mode="interp", policy="nested_path", eps=0.20,
                           confidence=0.80, seed=0, nn_method="watson")
            res = run_campaign(ds, cfg)
        finally:
            A.RTOL, A.ATOL = r0
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
        bshare = 100 * bnd[wrong].mean() if wrong.any() else float("nan")
        ax.set_title(f"{label}\n{int((~sk).sum())} of {len(P)} measured; wrong skips {int(wrong.sum())} "
                     f"({100 * wrong.sum() / n_lev:.1f} %)\n"
                     f"outside tolerance (prediction): {100 * F[reason != 'seed'].mean():.0f} % of sites\n"
                     f"wrong skips at phase boundaries: {bshare:.0f} %\nlevel rates {rates}",
                     fontsize=8, loc="left", color=INK)
        ax.set_aspect("equal")
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.set_xlabel("fraction of component 1")
        out.append(dict(target=target, tol=tol, measured=int((~sk).sum()), wrong=int(wrong.sum()),
                        wrong_share=float(wrong.sum() / n_lev), fail_share=float(F[reason != "seed"].mean()),
                        boundary_share=None if not wrong.any() else float(bnd[wrong].mean()), level_rates=rates))
    axs[0].set_ylabel("fraction of component 2")
    h = [Line2D([], [], ls="", marker=STYLE[k][1], color=STYLE[k][0], ms=6, label=STYLE[k][3])
         for k in ["seed", "calibration", "no_certificate", "interpolable"]]
    h.append(Line2D([], [], ls="", marker="x", color=INK, ms=6, label="Wrong skip"))
    fig.legend(handles=h, loc="lower center", ncol=5, frameon=False, fontsize=7.5)
    fig.subplots_adjust(left=0.05, right=0.99, top=0.78, bottom=0.14, wspace=0.18)
    fig.savefig(OUTD / "interp_envelope_seed0.png", dpi=200, facecolor=SURF)
    (OUTD / "interp_envelope_seed0.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
