"""
Prediction errors behind the hook figure: replays the NaCl (200)-width campaign of average cost
(seed 44) and records, at every design site labelled from the frozen predictor (calibration draw
and remainder of each level), the true and predicted (200) width and line presence.

    python -m experiments.hook_errors
"""
from __future__ import annotations

import numpy as np
from pathlib import Path
from scipy.spatial import cKDTree

from accountable.campaign import run_campaign
from experiments.record import build

ROW, SEED = "nacl_fwhm_nested_watson", 44
OUT = Path("results/hook/errors_s044.npz")


def main():
    ds, cfg, _ = build(ROW, SEED, {})
    pred, crit = cfg.predictor, cfg.criterion
    tree = cKDTree(ds.points)
    n = ds.n
    rec = dict(fwhm_true=np.full(n, np.nan), fwhm_hat=np.full(n, np.nan),
               has_true=np.zeros(n, bool), has_hat=np.zeros(n, bool), score=np.full(n, np.nan),
               labelled=np.zeros(n, bool))
    orig = pred.label

    def label(P_src, I_src, P_query, I_true, desc_true=None):
        out = orig(P_src, I_src, P_query, I_true, desc_true=desc_true)
        if np.asarray(P_query).size:
            I_hat = pred.predict(P_src, I_src, P_query)
            st = crit.stats(I_true, I_hat, desc_true=desc_true)
            _, qi = tree.query(np.atleast_2d(P_query))
            if not rec["labelled"][qi].any():  # first label of a site: the one its decision used
                rec["fwhm_true"][qi], rec["fwhm_hat"][qi] = st["fwhm_true"], st["fwhm_hat"]
                rec["has_true"][qi], rec["has_hat"][qi] = st["has_peak_true"], st["has_peak_hat"]
                rec["score"][qi] = st["score"]
                rec["labelled"][qi] = True
        return out

    pred.label = label
    res = run_campaign(ds, cfg)
    cand = np.flatnonzero(ds.candidate)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, measured=res.measured[cand], skipped=res.skipped[cand],
                        reason=np.array([str(r) for r in res.reason[cand]]), fwhm_eps=crit.fwhm_eps,
                        **{k: v[cand] for k, v in rec.items()})
    print(f"measured {int(res.measured[cand].sum())}, skipped {int(res.skipped[cand].sum())}, wrote {OUT}")


if __name__ == "__main__":
    main()
