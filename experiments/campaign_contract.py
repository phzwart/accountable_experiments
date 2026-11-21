"""
Campaign-level contracts: the plan is certified to reach its goal on every certified level at once. The
campaign failure probability 1 - c is divided equally among the certified levels of the plan when it is
declared, so each level runs at confidence 1 - (1 - c) / n_levels, and by the union bound all levels hold
together with probability at least c. Quantile path, natural-neighbour interpolation, 250 campaigns per map,
same seeds and budgets as the per-level runs of the record.

    python -m experiments.campaign_contract ir nacl
    python -m experiments.campaign_contract syn
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

from accountable import make_policy
from accountable.campaign import run_campaign
from experiments.record import build
from experiments.record_picked import worst_case_tail

# key: (row, budget eps, campaign confidence c, number of certified levels)
ROWS = {"ir": ("ir_nested_watson", 0.10, 0.75, 4),
        "nacl": ("nacl_fwhm_nested_watson", 0.20, 0.80, 4),
        "syn": ("syn_peak_2cert_nested_watson", 0.20, 0.80, 6)}
N_SEEDS = 250
OUT = Path("results/campaign_contract")


def one(row, eps, conf_level, seed):
    ds, cfg, _ = build(row, seed, {})
    cfg.policy = make_policy("nested_path", budget=eps, confidence=conf_level)
    t0 = time.time()
    r = run_campaign(ds, cfg)
    levels = []
    for lv in r.per_level:
        if lv.get("empty"):
            continue
        name = next(iter(lv["certificates"]))
        k = lv["certificates"][name]["k"]
        dl = worst_case_tail(k, eps, lv["n_cal"], lv["n_level"], "hypergeometric")
        rate = lv["level"]["E_rate"]
        levels.append(dict(L=lv["L"], n_level=lv["n_level"], n_cal=lv["n_cal"], k=k, picked=dl,
                           E_rate=rate, exceeded=bool(rate > eps + 1e-12)))
    c = ds.candidate & (ds.levels > cfg.seed_level)
    R = np.asarray(r.reason).astype(str)
    A = np.isin(R, ["not_interesting", "not_interesting+interpolable"])
    B = np.isin(R, ["interpolable", "not_interesting+interpolable"])
    W = r.skipped & ((A & r.interesting) | (B & r.fail_prior))
    return dict(seed=seed, measured=int(r.measured[ds.candidate].sum()), wrong=int((W & c).sum()),
                n_cert=int(c.sum()), n_total=int(ds.candidate.sum()), levels=levels,
                campaign_exceeded=any(x["exceeded"] for x in levels), seconds=time.time() - t0)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    keys = [k for k in sys.argv[1:] if k in ROWS] or list(ROWS)
    for key in keys:
        row, eps, conf, nlev = ROWS[key]
        conf_level = 1.0 - (1.0 - conf) / nlev
        f = OUT / f"{key}.jsonl"
        done = {json.loads(l)["seed"] for l in f.open()} if f.exists() else set()
        with f.open("a") as fh:
            for s in range(N_SEEDS):
                if s in done:
                    continue
                rec = one(row, eps, conf_level, s)
                rec.update(dataset=key, row=row, eps=eps, campaign_confidence=conf, level_confidence=conf_level)
                fh.write(json.dumps(rec) + "\n"); fh.flush()
                if s % 25 == 0:
                    print(key, s, rec["measured"], rec["campaign_exceeded"], flush=True)


if __name__ == "__main__":
    main()
