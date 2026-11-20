"""
Figure: how a skip is judged. For one site per panel, the spectrum is predicted from the measured
sites of the coarser levels by natural-neighbour weights (grey: the neighbours, line width by weight)
and compared with the truth under the claim of its dataset. Left column: a site the claim accepts;
right column: a site it rejects.
(a, b) IR map, envelope claim: the prediction must lie within 10 % + 0.10 absorbance of the truth,
       on average over channels above 0.02 (band around the truth).
(c, d) NaCl scan, width claim: the FWHM of the (200) line must agree within 0.02 nm^-1
       (bars at half maximum; the shaded bar is the accepted range of the predicted width).
(e, f) Calcination, size claim on a furnace run: the anatase (101) width must agree within 0.12 deg in
       every crucible; shown is the crucible with the largest discrepancy.

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
from experiments.tio2_calcination import adapter as TA  # noqa: E402
from experiments.tio2_calcination import forward_v2 as V  # noqa: E402
from experiments.tio2_calcination import furnace as FU  # noqa: E402

FIG = Path(__file__).resolve().parent
INK, INK2, GRID = "#0b0b0b", "#52514e", "#b9b8b3"
BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.size": 8, "font.family": "DejaVu Sans", "axes.edgecolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK})


def predict(ds, L):
    """Truth, prediction from levels < L, and neighbour weights for every site of level L."""
    lv = np.asarray(ds.levels)
    meas, q = np.flatnonzero(lv < L), np.flatnonzero(lv == L)
    P = np.asarray(ds.points, float)
    W = neighbour_weights(P[meas], P[q], method="watson")
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


def calc_panels(axs):
    ds = FU.load(blocks_=(8, 8, 16, 32), model="v2")
    sigma = FU.noise_sigma(ds)
    crit = FU.criterion("size", sigma)
    C = ds.meta["n_channels"]
    q, meas, It, Ih, W, Y = predict(ds, 3)
    st = crit.stats(It, Ih)
    S = np.asarray(st["block_scores"], float)
    sc = S.max(1)
    x = V.axis()
    win = (x > V.A101 - 1.5) & (x < V.A101 + 2.6)

    def present(i):
        b = int(np.nanargmax(S[i]))
        sl = slice(b * C, (b + 1) * C)
        out = []
        for I_ in (It[i, sl], Ih[i, sl]):
            d = peak_descriptors_window(savgol_filter(I_[None], TA.SMOOTH, 2, axis=1), x, V.A101, TA.A_HALF)
            out.append(bool(np.isfinite(d["fwhm"][0]) and d["height_above_base"][0] > 8 * sigma))
        return out
    pres = {i: present(i) for i in range(len(sc))}

    def anatase_height(i, which):
        bk = int(np.nanargmax(S[i]))
        sl = slice(bk * C, (bk + 1) * C)
        I_ = (It if which == 0 else Ih)[i, sl]
        d = peak_descriptors_window(savgol_filter(I_[None], TA.SMOOTH, 2, axis=1), x, V.A101, TA.A_HALF)
        return float(np.nan_to_num(d["height_above_base"][0]))
    ok = [i for i in np.flatnonzero(sc <= 1) if all(pres[i])]
    bad = [i for i in np.flatnonzero(sc > 1) if pres[i][0] or pres[i][1]]
    picks = [ok[int(np.argmax([anatase_height(i, 0) for i in ok]))],
             bad[int(np.argmax([max(anatase_height(i, 0), anatase_height(i, 1)) for i in bad]))]]
    for ax, i, lab in zip(axs, picks, ("accepted", "rejected")):
        b = int(np.nanargmax(S[i]))
        sl = slice(b * C, (b + 1) * C)
        Yb = np.asarray(Y)[:, sl]
        neighbours(ax, x, W, i, Yb, xsl=win)
        It_b, Ih_b = It[i, sl], Ih[i, sl]
        ax.plot(x[win], It_b[win], color=INK, lw=1.1)
        ax.plot(x[win], Ih_b[win], color=ORANGE, lw=1.1, ls="--")
        dt = peak_descriptors_window(savgol_filter(It_b[None], TA.SMOOTH, 2, axis=1), x, V.A101, TA.A_HALF)
        dh = peak_descriptors_window(savgol_filter(Ih_b[None], TA.SMOOTH, 2, axis=1), x, V.A101, TA.A_HALF)
        ft, fh, ct, ch = dt["fwhm"][0], dh["fwhm"][0], dt["q_peak"][0], dh["q_peak"][0]
        pt, ph = pres[i]
        aw = (x > V.A101 - 1.0) & (x < V.A101 + 1.0)
        for I_, f, c, col, on in ((It_b, ft, ct, INK, pt), (Ih_b, fh, ch, ORANGE, ph)):
            if not on:
                continue
            base = np.median(I_[aw][:8])
            yhalf = base + 0.5 * (I_[aw].max() - base)
            if col == INK:
                ax.add_patch(plt.Rectangle((c - (f + FU.SIZE_TOL) / 2, yhalf - 0.03 * It_b[win].max()), f + FU.SIZE_TOL,
                                           0.06 * It_b[win].max(), color=BLUE, alpha=0.2, lw=0))
            ax.plot([c - f / 2, c + f / 2], [yhalf, yhalf], color=col, lw=2.2, solid_capstyle="butt")
        if pt and ph:
            note = f"worst crucible: ΔFWHM = {abs(fh - ft):.2f}° (tolerance 0.12°)"
        elif ph and not pt:
            note = "worst crucible: anatase predicted, not measured"
        else:
            note = "worst crucible: anatase measured, not predicted"
        rec = V.recipe(ds.meta["recipes"][q[i] * FU.N_SLOTS + b][None])
        ax.set_xlabel("2θ (deg)")
        ax.set_ylabel("counts")
        style(ax, f"Calcination run ({rec['T'][0]:.0f} °C, {rec['t'][0]:.1f} h), size claim: {lab}\n{note}")


def main():
    fig, axs = plt.subplots(3, 2, figsize=(7.2, 7.4), facecolor="white",
                            gridspec_kw=dict(hspace=0.62, wspace=0.28, left=0.09, right=0.98, top=0.95, bottom=0.07))
    ir_panels(axs[0])
    nacl_panels(axs[1])
    calc_panels(axs[2])
    for k, ax in enumerate(axs.ravel()):
        ax.text(-0.02, 1.13, "abcdef"[k], transform=ax.transAxes, fontweight="bold", fontsize=9, ha="right")
    fig.savefig(FIG / "fig_claims.png", dpi=200)
    fig.savefig(FIG / "fig_claims.pdf")
    print("wrote", FIG / "fig_claims.png")


if __name__ == "__main__":
    main()
