"""The stock-picking chicken: a deliberately useless model under the same conformal thresholds.

Same designs, rounds, calibration draws, budget (0.20 per round) and confidence (0.80) as experiments/paired_gp.py.
At each site of a round the chicken pecks one measured site at random and copies its presence and width; it ranks the
sites by a random number. The calibration draw sets the threshold on that ranking exactly as for the Gaussian process.
The chicken states nothing about its own errors, so only the conformal cut is run.

    PYTHONPATH=$PWD:$PWD/src python experiments/chicken.py START N
"""
import json
import sys
from pathlib import Path

import numpy as np

from experiments.paired_gp import EPS, M, SEED_MAX, upper_count
from experiments.staged_gp_designs import make_design
from experiments.uncertified_gp import TOL

OUT = Path("results/revision2/paired_chicken.jsonl")


def conformal_cut(q, wrong, N, cal, rest):
    cap = int(np.floor(EPS * N)); m = len(cal)
    t_best, k_best, u_best = -np.inf, 0, upper_count(N, m, 0)
    for t in np.sort(np.unique(q)):
        k = int(((q[cal] <= t) & wrong[cal]).sum()); u = upper_count(N, m, k)
        if u - k <= cap:
            t_best, k_best, u_best = t, k, u
        else:
            break
    sk = rest[q[rest] <= t_best]
    return sk, dict(n_skip=int(len(sk)), realised=int(wrong[sk].sum()), stated=(u_best - k_best) / N)


def campaign(w, p, lv, design):
    rng_cal = np.random.default_rng(5000 + design); rng = np.random.default_rng(31337 + design)
    measured = lv <= SEED_MAX; rounds = []
    for L in range(SEED_MAX + 1, int(lv.max()) + 1):
        idx = np.flatnonzero(lv == L); N = len(idx)
        peck = rng.choice(np.flatnonzero(measured), size=N)          # copy a random measured site
        line = p[peck]
        wrong = np.where(line, (~p[idx]) | (np.abs(w[peck] - np.nan_to_num(w[idx], nan=1e9)) > TOL), p[idx])
        q = rng.random(N)                                             # random ranking
        cal = rng_cal.choice(N, size=min(M, N), replace=False)
        rest = np.setdiff1d(np.arange(N), cal)
        sk, rec = conformal_cut(q, wrong.astype(bool), N, cal, rest)
        rounds.append(dict(L=L, N=N, cap=int(np.floor(EPS * N)), base_wrong=float(wrong.mean()), contract=rec))
        sel = np.ones(N, bool); sel[sk] = False
        measured[idx[sel]] = True
    return rounds, int(measured.sum())


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
        rounds, total = campaign(w_all[idx], p_all[idx], lv, d)
        with OUT.open("a") as f:
            f.write(json.dumps(dict(kernel="chicken", driver="contract", design=d, measured=total, rounds=rounds)) + "\n")
        print(d, total, [(r["contract"]["realised"], r["cap"], r["contract"]["n_skip"]) for r in rounds], flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
