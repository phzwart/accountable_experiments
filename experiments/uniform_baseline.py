"""
Uniform subsampling at equal cost: the seed levels plus a uniform random sample of the remaining design sites,
of the size that brings the total to the mean number measured by the certified plan (quantile path,
natural-neighbour interpolation). Every other site is predicted from all measured sites with the same predictor,
and counted wrong where the prediction fails the claim's metric. Reported as a share of the sites of the
certified levels, the denominator of the guarantee. Nothing is calibrated, so no rate is stated.

    python -m experiments.uniform_baseline
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

import numpy as np

from experiments.record import OUT as REC, build

ROWS = {"ir": "ir_nested_watson", "nacl": "nacl_fwhm_nested_watson", "syn": "syn_peak_2cert_nested_watson"}
N_SEEDS = 20
OUT = Path("results/uniform_baseline.json")


def main():
    res = {}
    for key, row in ROWS.items():
        M = np.mean([json.loads(l)["summary"]["n_measured"] for l in gzip.open(REC / row / "runs.jsonl.gz", "rt")])
        runs = []
        for s in range(N_SEEDS):
            ds, cfg, _ = build(row, s, {})
            P, lv, cand = ds.points, ds.levels, ds.candidate
            truth = ds.oracle.truth(np.arange(ds.n))
            seed = (lv <= cfg.seed_level) & cand
            rest = np.flatnonzero(cand & ~seed)
            rng = np.random.default_rng(1000 + s)
            pick = rng.choice(rest, size=int(round(M)) - int(seed.sum()), replace=False)
            measured = seed.copy(); measured[pick] = True
            q = np.flatnonzero(cand & ~measured)
            mean = cfg.predictor.predict(P[measured], truth[measured], P[q])
            fail = np.asarray(cfg.criterion.stats(truth[q], mean)["outside_mean"], bool)
            cert = cand & (lv > cfg.seed_level)
            wrong = np.zeros(ds.n, bool); wrong[q] = fail
            runs.append(dict(seed=s, measured=int(measured.sum()), wrong=int((wrong & cert).sum()),
                             n_cert=int(cert.sum()), share=float((wrong & cert).sum() / cert.sum())))
        sh = np.array([r["share"] for r in runs])
        res[key] = dict(row=row, measured=float(np.mean([r["measured"] for r in runs])), share_mean=float(sh.mean()),
                        share_range=[float(sh.min()), float(sh.max())], runs=runs)
        print(key, res[key]["measured"], round(100 * sh.mean(), 1), [round(100 * x, 1) for x in res[key]["share_range"]],
              flush=True)
    OUT.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()


def certified_final(n=20):
    """Final-map error of the certified plan, same metric: skipped certified-level sites whose prediction from
    all measured sites fails the claim's metric, as a share of the certified-level sites."""
    from accountable.campaign import run_campaign
    out = {}
    for key, row in ROWS.items():
        sh, ms = [], []
        for s in range(n):
            ds, cfg, _ = build(row, s, {})
            r = run_campaign(ds, cfg)
            cert = ds.candidate & (ds.levels > cfg.seed_level)
            bad = np.zeros(ds.n, bool)
            for f in r.final:
                bad[f["index"]] = f["outside"]
            sh.append(float((bad & cert).sum() / cert.sum())); ms.append(int(r.measured[ds.candidate].sum()))
        out[key] = dict(measured=float(np.mean(ms)), share_mean=float(np.mean(sh)), share_range=[min(sh), max(sh)])
        print("certified final", key, out[key], flush=True)
    d = json.loads(OUT.read_text()); d["certified_final"] = out; OUT.write_text(json.dumps(d, indent=1))
