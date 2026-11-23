"""
Figure 1 (round 8): specified and calibrated in advance. NaCl (200)-width scan, 80 fresh hierarchical designs, one
Gaussian process on the staged plan (seed = levels 0-3, three rounds), budget 0.20 per round at confidence 0.80.
Per round the same frozen process and the same held-out calibration draw; on the leftover sites the cut is set either
by the process's own uncertainty (joint posterior draws) or by the calibration draw (exact bound). Each cut is shown
in the campaign it drives. Two kernels of the same process: white noise fitted, or a fixed nugget.

(a) Measured width with the seed and the three rounds of one design.
(b) Per round and campaign: wrong skips delivered minus the bound stated before the round (share of the round).
    Dark: the lowest 80 % of campaigns, ending at the tick; calibrated if the tick lies on zero.
(c) Share of campaigns within their stated bound, against the 80 % promised (Clopper-Pearson 95 %).

    python manuscript/figures/fig_hook3.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import beta, gaussian_kde

FIG = Path(__file__).resolve().parent
ROOT = FIG.parents[1]
sys.path.insert(0, str(FIG)); sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "src"))

INK, INK2 = "#0b0b0b", "#52514e"
ORANGE, PURPLE = "#eb6834", "#8e6cc8"
RED, BLUE = "#b8391f", "#2f5f9e"
CONF = 0.80
KLAB = {"fitted": "fitted noise", "nugget": "fixed nugget", "smooth": "long length scale"}


def cp(k, n, a=0.05):
    return (beta.ppf(a / 2, k, n - k + 1) if k > 0 else 0.0, beta.ppf(1 - a / 2, k + 1, n - k) if k < n else 1.0)


def arm(rr, kernel, cut):
    sub = [r for r in rr if r["kernel"] == kernel and r["driver"] == cut]
    N = np.array([[x["N"] for x in r["rounds"]] for r in sub])
    sk = np.array([[x[cut]["n_skip"] for x in r["rounds"]] for r in sub])
    wr = np.array([[x[cut]["realised"] for x in r["rounds"]] for r in sub])
    st = np.array([[x[cut]["stated"] for x in r["rounds"]] for r in sub])
    tot = np.array([r["measured"] for r in sub])
    return dict(d=wr / N - st, measured=(N - sk).mean(0), N=N.mean(0), total=tot.mean(), n=len(sub))


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK})
    rr = [json.loads(l) for l in open(ROOT / "results/revision2/paired_gp.jsonl")]
    A = {(k, c): arm(rr, k, c) for k in ("fitted", "nugget") for c in ("uq", "contract")}

    from fig_datasets import nacl_fwhm
    from experiments.nacl_saxs.adapter import load as nload
    img, _, (xs, ys), _, _ = nacl_fwhm()
    ds, grid = nload()
    xy = np.asarray(grid["xy_mm"], float)

    fig = plt.figure(figsize=(7.2, 3.4))
    # (a)
    axg = fig.add_axes([0.01, 0.24, 0.255, 0.56]); axg.set_facecolor("#f4f3ef")
    vmin, vmax = np.nanpercentile(img, 5), np.nanpercentile(img, 95)
    imw = axg.imshow(img, origin="lower", cmap="viridis", alpha=0.85, vmin=vmin, vmax=vmax, interpolation="nearest")
    rxy = xy[np.asarray(ds.meta["raster_index"])]
    dix = np.searchsorted(xs, rxy[:, 0].round(4)); diy = np.searchsorted(ys, rxy[:, 1].round(4)); lv = np.asarray(ds.levels)
    axg.scatter(dix[lv <= 3], diy[lv <= 3], s=6, c="white", marker="s", lw=0.6, edgecolors="black", zorder=5, label="seed")
    for r, (L, sz) in enumerate(zip((4, 5, 6), (3.5, 1.6, 0.5))):
        m = lv == L
        if r == 0:
            axg.scatter(dix[m], diy[m], s=sz, facecolors="none", edgecolors="black", lw=0.5, zorder=4, label="round 1")
        else:
            axg.scatter(dix[m], diy[m], s=sz, c="#111111", lw=0, alpha=0.8, zorder=3, label=f"round {r + 1}")
    axg.set_xlim(-0.5, img.shape[1] - 0.5); axg.set_ylim(-0.5, img.shape[0] - 0.5)
    axg.set_xticks([]); axg.set_yticks([])
    for sp in axg.spines.values():
        sp.set_visible(False)
    fig.canvas.draw()
    bb = axg.get_position()                                   # actual map box after equal aspect
    cwx = fig.add_axes([bb.x0 + 0.01, 0.175, bb.width - 0.02, 0.018])
    cw = fig.colorbar(imw, cax=cwx, orientation="horizontal"); cw.outline.set_visible(False); cw.solids.set_alpha(0.85)
    cw.ax.tick_params(labelsize=5.6, length=2)
    cw.set_label("(200) width, nm⁻¹", fontsize=6, labelpad=1)
    axg.legend(loc="upper center", bbox_to_anchor=(0.5, -0.29), ncol=4, frameon=False, fontsize=5.8,
               handletextpad=0.1, columnspacing=0.7, markerscale=1.8)
    fig.text(0.01, 0.955, "(a) Sample and one design", fontsize=7.8, color=INK)

    # (b)
    axb = fig.add_axes([0.40, 0.24, 0.365, 0.56])
    lo_y, hi_y = -0.16, 0.14
    axb.axhspan(0, hi_y, color=RED, alpha=0.05, lw=0, zorder=0); axb.axhspan(lo_y, 0, color=BLUE, alpha=0.05, lw=0, zorder=0)
    xpos = {("fitted", j): j for j in range(3)}; xpos.update({("nugget", j): 3.6 + j for j in range(3)})
    for kernel in ("fitted", "nugget"):
        for j in range(3):
            x0 = xpos[(kernel, j)]
            for side, cut, col in ((-1, "uq", ORANGE), (1, "contract", PURPLE)):
                v = A[(kernel, cut)]["d"][:, j]
                y = np.linspace(lo_y, hi_y, 600)
                dd = gaussian_kde(v, bw_method=0.35)(y); dd = dd / dd.max() * 0.4; k = dd > 0.004
                q = float(np.quantile(v, CONF))
                low = k & (y <= q); high = k & (y >= q)
                axb.fill_betweenx(y[low], x0, x0 + side * dd[low], color=col, alpha=0.8, lw=0, zorder=3)
                axb.fill_betweenx(y[high], x0, x0 + side * dd[high], facecolor="white", lw=0, zorder=2)
                axb.fill_betweenx(y[high], x0, x0 + side * dd[high], color=col, alpha=0.35, lw=0, zorder=3)
                wq = float(np.interp(q, y, dd))
                axb.plot([x0, x0 + side * max(wq, 0.07)], [q, q], color=INK, lw=1.0, zorder=4)
                axb.text(x0 + side * 0.25, lo_y - 0.048, f"{A[(kernel, cut)]['measured'][j]:.0f}", ha="center", va="top",
                         fontsize=5.8, color=col, clip_on=False)
        mid = np.mean([xpos[(kernel, j)] for j in range(3)])
        axb.text(mid, hi_y - 0.004, f"{KLAB[kernel]} kernel", ha="center", va="top", fontsize=7.0, color=INK,
                 fontweight="bold", zorder=6)
        axb.text(mid, lo_y - 0.088, f"total {A[(kernel, 'uq')]['total']:.0f} and {A[(kernel, 'contract')]['total']:.0f}",
                 ha="center", va="top", fontsize=6.0, color=INK2, clip_on=False)
    axb.axhline(0, color=INK, lw=0.9, zorder=5)
    axb.axvline(2.8, color=INK2, lw=0.6, ls=(0, (2, 2)))
    ticks = [xpos[(k, j)] for k in ("fitted", "nugget") for j in range(3)]
    axb.set_xticks(ticks, [f"round {j + 1}" for _ in range(2) for j in range(3)], fontsize=6.3)
    axb.text(-0.62, lo_y - 0.048, "measured", ha="right", va="top", fontsize=6, color=INK, clip_on=False)
    axb.text(6.15, 0.085, "unwanted\nlooseness", fontsize=6, color=RED, style="italic", ha="right", va="center", zorder=1)
    axb.text(6.15, -0.135, "unwanted\nconservatism", fontsize=6, color=BLUE, style="italic", ha="right", va="center", zorder=1)
    axb.set_xlim(-0.55, 6.15); axb.set_ylim(lo_y, hi_y)
    axb.set_ylabel("wrong skips: delivered minus\nstated bound (share of round)", fontsize=6.6, labelpad=1)
    axb.tick_params(axis="y", labelsize=6.2)
    for s_ in ("top", "right"):
        axb.spines[s_].set_visible(False)
    fig.text(0.315, 0.955, "(b) Delivered against stated, 80 campaigns per round", fontsize=7.8, color=INK)
    fig.text(0.40, 0.895, "own word (left halves)", fontsize=6.6, color=ORANGE, fontweight="bold")
    fig.text(0.58, 0.895, "contract (right halves)", fontsize=6.6, color=PURPLE, fontweight="bold")
    fig.text(0.40, 0.845, "dark: lowest 80 % of campaigns, ending at the tick;\ncalibrated if the tick lies on zero", fontsize=5.7, color=INK2, linespacing=1.1)

    # (c)
    axc = fig.add_axes([0.86, 0.24, 0.125, 0.56])
    axc.axhline(CONF, color=INK, lw=0.9, ls=(0, (4, 3)))
    axc.text(3.48, CONF - 0.008, "promised", fontsize=5.8, color=INK, ha="right", va="top")
    for kernel, mfc_on, dx in (("fitted", True, -0.08), ("nugget", False, 0.08)):
        for cut, col, mk, off in (("uq", ORANGE, "o", -0.12), ("contract", PURPLE, "s", 0.12)):
            d = A[(kernel, cut)]["d"]; n = d.shape[0]
            for j in range(3):
                kk = int((d[:, j] <= 1e-12).sum()); lo, hi = cp(kk, n)
                x = j + 1 + off + dx
                axc.plot([x, x], [lo, hi], color=col, lw=0.9)
                axc.plot(x, kk / n, mk, ms=4.2, mfc=col if mfc_on else "white", mec=col if not mfc_on else INK,
                         mew=1.0 if not mfc_on else 0.5, zorder=3)
    axc.set_xlim(0.5, 3.5); axc.set_ylim(0.5, 1.02)
    axc.set_xticks([1, 2, 3], ["1", "2", "3"], fontsize=6.3); axc.set_xlabel("round", fontsize=6.6)
    axc.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0]); axc.tick_params(axis="y", labelsize=6.2)
    axc.set_ylabel("campaigns within\ntheir stated bound", fontsize=6.6, labelpad=1)
    for s_ in ("top", "right"):
        axc.spines[s_].set_visible(False)
    axc.text(0.55, 0.53, "filled: fitted noise\nhollow: fixed nugget", fontsize=5.6, color=INK, va="bottom")
    fig.text(0.805, 0.955, "(c) Promise kept", fontsize=7.8, color=INK)

    for ext in ("png", "pdf", "svg"):
        fig.savefig(FIG / f"fig_hook3.{ext}", dpi=300)
    for kk, v in A.items():
        print(kk, "q80", np.quantile(v["d"], CONF, axis=0).round(3), "within", (v["d"] <= 1e-12).mean(0).round(3), "total", round(v["total"]))


if __name__ == "__main__":
    main()
