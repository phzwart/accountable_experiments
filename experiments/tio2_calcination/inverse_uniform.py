"""
Kinetic recovery from accountable-campaign runs versus uniform runs at matched budgets.

    python -m experiments.tio2_calcination.inverse_uniform

Arms (truth seed 0, forward model v2, same analysis pipeline and starting point as inverse.py):
  campaign      runs measured by the size-claim campaign, calibration seeds 0-4 (44-50 runs)
  random-sub    uniformly random subsets of the 64-run Sobol design, 47 runs (10 draws)
  iid-uniform   fresh designs of iid uniform (temperature, dwell) runs, 47 runs (6 designs)
  full design   all 64 Sobol runs
  seed levels   the 16 seed runs; random-sub-16: random 16 of the 64 (10 draws); iid-uniform-16 (6 designs)
Metrics per fit: error and cluster-robust s.e. of the four activation energies, and the error of the
temperature for 50 % rutile over the design's dwell range (1-4 h, native powder, no alumina).
"""
from __future__ import annotations

import json

import numpy as np

from accountable import run_campaign

from . import forward_v2 as V
from . import furnace as FU
from . import inverse as INV

OUT = INV.OUT
EIDX = (1, 3, 6, 8)
DWELL = 2.0 ** np.linspace(0, 2, 9)
TG = np.linspace(500, 1000, 251)


def uniform_world(n_runs, design_seed, truth_seed=0):
    """Recipes, run index and patterns for an iid uniform design in (temperature, dwell)."""
    v = np.random.default_rng(1000 + design_seed).random((n_runs, 2))
    run_id = np.repeat(np.arange(n_runs), FU.N_SLOTS)
    u = np.zeros((n_runs * FU.N_SLOTS, 4))
    for i in range(n_runs):
        for j, (c, b) in enumerate(FU.TRAY_V2):
            u[i * FU.N_SLOTS + j] = [v[i, 0], v[i, 1] * FU.DWELL_MAX_LOG2 / 4.0, c / 0.10, b / 0.5]
    slot = np.tile(np.arange(FU.N_SLOTS), n_runs)
    I, _ = V.realise(u, seed=truth_seed + 7919 * (design_seed + 1), furnace_key=run_id, slot=slot)
    rec = V.recipe(u)
    rec["run"] = run_id
    return rec, I


def t50(theta, c=0.0):
    p = INV.params_of(theta)
    TT, DD = np.meshgrid(TG, DWELL)
    rec = dict(T=TT.ravel(), t=DD.ravel(), c=np.full(TT.size, c), s=np.zeros(TT.size), b=np.zeros(TT.size))
    w = INV.predict(p, rec)[0].reshape(TT.shape)
    out = np.full(len(DWELL), np.nan)
    for k, row in enumerate(w):
        j = np.flatnonzero(row >= 0.5)
        if len(j) and j[0] > 0:
            out[k] = np.interp(0.5, row[j[0] - 1:j[0] + 1], TG[j[0] - 1:j[0] + 1])
    return out


def summarise(f, truth, t50_true):
    th = f["theta"]
    return dict(E=[float(th[k]) for k in EIDX], E_err=[float(th[k] - truth[k]) for k in EIDX],
                E_se=[float(f["se"][k]) for k in EIDX], z=((th - truth) / np.maximum(f["se"], 1e-12)).tolist(),
                t50_err=float(np.nanmax(np.abs(t50(th) - t50_true))), theta=th.tolist(), se=f["se"].tolist())


def main():
    truth = INV.theta_of(V.P)
    t50_true = t50(truth)
    th0 = truth + np.array([1.5, -60, -1.5, 60, 0.5, 1.0, -50, -1.0, 50, 0.0])
    th0[9] = 2.0
    ds = FU.load(blocks_=(8, 8, 16, 32), model="v2")
    sigma = FU.noise_sigma(ds)
    rec_all, I_all, _ = INV.crucibles(ds, np.arange(ds.n))
    obs_all = INV.observables(I_all, sigma)
    out = dict(arms={}, t50_true=t50_true.tolist(), dwell=DWELL.tolist())

    def fit_runs(runs):
        sel = (np.asarray(runs)[:, None] * FU.N_SLOTS + np.arange(FU.N_SLOTS)[None, :]).ravel()
        return INV.fit({k: v[sel] for k, v in rec_all.items()}, tuple(o[sel] for o in obs_all), th0)

    def record(arm, label, n, f):
        r = summarise(f, truth, t50_true)
        r.update(label=label, runs=int(n))
        out["arms"].setdefault(arm, []).append(r)
        print(f"{arm:16s} {label:12s} {n:3d} runs  dE", " ".join(f"{e:+6.0f}±{s:<3.0f}" for e, s in zip(r["E_err"], r["E_se"])),
              f"| T50 err ≤ {r['t50_err']:.1f} °C", flush=True)
        (OUT / "uniform.json").write_text(json.dumps(out, indent=1))

    record("full design", "sobol", ds.n, fit_runs(np.arange(ds.n)))
    for s in range(5):
        res = run_campaign(ds, FU.config(ds, target="size", seed=s))
        runs = np.flatnonzero(res.measured)
        record("campaign", f"seed {s}", len(runs), fit_runs(runs))
    rng = np.random.default_rng(2024)
    for d in range(10):
        record("random-sub", f"draw {d}", 47, fit_runs(np.sort(rng.choice(ds.n, 47, replace=False))))
    record("seed levels", "sobol", 16, fit_runs(np.flatnonzero(ds.levels <= 1)))
    for d in range(10):
        record("random-sub-16", f"draw {d}", 16, fit_runs(np.sort(rng.choice(ds.n, 16, replace=False))))
    for n, arm in ((47, "iid-uniform"), (16, "iid-uniform-16")):
        for d in range(6):
            rec, I = uniform_world(n, d)
            f = INV.fit(rec, INV.observables(I, sigma), th0)
            record(arm, f"design {d}", n, f)
    return out


if __name__ == "__main__":
    main()
