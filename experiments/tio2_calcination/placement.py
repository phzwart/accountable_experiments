"""
Where each claim sends the measurements in the 4-D recipe space.

    python -m experiments.tio2_calcination.placement

For the size and pattern claims (Delaunay protocol), the frequency with which a
recipe of a certified level was measured because no claim covered it, over all
campaigns. Reports the share of those measurements in the transformation front
(0.1 < rutile fraction < 0.9) and in the fast-coarsening region (top quartile of
the local change in anatase crystallite size), Spearman correlations with the
local change in each quantity, and a figure of 2-D projections.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import cKDTree
from scipy.stats import spearmanr

from . import adapter as A

RUNS = Path("runs/tio2")
OUT = Path("results/tio2")
INK, INK2 = "#0b0b0b", "#52514e"


def freq(row, n):
    files = sorted((RUNS / row).glob("s*.json"))
    f = np.zeros(n)
    for p in files:
        f[json.loads(p.read_text())["measured_nc"]] += 1
    return f / max(len(files), 1), len(files)


def main():
    ds = A.load()
    st = ds.meta["state"]
    P = np.asarray(ds.points)
    cert = np.asarray(ds.levels) > 2
    _, nn = cKDTree(P).query(P, k=9)
    nn = nn[:, 1:]
    fR, DA = st["f_R"], st["D_A"]
    v_front = np.median(np.abs(fR[:, None] - fR[nn]), axis=1)
    v_size = np.median(np.abs(DA[:, None] - DA[nn]), axis=1)
    front = (fR > 0.1) & (fR < 0.9)
    coarse = v_size >= np.quantile(v_size[cert], 0.75)
    out = {}
    rows = [r for r in ("size_delaunay", "pattern_delaunay", "size_delaunay_split", "size_gp_design") if (RUNS / r).exists()]
    F = {}
    for r in rows:
        f, k = freq(r, ds.n)
        F[r] = f
        tot = f[cert].sum()
        out[r] = dict(campaigns=k, measured_no_claim=float(tot),
                      share_front=float(f[cert & front].sum() / tot), front_share_of_sites=float(front[cert].mean()),
                      share_coarsening=float(f[cert & coarse].sum() / tot), coarsening_share_of_sites=float(coarse[cert].mean()),
                      spearman_front=float(spearmanr(f[cert], v_front[cert]).correlation),
                      spearman_size=float(spearmanr(f[cert], v_size[cert]).correlation))
    if "size_delaunay" in F and "pattern_delaunay" in F:
        a, b = F["size_delaunay"][cert], F["pattern_delaunay"][cert]
        out["overlap_size_pattern"] = float(np.minimum(a, b).sum() / np.maximum(a, b).sum())
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "placement.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))

    # figure: projections onto (T, dopant) and (T, seed), averaging frequency in bins
    r = A.F.recipe(P)
    pairs = [("T", "c", "temperature (°C)", "dopant fraction"), ("T", "s", "temperature (°C)", "rutile seed fraction")]
    show = [x for x in ("size_delaunay", "pattern_delaunay") if x in F]
    fig, axs = plt.subplots(len(show), 2, figsize=(7.2, 3.1 * len(show)), squeeze=False)
    for i, row in enumerate(show):
        for j, (a, b, la, lb) in enumerate(pairs):
            ax = axs[i, j]
            x, y = r[a][cert], r[b][cert]
            H, xe, ye = np.histogram2d(x, y, bins=12, weights=F[row][cert])
            C, _, _ = np.histogram2d(x, y, bins=[xe, ye])
            with np.errstate(invalid="ignore"):
                M = H / C
            im = ax.pcolormesh(xe, ye, M.T, cmap="Blues", vmin=0, vmax=np.nanmax(M))
            # transformation front: rutile fraction 0.5 contour of the truth, binned
            Hf, _, _ = np.histogram2d(x, y, bins=[xe, ye], weights=fR[cert])
            with np.errstate(invalid="ignore"):
                Mf = Hf / C
            xc, yc = 0.5 * (xe[1:] + xe[:-1]), 0.5 * (ye[1:] + ye[:-1])
            ax.contour(xc, yc, Mf.T, levels=[0.1, 0.5, 0.9], colors=INK2, linewidths=0.7, linestyles=["--", "-", "--"])
            ax.set_xlabel(la)
            ax.set_ylabel(lb)
            ax.set_title(f"{'size' if row.startswith('size') else 'pattern'} claim: mean frequency measured (no claim)",
                         fontsize=8, loc="left")
            fig.colorbar(im, ax=ax, shrink=0.85)
    fig.tight_layout()
    fig.savefig(OUT / "placement.png", dpi=200)


if __name__ == "__main__":
    main()
