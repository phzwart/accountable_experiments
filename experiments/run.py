"""
Run one accountable campaign.

    python -m experiments.run nacl_saxs --target fwhm --mode 2cert --confidence 0.9
    python -m experiments.run ir_bioreef --policy nested_path
    python -m experiments.run synthetic_saxs --target peak --mode 2cert

Results go to runs/<experiment>/<tag>/ (sites.npz, result.json).
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from accountable import run_campaign

EXPERIMENTS = ("nacl_saxs", "ir_bioreef", "synthetic_saxs")


def build(name, args):
    if name == "nacl_saxs":
        from .nacl_saxs import adapter as A
        ds, _ = A.load()
        cfg = A.config(ds, target=args.target or "fwhm", mode=args.mode or "2cert",
                       confidence=args.confidence or 0.90, seed=args.seed, score=args.score,
                       policy=args.policy or "separate", eps=args.eps or 0.10,
                       peak_eps=args.peak_eps, cal_size=args.cal_size, nn_method=args.nn_method)
    elif name == "ir_bioreef":
        from .ir_bioreef import adapter as A
        ds = A.load()
        cfg = A.config(ds, policy=args.policy or "nested_path", eps=args.eps or 0.10,
                       confidence=args.confidence or 0.75, seed=args.seed, cal_size=args.cal_size,
                       nn_method=args.nn_method)
    elif name == "synthetic_saxs":
        from .synthetic_saxs import adapter as A
        ds = A.load()
        cfg = A.config(ds, target=args.target or "envelope", mode=args.mode or "interp",
                       confidence=args.confidence or 0.90, seed=args.seed, score=args.score,
                       policy=args.policy or "separate", eps=args.eps or 0.10,
                       cal_size=args.cal_size, nn_method=args.nn_method)
    else:
        raise SystemExit(f"unknown experiment {name!r}; choose from {EXPERIMENTS}")
    return ds, cfg


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("experiment", choices=EXPERIMENTS)
    ap.add_argument("--target")
    ap.add_argument("--mode", choices=("interp", "2cert"))
    ap.add_argument("--policy")
    ap.add_argument("--confidence", type=float)
    ap.add_argument("--eps", type=float)
    ap.add_argument("--peak-eps", type=float)
    ap.add_argument("--score", default="logistic")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cal-size", type=int, default=40)
    ap.add_argument("--nn-method", default="legacy", choices=("legacy", "watson"))
    ap.add_argument("--out", default="runs")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args(argv)
    ds, cfg = build(args.experiment, args)
    t0 = time.time()
    res = run_campaign(ds, cfg, log=lambda m: print(m, flush=True))
    tag = args.tag or "_".join(str(x) for x in (
        args.target, args.mode, cfg.policy.policy_name, args.nn_method, f"c{args.confidence}",
        f"s{args.seed}") if x)
    out = res.save(Path(args.out) / args.experiment / tag)
    s = res.summary()
    s["seconds"] = round(time.time() - t0, 1)
    print(json.dumps(s, indent=1))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
