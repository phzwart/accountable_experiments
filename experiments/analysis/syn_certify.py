"""
Is the certification correct for every claim? Synthetic map, interpolation certificate only,
quantile path, budget 0.20 at confidence 0.80, natural neighbour; many campaigns per claim.
Per level: picked failure probability delta_L (worst case at the k used), whether the wrong-skip
rate exceeded the budget, and whether it could (covering every coverable site would exceed it).

    python -m experiments.analysis.syn_certify 100
"""
from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from accountable import run_campaign
from accountable.tails import worst_case_tail
from experiments.record_picked import poisson_binomial_sf
from experiments.study import _load

OUTD = Path("results/analysis/syn_certify")
VARIANTS = {
    "peak_x1": ("peak", dict(PEAK_EPS=0.005, FWHM_EPS=0.001)),
    "peak_x0.5": ("peak", dict(PEAK_EPS=0.0025, FWHM_EPS=0.0005)),
    "peak_x0.25": ("peak", dict(PEAK_EPS=0.00125, FWHM_EPS=0.00025)),
    "envelope_1pc": ("envelope", dict(RTOL=0.01, ATOL=0.01)),
    "envelope_5pc": ("envelope", dict(RTOL=0.05, ATOL=0.05)),
}
_CACHE = {}


def one(args):
    name, seed = args
    target, consts = VARIANTS[name]
    if "A" not in _CACHE:
        _CACHE["A"], _CACHE["ds"] = _load("synthetic_saxs")
    A, ds = _CACHE["A"], _CACHE["ds"]
    saved = {k: getattr(A, k) for k in consts}
    for k, v in consts.items():
        setattr(A, k, v)
    try:
        cfg = A.config(ds, target=target, mode="interp", policy="nested_path", eps=0.20, confidence=0.80,
                       seed=seed, nn_method="watson")
        cfg.final_labels = False
        cfg.post_labels = False
        res = run_campaign(ds, cfg)
    finally:
        for k, v in saved.items():
            setattr(A, k, v)
    tail = cfg.policy.describe().get("tail", "hypergeometric") if hasattr(cfg.policy, "describe") else "hypergeometric"
    levels = np.asarray(ds.levels)
    fail = np.asarray(res.fail_prior, bool)
    sc = np.asarray(res.scores["interp"], float)
    checks = []
    for lv in res.per_level:
        if lv.get("empty"):
            continue
        idx = np.flatnonzero((levels == lv["L"]) & np.asarray(ds.candidate, bool))
        N, m = lv["n_level"], lv["n_cal"]
        k = lv["certificates"]["interp"]["k"]
        dl = worst_case_tail(k, 0.20, m, N, tail)
        cov = np.isfinite(sc[idx])
        checks.append(dict(L=int(lv["L"]), N=int(N), k=int(k), picked=float(dl), rate=float(lv["level"]["E_rate"]),
                           exceeded=bool(lv["level"]["E_rate"] > 0.20 + 1e-12),
                           reachable=bool(np.mean(cov & fail[idx]) > 0.20 + 1e-12)))
    return dict(variant=name, seed=seed, measured=int(np.asarray(res.measured).sum()), checks=checks)


def summarise(rows):
    out = {}
    for name in VARIANTS:
        rs = [r for r in rows if r["variant"] == name]
        if not rs:
            continue
        ch = [c for r in rs for c in r["checks"]]
        p = np.array([c["picked"] for c in ch])
        x = int(sum(c["exceeded"] for c in ch))
        reach = [c for c in ch if c["reachable"]]
        pr = np.array([c["picked"] for c in reach])
        xr = int(sum(c["exceeded"] for c in reach))
        out[name] = dict(campaigns=len(rs), measured=float(np.mean([r["measured"] for r in rs])),
                         checks=len(ch), exceeded=x, allowed=float(p.sum()), mean_picked=float(p.mean()),
                         p_value=poisson_binomial_sf(p, x), reachable=len(reach), exceeded_reachable=xr,
                         allowed_reachable=float(pr.sum()), mean_rate=float(np.mean([c["rate"] for c in ch])))
    return out


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    names = sys.argv[2].split(",") if len(sys.argv) > 2 else list(VARIANTS)
    OUTD.mkdir(parents=True, exist_ok=True)
    with Pool(2) as pool:
        rows = list(pool.imap_unordered(one, [(nm, s) for nm in names for s in range(n)]))
    (OUTD / f"runs_{'_'.join(names) if len(names) < len(VARIANTS) else 'all'}.json").write_text(json.dumps(rows))
    print(json.dumps(summarise(rows), indent=1))
