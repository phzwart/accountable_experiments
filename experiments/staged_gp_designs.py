"""Frequency test of the staged like-for-like (experiments/staged_gp.py) over fresh hierarchical designs.
Each design: hierarchical Poisson-disk sampling on the unit square, radii 0.2 / sqrt(2)^l (l = 0..6), corners
forced, snapped to the NaCl raster as in the adapter. On each design, the own-word rule once and the contract
with one calibration seed. Output: per design and level, skipped, realised wrong skips, W_level, budget.

    PYTHONPATH=$PWD:$PWD/src python experiments/staged_gp_designs.py START N
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

import os
from experiments.staged_gp import EPS, SEED_MAX, contract, own_word, own_word_cal
OWN_CAL = os.environ.get("STAGED_OWN_CAL") == "1"
from experiments.uncertified_gp import site_truth

OUT = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("results/revision2/staged_gp_designs.jsonl")


def make_design(seed, xy_mm):
    from hiposa import PoissonDiskSamplerWithExisting
    rng = np.random.default_rng(seed); np.random.seed(int(rng.integers(0, 2 ** 31 - 1)))
    pts = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]); lab = np.zeros(4, np.int32)
    for lev, r in enumerate(0.2 / np.sqrt(2.0) ** np.arange(7)):
        s = PoissonDiskSamplerWithExisting(domain=[(0.0, 1.0), (0.0, 1.0)], r=float(r), existing_points=pts,
                                           existing_labels=lab, symmetry_operators=None, wrap=False)
        new, l = s.sample(new_label=int(lev), return_new_only=True)
        if len(new):
            pts = np.vstack([pts, new]); lab = np.concatenate([lab, l])
    lo = xy_mm.min(0); span = np.maximum(xy_mm.max(0) - lo, 1e-9)
    dist, nn = cKDTree((xy_mm - lo) / span).query(pts)
    best = {}
    for i, g in enumerate(nn):
        cand = (int(lab[i]), float(dist[i]), i)
        if int(g) not in best or cand < best[int(g)]:
            best[int(g)] = cand
    order = sorted(best, key=lambda g: (best[g][0], g))
    return np.asarray(order, int), np.asarray([best[g][0] for g in order], int)


def main(start, n):
    import sys as _s
    _s.path.insert(0, "manuscript/figures")
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
        done = {json.loads(l)["design"] for l in OUT.read_text().splitlines()}
    for d in range(start, start + n):
        if d in done:
            continue
        idx, lv = make_design(1000 + d, xy_all)
        xy, w, p = xy_all[idx], w_all[idx], p_all[idx]
        own = own_word_cal(xy, w, p, lv, d) if OWN_CAL else own_word(xy, w, p, lv)
        con = contract(xy, w, p, lv, d)
        for o in own:
            o.pop("stated_pmf", None)
        for lvl in own + con:                      # design indices -> raster indices
            lvl["skip_idx"] = idx[lvl["skip_idx"]].tolist(); lvl["wrong_idx"] = idx[lvl["wrong_idx"]].tolist()
        row = dict(design=d, n=int(len(idx)), decided=idx[lv > SEED_MAX].tolist(), own=own, contract=con)
        with OUT.open("a") as f:
            f.write(json.dumps(row) + "\n")
        print(d, len(idx), "own", own[-1]["measured_after"], [(o["realised"], int(EPS * o["N"])) for o in own],
              "contract", con[-1]["measured_after"], [(c["W_level"], int(EPS * c["N"])) for c in con], flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
