"""
Hook figure (Fig. 1): a guarantee on what was not measured. NaCl microdiffraction scan, one campaign of
average cost (quantile path, natural-neighbour interpolation, (200) width claim; seed 44: 612 of 1071
design sites measured, against a mean of 614).
(a) Height of the (200) line over the full raster (the truth, known here because the scan was measured
    everywhere), with the sites the campaign measured.
(b) The certified action of every design site, filled over the scan (nearest design site): measured for
    the seed, for calibration or because no claim covered it; skipped as not of interest, as predictable
    or both. Crosses: wrong skips, found afterwards against the full scan.
(c) Over 250 campaigns: the share of campaigns in which each design site was skipped wrongly.
(d) The guarantee on each certified level: at most 20 % of the level skipped wrongly, with confidence
    0.80. Dots: the realised wrong-skip rate in each of 250 campaigns; diamonds: this campaign.
    Numbers: campaigns in which the level exceeded its budget, against the number the guarantee allows.

    python manuscript/figures/fig_hook.py
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from experiments.record import OUT as REC, REASONS, build  # noqa: E402
from fig_datasets import nacl_fwhm  # noqa: E402

FIG = Path(__file__).resolve().parent
INK, INK2, GRID = "#0b0b0b", "#52514e", "#b9b8b3"
RED = "#c0392b"
ROW, SEED, BUDGET = "nacl_fwhm_nested_watson", 44, 0.20
ACT = {  # (colour, marker, size, label); measured actions in neutrals, skips in the categorical slots
    "seed": ("#5c5b58", "D", 9, "measured: seed"),
    "calibration": ("#9a9995", "s", 9, "measured: calibration draw"),
    "no_certificate": ("#d6d5d1", "s", 8, "measured: no claim covers it"),
    "not_interesting": ("#eda100", "o", 7, "skipped: not of interest"),
    "interpolable": ("#1baf7a", "o", 7, "skipped: predictable"),
    "not_interesting+interpolable": ("#2a78d6", "o", 7, "skipped: both claims"),
}


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK})
    z = np.load(REC / ROW / "sites.npz")
    i = int(np.flatnonzero(z["seeds"] == SEED)[0])
    ds, _, _ = build(ROW, SEED, {})
    site = z["site_index"]
    xy = np.asarray(ds.meta["xy_mm"], float)[site]
    reason = np.array(REASONS)[z["reason"][i]]
    measured = z["measured"][i].astype(bool)
    skipped = z["skipped"][i].astype(bool)
    inter, fail = z["interesting"][i].astype(bool), z["fail_prior"][i].astype(bool)
    a_cov = np.isin(reason, ["not_interesting", "not_interesting+interpolable"])
    b_cov = np.isin(reason, ["interpolable", "not_interesting+interpolable"])
    wrong = skipped & ((a_cov & inter) | (b_cov & fail))
    lv = np.asarray(z["levels"])

    runs = [json.loads(l) for l in gzip.open(REC / ROW / "runs.jsonl.gz", "rt")]
    picked = [p for p in json.loads((REC / "PICKED.json").read_text()) if p["row"] == ROW and p["event"] == "R_E"]

    # raster of the scan, each pixel filled by its nearest design site
    img, pres, (xs, ys), _, h = nacl_fwhm()
    ext = (xs[0], xs[-1], ys[0], ys[-1])
    XX, YY = np.meshgrid(xs, ys)
    _, nn = cKDTree(xy).query(np.c_[XX.ravel(), YY.ravel()])
    nn = nn.reshape(XX.shape)

    ring = pres.astype(float)

    def outline(ax):
        ax.contour(XX, YY, ring, levels=[0.5], colors=INK, linewidths=0.6)

    S = z["skipped"].astype(bool)
    Rall = np.array(REASONS)[z["reason"]]
    A_all = np.isin(Rall, ["not_interesting", "not_interesting+interpolable"])
    B_all = np.isin(Rall, ["interpolable", "not_interesting+interpolable"])
    W_all = S & ((A_all & z["interesting"].astype(bool)) | (B_all & z["fail_prior"].astype(bool)))
    freq = W_all.mean(0)

    fig = plt.figure(figsize=(7.2, 6.1), facecolor="white")
    gs = fig.add_gridspec(2, 2, left=0.08, right=0.97, top=0.83, bottom=0.15, wspace=0.38, hspace=0.38)

    def mapstyle(ax, title, left=True, bottom=True):
        ax.set_title(title, loc="left", fontsize=8)
        if bottom:
            ax.set_xlabel("stage x (mm)", fontsize=7)
        if left:
            ax.set_ylabel("stage y (mm)", fontsize=7)
        ax.tick_params(labelsize=6.5)

    # (a) truth with the measured locations
    ax = fig.add_subplot(gs[0, 0])
    ax.imshow(np.where(pres, np.nan, 0.0), origin="lower", cmap="Greys", vmin=-1, vmax=4, extent=ext)
    ax.imshow(h, origin="lower", cmap="Blues", extent=ext,
              norm=LogNorm(vmin=np.nanpercentile(h, 2), vmax=np.nanpercentile(h, 99.5)))
    ax.scatter(xy[measured, 0], xy[measured, 1], s=2.0, c=INK, linewidths=0)
    mapstyle(ax, f"(a) Measured: {int(measured.sum())} of {len(site)} sites,\n     on the true (200) line height")

    # (b) this campaign: certified action, filled
    keys = ["seed", "calibration", "no_certificate", "not_interesting", "interpolable", "not_interesting+interpolable"]
    code = np.array([keys.index(r) for r in reason])
    ax = fig.add_subplot(gs[0, 1])
    cmap = ListedColormap([ACT[k][0] for k in keys])
    ax.imshow(code[nn], origin="lower", cmap=cmap, vmin=-0.5, vmax=len(keys) - 0.5, extent=ext, alpha=0.85,
              interpolation="nearest")
    outline(ax)
    ax.scatter(xy[wrong, 0], xy[wrong, 1], s=10, marker="x", c=RED, linewidths=0.8)
    mapstyle(ax, f"(b) Every action certified: {int(skipped.sum())} sites\n     skipped, each under a named claim", left=False)

    # (c) where wrong skips happen, over 250 campaigns
    ax = fig.add_subplot(gs[1, 0])
    im = ax.imshow(freq[nn], origin="lower", cmap="Reds", vmin=0, vmax=max(0.5, np.percentile(freq, 99)), extent=ext,
                   interpolation="nearest")
    outline(ax)
    mapstyle(ax, "(c) Where skips went wrong: share of\n     250 campaigns, per site")
    cb = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.02)
    cb.ax.tick_params(labelsize=6.5)

    # (d) the guarantee, level by level
    ax = fig.add_subplot(gs[1, 1])
    levels = sorted({pl["L"] for r in runs for pl in r["per_level"] if not pl.get("empty")})
    rng = np.random.default_rng(0)
    for k, L in enumerate(levels):
        rates = np.array([pl["level"]["E_rate"] for r in runs for pl in r["per_level"]
                          if pl["L"] == L and not pl.get("empty")])
        ax.scatter(np.full(len(rates), k) + rng.uniform(-0.25, 0.25, len(rates)), rates, s=3, c=GRID, linewidths=0)
        this = [pl["level"]["E_rate"] for r in runs if r["seed"] == SEED for pl in r["per_level"] if pl["L"] == L][0]
        ax.scatter([k], [this], s=34, marker="D", c="#2a78d6", edgecolors="white", linewidths=0.6, zorder=3)
        ex = sum(p["exceeded"] for p in picked if p["L"] == L)
        allow = sum(p["picked"] for p in picked if p["L"] == L)
        ax.text(k, 0.33, f"{ex} / {allow:.0f}", ha="center", va="center", fontsize=6.5, color=INK2)
    ax.axhline(BUDGET, color=RED, lw=1.0)
    ax.text(len(levels) - 0.45, BUDGET + 0.006, "budget", color=RED, fontsize=6.5, ha="right", va="bottom")
    ax.text(-0.5, 0.365, "over budget / allowed", fontsize=6.3, color=INK2, va="center")
    ax.set_xticks(range(len(levels)))
    ax.set_xticklabels([f"level {L}\n{np.sum(lv == L)} sites" for L in levels], fontsize=6.5)
    ax.set_ylabel("share of the level skipped wrongly", fontsize=7)
    ax.set_ylim(0, 0.38)
    ax.set_xlim(-0.6, len(levels) - 0.4)
    ax.tick_params(labelsize=6.5)
    ax.set_title("(d) The guarantee, checked on every level\n     of 250 campaigns", loc="left", fontsize=8)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    handles = [plt.Rectangle((0, 0), 1, 1, color=ACT[k][0], label=ACT[k][3]) for k in keys]
    handles += [Line2D([], [], ls="", marker="x", color=RED, markersize=5, label="wrong skip (found afterwards)"),
                Line2D([], [], ls="", marker="D", color="#2a78d6", markersize=4.5, label="this campaign"),
                Line2D([], [], ls="", marker="o", color=GRID, markersize=3.5, label="each of 250 campaigns"),
                Line2D([], [], color=INK, lw=0.8, label="edge of the (200) signal")]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=6.4, frameon=False, bbox_to_anchor=(0.5, 0.0),
               columnspacing=1.2, handletextpad=0.4)

    cert = lv >= 3
    rate = wrong[cert].sum() / cert.sum()
    ex_all = sum(p["exceeded"] for p in picked)
    allow_all = sum(p["picked"] for p in picked)
    fig.text(0.08, 0.965, "A guarantee on what was not measured", fontsize=11, fontweight="bold", color=INK)
    fig.text(0.08, 0.905,
             "NaCl scan, (200) line width. Guarantee: at most 20 % of each level skipped wrongly, confidence 0.80.\n"
             f"This campaign: {100 * rate:.0f} % skipped wrongly.  250 campaigns: "
             f"{ex_all} of {len(picked)} levels over budget, {allow_all:.0f} allowed.",
             fontsize=7.2, color=INK2, va="center", linespacing=1.45)
    fig.savefig(FIG / "fig_hook.png", dpi=200)
    fig.savefig(FIG / "fig_hook.pdf")
    print("wrote", FIG / "fig_hook.png", "rate", round(rate, 3), "exceeded", ex_all, "allowed", round(allow_all, 1))


if __name__ == "__main__":
    main()
