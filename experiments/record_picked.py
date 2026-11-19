"""
Observed exceedances against the picked failure probability.

For every certified level of every recorded campaign, the rule chose k,
the largest number of calibration failures whose worst-case exceedance
probability F(k) does not exceed the nominal delta. F(k) is the picked
level delta_L: the guarantee actually made on that level is
P(R > eps) <= delta_L <= delta. This script recomputes delta_L from the
record (eps, m, N, k, tail) and compares the observed exceedances with
the number the picked levels allow (the sum of delta_L over checks).

For the union-bound statement of the per-claim form, delta_L is the sum
of the per-claim picked levels. Checks on which the budget cannot be
exceeded (covering every coverable site leaves the rate at or below
eps) are reported separately.

    python -m experiments.record_picked
"""
from __future__ import annotations

import json

import numpy as np

from accountable.campaign import INTEREST, INTERP
from accountable.tails import worst_case_tail
from experiments.record import OUT, PAPER_ROWS, load_row


def poisson_binomial_sf(p, k):
    """P(sum of independent Bernoulli(p_i) >= k)."""
    dist = np.zeros(len(p) + 1)
    dist[0] = 1.0
    for q in p:
        dist[1:] = dist[1:] * (1 - q) + dist[:-1] * q
        dist[0] *= (1 - q)
    return float(dist[k:].sum())


def row_checks(row):
    recs = load_row(row)
    z = np.load(OUT / row / "sites.npz")
    seeds = list(z["seeds"])
    levels = z["levels"]
    out = []
    for r in recs:
        i = seeds.index(r["seed"])
        cfg = r["config"]
        tail = cfg["policy"].get("tail", "binomial")
        names = [c["name"] for c in cfg["certificates"]]
        caps = {c["name"]: c["cap"] for c in cfg["certificates"]}
        lab = {INTERP: z["fail_prior"][i].astype(bool), INTEREST: z["interesting"][i].astype(bool)}
        for lv in r["per_level"]:
            if lv.get("empty"):
                continue
            idx = np.flatnonzero(levels == lv["L"])
            N, m = lv["n_level"], lv["n_cal"]
            sc = {nm: z[f"score_{nm}"][i][idx].astype(float) for nm in names}
            cov_all = {nm: np.isfinite(sc[nm]) & ((sc[nm] < caps[nm]) if caps[nm] is not None else True)
                       for nm in names}
            bad = {nm: lab[nm][idx] for nm in names}
            rmax = {f"R_{nm}": float(np.mean(cov_all[nm] & bad[nm])) for nm in names}
            rmax["R_E"] = float(np.mean(np.any([cov_all[nm] & bad[nm] for nm in names], axis=0)))
            per_claim = {}
            for g in lv["guarantees"]:
                ev, b = g["event"], g["budget"]
                if ev != "R_E" or len(lv["guarantees"]) == 1:
                    nm = ev[2:] if ev != "R_E" else names[0]
                    k = lv["certificates"][nm]["k"]
                    dl = worst_case_tail(k, b, m, N, tail)
                    per_claim[ev] = dl
            for g in lv["guarantees"]:
                ev, b = g["event"], g["budget"]
                if ev in per_claim:
                    dl = per_claim[ev]
                else:  # union-bound statement of the per-claim form
                    dl = float(sum(v for e, v in per_claim.items() if e != "R_E"))
                rate = lv["level"]["E_rate"] if ev == "R_E" else lv["certificates"][ev[2:]]["level_joint"]
                out.append(dict(row=row, seed=r["seed"], L=lv["L"], event=ev, budget=b,
                                nominal=1 - g["confidence"], picked=dl, exceeded=bool(rate > b + 1e-12),
                                reachable=bool(rmax[ev] > b + 1e-12)))
    return out


def main():
    allc = []
    for row in PAPER_ROWS:
        if (OUT / row / "runs.jsonl.gz").exists():
            allc += row_checks(row)
    (OUT / "PICKED.json").write_text(json.dumps(allc))
    lines = ["| Configuration | Event | Nominal δ | Checks | Mean picked δ_L | Allowed exceedances (Σ δ_L) | Observed | Observed / allowed | P(≥ observed) under δ_L | Reachable checks | Allowed on reachable | Observed on reachable |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for row in PAPER_ROWS:
        rs = [c for c in allc if c["row"] == row]
        for ev in ("R_E", "R_interest", "R_interp"):
            cs = [c for c in rs if c["event"] == ev]
            if not cs:
                continue
            p = np.array([c["picked"] for c in cs])
            x = int(sum(c["exceeded"] for c in cs))
            reach = [c for c in cs if c["reachable"]]
            pr = np.array([c["picked"] for c in reach])
            xr = int(sum(c["exceeded"] for c in reach))
            lines.append(
                f"| {row} | {ev} | {cs[0]['nominal']:.3f} | {len(cs)} | {p.mean():.3f} | {p.sum():.1f} | {x} | "
                f"{(x / p.sum()) if p.sum() > 0 else float('nan'):.2f} | {poisson_binomial_sf(p, x):.3f} | "
                f"{len(reach)} | {pr.sum():.1f} | {xr} |")
    (OUT / "PICKED.md").write_text(
        "# Observed exceedances against the picked failure probability\n\n"
        "δ_L is the worst-case failure probability at the number of allowed calibration failures the rule picked on each level "
        "(the attainable level at or below the nominal δ). 'Allowed exceedances' is the sum of δ_L over all level checks; "
        "the p-value treats checks as independent (indicative). 'Reachable' checks are those on which covering every coverable site "
        "would exceed the budget.\n\n" + "\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
