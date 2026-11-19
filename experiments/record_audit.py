"""
Confidence audit from the run record.

For every row, a subset of recorded seeds and every certified level, the
level population is rebuilt from the record (frozen scores, interest and
interpolation labels, caps, policy) and the calibration draw is repeated.
Reported per guarantee: nominal failure probability, the exact
finite-population worst case at the k used, the largest attainable rate,
and the attained exceedance probability.

    python -m experiments.record_audit --seeds 20 --draws 1000
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import hypergeom

from accountable import make_policy
from accountable.campaign import INTEREST, INTERP
from accountable.policies import LevelData
from accountable.tails import allowed_k
from experiments.record import OUT, PAPER_ROWS, load_row


def _policy(cfg):
    p = dict(cfg["policy"])
    return make_policy(p.pop("policy"), **p)


def audit_row(row, n_seeds, draws, seed0=12345):
    recs = load_row(row)[:n_seeds]
    z = np.load(OUT / row / "sites.npz")
    seeds = list(z["seeds"])
    levels = z["levels"]
    out = []
    for r in recs:
        i = seeds.index(r["seed"])
        cfg = r["config"]
        pol = _policy(cfg)
        names = [c["name"] for c in cfg["certificates"]]
        caps = {c["name"]: c["cap"] for c in cfg["certificates"]}
        lab = {INTERP: z["fail_prior"][i].astype(bool), INTEREST: z["interesting"][i].astype(bool)}
        rng = np.random.default_rng(seed0 + r["seed"])
        for lv in r["per_level"]:
            if lv.get("empty"):
                continue
            L = lv["L"]
            idx = np.flatnonzero(levels == L)
            N, m = len(idx), lv["n_cal"]
            sc = {nm: z[f"score_{nm}"][i][idx].astype(float) for nm in names}
            bad = {nm: lab[nm][idx] for nm in names}
            allc = {nm: np.isfinite(sc[nm]) & ((sc[nm] < caps[nm]) if caps[nm] is not None else True) for nm in names}

            def rates(cov):
                d = {f"R_{nm}": float(np.mean(cov[nm] & bad[nm])) for nm in names}
                d["R_E"] = float(np.mean(np.any([cov[nm] & bad[nm] for nm in names], axis=0)))
                return d

            rmax = rates(allc)
            st = {}
            for _ in range(draws):
                cal = np.sort(rng.choice(N, m, replace=False))
                d = pol.decide(LevelData(N, sc, cal, {nm: bad[nm][cal] for nm in names}, caps=caps))
                rr = rates(d.covers)
                for g in d.guarantees:
                    s = st.setdefault(g.event, [g.budget, g.confidence, 0, 0])
                    s[2] += rr[g.event] > g.budget + 1e-12
                    s[3] += 1
            joint = len(st) > 1
            for ev, (b, conf, ex, n) in st.items():
                wc = k = None
                if not (joint and ev == "R_E"):
                    k = allowed_k(b, m, 1 - conf, N=N, tail=getattr(pol, "tail", "binomial")).k
                    wc = float(hypergeom.cdf(k, N, int(np.floor(b * N)) + 1, m)) if k >= 0 else 0.0
                out.append(dict(row=row, seed=r["seed"], L=L, N=N, m=m, event=ev, budget=b,
                                nominal=1 - conf, k=k, worst_case=wc, rate_max=rmax[ev],
                                attained=ex / n, draws=n))
    return out


def table(rows):
    by = defaultdict(list)
    for r in rows:
        by[(r["row"], r["event"], r["L"])].append(r)
    lines = ["| Row | Event | Level | Sites | k | Nominal | Worst case | Largest attainable rate (mean) | Attained (mean over seeds) |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for (row, ev, L), rs in sorted(by.items(), key=lambda x: (PAPER_ROWS.index(x[0][0]) if x[0][0] in PAPER_ROWS else 99, x[0][1], x[0][2])):
        a = np.array([r["attained"] for r in rs])
        wc = rs[0]["worst_case"]
        lines.append(f"| {row} | {ev} | L{L} | {rs[0]['N']} | {rs[0]['k'] if rs[0]['k'] is not None else '–'} | "
                     f"{rs[0]['nominal']:.3f} | {('%.3f' % wc) if wc is not None else '–'} | "
                     f"{np.mean([r['rate_max'] for r in rs]):.3f} | {a.mean():.3f} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", default=",".join(PAPER_ROWS))
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--draws", type=int, default=1000)
    a = ap.parse_args()
    rows = []
    for row in a.rows.split(","):
        if (OUT / row / "sites.npz").exists():
            rows += audit_row(row, a.seeds, a.draws)
            print(row, "audited", flush=True)
    (OUT / "AUDIT.json").write_text(json.dumps(rows, indent=1))
    (OUT / "AUDIT.md").write_text(
        f"# Confidence audit from the run record\n\nFirst {a.seeds} recorded seeds per row, {a.draws} calibration redraws per level.\n\n"
        + table(rows) + "\n")


if __name__ == "__main__":
    main()
