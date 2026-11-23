"""Like-for-like on the staged plan (NaCl, (200) width, budget 0.20 per level at confidence 0.80).

One Gaussian process (presence and log width, as in SI 10.3) on the nested design, levels 3 to 6. On each
level the process is fitted to the measured sites and frozen; q is its own probability that skipping a site
is wrong. The sites are ranked by q, and the two rules differ only in who sets the cut:

- own word: skip in order of q while the process's own statement (Poisson-binomial of q over the skipped
  sites) keeps the count of wrong skips at most eps * N_L with probability 0.80; measure the rest.
- contract: measure a uniform draw of 40 sites of the level first; the cut is the largest threshold whose
  calibration failures (sites in the draw below the cut that would be wrong) stay within the exact
  hypergeometric allowance k(N_L, 40, eps, delta = 0.20); skip the sites outside the draw below the cut.

    PYTHONPATH=$PWD:$PWD/src python experiments/staged_gp.py [n_contract_campaigns]
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import hypergeom, norm

from experiments.uncertified_gp import TOL, fit, predict, site_truth

OUT = Path("results/revision2/staged_gp_nacl.json")
import os
EPS, CONF, M = float(os.environ.get("STAGED_EPS", 0.20)), 0.80, 40
SEED_MAX = int(os.environ.get("STAGED_SEED_MAX", 2))      # levels 0..SEED_MAX are measured in full


def poisson_binomial(q):
    pmf = np.zeros(len(q) + 1); pmf[0] = 1.0
    for p in q:
        pmf[1:] = pmf[1:] * (1 - p) + pmf[:-1] * p
        pmf[0] *= (1 - p)
    return pmf


def allowed_k(N, m, eps, delta):
    """Largest k with P(K <= k | W = floor(eps N) + 1) <= delta, and that probability (picked delta)."""
    W = int(np.floor(eps * N)) + 1
    ks = np.arange(0, m + 1); cdf = hypergeom.cdf(ks, N, W, m)
    ok = ks[cdf <= delta]
    return (int(ok.max()), float(cdf[ok.max()])) if len(ok) else (-1, 0.0)


def level_model(xy, w, p, measured, idx):
    gp_, mp, sp = fit(xy[measured], p[measured].astype(float))
    ph, _ = predict(gp_, mp, sp, xy[idx], latent=False); ph = np.clip(ph, 0.0, 1.0)
    ok = measured & p & np.isfinite(w)
    gw, mw, sw = fit(xy[ok], np.log(w[ok]))
    lm, ls = predict(gw, mw, sw, xy[idx], latent=False)
    wh = np.exp(lm)
    lo, hi = np.log(np.maximum(wh - TOL, 1e-12)), np.log(wh + TOL)
    sd = np.maximum(ls, 1e-12)
    p_in = np.where(ls > 0, norm.cdf((hi - lm) / sd) - norm.cdf((lo - lm) / sd), 1.0)
    line = ph >= 0.5
    q = np.where(line, 1.0 - ph * p_in, ph)
    wrong = np.where(line, (~p[idx]) | (np.abs(wh - np.nan_to_num(w[idx], nan=1e9)) > TOL), p[idx]).astype(bool)
    return q, wrong


def own_word(xy, w, p, lv):
    measured = lv <= SEED_MAX; levels = []
    for L in range(SEED_MAX + 1, int(lv.max()) + 1):
        idx = np.flatnonzero(lv == L); N = len(idx)
        q, wrong = level_model(xy, w, p, measured, idx)
        order = np.argsort(q, kind="stable"); n_skip = 0
        for n in range(1, N + 1):
            pmf = poisson_binomial(q[order[:n]])
            if pmf[: int(np.floor(EPS * N)) + 1].sum() >= CONF:
                n_skip = n
            else:
                break
        skip = order[:n_skip]
        pmf = poisson_binomial(q[skip])
        levels.append(dict(L=L, N=N, n_skip=int(n_skip), measured_after=int(measured.sum() + N - n_skip),
                           stated_pmf=pmf.tolist(), realised=int(wrong[skip].sum()),
                           stated_over=float(1.0 - pmf[: int(np.floor(EPS * N)) + 1].sum()),
                           stated_q=int(np.searchsorted(np.cumsum(pmf), CONF)),      # its own bound at CONF
                           skip_idx=idx[skip].tolist(), wrong_idx=idx[skip][wrong[skip]].tolist()))
        sel = np.ones(N, bool); sel[skip] = False
        measured[idx[sel]] = True
    return levels


def own_word_cal(xy, w, p, lv, seed):
    """Like-for-like with the contract: the same frozen process and the same uniform calibration draw, measured by
    default; the process's own statement then decides which of the remaining sites to skip. Calibration labels do
    not enter the decision; they enter the next round's fit, as in the contract."""
    rng = np.random.default_rng(5000 + seed)                  # same calibration draws as contract(seed)
    measured = lv <= SEED_MAX; levels = []
    for L in range(SEED_MAX + 1, int(lv.max()) + 1):
        idx = np.flatnonzero(lv == L); N = len(idx)
        q, wrong = level_model(xy, w, p, measured, idx)      # fitted and frozen before the draw
        cal = rng.choice(N, size=min(M, N), replace=False)
        rest = np.setdiff1d(np.arange(N), cal)
        order = rest[np.argsort(q[rest], kind="stable")]; n_skip = 0; cap = int(np.floor(EPS * N))
        for n in range(1, len(order) + 1):
            if poisson_binomial(q[order[:n]])[: cap + 1].sum() >= CONF:
                n_skip = n
            else:
                break
        skip = order[:n_skip]
        pmf = poisson_binomial(q[skip])
        levels.append(dict(L=L, N=N, m=len(cal), n_skip=int(n_skip), measured_after=int(measured.sum() + N - n_skip),
                           realised=int(wrong[skip].sum()),
                           stated_over=float(1.0 - pmf[: cap + 1].sum()),
                           stated_q=int(np.searchsorted(np.cumsum(pmf), CONF)),
                           skip_idx=idx[skip].tolist(), wrong_idx=idx[skip][wrong[skip]].tolist()))
        sel = np.ones(N, bool); sel[skip] = False
        measured[idx[sel]] = True
    return levels


