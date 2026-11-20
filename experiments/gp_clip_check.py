"""
How often does clipping GP predictions at zero change a claim label?

For each dataset and GP length-scale rule, every site of each certified level is predicted from all
sites of the coarser levels (the measured set of a campaign that skipped nothing), and its
interpolation label is computed from the raw and from the clipped prediction.

    python -m experiments.gp_clip_check
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from accountable.gp import gp_protocol
from experiments.ir_bioreef import adapter as IR
from experiments.nacl_saxs import adapter as NA
from experiments.synthetic_saxs import adapter as SA


def cases():
    ds = IR.load()
    yield "IR", ds, IR.criterion(), 3
    yield "IR tight", ds, __import__("accountable").AccuracyCriterion(kind="envelope", rtol=0.10, atol=0.01,
                                                                          signal_min=0.005), 3
    ds, _ = NA.load()
    yield "NaCl width", ds, NA.criterion("fwhm", ds.axis, NA.noise_sigma(ds)), 3
    ds = SA.load()
    yield "Synthetic peak", ds, SA.criterion("peak", ds.axis), 3


def main():
    out = {}
    for name, ds, crit, L0 in cases():
        lv = np.asarray(ds.levels)
        cand = np.asarray(ds.candidate, bool) if ds.candidate is not None else np.ones(len(lv), bool)
        for mode in ("mle", "design", "nonstationary"):
            pred, _ = gp_protocol(ds, crit, mode)
            n = flips = neg = fail0 = fail1 = 0
            for L in range(L0, lv.max() + 1):
                src, qry = np.flatnonzero(cand & (lv < L)), np.flatnonzero(cand & (lv == L))
                P = np.asarray(ds.points, float)
                I_src, I_true = ds.oracle.truth(src), ds.oracle.truth(qry)
                I_hat = pred.predict(P[src], I_src, P[qry])
                a = np.asarray(crit.stats(I_true, I_hat)["outside_mean"], bool)
                b = np.asarray(crit.stats(I_true, np.maximum(I_hat, 0.0))["outside_mean"], bool)
                n += len(qry)
                flips += int((a != b).sum())
                fail0 += int(a.sum())
                fail1 += int(b.sum())
                neg += int((I_hat < 0).any(axis=1).sum())
            out[f"{name} | {mode}"] = dict(sites=n, any_negative=neg, fails_raw=fail0, fails_clipped=fail1, flips=flips)
            print(f"{name:15s} {mode:14s} sites {n:5d}  negative predictions {neg:5d}  "
                  f"fails raw {fail0:5d} clipped {fail1:5d}  labels flipped {flips}", flush=True)
    Path("results/gp_clip_check.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
