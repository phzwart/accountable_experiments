"""
Synthetic map without the interest certificate: interpolation certificate only, quantile path,
budget 0.20 at confidence 0.80, natural neighbour, seed 0. Compared with seed 0 of the record
(both certificates). Writes results/analysis/syn_clumps/interp_only_seed0.png and .json.

    python -m experiments.analysis.syn_interp_only
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from accountable import run_campaign
from experiments.record import OUT as REC, REASONS
from experiments.study import _load

OUTD = Path("results/analysis/syn_clumps")
INK, INK2, SURF = "#0b0b0b", "#52514e", "#fcfcfb"
STYLE = {
    "not_interesting+interpolable": ("#2a78d6", "o", 9, "Skipped: both claims"),
    "calibration": ("#eb6834", "s", 16, "Calibration (measured)"),
    "interpolable": ("#1baf7a", "o", 9, "Skipped: predictable"),
    "not_interesting": ("#eda100", "o", 9, "Skipped: not of interest"),
    "seed": (INK, "D", 14, "Seed (measured)"),
    "no_certificate": ("#8a8984", "s", 12, "Measured: no claim"),
}
ORDER = ["not_interesting", "interpolable", "not_interesting+interpolable", "no_certificate", "calibration", "seed"]


def panel(ax, P, reason, skipped, inter, fail, title):
    a = np.isin(reason, ["not_interesting", "not_interesting+interpolable"])
    b = np.isin(reason, ["interpolable", "not_interesting+interpolable"])
    wrong = skipped & ((a & inter) | (b & fail))
    for k in ORDER:
        s = reason == k
        if s.any():
            c, m, sz, _ = STYLE[k]
            ax.scatter(P[s, 0], P[s, 1], s=sz, c=c, marker=m, linewidths=0, zorder=2)
    ax.scatter(P[wrong, 0], P[wrong, 1], s=28, marker="x", c=INK, linewidths=0.9, zorder=3)
    n_lev = int((reason != "seed").sum())
    lost = skipped & inter
    ax.set_title(f"{title}\n{int((~skipped).sum())} of {len(P)} measured, {int(skipped.sum())} skipped; "
                 f"wrong skips {int(wrong.sum())} ({100 * wrong.sum() / n_lev:.1f} %)\n"
                 f"interesting sites skipped: {int(lost.sum())} of {int(inter.sum())} "
                 f"({int((lost & a).sum())} as not of interest)", fontsize=8.2, loc="left", color=INK)
    ax.set_aspect("equal")
    ax.set_xlabel("fraction of component 1", color=INK2)
    ax.set_ylabel("fraction of component 2", color=INK2)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    return dict(measured=int((~skipped).sum()), skipped=int(skipped.sum()), wrong=int(wrong.sum()),
                wrong_share=float(wrong.sum() / n_lev), interesting_skipped=int(lost.sum()),
                interesting=int(inter.sum()))


def main():
    A, ds = _load("synthetic_saxs")
    cfg = A.config(ds, target="peak", mode="interp", policy="nested_path", eps=0.20, confidence=0.80,
                   seed=0, nn_method="watson")
    res = run_campaign(ds, cfg)
    cand = np.flatnonzero(ds.candidate)
    P = np.asarray(ds.points, float)[cand]
    r_new = np.asarray(res.reason)[cand].astype(str)
    z = np.load(REC / "syn_peak_2cert_nested_watson" / "sites.npz")
    i0 = int(np.flatnonzero(z["seeds"] == 0)[0])
    r_old = np.array(REASONS)[z["reason"][i0]]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 5.4), facecolor=SURF)
    s_old = panel(axs[0], P, r_old, z["skipped"][i0].astype(bool), z["interesting"][i0].astype(bool),
                  z["fail_prior"][i0].astype(bool), "Both certificates (record, seed 0)")
    s_new = panel(axs[1], P, r_new, np.asarray(res.skipped)[cand], np.asarray(res.interesting)[cand],
                  np.asarray(res.fail_prior)[cand], "Interpolation certificate only (seed 0)")
    h = [Line2D([], [], ls="", marker=STYLE[k][1], color=STYLE[k][0], ms=6, label=STYLE[k][3])
         for k in ["seed", "calibration", "no_certificate", "not_interesting", "interpolable",
                   "not_interesting+interpolable"]]
    h.append(Line2D([], [], ls="", marker="x", color=INK, ms=6, label="Wrong skip"))
    fig.legend(handles=h, loc="lower center", ncol=4, frameon=False, fontsize=7.5)
    fig.subplots_adjust(left=0.07, right=0.98, top=0.83, bottom=0.2, wspace=0.25)
    fig.savefig(OUTD / "interp_only_seed0.png", dpi=220, facecolor=SURF)
    levels = [dict(L=pl["L"], E_rate=pl["level"]["E_rate"]) for pl in res.per_level]
    (OUTD / "interp_only_seed0.json").write_text(json.dumps(dict(both=s_old, interp_only=s_new,
                                                                 levels=levels, map=res.map_certificates[-1]
                                                                 if res.map_certificates else None)))
    print(json.dumps(dict(both=s_old, interp_only=s_new, levels=levels), indent=1))


if __name__ == "__main__":
    main()
