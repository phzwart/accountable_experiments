"""
What the measured runs of an accountable campaign still teach: kinetic recovery across synthetic worlds.

    python -m experiments.tio2_calcination.kinetics_worlds --worlds 0-19 [--part 0 --parts 2]
    python -m experiments.tio2_calcination.kinetics_worlds --report

Per world (truth seed; forward model v2; 64-run nested Sobol design, levels 8/8/16/32; same
fitting pipeline and starting point as inverse.py), paired arms:
  full        all 64 runs
  size        runs measured by the size-claim campaign (calibration seed = world)
  pattern     runs measured by the pattern-claim campaign (same seed)
  random      a uniformly random subset of the 64 runs, of the size campaign's size
  oracle      a kinetics-optimal subset of the same size: the seed levels plus runs added greedily
              to maximise the determinant of the Fisher information at the true parameters
              (a design that knows the answer; an upper bound on precision)
Also per world: the D-efficiency of each subset relative to the full design at the truth, and
the audit of both campaigns (level checks, exceedances, wrong skips).
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from accountable import run_campaign
from accountable import INTEREST, INTERP

from . import forward_v2 as V
from . import furnace as FU
from . import inverse as INV
from .inverse_uniform import t50

OUT = Path("results/tio2/kinetics_worlds")
EIDX = (1, 3, 6, 8)
PATTERN = dict(rtol=0.25, atol_sigma=4.0)


def audit(ds, res):
    from accountable.tails import worst_case_tail
    names = [c["name"] for c in res.config["certificates"]]
    tail = res.config["policy"].get("tail", "hypergeometric")
    levels = np.asarray(ds.levels)
    lab = {INTERP: np.asarray(res.fail_prior, bool), INTEREST: np.asarray(res.interesting, bool)}
    checks = []
    for lv in res.per_level:
        if lv.get("empty"):
            continue
        g = [x for x in lv["guarantees"] if x["event"] == "R_E"][0]
        k = lv["certificates"][names[0]]["k"]
        checks.append(dict(L=lv["L"], picked=float(worst_case_tail(k, g["budget"], lv["n_cal"], lv["n_level"], tail)),
                           exceeded=bool(lv["level"]["E_rate"] > g["budget"] + 1e-12)))
    sk = np.asarray(res.skipped, bool)
    reason = np.asarray(res.reason).astype(str)
    cov_int = np.isin(reason, ["not_interesting", "not_interesting+interpolable"])
    cov_itp = np.isin(reason, ["interpolable", "not_interesting+interpolable"])
    wrong = sk & ((cov_int & lab[INTEREST]) | (cov_itp & lab[INTERP]))
    return dict(checks=checks, n_wrong=int(wrong.sum()), n_skipped=int(sk.sum()))


def run_info(rec, obs, theta):
    """Per-run Fisher information J_g^T J_g at theta (residuals scaled as in the fit)."""
    r0 = INV.residuals(theta, rec, obs)
    g = INV.residual_groups(rec, obs)
    steps = np.array([1e-3, 0.3, 1e-3, 0.3, 1e-3, 1e-3, 0.3, 1e-3, 0.3, 0.01])
    J = np.empty((len(r0), len(theta)))
    for k in range(len(theta)):
        t = theta.copy()
        t[k] += steps[k]
        J[:, k] = (INV.residuals(t, rec, obs) - r0) / steps[k]
    runs = np.unique(rec["run"])
    return {int(k): J[g == k].T @ J[g == k] for k in runs}


def logdet(M):
    s, v = np.linalg.slogdet(M + 1e-9 * np.eye(len(M)))
    return v if s > 0 else -np.inf


def d_eff(info, subset, full):
    p = len(next(iter(info.values())))
    A = sum(info[k] for k in subset)
    F = sum(info[k] for k in full)
    return float(np.exp((logdet(A) - logdet(F)) / p))


def greedy_oracle(info, start, n):
    chosen = list(start)
    rest = [k for k in info if k not in chosen]
    A = sum(info[k] for k in chosen)
    while len(chosen) < n:
        best = max(rest, key=lambda k: logdet(A + info[k]))
        chosen.append(best)
        rest.remove(best)
        A = A + info[best]
    return np.array(sorted(chosen))


def one_world(w):
    t0 = time.time()
    truth = INV.theta_of(V.P)
    t50_true = t50(truth)
    th0 = truth + np.array([1.5, -60, -1.5, 60, 0.5, 1.0, -50, -1.0, 50, 0.0])
    th0[9] = 2.0
    ds = FU.load(truth_seed=w, blocks_=(8, 8, 16, 32), model="v2")
    sigma = FU.noise_sigma(ds)
    rec, I, _ = INV.crucibles(ds, np.arange(ds.n))
    obs = INV.observables(I, sigma)
    res_s = run_campaign(ds, FU.config(ds, target="size", seed=w))
    res_p = run_campaign(ds, FU.config(ds, target="pattern", seed=w, **PATTERN))
    size_runs = np.flatnonzero(res_s.measured)
    n = len(size_runs)
    seed_runs = np.flatnonzero(ds.levels <= 1)
    info = run_info(rec, obs, truth)
    arms = {"full": np.arange(ds.n), "size": size_runs, "pattern": np.flatnonzero(res_p.measured),
            "random": np.sort(np.random.default_rng(5000 + w).choice(ds.n, n, replace=False)),
            "oracle": greedy_oracle(info, seed_runs, n), "seed": seed_runs}
    out = dict(world=w, arms={}, audit=dict(size=audit(ds, res_s), pattern=audit(ds, res_p)))
    for name, runs in arms.items():
        sel = (np.asarray(runs)[:, None] * FU.N_SLOTS + np.arange(FU.N_SLOTS)[None, :]).ravel()
        f = INV.fit({k: v[sel] for k, v in rec.items()}, tuple(o[sel] for o in obs), th0)
        th = f["theta"]
        out["arms"][name] = dict(runs=[int(r) for r in runs], n=len(runs), theta=th.tolist(), se=f["se"].tolist(),
                                 z=((th - truth) / np.maximum(f["se"], 1e-12)).tolist(),
                                 t50_err=float(np.nanmax(np.abs(t50(th) - t50_true))),
                                 d_eff=d_eff(info, runs, np.arange(ds.n)))
    # information carried by the runs the size campaign skipped, against random sets of the same size
    skipped = np.setdiff1d(np.arange(ds.n), size_runs)
    rng = np.random.default_rng(9000 + w)
    rand_sets = [rng.choice(ds.n, len(skipped), replace=False) for _ in range(200)]
    tr_full = np.trace(np.linalg.pinv(sum(info.values())))
    def loss(drop):          # relative increase in the summed variance (A-criterion) when runs are dropped
        keep = np.setdiff1d(np.arange(ds.n), drop)
        return float(np.trace(np.linalg.pinv(sum(info[k] for k in keep))) / tr_full - 1)
    out["skipped"] = dict(n=len(skipped), d_eff_without=d_eff(info, size_runs, np.arange(ds.n)),
                          d_eff_without_random=[d_eff(info, np.setdiff1d(np.arange(ds.n), s), np.arange(ds.n))
                                                for s in rand_sets])
    out["seconds"] = time.time() - t0
    return out


def parse(spec):
    a, b = spec.split("-") if "-" in spec else (spec, spec)
    return list(range(int(a), int(b) + 1))


def report():
    R = [json.loads(p.read_text()) for p in sorted(OUT.glob("w*.json"))]
    truth = INV.theta_of(V.P)
    arms = ["full", "size", "pattern", "random", "oracle", "seed"]
    lines = [f"Worlds: {len(R)}", "",
             "| Arm | Runs (mean) | Median s.e. of E (nucl / contact / anat. coars. / rut. coars.) | "
             "s.e. ratio to full (median, 4 E) | RMSE of E over worlds | |z| ≤ 2 (all 10 parameters) | D-efficiency (median) | T50 error, median (°C) |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    summ = {}
    for a in arms:
        n = np.mean([r["arms"][a]["n"] for r in R])
        se = np.array([[r["arms"][a]["se"][k] for k in EIDX] for r in R])
        sef = np.array([[r["arms"]["full"]["se"][k] for k in EIDX] for r in R])
        err = np.array([[r["arms"][a]["theta"][k] - truth[k] for k in EIDX] for r in R])
        z = np.abs(np.array([r["arms"][a]["z"] for r in R]))
        de = np.array([r["arms"][a]["d_eff"] for r in R])
        t5 = np.array([r["arms"][a]["t50_err"] for r in R])
        summ[a] = dict(n=n, se=np.median(se, 0).tolist(), ratio=np.median(se / sef, 0).tolist(),
                       rmse=np.sqrt((err ** 2).mean(0)).tolist(), cover2=float((z <= 2).mean()),
                       d_eff=float(np.median(de)), t50=float(np.median(t5)))
        s = summ[a]
        lines.append(f"| {a} | {n:.1f} | " + " / ".join(f"{v:.0f}" for v in s["se"]) + " | "
                     + " / ".join(f"{v:.2f}" for v in s["ratio"]) + " | " + " / ".join(f"{v:.0f}" for v in s["rmse"])
                     + f" | {100 * s['cover2']:.0f} % | {s['d_eff']:.2f} | {s['t50']:.1f} |")
    # paired: campaign vs random
    rs = np.array([[r["arms"]["size"]["se"][k] / r["arms"]["random"]["se"][k] for k in EIDX] for r in R])
    de_pair = np.array([r["arms"]["size"]["d_eff"] - r["arms"]["random"]["d_eff"] for r in R])
    sk = np.array([r["skipped"]["d_eff_without"] for r in R])
    pct = np.array([np.mean(np.array(r["skipped"]["d_eff_without_random"]) <= r["skipped"]["d_eff_without"]) for r in R])
    lines += ["", f"Paired size campaign / random subset, s.e. ratio median (4 E): "
              + " / ".join(f"{v:.2f}" for v in np.median(rs, 0)),
              f"D-efficiency difference size − random: median {np.median(de_pair):+.3f}, "
              f"size higher in {np.mean(de_pair > 0) * 100:.0f} % of worlds",
              f"Skipped runs: D-efficiency of the measured runs alone, median {np.median(sk):.3f}; "
              f"percentile among random drops of the same size, median {np.median(pct) * 100:.0f}",
              ""]
    for c in ("size", "pattern"):
        ch = [x for r in R for x in r["audit"][c]["checks"]]
        lines.append(f"{c} campaigns: {len(ch)} level checks, allowed {sum(x['picked'] for x in ch):.1f}, "
                     f"observed {sum(x['exceeded'] for x in ch)}; runs measured mean "
                     f"{np.mean([r['arms'][c]['n'] for r in R]):.1f}")
    # overlap between size and pattern measured runs
    jac = [len(set(r["arms"]["size"]["runs"]) & set(r["arms"]["pattern"]["runs"]))
           / len(set(r["arms"]["size"]["runs"]) | set(r["arms"]["pattern"]["runs"])) for r in R]
    lines.append(f"Size/pattern measured-run overlap (Jaccard), median {np.median(jac):.2f}")
    def cert_overlap(a, b):
        out = []
        for r in R:
            cert = set(range(16, 64))
            A_, B_ = set(r["arms"][a]["runs"]) & cert, set(r["arms"][b]["runs"]) & cert
            out.append(len(A_ & B_) / max(len(B_), 1))
        return float(np.median(out))
    lines.append(f"Share of the kinetics-optimal certified-level runs also measured: size {cert_overlap('size', 'oracle'):.2f}, "
                 f"pattern {cert_overlap('pattern', 'oracle'):.2f}, random {cert_overlap('random', 'oracle'):.2f}")
    t5 = {a: np.array([r["arms"][a]["t50_err"] for r in R]) for a in arms}
    lines.append("T50 error 90th percentile: " + ", ".join(f"{a} {np.percentile(t5[a], 90):.1f}" for a in arms))
    win = np.array([[r["arms"]["size"]["se"][k] < r["arms"]["random"]["se"][k] for k in EIDX] for r in R]).mean(0)
    lines.append("Share of worlds with smaller s.e. for size than random (4 E): " + " / ".join(f"{100 * v:.0f} %" for v in win))
    (OUT / "SUMMARY.md").write_text("\n".join(lines) + "\n")
    (OUT / "summary.json").write_text(json.dumps(dict(arms=summ, se_ratio_size_random=np.median(rs, 0).tolist(),
                                                      d_eff_pair=float(np.median(de_pair)),
                                                      skipped_pct=float(np.median(pct)),
                                                      jaccard=float(np.median(jac)), worlds=len(R)), indent=1))
    print("\n".join(lines))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", default="0-19")
    ap.add_argument("--part", type=int, default=0)
    ap.add_argument("--parts", type=int, default=1)
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    if a.report:
        report()
    else:
        OUT.mkdir(parents=True, exist_ok=True)
        for w in parse(a.worlds)[a.part::a.parts]:
            p = OUT / f"w{w:03d}.json"
            if p.exists():
                continue
            r = one_world(w)
            p.write_text(json.dumps(r))
            print(f"world {w}: {r['seconds']:.0f}s", {k: round(v["d_eff"], 2) for k, v in r["arms"].items()}, flush=True)
