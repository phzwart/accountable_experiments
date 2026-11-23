"""
Figure 1 (round 3): one Gaussian process on the NaCl (200)-width scan, certified or trusting itself.
(a) A certified plan of average cost with the process as predictor and its own posterior probability of a
    wrong skip as the frozen interpolation score (quantile path, 20 % per level at 0.80; 50 campaigns).
(b) The same process and the same probability, skipping where the probability is at most alpha = 0.20 (SI 7.2).
(c) Stated against realised share of certified-level sites skipped wrongly, with sites measured.

Former versions: fig_hook_three_nacl.py (skip rule on the width interval), fig_hook_three_syn.py (synthetic map).

    python -m experiments.uncertified_all nacl && python manuscript/figures/fig_hook_three.py
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
from fig_hook import ROOT, INK, INK2, GRID, RED  # noqa: E402
from fig_datasets import nacl_fwhm  # noqa: E402
from fig_hook_compare import COL, BLUE, certified_cloud  # noqa: E402
from experiments.record import OUT as REC, REASONS, build  # noqa: E402

ROW = "nacl_fwhm_nested_gpfail_mle"
NN_ROW = "nacl_fwhm_nested_watson"
ORANGE = "#eb6834"
PURPLE = "#8e6cc8"
NOT_INT = ["not_interesting", "not_interesting+interpolable"]


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK})
    z = np.load(REC / ROW / "sites.npz")
    lv = np.asarray(z["levels"]); cert = lv >= 3
    ds, _, _ = build(ROW, 0, {})
    xy = np.asarray(ds.meta["xy_mm"], float)[z["site_index"]]
    img, pres, (xs, ys), _, _ = nacl_fwhm()
    ext = (xs[0], xs[-1], ys[0], ys[-1])
    XX, YY = np.meshgrid(xs, ys)
    _, nn = cKDTree(xy).query(np.c_[XX.ravel(), YY.ravel()])
    nn = nn.reshape(XX.shape)

    meas = z["measured"].sum(1)
    i = int(np.argmin(np.abs(meas - meas.mean())))          # a campaign of average cost
    R = np.array(REASONS)[z["reason"][i]]
    S = z["skipped"][i].astype(bool)
    A = np.isin(R, NOT_INT); B = np.isin(R, ["interpolable", "not_interesting+interpolable"])
    c_act = np.where(~S, "measured", np.where(A, "no_line", "predictable")).astype(object)
    c_wrong = S & ((A & z["interesting"][i].astype(bool)) | (B & z["fail_prior"][i].astype(bool)))

    U = ROOT / "results/uncertified"
    def unc(a, kind="predictive"):
        u = np.load(U / f"nacl_{kind}_a{a:.2f}.npz")
        act = u["action"].astype(object)
        act = np.where(np.isin(act, ["seed", "measured"]), "measured",
                       np.where(np.isin(act, NOT_INT), "no_line", "predictable")).astype(object)
        row = [r for r in json.loads((U / "nacl.json").read_text()) if r["kind"] == kind and abs(r["alpha"] - a) < 1e-9][0]
        return act, u["wrong"].astype(bool), row
    g_act, g_wrong, grow = unc(0.20)

    FW, FH = 7.2, 2.45
    fig = plt.figure(figsize=(FW, FH), facecolor="white")
    mw = 0.20; mh = mw * FW / FH
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
    amap(0.005, c_act, c_wrong, f"(a) GP, guaranteed\n{int((~S).sum())} measured; 20 % per level")
    amap(0.24, g_act, g_wrong, f"(b) Same GP, trusting itself\n{grow['measured']} measured (α = 0.20)")

    ax = fig.add_axes([0.66, y0 + 0.03, 0.33, mh - 0.08])
    cm, cr = certified_cloud(ROW, cert)
    cr = 100 * np.asarray(cr)
    nm, nr = certified_cloud(NN_ROW, cert)
    nr = 100 * np.asarray(nr)
    rows = [("GP, guaranteed\n(mean, 50)", 20.0, cr.mean(), np.percentile(cr, [5, 95]), int(round(np.mean(cm))), PURPLE),
            ("natural neighbour,\nguaranteed (mean, 250)", 20.0, nr.mean(), np.percentile(nr, [5, 95]), int(round(np.mean(nm))), BLUE)]
    for a in (0.05, 0.20, 0.32):
        _, _, r = unc(a)
        rows.append((f"GP, trusting itself,\nα = {a:.2f}", 100 * r["stated_rate"], 100 * r["wrong_rate"], None, r["measured"], ORANGE))
    n = len(rows)
    for k, (lab, st, re, rng, mm, col) in enumerate(rows):
        yk = n - 1 - k
        ax.plot([st, re], [yk, yk], color=GRID, lw=2.0, zorder=1, solid_capstyle="round")
        ax.scatter([st], [yk], marker="|", s=80, c=col, linewidths=1.5, zorder=3)
        ax.scatter([re], [yk], marker="o", s=20, c=col, edgecolors="white", linewidths=0.5, zorder=4)
        if rng is not None:
            ax.plot(rng, [yk, yk], color=col, lw=0.8, zorder=2)
        ax.text(27.0, yk, f"{mm}", va="center", ha="right", fontsize=6.4, color=INK2)
    ax.set_yticks(list(range(n - 1, -1, -1)), [r[0] for r in rows], fontsize=6.0)
    ax.set_xlim(-0.5, 27.8); ax.set_ylim(-0.6, n - 0.4)
    ax.set_xlabel("share of sites skipped in error (%)", fontsize=6.8)
    ax.text(27.0, n - 0.38, "measured", ha="right", va="bottom", fontsize=6.0, color=INK2)
    ax.set_title("(c) Stated (|) and realised (●)", loc="left", fontsize=7.2, pad=10)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.tick_params(labelsize=6.2)

    handles = [plt.Rectangle((0, 0), 1, 1, color=COL["measured"], label="measured"),
               plt.Rectangle((0, 0), 1, 1, color=COL["no_line"], label="skipped: no line"),
               plt.Rectangle((0, 0), 1, 1, color=COL["predictable"], label="skipped: predictable"),
               Line2D([], [], ls="", marker="x", color=RED, markersize=4.5, label="skip error, found afterwards"),
               Line2D([], [], color=INK, lw=0.6, label="edge of the line")]
    fig.legend(handles=handles, loc="lower left", ncol=5, fontsize=6.2, frameon=False, bbox_to_anchor=(0.0, 0.0),
               columnspacing=1.0, handletextpad=0.4)
    fig.text(0.005, 0.94, "One Gaussian process, one scan: with conformal thresholds and with its own uncertainty",
             fontsize=8.4, fontweight="bold", color=INK)
    fig.savefig(FIG / "fig_hook_three.png", dpi=220)
    fig.savefig(FIG / "fig_hook_three.pdf")
    print("wrote", FIG / "fig_hook_three.png", "campaign", int(z["seeds"][i]), int((~S).sum()), "wrong", int(c_wrong.sum()),
          "cert mean", round(cr.mean(), 1), np.percentile(cr, [5, 95]).round(1), round(float(np.mean(cm))),
          "NN", round(nr.mean(), 1), "GP a=0.20", grow["measured"], round(100 * grow["stated_rate"], 2), round(100 * grow["wrong_rate"], 2))


if __name__ == "__main__":
    main()
