"""
Certified campaigns at several budgets, for the cost analysis: the quantile path with natural-neighbour
interpolation (20 campaigns per budget) and with the maximum-likelihood GP as predictor (8 per budget), on the
three maps, at each dataset's confidence. Records sites measured and wrong skips on the certified levels.

    python -m experiments.certified_budgets [nacl|ir|syn ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from accountable.campaign import run_campaign
from accountable import make_policy
from experiments.record import build

ROWS = {"nacl": ("nacl_fwhm_nested_watson", "nacl_fwhm_nested_gp_mle", 0.80),
        "ir": ("ir_nested_watson", "ir_nested_gp_mle", 0.75),
        "syn": ("syn_peak_2cert_nested_watson", "syn_peak_2cert_nested_gp_mle", 0.80)}
EPS = (0.05, 0.10, 0.20, 0.30)
N_SEEDS = {"sibson": 20, "gp": 8}
OUT = Path("results/uncertified")


def one(row, eps, conf, seed):
    ds, cfg, _ = build(row, seed, {})
    cfg.policy = make_policy("nested_path", budget=eps, confidence=conf)
    r = run_campaign(ds, cfg)
    c = ds.candidate & (ds.levels > cfg.seed_level)
    R = np.asarray(r.reason).astype(str)
    A = np.isin(R, ["not_interesting", "not_interesting+interpolable"])
    B = np.isin(R, ["interpolable", "not_interesting+interpolable"])
    W = r.skipped & ((A & r.interesting) | (B & r.fail_prior))
    return dict(measured=int(r.measured[ds.candidate].sum()), wrong=int((W & c).sum()),
                skipped=int((r.skipped & c).sum()), n_cert=int(c.sum()), n_total=int(ds.candidate.sum()))


def main():
    keys = [k for k in sys.argv[1:] if k in ROWS] or list(ROWS)
    for key in keys:
        sib, gp, conf = ROWS[key]
        out = []
        for name, row in (("sibson", sib), ("gp", gp)):
            for eps in EPS:
                runs = [one(row, eps, conf, s) for s in range(N_SEEDS[name])]
                m = np.mean([x["measured"] for x in runs]); w = np.mean([x["wrong"] for x in runs])
                out.append(dict(dataset=key, predictor=name, eps=eps, confidence=conf, runs=runs,
                                measured=float(m), wrong=float(w), n_cert=runs[0]["n_cert"], n_total=runs[0]["n_total"]))
                print(f"{key} {name} eps {eps:.2f}: measured {m:.0f}, wrong {w:.1f} ({100 * w / runs[0]['n_cert']:.1f} %)", flush=True)
        (OUT / f"certified_{key}.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
