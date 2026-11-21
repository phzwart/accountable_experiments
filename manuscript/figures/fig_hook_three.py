"""
Figure 1: three campaigns on the NaCl (200)-width scan, and what each states about its wrong skips.
(a) The certified plan of average cost (quantile path, natural-neighbour interpolation; seed 44).
(b) A campaign guided by a Gaussian process refitted after each level, 68 % intervals on the latent width.
(c) The same with the predictive standard deviation (latent plus fitted noise).
(d) Stated against realised share of the sites of levels 3 to 6 skipped wrongly, with sites measured.
For (b, c) the statement is the model's own probability of a wrong skip summed over its skips; for the certified
plan it is the bound. Certified: mean and 5-95 % range over 250 campaigns.

    python -m experiments.uncertified_gp && python manuscript/figures/fig_hook_three.py
"""
from __future__ import annotations

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
from fig_hook import ROOT, ROW, SEED, INK, INK2, GRID, RED  # noqa: E402
from fig_datasets import nacl_fwhm  # noqa: E402
from fig_hook_compare import COL, BLUE, certified_cloud  # noqa: E402
from experiments.record import OUT as REC, REASONS, build  # noqa: E402

ORANGE = "#eb6834"


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": INK2,
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

    def unc(sd):
        u = np.load(ROOT / f"results/hook/uncertified_{sd}_z1.00.npz")
        a = u["action"].astype(object)
        a[a == "seed"] = "measured"
        row = [r for r in res["uncertified"] if r["sd"] == sd and r["z"] == 1.0][0]
        return a, u["wrong"], row

    la, lw, lrow = unc("latent")
    pa, pw, prow = unc("predictive")

    FW, FH = 7.2, 2.4
    fig = plt.figure(figsize=(FW, FH), facecolor="white")
    mw = 0.19
    mh = mw * FW / FH
    X0 = (0.005, 0.215, 0.425)
    y0 = 0.17
    keys = ["measured", "no_line", "predictable"]
    cmap = ListedColormap([COL[k] for k in keys])

    def amap(x, act, wrong, title):
        ax = fig.add_axes([x, y0, mw, mh])
        code = np.array([keys.index(k) for k in act])
        ax.imshow(code[nn], origin="lower", cmap=cmap, vmin=-0.5, vmax=2.5, extent=ext, interpolation="nearest")
        ax.contour(XX, YY, pres.astype(float), levels=[0.5], colors=INK, linewidths=0.4)
        ax.scatter(xy[wrong, 0], xy[wrong, 1], s=5, marker="x", c=RED, linewidths=0.55)
        ax.set_title(title, loc="left", fontsize=7.2, pad=3)
        ax.set_xticks([]); ax.set_yticks([])
        return ax

    amap(X0[0], c_act, c_wrong, f"(a) Certified plan\n{int((~S).sum())} measured; bound 20 %")
    amap(X0[1], la, lw, f"(b) GP, latent s.d.\n{lrow['measured']} measured; no bound")
    amap(X0[2], pa, pw, f"(c) GP, predictive s.d.\n{prow['measured']} measured; no bound")

    # (d) stated against realised, same denominator
    ax = fig.add_axes([0.755, y0 + 0.03, 0.235, mh - 0.08])
    cm, cr = certified_cloud(ROW, cert)
    cr = 100 * np.asarray(cr)
    pts = [("certified\n(mean, 250)", 20.0, cr.mean(), np.percentile(cr, [5, 95]), int(round(np.mean(cm))), BLUE),
           ("GP, latent", 100 * lrow["stated_rate"], 100 * lrow["wrong_rate"], None, lrow["measured"], ORANGE),
           ("GP, predictive", 100 * prow["stated_rate"], 100 * prow["wrong_rate"], None, prow["measured"], INK2)]
    for k, (lab, st, re, rng, meas, col) in enumerate(pts):
        yk = 2 - k
        ax.plot([st, re], [yk, yk], color=GRID, lw=2.2, zorder=1, solid_capstyle="round")
        ax.scatter([st], [yk], marker="|", s=90, c=col, linewidths=1.6, zorder=3)
        ax.scatter([re], [yk], marker="o", s=22, c=col, edgecolors="white", linewidths=0.5, zorder=4)
        if rng is not None:
            ax.plot(rng, [yk, yk], color=col, lw=0.8, zorder=2)
        ax.text(26.5, yk, f"{meas}", va="center", ha="right", fontsize=6.6, color=INK2)
    ax.set_yticks([2, 1, 0], [p[0] for p in pts], fontsize=6.6)
    ax.set_xlim(-0.5, 27.5); ax.set_ylim(-0.6, 2.6)
    ax.set_xlabel("share of sites skipped wrongly (%)", fontsize=6.8)
    ax.text(26.5, 2.62, "measured", ha="right", va="bottom", fontsize=6.0, color=INK2)
    ax.set_title("(d) Stated (|) and realised (●)", loc="left", fontsize=7.2, pad=10)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.tick_params(labelsize=6.4)

    handles = [plt.Rectangle((0, 0), 1, 1, color=COL["measured"], label="measured"),
               plt.Rectangle((0, 0), 1, 1, color=COL["no_line"], label="skipped: no line"),
               plt.Rectangle((0, 0), 1, 1, color=COL["predictable"], label="skipped: predictable"),
               Line2D([], [], ls="", marker="x", color=RED, markersize=4.5, label="wrong skip, found afterwards"),
               Line2D([], [], color=INK, lw=0.6, label="edge of the line")]
    fig.legend(handles=handles, loc="lower left", ncol=5, fontsize=6.2, frameon=False, bbox_to_anchor=(0.0, 0.0),
               columnspacing=1.0, handletextpad=0.4)
    fig.text(0.005, 0.94, "Three campaigns on one NaCl scan: only the certified plan states a rate it is bound to keep",
             fontsize=8.6, fontweight="bold", color=INK)
    fig.savefig(FIG / "fig_hook_three.png", dpi=220)
    fig.savefig(FIG / "fig_hook_three.pdf")
    print("wrote", FIG / "fig_hook_three.png")


if __name__ == "__main__":
    main()
