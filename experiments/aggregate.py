"""
Summarise the study: seed-0 table and, for replicated rows, how often each
stated rate exceeded its budget on the level population.

    python -m experiments.aggregate > runs/study/summary.md
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from accountable.tails import clopper_pearson

ROOT = Path("runs/study")


def _rows(path):
    return [json.loads(p.read_text()) for p in sorted(path.glob("*.json"))]


def seed0_table():
    out = ["| Row | Measured | Skipped | Statement on R_E | Remainder R_E by level |",
           "| --- | --- | --- | --- | --- |"]
    for r in _rows(ROOT):
        g = r.get("guarantee_RE")
        if g is None and len(r.get("guarantees", [])) == 1:
            g = r["guarantees"][0]  # one certificate: its rate is R_E
        stmt = f"≤ {g['budget']:.2f} at {g['confidence']:.2f}" if g else "none"
        out.append(f"| {r['name']} | {r['n_measured']} / {r['n_design']} | {r['n_skipped']} | {stmt} | "
                   + ", ".join(f"{x:.3f}" for x in r["rem_E"]) + " |")
    return "\n".join(out)


def replication_table():
    rep = ROOT / "rep"
    if not rep.exists():
        return ""
    by = defaultdict(list)
    for r in _rows(rep):
        by[r["name"]].append(r)
    out = ["| Row | Seeds | Mean measured | Event | Budget | Nominal failure | Exceedances / trials | 95% interval |",
           "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for name, rs in sorted(by.items()):
        meas = np.mean([r["n_measured"] for r in rs])
        g = rs[0]["guarantees"]
        checks = []
        for st in g:
            ev = st["event"]
            if ev == "R_E":
                vals = [x for r in rs for x in r["level_E"]]
            else:
                nm = ev.split("_", 1)[1]
                vals = [x for r in rs for x in r["level_cert"][nm]]
            checks.append((ev, st["budget"], 1 - st["confidence"], vals))
        if not g:  # legacy: the statement the original run intended
            checks.append(("R_E (intended)", 0.10, 0.25, [x for r in rs for x in r["level_E"]]))
        for ev, b, fail, vals in checks:
            k = int(np.sum(np.asarray(vals) > b + 1e-12))
            lo, hi = clopper_pearson(k, len(vals), 0.95)
            out.append(f"| {name} | {len(rs)} | {meas:.0f} | {ev} | {b:.2f} | {fail:.2f} | "
                       f"{k}/{len(vals)} | {lo:.3f}–{hi:.3f} |")
    return "\n".join(out)


if __name__ == "__main__":
    print("## Seed 0\n")
    print(seed0_table())
    print("\n## Replication over calibration seeds (level rates)\n")
    print(replication_table())
