"""
Where and why the synthetic map collects wrong skips (quantile path, natural neighbour).

Per design site: true peak descriptors and phase; frequency over the 250 recorded campaigns of
being skipped as not of interest, skipped as predictable, and of each kind of wrong skip.
At decision time (reconstructed from the record for a set of campaigns): the spectrum predicted
from the sites measured on coarser levels, its peak descriptors, and the logistic interest score.

    python -m experiments.analysis.syn_clumps
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from accountable import peak_descriptors
from accountable.sibson import interpolate
from experiments.record import OUT as REC, REASONS, build

ROW = "syn_peak_2cert_nested_watson"
OUTD = Path("results/analysis/syn_clumps")


def main(n_recon=20):
    OUTD.mkdir(parents=True, exist_ok=True)
    ds, cfg, _ = build(ROW, 0, {})
    z = np.load(REC / ROW / "sites.npz")
    site = z["site_index"]
    q = ds.axis
    I_all = ds.oracle.truth(np.arange(len(ds.points)))
    P = np.asarray(ds.points, float)
    d = peak_descriptors(I_all[site], q)
    phase = np.asarray(ds.meta["phase"])[site]
    R = np.array(REASONS)[z["reason"]]
    sk = z["skipped"].astype(bool)
    I = z["interesting"].astype(bool)
    F = z["fail_prior"].astype(bool)
    a = np.isin(R, ["not_interesting", "not_interesting+interpolable"])
    b = np.isin(R, ["interpolable", "not_interesting+interpolable"])
    w_int = sk & a & I
    w_itp = sk & b & F & ~(a & I)
    lev = z["levels"]
    out = dict(
        site=site.tolist(), x=P[site, 0].tolist(), y=P[site, 1].tolist(), level=lev.tolist(),
        phase=phase.tolist(), interesting_true=I[0].tolist(),
        prominence=np.nan_to_num(d["prominence"], nan=-1).tolist(), q_peak=np.nan_to_num(d["q_peak"], nan=-1).tolist(),
        fwhm=np.nan_to_num(d["fwhm"], nan=-1).tolist(), hab=np.nan_to_num(d["height_above_base"], nan=-1).tolist(),
        f_skip_int=(sk & a).mean(0).tolist(), f_wrong_int=w_int.mean(0).tolist(),
        f_skip_itp=(sk & b).mean(0).tolist(), f_wrong_itp=w_itp.mean(0).tolist(),
        f_fail_prior=F.mean(0).tolist(),
    )
    # Reconstruct decision-time predictions for the first campaigns.
    seeds = z["seeds"][:n_recon]
    pred_prom, pred_q, pred_fwhm, score_int, wrong_int = [], [], [], [], []
    for s_i in range(len(seeds)):
        meas = z["measured"][s_i].astype(bool)
        for L in np.unique(lev):
            idx = np.flatnonzero(lev == L)
            src = meas & (lev < L)
            if src.sum() < 3:
                continue
            Ihat = interpolate(P[site[src]], I_all[site[src]], P[site[idx]], images=ds.images, method="watson")
            dd = peak_descriptors(Ihat, q)
            pred_prom.append(np.nan_to_num(dd["prominence"], nan=-1)[:, None])
            pred_q.append(np.nan_to_num(dd["q_peak"], nan=-1)[:, None])
            pred_fwhm.append(np.nan_to_num(dd["fwhm"], nan=-1)[:, None])
            score_int.append(z["score_interest"][s_i, idx][:, None])
            wrong_int.append(np.column_stack([np.full(len(idx), s_i), idx, w_int[s_i, idx], (sk & a)[s_i, idx],
                                              I[s_i, idx]]))
    rec = np.column_stack([np.vstack(wrong_int), np.vstack(pred_prom), np.vstack(pred_q),
                           np.vstack(pred_fwhm), np.vstack(score_int)])
    np.savez_compressed(OUTD / "decision_time.npz", rec=rec,
                        cols=np.array(["seed_i", "site_i", "wrong_int", "skipped_int", "interesting",
                                       "pred_prom", "pred_q", "pred_fwhm", "score_interest"]))
    (OUTD / "sites.json").write_text(json.dumps(out))
    np.savez_compressed(OUTD / "spectra.npz", q=q, I=I_all[site])


if __name__ == "__main__":
    main()
