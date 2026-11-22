"""
Figure 1 (round 4): when a statement about the skips is known, on the NaCl (200)-width scan.
(a) A Gaussian process steering on its own stated error (SI 10.3, 30 runs): stated and realised share of the
    sites beyond the seed predicted wrongly, against measurements spent; audit of 100 skipped sites after the stop.
(b) The certified plan with the same process as predictor and score (50 campaigns): the bound of each level,
    fixed after its calibration draw and before its decision, and the realised share of the level skipped wrongly.
(c) Timeline: decisions against the moment a checkable statement about them exists.

No new runs: reads results/revision2/gpstop_nacl.jsonl and results/record/nacl_fwhm_nested_gpfail_mle.

    python manuscript/figures/fig_hook_timing.py
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import hypergeom

FIG = Path(__file__).resolve().parent
ROOT = FIG.parents[1]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#b9b8b3"
ORANGE, PURPLE, GREY = "#eb6834", "#8e6cc8", "#9a9995"
BUDGET, CONF, N_AUDIT = 0.20, 0.80, 100
N_SITES, N_SEED = 1071, 76
N_DEC = N_SITES - N_SEED                      # sites beyond the seed, the population of every share


def audit_upper(n_skip: int, k: int) -> int:
    """Exact hypergeometric upper limit on the wrong skips among n_skip, k failures in N_AUDIT drawn."""
    w = np.arange(k, n_skip + 1)
    ok = hypergeom.cdf(k, n_skip, w, N_AUDIT) > 1 - CONF
    return int(w[ok].max())


def stopping_runs():
    rr = [json.loads(l) for l in open(ROOT / "results/revision2/gpstop_nacl.jsonl")]
    xs = sorted({t["measured"] for r in rr for t in r["trajectory"]})
    stated = np.full((len(rr), len(xs)), np.nan); real = stated.copy()
    for i, r in enumerate(rr):
        for t in r["trajectory"]:
            j = xs.index(t["measured"]); stated[i, j] = t["stated_predictive"]; real[i, j] = t["true_share"]
    stops = np.array([r["stops"]["predictive"]["measured"] for r in rr])
    true_at_stop = np.array([r["stops"]["predictive"]["true_share"] for r in rr])
    # audit bound at the stop: distribution over draws, pooled over runs (shares of N_DEC)
    ub, meets = [], []
    for m, s in zip(stops, true_at_stop):
        n_skip = N_SITES - m; wrong = int(round(s * N_DEC))
        ks = np.arange(0, N_AUDIT + 1); pk = hypergeom.pmf(ks, n_skip, wrong, N_AUDIT)
        u = np.array([audit_upper(n_skip, k) / N_DEC for k in ks])
        ub.append((u, pk)); meets.append(float(pk[u <= BUDGET].sum()))
    return np.array(xs), stated, real, stops, true_at_stop, ub, float(np.mean(meets))


def certified_runs():
    rows = [json.loads(l) for l in gzip.open(ROOT / "results/record/nacl_fwhm_nested_gpfail_mle/runs.jsonl.gz")]
    lv = {}
    for r in rows:
        spent = N_SEED
        for p in r["per_level"]:
            a = spent; c = spent + p["n_cal"]; spent = c + p["n_measured_rem"]
            lv.setdefault(p["L"], []).append((a, c, spent, p["level"]["E_rate"]))
    out = {L: np.array(v) for L, v in sorted(lv.items())}
    total = np.array([sum(p["n_cal"] + p["n_measured_rem"] for p in r["per_level"]) + N_SEED for r in rows])
    return out, total


def band(ax, x, Y, col, ls, label):
    ok = np.sum(~np.isnan(Y), 0) >= 5
    m = np.nanmean(Y, 0); lo, hi = np.nanpercentile(Y, [5, 95], 0)
    ax.fill_between(x[ok], lo[ok], hi[ok], color=col, alpha=0.15, lw=0)
    ax.plot(x[ok], m[ok], color=col, lw=2, ls=ls, label=label, solid_capstyle="round")


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK})
    xs, stated, real, stops, true_at_stop, ub, meets = stopping_runs()
    lv, total = certified_runs()
    print(f"stopping: {stops.min()}-{stops.max()} (mean {stops.mean():.0f}), wrong {100*true_at_stop.mean():.1f} %, "
          f"audit meets budget in {100*meets:.0f} % of draws; certified {total.mean():.0f} ± {total.std():.0f}")

    fig = plt.figure(figsize=(7.2, 3.9))
    gs = fig.add_gridspec(2, 2, height_ratios=[3.0, 1.15], hspace=0.55, wspace=0.12,
                          left=0.09, right=0.985, top=0.93, bottom=0.10)
    axa = fig.add_subplot(gs[0, 0]); axb = fig.add_subplot(gs[0, 1], sharey=axa); axc = fig.add_subplot(gs[1, :])
    xmax = 800
    for ax in (axa, axb):
        ax.axhline(BUDGET, color=INK2, lw=0.8, ls=(0, (4, 3)))
        ax.set_xlim(60, xmax); ax.set_ylim(0, 0.42)
        ax.grid(axis="y", color=GRID, lw=0.4, alpha=0.6)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.set_xlabel("sites measured")
    axa.text(xmax, BUDGET + 0.008, "budget 0.20", ha="right", va="bottom", color=INK2, fontsize=7)

    # (a) steering on its own statement
    band(axa, xs, stated, ORANGE, "-", "stated by the process during the run")
    band(axa, xs, real, INK2, (0, (2, 1.5)), "realised (known only from the full scan)")
    axa.plot(stops, np.full(len(stops), 0.012), "|", color=ORANGE, ms=6, mew=0.8)
    axa.text(stops.mean(), 0.03, "stops", color=ORANGE, ha="center", fontsize=7)
    u = np.concatenate([a for a, _ in ub]); w = np.concatenate([p for _, p in ub]) / len(ub)
    o = np.argsort(u); cdf = np.cumsum(w[o]); q = lambda p: u[o][np.searchsorted(cdf, p)]  # noqa: E731
    xa = stops.mean() + N_AUDIT
    axa.add_patch(plt.Rectangle((xa - 14, q(0.05)), 28, q(0.95) - q(0.05), color=ORANGE, alpha=0.35, lw=0))
    axa.plot([xa - 14, xa + 14], [q(0.5)] * 2, color=ORANGE, lw=2)
    axa.annotate(f"audit of {N_AUDIT} skipped\nsites after the stop:\nwithin budget in\n{100*meets:.0f} % of draws",
                 (xa, q(0.05)), (xa + 30, 0.075), fontsize=7, color=INK, va="center",
                 arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
    axa.set_ylabel("share of sites beyond the seed\nskipped or predicted wrongly")
    axa.set_title("(a) Steering on its own stated error", loc="left", fontsize=8, color=INK)
    axa.legend(frameon=False, loc="upper right", fontsize=7, bbox_to_anchor=(1.0, 1.02))

    # (b) the contract
    for L, v in lv.items():
        a, c, e, r = v.T
        A, C, E = a.mean(), c.mean(), e.mean()
        axb.axvspan(A, C, color=GREY, alpha=0.18, lw=0)
        axb.plot([C, E], [BUDGET, BUDGET], color=PURPLE, lw=3, solid_capstyle="butt")
        jit = np.random.default_rng(L).uniform(-0.3, 0.3, len(r)) * max(E - C, 30)
        axb.scatter((C + E) / 2 + jit, r, s=5, color=PURPLE, alpha=0.35, lw=0)
        axb.plot([(C + E) / 2 - 8, (C + E) / 2 + 8], [r.mean()] * 2, color=INK, lw=1.6)
        axb.text((A + E) / 2, 0.405, f"L{L}", ha="center", fontsize=7, color=INK2)
    axb.text(lv[6][:, 1].mean() + 4, BUDGET + 0.012, "bound, fixed before\nthe level is decided",
             fontsize=7, color=PURPLE, va="bottom")
    axb.text(np.mean(lv[6][:, :2]), 0.004, "calibration\ndraw", fontsize=6.5, color=INK2, ha="center", va="bottom")
    axb.text(lv[5][:, 1].mean(), 0.385, "realised share of each level skipped wrongly\n(dots: campaigns; bar: mean)",
             fontsize=7, color=INK, va="top")
    axb.set_title(f"(b) The same process under the contract: {total.mean():.0f} sites",
                  loc="left", fontsize=8, color=INK)
    plt.setp(axb.get_yticklabels(), visible=False)

    # (c) timeline
    lanes = {"steering on its own statement": 1.0, "under the contract": 0.0}
    for name, y in lanes.items():
        axc.plot([N_SEED, xmax], [y, y], color=GRID, lw=0.8)
        axc.text(N_SEED, y + 0.42, name, ha="left", va="center", fontsize=7.5, color=INK)
    tx = xs[xs <= stops.mean()]
    axc.plot(tx, np.full(len(tx), 1.0), "|", color=ORANGE, ms=8, mew=1)
    axc.plot([xa], [1.0], "D", color=ORANGE, ms=5)
    axc.text(xa + 10, 1.0, "first check: audit after the campaign", va="center", fontsize=7, color=INK)
    for L, v in lv.items():
        C, E = v[:, 1].mean(), v[:, 2].mean()
        axc.plot([C], [0.0], "D", color=PURPLE, ms=5)
        axc.plot([C + 0.5 * (E - C)], [0.0], "|", color=PURPLE, ms=8, mew=1)
    axc.text(lv[6][:, 2].mean() * 0.5 + lv[6][:, 1].mean() * 0.5 + 12, 0.0, "bound before each decision", va="center", fontsize=7, color=INK)
    axc.plot([], [], "|", color=INK2, ms=8, mew=1, label="decision")
    axc.plot([], [], "D", color=INK2, ms=5, ls="", label="checkable statement")
    axc.legend(frameon=False, loc="lower right", ncol=2, fontsize=7)
    axc.set_xlim(60, xmax); axc.set_ylim(-1.0, 1.6); axc.set_yticks([])
    for s in ("top", "right", "left"):
        axc.spines[s].set_visible(False)
    axc.set_xlabel("sites measured")
    axc.set_title("(c) When a statement about the skips can be checked", loc="left", fontsize=8, color=INK)

    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"fig_hook_timing.{ext}", dpi=300)
    print("wrote", FIG / "fig_hook_timing.png")


if __name__ == "__main__":
    main()
