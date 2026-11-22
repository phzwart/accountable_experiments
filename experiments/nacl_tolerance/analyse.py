"""NaCl (200) width: per-site estimator precision and site-to-site variation on the full raster.

    PYTHONPATH=$PWD:$PWD/src python experiments/nacl_tolerance/analyse.py
"""
import json
import numpy as np
from scipy.spatial import cKDTree
from accountable import peak_descriptors, estimate_window_noise
from experiments.nacl_saxs.adapter import load, Q200, Q200_HALF, PRESENCE_C
from experiments._paths import data_root

ds, grid = load()
I = np.asarray(grid["intensity"], float); q = np.asarray(grid["q"], float); xy = np.asarray(grid["xy_mm"], float)
sigma = float(estimate_window_noise(ds.oracle.truth(np.arange(ds.n)), q, Q200, Q200_HALF)["sigma"])

def desc(P):
    d = peak_descriptors(P, q, q_center=Q200, q_halfwidth=Q200_HALF)
    hab = np.asarray(d["height_above_base"], float)
    pres = np.asarray(d["has_peak"], bool) & np.isfinite(hab) & (hab > PRESENCE_C * sigma)
    return np.asarray(d["fwhm"], float), np.asarray(d["q_peak"] if "q_peak" in d else d["position"], float), hab, pres

w, pos, hab, pres = desc(I)
rng = np.random.default_rng(0); R = 40
W = np.empty((R, len(I)))
for r in range(R):
    W[r], *_ = desc(I + rng.normal(0, sigma, I.shape))
sd = np.nanstd(W, 0)
# twin-copy check, as in SI 2: two noisy copies, fraction differing by more than t
def twin_fail(t):
    a = W[0::2]; b = W[1::2]
    return float(np.nanmean(np.abs(a - b)[:, pres] > t))

tree = cKDTree(xy); step = 0.25
out = dict(sigma=sigma, n_raster=len(I), present=float(pres.mean()),
           width_quantiles=dict(zip(["p05", "p25", "p50", "p75", "p95"], np.nanpercentile(w[pres], [5, 25, 50, 75, 95]).round(4).tolist())),
           position_quantiles=dict(zip(["p05", "p50", "p95"], np.nanpercentile(pos[pres], [5, 50, 95]).round(4).tolist())),
           bin_width=float(np.median(np.diff(q))),
           est_sd_quantiles=dict(zip(["p25", "p50", "p75", "p90"], np.nanpercentile(sd[pres], [25, 50, 75, 90]).round(4).tolist())),
           twin_fail={str(t): twin_fail(t) for t in (0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08)})
vg = {}
for k in (1, 2, 3, 4, 6):
    pairs = tree.query_pairs(k * step * 1.05, output_type="ndarray")
    d = np.linalg.norm(xy[pairs[:, 0]] - xy[pairs[:, 1]], axis=1)
    pairs = pairs[d > (k - 1) * step * 1.05]
    ok = pres[pairs[:, 0]] & pres[pairs[:, 1]]
    dw = np.abs(w[pairs[ok, 0]] - w[pairs[ok, 1]])
    vg[k] = dict(n=int(ok.sum()), median=float(np.nanmedian(dw)), p75=float(np.nanpercentile(dw, 75)),
                 frac_gt={str(t): float(np.nanmean(dw > t)) for t in (0.02, 0.03, 0.04, 0.05, 0.06, 0.08)})
out["neighbour_abs_dw_by_raster_steps"] = vg
# design spacing: level-6 sites to their nearest coarser design site
pts_mm = ds.meta["xy_mm"]; lv = ds.levels
fine = lv == lv.max(); coarse = ~fine
dd, _ = cKDTree(pts_mm[coarse]).query(pts_mm[fine])
out["design_finest_nn_mm"] = dict(median=float(np.median(dd)), p90=float(np.percentile(dd, 90)))
json.dump(out, open("experiments/nacl_tolerance/analysis.json", "w"), indent=1)
np.savez("experiments/nacl_tolerance/widths.npz", w=w, pos=pos, hab=hab, pres=pres, sd=sd, xy=xy)
print(json.dumps(out, indent=1))
