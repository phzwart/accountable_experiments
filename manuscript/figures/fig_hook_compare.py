"""
Hook figure (Fig. 1): two campaigns on the same fully measured NaCl scan, (200) width claim, at about the same
cost. GP-guided (uncertified): a GP refitted after each level skips a site when sure there is no line, or when
its 68 % interval on the width lies within the tolerance. Certified: the campaign of average cost (seed 44).
(a) True (200) width. (b), (c) Actions of each campaign, wrong skips found afterwards against the full scan.
(d) Sites measured against the realised share of levels 3-6 skipped wrongly: 250 certified campaigns with
    natural-neighbour prediction, 3 x 250 certified campaigns with the GP posterior mean as predictor
    (length scale by maximum likelihood, by design, nonstationary), and the uncertified GP rule at four
    interval widths, with latent or predictive standard deviation.
(e) GP rule: share of predictable skips wrong, promised by the interval and realised.
(f) Certified: realised share of each level skipped wrongly in 250 campaigns, against the budget of 20 %.
    The guarantee is statistical: a level exceeds the budget with probability at most delta_L <= 0.20
    (confidence 0.80); numbers give level-runs over budget against the sum of the picked delta_L.

    python -m experiments.uncertified_gp && python manuscript/figures/fig_hook_compare.py
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from scipy.spatial import cKDTree

FIG = Path(__file__).resolve().parent
sys.path.insert(0, str(FIG))
from fig_hook import ROOT, ROW, SEED, INK, INK2, GRID, RED, BUDGET  # noqa: E402
from fig_datasets import nacl_fwhm  # noqa: E402
from experiments.record import OUT as REC, REASONS, build  # noqa: E402

COL = {"measured": "#a8a7a3", "no_line": "#eda100", "predictable": "#1baf7a"}
PURPLE = "#8e6cc8"
GP_ROWS = ["nacl_fwhm_nested_gp_mle", "nacl_fwhm_nested_gp_design", "nacl_fwhm_nested_gp_nonstationary"]


def certified_cloud(row, cert):
    z = np.load(REC / row / "sites.npz")
    S = z["skipped"].astype(bool)
    R = np.array(REASONS)[z["reason"]]
    A = np.isin(R, ["not_interesting", "not_interesting+interpolable"])
    B = np.isin(R, ["interpolable", "not_interesting+interpolable"])
    W = S & ((A & z["interesting"].astype(bool)) | (B & z["fail_prior"].astype(bool)))
    return z["measured"].sum(1), W[:, cert].mean(1)
BLUE = "#2a78d6"


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK})
    res = json.loads((ROOT / "results/hook/uncertified.json").read_text())
    z = np.load(REC / ROW / "sites.npz")
    i = int(np.flatnonzero(z["seeds"] == SEED)[0])
    ds, _, _ = build(ROW, SEED, {})
    xy = np.asarray(ds.meta["xy_mm"], float)[z["site_index"]]
    lv = np.asarray(z["levels"])
    cert = lv >= 3
    img, pres, (xs, ys), _, _ = nacl_fwhm()
    ext = (xs[0], xs[-1], ys[0], ys[-1])
    XX, YY = np.meshgrid(xs, ys)
    _, nn = cKDTree(xy).query(np.c_[XX.ravel(), YY.ravel()])
    nn = nn.reshape(XX.shape)

    R = np.array(REASONS)[z["reason"][i]]
    S = z["skipped"][i].astype(bool)
    Acov = np.isin(R, ["not_interesting", "not_interesting+interpolable"])
    Bcov = np.isin(R, ["interpolable", "not_interesting+interpolable"])
    c_act = np.where(~S, "measured", np.where(Acov, "no_line", "predictable")).astype(object)
    c_wrong = S & ((Acov & z["interesting"][i].astype(bool)) | (Bcov & z["fail_prior"][i].astype(bool)))
    u = np.load(ROOT / "results/hook/uncertified_latent_z1.00.npz")
    u_act, u_wrong = u["action"].astype(object), u["wrong"]
    u_act[u_act == "seed"] = "measured"
    rowu = [r for r in res["uncertified"] if r["sd"] == "latent" and r["z"] == 1.0][0]

    FW, FH = 7.2, 6.0
    fig = plt.figure(figsize=(FW, FH), facecolor="white")
    mw = 0.265
    mh = mw * FW / FH
    X0 = (0.07, 0.385, 0.70)
    ty, by, bh = 0.505, 0.135, 0.255

    def style(ax, title):
        ax.set_title(title, loc="left", fontsize=7.4, pad=4)
        ax.tick_params(labelsize=6.3)

    # (a) truth
    ax = fig.add_axes([X0[0], ty, mw, mh])
    ax.imshow(np.where(pres, np.nan, 0.0), origin="lower", cmap=ListedColormap(["#ecebe7"]), extent=ext)
    im = ax.imshow(img, origin="lower", cmap="Blues", vmin=np.nanpercentile(img, 2), vmax=np.nanpercentile(img, 98),
                   extent=ext, interpolation="nearest")
    style(ax, "(a) The scan, measured in full:\n     width of the (200) line")
    ax.set_xticks([]); ax.set_yticks([])
    cax = ax.inset_axes([0.0, -0.075, 1.0, 0.045])
    cb = fig.colorbar(im, cax=cax, orientation="horizontal")
    cb.ax.tick_params(labelsize=6.0)
    cb.set_label("nm$^{-1}$; grey: no line", fontsize=6.2, labelpad=1)

    keys = ["measured", "no_line", "predictable"]
    cmap = ListedColormap([COL[k] for k in keys])

    def amap(x, act, wrong, title):
        ax = fig.add_axes([x, ty, mw, mh])
        code = np.array([keys.index(a) for a in act])
        ax.imshow(code[nn], origin="lower", cmap=cmap, vmin=-0.5, vmax=2.5, extent=ext, alpha=0.9,
                  interpolation="nearest")
        ax.contour(XX, YY, pres.astype(float), levels=[0.5], colors=INK, linewidths=0.5)
        ax.scatter(xy[wrong, 0], xy[wrong, 1], s=8, marker="x", c=RED, linewidths=0.7)
        style(ax, title)
        ax.set_xticks([]); ax.set_yticks([])
        return ax

    amap(X0[1], u_act, u_wrong, f"(b) GP-guided: {rowu['measured']} measured,\n"
                                f"     {100 * rowu['wrong_rate']:.0f} % of sites wrong; no bound")
    amap(X0[2], c_act, c_wrong, f"(c) Certified: {int((~S).sum())} measured,\n"
                                f"     {100 * c_wrong[cert].mean():.0f} % of sites wrong; bound 20 %")

    # cost against realised error: Figure S7 (SI 7)
    figd, ax = plt.subplots(figsize=(3.6, 2.9), facecolor="white", gridspec_kw=dict(left=0.16, right=0.97, top=0.9, bottom=0.16))
    cm, cr = np.array(res["certified"]["measured"]), np.array(res["certified"]["wrong_rate"])
    ax.scatter(cm, cr, s=3, c=GRID, linewidths=0)
    gm, gr = zip(*[certified_cloud(r, cert) for r in GP_ROWS])
    gm, gr = np.concatenate(gm), np.concatenate(gr)
    ax.scatter(gm, gr, s=3, c=PURPLE, alpha=0.55, linewidths=0)
    ax.annotate("certified GP", (np.median(gm), np.percentile(gr, 97)), xytext=(0, 6), textcoords="offset points",
                fontsize=6.1, color=PURPLE, ha="center")
    ax.annotate("certified natural\nneighbour", (575, 0.05), fontsize=6.1, color=INK2, ha="left")
    ax.scatter([int((~S).sum())], [c_wrong[cert].mean()], s=28, marker="D", c=BLUE, edgecolors="white",
               linewidths=0.6, zorder=3)
    for r in res["uncertified"]:
        ax.scatter([r["measured"]], [r["wrong_rate"]], s=24, marker="o" if r["sd"] == "latent" else "s",
                   facecolors="none", edgecolors=INK, lw=0.9, zorder=4)
    ax.annotate("GP, 68 %", (rowu["measured"], rowu["wrong_rate"]), xytext=(7, 3), textcoords="offset points",
                fontsize=6.1, color=INK2)
    ax.annotate("GP, 90–99 %", (900, 0.012), xytext=(-4, 12), textcoords="offset points", fontsize=6.1,
                color=INK2, ha="right")
    ax.set_xlim(560, 960); ax.set_ylim(-0.01, 0.27)
    ax.set_xlabel("sites measured (of 1071)", fontsize=6.8)
    ax.set_ylabel("share of sites skipped wrongly", fontsize=6.8)
    style(ax, "Cost against realised error, NaCl scan, levels 3 to 6")
    ax.legend(handles=[Line2D([], [], ls="", marker="o", color=GRID, markersize=3.5, label="certified, natural neighbour"),
                       Line2D([], [], ls="", marker="o", color=PURPLE, markersize=3.5, label="certified, Gaussian process"),
                       Line2D([], [], ls="", marker="o", mfc="none", color=INK, markersize=4.5, label="uncertified Gaussian process")],
              fontsize=5.8, frameon=False, loc="upper right")
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    # (d) GP: promised against realised
    ax = fig.add_axes([X0[0], by, 0.40, bh])
    lat = [r for r in res["uncertified"] if r["sd"] == "latent" and r["wrong_pred"] is not None]
    k = np.arange(len(lat))
    ax.bar(k - 0.19, [r["nominal"] for r in lat], 0.36, color=GRID)
    ax.bar(k + 0.19, [r["wrong_pred"] for r in lat], 0.36, color=RED)
    for j, r in enumerate(lat):
        ax.text(j + 0.19, r["wrong_pred"] + 0.008, f"n={r['n_skip_pred']}", ha="center", fontsize=5.6, color=INK2)
    ax.set_xticks(k); ax.set_xticklabels([f"{100 * (1 - r['nominal']):.0f} %" for r in lat], fontsize=6.3)
    ax.set_xlabel("GP interval", fontsize=6.8)
    ax.set_ylabel("share of predictable skips wrong", fontsize=6.8)
    ax.set_ylim(0, 0.45)
    ax.text(0.98, 0.98, "promised", transform=ax.transAxes, ha="right", va="top", fontsize=6.3, color=INK2)
    ax.text(0.98, 0.90, "realised", transform=ax.transAxes, ha="right", va="top", fontsize=6.3, color=RED)
    style(ax, "(d) Uncertified GP: what the interval promised, what happened")
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    # (f) certified: guaranteed against realised, per level
    ax = fig.add_axes([0.585, by, 0.385, bh])
    runs = [json.loads(l) for l in gzip.open(REC / ROW / "runs.jsonl.gz", "rt")]
    picked = [p for p in json.loads((REC / "PICKED.json").read_text()) if p["row"] == ROW and p["event"] == "R_E"]
    levels = sorted({pl["L"] for r in runs for pl in r["per_level"] if not pl.get("empty")})
    rng = np.random.default_rng(0)
    for j, L in enumerate(levels):
        rates = np.array([pl["level"]["E_rate"] for r in runs for pl in r["per_level"]
                          if pl["L"] == L and not pl.get("empty")])
        ax.scatter(np.full(len(rates), j) + rng.uniform(-0.25, 0.25, len(rates)), rates, s=2.5, c=GRID, linewidths=0)
        this = [pl["level"]["E_rate"] for r in runs if r["seed"] == SEED for pl in r["per_level"] if pl["L"] == L][0]
        ax.scatter([j], [this], s=26, marker="D", c=BLUE, edgecolors="white", linewidths=0.6, zorder=3)
        ex = sum(p["exceeded"] for p in picked if p["L"] == L)
        allow = sum(p["picked"] for p in picked if p["L"] == L)
        ax.text(j, 0.385, f"{ex}/{allow:.0f}", ha="center", va="center", fontsize=5.9, color=INK2)
    ax.text(-0.55, 0.415, "levels over budget / expected", fontsize=5.7, color=INK2, va="center")
    ax.axhline(BUDGET, color=RED, lw=1.0)
    ax.text(len(levels) - 0.45, BUDGET + 0.006, "budget", color=RED, fontsize=6.1, ha="right", va="bottom")
    ax.set_xticks(range(len(levels)))
    ax.set_xticklabels([f"L{L}" for L in levels], fontsize=6.3)
    ax.set_xlabel("level", fontsize=6.8)
    ax.set_ylabel("share of level skipped wrongly", fontsize=6.8, labelpad=1)
    ax.set_ylim(0, 0.43); ax.set_xlim(-0.6, len(levels) - 0.4)
    style(ax, "(e) Certified: each level over budget with probability\n     at most its picked failure probability")
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    handles = [plt.Rectangle((0, 0), 1, 1, color=COL["measured"], label="measured"),
               plt.Rectangle((0, 0), 1, 1, color=COL["no_line"], label="skipped: no line"),
               plt.Rectangle((0, 0), 1, 1, color=COL["predictable"], label="skipped: predictable"),
               Line2D([], [], ls="", marker="x", color=RED, markersize=5, label="wrong skip, found afterwards"),
               Line2D([], [], color=INK, lw=0.8, label="true edge of the line"),
               Line2D([], [], ls="", marker="o", color=GRID, markersize=3.5, label="certified natural neighbour, 250 campaigns"),
               Line2D([], [], ls="", marker="D", color=BLUE, markersize=4.5, label="certified, shown in (c)")]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=6.2, frameon=False, bbox_to_anchor=(0.5, 0.0),
               columnspacing=1.0, handletextpad=0.4)
    fig.text(0.07, 0.968, "Two campaigns, one scan: only one fixes its error rate in advance",
             fontsize=10, fontweight="bold", color=INK)
    fig.text(0.07, 0.938, "NaCl microdiffraction, width of the (200) line, tolerance 0.02 nm$^{-1}$. Both campaigns "
             "skip about 40 % of 1071 sites;\nthe certified one bounds, on each level, the share of its sites skipped wrongly at 20 %, "
             "with confidence 0.80 for that level.",
             fontsize=6.9, color=INK2, va="top", linespacing=1.4)
    figd.savefig(FIG / "figS7_cost.png", dpi=200)
    figd.savefig(FIG / "figS7_cost.pdf")
    fig.savefig(FIG / "fig_hook_compare.png", dpi=200)
    fig.savefig(FIG / "fig_hook_compare.pdf")
    print("wrote", FIG / "fig_hook_compare.png")


if __name__ == "__main__":
    main()
