"""
Figure 1 (round 9): specified and calibrated in advance. Same runs as fig_hook3.py (experiments/paired_gp.py):
NaCl (200)-width scan, 80 fresh hierarchical designs, three rounds, budget 0.20 per round at confidence 0.80;
per round the same frozen Gaussian process and the same held-out calibration draw; the cut on the leftover sites is
set by the process's own uncertainty or by the calibration draw, each shown in the campaigns it drives; two kernels.

(a) Measured width with the seed and the three rounds of one design.
(b) Share of campaigns whose wrong skips stayed within the bound stated before the round, against the 80 % promised
    (Clopper-Pearson 95 %). Above the line: budget left unused; below: promise broken.

    python manuscript/figures/fig_hook4.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

FIG = Path(__file__).resolve().parent
ROOT = FIG.parents[1]
sys.path.insert(0, str(FIG)); sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "src"))
from fig_hook3 import BLUE, CONF, INK, INK2, KLAB, ORANGE, PURPLE, RED, arm, cp  # noqa: E402


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

    fig = plt.figure(figsize=(7.2, 3.3))
    # (a) sample and one design
    axg = fig.add_axes([0.02, 0.25, 0.30, 0.60]); axg.set_facecolor("#f4f3ef")
    vmin, vmax = np.nanpercentile(img, 5), np.nanpercentile(img, 95)
    imw = axg.imshow(img, origin="lower", cmap="viridis", alpha=0.85, vmin=vmin, vmax=vmax, interpolation="nearest")
    rxy = xy[np.asarray(ds.meta["raster_index"])]
    dix = np.searchsorted(xs, rxy[:, 0].round(4)); diy = np.searchsorted(ys, rxy[:, 1].round(4)); lv = np.asarray(ds.levels)
    axg.scatter(dix[lv <= 3], diy[lv <= 3], s=7, c="white", marker="s", lw=0.6, edgecolors="black", zorder=5, label="seed")
    for r, (L, sz) in enumerate(zip((4, 5, 6), (4, 1.8, 0.6))):
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
    bb = axg.get_position()
    cwx = fig.add_axes([bb.x0 + 0.01, 0.175, bb.width - 0.02, 0.018])
    cw = fig.colorbar(imw, cax=cwx, orientation="horizontal"); cw.outline.set_visible(False); cw.solids.set_alpha(0.85)
    cw.ax.tick_params(labelsize=5.8, length=2); cw.set_label("(200) width, nm⁻¹", fontsize=6.2, labelpad=1)
    axg.legend(loc="upper center", bbox_to_anchor=(0.5, -0.27), ncol=4, frameon=False, fontsize=6,
               handletextpad=0.1, columnspacing=0.8, markerscale=1.8)
    fig.text(0.01, 0.955, "(a) Sample and one design", fontsize=7.8, color=INK)

    # (b) promise kept
    axb = fig.add_axes([0.45, 0.25, 0.53, 0.60])
    lo, hi = 0.5, 1.09
    axb.axhspan(CONF, hi, color=BLUE, alpha=0.06, lw=0, zorder=0)
    axb.axhspan(lo, CONF, color=RED, alpha=0.06, lw=0, zorder=0)
    axb.axhline(CONF, color=INK, lw=1.0, zorder=2)
    gx = {"fitted": 0.0, "nugget": 3.8}
    for kernel in ("fitted", "nugget"):
        for j in range(3):
            for cut, col, mk, off in (("uq", ORANGE, "o", -0.16), ("contract", PURPLE, "s", 0.16)):
                d = A[(kernel, cut)]["d"]; n = d.shape[0]
                kk = int((d[:, j] <= 1e-12).sum()); l_, h_ = cp(kk, n)
                x = gx[kernel] + j + off
                axb.plot([x, x], [l_, h_], color=col, lw=1.3, zorder=3, solid_capstyle="butt")
                axb.plot(x, kk / n, mk, ms=6, color=col, mec=INK, mew=0.6, zorder=4)
        mid = gx[kernel] + 1
        axb.text(mid, hi - 0.003, f"{KLAB[kernel]} kernel", ha="center", va="top", fontsize=7.4, color=INK, fontweight="bold")
        axb.text(mid, lo - 0.115, f"measured: {A[(kernel, 'uq')]['total']:.0f} own word, "
                                  f"{A[(kernel, 'contract')]['total']:.0f} contract",
                 ha="center", va="top", fontsize=6.2, color=INK2, clip_on=False)
    axb.axvline(2.9, color=INK2, lw=0.6, ls=(0, (2, 2)))
    axb.text(6.75, 1.035, "budget left unused", ha="right", va="center", fontsize=6.4, color=BLUE, style="italic")
    axb.text(6.75, 0.52, "promise broken", ha="right", va="bottom", fontsize=6.4, color=RED, style="italic")
    axb.text(-0.45, CONF + 0.006, "promised: 80 %", ha="left", va="bottom", fontsize=6.4, color=INK)
    ticks = [gx[k] + j for k in ("fitted", "nugget") for j in range(3)]
    axb.set_xticks(ticks, [f"round {j + 1}" for _ in range(2) for j in range(3)], fontsize=6.6)
    axb.set_xlim(-0.5, 6.8); axb.set_ylim(lo, hi)
    axb.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0], ["50 %", "60 %", "70 %", "80 %", "90 %", "100 %"])
    axb.tick_params(axis="y", labelsize=6.6)
    axb.set_ylabel("campaigns within the bound\nstated before the round", fontsize=7, labelpad=2)
    for s_ in ("top", "right"):
        axb.spines[s_].set_visible(False)
    fig.text(0.40, 0.955, "(b) Was the stated bound kept? 80 campaigns per round", fontsize=7.8, color=INK)
    fig.text(0.45, 0.895, "●", fontsize=8, color=ORANGE); fig.text(0.47, 0.895, "process's own word", fontsize=7, color=ORANGE, fontweight="bold")
    fig.text(0.64, 0.895, "■", fontsize=8, color=PURPLE); fig.text(0.66, 0.895, "contract (calibration draw)", fontsize=7, color=PURPLE, fontweight="bold")

    for ext in ("png", "pdf", "svg"):
        fig.savefig(FIG / f"fig_hook4.{ext}", dpi=300)


if __name__ == "__main__":
    main()
