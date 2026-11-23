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
    axa = fig.add_axes([0.09, 0.56, 0.50, 0.33])
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
    axa.text(-0.5, 0.33 * S, f"requested: at most {EPS:.2f} in 80 % of campaigns (dashed)", ha="left", va="center",
             fontsize=6.8, color=INK)
    axa.set_xticks(range(4), [f"level {L}" for L in levels]); axa.set_xlim(-0.55, 3.6)
    axa.set_ylim(0, 0.36 * S); axa.set_yticks(np.round(np.arange(0, 0.31 * S, 0.1 * S), 3))
    axa.set_ylabel("share of the level\nskipped wrongly", labelpad=2)
    axa.grid(axis="y", color=GRID, lw=0.4, alpha=0.6)
    for s in ("top", "right"):
        axa.spines[s].set_visible(False)
    fig.text(0.02, 0.96, "(a) Delivered: the share that 80 % of the 80 campaigns stay at or below", fontsize=8, color=INK)
    fig.text(0.09, 0.925, "own word (left)", fontsize=7.2, color=ORANGE, fontweight="bold")
    fig.text(0.215, 0.925, f"{m_own.mean():.0f} ± {m_own.std():.0f} measured", fontsize=7, color=INK)
    fig.text(0.37, 0.925, "contract (right)", fontsize=7.2, color=PURPLE, fontweight="bold")
    fig.text(0.49, 0.925, f"{m_con.mean():.0f} ± {m_con.std():.0f} measured", fontsize=7, color=INK)

    # (b) calibration
    axb = fig.add_axes([0.72, 0.56, 0.25, 0.33])
    lim = 0.32
    axb.plot([0, lim], [0, lim], color=INK2, lw=0.8, ls=(0, (4, 3)))
    for st, X, col, mk in ((stated_own, own_over, ORANGE, "o"), (stated_con, con_over, PURPLE, "s")):
        for j in range(4):
            k = int(X[:, j].sum()); lo, hi = cp(k, n)
            axb.plot([st[j], st[j]], [lo, hi], color=col, lw=1.0, alpha=0.8)
            axb.plot(st[j], k / n, mk, ms=4.5, color=col, mec=INK, mew=0.6, zorder=3)
            axb.text(st[j] + 0.006, k / n, str(levels[j]), fontsize=6, color=col, va="center")
    axb.set_xlim(0, lim); axb.set_ylim(0, lim)
    axb.set_xticks([0, 0.1, 0.2, 0.3]); axb.set_yticks([0, 0.1, 0.2, 0.3])
    axb.set_xlabel("stated chance of exceeding\nthe budget, before deciding")
    axb.set_ylabel("realised over 80 campaigns")
    axb.grid(color=GRID, lw=0.4, alpha=0.5)
    for s in ("top", "right"):
        axb.spines[s].set_visible(False)
    fig.text(0.66, 0.96, "(b) Stated and realised, by level", fontsize=8, color=INK)
    to, tc = tests["own"], tests["contract"]
    axb.text(0.01, 0.31, "level trend\n" + ("own word p < 5·10⁻⁵" if to["p_trend"] < 5e-5 else f"own word p = {to['p_trend']:.3f}")
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
    axl = fig.add_axes([0.22, 0.02, 0.28, 0.38]); axr = fig.add_axes([0.50, 0.02, 0.28, 0.38])
    im = axl.imshow(maps["own"], **kw); axr.imshow(maps["contract"][:, ::-1], **kw)
    for ax, t, c in ((axl, "own word", ORANGE), (axr, "contract (mirrored)", PURPLE)):
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_title(t, fontsize=7.5, color=c, fontweight="bold")
    fig.text(0.02, 0.44, "(c) Where sites are skipped wrongly: share of the 80 campaigns, per site", fontsize=8, color=INK)
    cax = fig.add_axes([0.83, 0.07, 0.018, 0.25])
    cb = fig.colorbar(im, cax=cax, ticks=np.round(np.linspace(0, 0.8 * S, 5), 2))
    cb.outline.set_visible(False); cb.ax.tick_params(labelsize=6.5, length=2)
    ins = fig.add_axes([0.04, 0.12, 0.14, 0.18])
    ins.imshow(img, origin="lower", cmap="magma", interpolation="nearest",
               vmin=np.nanpercentile(img, 5), vmax=np.nanpercentile(img, 95))
    ins.set_xticks([]); ins.set_yticks([])
    for sp in ins.spines.values():
        sp.set_color(INK2); sp.set_linewidth(0.5)
    ins.set_title("measured (200) width", fontsize=6.5, color=INK)

    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"fig_hook_request{TAG}.{ext}", dpi=300)
    print({L: (round(float(np.quantile(own[:, j], .8)), 3), round(float(np.quantile(con[:, j], .8)), 3)) for j, L in enumerate(levels)})


if __name__ == "__main__":
    main()
