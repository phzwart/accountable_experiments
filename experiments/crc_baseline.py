"""
Conformal risk control on the same calibration draw (Angelopoulos et al., ICLR 2024): the expectation analogue
of the certified rule. Along the same nested path, the threshold admits the largest number k of failing
calibration sites with (k + 1) / (m + 1) <= eps, which bounds the expected share of the level skipped wrongly by
eps but makes no statement about a single level. Same seeds, scores, predictor and budget as the certified
runs of the record; only the allowed number of calibration failures changes.

    python -m experiments.crc_baseline ir nacl syn
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

import accountable.policies as P
from accountable import make_policy
from accountable.campaign import run_campaign
from accountable.tails import TailDecision
from experiments.record import build

ROWS = {"ir": ("ir_nested_watson", 0.10), "nacl": ("nacl_fwhm_nested_watson", 0.20),
        "syn": ("syn_env_nested_watson", 0.10)}
N_SEEDS = 250
OUT = Path("results/crc_baseline")


def crc_k(eps, m, delta, N=None, tail="hypergeometric"):
    k = int(math.floor(eps * (m + 1) - 1 + 1e-12))
    return TailDecision(k=k, k_binomial=k, k_hypergeometric=k, eps=float(eps), m=int(m), delta=float(delta),
                        N=N, tail="crc", delta_picked=None)


def main():
    P.allowed_k = crc_k
    OUT.mkdir(parents=True, exist_ok=True)
    keys = [k for k in sys.argv[1:] if k in ROWS] or list(ROWS)
    for key in keys:
        row, eps = ROWS[key]
        f = OUT / f"{key}.jsonl"
        done = {json.loads(l)["seed"] for l in f.open()} if f.exists() else set()
        with f.open("a") as fh:
            for s in range(N_SEEDS):
                if s in done:
                    continue
                ds, cfg, _ = build(row, s, {})
                cfg.policy = make_policy("nested_path", budget=eps, confidence=0.5)
                t0 = time.time()
                r = run_campaign(ds, cfg)
                lev = [dict(L=lv["L"], E_rate=lv["level"]["E_rate"],
                            k=next(iter(lv["certificates"].values()))["k"])
                       for lv in r.per_level if not lv.get("empty")]
                c = ds.candidate & (ds.levels > cfg.seed_level)
                R = np.asarray(r.reason).astype(str)
                A = np.isin(R, ["not_interesting", "not_interesting+interpolable"])
                B = np.isin(R, ["interpolable", "not_interesting+interpolable"])
                W = r.skipped & ((A & r.interesting) | (B & r.fail_prior))
                rec = dict(dataset=key, seed=s, eps=eps, measured=int(r.measured[ds.candidate].sum()),
                           wrong=int((W & c).sum()), n_cert=int(c.sum()), levels=lev,
                           exceeded=[x["E_rate"] > eps + 1e-12 for x in lev], seconds=time.time() - t0)
                fh.write(json.dumps(rec) + "\n"); fh.flush()
                if s % 20 == 0:
                    print(key, s, rec["measured"], sum(rec["exceeded"]), flush=True)


if __name__ == "__main__":
    main()
