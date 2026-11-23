"""Interpolated maps after round 3 of one paired design (NaCl (200) width): rows are kernels, columns are the
cut that drove the campaign (uncertainty of the model, conformal thresholds), each with its error map against the measured raster.
Reads results/revision2/paired_gp_maps_d<D>.npz from experiments/paired_gp_maps.py."""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "src"), str(Path(__file__).parent)]
INK, INK2 = "#1f1f1f", "#5a5a5a"
TOL = 0.02
KLAB = {"fitted": "fitted noise", "nugget": "fixed nugget", "smooth": "long length scale"}
DLAB = {"uq": "uncertainty of model", "contract": "conformal thresholds"}
ABSENT = "#d9d7d0"


def main(design=0, src="campaign"):
    from fig_datasets import nacl_fwhm
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7, "axes.edgecolor": INK2})
    img, pres, (xs, ys), _, _ = nacl_fwhm()
    best = src != "campaign"
    R = np.load(ROOT / (f"results/revision2/paired_gp_bestfit_d{design}_{src}.npz" if best
                        else f"results/revision2/paired_gp_maps_d{design}.npz"))
    sh = tuple(R["shape"]); ix, iy, ridx = R["ix"], R["iy"], R["raster_idx"]
    vmin, vmax = np.nanpercentile(img, 5), np.nanpercentile(img, 95)
    cmap = plt.get_cmap("viridis").copy(); cmap.set_bad(ABSENT)
    ecmap = ListedColormap(["#f1efe9", "#e0a43a", "#b8322a"])   # within tolerance, width off, presence wrong

    def to_img(v):
        out = np.full(sh, np.nan); out[iy, ix] = v; return out

    FW, FH, S = 7.2, 4.85, 1.15                                # figure and panel size, inches
    fig = plt.figure(figsize=(FW, FH))
    gap, pgap = 0.04, 0.30
    X0 = 1.88
    xin = [X0, X0 + S + gap, X0 + 2 * S + gap + pgap, X0 + 3 * S + 2 * gap + pgap]
    yin = [FH - 0.42 - S - r * (S + 0.30) for r in range(3)]
    W, H = S / FW, S / FH
    xpos = [x / FW for x in xin]; ypos = [y / FH for y in yin]
    # measured raster
    ag = fig.add_axes([0.10 / FW, ypos[0], 1.35 / FW, 1.35 / FH])
    im = ag.imshow(img, origin="lower", cmap=cmap, vmin=vmin, vmax=vmax, interpolation="nearest")
    ag.set_xticks([]); ag.set_yticks([]); ag.set_title("measured raster", fontsize=7.2, color=INK, pad=3)
    for sp_ in ag.spines.values():
        sp_.set_visible(False)
    cb = fig.colorbar(im, cax=fig.add_axes([0.10 / FW, ypos[0] - 0.22 / FH, 1.35 / FW, 0.07 / FH]),
                      orientation="horizontal")
    cb.outline.set_visible(False); cb.ax.tick_params(labelsize=5.6, length=2)
    cb.set_label("(200) width, nm⁻¹", fontsize=6, labelpad=1)
    # legend for the error maps and overlays
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    hs = [Patch(fc=ABSENT, label="no line (stated or measured)"),
          Patch(fc="#f1efe9", ec="#bbbbbb", lw=0.4, label=f"within ±{TOL} nm⁻¹"),
          Patch(fc="#e0a43a", label="width off"), Patch(fc="#b8322a", label="presence wrong"),
          Line2D([], [], ls="", marker="x", ms=3, mec="black", mew=0.8, label="wrong skip (design site)")]
    lg = fig.legend(handles=hs, loc="upper left", bbox_to_anchor=(0.10 / FW, ypos[1] + 0.55 * H), frameon=False, fontsize=5.8,
                    handlelength=1.2, borderaxespad=0)

    for r, k in enumerate(("fitted", "nugget", "smooth")):
        for c, d in enumerate(("uq", "contract")):
            t = f"{k}_{d}"
            ph, wh = (R[f"{t}_bph"], R[f"{t}_bwh"]) if best else (R[f"{t}_ph"], R[f"{t}_wh"])
            line = ph >= 0.5
            mp = to_img(np.where(line, wh, np.nan))
            gtw, gtp = img[iy, ix], pres[iy, ix]
            err = np.where(line & gtp, np.where(np.abs(wh - np.nan_to_num(gtw, nan=1e9)) > TOL, 1, 0),
                           np.where(line != gtp, 2, -1))
            eimg = to_img(err.astype(float)); eimg[eimg < 0] = np.nan
            share = float((err > 0).mean())
            wrong = R[f"{t}_wrong"]; meas = R[f"{t}_measured"]; sk = R[f"{t}_skipped"]
            wx, wy = ix[ridx[wrong]], iy[ridx[wrong]]
            for j, (A, cm, kw) in enumerate(((mp, cmap, dict(vmin=vmin, vmax=vmax)),
                                             (eimg, ecmap.with_extremes(bad=ABSENT), dict(vmin=0, vmax=2)))):
                ax = fig.add_axes([xpos[2 * c + j], ypos[r], W, H])
                ax.imshow(A, origin="lower", cmap=cm, interpolation="nearest", **kw)
                ax.scatter(wx, wy, s=3.5, marker="x", c="white" if j == 0 else "black", lw=0.55, zorder=4)
                ax.set_xticks([]); ax.set_yticks([])
                for s in ax.spines.values():
                    s.set_visible(False)
                if r == 0:
                    ax.set_title(("interpolated map" if j == 0 else "error against raster"), fontsize=6.6,
                                 color=INK2, pad=2)
                if j == 1:
                    ax.text(-gap / S / 2, -0.04, f"{int(meas.sum())} measured · {int(wrong.sum())} of {int(sk.sum())} "
                            f"skips wrong · {share:.0%} of raster off", transform=ax.transAxes, ha="center",
                            va="top", fontsize=5.8, color=INK)
            if c == 0:
                fig.text(xpos[0] - 0.06 / FW, ypos[r] + H / 2, "steered with\n" + KLAB[k], rotation=90, ha="right", va="center",
                         fontsize=7.2, color=INK)
    if best:
        ph, wh = R["all_bph"], R["all_bwh"]; line = ph >= 0.5
        e = np.where(line, (~pres[iy, ix]) | (np.abs(wh - np.nan_to_num(img[iy, ix], nan=1e9)) > TOL), pres[iy, ix])
        fig.text(0.10 / FW, ypos[2] + 0.5 * H, "Same Matérn (ν = ½) fit on\nevery measured set.\n"
                 f"All {len(ridx)} design sites measured:\n{e.mean():.0%} of raster off.", fontsize=6.2,
                 color=INK, va="center", linespacing=1.4)
    for c, d in enumerate(("uq", "contract")):
        fig.text((xpos[2 * c] + xpos[2 * c + 1] + W) / 2, 1 - 0.06 / FH, f"cut by {DLAB[d]}", ha="center",
                 va="top", fontsize=8, color=INK, weight="bold")
    out = ROOT / ("manuscript/figures/figS_paired_maps" + (("_matern" if src == "nu0.5" else f"_{src}") if best else ""))
    for ext in ("png", "pdf", "svg"):
        fig.savefig(f"{out}.{ext}", dpi=300 if ext == "png" else None)
    print(out)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 0, sys.argv[2] if len(sys.argv) > 2 else "campaign")
