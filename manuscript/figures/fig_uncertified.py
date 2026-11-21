"""
Certified against uncertified campaigns on the NaCl (200)-width map.
(a) Actions of the uncertified GP campaign closest in cost to the certified one (latent sd, z = 1), with its
    wrong skips. (b) The certified campaign of Fig. 1 (seed 44), same encoding.
(c) Cost against the realised share of sites skipped wrongly (levels 3 to 6): 250 certified campaigns and
    the uncertified rules (latent or predictive GP standard deviation; z = 1, 1.64, 1.96, 2.58).
(d) What the GP intervals promised against what happened at the sites skipped as predictable.

    python -m experiments.uncertified_gp && python manuscript/figures/fig_uncertified.py
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
from fig_hook import ROOT, ROW, SEED, INK, INK2, GRID, RED, BUDGET  # noqa: E402
from fig_datasets import nacl_fwhm  # noqa: E402
from experiments.record import OUT as REC, REASONS, build  # noqa: E402

COL = {"measured": "#9a9995", "no_line": "#eda100", "predictable": "#1baf7a"}
BLUE = "#2a78d6"


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2})
    res = json.loads((ROOT / "results/hook/uncertified.json").read_text())
    z = np.load(REC / ROW / "sites.npz")
    i = int(np.flatnonzero(z["seeds"] == SEED)[0])
    ds, _, _ = build(ROW, SEED, {})
    xy = np.asarray(ds.meta["xy_mm"], float)[z["site_index"]]
    lv = np.asarray(z["levels"])
    img, pres, (xs, ys), _, _ = nacl_fwhm()
    ext = (xs[0], xs[-1], ys[0], ys[-1])
    XX, YY = np.meshgrid(xs, ys)
    _, nn = cKDTree(xy).query(np.c_[XX.ravel(), YY.ravel()])
    nn = nn.reshape(XX.shape)

    # certified campaign, actions collapsed to the same three classes
    R = np.array(REASONS)[z["reason"][i]]
    S = z["skipped"][i].astype(bool)
    Acov = np.isin(R, ["not_interesting", "not_interesting+interpolable"])
    Bcov = np.isin(R, ["interpolable", "not_interesting+interpolable"])
    c_act = np.where(~S, "measured", np.where(Acov, "no_line", "predictable"))
    c_wrong = S & ((Acov & z["interesting"][i].astype(bool)) | (Bcov & z["fail_prior"][i].astype(bool)))
    u = np.load(ROOT / "results/hook/uncertified_latent_z1.00.npz")
    u_act, u_wrong = u["action"].copy(), u["wrong"]
    u_act[u_act == "seed"] = "measured"
    c_act = c_act.astype(object); c_act[lv <= 2] = "measured"

    fig = plt.figure(figsize=(7.2, 6.4), facecolor="white")
    FW, FH = 7.2, 6.4
    mw = 0.30; mh = mw * FW / FH
    keys = ["measured", "no_line", "predictable"]
    cmap = ListedColormap([COL[k] for k in keys])

    def amap(x, y, act, wrong, title):
        ax = fig.add_axes([x, y, mw, mh])
        code = np.array([keys.index(a) for a in act])
        ax.imshow(code[nn], origin="lower", cmap=cmap, vmin=-0.5, vmax=2.5, extent=ext, alpha=0.85,
                  interpolation="nearest")
        ax.contour(XX, YY, pres.astype(float), levels=[0.5], colors=INK, linewidths=0.5)
        ax.scatter(xy[wrong, 0], xy[wrong, 1], s=8, marker="x", c=RED, linewidths=0.7)
        ax.set_title(title, loc="left", fontsize=7.4)
        ax.set_xticks([]); ax.set_yticks([])
        return ax

    cert = lv >= 3
    rowu = [r for r in res["uncertified"] if r["sd"] == "latent" and r["z"] == 1.0][0]
    amap(0.08, 0.50, u_act, u_wrong,
         f"(a) Uncertified: GP, 68 % interval within tolerance\n     {rowu['measured']} measured, "
         f"{100 * rowu['wrong_rate']:.0f} % skipped wrongly, no rate stated")
    amap(0.58, 0.50, c_act, c_wrong,
         f"(b) Certified (Fig. 1): {int((~S).sum())} measured,\n     "
         f"{100 * c_wrong[cert].mean():.0f} % skipped wrongly, at most 20 % guaranteed")

    # (c) cost against realised wrong-skip share
    ax = fig.add_axes([0.08, 0.14, 0.38, 0.25])
    cm, cr = np.array(res["certified"]["measured"]), np.array(res["certified"]["wrong_rate"])
    ax.scatter(cm, cr, s=4, c=GRID, linewidths=0, label="certified, 250 campaigns")
    ax.scatter([int((~S).sum())], [c_wrong[cert].mean()], s=30, marker="D", c=BLUE, edgecolors="white",
               linewidths=0.6, zorder=3, label="certified, Fig. 1")
    for r in res["uncertified"]:
        mk = "o" if r["sd"] == "latent" else "s"
        ax.scatter([r["measured"]], [r["wrong_rate"]], s=26, marker=mk, facecolors="none", edgecolors=INK, lw=0.9,
                   zorder=4)
    for r in res["uncertified"]:
        if r["sd"] == "latent" and r["z"] in (1.0, 1.96):
            ax.annotate(f"z = {r['z']:g}", (r["measured"], r["wrong_rate"]), xytext=(6, 4),
                        textcoords="offset points", fontsize=6.3, color=INK2)
    ax.annotate("predictive sd,\nevery z", (922, 0.003), xytext=(-6, 14), textcoords="offset points", fontsize=6.3,
                color=INK2, ha="right")
    ax.axhline(BUDGET, color=RED, lw=1.0)
    ax.text(1071, BUDGET + 0.005, "certified budget", color=RED, fontsize=6.3, ha="right", va="bottom")
    ax.set_xlim(560, 1080); ax.set_ylim(-0.01, 0.27)
    ax.set_xlabel("sites measured (of 1071)", fontsize=7)
    ax.set_ylabel("share of levels 3–6 skipped wrongly", fontsize=7)
    ax.tick_params(labelsize=6.5)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.set_title("(c) Cost and realised error", loc="left", fontsize=7.6)

    # (d) promised against realised, sites skipped as predictable
    ax = fig.add_axes([0.62, 0.14, 0.33, 0.25])
    lat = [r for r in res["uncertified"] if r["sd"] == "latent" and r["wrong_pred"] is not None]
    xs_ = np.arange(len(lat))
    ax.bar(xs_ - 0.18, [r["nominal"] for r in lat], 0.34, color=GRID, label="promised by the interval")
    ax.bar(xs_ + 0.18, [r["wrong_pred"] for r in lat], 0.34, color=RED, label="realised")
    for k, r in enumerate(lat):
        ax.text(k + 0.18, r["wrong_pred"] + 0.01, f"{r['n_skip_pred']}", ha="center", fontsize=6, color=INK2)
    ax.set_xticks(xs_); ax.set_xticklabels([f"z = {r['z']:g}" for r in lat], fontsize=6.5)
    ax.set_ylabel("share of predictable skips wrong", fontsize=7)
    ax.tick_params(labelsize=6.5)
    ax.legend(fontsize=6.3, frameon=False, loc="upper right", ncol=2, bbox_to_anchor=(1.0, 1.04))
    ax.set_ylim(0, 0.48)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.set_title("(d) GP intervals, latent sd: promised\n     and realised (numbers: skips)", loc="left", fontsize=7.6)

    handles = [plt.Rectangle((0, 0), 1, 1, color=COL["measured"], label="measured"),
               plt.Rectangle((0, 0), 1, 1, color=COL["no_line"], label="skipped: no line / not of interest"),
               plt.Rectangle((0, 0), 1, 1, color=COL["predictable"], label="skipped: predictable"),
               Line2D([], [], ls="", marker="x", color=RED, markersize=5, label="wrong skip"),
               Line2D([], [], ls="", marker="o", mfc="none", color=INK, markersize=5, label="uncertified, latent sd"),
               Line2D([], [], ls="", marker="s", mfc="none", color=INK, markersize=5,
                      label="uncertified, predictive sd"),
               Line2D([], [], ls="", marker="o", color=GRID, markersize=3.5, label="certified, 250 campaigns"),
               Line2D([], [], ls="", marker="D", color=BLUE, markersize=4.5, label="certified, Fig. 1")]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=6.3, frameon=False, bbox_to_anchor=(0.5, 0.0),
               columnspacing=1.0, handletextpad=0.4)
    fig.text(0.08, 0.972, "The same scan without certification", fontsize=10.5, fontweight="bold", color=INK)
    fig.text(0.08, 0.945, "Uncertified: a GP refitted after each level skips a site when it is sure there is no line, "
             "or when its\nz-interval on the width lies within the tolerance (0.02 nm$^{-1}$). Same design, seed "
             "sites and scoring of wrong skips.", fontsize=6.9, color=INK2, va="top", linespacing=1.4)
    fig.savefig(FIG / "fig_uncertified.png", dpi=200)
    fig.savefig(FIG / "fig_uncertified.pdf")
    print("wrote", FIG / "fig_uncertified.png")


if __name__ == "__main__":
    main()
