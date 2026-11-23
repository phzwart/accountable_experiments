"""
Figure 1 (round 6): what was requested, and what was delivered. Same runs as fig_hook_calibrated.py
(80 fresh designs, one Gaussian process on the staged plan, budget EPS per level at confidence 0.80).

The request is a PAC statement: the share of a level skipped wrongly stays at or below the budget in at least
80 % of campaigns. What answers it is the 80th percentile of that share over campaigns (the achieved bound),
and how often the budget is exceeded against the rate each rule stated before deciding.

(a) Achieved bound per level with a 95 % bootstrap interval over designs; distributions faint behind.
(b) Calibration: stated against realised chance of exceeding the budget, per level, Clopper-Pearson 95 %.
(c) Mirrored maps: share of designs in which each site was skipped wrongly; inset the measured width.

    [STAGED_EPS=0.10] python manuscript/figures/fig_hook_request.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import beta

FIG = Path(__file__).resolve().parent
sys.path.insert(0, str(FIG))
from fig_hook_calibrated import (EPS, INK, INK2, GRID, ORANGE, PURPLE, RES, ROOT, S, TAG, half_violin,  # noqa: E402
                                 shares, site_maps)


def cp(k, n, a=0.05):
    return (beta.ppf(a / 2, k, n - k + 1) if k > 0 else 0.0, beta.ppf(1 - a / 2, k + 1, n - k) if k < n else 1.0)


def boot_q(v, q=0.80, B=4000, seed=0):
    rng = np.random.default_rng(seed)
    b = np.quantile(v[rng.integers(0, len(v), (B, len(v)))], q, axis=1)
    return np.quantile(v, q), np.percentile(b, [2.5, 97.5])


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK})
    own, con, own_over, con_over, m_own, m_con = shares()
    rr = [json.loads(l) for l in open(ROOT / RES)]
    stated_con = np.array([[l["delta_picked"] for l in r["contract"]] for r in rr]).mean(0)
    stated_own = np.array([[l["stated_over"] for l in r["own"]] for r in rr]).mean(0)
    tests = json.load(open(ROOT / RES.replace(".jsonl", "_trend_tests.json")))
    n = len(rr); levels = [3, 4, 5, 6]

    fig = plt.figure(figsize=(7.2, 5.0))

    # (a) achieved bound
    axa = fig.add_axes([0.09, 0.60, 0.50, 0.29])
    for j in range(4):
        for side, v, col in ((-1, own[:, j], ORANGE), (1, con[:, j], PURPLE)):
            vv = half_violin.__wrapped__ if hasattr(half_violin, "__wrapped__") else None  # noqa: F841
            y = np.linspace(0, 0.6 * S, 300)
            from scipy.stats import gaussian_kde
            d = gaussian_kde(v, bw_method=0.35)(y); d = d / d.max() * 0.34; keep = d > 0.0034
            xs = j + side * d[keep]
            axa.fill_betweenx(y[keep], j, xs, color=col, alpha=0.13, lw=0)
            qa, (lo, hi) = boot_q(v)
            x = j + side * 0.17
            axa.plot([x, x], [lo, hi], color=col, lw=1.4, solid_capstyle="butt")
            axa.plot(x, qa, "o", ms=5, color=col, mec=INK, mew=0.7, zorder=4)
    axa.axhline(EPS, color=INK, lw=1.0, ls=(0, (4, 3)))
    axa.text(-0.5, 0.325 * S, f"requested per round (dashed): at most {EPS:.2f} of its sites\nskipped wrongly, in at least 80 % of campaigns", ha="left", va="center",
             fontsize=6.8, color=INK)
    Nmean = np.array([[l["N"] for l in r["own"]] for r in rr]).mean(0)
    axa.set_xticks(range(4), [f"round {j + 1}\n{Nmean[j]:.0f} sites" for j in range(4)])
    axa.annotate("", xy=(3.45, -0.105 * S), xytext=(-0.35, -0.105 * S), xycoords="data", annotation_clip=False,
                 arrowprops=dict(arrowstyle="->", color=INK2, lw=0.7))
    axa.text(1.55, -0.118 * S, "coarse to fine", ha="center", va="top", fontsize=6.5, color=INK2, clip_on=False); axa.set_xlim(-0.55, 3.6)
    axa.set_ylim(0, 0.36 * S); axa.set_yticks(np.round(np.arange(0, 0.31 * S, 0.1 * S), 3))
    axa.set_ylabel("share of the round's sites\nskipped wrongly", labelpad=2)
    axa.grid(axis="y", color=GRID, lw=0.4, alpha=0.6)
    for s in ("top", "right"):
        axa.spines[s].set_visible(False)
    fig.text(0.02, 0.99, "A campaign decides in four rounds, each over a finer set of sites; rounds are the levels of Section 3.", fontsize=7.3, color=INK2, va="top")
    fig.text(0.02, 0.945, "(a) Delivered: the share that 80 % of the 80 campaigns stay at or below", fontsize=8, color=INK)
    fig.text(0.09, 0.91, "own word (left)", fontsize=7.2, color=ORANGE, fontweight="bold")
    fig.text(0.215, 0.91, f"{m_own.mean():.0f} ± {m_own.std():.0f} measured", fontsize=7, color=INK)
    fig.text(0.37, 0.91, "contract (right)", fontsize=7.2, color=PURPLE, fontweight="bold")
    fig.text(0.49, 0.91, f"{m_con.mean():.0f} ± {m_con.std():.0f} measured", fontsize=7, color=INK)

    # (b) calibration
    axb = fig.add_axes([0.72, 0.60, 0.25, 0.29])
    lim = 0.32
    axb.plot([0, lim], [0, lim], color=INK2, lw=0.8, ls=(0, (4, 3)))
    for st, X, col, mk in ((stated_own, own_over, ORANGE, "o"), (stated_con, con_over, PURPLE, "s")):
        for j in range(4):
            k = int(X[:, j].sum()); lo, hi = cp(k, n)
            axb.plot([st[j], st[j]], [lo, hi], color=col, lw=1.0, alpha=0.8)
            axb.plot(st[j], k / n, mk, ms=4.5, color=col, mec=INK, mew=0.6, zorder=3)
            axb.text(st[j] + 0.006, k / n, str(j + 1), fontsize=6, color=col, va="center")
    axb.set_xlim(0, lim); axb.set_ylim(0, lim)
    axb.set_xticks([0, 0.1, 0.2, 0.3]); axb.set_yticks([0, 0.1, 0.2, 0.3])
    axb.set_xlabel("stated chance of exceeding the\nrequest, before the round is decided")
    axb.set_ylabel("realised over 80 campaigns")
    axb.grid(color=GRID, lw=0.4, alpha=0.5)
    for s in ("top", "right"):
        axb.spines[s].set_visible(False)
    fig.text(0.66, 0.945, "(b) Stated and realised, by round", fontsize=8, color=INK)
    to, tc = tests["own"], tests["contract"]
    axb.text(0.01, 0.31, "trend over rounds\n" + ("own word p < 5·10⁻⁵" if to["p_trend"] < 5e-5 else f"own word p = {to['p_trend']:.3f}")
             + f"\ncontract p = {tc['p_trend']:.2f}", fontsize=6.3, color=INK, va="top")

    # (c) mirrored maps
    sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "src"))
    from fig_datasets import nacl_fwhm
    from experiments.nacl_saxs.adapter import load
    img, pres, (xs_, ys_), _, _ = nacl_fwhm()
    _, grid = load()
    xy = np.asarray(grid["xy_mm"], float)
    rix = np.searchsorted(xs_, xy[:, 0].round(4)); riy = np.searchsorted(ys_, xy[:, 1].round(4))
    maps, nd = site_maps(img.shape, riy, rix)
    cmap = plt.get_cmap("Reds").copy(); cmap.set_bad("#e9e8e4")
    kw = dict(origin="lower", cmap=cmap, vmin=0, vmax=0.8 * S, interpolation="nearest", aspect="equal")
    W, H0, Y0 = 0.25, 0.315, 0.075
    axw = fig.add_axes([0.085, Y0, W, H0]); axl = fig.add_axes([0.37, Y0, W, H0]); axr = fig.add_axes([0.655, Y0, W, H0])
    imw = axw.imshow(img, origin="lower", cmap="Greys", interpolation="nearest", aspect="equal", alpha=0.6,
                     vmin=np.nanpercentile(img, 5), vmax=np.nanpercentile(img, 95))
    # one design (the paper's): seed and the four rounds, coarse to fine
    ds_, _ = load()
    rxy = np.asarray(grid["xy_mm"], float)[np.asarray(ds_.meta["raster_index"])]
    dix = np.searchsorted(xs_, rxy[:, 0].round(4)); diy = np.searchsorted(ys_, rxy[:, 1].round(4))
    lvd = np.asarray(ds_.levels)
    ROUND_COL = ["#0b3c5d", "#1a7a96", "#2fb3c3", "#7fd6d2"]
    axw.scatter(dix[lvd <= 2], diy[lvd <= 2], s=9, c=INK, marker="s", lw=0, label="seed")
    for r, (L, sz) in enumerate(zip((3, 4, 5, 6), (8, 4.5, 2.2, 0.9))):
        m = lvd == L
        axw.scatter(dix[m], diy[m], s=sz, c=ROUND_COL[r], lw=0, label=f"round {r + 1}")
    axw.legend(loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=5, frameon=False, fontsize=5.8,
               handletextpad=0.1, columnspacing=0.6, markerscale=2.2)
    axw.set_xlim(-0.5, img.shape[1] - 0.5); axw.set_ylim(-0.5, img.shape[0] - 0.5)
    im = axl.imshow(maps["own"], **kw); axr.imshow(maps["contract"], **kw)
    for ax, t, c in ((axw, "measured width and one design", INK), (axl, "own word", ORANGE), (axr, "contract", PURPLE)):
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_title(t, fontsize=7.5, color=c, fontweight="bold")
    fig.text(0.02, 0.44, "(c) The measured width, and where sites are skipped wrongly (share of the 80 campaigns, per site)",
             fontsize=8, color=INK)
    cax = fig.add_axes([0.915, Y0 + 0.04, 0.014, H0 - 0.08])
    cb = fig.colorbar(im, cax=cax, ticks=np.round(np.linspace(0, 0.8 * S, 5), 2))
    cb.outline.set_visible(False); cb.ax.tick_params(labelsize=6.5, length=2)
    cb.set_label("skipped wrongly", fontsize=6.5)
    cwx = fig.add_axes([0.065, Y0 + 0.04, 0.010, H0 - 0.08])
    cw = fig.colorbar(imw, cax=cwx)
    cw.outline.set_visible(False); cw.ax.tick_params(labelsize=6, length=2)
    cwx.yaxis.set_ticks_position("left"); cwx.yaxis.set_label_position("left")
    cw.set_label("(200) width, nm⁻¹", fontsize=6)
    cw.solids.set_alpha(0.6)

    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"fig_hook_request{TAG}.{ext}", dpi=300)
    print({L: (round(float(np.quantile(own[:, j], .8)), 3), round(float(np.quantile(con[:, j], .8)), 3)) for j, L in enumerate(levels)})


if __name__ == "__main__":
    main()
