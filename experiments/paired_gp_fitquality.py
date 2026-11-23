"""Does the set measured under the contract give a better map than the set measured under the process's own
statement, once both are interpolated by the same well-chosen model?

Per design and per steering kernel, both campaigns (driven by the own statement, driven by the contract) are replayed
to the end of round 3. Every measured set, and a size-matched control (the seed plus a uniform random draw of the other
design sites), is interpolated by one Matern (nu = 1/2) Gaussian process: a classifier for presence and a regression
with fitted noise for log width. Error is the share of raster sites with presence wrong or width off by more than the
tolerance, over the whole raster and over raster sites outside the design.

    PYTHONPATH=$PWD:$PWD/src python experiments/paired_gp_fitquality.py KERNEL START N
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("BESTFIT_NU", "0.5")
import numpy as np

import experiments.paired_gp_bestfit as B
from experiments.paired_gp import SEED_MAX
from experiments.paired_gp_maps import replay
from experiments.staged_gp_designs import make_design
from experiments.uncertified_gp import TOL

OUT = Path("results/revision2/paired_gp_fitquality.jsonl")


def score(xy, w, p, meas, xy_all, w_all, p_all, off_design):
    ph, _ = B.best_presence(xy[meas], p[meas], xy_all)
    ok = meas & p & np.isfinite(w)
    wh, _ = B.best_width(xy[ok], np.log(w[ok]), xy_all)
    line = ph >= 0.5
    pe = line != p_all
    we = line & p_all & (np.abs(wh - np.nan_to_num(w_all, nan=1e9)) > TOL)
    e = pe | we
    return dict(n=int(meas.sum()), all=float(e.mean()), off=float(e[off_design].mean()),
                presence=float(pe.mean()), width=float(we.mean()))


def main(kernel, start, n):
    sys.path.insert(0, "manuscript/figures")
    from fig_datasets import nacl_fwhm
    from experiments.nacl_saxs.adapter import load
    _, grid = load()
    xy_all = np.asarray(grid["xy_mm"], float)
    img, pres, (xs, ys), _, _ = nacl_fwhm()
    ix = np.searchsorted(xs, xy_all[:, 0].round(4).clip(xs[0], xs[-1]))
    iy = np.searchsorted(ys, xy_all[:, 1].round(4).clip(ys[0], ys[-1]))
    w_all, p_all = img[iy, ix], pres[iy, ix]
    done = set()
    if OUT.exists():
        done = {(r["kernel"], r["design"]) for r in map(json.loads, OUT.read_text().splitlines())}
    for d in range(start, start + n):
        if (kernel, d) in done:
            continue
        idx, lv = make_design(1000 + d, xy_all)
        xy, w, p = xy_all[idx], w_all[idx], p_all[idx]
        off_design = np.ones(len(xy_all), bool); off_design[idx] = False
        rng = np.random.default_rng(7700 + d)
        rec = dict(kernel=kernel, design=d)
        for driver in ("uq", "contract"):
            meas, sk, wr = replay(xy, w, p, lv, d, kernel, driver)
            rec[driver] = score(xy, w, p, meas, xy_all, w_all, p_all, off_design)
            rec[driver]["wrong_skips"] = int(wr.sum())
            ctrl = lv <= SEED_MAX
            rest = np.flatnonzero(~ctrl)
            ctrl[rng.choice(rest, size=int(meas.sum() - ctrl.sum()), replace=False)] = True
            rec[f"{driver}_random"] = score(xy, w, p, ctrl, xy_all, w_all, p_all, off_design)
        with OUT.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        print(kernel, d, {k: (v["n"], round(v["all"], 3), round(v["off"], 3)) for k, v in rec.items()
                          if isinstance(v, dict)}, flush=True)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
