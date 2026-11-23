"""Replay one GP stopping run of revision2.gpstop (same seed, same random stream) and keep, after each
batch, the per-site wrong-skip probabilities the process states and the true wrong-skip indicators.

    PYTHONPATH=$PWD:$PWD/src python experiments/gpstop_replay.py 29
"""
import sys
import numpy as np
from scipy.stats import norm
from experiments.revision2 import OUT, upper_count  # noqa: F401
from experiments.uncertified_gp import TOL, fit, predict, site_truth


def replay(s, eps=0.20, batch=25, frac=0.8, n_a=100, conf=0.80):
    z, xy, w, p = site_truth()
    lv = np.asarray(z["levels"]); n_cert = int((lv >= 3).sum())
    rng = np.random.default_rng(9000 + s)
    measured = lv <= 2
    out = dict(measured=[], q=[], wrong=[], joint=[])
    jrng = np.random.default_rng(77 + s)
    while True:
        U = np.flatnonzero(~measured)
        gp_, mp, sp = fit(xy[measured], p[measured].astype(float))
        ph, _ = predict(gp_, mp, sp, xy[U], latent=False); ph = np.clip(ph, 0.0, 1.0)
        ok = measured & p & np.isfinite(w)
        gw, mw, sw = fit(xy[ok], np.log(w[ok]))
        lm, ls = predict(gw, mw, sw, xy[U], latent=False)
        wh = np.exp(lm)
        lo, hi = np.log(np.maximum(wh - TOL, 1e-12)), np.log(wh + TOL)
        sd = np.maximum(ls, 1e-12)
        p_in = np.where(ls > 0, norm.cdf((hi - lm) / sd) - norm.cdf((lo - lm) / sd), 1.0)
        line = ph >= 0.5
        q = np.where(line, 1.0 - ph * p_in, ph)
        wrong = np.where(line, (~p[U]) | (np.abs(wh - np.nan_to_num(w[U], nan=1e9)) > TOL), p[U]).astype(bool)
        # the process's joint statement: presence as stated per site, log width drawn jointly from its predictive
        _, cov = gw.predict(xy[U], return_cov=True)
        cov = cov * sw ** 2
        Lc = np.linalg.cholesky(cov + 1e-9 * np.eye(len(U)))
        D = 2000
        lw = lm[None, :] + jrng.standard_normal((D, len(U))) @ Lc.T
        pres = jrng.random((D, len(U))) < ph[None, :]
        bad = np.where(line[None, :], (~pres) | (np.abs(np.exp(lw) - wh[None, :]) > TOL), pres)
        out["joint"].append(bad.sum(1))
        out["measured"].append(int(measured.sum())); out["q"].append(q); out["wrong"].append(wrong)
        for _ in range(200):                       # keep the random stream identical to gpstop
            rng.choice(len(U), size=n_a, replace=False)
        print(int(measured.sum()), round(q.sum() / n_cert, 4), round(wrong.sum() / n_cert, 4), flush=True)
        if q.sum() / n_cert <= eps or len(U) <= batch:
            break
        cand = rng.choice(len(U), size=max(batch, int(frac * len(U))), replace=False)
        take = cand[np.argsort(-q[cand])[:batch]]
        measured[U[take]] = True
    np.savez(OUT / f"gpstop_replay_s{s:02d}.npz", measured=np.array(out["measured"]), n_cert=n_cert,
             q=np.array(out["q"], dtype=object), wrong=np.array(out["wrong"], dtype=object),
             joint=np.array(out["joint"]))


if __name__ == "__main__":
    replay(int(sys.argv[1]))
