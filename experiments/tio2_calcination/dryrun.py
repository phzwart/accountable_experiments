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
    # few-days pilot: furnace runs as units (furnace.py)
    "runs128_size": dict(unit="run", target="size"),
    "runs128_pattern": dict(unit="run", target="pattern"),
    "runs128_size_random": dict(unit="run", target="size", score="random"),
    "runs64_size": dict(unit="run", target="size", blocks=(8, 8, 16, 32)),
    "runs64_pattern": dict(unit="run", target="pattern", blocks=(8, 8, 16, 32)),
    # same pilot on forward model v2 (literature-anchored kinetics, realistic XRD)
    "v2_runs128_size": dict(unit="run", target="size", model="v2"),
    "v2_runs128_pattern": dict(unit="run", target="pattern", model="v2", rtol=0.25, atol_sigma=4.0),
    "v2_runs128_size_random": dict(unit="run", target="size", score="random", model="v2"),
    "v2_runs64_size": dict(unit="run", target="size", blocks=(8, 8, 16, 32), model="v2"),
}


def _seeds(s):
    a, b = s.split("-") if "-" in s else (s, s)
    return range(int(a), int(b) + 1)


def one(row: str, seed: int) -> dict:
    kw = dict(ROWS[row])
    furnace = kw.pop("furnace", "per_sample")
    unit = kw.pop("unit", "recipe")
    t0 = time.time()
    if unit == "run":
        from . import furnace as FU
        ds = FU.load(truth_seed=0, blocks_=tuple(kw.pop("blocks", FU.BLOCKS)), model=kw.pop("model", "v1"))
        res = run_campaign(ds, FU.config(ds, seed=seed, **kw))
    else:
        ds = A.load(truth_seed=0, furnace=furnace)
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
    sched = {}
    if unit == "run":
        for nf in (4, 8):
            for pipe in (False, True):
                for slow in (True, False):
                    sched[f"f{nf}_{'pipe' if pipe else 'seq'}_{'slow' if slow else 'fast'}"] = round(
                        FU.schedule(res, ds, nf, pipe, slow)[0], 1)
    return dict(row=row, seed=seed, seconds=round(time.time() - t0, 1), n_measured=res.n_measured, schedule=sched,
                n_sites=int(ds.n),
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
    lines = ["| Row | Campaigns | Measured (mean ± s.d.) of 1024 | No claim | Level checks | Allowed (Σ δ_L) | Observed | Obs / allowed | P(≥ obs) | Wrong skips | Interesting sites lost |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for row in ROWS:
        files = sorted((RUNS / row).glob("s*.json"))
        if not files or "runs" in row:
            continue
        R = [json.loads(f.read_text()) for f in files]
        meas = np.array([r["n_measured"] for r in R])
        nc = np.array([len(r["measured_nc"]) for r in R])
        ch = [c for r in R for c in r["checks"]]
        allowed = sum(c["picked"] for c in ch)
        obs = sum(c["exceeded"] for c in ch)
        wr = np.array([len(r["wrong"]) for r in R])
        lost = np.array([r["wrong_interesting"] / max(r["interesting"], 1) for r in R])
        from experiments.record_picked import poisson_binomial_sf
        pval = float(poisson_binomial_sf(np.array([c["picked"] for c in ch]), int(obs)))
        summary[row] = dict(n=len(R), measured=[float(meas.mean()), float(meas.std(ddof=1)) if len(R) > 1 else 0.0],
                            no_claim=float(nc.mean()), checks=len(ch), allowed=allowed, observed=int(obs),
                            wrong=float(wr.mean()), lost_interesting=float(lost.mean()), p_value=pval,
                            mean_seconds=float(np.mean([r["seconds"] for r in R])))
        lines.append(f"| {row} | {len(R)} | {meas.mean():.0f} ± {summary[row]['measured'][1]:.0f} | {nc.mean():.0f} | {len(ch)} | "
                     f"{allowed:.1f} | {obs} | {obs / max(allowed, 1e-9):.2f} | {pval:.2f} | {wr.mean():.0f} | {100 * lost.mean():.0f} % |")
    # furnace-run pilot rows
    lines += ["", "| Row | Model | Campaigns | Runs measured (of design) | Exceedances / allowed | P(≥ obs) | Runs with a mixed-phase crucible lost | Days, 4 furnaces (seq, slow ramp) | Days, 8 furnaces (pipelined, fast ramp) |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    from experiments.record_picked import poisson_binomial_sf
    for row in ROWS:
        files = sorted((RUNS / row).glob("s*.json"))
        if not files or "runs" not in row:
            continue
        R = [json.loads(f.read_text()) for f in files]
        meas = np.array([r["n_measured"] for r in R])
        ch = [c for r in R for c in r["checks"]]
        allowed = sum(c["picked"] for c in ch)
        obs = int(sum(c["exceeded"] for c in ch))
        pval = float(poisson_binomial_sf(np.array([c["picked"] for c in ch]), obs))
        lost = np.array([r["wrong_interesting"] / max(r["interesting"], 1) for r in R])
        d4 = np.array([r["schedule"]["f4_seq_slow"] for r in R]) / 24
        d8 = np.array([r["schedule"]["f8_pipe_fast"] for r in R]) / 24
        summary[row] = dict(n=len(R), n_sites=R[0]["n_sites"], measured=[float(meas.mean()), float(meas.std(ddof=1))],
                            checks=len(ch), allowed=allowed, observed=obs, p_value=pval, lost_interesting=float(lost.mean()),
                            days={k: float(np.mean([r["schedule"][k] for r in R]) / 24) for k in R[0]["schedule"]})
        model = "v2" if row.startswith("v2_") else "v1"
        lines.append(f"| {row} | {model} | {len(R)} | {meas.mean():.0f} ± {meas.std(ddof=1):.0f} of {R[0]['n_sites']} | {obs} / {allowed:.1f} | {pval:.2f} | "
                     f"{100 * lost.mean():.0f} % | {d4.mean():.1f} ± {d4.std(ddof=1):.1f} | {d8.mean():.1f} ± {d8.std(ddof=1):.1f} |")
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
