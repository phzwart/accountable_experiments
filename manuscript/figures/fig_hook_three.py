"""
Figure 1: two campaigns on the synthetic phase map, and what each states about its wrong skips.
(a) A certified plan of average cost (quantile path, natural-neighbour interpolation, 20 % per level at 0.80).
(b) A campaign guided by the Gaussian process of the certified GP campaigns, refitted after each level, skipping a
    site when its own probability of a wrong skip is at most 0.20, with the predictive standard deviation (SI 7.2).
(c) Stated against realised share of certified-level sites skipped wrongly, with sites measured; the GP on the
    synthetic map at three thresholds and on the NaCl scan, where its fitted noise makes the statement hold.

    python -m experiments.uncertified_all syn && python manuscript/figures/fig_hook_three.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

FIG = Path(__file__).resolve().parent
sys.path.insert(0, str(FIG))
from fig_hook import ROOT, INK, INK2, GRID, RED  # noqa: E402
from fig_hook_compare import COL, BLUE, certified_cloud  # noqa: E402
from experiments.record import OUT as REC, REASONS, build  # noqa: E402
from experiments.synthetic_saxs import forward  # noqa: E402

ROW = "syn_env_nested_watson"
ORANGE = "#eb6834"
NOT_INT = ["not_interesting", "not_interesting+interpolable"]


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK})
    z = np.load(REC / ROW / "sites.npz")
    lv = np.asarray(z["levels"]); cert = lv >= 3
    ds, _, _ = build(ROW, 0, {})
    P = ds.points[z["site_index"]]
    meas = z["measured"].sum(1)
    i = int(np.argmin(np.abs(meas - meas.mean())))          # a campaign of average cost
    R = np.array(REASONS)[z["reason"][i]]
    S = z["skipped"][i].astype(bool)
    A = np.isin(R, NOT_INT); B = np.isin(R, ["interpolable", "not_interesting+interpolable"])
    c_act = np.where(~S, "measured", np.where(A, "no_line", "predictable")).astype(object)
    c_wrong = S & ((A & z["interesting"][i].astype(bool)) | (B & z["fail_prior"][i].astype(bool)))

    U = ROOT / "results/uncertified"
    def unc(key, a):
        u = np.load(U / f"{key}_predictive_a{a:.2f}.npz")
        act = u["action"].astype(object)
        act = np.where(np.isin(act, ["seed", "measured"]), "measured",
                       np.where(np.isin(act, NOT_INT), "no_line", "predictable")).astype(object)
        row = [r for r in json.loads((U / f"{key}.json").read_text()) if r["kind"] == "predictive" and abs(r["alpha"] - a) < 1e-9][0]
        return act, u["wrong"].astype(bool), row
    g_act, g_wrong, grow = unc("syn", 0.10)

    FW, FH = 7.2, 2.55
    fig = plt.figure(figsize=(FW, FH), facecolor="white")
    mw = 0.215; mh = mw * FW / FH * 0.92
    y0 = 0.16
    keys = ["measured", "no_line", "predictable"]
    gx, gy = np.meshgrid(np.linspace(0, 1, 400), np.linspace(0, 1, 400))
    ph = forward.classify(gx.ravel(), gy.ravel())
    codes = {v: k for k, v in enumerate(sorted(set(np.asarray(ph).tolist())))}
    phc = np.array([codes[v] for v in np.asarray(ph).tolist()], float).reshape(gx.shape)
    phc[gx + gy > 1] = np.nan

    def amap(x, act, wrong, title):
        ax = fig.add_axes([x, y0, mw, mh])
        for k in keys:
            m = act == k
            ax.scatter(P[m, 0], P[m, 1], s=2.2, c=COL[k], linewidths=0, zorder=2)
        ax.contour(gx, gy, phc, levels=np.arange(len(codes)) + 0.5, colors=INK, linewidths=0.7, zorder=1)
        ax.plot([0, 1, 0, 0], [0, 0, 1, 0], color=INK2, lw=0.5)
        ax.scatter(P[wrong, 0], P[wrong, 1], s=4, marker="x", c=RED, linewidths=0.45, zorder=3)
        ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.02); ax.set_aspect("equal")
        ax.set_title(title, loc="left", fontsize=7.2, pad=3)
        ax.axis("off")
    amap(0.005, c_act, c_wrong, f"(a) Certified, 10 % per level\n{int((~S).sum())} measured")
    amap(0.255, g_act, g_wrong, f"(b) GP, predictive s.d., α = 0.10\n{grow['measured']} measured; no bound")

    ax = fig.add_axes([0.665, y0 + 0.04, 0.325, mh - 0.1])
    cm, cr = certified_cloud(ROW, cert)
    cr = 100 * np.asarray(cr)
    rows = [("certified\n(mean, 250)", 10.0, cr.mean(), np.percentile(cr, [5, 95]), int(round(np.mean(cm))), BLUE)]
    for a in (0.05, 0.10, 0.20):
        _, _, r = unc("syn", a)
        rows.append((f"GP, α = {a:.2f}", 100 * r["stated_rate"], 100 * r["wrong_rate"], None, r["measured"], ORANGE))
    nacl = json.loads((ROOT / "results/hook/uncertified.json").read_text())
    nr = [r for r in nacl["uncertified"] if r["sd"] == "predictive" and r["z"] == 1.0][0]
    rows.append(("GP, NaCl scan", 100 * nr["stated_rate"], 100 * nr["wrong_rate"], None, nr["measured"], INK2))
    n = len(rows)
    for k, (lab, st, re, rng, mm, col) in enumerate(rows):
        yk = n - 1 - k
        ax.plot([st, re], [yk, yk], color=GRID, lw=2.0, zorder=1, solid_capstyle="round")
        ax.scatter([st], [yk], marker="|", s=80, c=col, linewidths=1.5, zorder=3)
        ax.scatter([re], [yk], marker="o", s=20, c=col, edgecolors="white", linewidths=0.5, zorder=4)
        if rng is not None:
            ax.plot(rng, [yk, yk], color=col, lw=0.8, zorder=2)
        ax.text(38.5, yk, f"{mm}", va="center", ha="right", fontsize=6.4, color=INK2)
    ax.set_yticks(list(range(n - 1, -1, -1)), [r[0] for r in rows], fontsize=6.4)
    ax.set_xlim(-0.5, 39.5); ax.set_ylim(-0.6, n - 0.4)
    ax.set_xlabel("share of sites skipped wrongly (%)", fontsize=6.8)
    ax.text(38.5, n - 0.38, "measured", ha="right", va="bottom", fontsize=6.0, color=INK2)
    ax.set_title("(c) Stated (|) and realised (●)", loc="left", fontsize=7.2, pad=10)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.tick_params(labelsize=6.4)

    handles = [Line2D([], [], ls="", marker="o", color=COL["measured"], markersize=3.5, label="measured"),
               Line2D([], [], ls="", marker="o", color=COL["no_line"], markersize=3.5, label="skipped: not of interest"),
               Line2D([], [], ls="", marker="o", color=COL["predictable"], markersize=3.5, label="skipped: predictable"),
               Line2D([], [], ls="", marker="x", color=RED, markersize=4.5, label="wrong skip, found afterwards"),
               Line2D([], [], color=INK, lw=0.6, label="phase boundary")]
    fig.legend(handles=handles, loc="lower left", ncol=5, fontsize=6.2, frameon=False, bbox_to_anchor=(0.0, 0.0),
               columnspacing=1.0, handletextpad=0.3)
    fig.text(0.005, 0.945, "Two campaigns on one phase map: only the certified plan bounds its rate before any skip",
             fontsize=8.6, fontweight="bold", color=INK)
    fig.savefig(FIG / "fig_hook_three.png", dpi=220)
    fig.savefig(FIG / "fig_hook_three.pdf")
    print("wrote", FIG / "fig_hook_three.png", "campaign", int(z["seeds"][i]), int((~S).sum()), "wrong", int(c_wrong.sum()),
          "GP", grow["measured"], grow["wrong"], round(100 * grow["stated_rate"], 2), round(100 * grow["wrong_rate"], 1),
          "cert mean", round(cr.mean(), 1), np.percentile(cr, [5, 95]).round(1), "NaCl", nr["stated_rate"], nr["wrong_rate"], nr["measured"])


if __name__ == "__main__":
    main()
