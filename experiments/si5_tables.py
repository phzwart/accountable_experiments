"""
Regenerate Tables S5.1–S5.3 of SI 5 from the run record and splice them into the manuscript.

    python -m experiments.si5_tables
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from experiments.record import OUT, PAPER_ROWS

SI5 = Path("manuscript/supplement_SI5.md")


def md_table(path):
    return [l for l in Path(path).read_text().splitlines() if l.startswith("|")]


def table_s52():
    A = json.loads((OUT / "AUDIT.json").read_text())
    g = defaultdict(list)
    for r in A:
        if "separate" in r["row"] and r["event"] == "R_E":
            continue
        g[(r["row"], r["event"])].append(r)
    old = list(dict.fromkeys((r["row"], r["event"]) for r in A if (r["row"], r["event"]) in g and r["row"] in PAPER_ROWS))
    order = sorted(old, key=lambda k: (PAPER_ROWS.index(k[0]), old.index(k)))
    lines = ["| Configuration | Event | Levels audited | Mean worst case | Mean attained | Attained / worst case | Levels where the budget cannot be exceeded |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for key in order:
        rs = [r for r in g[key] if r["worst_case"] is not None]
        if not rs:
            continue
        ex = [r for r in rs if r["rate_max"] > r["budget"]]
        wc = sum(r["worst_case"] for r in ex)
        ratio = f"{sum(r['attained'] for r in ex) / wc:.2f}" if ex and wc > 0 else "–"
        mw = sum(r["worst_case"] for r in rs) / len(rs)
        ma = sum(r["attained"] for r in rs) / len(rs)
        lines.append(f"| {key[0]} | {key[1]} | {len(rs)} | {mw:.3f} | {ma:.3f} | {ratio} | {len(rs) - len(ex)} of {len(rs)} |")
    return lines


def splice(text, caption, new):
    lines = text.splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith(caption))
    j = next(k for k in range(i + 1, len(lines)) if lines[k].startswith("|"))
    e = j
    while e < len(lines) and lines[e].startswith("|"):
        e += 1
    return "\n".join(lines[:j] + new + lines[e:]) + "\n"


def main():
    t = SI5.read_text()
    t = splice(t, "**Table S5.1.**", md_table(OUT / "SUMMARY.md"))
    t = splice(t, "**Table S5.2.**", table_s52())
    t = splice(t, "**Table S5.3.**", md_table(OUT / "PICKED.md"))
    SI5.write_text(t)


if __name__ == "__main__":
    main()