def contract(xy, w, p, lv, seed):
    rng = np.random.default_rng(5000 + seed)
    measured = lv <= SEED_MAX; levels = []
    for L in range(SEED_MAX + 1, int(lv.max()) + 1):
        idx = np.flatnonzero(lv == L); N = len(idx)
        q, wrong = level_model(xy, w, p, measured, idx)      # fitted and frozen before the draw
        cal = rng.choice(N, size=min(M, N), replace=False)
        k_ok, d_pick = allowed_k(N, len(cal), EPS, 1 - CONF)
        ts = np.concatenate([[-np.inf], np.sort(np.unique(q))])
        t_best = -np.inf
        for t in ts:                                          # largest threshold within the allowance
            if ((q[cal] <= t) & wrong[cal]).sum() <= k_ok:
                t_best = t
            else:
                break
        k_cal = int(((q[cal] <= t_best) & wrong[cal]).sum())
        rest = np.setdiff1d(np.arange(N), cal)
        skip = rest[q[rest] <= t_best]
        levels.append(dict(L=L, N=N, m=len(cal), k_allowed=k_ok, delta_picked=d_pick, k_cal=k_cal,
                           n_skip=int(len(skip)), measured_after=int(measured.sum() + N - len(skip)),
                           realised=int(wrong[skip].sum()), W_level=int(((q <= t_best) & wrong).sum()),
                           skip_idx=idx[skip].tolist(), wrong_idx=idx[skip][wrong[skip]].tolist()))
        sel = np.ones(N, bool); sel[skip] = False
        measured[idx[sel]] = True
    return levels


def main(n=50):
    z, xy, w, p = site_truth()
    lv = np.asarray(z["levels"])
    res = dict(own=own_word(xy, w, p, lv))
    o = res["own"]
    print("own word:", o[-1]["measured_after"], [(l["n_skip"], l["realised"], int(np.floor(EPS * l["N"]))) for l in o], flush=True)
    res["contract"] = []
    for s in range(n):
        c = contract(xy, w, p, lv, s); res["contract"].append(c)
        print("contract", s, c[-1]["measured_after"], [(l["n_skip"], l["realised"], l["W_level"], int(np.floor(EPS * l["N"]))) for l in c], flush=True)
    OUT.write_text(json.dumps(res))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 50)
