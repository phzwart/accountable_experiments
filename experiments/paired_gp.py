"""Paired comparison of the two cuts on identical states (NaCl, (200) width, three rounds, budget 0.20 per round at
confidence 0.80), for two kernels of the same Gaussian process.

Per round: the process (presence and log width) is fitted on everything measured so far and frozen; a uniform
calibration draw of 40 sites is measured. On the leftover sites, ranked by the process's probability of a wrong skip,
both cuts are computed on the identical state, with the same target (wrong skips among leftover sites at most
floor(EPS N) with probability at least CONF):
  uq:       the process's own statement, from joint posterior draws (presence per site as stated, log width drawn
            jointly over the leftover sites);
  iid:      site by site: skip every site whose probability of a wrong skip is at most alpha, with alpha the largest
            value for which the Poisson-binomial count of wrong skips (the process's probabilities taken as
            independent) stays within the target with probability CONF;
  contract: the exact hypergeometric upper limit from the calibration labels, less the failures already seen.
One of the two cuts drives the trajectory (which sites are measured and enter the next fit); both are recorded.

Kernels: 'fitted' (white-noise level fitted by marginal likelihood, as elsewhere in the paper) and 'nugget'
(white noise fixed at 1e-4 of the standardised variance: a common interpolating choice).

    PYTHONPATH=$PWD:$PWD/src python experiments/paired_gp.py KERNEL DRIVER START N
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import hypergeom, norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C, WhiteKernel

from experiments.staged_gp_designs import make_design
from experiments.uncertified_gp import TOL

EPS, CONF, M, SEED_MAX, D = 0.20, 0.80, 40, 3, 2000
OUT = Path("results/revision2/paired_gp.jsonl")


def fit(X, y, kernel):
    wk = WhiteKernel(0.1, (1e-4, 10.0)) if kernel == "fitted" else WhiteKernel(1e-4, "fixed")
    ls_lo = 1.0 if kernel == "smooth" else 0.05            # 'smooth': length scale held at or above 1 mm, nugget fixed
    k = C(1.0) * RBF(max(1.0, ls_lo), (ls_lo, 20.0)) + wk
    mu, sd = y.mean(), y.std()
    g = GaussianProcessRegressor(k, alpha=1e-8, n_restarts_optimizer=2, random_state=0).fit(X, (y - mu) / sd)
    return g, mu, sd


def upper_count(N, m, k):
    W = np.arange(k, N + 1)
    return int(W[hypergeom.cdf(k, N, W, m) > 1 - CONF].max())


def round_state(xy, w, p, measured, idx, kernel, rng):
    gp_, mp, sp = fit(xy[measured], p[measured].astype(float), kernel)
    ph = np.clip(gp_.predict(xy[idx]) * sp + mp, 0.0, 1.0)
    ok = measured & p & np.isfinite(w)
    gw, mw, sw = fit(xy[ok], np.log(w[ok]), kernel)
    lm, cov = gw.predict(xy[idx], return_cov=True)
    lm = lm * sw + mw; cov = cov * sw ** 2
    ls = np.sqrt(np.clip(np.diag(cov), 1e-24, None))
    wh = np.exp(lm)
    lo, hi = np.log(np.maximum(wh - TOL, 1e-12)), np.log(wh + TOL)
    p_in = norm.cdf((hi - lm) / ls) - norm.cdf((lo - lm) / ls)
    line = ph >= 0.5
    q = np.where(line, 1.0 - ph * p_in, ph)
    wrong = np.where(line, (~p[idx]) | (np.abs(wh - np.nan_to_num(w[idx], nan=1e9)) > TOL), p[idx]).astype(bool)
    return dict(ph=ph, lm=lm, cov=cov, wh=wh, line=line, q=q, wrong=wrong)


def joint_wrong(st, sub, rng):
    """Draws x sites indicator of a wrong skip, from the process's own joint predictive over the sites `sub`."""
    cov = st["cov"][np.ix_(sub, sub)]
    Lc = np.linalg.cholesky(cov + 1e-10 * np.eye(len(sub)) * max(1.0, np.trace(cov) / len(sub)))
    lw = st["lm"][sub][None, :] + rng.standard_normal((D, len(sub))) @ Lc.T
    pres = rng.random((D, len(sub))) < st["ph"][sub][None, :]
    line = st["line"][sub][None, :]
    return np.where(line, (~pres) | (np.abs(np.exp(lw) - st["wh"][sub][None, :]) > TOL), pres)


