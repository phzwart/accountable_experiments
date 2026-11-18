"""
IR protocol comparison at a tight tolerance, where interpolation binds.

Envelope tolerance ±(10 % + 0.01) absorbance, signal floor 0.005; either
with the interest certificate at absorbance 0.02 ("tight") or with the
interpolation certificate alone ("tight_interp"). Quantile path, R_E ≤ 0.10
at confidence 0.75, natural neighbour against three GP length-scale rules.

    python -m experiments.ir_bioreef.tight_protocols 20 tight sibson,gp_mle
"""
import json
import sys
from pathlib import Path

import numpy as np

from accountable import make_policy, run_campaign
from experiments.ir_bioreef import adapter as A
from experiments.study import summarise

VARIANTS = {"tight": 0.02, "tight_interp": None}


def main():
    n_seeds = int(sys.argv[1])
    variants = sys.argv[2].split(",")
    protos = sys.argv[3].split(",")
    out = Path("runs/ir_tight")
    out.mkdir(parents=True, exist_ok=True)
    ds = A.load()
    A.RTOL, A.ATOL, A.FLOOR = 0.10, 0.01, 0.005
    for v in variants:
        interest = VARIANTS[v]
        A.INTEREST_LEVEL = interest if interest is not None else 0.10
        for p in protos:
            for s in range(n_seeds):
                path = out / f"{v}_{p}_s{s:02d}.json"
                if path.exists():
                    continue
                cfg = A.config(ds, policy="nested_path", eps=0.10, confidence=0.75, seed=s, interp_model=p)
                if interest is None:
                    cfg.certificates = [c for c in cfg.certificates if c.name == "interp"]
                    cfg.policy = make_policy("nested_path", budget=0.10, confidence=0.75)
                else:
                    cfg.certificates[0].cap = interest
                    cfg.interest = A.interest_predicate(interest)
                r = run_campaign(ds, cfg)
                lv = [x for x in r.per_level if not x.get("empty")]
                row = dict(variant=v, protocol=p, seed=s, **summarise(r),
                           cal_fail_interp=[x["certificates"]["interp"]["cal_bad"] for x in lv],
                           skipped=np.flatnonzero(r.skipped).tolist())
                path.write_text(json.dumps(row, default=str))
                print(v, p, s, row["n_measured"], row["cal_fail_interp"], flush=True)


if __name__ == "__main__":
    main()
