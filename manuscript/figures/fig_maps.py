"""
Figure 5: maps with the reason recorded for every design site, one campaign per dataset
(quantile path, natural-neighbour interpolation, seed 0), with the wrong skips found against
the fully measured truth and the map bound of the last level.

    python manuscript/figures/fig_maps.py
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.record import OUT as REC, REASONS, build  # noqa: E402

FIG = Path(__file__).resolve().parent
INK, INK2, SURF, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e3df"
# Categorical slots in fixed order (blue, orange, aqua, yellow); neutrals for measured sites.
STYLE = {
    "not_interesting+interpolable": dict(c="#2a78d6", m="o", s=9, label="Skipped: both claims"),
    "calibration": dict(c="#eb6834", m="s", s=16, label="Calibration (measured)"),
    "interpolable": dict(c="#1baf7a", m="o", s=9, label="Skipped: predictable"),
    "not_interesting": dict(c="#eda100", m="o", s=9, label="Skipped: not of interest"),
    "seed": dict(c=INK, m="D", s=14, label="Seed (measured)"),
    "no_certificate": dict(c="#8a8984", m="s", s=12, label="Measured: no claim"),
}
ORDER = ["not_interesting", "interpolable", "not_interesting+interpolable", "no_certificate", "calibration", "seed"]
PANELS = [
    ("ir_nested_watson", "IR map", "um", r"$R_E \leq 0.10$ at confidence 0.75"),
    ("nacl_fwhm_nested_watson", "NaCl scan", "mm", r"$R_E \leq 0.20$ at confidence 0.80"),
    ("syn_peak_2cert_nested_watson", "Synthetic SAXS", "comp", r"$R_E \leq 0.20$ at confidence 0.80"),
]
SEED = 0


def load(row):
    z = np.load(REC / row / "sites.npz")
    i = int(np.flatnonzero(z["seeds"] == SEED)[0])
    rec = next(json.loads(l) for l in gzip.open(REC / row / "runs.jsonl.gz", "rt") if json.loads(l)["seed"] == SEED)
    ds, _, _ = build(row, SEED, {})
    return ds, z, i, rec


def coords(ds, site_index, unit):
    P = np.asarray(ds.points, float)[site_index]
    if unit == "um":
        return P * 41.0, "x (µm)", "y (µm)"
    if unit == "mm":
        return np.asarray(ds.meta["xy_mm"], float)[site_index], "x (mm)", "y (mm)"
    return P, "fraction of component 1", "fraction of component 2"


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
    fig, axs = plt.subplots(1, 3, figsize=(12.5, 5.2), facecolor=SURF,
                            gridspec_kw=dict(width_ratios=[1.45, 1.0, 1.0]))
    for ax, (row, title, unit, stmt) in zip(axs, PANELS):
        ds, z, i, rec = load(row)
        site = z["site_index"]
        reason = np.array(REASONS)[z["reason"][i]]
        P, xl, yl = coords(ds, site, unit)
        skipped = z["skipped"][i].astype(bool)
        inter, fail = z["interesting"][i].astype(bool), z["fail_prior"][i].astype(bool)
        a_cov = np.isin(reason, ["not_interesting", "not_interesting+interpolable"])
        b_cov = np.isin(reason, ["interpolable", "not_interesting+interpolable"])
        wrong = skipped & ((a_cov & inter) | (b_cov & fail))
        for key in ORDER:
            sel = reason == key
            if sel.any():
                st = STYLE[key]
                ax.scatter(P[sel, 0], P[sel, 1], s=st["s"], c=st["c"], marker=st["m"], linewidths=0, zorder=2)
        ax.scatter(P[wrong, 0], P[wrong, 1], s=28, marker="x", c=INK, linewidths=0.9, zorder=3)
        mc = rec["map_certificates"][-1]
        n_meas = int((~skipped).sum())
        n_lev = int((reason != "seed").sum())
        ax.set_title(f"{title}, {stmt}\n{n_meas} of {len(site)} sites measured, {int(skipped.sum())} skipped\n"
                     f"wrong skips: {int(wrong.sum())} ({100 * wrong.sum() / n_lev:.1f} % of certified-level sites)",
                     color=INK, fontsize=8.2, loc="left")
        ax.text(0.0, -0.17, f"Map bound, level {mc['from_level']}: at most {100 * mc['upper']:.1f} % of sites outside\n"
                f"tolerance at confidence {mc['confidence']:.2f} ({mc['failures']} of {mc['m']} calibration\n"
                f"sites failed); actual {100 * mc['level_fail_fraction']:.1f} %",
                transform=ax.transAxes, fontsize=7.3, color=INK2, va="top")
        ax.set_xlabel(xl, color=INK2)
        ax.set_ylabel(yl, color=INK2)
        ax.set_aspect("equal")
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.tick_params(colors=INK2, labelsize=7)
        if unit == "um":
            ax.invert_yaxis()
    handles = [Line2D([], [], ls="", marker=STYLE[k]["m"], color=STYLE[k]["c"], ms=6, label=STYLE[k]["label"])
               for k in ["seed", "calibration", "no_certificate", "not_interesting", "interpolable",
                         "not_interesting+interpolable"]]
    handles.append(Line2D([], [], ls="", marker="x", color=INK, ms=6, label="Wrong skip (checked against truth)"))
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=7.5, bbox_to_anchor=(0.5, 0.0))
    fig.subplots_adjust(left=0.05, right=0.98, top=0.83, bottom=0.30, wspace=0.30)
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"fig5_maps.{ext}", dpi=250, facecolor=SURF)


if __name__ == "__main__":
    main()
