"""
Figure 3: forms of guarantee. Measurements spent and level wrong-skip rates
for three forms on three datasets (20 calibration seeds), and the Monte
Carlo check of the sequential rule against the two single-budget paths.

    python manuscript/figures/fig_forms.py
"""
import collections
import glob
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from accountable.policies import (LegacySequentialPolicy, LevelData, NestedPathPolicy,
                                  PriorityPathPolicy)

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
COL = {"separate": "#2a78d6", "nested": "#eb6834", "priority": "#1baf7a", "legacy": "#8a8984"}
LAB = {"separate": "Per-claim\nbudgets", "nested": "Quantile\npath", "priority": "Priority\npath"}

DATASETS = [
    ("IR map", "ir_{}", {"separate": "separate_split_watson", "nested": "nested_watson", "priority": "priority_watson"}, 959, 0.10, 0.25),
    ("NaCl scan", "nacl_fwhm_{}", {"separate": "separate_watson", "nested": "nested_watson", "priority": "priority_watson"}, 1071, 0.20, 0.20),
    # synthetic map: one claim from round 3, so the three forms coincide; not shown
]


def load():
    """Per-row run lists from the run record (results/record)."""
    import gzip
    by = collections.defaultdict(list)
    for f in glob.glob(str(ROOT / "results/record/*/runs.jsonl.gz")):
        with gzip.open(f, "rt") as fh:
            for line in fh:
                r = json.loads(line)
                by[r["row"]].append(dict(n_measured=r["summary"]["n_measured"], level_E=r["study"]["level_E"]))
    return by


def mc_sequential(T=4000):
    N = 399
    rng = np.random.default_rng(7)
    sa, sb = rng.random(N) * 0.09, rng.random(N)
    Z, F = rng.random(N) < 0.5, rng.random(N) < 0.1
    pols = {"legacy": LegacySequentialPolicy(0.10, 0.25),
            "nested": NestedPathPolicy(0.10, 0.75),
            "priority": PriorityPathPolicy(0.10, 0.75, order=["interest", "interp"])}
    out = {}
    for key, pol in pols.items():
        r = np.random.default_rng(0)
        ex = 0
        for _ in range(T):
            cal = np.sort(r.choice(N, 40, replace=False))
            d = pol.decide(LevelData(N, {"interest": sa, "interp": sb}, cal,
                                     {"interest": Z[cal], "interp": F[cal]}, caps={"interest": 0.1}))
            ex += (((d.covers["interest"] & Z) | (d.covers["interp"] & F)).mean() > 0.10)
        out[key] = int(ex)
    return out, T


def style(ax):
    ax.set_facecolor(SURF)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
        ax.spines[s].set_linewidth(0.8)
    ax.tick_params(colors=INK2, labelsize=8, width=0.8)
    ax.yaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def main():
    by = load()
    mc, T = mc_sequential()
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
    fig = plt.figure(figsize=(10.0, 5.2), facecolor=SURF, constrained_layout=True)
    gs = fig.add_gridspec(2, 4, width_ratios=[1, 1, 1, 0.9])
    forms = ["separate", "nested", "priority"]
    x = np.arange(3)
    for j, (title, pat, rows, n_design, eps, fail) in enumerate(DATASETS):
        a = fig.add_subplot(gs[0, j]); style(a)
        b = fig.add_subplot(gs[1, j]); style(b)
        exc = []
        for i, f in enumerate(forms):
            rs = by[pat.format(rows[f])]
            meas = np.array([r["n_measured"] for r in rs])
            a.bar(i, meas.mean(), width=0.62, color=COL[f], zorder=2)
            a.errorbar(i, meas.mean(), yerr=meas.std(ddof=1), color=INK, lw=0.9, capsize=3, zorder=3)
            a.text(i, meas.mean() + meas.std(ddof=1) + n_design * 0.03, f"{meas.mean():.0f}",
                   ha="center", va="bottom", color=INK, fontsize=8)
            E = np.array([v for r in rs for v in r["level_E"] if np.isfinite(v)])
            jit = np.random.default_rng(i + 10 * j).uniform(-0.2, 0.2, len(E))
            b.scatter(i + jit, E, s=3, color=COL[f], alpha=0.5, linewidths=0, zorder=2)
            k = int(np.sum(E > eps + 1e-12))
            exc.append(f"{k}/{len(E)}")
        a.axhline(n_design, color=INK2, lw=0.9, ls=(0, (4, 3)), zorder=1)
        a.text(2.45, n_design, f"design {n_design}", ha="right", va="bottom", color=INK2, fontsize=7.5)
        a.set_ylim(0, n_design * 1.18)
        a.set_xticks(x, [LAB[f] for f in forms])
        a.set_title(f"{title}\n$R_E \\leq {eps:.2f}$ at confidence {1 - fail:.2f}", color=INK, fontsize=9)
        if j == 0:
            a.set_ylabel("Sites measured (mean ± s.d.)", color=INK)
            b.set_ylabel("Wrong-skip rate on a level", color=INK)
        b.axhline(eps, color=INK, lw=1.0, zorder=1)
        b.text(-0.45, eps, " budget", ha="left", va="bottom", color=INK, fontsize=7.5)
        b.set_ylim(-0.01, eps * 1.65)
        b.set_xlim(-0.55, 2.55)
        b.set_xticks(x, [f"{LAB[f]}\n{e}" for f, e in zip(forms, exc)], fontsize=7)
    c = fig.add_subplot(gs[:, 3]); style(c)
    keys = ["legacy", "nested", "priority"]
    labs = ["Sequential\nrule", "Quantile\npath", "Priority\npath"]
    se = np.sqrt(0.25 * 0.75 / T)
    for i, kk in enumerate(keys):
        c.bar(i, mc[kk] / T, width=0.62, color=COL[kk], zorder=2)
        c.text(i, mc[kk] / T + 0.008, f"{mc[kk]}/{T}", ha="center", va="bottom", color=INK, fontsize=7)
    c.axhline(0.25, color=INK, lw=1.0)
    c.axhspan(0.25 - 2 * se, 0.25 + 2 * se, color=GRID, zorder=0)
    c.text(2.45, 0.252, "allowed 0.25", ha="right", va="bottom", color=INK, fontsize=7.5)
    c.set_ylim(0, 0.36)
    c.set_xticks(range(3), labs)
    c.set_ylabel("Fraction of draws with $R_E > 0.10$", color=INK)
    c.set_title(f"Uninformative population\n{T} calibration draws", color=INK, fontsize=9)
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"fig3_forms.{ext}", dpi=250, facecolor=SURF)
    print(mc, T)


if __name__ == "__main__":
    main()
