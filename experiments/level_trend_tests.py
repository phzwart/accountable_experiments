"""Are the per-level over-budget rates consistent with one stated confidence? Tests on the 80 fresh designs.

For each rule (process's own word, contract) and level: over-budget count, one-sided binomial p-value of
exceeding the promised rate 0.20 (validity), and two-sided against the rule's own nominal rate (sharpness).
Across levels, with the four levels of a design paired: Cochran's Q for equal rates and a permutation test
for a monotone trend (slope of the rate against level; level labels permuted within each design).

    python experiments/level_trend_tests.py [results file] [key_own] [key_contract]
"""
import json
import os
import sys

import numpy as np
from scipy.stats import binomtest
from scipy.stats import chi2


def cochrans_q(X):
    k = X.shape[1]; C = X.sum(0); R = X.sum(1); N = X.sum()
    den = k * N - (R ** 2).sum()
    Q = (k - 1) * (k * (C ** 2).sum() - N ** 2) / den if den > 0 else 0.0
    return Q, float(chi2.sf(Q, k - 1))

f = sys.argv[1] if len(sys.argv) > 1 else "results/revision2/staged_gp_designs.jsonl"
keys = sys.argv[2:] or ["own", "contract"]
EPS = float(os.environ.get("STAGED_EPS", 0.20))
rr = [json.loads(l) for l in open(f)]
out = {}
for key in keys:
    wk = "W_level" if "contract" in key else "realised"
    X = np.array([[l[wk] > np.floor(EPS * l["N"]) for l in r[key]] for r in rr]).astype(int)   # designs x levels
    n, L = X.shape
    rate = X.mean(0)
    nominal = np.array([[l.get("delta_picked", l.get("stated_over", 0.2)) for l in r[key]] for r in rr]).mean(0)
    p_valid = [binomtest(int(X[:, j].sum()), n, 0.2, alternative="greater").pvalue for j in range(L)]
    p_sharp = [binomtest(int(X[:, j].sum()), n, nominal[j]).pvalue for j in range(L)]
    q = cochrans_q(X)
    lev = np.arange(L) - (L - 1) / 2
    slope = lambda A: float((A.mean(0) * lev).sum() / (lev ** 2).sum())       # noqa: E731
    s0 = slope(X); rng = np.random.default_rng(0); B = 20000
    perm = np.array([slope(np.array([rng.permutation(row) for row in X])) for _ in range(B)])
    p_trend = float((np.abs(perm) >= abs(s0) - 1e-12).mean())
    out[key] = dict(n=n, over=X.sum(0).tolist(), rate=rate.round(3).tolist(), nominal=nominal.round(3).tolist(),
                    p_exceeds_0p20=np.round(p_valid, 4).tolist(), p_vs_nominal=np.round(p_sharp, 5).tolist(),
                    cochran_q=round(float(q[0]), 2), p_equal_rates=q[1],
                    slope_per_level=round(s0, 4), p_trend=p_trend)
    print(key, json.dumps(out[key]))
json.dump(out, open(f.replace(".jsonl", "_trend_tests.json"), "w"), indent=1)
