"""
Hook figure: every action certified. One campaign on the IR map (quantile path, natural-neighbour
interpolation, seed 0). Left: amide-I absorbance (grey) with every design site marked by its certified
action; crosses: wrong skips found afterwards against the full measurement. Right: the evidence behind
three actions, (A) measured because no claim covered it, (B) skipped as predictable, (C) skipped as not
of interest: prediction from the sites measured before the decision (orange), the measurement taken
afterwards for the check (black), and the tolerance of the claim (shaded).

    python manuscript/figures/fig_hook.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from accountable.sibson import neighbour_weights  # noqa: E402
from experiments.ir_bioreef import adapter as IR  # noqa: E402
from experiments.record import REASONS  # noqa: E402
from fig_datasets import ir_amide  # noqa: E402
from fig_maps import STYLE, load  # noqa: E402

FIG = Path(__file__).resolve().parent
INK, INK2 = "#0b0b0b", "#52514e"
ORANGE, BLUE = "#eb6834", "#2a78d6"
ROW = "ir_nested_watson"


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2})
    ds, z, i, rec = load(ROW)
    site = z["site_index"]
    reason = np.array(REASONS)[z["reason"][i]]
    measured = z["measured"][i].astype(bool)
    skipped = z["skipped"][i].astype(bool)
    inter, fail = z["interesting"][i].astype(bool), z["fail_prior"][i].astype(bool)
    a_cov = np.isin(reason, ["not_interesting", "not_interesting+interpolable"])
    b_cov = np.isin(reason, ["interpolable", "not_interesting+interpolable"])
    wrong = skipped & ((a_cov & inter) | (b_cov & fail))
    lv = np.asarray(ds.levels)[site]
    P = np.asarray(ds.points, float)[site]
    Pum = P * 41.0
    I_all = ds.oracle.truth(site)
    x = ds.axis

    def predict(j):
        src = np.flatnonzero(measured & (lv < lv[j]))
        W = neighbour_weights(P[src], P[[j]], method="watson")
        return W.apply(I_all[src])[0]

    # pick three illustrative sites on certified levels
    cert = lv >= 3
    big = I_all.max(1) > 0.12

    def pick(mask, key):
        c = np.flatnonzero(mask)
        return c[np.argmax(key(c))]
    jA = pick(cert & (reason == "no_certificate") & fail & big, lambda c: I_all[c].max(1))
    far = np.linalg.norm(Pum - Pum[jA], axis=1) > 10
    jB = pick(cert & (reason == "interpolable") & ~wrong & big & far, lambda c: I_all[c].max(1))
    jC = pick(cert & (reason == "not_interesting") & ~wrong, lambda c: -np.abs(I_all[c].max(1) - 0.05))

    fig = plt.figure(figsize=(7.2, 4.8), facecolor="white")
    gs = fig.add_gridspec(3, 2, width_ratios=[1.55, 1.0], left=0.07, right=0.985, top=0.755, bottom=0.21,
                          wspace=0.22, hspace=0.75)
    ax = fig.add_subplot(gs[:, 0])
    img, _ = ir_amide()
    ax.imshow(img, origin="lower", cmap="Greys", vmin=-0.05, vmax=np.nanpercentile(img, 99.5),
              extent=(-0.5, img.shape[1] - 0.5, -0.5, img.shape[0] - 0.5), alpha=0.55)
    for key in ["not_interesting", "interpolable", "not_interesting+interpolable", "no_certificate", "calibration", "seed"]:
        sel = reason == key
        st = STYLE[key]
        ax.scatter(Pum[sel, 0], Pum[sel, 1], s=st["s"] * 0.9, c=st["c"], marker=st["m"], linewidths=0, zorder=2)
    ax.scatter(Pum[wrong, 0], Pum[wrong, 1], s=26, marker="x", c="#c0392b", linewidths=1.0, zorder=3)
    for lab, j in zip("ABC", (jA, jB, jC)):
        ax.scatter(Pum[j, 0], Pum[j, 1], s=90, facecolors="none", edgecolors=INK, linewidths=1.1, zorder=4)
        ax.annotate(lab, Pum[j], xytext=(5, 5), textcoords="offset points", fontsize=9, fontweight="bold", zorder=5)
    ax.set_xlabel("x (µm)")
    ax.set_ylabel("y (µm)")
    ax.set_xlim(-0.8, 41.8)
    ax.set_ylim(-0.8, 28.8)
    handles = [Line2D([], [], ls="", marker=STYLE[k]["m"], color=STYLE[k]["c"], markersize=5, label=STYLE[k]["label"])
               for k in ["seed", "calibration", "no_certificate", "not_interesting", "interpolable",
                         "not_interesting+interpolable"]]
    handles.append(Line2D([], [], ls="", marker="x", color="#c0392b", markersize=6, label="Wrong skip (found afterwards)"))
    ax.legend(handles=handles, fontsize=6.3, frameon=True, framealpha=0.9, loc="upper left",
              bbox_to_anchor=(-0.02, -0.14), ncol=3, columnspacing=0.8, handletextpad=0.3)

    titles = {jA: "A  measured: no claim covers it", jB: "B  skipped: predictable from neighbours",
              jC: "C  skipped: not of interest"}
    for k, j in enumerate((jA, jB, jC)):
        a = fig.add_subplot(gs[k, 1])
        pred = predict(j)
        if j == jC:
            a.axhline(IR.INTEREST_LEVEL, color=BLUE, lw=0.8, ls=":")
            a.fill_between(x, -0.02, IR.INTEREST_LEVEL, color=BLUE, alpha=0.10, lw=0)
        else:
            tol = IR.RTOL * np.abs(I_all[j]) + IR.ATOL
            a.fill_between(x, I_all[j] - tol, I_all[j] + tol, color=BLUE, alpha=0.13, lw=0)
        a.plot(x, I_all[j], color=INK, lw=1.0)
        a.plot(x, pred, color=ORANGE, lw=1.0, ls="--")
        a.invert_xaxis()
        a.set_title(titles[j], loc="left", fontsize=7.5)
        a.tick_params(labelsize=6.5)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        if k == 2:
            a.set_xlabel("wavenumber (cm$^{-1}$)", fontsize=7)
    fig.legend(handles=[Line2D([], [], color=ORANGE, ls="--", label="predicted before the decision"),
                        Line2D([], [], color=INK, label="measured (for the check)"),
                        plt.Rectangle((0, 0), 1, 1, color=BLUE, alpha=0.15, label="tolerance of the claim")],
               fontsize=6.3, frameon=False, loc="lower right", bbox_to_anchor=(0.985, 0.02), ncol=1)

    n = len(site)
    n_meas = int(measured.sum())
    rate = wrong[cert].sum() / cert.sum()
    fig.text(0.07, 0.955, "Every action certified", fontsize=11, fontweight="bold", color=INK)
    fig.text(0.07, 0.875,
             f"IR map, {n} sites: {n_meas} measured, each with the reason it was needed; {n - n_meas} skipped, each under a named claim.\n"
             f"Guarantee per level: at most 10 % of the sites skipped wrongly, with confidence 0.75.\n"
             f"Checked afterwards against the full measurement: {100 * rate:.1f} % of the sites on certified levels were skipped wrongly.",
             fontsize=7.3, color=INK2, va="center", linespacing=1.4)
    fig.savefig(FIG / "fig_hook_ir.png", dpi=200)
    fig.savefig(FIG / "fig_hook_ir.pdf")
    print("wrote", FIG / "fig_hook_ir.png", "rate", rate, "measured", n_meas)


if __name__ == "__main__":
    main()
