"""
Figure 1 (round 7): specified and calibrated in advance. NaCl (200)-width scan, 80 fresh hierarchical designs,
one Gaussian process on the staged plan (seed = levels 0-3, three rounds), budget 0.20 per round at
confidence 0.80. The two rules differ only in who sets the cut on each round.

(a) Measured width (viridis) with the seed and the three rounds of one design.
(b) Per round and campaign, delivered minus stated: the share of the round's sites skipped wrongly less the
    bound the rule stated for it before the round (its own 80 % statement for the own word; the exact
    calibration bound for the contract). Zero: the rule delivered what it stated. The dot marks the 80th
    percentile over campaigns (zero if the 80 % statement is calibrated), with a 95 % bootstrap interval.
(c) Stated against realised chance of going over the requested budget, per round; filled: this setting;
    hollow: the same scan with a two-round seed at budgets 0.20 and 0.10.

    python manuscript/figures/fig_hook2.py
Also writes the SI figure of wrong-skip maps (figS_wrong_maps.png).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde, hypergeom

FIG = Path(__file__).resolve().parent
ROOT = FIG.parents[1]
sys.path.insert(0, str(FIG)); sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "src"))
from fig_hook_request import boot_q, cp  # noqa: E402

INK, INK2, GRID = "#0b0b0b", "#52514e", "#b9b8b3"
ORANGE, PURPLE = "#eb6834", "#8e6cc8"
RED, BLUE = "#b8391f", "#2f5f9e"
CONF = 0.80
MAIN = ROOT / "results/revision2/staged_gp_designs_seed3.jsonl"
OTHER = [(ROOT / "results/revision2/staged_gp_designs_v2.jsonl", 0.20, "two-round seed, 0.20"),
         (ROOT / "results/revision2/staged_gp_designs_eps10.jsonl", 0.10, "two-round seed, 0.10")]


def contract_bound(l, conf=CONF):
    N, m, k = l["N"], l["m"], l["k_cal"]
    W = np.arange(k, N + 1)
    return (int(W[hypergeom.cdf(k, N, W, m) > 1 - conf].max()) - k) / N


def load(path):
    return [json.loads(l) for l in open(path)]


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK})
    rr = load(MAIN); n = len(rr); R = len(rr[0]["own"]); EPS = 0.20
    own = np.array([[l["realised"] / l["N"] for l in r["own"]] for r in rr])
    con = np.array([[l["realised"] / l["N"] for l in r["contract"]] for r in rr])
    st_own = np.array([[l["stated_q"] / l["N"] for l in r["own"]] for r in rr])
    st_con = np.array([[contract_bound(l) for l in r["contract"]] for r in rr])
    d_own, d_con = own - st_own, con - st_con
    Nmean = np.array([[l["N"] for l in r["own"]] for r in rr]).mean(0)
    m_own = np.array([[l["N"] - l["n_skip"] for l in r["own"]] for r in rr]).mean(0)
    m_con = np.array([[l["N"] - l["n_skip"] for l in r["contract"]] for r in rr]).mean(0)
    tot_own = np.array([r["own"][-1]["measured_after"] for r in rr]); tot_con = np.array([r["contract"][-1]["measured_after"] for r in rr])
    print("within own stated bound: own", (d_own <= 1e-12).mean(0).round(3), "contract", (d_con <= 1e-12).mean(0).round(3))

    from fig_datasets import nacl_fwhm
    from experiments.nacl_saxs.adapter import load as nload
    img, _, (xs, ys), _, _ = nacl_fwhm()
    ds, grid = nload()
    xy = np.asarray(grid["xy_mm"], float)

    fig = plt.figure(figsize=(7.2, 3.25))
    # (a) sample and one design
    axg = fig.add_axes([0.075, 0.19, 0.215, 0.64])
    axg.set_facecolor("#f4f3ef")
    vmin, vmax = np.nanpercentile(img, 5), np.nanpercentile(img, 95)
    imw = axg.imshow(img, origin="lower", cmap="viridis", alpha=0.85, vmin=vmin, vmax=vmax, interpolation="nearest")
    rxy = xy[np.asarray(ds.meta["raster_index"])]
    dix = np.searchsorted(xs, rxy[:, 0].round(4)); diy = np.searchsorted(ys, rxy[:, 1].round(4)); lv = np.asarray(ds.levels)
    axg.scatter(dix[lv <= 3], diy[lv <= 3], s=7, c="white", marker="s", lw=0.7, edgecolors="black", zorder=5, label="seed")
    for r, (L, sz) in enumerate(zip((4, 5, 6), (4, 1.8, 0.6))):
        m = lv == L
        if r == 0:
            axg.scatter(dix[m], diy[m], s=sz, facecolors="none", edgecolors="black", lw=0.6, zorder=4, label="round 1")
        else:
            axg.scatter(dix[m], diy[m], s=sz, c="#111111", lw=0, alpha=0.8, zorder=3, label=f"round {r + 1}")
    axg.set_xlim(-0.5, img.shape[1] - 0.5); axg.set_ylim(-0.5, img.shape[0] - 0.5)
    axg.set_xticks([]); axg.set_yticks([])
    for sp in axg.spines.values():
        sp.set_visible(False)
    axg.legend(loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=4, frameon=False, fontsize=5.6,
               handletextpad=0.05, columnspacing=0.4, markerscale=1.6)
    cwx = fig.add_axes([0.05, 0.26, 0.008, 0.50])
    cw = fig.colorbar(imw, cax=cwx); cw.outline.set_visible(False); cw.solids.set_alpha(0.85)
    cw.ax.tick_params(labelsize=5.5, length=2); cwx.yaxis.set_ticks_position("left"); cwx.yaxis.set_label_position("left")
    cw.set_label("(200) width, nm⁻¹", fontsize=5.8, labelpad=1)
    fig.text(0.01, 0.95, "(a) Sample and one design", fontsize=7.8, color=INK)

    # (b) delivered minus stated
    axb = fig.add_axes([0.405, 0.25, 0.33, 0.555])
    lo_y, hi_y = -0.16, 0.10
    axb.axhspan(0, hi_y, color=RED, alpha=0.05, lw=0); axb.axhspan(lo_y, 0, color=BLUE, alpha=0.05, lw=0)
    axb.axhline(0, color=INK, lw=0.9)
    for j in range(R):
        for side, v, col in ((-1, d_own[:, j], ORANGE), (1, d_con[:, j], PURPLE)):
            y = np.linspace(lo_y, hi_y, 400)
            dd = gaussian_kde(v, bw_method=0.35)(y); dd = dd / dd.max() * 0.36; k = dd > 0.0036
            axb.fill_betweenx(y[k], j, j + side * dd[k], color=col, alpha=0.30, lw=0)
            qa, (lo, hi) = boot_q(v, CONF)
            x = j + side * 0.15
            axb.plot([x, x], [lo, hi], color=INK, lw=0.9, solid_capstyle="butt")
            axb.plot([x - 0.04, x + 0.04], [lo, lo], color=INK, lw=0.9); axb.plot([x - 0.04, x + 0.04], [hi, hi], color=INK, lw=0.9)
            axb.plot(x, qa, "o", ms=4.8, color=col, mec=INK, mew=0.7, zorder=4)
    axb.text(R - 0.45, hi_y - 0.008, "unwanted looseness:\nmore wrong skips than stated", fontsize=6, color=RED,
             style="italic", ha="right", va="top")
    axb.text(R - 0.45, lo_y + 0.008, "unwanted conservatism:\nstated budget left unused", fontsize=6, color=BLUE,
             style="italic", ha="right", va="bottom")
    axb.set_xticks(range(R), [f"round {j + 1}\n{Nmean[j]:.0f} sites" for j in range(R)], fontsize=6.8)
    for j in range(R):
        axb.text(j - 0.2, lo_y - 0.052, f"{m_own[j]:.0f}", ha="center", va="top", fontsize=6.5, color=ORANGE, clip_on=False)
        axb.text(j + 0.2, lo_y - 0.052, f"{m_con[j]:.0f}", ha="center", va="top", fontsize=6.5, color=PURPLE, clip_on=False)
    axb.text(-0.6, lo_y - 0.052, "measured", ha="right", va="top", fontsize=6.3, color=INK, clip_on=False)
    axb.set_xlim(-0.55, R - 0.45); axb.set_ylim(lo_y, hi_y)
    axb.set_ylabel("wrong skips: delivered\nminus stated (share of round)", fontsize=6.8, labelpad=1)
    axb.tick_params(axis="y", labelsize=6.5)
    for s_ in ("top", "right"):
        axb.spines[s_].set_visible(False)
    fig.text(0.33, 0.95, "(b) Wrong skips: delivered minus stated", fontsize=7.8, color=INK)
    fig.text(0.405, 0.875, "own word", fontsize=6.8, color=ORANGE, fontweight="bold")
    fig.text(0.49, 0.875, f"{tot_own.mean():.0f} sites measured", fontsize=6.6, color=INK)
    fig.text(0.635, 0.875, "contract", fontsize=6.8, color=PURPLE, fontweight="bold")
    fig.text(0.708, 0.875, f"{tot_con.mean():.0f} sites", fontsize=6.6, color=INK)
    fig.text(0.405, 0.833, "shape: spread over 80 campaigns;  dot: level 80 % stay at or below;  bar: uncertainty of the dot (95 %)", fontsize=5.6, color=INK2)

    # (c) stated vs realised chance of going over the request
    axc = fig.add_axes([0.815, 0.25, 0.17, 0.57])
    lim = 0.32
    axc.fill_between([0, lim], [0, lim], [lim, lim], color=RED, alpha=0.05, lw=0)
    axc.fill_between([0, lim], [0, 0], [0, lim], color=BLUE, alpha=0.05, lw=0)
    axc.plot([0, lim], [0, lim], color=INK2, lw=0.8, ls=(0, (4, 3)))

    def pts(rows, eps, filled):
        for key, col, mk in (("own", ORANGE, "o"), ("contract", PURPLE, "s")):
            wk = "realised" if key == "own" else "W_level"
            X = np.array([[l[wk] > np.floor(eps * l["N"]) for l in r[key]] for r in rows])
            st = np.array([[l["stated_over"] if key == "own" else l["delta_picked"] for l in r[key]] for r in rows]).mean(0)
            for j in range(X.shape[1]):
                k = int(X[:, j].sum()); lo, hi = cp(k, len(rows))
                if filled:
                    axc.plot([st[j], st[j]], [lo, hi], color=col, lw=0.9, alpha=0.8)
                axc.plot(st[j], k / len(rows), mk, ms=5.0 if filled else 3.6, mfc=col if filled else "white",
                         mec=INK if filled else col, mew=0.5 if filled else 1.0, zorder=3 if filled else 2)
    for path, eps, _ in OTHER:
        pts(load(path), eps, False)
    pts(rr, EPS, True)
    axc.set_xlim(0, lim); axc.set_ylim(0, lim)
    axc.set_xticks([0, 0.1, 0.2, 0.3]); axc.set_yticks([0, 0.1, 0.2, 0.3]); axc.tick_params(labelsize=6.3)
    axc.set_xlabel("stated chance of going over\nthe request, before the round", fontsize=6.5)
    axc.set_ylabel("realised in 80 campaigns", fontsize=6.5, labelpad=1)
    for s_ in ("top", "right"):
        axc.spines[s_].set_visible(False)
    axc.text(0.01, 0.31, "filled: this setting\nhollow: two-round seed,\nbudgets 0.20 and 0.10", fontsize=5.6, color=INK, va="top")
    fig.text(0.765, 0.95, "(c) Going over the request", fontsize=7.8, color=INK)

    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"fig_hook2.{ext}", dpi=300)

    # SI: maps of wrong-skip frequency
    rix = np.searchsorted(xs, xy[:, 0].round(4)); riy = np.searchsorted(ys, xy[:, 1].round(4))
    dec = np.zeros(len(xy)); wr = {k: np.zeros(len(xy)) for k in ("own", "contract")}
    for r in rr:
        dec[r["decided"]] += 1
        for k in wr:
            for l in r[k]:
                wr[k][l["wrong_idx"]] += 1
    f2, axs = plt.subplots(1, 3, figsize=(7.2, 2.6))
    axs[0].set_facecolor("#f4f3ef")
    axs[0].imshow(img, origin="lower", cmap="viridis", alpha=0.85, vmin=vmin, vmax=vmax, interpolation="nearest")
    axs[0].set_title("measured (200) width", fontsize=7.5)
    cmap = plt.get_cmap("Reds").copy(); cmap.set_bad("#e9e8e4")
    for ax, k, t, c in ((axs[1], "own", "own word", ORANGE), (axs[2], "contract", "contract", PURPLE)):
        M = np.full(img.shape, np.nan); ok = dec > 0
        M[riy[ok], rix[ok]] = wr[k][ok] / dec[ok]
        im = ax.imshow(M, origin="lower", cmap=cmap, vmin=0, vmax=0.8, interpolation="nearest")
        ax.set_title(t, fontsize=7.5, color=c, fontweight="bold")
    for ax in axs:
        ax.set_xticks([]); ax.set_yticks([])
    cb = f2.colorbar(im, ax=axs, fraction=0.02, pad=0.01); cb.set_label("share of 80 campaigns skipped wrongly", fontsize=6.5)
    f2.savefig(FIG / "figS_wrong_maps.png", dpi=300)


if __name__ == "__main__":
    main()
