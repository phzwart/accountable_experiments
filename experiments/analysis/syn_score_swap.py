"""
Causal check on the synthetic map: replace the feature of the logistic interest score
(absolute height above the local baseline) by the quantity the interest label uses
(prominence, the height relative to the baseline), all else equal. Quantile path,
natural neighbour, same seeds as the record.

    python -m experiments.analysis.syn_score_swap 60
"""
from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from accountable import peak_descriptors, run_campaign
from accountable.scores import LogisticInterestScore
from experiments.record import build

ROW = "syn_peak_2cert_nested_watson"
OUTD = Path("results/analysis/syn_clumps")


class LogisticProminenceScore(LogisticInterestScore):
    name = "logistic_prominence"

    def _prominence(self, I):
        d = peak_descriptors(I, self._ms.axis, q_center=self.q_center, q_halfwidth=self.q_half)
        pr = np.asarray(d["prominence"], float)
        return np.where(np.isfinite(pr), pr, 0.0)


class PredictedProminenceScore(LogisticInterestScore):
    """Score = prominence of the interpolated spectrum itself (no learned model)."""
    name = "predicted_prominence"

    def fit(self, ms):
        self._ms = ms

    def score(self, points):
        from accountable.sibson import interpolate
        points = np.asarray(points, float)
        if len(points) == 0:
            return np.zeros(0, float)
        ms = self._ms
        I_hat = interpolate(ms.P, ms.I, points, images=ms.images, k_fallback=ms.k_fallback, method=ms.nn_method)
        d = peak_descriptors(I_hat, ms.axis)
        pr = np.asarray(d["prominence"], float)
        return np.where(np.isfinite(pr), pr, 0.0)


VARIANT = {"prominence_logistic": LogisticProminenceScore, "predicted_prominence": PredictedProminenceScore}


def one(args):
    seed, variant = args
    ds, cfg, _ = build(ROW, seed, {})
    c0 = cfg.certificates[0]
    old = c0.score
    c0.score = VARIANT[variant](old.interest, old.q_center, old.q_half, seed=old.seed)
    cfg.final_labels = False
    cfg.post_labels = False
    res = run_campaign(ds, cfg)
    cand = np.flatnonzero(ds.candidate)
    phase = np.asarray(ds.meta["phase"])[cand]
    reason = np.asarray(res.reason)[cand].astype(str)
    sk = np.asarray(res.skipped)[cand]
    I = np.asarray(res.interesting)[cand]
    F = np.asarray(res.fail_prior)[cand]
    a = np.isin(reason, ["not_interesting", "not_interesting+interpolable"])
    b = np.isin(reason, ["interpolable", "not_interesting+interpolable"])
    w = sk & ((a & I) | (b & F))
    exc = [bool(pl["level"]["E_rate"] > 0.2) for pl in res.per_level if "level" in pl and pl["level"].get("E_rate") is not None]
    return dict(seed=seed, measured=int((~sk).sum()), wrong=int(w.sum()), wrong_int=int((sk & a & I).sum()),
                wrong_L1=int((w & (phase == 0)).sum()), exceed=int(sum(exc)), checks=len(exc),
                wrong_sites=np.flatnonzero(w).tolist())


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    variant = sys.argv[2] if len(sys.argv) > 2 else "prominence_logistic"
    with Pool(2) as p:
        rows = list(p.imap_unordered(one, [(s, variant) for s in range(n)]))
    (OUTD / f"score_swap_{variant}.json").write_text(json.dumps(sorted(rows, key=lambda r: r["seed"])))
    m = np.array([r["measured"] for r in rows]); w = np.array([r["wrong"] for r in rows])
    print(f"measured {m.mean():.0f} ± {m.std():.0f}; wrong {w.mean():.1f}; wrong in L1 {np.mean([r['wrong_L1'] for r in rows]):.1f}; "
          f"exceedances {sum(r['exceed'] for r in rows)}/{sum(r['checks'] for r in rows)}")