def poisbin_cut(qs, cap):
    """Longest prefix of the sorted probabilities qs, ending at a change of value (a threshold alpha on q), whose
    Poisson-binomial count of wrong skips is at most cap with probability >= CONF; returns its length and the
    CONF-quantile of that count (the rate the process states)."""
    f = np.zeros(cap + 2); f[0] = 1.0                       # f[k] = P(K = k), last bin = P(K > cap)
    best, st = 0, 0.0
    for i, qi in enumerate(qs):
        g = f * (1.0 - qi); g[1:] += f[:-1] * qi; g[-1] += f[-1] * qi
        f = g
        if f[:-1].sum() < CONF:
            break
        if i + 1 == len(qs) or qs[i + 1] > qi:
            best, st = i + 1, float(np.searchsorted(np.cumsum(f), CONF))
    return best, st


def cuts(st, N, cal, rest, rng):
    q, wrong = st["q"], st["wrong"]; cap = int(np.floor(EPS * N)); m = len(cal)
    order = rest[np.argsort(q[rest], kind="stable")]
    # uq: joint statement on growing prefixes of the ranking
    J = joint_wrong(st, order, rng).cumsum(1)                 # draws x prefix length
    okp = (J <= cap).mean(0) >= CONF
    n_uq = int(np.argmin(okp)) if not okp.all() else len(order)
    sk_uq = order[:n_uq]
    st_uq = float(np.quantile(J[:, n_uq - 1], CONF)) / N if n_uq else 0.0
    # iid: site-by-site threshold on q, with the threshold set from the process's own probabilities taken as
    # independent (Poisson-binomial count of wrong skips; Hoeffding 1956)
    n_iid, st_iid = poisbin_cut(q[order], cap)
    sk_iid = order[:n_iid]
    # contract: largest threshold within the cap after the calibration failures
    t_best, k_best, u_best = -np.inf, 0, upper_count(N, m, 0)
    for t in np.sort(np.unique(q)):
        k = int(((q[cal] <= t) & wrong[cal]).sum()); u = upper_count(N, m, k)
        if u - k <= cap:
            t_best, k_best, u_best = t, k, u
        else:
            break
    sk_c = rest[q[rest] <= t_best]
    return dict(uq=dict(n_skip=int(n_uq), realised=int(wrong[sk_uq].sum()), stated=st_uq, skip=sk_uq),
                iid=dict(n_skip=int(n_iid), realised=int(wrong[sk_iid].sum()), stated=st_iid / N, skip=sk_iid),
                contract=dict(n_skip=int(len(sk_c)), realised=int(wrong[sk_c].sum()), stated=(u_best - k_best) / N,
                              skip=sk_c))


def campaign(xy, w, p, lv, design, kernel, driver):
    rng_cal = np.random.default_rng(5000 + design); rng = np.random.default_rng(9100 + design)
    measured = lv <= SEED_MAX; rounds = []
    for L in range(SEED_MAX + 1, int(lv.max()) + 1):
        idx = np.flatnonzero(lv == L); N = len(idx)
        st = round_state(xy, w, p, measured, idx, kernel, rng)
        cal = rng_cal.choice(N, size=min(M, N), replace=False)
        rest = np.setdiff1d(np.arange(N), cal)
        c = cuts(st, N, cal, rest, rng)
        rec = dict(L=L, N=N, cap=int(np.floor(EPS * N)))
        for k in ("uq", "iid", "contract"):
            rec[k] = {kk: v for kk, v in c[k].items() if kk != "skip"}
        rounds.append(rec)
        sel = np.ones(N, bool); sel[c[driver]["skip"]] = False
        measured[idx[sel]] = True
    return rounds, int(measured.sum())


def main(kernel, driver, start, n):
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
        done = {(r["kernel"], r["driver"], r["design"]) for r in map(json.loads, OUT.read_text().splitlines())}
    for d in range(start, start + n):
        if (kernel, driver, d) in done:
            continue
        idx, lv = make_design(1000 + d, xy_all)
        rounds, total = campaign(xy_all[idx], w_all[idx], p_all[idx], lv, d, kernel, driver)
        with OUT.open("a") as f:
            f.write(json.dumps(dict(kernel=kernel, driver=driver, design=d, measured=total, rounds=rounds)) + "\n")
        print(kernel, driver, d, total, [(r["iid"]["realised"], r["iid"]["n_skip"], r["uq"]["n_skip"], r["cap"]) for r in rounds], flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
