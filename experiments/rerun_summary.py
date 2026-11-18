"""Summarise runs/rerun: mean measured and bound exceedances per row."""
import collections
import glob
import json

import numpy as np

from accountable.tails import clopper_pearson

by = collections.defaultdict(list)
for f in glob.glob("runs/rerun/*/s*.json"):
    r = json.load(open(f))
    by[r["name"]].append(r)
print("| Row | Seeds | Measured (mean ± sd) | Design | Statement | Exceedances / trials |")
print("| --- | --- | --- | --- | --- | --- |")
for n, rs in sorted(by.items()):
    g = rs[0]["guarantees"]
    st = next((x for x in g if x["event"] == "R_E"), g[0])
    if st["event"] == "R_E":
        vals = [v for r in rs for v in r["level_E"]]
    else:
        nm = st["event"].split("_", 1)[1]
        vals = [v for r in rs for v in r["level_cert"][nm]]
    k = int(sum(v > st["budget"] + 1e-12 for v in vals))
    m = [r["n_measured"] for r in rs]
    print(f"| {n} | {len(rs)} | {np.mean(m):.0f} ± {np.std(m):.0f} | {rs[0]['n_design']} | "
          f"{st['event']} ≤ {st['budget']:.2f} at {st['confidence']:.2f} | {k}/{len(vals)} |")
