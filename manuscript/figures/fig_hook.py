"""
Hook figure (Fig. 1): a guarantee on what was not measured. NaCl microdiffraction scan, one campaign of
average cost (quantile path, natural-neighbour interpolation, (200) width claim; seed 44: 612 of 1071
design sites measured, against a mean of 614).
(a) Width of the (200) line over the full raster (the truth, known here because the scan was measured
    everywhere), with the sites the campaign measured.
(b) The certified map at the resolution of the deepest level (median spacing 0.35 mm), filled by nearest
    design site: measured widths, and decision-time natural-neighbour predictions where skipped as
    predictable; grey where no line was measured or the site was certified as not of interest.
(c) A display map drawn afterwards: noise-free GP regression on the measured sites (width where the line is
    present, a second GP on presence), length scale bounded below by the design spacing (the likelihood
    settles on the bound). No certificate attaches to it.
(d) The certified action of every design site: measured for the seed, for calibration or because no
    claim covered it; skipped as not of interest, as predictable or both. Crosses: wrong skips.
(e) At each site skipped under the interpolation claim, the error of the predicted (200) width at the
    time of the decision, relative to the true width (agreed absence counts as zero). Red line on the
    colour bar: the tolerance of 0.02 nm^-1 as a share of the median width. Errors come from a replay of
    the campaign (python -m experiments.hook_errors).
(f) The guarantee on each certified level: at most 20 % of the level skipped wrongly, with confidence
    0.80. Dots: the realised wrong-skip rate in each of 250 campaigns; diamonds: this campaign.
    Numbers: levels over budget against the number the guarantee allows.

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


def final_map(xy_m, w_m, p_m, XX, YY, noise=True, ls_min=0.05):
    """GP regression of the width on the measured sites where the line is present, and of the presence
    indicator on all measured sites (thresholded at one half); hyperparameters by maximum likelihood."""
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C, WhiteKernel

    Q = np.c_[XX.ravel(), YY.ravel()]
    ok = p_m & np.isfinite(w_m)
    k = C(1.0) * RBF(max(1.0, 1.5 * ls_min), (ls_min, 20.0))
    if noise:
        k = k + WhiteKernel(0.1, (1e-4, 10.0))
    jit = 1e-10 if noise else 1e-4  # without a noise term the GP interpolates the measurements
    mu, sd = w_m[ok].mean(), w_m[ok].std()
    gw = GaussianProcessRegressor(k, alpha=jit, normalize_y=False, n_restarts_optimizer=2, random_state=0)
    gw.fit(xy_m[ok], (w_m[ok] - mu) / sd)
    gp_w = (gw.predict(Q) * sd + mu).reshape(XX.shape)
    gpp = GaussianProcessRegressor(k, alpha=jit, n_restarts_optimizer=2, random_state=0)
    gpp.fit(xy_m, p_m.astype(float) - 0.5)
    gp_p = (gpp.predict(Q) > 0).reshape(XX.shape)
    return gp_w, gp_p, (str(gw.kernel_), str(gpp.kernel_))


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

    # prediction errors at decision time, from the replay of this campaign
    e = np.load(ROOT / "results" / "hook" / "errors_s044.npz")
    assert int(e["measured"].sum()) == int(measured.sum())
    wt, wh = e["fwhm_true"], e["fwhm_hat"]
    covB = skipped & b_cov
    width = covB & e["has_true"] & e["has_hat"] & np.isfinite(wt) & np.isfinite(wh)
    absent = covB & ~e["has_true"] & ~e["has_hat"]
    mism = covB & (e["has_true"] != e["has_hat"])
    rel = np.full(len(site), np.nan)
    rel[width] = 100 * np.abs(wh[width] - wt[width]) / wt[width]
    rel[absent] = 0.0
    tol_med = 100 * float(e["fwhm_eps"]) / np.median(wt[width])

    # final map for display: a GP fitted afterwards to the measured sites (width where the line is
    # present, and a second GP on the presence indicator); the certificates use the decision-time predictor
    ixs = np.searchsorted(xs, xy[:, 0].round(4).clip(xs[0], xs[-1]))
    iys = np.searchsorted(ys, xy[:, 1].round(4).clip(ys[0], ys[-1]))
    w_site, p_site = img[iys, ixs], pres[iys, ixs]
    d_, _ = cKDTree(xy).query(xy, k=2)
    spacing = float(np.median(d_[:, 1]))
    gp_w, gp_p, gp_txt = final_map(xy[measured], w_site[measured], p_site[measured], XX, YY, noise=False,
                                   ls_min=spacing)
    # the certified map at the design resolution: measured widths, and the decision-time predictions at
    # sites skipped as predictable; no line where measured without one or certified as not of interest
    nat = np.where(measured & p_site, w_site, np.nan)
    pr = skipped & (reason == "interpolable") & e["has_hat"]
    nat[pr] = e["fwhm_hat"][pr]

    FW, FH = 7.2, 7.0
    fig = plt.figure(figsize=(FW, FH), facecolor="white")
    mw = 0.27
    mh = mw * FW / FH
    top_y, bot_y = 0.575, 0.165
    X0 = (0.075, 0.385, 0.695)
    pos = {"a": (X0[0], top_y), "b": (X0[1], top_y), "c": (X0[2], top_y), "d": (X0[0], bot_y), "e": (X0[1], bot_y)}

    def mapax(k):
        x, y = pos[k]
        return fig.add_axes([x, y, mw, mh])

    def mapstyle(ax, title, left=True, bottom=True):
        ax.set_title(title, loc="left", fontsize=7.4, pad=4)
        if bottom:
            ax.set_xlabel("stage x (mm)", fontsize=6.8)
        else:
            ax.set_xticklabels([])
        if left:
            ax.set_ylabel("stage y (mm)", fontsize=6.8)
        else:
            ax.set_yticklabels([])
        ax.tick_params(labelsize=6.2)

    wlo, whi = np.nanpercentile(img, 2), np.nanpercentile(img, 98)
    absent_bg = ListedColormap(["#ecebe7"])

    # (a) the true width with the measured locations
    ax = mapax("a")
    ax.imshow(np.where(pres, np.nan, 0.0), origin="lower", cmap=absent_bg, extent=ext)
    imw = ax.imshow(img, origin="lower", cmap="Blues", vmin=wlo, vmax=whi, extent=ext, interpolation="nearest")
    ax.scatter(xy[measured, 0], xy[measured, 1], s=1.6, c=INK, linewidths=0)
    mapstyle(ax, f"(a) Truth, with the {int(measured.sum())} of\n     {len(site)} sites measured", bottom=False)

    # (b) the certified map at the resolution of the deepest level
    ax = mapax("b")
    ax.imshow(np.zeros_like(img), origin="lower", cmap=absent_bg, extent=ext)
    ax.imshow(nat[nn], origin="lower", cmap="Blues", vmin=wlo, vmax=whi, extent=ext, interpolation="nearest")
    outline(ax)
    mapstyle(ax, f"(b) Certified map at {spacing:.2f} mm:\n     measured or certified prediction", left=False,
             bottom=False)
    cax = ax.inset_axes([0.0, -0.07, 1.0, 0.04])
    cb = fig.colorbar(imw, cax=cax, orientation="horizontal")
    cb.ax.tick_params(labelsize=6.2)
    cb.set_label("(200) width in (a)–(c), nm$^{-1}$; grey: no line", fontsize=6.4, labelpad=1)

    # (c) the final map, drawn afterwards with a GP
    ax = mapax("c")
    ax.imshow(np.where(gp_p, np.nan, 0.0), origin="lower", cmap=absent_bg, extent=ext)
    ax.imshow(np.where(gp_p, gp_w, np.nan), origin="lower", cmap="Blues", vmin=wlo, vmax=whi, extent=ext,
              interpolation="nearest")
    outline(ax)
    mapstyle(ax, "(c) Display map: GP fitted afterwards,\n     length scale set by the spacing", left=False, bottom=False)

    # (d) this campaign: certified action, filled
    keys = ["seed", "calibration", "no_certificate", "not_interesting", "interpolable", "not_interesting+interpolable"]
    code = np.array([keys.index(r) for r in reason])
    ax = mapax("d")
    cmap = ListedColormap([ACT[k][0] for k in keys])
    ax.imshow(code[nn], origin="lower", cmap=cmap, vmin=-0.5, vmax=len(keys) - 0.5, extent=ext, alpha=0.85,
              interpolation="nearest")
    outline(ax)
    ax.scatter(xy[wrong, 0], xy[wrong, 1], s=8, marker="x", c=RED, linewidths=0.7)
    mapstyle(ax, f"(d) Every action certified:\n     {int(skipped.sum())} skips under named claims")

    # (e) this campaign: how far off the certified prediction was at each site skipped as predictable
    ax = mapax("e")
    bg = np.where(measured, 0, 1)[nn].astype(float)  # measured: white; skipped under the interest claim only: grey
    ax.imshow(bg, origin="lower", cmap=ListedColormap(["white", "#dcdbd7"]), vmin=0, vmax=1, extent=ext,
              interpolation="nearest")
    cm = plt.get_cmap("Purples")
    cm = ListedColormap(cm(np.linspace(0.18, 1.0, 256)))
    cm.set_over(cm(1.0))
    im = ax.imshow(np.ma.masked_invalid(rel[nn]), origin="lower", cmap=cm, vmin=0, vmax=50, extent=ext,
                   interpolation="nearest")
    outline(ax)
    ax.scatter(xy[wrong & b_cov, 0], xy[wrong & b_cov, 1], s=8, marker="x", c=RED, linewidths=0.7)
    mapstyle(ax, f"(e) Error of certified predictions:\n     median {np.median(rel[width]):.0f} % of the true width", left=False)
    cax = ax.inset_axes([1.03, 0.0, 0.04, 1.0])
    cb = fig.colorbar(im, cax=cax, extend="max")
    cb.ax.tick_params(labelsize=6.2)
    cb.set_label("|predicted − true| / true width (%)", fontsize=6.2)
    cb.ax.axhline(tol_med, color=RED, lw=1.0)

    # (f) the guarantee, level by level
    ax = fig.add_axes([0.80, bot_y + 0.035, 0.175, mh - 0.035])
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
        ax.text(k, 0.33, f"{ex}/{allow:.0f}", ha="center", va="center", fontsize=6.2, color=INK2)
    ax.axhline(BUDGET, color=RED, lw=1.0)
    ax.text(len(levels) - 0.45, BUDGET + 0.006, "budget", color=RED, fontsize=6.2, ha="right", va="bottom")
    ax.text(-0.5, 0.365, "levels over budget / allowed", fontsize=6.0, color=INK2, va="center")
    ax.set_xticks(range(len(levels)))
    ax.set_xticklabels([f"L{L}\n{np.sum(lv == L)}" for L in levels], fontsize=6.2)
    ax.set_xlabel("level and its sites", fontsize=6.8)
    ax.set_ylabel("share of the level skipped wrongly", fontsize=6.6, labelpad=2)
    ax.set_ylim(0, 0.38)
    ax.set_xlim(-0.6, len(levels) - 0.4)
    ax.tick_params(labelsize=6.5)
    ax.set_title("(f) The guarantee on every\n     level, 250 campaigns", loc="left", fontsize=7.4, pad=4)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    handles = [plt.Rectangle((0, 0), 1, 1, color=ACT[k][0], label=ACT[k][3]) for k in keys]
    handles += [Line2D([], [], ls="", marker="x", color=RED, markersize=5, label="wrong skip (found afterwards)"),
                Line2D([], [], ls="", marker="D", color="#2a78d6", markersize=4.5, label="this campaign"),
                Line2D([], [], ls="", marker="o", color=GRID, markersize=3.5, label="each of 250 campaigns"),
                Line2D([], [], color=INK, lw=0.8, label="edge of the (200) signal"),
                plt.Rectangle((0, 0), 1, 1, fc="#dcdbd7", ec=INK2, lw=0.4, label="(e) skipped as not of interest"),
                plt.Rectangle((0, 0), 1, 1, fc="white", ec=INK2, lw=0.4, label="(e) measured")]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=6.4, frameon=False, bbox_to_anchor=(0.5, 0.005),
               columnspacing=1.2, handletextpad=0.4)

    cert = lv >= 3
    rate = wrong[cert].sum() / cert.sum()
    ex_all = sum(p["exceeded"] for p in picked)
    allow_all = sum(p["picked"] for p in picked)
    fig.text(0.075, 0.972, "A guarantee on what was not measured", fontsize=11, fontweight="bold", color=INK)
    fig.text(0.075, 0.928,
             "NaCl scan, (200) line width. Guarantee: at most 20 % of each level skipped wrongly, confidence 0.80.\n"
             f"This campaign: {100 * rate:.0f} % skipped wrongly.  250 campaigns: "
             f"{ex_all} of {len(picked)} levels over budget, {allow_all:.0f} allowed.",
             fontsize=7.2, color=INK2, va="center", linespacing=1.45)
    fig.savefig(FIG / "fig_hook.png", dpi=200)
    fig.savefig(FIG / "fig_hook.pdf")
    print(gp_txt); print("wrote", FIG / "fig_hook.png", "rate", round(rate, 3), "exceeded", ex_all, "allowed", round(allow_all, 1))


if __name__ == "__main__":
    main()
