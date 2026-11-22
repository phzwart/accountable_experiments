import sys, json, time
import numpy as np
from pathlib import Path
import experiments.revision2 as R
from experiments.record import build
from accountable.campaign import run_campaign
lo, hi, out = int(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3])
done = set()
for f in [R.OUT/"recall_nacl.jsonl", out]:
    if f.exists(): done |= {json.loads(l)["seed"] for l in f.open()}
row, eps = R.ROWS["nacl"], R.EPS["nacl"]
with out.open("a") as fh:
    for s in range(lo, hi):
        if s in done: continue
        ds, cfg, _ = build(row, s, {})
        cfg.policy = R.RecallNestedPathPolicy(budget=eps, confidence=cfg.policy.confidence, recall_budget=0.20, recall_confidence=0.80)
        t0 = time.time(); r = run_campaign(ds, cfg)
        rec = dict(seed=s, measured=int(r.measured[ds.candidate].sum()), levels=R._levels(r, eps),
                   recall=R._recall_rates(ds, r, cfg.seed_level + 1), eps_r=0.20, conf_r=0.80, seconds=time.time() - t0)
        fh.write(json.dumps(rec) + "\n"); fh.flush()
