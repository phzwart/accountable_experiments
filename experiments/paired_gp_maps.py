"""Interpolated maps after the last round of one paired design, for each kernel and each driving cut.

The campaign of experiments/paired_gp.py is replayed for one design; after round 3 the process (presence and log
width, same kernel) is refitted on everything measured and its posterior mean is drawn over the full raster.
Skipped design sites and the wrong skips among them are stored for overlay.

    PYTHONPATH=$PWD:$PWD/src python experiments/paired_gp_maps.py DESIGN
"""
import sys
from pathlib import Path

import numpy as np

from experiments.paired_gp import (EPS, M, SEED_MAX, cuts, fit, round_state)
from experiments.staged_gp_designs import make_design
from experiments.uncertified_gp import TOL

OUT = Path("results/revision2")


def replay(xy, w, p, lv, design, kernel, driver):
    rng_cal = np.random.default_rng(5000 + design); rng = np.random.default_rng(9100 + design)
    measured = lv <= SEED_MAX
    skipped, wrong = np.zeros(len(lv), bool), np.zeros(len(lv), bool)
    for L in range(SEED_MAX + 1, int(lv.max()) + 1):
        idx = np.flatnonzero(lv == L); N = len(idx)
        st = round_state(xy, w, p, measured, idx, kernel, rng)
        cal = rng_cal.choice(N, size=min(M, N), replace=False)
        rest = np.setdiff1d(np.arange(N), cal)
        c = cuts(st, N, cal, rest, rng)
        sk = c[driver]["skip"]
        skipped[idx[sk]] = True; wrong[idx[sk]] = st["wrong"][sk]
        sel = np.ones(N, bool); sel[sk] = False
        measured[idx[sel]] = True
    return measured, skipped, wrong


def interpolate(xy, w, p, measured, kernel, xy_full):
    gp_, mp, sp = fit(xy[measured], p[measured].astype(float), kernel)
    ph = np.clip(gp_.predict(xy_full) * sp + mp, 0.0, 1.0)
    ok = measured & p & np.isfinite(w)
    gw, mw, sw = fit(xy[ok], np.log(w[ok]), kernel)
    wh = np.exp(gw.predict(xy_full) * sw + mw)
    return ph, wh


def main(design):
    sys.path.insert(0, "manuscript/figures")
    from fig_datasets import nacl_fwhm
    from experiments.nacl_saxs.adapter import load
    _, grid = load()
    xy_all = np.asarray(grid["xy_mm"], float)
    img, pres, (xs, ys), _, _ = nacl_fwhm()
    ix = np.searchsorted(xs, xy_all[:, 0].round(4).clip(xs[0], xs[-1]))
    iy = np.searchsorted(ys, xy_all[:, 1].round(4).clip(ys[0], ys[-1]))
    w_all, p_all = img[iy, ix], pres[iy, ix]
    idx, lv = make_design(1000 + design, xy_all)
    xy, w, p = xy_all[idx], w_all[idx], p_all[idx]
    res = dict(design=design, raster_idx=idx, lv=lv, ix=ix, iy=iy, shape=np.array(img.shape))
    for kernel in ("fitted", "nugget", "smooth"):
        for driver in ("uq", "contract"):
            meas, sk, wr = replay(xy, w, p, lv, design, kernel, driver)
            ph, wh = interpolate(xy, w, p, meas, kernel, xy_all)
            tag = f"{kernel}_{driver}"
            res[f"{tag}_measured"], res[f"{tag}_skipped"], res[f"{tag}_wrong"] = meas, sk, wr
            res[f"{tag}_ph"], res[f"{tag}_wh"] = ph, wh
            gt_wrong = np.where(ph >= 0.5, (~p_all) | (np.abs(wh - np.nan_to_num(w_all, nan=1e9)) > TOL), p_all)
            print(tag, "measured", int(meas.sum()), "skipped", int(sk.sum()), "wrong skips", int(wr.sum()),
                  "raster share wrong", round(float(gt_wrong.mean()), 3), flush=True)
    np.savez_compressed(OUT / f"paired_gp_maps_d{design}.npz", **res)


if __name__ == "__main__":
    main(int(sys.argv[1]))
