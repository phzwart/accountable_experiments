"""
Figure 1 (round 5): specified and calibrated in advance. NaCl (200)-width scan, 80 fresh hierarchical designs,
one Gaussian process (presence and log width) on the staged plan, budget 0.20 per level at confidence 0.80.
The two rules differ only in who sets the cut on each level: the process's own statement, or a uniform
calibration draw of 40 sites with the exact hypergeometric cut (the contract).

(a) Split violins per level: share of the level skipped wrongly over the 80 designs, own word (left) and
    contract (right); budget line; share of designs over budget printed above.
(b) Mirrored heatmap: designs (rows) by level, own word mirrored to the left of the contract, colour the share
    of the level skipped wrongly on a diverging scale centred on the budget. Inset: the measured (200) width.

    python manuscript/figures/fig_hook_calibrated.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from scipy.stats import gaussian_kde

FIG = Path(__file__).resolve().parent
ROOT = FIG.parents[1]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#b9b8b3"
ORANGE, PURPLE = "#eb6834", "#8e6cc8"
import os
EPS = float(os.environ.get("STAGED_EPS", 0.20))
RES = "results/revision2/staged_gp_designs_v2.jsonl" if EPS == 0.20 else f"results/revision2/staged_gp_designs_eps{int(round(100 * EPS))}.jsonl"
S = EPS / 0.20
TAG = "" if EPS == 0.20 else f"_eps{int(round(100 * EPS))}"
DIV = LinearSegmentedColormap.from_list("div", ["#2f5f9e", "#9fbbe0", "#f2f1ed", "#efa58c", "#b8391f"])


def shares():
    rr = [json.loads(l) for l in open(ROOT / RES)]
    own = np.array([[l["realised"] / l["N"] for l in r["own"]] for r in rr])
    con = np.array([[l["W_level"] / l["N"] for l in r["contract"]] for r in rr])
    own_over = np.array([[l["realised"] > np.floor(EPS * l["N"]) for l in r["own"]] for r in rr])
    con_over = np.array([[l["W_level"] > np.floor(EPS * l["N"]) for l in r["contract"]] for r in rr])
    m_own = np.array([r["own"][-1]["measured_after"] for r in rr])
    m_con = np.array([r["contract"][-1]["measured_after"] for r in rr])
    return own, con, own_over, con_over, m_own, m_con


def half_violin(ax, x, v, side, col, width=0.38):
    y = np.linspace(0, 0.6 * S, 300)
    d = gaussian_kde(v, bw_method=0.35)(y); d = d / d.max() * width
    keep = d > 0.01 * width; y, d = y[keep], d[keep]
    xs = x - d if side < 0 else x + d
    ax.fill_betweenx(y, x, xs, color=col, alpha=0.55, lw=0)
    ax.plot(xs, y, color=col, lw=0.8)
    q1, q2, q3 = np.percentile(v, [25, 50, 75])
    off = -0.09 if side < 0 else 0.09
    ax.plot([x + off, x + off], [q1, q3], color=INK, lw=1.6, solid_capstyle="butt")
    ax.plot(x + off, q2, "o", ms=2.8, color="white", mec=INK, mew=0.8, zorder=3)


def site_maps(shape, raster_iy, raster_ix):
    rr = [json.loads(l) for l in open(ROOT / RES)]
    n = len(raster_iy); dec = np.zeros(n); wrong = {k: np.zeros(n) for k in ("own", "contract")}
    for r in rr:
        dec[r["decided"]] += 1
        for k in wrong:
            for l in r[k]:
                wrong[k][l["wrong_idx"]] += 1
    maps = {}
    for k in wrong:
        img = np.full(shape, np.nan)
        ok = dec > 0
        img[raster_iy[ok], raster_ix[ok]] = wrong[k][ok] / dec[ok]
        maps[k] = img
    return maps, len(rr)


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK})
    own, con, own_over, con_over, m_own, m_con = shares()
    tests = json.load(open(ROOT / RES.replace(".jsonl", "_trend_tests.json")))
    rr = [json.loads(l) for l in open(ROOT / RES)]
    nominal = np.array([[l["delta_picked"] for l in r["contract"]] for r in rr]).mean(0)
    stated = np.array([[l["stated_over"] for l in r["own"]] for r in rr]).mean(0)
    levels = [3, 4, 5, 6]

    fig = plt.figure(figsize=(7.2, 3.5))
    axa = fig.add_axes([0.145, 0.10, 0.43, 0.66])

    # (a) split violins
    for j, L in enumerate(levels):
        half_violin(axa, j, own[:, j], -1, ORANGE)
        half_violin(axa, j, con[:, j], +1, PURPLE)
        for side, v, col in ((-1, own[:, j], ORANGE), (1, con[:, j], PURPLE)):     # achieved PAC bound at 0.80
            qa = np.quantile(v, 0.80)
            axa.plot([j, j + 0.36 * side], [qa, qa], color=col, lw=2.2, solid_capstyle="butt", zorder=4)
            axa.plot([j, j + 0.36 * side], [qa, qa], color=INK, lw=0.6, zorder=5)
        for y, (a, b) in (((0.475 if S == 1 else 0.535) * S, (own_over[:, j].mean(), con_over[:, j].mean())), ((0.44 if S == 1 else 0.50) * S, (stated[j], nominal[j]))):
            axa.text(j - 0.2, y, f"{100 * a:.0f} %", ha="center", fontsize=7, color=ORANGE)
            axa.text(j + 0.2, y, f"{100 * b:.0f} %", ha="center", fontsize=7, color=PURPLE)
    axa.text(-0.62, (0.482 if S == 1 else 0.542) * S, "over budget", ha="right", va="center", fontsize=6.5, color=INK, clip_on=False)
    axa.text(-0.62, (0.447 if S == 1 else 0.507) * S, "stated", ha="right", va="center", fontsize=6.5, color=INK2, clip_on=False)
    axa.axhline(EPS, color=INK2, lw=0.8, ls=(0, (4, 3)))
    axa.text(3.62, EPS - 0.006 * S, "budget", ha="right", va="top", fontsize=7, color=INK2)
    axa.annotate("achieved bound: 80 % of\ndesigns at or below", (3.25, np.quantile(con[:, 3], 0.8)), (2.2, 0.35 * S),
                 fontsize=6.5, color=INK, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
    axa.set_xticks(range(4), [f"level {L}" for L in levels]); axa.set_xlim(-0.6, 3.65); axa.set_ylim(0, (0.5 if S == 1 else 0.56) * S)
    axa.set_yticks(np.round(np.arange(0, 0.41 * S, 0.1 * S), 3))
    axa.set_ylabel("share of the level skipped wrongly", labelpad=2)
    axa.grid(axis="y", color=GRID, lw=0.4, alpha=0.6)
    for s in ("top", "right"):
        axa.spines[s].set_visible(False)
    tc = tests["contract"]
    fig.text(0.02, 0.94, "(a) One process, one plan, 80 designs", fontsize=8, color=INK)
    fig.text(0.02, 0.885, "own word", fontsize=7.5, color=ORANGE, fontweight="bold")
    fig.text(0.105, 0.885, f"measured {m_own.mean():.0f} ± {m_own.std():.0f}, level trend " + (f"p < 5·10⁻⁵" if tests['own']['p_trend'] < 5e-5 else f"p = {tests['own']['p_trend']:.3f}"), fontsize=7, color=INK)
    fig.text(0.02, 0.845, "contract", fontsize=7.5, color=PURPLE, fontweight="bold")
    fig.text(0.105, 0.845, f"measured {m_con.mean():.0f} ± {m_con.std():.0f}, level trend p = {tc['p_trend']:.2f}", fontsize=7, color=INK)

    # (b) mirrored spatial heatmaps of the probability that a site is skipped wrongly
    sys.path.insert(0, str(FIG)); sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "src"))
    from fig_datasets import nacl_fwhm
    from experiments.nacl_saxs.adapter import load
    img, pres, (xs, ys), _, _ = nacl_fwhm()
    _, grid = load()
    xy = np.asarray(grid["xy_mm"], float)
    rix = np.searchsorted(xs, xy[:, 0].round(4)); riy = np.searchsorted(ys, xy[:, 1].round(4))
    maps, nd = site_maps(img.shape, riy, rix)
    cmap = plt.get_cmap("Reds").copy(); cmap.set_bad("#e9e8e4")
    axl = fig.add_axes([0.615, 0.20, 0.18, 0.56]); axr = fig.add_axes([0.795, 0.20, 0.18, 0.56])
    kw = dict(origin="lower", cmap=cmap, vmin=0, vmax=0.8 * S, interpolation="nearest", aspect="equal")
    im = axl.imshow(maps["own"], **kw)
    axr.imshow(maps["contract"][:, ::-1], **kw)                                  # mirrored about the seam
    for ax, t, c in ((axl, "own word", ORANGE), (axr, "contract (mirrored)", PURPLE)):
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_title(t, fontsize=7.5, color=c, fontweight="bold")
    fig.text(0.615, 0.94, "(b) Where sites are skipped wrongly", fontsize=8, color=INK)
    cax = fig.add_axes([0.66, 0.085, 0.27, 0.022])
    cb = fig.colorbar(im, cax=cax, orientation="horizontal", ticks=np.round(np.linspace(0, 0.8 * S, 5), 2))
    cb.outline.set_visible(False); cb.ax.tick_params(labelsize=6.5, length=2)
    cax.set_title(f"share of the {nd} designs in which the site was skipped wrongly", fontsize=6.5, pad=2)
    # inset: the measured width
    ins = fig.add_axes([0.905, 0.80, 0.07, 0.13])
    ins.imshow(img, origin="lower", cmap="magma", interpolation="nearest",
               vmin=np.nanpercentile(img, 5), vmax=np.nanpercentile(img, 95))
    ins.set_xticks([]); ins.set_yticks([])
    for sp in ins.spines.values():
        sp.set_color(INK2); sp.set_linewidth(0.5)
    ins.text(-0.08, 0.5, "measured\nwidth", transform=ins.transAxes, ha="right", va="center", fontsize=6.5)

    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"fig_hook_calibrated{TAG}.{ext}", dpi=300)
    print("own over by level", own_over.mean(0), "contract", con_over.mean(0), "nominal", nominal.round(3))


if __name__ == "__main__":
    main()
