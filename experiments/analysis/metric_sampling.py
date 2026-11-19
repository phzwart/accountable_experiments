"""
Where does each metric send the measurements? Per-site frequencies over 50 campaigns of being
measured (outside seed and calibration), of failing the prediction, and of being a wrong skip,
for the peak / line-width metric against the whole-profile metric, at default and matched
tolerances. Interpolation certificate only, quantile path, natural neighbour.

    python -m experiments.analysis.metric_sampling 50
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from accountable import SpectrumRoute, make_policy, run_campaign
from accountable.campaign import INTERP
from experiments.analysis.metric_study import BUDGET, setup

OUTD = Path("results/analysis/metric_sampling")
PAIRS = {
    "synthetic_saxs": ["default | peak, absolute (Δq 0.005, ΔFWHM 0.001 Å⁻¹)", "default | profile, 0.01 + 1 %",
                       "matched | peak, absolute", "matched | profile, absolute + relative"],
    "nacl_saxs": ["default | (200) FWHM, absolute (0.02 nm⁻¹)", "default | profile, 0.01 + 1 %",
                  "matched | (200) FWHM, absolute", "matched | profile, absolute + relative"],
}


def one(args):
    exp, metric, seed = args
    A, ds, crits = setup(exp)
    eps, conf = BUDGET[exp]
    cfg = A.config(ds, target="envelope", mode="interp", policy="nested_path", eps=eps, confidence=conf,
                   seed=seed, nn_method="watson")
    images = getattr(cfg.predictor, "images", None)
    cfg.criterion = crits[metric]
    cfg.predictor = SpectrumRoute(crits[metric], images=images, nn_method="watson")
    cfg.final_labels = False
    cfg.post_labels = False
    res = run_campaign(ds, cfg)
    reason = np.asarray(res.reason).astype(str)
    fail = np.asarray(res.fail_prior, bool)
    sk = np.asarray(res.skipped, bool)
    return (exp, metric, seed, (reason == "no_certificate"), np.asarray(res.is_cal, bool), fail,
            sk & (reason == "interpolable") & fail)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    OUTD.mkdir(parents=True, exist_ok=True)
    jobs = [(e, m, s) for e, ms in PAIRS.items() for m in ms for s in range(n)]
    for e in PAIRS:
        setup(e)
    with Pool(2) as pool:
        rows = list(pool.imap_unordered(one, jobs, chunksize=4))
    for e, ms in PAIRS.items():
        out = {}
        for k, m in enumerate(ms):
            rs = [r for r in rows if r[0] == e and r[1] == m]
            out[f"meas_{k}"] = np.mean([r[3] for r in rs], 0)
            out[f"cal_{k}"] = np.mean([r[4] for r in rs], 0)
            out[f"fail_{k}"] = np.mean([r[5] for r in rs], 0)
            out[f"wrong_{k}"] = np.mean([r[6] for r in rs], 0)
        np.savez_compressed(OUTD / f"{e}.npz", metrics=np.array(ms), **out)
    print("done", len(rows))
