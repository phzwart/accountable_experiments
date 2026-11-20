"""
Dry-run campaigns on the simulated 4-D calcination map.

    python -m experiments.tio2_calcination.dryrun run --rows size_delaunay --seeds 0-99
    python -m experiments.tio2_calcination.dryrun report

``run`` writes one compact record per campaign to runs/tio2/<row>/ (resumable);
``report`` aggregates them into results/tio2/SUMMARY.md and summary.json.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from accountable import INTEREST, INTERP, run_campaign
from accountable.tails import worst_case_tail

from . import adapter as A

RUNS = Path("runs/tio2")
OUT = Path("results/tio2")

ROWS = {
    "size_delaunay": dict(target="size"),
    "pattern_delaunay": dict(target="pattern"),
    "size_random": dict(target="size", score="random"),
    "pattern_random": dict(target="pattern", score="random"),
    "size_gp_design": dict(target="size", interp_model="gp_design"),
    "size_delaunay_split": dict(target="size", furnace="split"),
}


def _seeds(s):
    a, b = s.split("-") if "-" in s else (s, s)
    return range(int(a), int(b) + 1)


def one(row: str, seed: int) -> dict:
    kw = dict(ROWS[row])
    furnace = kw.pop("furnace", "per_sample")
    ds = A.load(truth_seed=0, furnace=furnace)
    t0 = time.time()
    res = run_campaign(ds, A.config(ds, seed=seed, **kw))
    names = [c["name"] for c in res.config["certificates"]]
    tail = res.config["policy"].get("tail", "hypergeometric")
    levels = np.asarray(ds.levels)
    lab = {INTERP: np.asarray(res.fail_prior, bool), INTEREST: np.asarray(res.interesting, bool)}
    checks = []
    for lv in res.per_level:
        if lv.get("empty"):
            continue
        g = [x for x in lv["guarantees"] if x["event"] == "R_E"][0]
        b = g["budget"]
        k = lv["certificates"][names[0]]["k"]
        dl = worst_case_tail(k, b, lv["n_cal"], lv["n_level"], tail)
        idx = np.flatnonzero(levels == lv["L"])
        rmax = float(np.mean(np.any([lab[nm][idx] for nm in names], axis=0)))
        checks.append(dict(L=lv["L"], n=lv["n_level"], m=lv["n_cal"], rate=lv["level"]["E_rate"], budget=b,
                           picked=dl, exceeded=bool(lv["level"]["E_rate"] > b + 1e-12),
                           reachable=bool(rmax > b + 1e-12)))
    wrong = np.zeros(len(levels), bool)
    sk = np.asarray(res.skipped, bool)
    reason = np.asarray(res.reason).astype(str)
    cov_int = np.isin(reason, ["not_interesting", "not_interesting+interpolable"])
    cov_itp = np.isin(reason, ["interpolable", "not_interesting+interpolable"])
    wrong = sk & ((cov_int & lab[INTEREST]) | (cov_itp & lab[INTERP]))
    return dict(row=row, seed=seed, seconds=round(time.time() - t0, 1), n_measured=res.n_measured,
                reasons=res.summary()["reasons"], checks=checks,
                measured_nc=np.flatnonzero(reason == "no_certificate").tolist(),
                wrong=np.flatnonzero(wrong).tolist(), interesting=int(lab[INTEREST].sum()),
                wrong_interesting=int((wrong & lab[INTEREST]).sum()))


def run(rows, seeds):
    for row in rows:
        d = RUNS / row
        d.mkdir(parents=True, exist_ok=True)
        for s in seeds:
            p = d / f"s{s:03d}.json"
            if p.exists():
                continue
            p.write_text(json.dumps(one(row, s)))


def report():
    from scipy.stats import binom
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {}
    lines = ["| Row | Campaigns | Measured (mean ± s.d.) of 1024 | No claim | Level checks | Allowed (Σ δ_L) | Observed | Obs / allowed | Wrong skips | Interesting sites lost |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for row in ROWS:
        files = sorted((RUNS / row).glob("s*.json"))
        if not files:
            continue
        R = [json.loads(f.read_text()) for f in files]
        meas = np.array([r["n_measured"] for r in R])
        nc = np.array([len(r["measured_nc"]) for r in R])
        ch = [c for r in R for c in r["checks"]]
        allowed = sum(c["picked"] for c in ch)
        obs = sum(c["exceeded"] for c in ch)
        wr = np.array([len(r["wrong"]) for r in R])
        lost = np.array([r["wrong_interesting"] / max(r["interesting"], 1) for r in R])
        summary[row] = dict(n=len(R), measured=[float(meas.mean()), float(meas.std(ddof=1)) if len(R) > 1 else 0.0],
                            no_claim=float(nc.mean()), checks=len(ch), allowed=allowed, observed=int(obs),
                            wrong=float(wr.mean()), lost_interesting=float(lost.mean()),
                            mean_seconds=float(np.mean([r["seconds"] for r in R])))
        lines.append(f"| {row} | {len(R)} | {meas.mean():.0f} ± {summary[row]['measured'][1]:.0f} | {nc.mean():.0f} | {len(ch)} | "
                     f"{allowed:.1f} | {obs} | {obs / max(allowed, 1e-9):.2f} | {wr.mean():.0f} | {100 * lost.mean():.0f} % |")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1))
    (OUT / "TABLE.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--rows", default=",".join(ROWS))
    r.add_argument("--seeds", default="0-99")
    sub.add_parser("report")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        run(a.rows.split(","), _seeds(a.seeds))
    else:
        report()


if __name__ == "__main__":
    main()
