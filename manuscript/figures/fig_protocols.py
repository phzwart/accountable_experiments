"""
Figure 4: the cost of one assertion across interpolation protocols
(natural-neighbour and three Gaussian-process length-scale rules), quantile
path, all recorded calibration seeds. Figure S1: GP posterior standard deviation on
one IR level under the three length-scale rules, with the local length
scale of the non-stationary rule.

    python manuscript/figures/fig_protocols.py
"""
import collections
import glob
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
PROTO = ["nn", "gp_mle", "gp_design", "gp_nonstationary"]
COL = {"nn": "#2a78d6", "gp_mle": "#eb6834", "gp_design": "#1baf7a", "gp_nonstationary": "#eda100"}
LAB = {"nn": "Natural\nneighbour", "gp_mle": "GP, max.\nlikelihood", "gp_design": "GP, design\nspacing",
       "gp_nonstationary": "GP, local\nspacing"}
SEQ = LinearSegmentedColormap.from_list("seq", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])

DATASETS = [
    ("IR map, original tolerance", "ir_nested_{}", "ir_nested_watson", 959, 0.10, 0.25),
    ("IR map, tight tolerance", "ir_tight_{}", "ir_tight_sibson", 959, 0.10, 0.25),
    ("NaCl scan", "nacl_fwhm_nested_{}", "nacl_fwhm_nested_watson", 1071, 0.20, 0.20),
    ("Synthetic SAXS", "syn_peak_2cert_nested_{}", "syn_peak_2cert_nested_watson", 2118, 0.20, 0.20),
]


def style(ax, grid=True):
    ax.set_facecolor(SURF)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
        ax.spines[s].set_linewidth(0.8)
    ax.tick_params(colors=INK2, labelsize=7.5, width=0.8)
    if grid:
        ax.yaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


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


def fig4(by):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
    fig, axs = plt.subplots(2, 4, figsize=(13.0, 5.4), facecolor=SURF, constrained_layout=True)
    x = np.arange(len(PROTO))
    for j, (title, pat, nn, n_design, eps, fail) in enumerate(DATASETS):
        a, b = axs[0, j], axs[1, j]
        style(a), style(b)
        exc = []
        for i, p in enumerate(PROTO):
            rs = by[nn if p == "nn" else pat.format(p)]
            meas = np.array([r["n_measured"] for r in rs])
            a.bar(i, meas.mean(), width=0.64, color=COL[p], zorder=2)
            a.errorbar(i, meas.mean(), yerr=meas.std(ddof=1), color=INK, lw=0.9, capsize=3, zorder=3)
            a.text(i, meas.mean() + meas.std(ddof=1) + n_design * 0.03, f"{meas.mean():.0f}",
                   ha="center", va="bottom", color=INK, fontsize=7.5)
            E = np.array([v for r in rs for v in r["level_E"] if np.isfinite(v)])
            jit = np.random.default_rng(i + 10 * j).uniform(-0.22, 0.22, len(E))
            b.scatter(i + jit, E, s=3, color=COL[p], alpha=0.5, linewidths=0, zorder=2)
            k = int(np.sum(E > eps + 1e-12))
            exc.append(f"{k}/{len(E)}")
        a.axhline(n_design, color=INK2, lw=0.9, ls=(0, (4, 3)), zorder=1)
        a.text(3.45, n_design, f"design {n_design}", ha="right", va="bottom", color=INK2, fontsize=7)
        a.set_ylim(0, n_design * 1.18)
        a.set_xticks(x, [LAB[p] for p in PROTO], fontsize=7)
        a.set_title(f"{title}\n$R_E \\leq {eps:.2f}$ at confidence {1 - fail:.2f}", color=INK, fontsize=9)
        b.axhline(eps, color=INK, lw=1.0, zorder=1)
        b.text(-0.5, eps, " budget", ha="left", va="bottom", color=INK, fontsize=7)
        b.set_ylim(-0.01, eps * 1.8)
        b.set_xlim(-0.6, 3.6)
        b.set_xticks(x, [f"{LAB[p]}\n{e}" for p, e in zip(PROTO, exc)], fontsize=6.5)
        if j == 0:
            a.set_ylabel("Sites measured (mean ± s.d.)", color=INK)
            b.set_ylabel("Wrong-skip rate on a level", color=INK)
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"fig4_protocols.{ext}", dpi=250, facecolor=SURF)


