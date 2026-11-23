"""
Figure 1 (round 4b): what is stated about the wrong skips, and what was realised, as sites are measured.
NaCl (200)-width scan, budget 0.20.

(a) A Gaussian process steering on its own stated error (seed 29 of SI 10.3, stop at 476, near the mean of 30 runs).
    After every batch: sites still unmeasured (bar, skipped if the run stopped there), the distribution of wrong
    skips among them that the process itself states (violin: 2000 joint draws from its own predictive, presence
    per site as stated and log width jointly over all unmeasured sites, central 95 % shaded), and the realised count (dot), known only from the full scan.
(b) The certified plan with the same process as predictor and score (campaign of average cost, 757 measured).
    After each level: sites skipped so far (bar), the distribution of wrong skips that the calibration draws
    support (violin: confidence distribution of the exact hypergeometric test, convolved over levels, central
    95 % shaded), the PAC bound of the contract (tick: budget of each level less its calibration failures,
    summed), and the realised count (dot).

No new runs: results/revision2/gpstop_replay_s29.npz (exact replay of gpstop seed 29) and
results/record/nacl_fwhm_nested_gpfail_mle.

    python manuscript/figures/fig_hook_pac.py
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import hypergeom

FIG = Path(__file__).resolve().parent
ROOT = FIG.parents[1]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#b9b8b3"
ORANGE, PURPLE, BAR = "#eb6834", "#8e6cc8", "#e4e3df"
EPS, SEED, CAMPAIGN = 0.20, 29, 22


def poisson_binomial(q):
    pmf = np.zeros(len(q) + 1); pmf[0] = 1.0
    for p in q:
        pmf[1:] = pmf[1:] * (1 - p) + pmf[:-1] * p
        pmf[0] *= (1 - p)
    return pmf


def cd_remaining(N, m, k):
    """Confidence distribution of W - k, W the level count of the event, from k events among m drawn of N:
    H(w) = 1 - P_{w+1}(K <= k), whose (1 - a) quantile is the exact upper confidence bound."""
    w = np.arange(0, N + 2)
    G = hypergeom.cdf(k, N, np.minimum(w, N), m)
    G[w > N] = 0.0
    h = G[:-1] - G[1:]
    h[: k] = 0.0
    return h[k:] / h.sum()                      # pmf of W - k = 0, 1, ...


def quantiles(pmf, ps):
    c = np.cumsum(pmf)
    return [int(np.searchsorted(c, p)) for p in ps]


def violin(ax, x, pmf, half, col, lo_hi):
    y = np.arange(len(pmf)); keep = pmf > pmf.max() * 1e-3
    y, d = y[keep], pmf[keep] / pmf.max() * half
    ax.fill_betweenx(y, x - d, x + d, color=col, alpha=0.25, lw=0)
    band = (y >= lo_hi[0]) & (y <= lo_hi[1])
    ax.fill_betweenx(y[band], x - d[band], x + d[band], color=col, alpha=0.75, lw=0)


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK})
    z = np.load(ROOT / f"results/revision2/gpstop_replay_s{SEED:02d}.npz", allow_pickle=True)
    rows = [json.loads(l) for l in gzip.open(ROOT / "results/record/nacl_fwhm_nested_gpfail_mle/runs.jsonl.gz")]
    run = rows[CAMPAIGN]

    fig, (axa, axb) = plt.subplots(1, 2, figsize=(7.2, 3.4), sharey=True,
                                   gridspec_kw=dict(wspace=0.08, left=0.085, right=0.985, top=0.82, bottom=0.13))
    xmax, ymax = 800, 1000
    for ax in (axa, axb):
        ax.set_xlim(50, xmax); ax.set_ylim(0, ymax)
        ax.grid(axis="y", color=GRID, lw=0.4, alpha=0.6)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.set_xlabel("sites measured")
    axa.set_ylabel("sites")

    # (a) the process on its own word
    inside = 0
    for x, q, wr, jd in zip(z["measured"], z["q"], z["wrong"], z["joint"]):
        q = np.asarray(q, float); wr = np.asarray(wr, bool)
        axa.bar(x, len(q), width=18, color=BAR, lw=0, zorder=0)
        pmf = np.bincount(jd, minlength=len(q) + 1).astype(float)
        pmf = np.convolve(pmf, np.ones(9) / 9, mode="same"); pmf /= pmf.sum()
        lo, hi = np.percentile(jd, [2.5, 97.5])
        violin(axa, x, pmf, 10, ORANGE, (lo, hi))
        axa.plot(x, wr.sum(), "o", ms=2.6, color=INK, zorder=3)
        inside += lo <= wr.sum() <= hi
    n_b = len(z["measured"])
    axa.annotate("stops when its stated\nshare meets the budget", (z["measured"][-1] + 10, 200), (540, 330), fontsize=7,
                 color=INK, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
    axa.text(xmax, 960, f"realised count inside the stated\n95 % range after {inside} of {n_b} batches",
             ha="right", va="top", fontsize=7, color=INK)
    axa.set_title("(a) A Gaussian process steering on its own stated error", loc="left", fontsize=8, color=INK)

    # (b) the contract
    spent, skipped, real, bound, conv = 76, 0, 0, 0, np.array([1.0])
    for p in run["per_level"]:
        t = p["certificates"]["interp"]["tails"]
        N, m = p["n_level"], p["n_cal"]
        W = int(round(p["level"]["E_rate"] * N)); k = W - p["rem"]["E_count"]
        spent += p["n_cal"] + p["n_measured_rem"]; skipped += p["n_skip"]; real += p["rem"]["E_count"]
        bound += int(np.floor(EPS * N)) - k
        conv = np.convolve(conv, cd_remaining(N, m, k))
        lo, hi = quantiles(conv, [0.025, 0.975])
        axb.bar(spent, skipped, width=36, color=BAR, lw=0, zorder=0)
        violin(axb, spent, conv, 20, PURPLE, (lo, hi))
        axb.plot([spent - 22, spent + 22], [bound] * 2, color=INK, lw=1.2, zorder=3)
        axb.plot(spent, real, "o", ms=3.2, color=INK, zorder=4)
        axb.text(spent, max(skipped, hi) + 18, f"L{p['L']}", ha="center", fontsize=7, color=INK2)
    axb.annotate("PAC bound of the contract,\nfixed before the level is decided", (spent - 22, bound), (300, 560),
                 fontsize=7, color=INK, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
    axb.set_title(f"(b) The same process under the contract", loc="left", fontsize=8, color=INK)

    # shared key
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    handles = [Patch(color=BAR, label="sites skipped"),
               Patch(color=ORANGE, alpha=0.75, label="wrong skips stated by the process (central 95 % dark)"),
               Patch(color=PURPLE, alpha=0.75, label="wrong skips supported by the calibration draws (central 95 % dark)"),
               Line2D([], [], marker="o", ls="", color=INK, ms=3, label="wrong skips realised, known from the full scan")]
    fig.legend(handles=handles, loc="upper center", ncol=2, frameon=False, fontsize=7, bbox_to_anchor=(0.53, 1.0),
               handlelength=1.2, columnspacing=2.0)
    print(f"GP seed {SEED}: stop at {z['measured'][-1]}, inside {inside}/{n_b}; contract campaign {CAMPAIGN}: "
          f"{spent} measured, {skipped} skipped, {real} wrong, bound {bound}")
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"fig_hook_pac.{ext}", dpi=300)


if __name__ == "__main__":
    main()
