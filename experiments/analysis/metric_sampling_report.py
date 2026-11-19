"""
Figure and numbers for metric_sampling: where each metric sends the measurements.

    python -m experiments.analysis.metric_sampling_report
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import cKDTree
from scipy.stats import spearmanr

from accountable import peak_descriptors
from experiments.study import _load

OUTD = Path("results/analysis/metric_sampling")
INK, INK2, SURF = "#0b0b0b", "#52514e", "#fcfcfb"


def local_variation(ds, exp, cand):
    """Per-site change to its 6 nearest design neighbours, in units of each metric's default tolerance."""
    P = np.asarray(ds.points, float)[cand]
    I = np.asarray(ds.oracle.truth(cand), float)
    _, nn = cKDTree(P).query(P, k=7)
    nn = nn[:, 1:]
    prof = np.abs(I[:, None, :] - I[nn]) / (0.01 * np.abs(I[:, None, :]) + 0.01)
    v_prof = np.median(prof.mean(-1), axis=1)
    if exp == "synthetic_saxs":
        d = peak_descriptors(I, ds.axis)
        qp, fw = np.nan_to_num(d["q_peak"], nan=0.0), np.nan_to_num(d["fwhm"], nan=0.0)
        v_peak = np.median(np.maximum(np.abs(qp[:, None] - qp[nn]) / 0.005, np.abs(fw[:, None] - fw[nn]) / 0.001), axis=1)
    else:
        A, _ = _load("nacl_saxs")
        d = peak_descriptors(I, ds.axis, q_center=A.Q200, q_halfwidth=A.Q200_HALF)
        fw = np.nan_to_num(d["fwhm"], nan=0.0)
        v_peak = np.median(np.abs(fw[:, None] - fw[nn]) / 0.02, axis=1)
    return v_peak, v_prof


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
    summary = {}
    fig, axs = plt.subplots(4, 3, figsize=(11.5, 14.5), facecolor=SURF)
    row = 0
    for exp, unit in [("synthetic_saxs", "comp"), ("nacl_saxs", "mm")]:
        z = np.load(OUTD / f"{exp}.npz")
        ms = list(z["metrics"])
        _, ds = _load(exp)
        cand = np.flatnonzero(np.asarray(ds.candidate, bool)) if ds.candidate is not None else np.arange(len(ds.points))
        lev = np.asarray(ds.levels)[cand]
        cert = lev > 2
        if unit == "mm":
            P = np.asarray(ds.meta["xy_mm"], float)[cand]
        else:
            P = np.asarray(ds.points, float)[cand]
        v_peak, v_prof = local_variation(ds, exp, cand)
        ph = np.asarray(ds.meta["phase"])[cand] if "phase" in ds.meta else None
        res = {}
        for blk, (a, b) in [("default", (0, 1)), ("matched", (2, 3))]:
            ma, mb = z[f"meas_{a}"][cand], z[f"meas_{b}"][cand]
            r = dict(
                measured=[float(ma[cert].sum()), float(mb[cert].sum())],
                spearman_peakmetric_vs=[float(spearmanr(ma[cert], v_peak[cert]).correlation),
                                        float(spearmanr(ma[cert], v_prof[cert]).correlation)],
                spearman_profilemetric_vs=[float(spearmanr(mb[cert], v_peak[cert]).correlation),
                                           float(spearmanr(mb[cert], v_prof[cert]).correlation)],
                overlap=float(np.minimum(ma, mb)[cert].sum() / max(np.maximum(ma, mb)[cert].sum(), 1e-9)),
            )
            if ph is not None:
                _, nn = cKDTree(P).query(P, k=7)
                bnd = (ph[nn[:, 1:]] != ph[:, None]).any(1)
                r["boundary_share_of_measurements"] = [float(ma[cert & bnd].sum() / ma[cert].sum()),
                                                       float(mb[cert & bnd].sum() / mb[cert].sum()),
                                                       float((cert & bnd).sum() / cert.sum())]
                r["measured_by_phase"] = {str(p): [float(ma[cert & (ph == p)].sum()), float(mb[cert & (ph == p)].sum())]
                                          for p in np.unique(ph)}
            res[blk] = r
            vmax = max(ma.max(), mb.max(), 1e-9)
            for j, (vals, title) in enumerate([(ma, ms[a]), (mb, ms[b])]):
                ax = axs[row, j]
                sc = ax.scatter(P[cert, 0], P[cert, 1], c=vals[cert], s=6, cmap="Blues", vmin=0, vmax=vmax, linewidths=0)
                ax.set_title(f"{title.split(' | ')[1]}\nP(measured, no claim): {vals[cert].sum():.0f} sites expected",
                             fontsize=8, loc="left", color=INK)
                fig.colorbar(sc, ax=ax, shrink=0.75)
            ax = axs[row, 2]
            dlt = (mb - ma)[cert]
            lim = max(np.abs(dlt).max(), 1e-9)
            sc = ax.scatter(P[cert, 0], P[cert, 1], c=dlt, s=6, cmap="RdBu_r", vmin=-lim, vmax=lim, linewidths=0)
            ax.set_title(f"{exp.split('_')[0]} ({blk}): profile − peak\nred: measured more under the profile metric",
                         fontsize=8, loc="left", color=INK)
            fig.colorbar(sc, ax=ax, shrink=0.75)
            for ax in axs[row]:
                ax.set_aspect("equal")
                ax.tick_params(labelsize=6)
            row += 1
        summary[exp] = res
    fig.tight_layout()
    fig.savefig(OUTD / "sampling_maps.png", dpi=170, facecolor=SURF)
    (OUTD / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
