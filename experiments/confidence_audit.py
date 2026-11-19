"""
Confidence audit for any experiment: attained exceedance probability of
every stated guarantee, level by level, against its nominal value and its
exact finite-population worst case.

For each certified level of a campaign, the level population (frozen
scores, interest and interpolation labels of every site) is held fixed and
the calibration draw is repeated ``draws`` times through the policy.

    python -m experiments.confidence_audit nacl_fwhm_nested_watson 3 2000 hypergeometric boundary
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import hypergeom

from accountable import run_campaign
from accountable.campaign import INTEREST, INTERP
from accountable.policies import LevelData
from accountable.tails import allowed_k
from experiments.study import ROWS, _load


def worst_case(eps, delta, m, N, tail):
    k = allowed_k(eps, m, delta, N=N, tail=tail).k
    K = int(np.floor(eps * N)) + 1
    return k, float(hypergeom.cdf(k, N, K, m)) if k >= 0 else 0.0


def audit_level(res, ds, cfg, L, draws, rng):
    idx = np.flatnonzero((ds.levels == L) & ds.candidate)
    N = len(idx)
    names = [c.name for c in cfg.certificates]
    scores = {nm: res.scores[nm][idx] for nm in names}
    labels = {INTERP: res.fail_prior[idx].astype(bool), INTEREST: res.interesting[idx].astype(bool)}
    bad = {nm: labels[nm] for nm in names}
    caps = {c.name: c.cap for c in cfg.certificates}
    pol, m = cfg.policy, min(cfg.cal_size, N)

    def rates(covers):
        out = {f"R_{nm}": float(np.mean(covers[nm] & bad[nm])) for nm in names}
        out["R_E"] = float(np.mean(np.any([covers[nm] & bad[nm] for nm in names], axis=0)))
        return out

    cover_all = {nm: np.isfinite(scores[nm]) & ((scores[nm] < caps[nm]) if caps.get(nm) is not None else True)
                 for nm in names}
    r_max = rates(cover_all)
    stats = {}
    for _ in range(draws):
        cal = np.sort(rng.choice(N, m, replace=False))
        d = pol.decide(LevelData(N, scores, cal, {nm: bad[nm][cal] for nm in names}, caps=caps))
        r = rates(d.covers)
        for g in d.guarantees:
            st = stats.setdefault(g.event, dict(budget=g.budget, confidence=g.confidence, ex=0, n=0))
            st["n"] += 1
            st["ex"] += r[g.event] > g.budget + 1e-12
    rows = []
    tail = getattr(pol, "tail", "binomial")
    for ev, st in stats.items():
        delta = 1 - st["confidence"]
        joint = ev == "R_E" and len(stats) > 1          # union-bound statement of the per-claim form
        k, wc = (None, None) if joint else worst_case(st["budget"], delta, m, N, tail)
        rows.append(dict(L=int(L), N=N, event=ev, budget=st["budget"], nominal=delta, k=k,
                         worst_case=wc, rate_max=r_max[ev], attained=st["ex"] / st["n"]))
    return rows


def main():
    row, n_seeds = sys.argv[1], int(sys.argv[2])
    draws = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
    tail = sys.argv[4] if len(sys.argv) > 4 else "binomial"
    placement = sys.argv[5] if len(sys.argv) > 5 else "calibration"
    exp, kw = ROWS[row]
    A, ds = _load(exp)
    pk = dict(tail=tail)
    if kw.get("policy", "separate") in ("nested_path", "priority_path"):
        pk["placement"] = placement
    out = []
    for s in range(n_seeds):
        cfg = A.config(ds, seed=s, policy_kwargs=pk, **kw)
        res = run_campaign(ds, cfg)
        rng = np.random.default_rng(1000 + s)
        for L in sorted(set(ds.levels[ds.candidate])):
            if L <= cfg.seed_level:
                continue
            for r in audit_level(res, ds, cfg, L, draws, rng):
                r.update(row=row, seed=s, tail=tail, placement=placement if "placement" in pk else None,
                         n_measured=res.n_measured)
                out.append(r)
                print(json.dumps(r), flush=True)
    d = Path("results/confidence_audit")
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{row}_{tail}_{pk.get('placement', 'na')}.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
