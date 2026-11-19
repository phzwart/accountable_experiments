"""
Where the IR confidence goes: nominal δ against the attained exceedance
probability, level by level.

For each certified level of a campaign, the level population (frozen scores,
interest and interpolation labels of every site) is fixed and the
calibration draw is repeated many times. Reported per level:

- nominal δ;
- binomial attainment P(Bin(m, ε) <= k) at the integer k used;
- finite-population attainment P(Hyp(N, floor(εN)+1, m) <= k);
- R_E,max: the shared rate if every coverable site were covered;
- the exceedance frequency of the actual policy over the redraws.

    python -m experiments.ir_bioreef.confidence_audit loose 5
    python -m experiments.ir_bioreef.confidence_audit tight 5
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import binom, hypergeom

from accountable import run_campaign
from accountable.campaign import INTEREST, INTERP
from accountable.policies import LevelData
from accountable.tails import allowed_k
from experiments.ir_bioreef import adapter as A


def setup(variant):
    if variant == "tight":
        A.RTOL, A.ATOL, A.FLOOR, A.INTEREST_LEVEL = 0.10, 0.01, 0.005, 0.02
    else:
        A.RTOL, A.ATOL, A.FLOOR, A.INTEREST_LEVEL = 0.10, 0.10, 0.02, 0.10


def audit_level(res, ds, cfg, L, draws, rng):
    idx = np.flatnonzero((ds.levels == L) & ds.candidate)
    N = len(idx)
    scores = {nm: res.scores[nm][idx] for nm in res.scores}
    bad = {INTERP: res.fail_prior[idx].astype(bool), INTEREST: res.interesting[idx].astype(bool)}
    caps = {c.name: c.cap for c in cfg.certificates}
    pol = cfg.policy
    eps, delta, m = pol.budget, 1 - pol.confidence, cfg.cal_size
    k = allowed_k(eps, m, delta, N=N, tail=pol.tail).k
    # Largest attainable shared rate: every site each certificate may cover.
    cover_all = {nm: np.isfinite(s) & (s < caps[nm] if caps.get(nm) is not None else True)
                 for nm, s in scores.items()}
    RE_max = float(np.mean(np.any([cover_all[nm] & bad[nm] for nm in scores], axis=0)))
    ex = 0
    for _ in range(draws):
        cal = np.sort(rng.choice(N, m, replace=False))
        d = pol.decide(LevelData(N, scores, cal, {nm: bad[nm][cal] for nm in scores}, caps=caps))
        RE = np.mean(np.any([d.covers[nm] & bad[nm] for nm in scores], axis=0))
        ex += RE > eps + 1e-12
    K = int(np.floor(eps * N)) + 1
    return dict(L=int(L), N=N, k=k, nominal=delta,
                binomial=float(binom.cdf(k, m, eps)),
                hypergeometric=float(hypergeom.cdf(k, N, K, m)),
                RE_max=RE_max, attained=ex / draws)


def main():
    variant, n_seeds = sys.argv[1], int(sys.argv[2])
    draws = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
    tail = sys.argv[4] if len(sys.argv) > 4 else "binomial"
    placement = sys.argv[5] if len(sys.argv) > 5 else "calibration"
    setup(variant)
    ds = A.load()
    rows = []
    for s in range(n_seeds):
        cfg = A.config(ds, policy="nested_path", eps=0.10, confidence=0.75, seed=s,
                       policy_kwargs=dict(tail=tail, placement=placement))
        cfg.certificates[0].cap = A.INTEREST_LEVEL
        cfg.interest = A.interest_predicate(A.INTEREST_LEVEL)
        res = run_campaign(ds, cfg)
        rng = np.random.default_rng(1000 + s)
        for L in range(cfg.seed_level + 1, int(ds.levels.max()) + 1):
            r = audit_level(res, ds, cfg, L, draws, rng)
            r.update(seed=s, variant=variant, tail=tail, placement=placement,
                     n_measured=res.n_measured)
            rows.append(r)
            print(json.dumps(r), flush=True)
    out = Path("results/ir_confidence_audit")
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{variant}_{tail}_{placement}.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
