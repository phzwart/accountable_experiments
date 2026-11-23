"""Where does success come from: staging or calibration? NaCl, same Gaussian process as experiments/staged_gp.py,
same 80 fresh designs as experiments/staged_gp_designs.py.

Arms per design:
  staged_shuffled_own / staged_shuffled_contract: the staged rules with level membership shuffled at random
      (same level sizes), so the seed and every level are random subsets instead of space-filling ones.
  unstaged_own: from the seed (levels 0-2), batches of 25 chosen among a random 80 % of the unmeasured sites by
      the process's probability of a wrong skip, until its own statement on skipping every unmeasured site
      (Poisson-binomial) gives P(wrong <= eps * N_cert) >= 0.80.
  unstaged_contract: the same acquisition up to that point, then a uniform draw of 40 unmeasured sites and the
      exact hypergeometric cut on the unmeasured set (allowed count floor(eps * N_cert)), the rest measured.

    PYTHONPATH=$PWD:$PWD/src python experiments/factorial_gp.py START N
"""
import json
import sys
from pathlib import Path

import numpy as np

from experiments.staged_gp import CONF, EPS, M, allowed_k, contract, level_model, own_word, poisson_binomial
from experiments.staged_gp_designs import make_design

OUT = Path("results/revision2/factorial_gp.jsonl")


def unstaged(xy, w, p, lv, seed, batch=25, frac=0.8):
    rng = np.random.default_rng(7000 + seed)
    measured = lv <= 2; n_cert = int((lv >= 3).sum()); cap = int(np.floor(EPS * n_cert))
    while True:
        U = np.flatnonzero(~measured)
        q, wrong = level_model(xy, w, p, measured, U)
        if poisson_binomial(q)[: cap + 1].sum() >= CONF or len(U) <= batch:
            break
        cand = rng.choice(len(U), size=max(batch, int(frac * len(U))), replace=False)
        measured[U[cand[np.argsort(-q[cand])[:batch]]]] = True
    own = dict(measured=int(measured.sum()), realised=int(wrong.sum()), cap=cap, over=bool(wrong.sum() > cap))
    # contract on top: frozen model, uniform draw from the unmeasured set, ranked cut
    N = len(U); cal = rng.choice(N, size=min(M, N), replace=False)
    Wstar = cap + 1
    ks = np.arange(0, len(cal) + 1)
    from scipy.stats import hypergeom
    cdf = hypergeom.cdf(ks, N, min(Wstar, N), len(cal)); okk = ks[cdf <= 1 - CONF]
    k_ok = int(okk.max()) if len(okk) else -1
    t_best = -np.inf
    for t in np.concatenate([[-np.inf], np.sort(np.unique(q))]):
        if ((q[cal] <= t) & wrong[cal]).sum() <= k_ok:
            t_best = t
        else:
            break
    rest = np.setdiff1d(np.arange(N), cal); skip = rest[q[rest] <= t_best]
    W = int(((q <= t_best) & wrong).sum())
    con = dict(measured=int(measured.sum() + N - len(skip)), realised=int(wrong[skip].sum()), W=W, cap=cap,
               over=bool(W > cap), k_allowed=k_ok)
    return own, con


def main(start, n):
    sys.path.insert(0, "manuscript/figures")
    from fig_datasets import nacl_fwhm
    from experiments.nacl_saxs.adapter import load
    _, grid = load()
    xy_all = np.asarray(grid["xy_mm"], float)
    img, pres, (xs, ys), _, _ = nacl_fwhm()
    ix = np.searchsorted(xs, xy_all[:, 0].round(4).clip(xs[0], xs[-1]))
    iy = np.searchsorted(ys, xy_all[:, 1].round(4).clip(ys[0], ys[-1]))
    w_all, p_all = img[iy, ix], pres[iy, ix]
    done = {json.loads(l)["design"] for l in OUT.read_text().splitlines()} if OUT.exists() else set()
    for d in range(start, start + n):
        if d in done:
            continue
        idx, lv = make_design(1000 + d, xy_all)
        xy, w, p = xy_all[idx], w_all[idx], p_all[idx]
        lv_sh = np.random.default_rng(3000 + d).permutation(lv)
        so = own_word(xy, w, p, lv_sh)
        for o in so:
            o.pop("stated_pmf")
        sc = contract(xy, w, p, lv_sh, d)
        uo, uc = unstaged(xy, w, p, lv, d)
        row = dict(design=d, staged_shuffled_own=so, staged_shuffled_contract=sc, unstaged_own=uo, unstaged_contract=uc)
        with OUT.open("a") as f:
            f.write(json.dumps(row) + "\n")
        print(d, "shuf own", so[-1]["measured_after"], "shuf con", sc[-1]["measured_after"],
              "unst own", uo["measured"], uo["realised"], uo["cap"], "unst con", uc["measured"], uc["W"], flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
