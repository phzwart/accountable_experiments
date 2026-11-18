"""
Rerun of the three cases with exact natural-neighbour weights.

Each row holds one statement fixed and changes the protocol (score,
budget scheme). Every row is replicated over calibration seeds.

    python -m experiments.rerun --experiment ir_bioreef --seeds 20
    python -m experiments.rerun --experiment nacl_saxs --seeds 20
    python -m experiments.rerun --experiment synthetic_saxs --seeds 10
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from accountable import run_campaign

from .study import _load, summarise

# (experiment, row name, adapter kwargs). Statement noted per group.
ROWS = [
    # IR: R_E <= 0.10 at confidence 0.75, one budget on the shared event.
    *[("ir_bioreef", f"ir_nested_{s}", dict(policy="nested_path", eps=0.10, confidence=0.75, score=s))
      for s in ("logistic", "sibson_disagreement", "random")],
    # NaCl (200) width and full-profile envelope: R_E <= 0.20 at 0.80.
    *[("nacl_saxs", f"nacl_{t}_{p}_{s}", dict(target=t, mode="2cert", score=s, **kw))
      for t in ("fwhm", "envelope")
      for p, kw in (("separate", dict(policy="separate", eps=0.10, confidence=0.90)),
                    ("nested", dict(policy="nested_path", eps=0.20, confidence=0.80)))
      for s in ("logistic", "random")],
    # Synthetic: envelope, interpolation only (R_interp <= 0.10 at 0.90);
    # peak with two certificates (R_E <= 0.20 at 0.80).
    *[("synthetic_saxs", f"syn_envelope_interp_{s}", dict(target="envelope", mode="interp", eps=0.10, confidence=0.90, score=s))
      for s in ("logistic", "random")],
    *[("synthetic_saxs", f"syn_peak_2cert_{p}_logistic", dict(target="peak", mode="2cert", **kw))
      for p, kw in (("separate", dict(policy="separate", eps=0.10, confidence=0.90)),
                    ("nested", dict(policy="nested_path", eps=0.20, confidence=0.80)))],
]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--experiment", required=True)
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--out", default="runs/rerun")
    args = ap.parse_args(argv)
    out = Path(args.out)
    rows = [r for r in ROWS if r[0] == args.experiment]
    A, ds = _load(args.experiment)
    for seed in range(args.seeds):
        for exp, name, kw in rows:
            path = out / name / f"s{seed:02d}.json"
            if path.exists():
                continue
            t0 = time.time()
            res = run_campaign(ds, A.config(ds, seed=seed, nn_method="watson", **kw))
            row = dict(name=name, experiment=exp, seed=seed, kwargs=kw, config=res.config,
                       seconds=round(time.time() - t0, 1), **summarise(res))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(row, indent=1, default=str))
            print(f"{name} s{seed}: measured {row['n_measured']}/{row['n_design']}  "
                  f"level_E {row['level_E']}  ({row['seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