def figS1(level=5, seed=0):
    from accountable import run_campaign
    from accountable.gp import GPEngine
    from experiments.ir_bioreef import adapter as A

    ds = A.load()
    res = run_campaign(ds, A.config(ds, policy="nested_path", seed=seed, interp_model="gp_nonstationary"))
    P = ds.points
    prior = res.measured & (ds.levels < level)
    q = np.flatnonzero(ds.levels == level)
    Y = ds.oracle.truth(np.flatnonzero(prior))
    panels = []
    for mode, name in [("mle", "Max. likelihood"), ("design", "Design spacing"), ("nonstationary", "Local spacing")]:
        e = GPEngine(mode=mode, design_points=P, design_levels=ds.levels).fit(P[prior], Y)
        ell = e.info.get("lengthscale", e.info.get("lengthscale_median"))
        panels.append((f"{name}\n$\\ell$ = {ell:.3f}" + (" (median)" if mode == "nonstationary" else ""),
                       e.std(P[q]), "Posterior s.d."))
        if mode == "nonstationary":
            panels.append(("Local length scale\n$\\ell(x)$, local-spacing rule", e._lfun(P[q]), "$\\ell$ (design units)"))
    from experiments._paths import data_root
    z = np.load(data_root() / "IR_data" / "interest_gate_um" / "prepared.npz")
    R, ny, nx = np.asarray(z["points"], float), int(z["ny"]), int(z["nx"])
    um = float(z["scale_um"])                       # design units are micrometres / um
    engines = {}
    panels = []
    for mode, name in [("mle", "Max. likelihood"), ("design", "Design spacing"), ("nonstationary", "Local spacing")]:
        e = GPEngine(mode=mode, design_points=P, design_levels=ds.levels).fit(P[prior], Y)
        engines[mode] = e
        ell = e.info.get("lengthscale", e.info.get("lengthscale_median"))
        lab = "median $\\ell$" if mode == "nonstationary" else "$\\ell$"
        panels.append((f"{name}, {lab} = {ell * um:.1f} µm", e.std(R).reshape(ny, nx), "Posterior s.d."))
        print(mode, e.info)
    lx = engines["nonstationary"]._lfun(R).reshape(ny, nx) * um
    panels.append(("Local length scale $\\ell(x)$", lx, "$\\ell$ (µm)"))
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
    fig, axs = plt.subplots(1, 4, figsize=(11.0, 2.9), facecolor=SURF, constrained_layout=True)
    vmax = max(p[1].max() for p in panels[:3])
    ext = (-0.5, nx - 0.5, ny - 0.5, -0.5)
    mx, my = P[prior, 0] * um, P[prior, 1] * um
    for ax, (title, v, cl) in zip(axs, panels):
        style(ax, grid=False)
        norm = dict(vmin=0, vmax=vmax) if cl == "Posterior s.d." else {}
        im = ax.imshow(v, cmap=SEQ, extent=ext, interpolation="nearest", **norm)
        ax.scatter(mx, my, s=5, color=INK, linewidths=0)
        ax.set_xticks([0, 20, 40]), ax.set_yticks([0, 10, 20])
        ax.set_title(title, color=INK, fontsize=8.5)
        cb = fig.colorbar(im, ax=ax, shrink=0.75)
        cb.ax.tick_params(labelsize=7, colors=INK2)
        cb.set_label(cl, color=INK2, fontsize=7.5)
    axs[0].set_ylabel("y (µm)", color=INK2)
    for ax in axs:
        ax.set_xlabel("x (µm)", color=INK2)
    fig.suptitle(f"IR map before level {level}: {int(prior.sum())} measured sites (dots); "
                 f"GP evaluated on the full {nx} × {ny} µm raster", color=INK, fontsize=9)
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"figS1_gp_std.{ext}", dpi=250, facecolor=SURF)


if __name__ == "__main__":
    fig4(load())
    figS1()
