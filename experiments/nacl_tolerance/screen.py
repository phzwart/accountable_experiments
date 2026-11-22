"""Screen NaCl width tolerance and budget with natural-neighbour campaigns (quantile path, confidence 0.80).

    PYTHONPATH=$PWD:$PWD/src python experiments/nacl_tolerance/screen.py
"""
import json, sys, time
from pathlib import Path
import numpy as np
from accountable import run_campaign
from experiments.nacl_saxs import adapter as A
from experiments.study import summarise

TOLS = [float(x) for x in sys.argv[2:]] or [0.02, 0.03, 0.04, 0.05]
OUT = Path(f"experiments/nacl_tolerance/screen_{'_'.join(map(str, TOLS))}.jsonl")
done = set()
if OUT.exists():
    for l in OUT.read_text().splitlines():
        r = json.loads(l); done.add((r["tol"], r["eps"], r["seed"]))
ds, _ = A.load()
n_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 20
for tol in TOLS:
    for eps in (0.10, 0.20):
        for seed in range(n_seeds):
            if (tol, eps, seed) in done:
                continue
            t0 = time.time()
            res = run_campaign(ds, A.config(ds, target="fwhm", mode="2cert", policy="nested_path", eps=eps,
                                            confidence=0.80, nn_method="watson", seed=seed, tol=tol))
            s = summarise(res)
            with OUT.open("a") as f:
                f.write(json.dumps(dict(tol=tol, eps=eps, seed=seed, measured=s["n_measured"], level_E=s["level_E"],
                                        sec=round(time.time() - t0, 1))) + "\n")
        print(tol, eps, "done", flush=True)
