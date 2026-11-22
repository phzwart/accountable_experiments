"""
Per-site record of a campaign, measured sites included: for one campaign of average cost per dataset, the
campaign is replayed and every design site gets its decision-time entries (level, action, score and certified
cut per claim, margin above the cut, rank of the score within its level, frozen prediction label) and its
outcome (residual of the frozen prediction in units of the tolerance, failure label, interest label, and the
conformal p-value of the residual among the calibration residuals of the same level).

    python -m experiments.measurement_record

Writes results/measurement_record/<row>.npz and <row>.csv.
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from accountable.campaign import run_campaign
from experiments.record import OUT as REC, REASONS, build

ROWS = {"nacl_fwhm_nested_watson": "NaCl (200) width",
        "ir_nested_watson": "IR amide I",
        "syn_env_nested_watson": "synthetic SAXS profile"}
OUT = Path("results/measurement_record")
SEED_OVERRIDE = {"nacl_fwhm_nested_watson": 44}  # the campaign of Fig. 1


def wrong_matrix(z):
    S = z["skipped"].astype(bool)
    R = np.array(REASONS)[z["reason"]]
    A = np.isin(R, ["not_interesting", "not_interesting+interpolable"])
    B = np.isin(R, ["interpolable", "not_interesting+interpolable"])
    return S & ((A & z["interesting"].astype(bool)) | (B & z["fail_prior"].astype(bool)))


def average_seed(z):
    """Campaign of average cost: measured count closest to the mean, then wrong skips closest to the median."""
    m = z["measured"].sum(1)
    w = wrong_matrix(z).sum(1)
    d = np.abs(m - m.mean())
    cand = np.flatnonzero(d == d.min())
    return int(z["seeds"][cand[np.argmin(np.abs(w[cand] - np.median(w)))]])


def conformal_p(r, lv, is_cal, seed):
    """Randomised conformal p-value of each residual among the calibration residuals of its level:
    (#{cal > r} + U (#{cal = r} + 1)) / (n_cal + 1), U uniform; ties (agreed absence, r = 0) are broken at
    random, so the p-values of exchangeable residuals are uniform."""
    rng = np.random.default_rng(seed)
    p = np.full(len(r), np.nan)
    for L in np.unique(lv):
        cm = (lv == L) & is_cal
        if cm.sum() == 0:
            continue
        rc = r[cm]
        m = np.flatnonzero(lv == L)
        gt = (rc[None, :] > r[m][:, None]).sum(1)
        eq = (rc[None, :] == r[m][:, None]).sum(1)
        p[m] = (gt + rng.uniform(size=len(m)) * (eq + 1)) / (len(rc) + 1)
    return p


def repvalue():
    """Recompute the p-values of saved records without replaying the campaigns."""
    for row in ROWS:
        f = OUT / f"{row}.npz"
        d = dict(np.load(f))
        d["p_resid"] = conformal_p(d["residual"], d["level"], d["is_cal"], int(d["seed"]))
        np.savez_compressed(f, **d)


def replay(row, seed):
    ds, cfg, _ = build(row, seed, {})
    pred, crit = cfg.predictor, cfg.criterion
    tree = cKDTree(np.asarray(ds.points, float))
    resid = np.full(ds.n, np.nan)
    seen = np.zeros(ds.n, bool)
    orig = pred.label

    def label(P_src, I_src, P_query, I_true, desc_true=None):
        out = orig(P_src, I_src, P_query, I_true, desc_true=desc_true)
        if np.asarray(P_query).size:
            I_hat = pred.predict(P_src, I_src, P_query)
            st = crit.stats(I_true, I_hat, desc_true=desc_true)
            _, qi = tree.query(np.atleast_2d(P_query))
            new = ~seen[qi]  # first label of a site: the one its decision used
            resid[qi[new]] = np.asarray(st["score"], float)[new]
            seen[qi[new]] = True
        return out

    pred.label = label
    res = run_campaign(ds, cfg)
    cand = np.flatnonzero(ds.candidate)
    return res, resid, cand


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    import sys
    if "--repvalue" in sys.argv:
        return repvalue()
    only = sys.argv[1:]
    for row, name in ROWS.items():
        if only and row not in only:
            continue
        z = np.load(REC / row / "sites.npz")
        seed = SEED_OVERRIDE.get(row, average_seed(z))
        i = int(np.flatnonzero(z["seeds"] == seed)[0])
        res, resid, cand = replay(row, seed)
        lv = np.asarray(z["levels"])
        reason = np.array([str(r) for r in res.reason[cand]])
        assert (reason == np.array(REASONS)[z["reason"][i]]).all(), "replay differs from the record"
        assert int(res.measured[cand].sum()) == int(z["measured"][i].sum())
        r = resid[cand]
        # residual undefined where presence of the feature decides: agreed absence counts as 0, disagreement as inf
        r = np.where(np.isnan(r), np.where(res.fail_prior[cand], np.inf, 0.0), r)
        names = sorted(res.scores)
        rec = dict(level=lv, reason=reason, measured=res.measured[cand], skipped=res.skipped[cand],
                   is_cal=res.is_cal[cand], residual=r, fail=res.fail_prior[cand],
                   interesting=res.interesting[cand])
        for nm in names:
            s, t = res.scores[nm][cand], res.thresholds[nm][cand]
            rank = np.full(len(s), np.nan)
            for L in np.unique(lv):
                m = (lv == L) & np.isfinite(s)
                if m.any():
                    rank[m] = (np.argsort(np.argsort(s[m])) + 1) / m.sum()
            rec[f"score_{nm}"], rec[f"tau_{nm}"], rec[f"margin_{nm}"], rec[f"rank_{nm}"] = s, t, s - t, rank
        p = conformal_p(r, lv, rec["is_cal"], seed)
        rec["p_resid"] = p
        np.savez_compressed(OUT / f"{row}.npz", seed=seed, names=np.array(names), **rec)
        with open(OUT / f"{row}.csv", "w", newline="") as f:
            keys = [k for k in rec]
            wr = csv.writer(f)
            wr.writerow(["site"] + keys)
            for j in range(len(r)):
                wr.writerow([j] + [rec[k][j] if not isinstance(rec[k][j], (float, np.floating)) else
                                   f"{rec[k][j]:.4g}" for k in keys])
        print(f"{name}: seed {seed}, measured {int(rec['measured'].sum())}, claims {names}")


if __name__ == "__main__":
    main()
