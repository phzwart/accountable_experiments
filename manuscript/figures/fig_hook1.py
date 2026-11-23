"""
Figure 1: specified and calibrated in advance. NaCl (200)-width scan, 80 fresh hierarchical designs, one Gaussian
process on the staged plan, budget EPS per round at confidence 0.80; the two rules differ only in who sets the cut
(the process's own statement, or a uniform calibration draw with the exact hypergeometric cut).

(a) Measured width (viridis) with the seed and the four rounds of one design.
(b) Delivered per round: the share of the round's sites skipped wrongly that 80 % of campaigns stay at or below
    (95 % bootstrap interval), distributions faint behind, against the request.
(c) Where sites are skipped wrongly: share of the 80 campaigns, per site, own word and contract.
(d) Stated against realised chance of exceeding the request, per round (Clopper-Pearson 95 %).

    [STAGED_EPS=0.10] python manuscript/figures/fig_hook1.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde

FIG = Path(__file__).resolve().parent
sys.path.insert(0, str(FIG))
from fig_hook_calibrated import EPS, GRID, INK, INK2, ORANGE, PURPLE, RES, ROOT, S, SEED_MAX, TAG, shares, site_maps  # noqa: E402
from fig_hook_request import boot_q, cp  # noqa: E402


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK})
    own, con, own_over, con_over, m_own, m_con = shares()
    rr = [json.loads(l) for l in open(ROOT / RES)]
    stated_con = np.array([[l["delta_picked"] for l in r["contract"]] for r in rr]).mean(0)
    stated_own = np.array([[l["stated_over"] for l in r["own"]] for r in rr]).mean(0)
    Nmean = np.array([[l["N"] for l in r["own"]] for r in rr]).mean(0)
    con_real = np.array([[l["realised"] / l["N"] for l in r["contract"]] for r in rr])     # actual wrong skips
    meas_own = np.array([[l["N"] - l["n_skip"] for l in r["own"]] for r in rr]).mean(0)
    meas_con = np.array([[l["N"] - l["n_skip"] for l in r["contract"]] for r in rr]).mean(0)
    from scipy.stats import hypergeom

    def contract_bound(l, conf=0.80):
        """Exact upper limit at conf on the round's event count from the calibration draw, less the failures
        already seen in the draw: the bound on actual wrong skips the contract states before the round."""
        N, m, k = l["N"], l["m"], l["k_cal"]
        W = np.arange(k, N + 1)
        u = int(W[hypergeom.cdf(k, N, W, m) > 1 - conf].max())
        return (u - k) / N
    st_own = np.array([[l["stated_q"] / l["N"] for l in r["own"]] for r in rr])
    st_con = np.array([[contract_bound(l) for l in r["contract"]] for r in rr])
    cov_own = (own <= st_own + 1e-12).mean(0); cov_con = (con_real <= st_con + 1e-12).mean(0)
    print("stated bound (mean) own", st_own.mean(0).round(3), "contract", st_con.mean(0).round(3))
    print("delivered q80 own", np.quantile(own, .8, axis=0).round(3), "contract", np.quantile(con_real, .8, axis=0).round(3))
    print("coverage of own bound: own word", cov_own.round(3), "contract", cov_con.round(3))
    tests = json.load(open(ROOT / RES.replace(".jsonl", "_trend_tests.json")))
    n = len(rr); R = own.shape[1]

    sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "src"))
    from fig_datasets import nacl_fwhm
    from experiments.nacl_saxs.adapter import load
    img, _, (xs, ys), _, _ = nacl_fwhm()
    ds, grid = load()
    xy = np.asarray(grid["xy_mm"], float)
    rix = np.searchsorted(xs, xy[:, 0].round(4)); riy = np.searchsorted(ys, xy[:, 1].round(4))
    maps, nd = site_maps(img.shape, riy, rix)

    fig = plt.figure(figsize=(7.2, 5.4))
    MW, MH = 0.255, 0.33                       # map axes size (figure fraction), identical for all three maps
    X1, X2 = 0.105, 0.375
    YT, YB = 0.555, 0.065

    def clean(ax):
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)

    # (a) measured width with one design
    axg = fig.add_axes([X1, YT, MW, MH])
    axg.set_facecolor("#f4f3ef")
    vmin, vmax = np.nanpercentile(img, 5), np.nanpercentile(img, 95)
    imw = axg.imshow(img, origin="lower", cmap="viridis", alpha=0.85, vmin=vmin, vmax=vmax, interpolation="nearest")
    rxy = xy[np.asarray(ds.meta["raster_index"])]
    dix = np.searchsorted(xs, rxy[:, 0].round(4)); diy = np.searchsorted(ys, rxy[:, 1].round(4))
    lv = np.asarray(ds.levels)
    axg.scatter(dix[lv <= SEED_MAX], diy[lv <= SEED_MAX], s=11, c="white", marker="s", lw=0.8, edgecolors="black", zorder=5, label="seed")
    for r, (L, sz) in enumerate(zip(range(SEED_MAX + 1, 7), (9, 5, 2.2, 0.7)[4 - R:] if R < 4 else (9, 5, 2.2, 0.7))):
        m = lv == L
        if r < R - 2:
            axg.scatter(dix[m], diy[m], s=sz, facecolors="none", edgecolors="black" if r == 0 else "#3a3a3a", lw=0.7,
                        zorder=4, label=f"round {r + 1}")
        else:
            axg.scatter(dix[m], diy[m], s=sz, c="#111111", lw=0, alpha=0.8, zorder=3, label=f"round {r + 1}")
    axg.set_xlim(-0.5, img.shape[1] - 0.5); axg.set_ylim(-0.5, img.shape[0] - 0.5)
    clean(axg)
    axg.legend(loc="upper center", bbox_to_anchor=(0.5, -0.005), ncol=R + 1, frameon=False, fontsize=5.8,
               handletextpad=0.05, columnspacing=0.45, markerscale=1.5)
    cwx = fig.add_axes([X1 - 0.03, YT + 0.04, 0.010, MH - 0.08])
    cw = fig.colorbar(imw, cax=cwx); cw.outline.set_visible(False); cw.solids.set_alpha(0.85)
    cw.ax.tick_params(labelsize=6, length=2); cwx.yaxis.set_ticks_position("left"); cwx.yaxis.set_label_position("left")
    cw.set_label("(200) width, nm⁻¹", fontsize=6.3)
    fig.text(0.02, 0.965, "(a) The sample and one design", fontsize=8, color=INK)

    # (b) delivered per round
    axb = fig.add_axes([0.49, YT + 0.06, 0.48, MH - 0.065])
    for j in range(R):
        for side, v, col in ((-1, own[:, j], ORANGE), (1, con_real[:, j], PURPLE)):
            y = np.linspace(0, 0.6 * S, 300)
            d = gaussian_kde(v, bw_method=0.35)(y); d = d / d.max() * 0.34; k = d > 0.0034
            axb.fill_betweenx(y[k], j, j + side * d[k], color=col, alpha=0.13, lw=0)
            qa, (lo, hi) = boot_q(v)
            x = j + side * 0.17
            axb.plot([x, x], [lo, hi], color=col, lw=1.4, solid_capstyle="butt")
            axb.plot(x, qa, "o", ms=5, color=col, mec=INK, mew=0.7, zorder=4)
    for j in range(R):
        for side, v, col in ((-1, st_own[:, j], ORANGE), (1, st_con[:, j], PURPLE)):
            x0, x1 = (j - 0.36, j - 0.02) if side < 0 else (j + 0.02, j + 0.36)
            axb.plot([x0, x1], [v.mean(), v.mean()], color=col, lw=2.0, ls=(0, (2.5, 1.5)), zorder=3)
    # deviation of delivered from stated: arrows
    for j in range(R):
        for side, st, v, col in ((-1, st_own[:, j], own[:, j], ORANGE), (1, st_con[:, j], con_real[:, j], PURPLE)):
            ys, yd = st.mean(), np.quantile(v, 0.80); x = j + side * 0.27
            if abs(yd - ys) > 0.008 * S:
                axb.annotate("", xy=(x, yd), xytext=(x, ys),
                             arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9, mutation_scale=7, shrinkA=0, shrinkB=1))
    jlab = int(np.argmax(st_own.mean(0) - np.quantile(own, 0.80, axis=0)))
    axb.annotate("unwanted conservatism:\nbudget stated but not used", xy=(jlab - 0.27, np.quantile(own[:, jlab], 0.8) - 0.004 * S),
                 xytext=(jlab - 0.95, 0.045 * S), fontsize=6.4, color=INK, style="italic", ha="center",
                 arrowprops=dict(arrowstyle="-", color=INK2, lw=0.5))
    axb.text(-0.5, 0.36 * S, "dashed marks: the bound each rule stated before the round,\n"
                             "at 80 % (mean over campaigns); dots: what was delivered", fontsize=6.6, color=INK, va="center")
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    hk = [Patch(color=INK2, alpha=0.18, label="spread over the 80 campaigns"),
          Line2D([], [], marker="o", ls="-", color=INK2, mfc="white", mec=INK, ms=4.5, lw=1.2,
                 label="80 % of campaigns at or below\n(delivered bound, 95 % interval)")]
    axb.legend(handles=hk, loc="upper right", bbox_to_anchor=(1.0, 0.84), frameon=False, fontsize=6.3,
               handlelength=1.4, labelspacing=0.5)
    axb.set_xticks(range(R), [f"round {j + 1}\n{Nmean[j]:.0f} sites" for j in range(R)])
    for j in range(R):
        axb.text(j - 0.2, -0.115 * S, f"{meas_own[j]:.0f}", ha="center", va="top", fontsize=7, color=ORANGE, clip_on=False)
        axb.text(j + 0.2, -0.115 * S, f"{meas_con[j]:.0f}", ha="center", va="top", fontsize=7, color=PURPLE, clip_on=False)
    axb.text(-0.62, -0.115 * S, "measured", ha="right", va="top", fontsize=6.8, color=INK, clip_on=False)
    axb.set_xlim(-0.55, R - 0.4); axb.set_ylim(0, 0.39 * S)
    axb.set_yticks(np.round(np.arange(0, 0.31 * S, 0.1 * S), 3))
    axb.set_ylabel("share of the round's sites\nskipped wrongly, per campaign", labelpad=2)
    axb.grid(axis="y", color=GRID, lw=0.4, alpha=0.6)
    for s_ in ("top", "right"):
        axb.spines[s_].set_visible(False)
    fig.text(0.40, 0.965, "(b) Wrong skips per round: the share 80 % of campaigns stay at or below", fontsize=8, color=INK)
    fig.text(0.49, 0.928, "own word (left)", fontsize=7.2, color=ORANGE, fontweight="bold")
    fig.text(0.612, 0.928, f"{m_own.mean():.0f} ± {m_own.std():.0f} sites", fontsize=7, color=INK)
    fig.text(0.745, 0.928, "contract (right)", fontsize=7.2, color=PURPLE, fontweight="bold")
    fig.text(0.874, 0.928, f"{m_con.mean():.0f} ± {m_con.std():.0f} sites", fontsize=7, color=INK)

    # (c) wrong-skip maps, same size as (a), the own word directly under (a)
    cmap = plt.get_cmap("Reds").copy(); cmap.set_bad("#e9e8e4")
    kw = dict(origin="lower", cmap=cmap, vmin=0, vmax=0.8 * S, interpolation="nearest")
    axl = fig.add_axes([X1, YB, MW, MH]); axr = fig.add_axes([X2, YB, MW, MH])
    im = axl.imshow(maps["own"], **kw); axr.imshow(maps["contract"], **kw)
    for ax, t, c in ((axl, "own word", ORANGE), (axr, "contract", PURPLE)):
        clean(ax); ax.set_title(t, fontsize=7.5, color=c, fontweight="bold", pad=2)
    cax = fig.add_axes([X2 + MW + 0.008, YB + 0.04, 0.010, MH - 0.08])
    cb = fig.colorbar(im, cax=cax, ticks=np.round(np.linspace(0, 0.8 * S, 5), 2))
    cb.outline.set_visible(False); cb.ax.tick_params(labelsize=6, length=2)
    cb.set_label(f"skipped wrongly, share of {nd} campaigns", fontsize=6.3)
    fig.text(0.02, 0.445, "(c) Where sites are skipped wrongly", fontsize=8, color=INK)

    # (d) stated against realised
    axd = fig.add_axes([0.765, YB + 0.03, 0.215, MH - 0.02])
    lim = 0.32
    axd.plot([0, lim], [0, lim], color=INK2, lw=0.8, ls=(0, (4, 3)))
    axd.fill_between([0, lim], [0, lim], [lim, lim], color="#c0392b", alpha=0.06, lw=0)
    axd.fill_between([0, lim], [0, 0], [0, lim], color="#2f5f9e", alpha=0.06, lw=0)
    axd.text(0.03, 0.255, "unwanted looseness:\nover more often than stated", fontsize=5.8, color="#8e2a1e", style="italic", va="top")
    axd.text(0.315, 0.055, "unwanted conservatism:\nover less often than stated", fontsize=5.8, color="#23477a", style="italic",
             ha="right", va="bottom")
    for st, X, col, mk in ((stated_own, own_over, ORANGE, "o"), (stated_con, con_over, PURPLE, "s")):
        for j in range(R):
            k = int(X[:, j].sum()); lo, hi = cp(k, n)
            axd.plot([st[j], st[j]], [lo, hi], color=col, lw=1.0, alpha=0.8)
            axd.plot(st[j], k / n, mk, ms=4.3, color=col, mec=INK, mew=0.6, zorder=3)
            axd.text(st[j] + 0.007, k / n, str(j + 1), fontsize=6, color=col, va="center")
    axd.set_xlim(0, lim); axd.set_ylim(0, lim)
    axd.set_xticks([0, 0.1, 0.2, 0.3]); axd.set_yticks([0, 0.1, 0.2, 0.3])
    axd.tick_params(labelsize=6.5)
    axd.set_xlabel("stated before the round", fontsize=7)
    axd.set_ylabel("realised in 80 campaigns", fontsize=7)
    axd.grid(color=GRID, lw=0.4, alpha=0.5)
    for s_ in ("top", "right"):
        axd.spines[s_].set_visible(False)
    to, tc = tests["own"], tests["contract"]
    axd.text(0.01, 0.318, "trend over rounds\n" + ("own word p < 5·10⁻⁵" if to["p_trend"] < 5e-5 else f"own word p = {to['p_trend']:.3f}")
             + f"\ncontract p = {tc['p_trend']:.2f}", fontsize=5.9, color=INK, va="top")
    fig.text(0.70, 0.445, "(d) Chance of exceeding the request", fontsize=8, color=INK)

    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"fig_hook1{TAG}.{ext}", dpi=300)


if __name__ == "__main__":
    main()
