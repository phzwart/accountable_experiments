"""
Figure: how a skip is judged. For one site per panel, the spectrum is predicted from the measured
sites of the coarser levels by natural-neighbour weights (grey: the neighbours, line width by weight)
and compared with the truth under the claim of its dataset. Left column: a site the claim accepts;
right column: a site it rejects.
(a, b) IR map, envelope claim: the prediction must lie within 10 % + 0.10 absorbance of the truth,
       on average over channels above 0.02 (band around the truth).
(c, d) NaCl scan, width claim: the FWHM of the (200) line must agree within 0.02 nm^-1
       (bars at half maximum; the shaded bar is the accepted range of the predicted width).
(e, f) Synthetic scattering map, peak claim: the dominant-peak position must agree within 0.005 A^-1
       and its width within 0.001 A^-1 (bars at half maximum; shaded: the accepted ranges).

    python manuscript/figures/fig_claims.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from accountable.sibson import neighbour_weights  # noqa: E402
from accountable.criteria import peak_descriptors_window  # noqa: E402
from accountable import peak_descriptors  # noqa: E402
from experiments.ir_bioreef import adapter as IR  # noqa: E402
from experiments.nacl_saxs import adapter as NA  # noqa: E402
from experiments.synthetic_saxs import adapter as SA  # noqa: E402

FIG = Path(__file__).resolve().parent
INK, INK2, GRID = "#0b0b0b", "#52514e", "#b9b8b3"
BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.size": 8, "font.family": "DejaVu Sans", "axes.edgecolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK})


def predict(ds, L, images=None, candidate=None):
    """Truth, prediction from levels < L, and neighbour weights for every site of level L."""
    lv = np.asarray(ds.levels)
    cand = np.ones(len(lv), bool) if candidate is None else np.asarray(candidate, bool)
    meas, q = np.flatnonzero((lv < L) & cand), np.flatnonzero((lv == L) & cand)
    P = np.asarray(ds.points, float)
    W = neighbour_weights(P[meas], P[q], images=images, method="watson")
    Y = ds.oracle.truth(meas)
    return q, meas, ds.oracle.truth(q), W.apply(Y), W, Y


def neighbours(ax, x, W, i, Y, scale=1.0, xsl=slice(None)):
    keys, raw = np.asarray(W.keys[i]), np.asarray(W.raw[i], float)
    w = raw / raw.sum()
    for k, wk in sorted(zip(keys, w), key=lambda t: -t[1])[:6]:
        ax.plot(x[xsl], scale * Y[k][xsl], color=GRID, lw=0.4 + 2.2 * wk, zorder=1)


def style(ax, title):
    ax.set_title(title, loc="left", fontsize=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def ir_panels(axs):
    ds = IR.load()
    crit = IR.criterion()
    q, meas, It, Ih, W, Y = predict(ds, 5)
    st = crit.stats(It, Ih)
    sc = np.asarray(st["score"], float)
    big = It.max(1) > 0.15
    ok = np.flatnonzero(big & (sc <= 1))
    bad = np.flatnonzero(big & (sc > 1))
    pick = [ok[np.argmin(np.abs(sc[ok] - 0.3))], bad[np.argmin(np.abs(sc[bad] - 1.6))]]
    x = ds.axis
    for ax, i, lab in zip(axs, pick, ("accepted", "rejected")):
        tol = IR.RTOL * np.abs(It[i]) + IR.ATOL
        neighbours(ax, x, W, i, Y)
        ax.fill_between(x, It[i] - tol, It[i] + tol, color=BLUE, alpha=0.13, lw=0, zorder=0)
        ax.plot(x, It[i], color=INK, lw=1.1, label="measured (truth)")
        ax.plot(x, Ih[i], color=ORANGE, lw=1.1, ls="--", label="predicted")
        ax.invert_xaxis()
        ax.set_xlabel("wavenumber (cm$^{-1}$)")
        ax.set_ylabel("absorbance")
        style(ax, f"IR, envelope claim: {lab}\nmean ρ = {sc[i]:.2f} (accepted if ≤ 1)")
    axs[0].legend(fontsize=6.5, frameon=False, loc="upper left")


def width_marks(ax, x, I, d, col, y0=None):
    if not np.isfinite(d["fwhm"]):
        return
    hm = d["half_level"] if "half_level" in d else None
    c, f = d["q_peak"], d["fwhm"]
    y = hm if hm is not None else (y0 if y0 is not None else np.interp(c, x, I) / 2)
    ax.plot([c - f / 2, c + f / 2], [y, y], color=col, lw=2.0, solid_capstyle="butt")


def nacl_panels(axs):
    ds, _ = NA.load()
    sigma = NA.noise_sigma(ds)
    crit = NA.criterion("fwhm", ds.axis, sigma)
    q, meas, It, Ih, W, Y = predict(ds, 5)
    st = crit.stats(It, Ih)
    sc = np.asarray(st["score"], float)
    dt = peak_descriptors(It, ds.axis, q_center=NA.Q200, q_halfwidth=NA.Q200_HALF)
    dh = peak_descriptors(Ih, ds.axis, q_center=NA.Q200, q_halfwidth=NA.Q200_HALF)
    h = np.asarray(dt["height_above_base"], float)
    hh = np.asarray(dh["height_above_base"], float)
    ratio = hh / np.maximum(h, 1e-9)
    valid = (np.isfinite(sc) & np.isfinite(dt["fwhm"]) & np.isfinite(dh["fwhm"]) & (h > 20 * sigma)
             & (ratio > 0.5) & (ratio < 2))
    ok = np.flatnonzero(valid & (sc <= 1))
    bad = np.flatnonzero(valid & (sc > 1))
    pick = [ok[np.argmax(h[ok])], bad[np.argmin(np.abs(sc[bad] - 2.0))]]
    x = ds.axis
    win = (x > NA.Q200 - 0.6) & (x < NA.Q200 + 0.6)
    for ax, i, lab in zip(axs, pick, ("accepted", "rejected")):
        neighbours(ax, x, W, i, Y, xsl=win)
        ax.plot(x[win], It[i][win], color=INK, lw=1.1)
        ax.plot(x[win], Ih[i][win], color=ORANGE, lw=1.1, ls="--")
        for I_, d, col, dy in ((It[i], dt, INK, 0.0), (Ih[i], dh, ORANGE, 0.0)):
            yw = I_[win]
            base = np.median(np.r_[yw[:5], yw[-5:]])
            yhalf = base + 0.5 * (yw.max() - base)
            c, f = d["q_peak"][i], d["fwhm"][i]
            if col == INK:
                ax.add_patch(plt.Rectangle((c - (f + NA.FWHM_TOL) / 2, yhalf - 0.04 * yw.max()), f + NA.FWHM_TOL,
                                           0.08 * yw.max(), color=BLUE, alpha=0.2, lw=0))
            ax.plot([c - f / 2, c + f / 2], [yhalf, yhalf], color=col, lw=2.2, solid_capstyle="butt")
        ax.set_xlabel("q (nm$^{-1}$)")
        ax.set_ylabel("intensity (counts)")
        style(ax, f"NaCl, (200) width claim: {lab}\nΔFWHM = {abs(dh['fwhm'][i] - dt['fwhm'][i]):.3f} nm$^{{-1}}$ (tolerance 0.02)")


def saxs_panels(axs):
    ds = SA.load()
    crit = SA.criterion("peak", ds.axis)
    q, meas, It, Ih, W, Y = predict(ds, 6, images=SA.wall_images, candidate=ds.candidate)
    st = crit.stats(It, Ih)
    sc = np.asarray(st["score"], float)
    x = ds.axis
    dt, dh = peak_descriptors(It, x), peak_descriptors(Ih, x)
    pr = np.asarray(dt["prominence"], float)
    valid = np.isfinite(sc) & (pr >= 2 * SA.PROMINENCE) & np.isfinite(dh["fwhm"])
    ok = np.flatnonzero(valid & (sc <= 1))
    bad = np.flatnonzero(valid & (sc > 1.5) & (sc < 6))
    pick = [ok[np.argmin(np.abs(sc[ok] - 0.5))], bad[np.argmin(np.abs(sc[bad] - 3))]]
    for ax, i, lab in zip(axs, pick, ("accepted", "rejected")):
        c = dt["q_peak"][i]
        win = (x > c - 0.03) & (x < c + 0.03)
        neighbours(ax, x, W, i, Y, xsl=win)
        ax.plot(x[win], It[i][win], color=INK, lw=1.1)
        ax.plot(x[win], Ih[i][win], color=ORANGE, lw=1.1, ls="--")
        for I_, d, col in ((It[i], dt, INK), (Ih[i], dh, ORANGE)):
            yw = I_[win]
            base = np.min(yw)
            yhalf = base + 0.5 * (yw.max() - base)
            cc, f = d["q_peak"][i], d["fwhm"][i]
            if col == INK:
                ax.axvspan(cc - SA.PEAK_EPS, cc + SA.PEAK_EPS, color=BLUE, alpha=0.10, lw=0)
                ax.add_patch(plt.Rectangle((cc - (f + SA.FWHM_EPS) / 2, yhalf - 0.03 * yw.max()), f + SA.FWHM_EPS,
                                           0.06 * yw.max(), color=BLUE, alpha=0.25, lw=0))
            ax.plot([cc - f / 2, cc + f / 2], [yhalf, yhalf], color=col, lw=2.2, solid_capstyle="butt")
        dq = abs(dh["q_peak"][i] - dt["q_peak"][i])
        dw = abs(dh["fwhm"][i] - dt["fwhm"][i])
        ax.set_xlabel("q (Å$^{-1}$)")
        ax.set_ylabel("intensity")
        style(ax, f"Synthetic map, peak claim: {lab}\nΔq* = {dq:.4f}, ΔFWHM = {dw:.4f} Å$^{{-1}}$")


def main():
    fig, axs = plt.subplots(3, 2, figsize=(7.2, 7.4), facecolor="white",
                            gridspec_kw=dict(hspace=0.62, wspace=0.28, left=0.09, right=0.98, top=0.95, bottom=0.07))
    ir_panels(axs[0])
    nacl_panels(axs[1])
    saxs_panels(axs[2])
    for k, ax in enumerate(axs.ravel()):
        ax.text(-0.02, 1.13, "abcdef"[k], transform=ax.transAxes, fontweight="bold", fontsize=9, ha="right")
    fig.savefig(FIG / "fig_claims.png", dpi=200)
    fig.savefig(FIG / "fig_claims.pdf")
    print("wrote", FIG / "fig_claims.png")


if __name__ == "__main__":
    main()
