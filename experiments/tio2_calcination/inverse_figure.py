"""Figure for the inverse study: recovered Arrhenius lines with bands, transformation map, z-scores.

    python -m experiments.tio2_calcination.inverse_figure
"""
from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from . import forward_v2 as V
from . import inverse as INV

INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e2dc"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
R = V.R_GAS

# (title, index of ln k_ref, index of E, reference T in K, unit)
PROC = [("Surface nucleation of rutile", 0, 1, INV.T_NUC, "ln (k / k_true)"),
        ("Contact growth of rutile on anatase", 2, 3, INV.T_AR, "ln (k / k_true)"),
        ("Anatase coarsening", 5, 6, 963.15, "ln (K / K_true)"),
        ("Rutile coarsening", 7, 8, 1173.15, "ln (K / K_true)")]


def band(theta, cov, i, j, Tref, T):
    x = -(1 / T - 1 / Tref) / R
    m = theta[i] + theta[j] * x
    v = cov[i, i] + x ** 2 * cov[j, j] + 2 * x * cov[i, j]
    return m, np.sqrt(np.clip(v, 0, None))


def t50_curve(theta, dwell, c, Tg):
    p = INV.params_of(theta)
    TT, DD = np.meshgrid(Tg, dwell)
    rec = dict(T=TT.ravel(), t=DD.ravel(), c=np.full(TT.size, c), s=np.zeros(TT.size), b=np.zeros(TT.size))
    w = INV.predict(p, rec)[0].reshape(TT.shape)
    out = np.full(len(dwell), np.nan)
    for k, row in enumerate(w):
        j = np.flatnonzero(row >= 0.5)
        if len(j) and j[0] > 0:
            a = j[0]
            out[k] = np.interp(0.5, row[a - 1:a + 1], Tg[a - 1:a + 1])
    return out


def main():
    F = json.load(open(INV.OUT / "fits.json"))
    truth = np.array(F["truth"])
    fits = F["fits"]
    show = [("world A | full design", BLUE, "full design, 64 runs"),
            ("world A | campaign 0", ORANGE, "accountable campaign, 47 runs"),
            ("world A | seed levels", AQUA, "seed levels only, 16 runs")]
    # covariance from correlations and standard errors
    def cov_of(f):
        se = np.array(f["se"])
        return np.array(f["corr"]) * np.outer(se, se)

    fig = plt.figure(figsize=(12.5, 7.6))
    gs = fig.add_gridspec(2, 3, hspace=0.42, wspace=0.45, left=0.05, right=0.985, top=0.87, bottom=0.08)
    Tc = np.linspace(500, 1000, 200)
    T = Tc + 273.15
    letters = "abcdef"
    for k, (title, i, j, Tref, ylab) in enumerate(PROC):
        ax = fig.add_subplot(gs[k // 2, k % 2] if k < 2 else gs[1, k - 2])
        mt = truth[i] - truth[j] * (1 / T - 1 / Tref) / R
        for key, col, lab in show:
            f = fits[key]
            m, s = band(np.array(f["theta"]), cov_of(f), i, j, Tref, T)
            ax.fill_between(1000 / T, m - mt - 2 * s, m - mt + 2 * s, color=col, alpha=0.16, lw=0)
            ax.plot(1000 / T, m - mt, color=col, lw=1.4, label=lab + " (±2 s.e.)")
        ax.axhline(0, color=INK, lw=1.2, ls="--", label="truth")
        ax.set_ylim(-3, 3)
        Ej = [fits[key]["theta"][j] for key, _, _ in show]
        Es = [fits[key]["se"][j] for key, _, _ in show]
        ax.set_title(f"({letters[k]}) {title}\nE: truth {truth[j]:.0f}; fits " +
                     ", ".join(f"{e:.0f}±{s:.0f}" for e, s in zip(Ej, Es)) + " kJ/mol",
                     fontsize=9, loc="left", color=INK)
        ticks = np.array([500, 600, 700, 800, 900, 1000])
        ax.set_xticks(1000 / (ticks + 273.15))
        ax.set_xticklabels([f"{t}" for t in ticks])
        ax.invert_xaxis()
        ax.set_xlabel("temperature (°C, reciprocal scale)", fontsize=8.5, color=INK2)
        ax.set_ylabel(ylab, fontsize=8.5, color=INK2)
        ax.grid(color=GRID, lw=0.6)
        ax.tick_params(labelsize=8, colors=INK2)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        if k == 0:
            ax.legend(fontsize=7.5, frameon=False, loc="upper left")

    # (e) transformation map: T at which half the anatase has converted, vs dwell
    ax = fig.add_subplot(gs[0, 2])
    dwell = 2.0 ** np.linspace(0, 4, 13)
    Tg = np.linspace(500, 1000, 251)
    f = fits["world A | campaign 0"]
    th, cv = np.array(f["theta"]), cov_of(f)
    rng = np.random.default_rng(0)
    draws = rng.multivariate_normal(th, cv, size=150)
    for c, ls, lab in ((0.0, "-", "no alumina"), (0.05, ":", "5 % alumina")):
        tt = t50_curve(truth, dwell, c, Tg)
        D = np.array([t50_curve(d, dwell, c, Tg) for d in draws])
        lo, hi = np.nanpercentile(D, [5, 95], axis=0)
        ax.fill_between(dwell, lo, hi, color=ORANGE, alpha=0.2, lw=0)
        ax.plot(dwell, t50_curve(th, dwell, c, Tg), color=ORANGE, lw=1.4, ls=ls, label=f"campaign estimate, {lab}")
        ax.plot(dwell, tt, color=INK, lw=1.4, ls=ls, alpha=0.8, label=f"truth, {lab}")
    ax.set_xscale("log", base=2)
    ax.set_xticks([1, 2, 4, 8, 16])
    ax.set_xticklabels(["1", "2", "4", "8", "16"])
    ax.set_xlabel("dwell (h)", fontsize=8.5, color=INK2)
    ax.set_ylabel("temperature for 50 % rutile (°C)", fontsize=8.5, color=INK2)
    ax.set_title("(e) Transformation map, native powder\nband: 90 % over parameter uncertainty",
                 fontsize=9, loc="left", color=INK)
    ax.legend(fontsize=7, frameon=False)
    ax.grid(color=GRID, lw=0.6)
    ax.tick_params(labelsize=8, colors=INK2)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)

    # (f) z-scores of all fits
    ax = fig.add_subplot(gs[1, 2])
    names = ["nucleation rate", "nucleation E", "contact-growth rate", "contact-growth E", "alumina inhibition",
             "anatase coarsening rate", "anatase coarsening E", "rutile coarsening rate", "rutile coarsening E",
             "rutile microstrain"]
    y = np.arange(len(names))[::-1]
    for key, f in fits.items():
        z = np.array(f["z"])
        col = INK2 if "world B" in key else (AQUA if "seed" in key else (BLUE if "full" in key else ORANGE))
        mk = "s" if "world B" in key else "o"
        ax.plot(z, y + rng.uniform(-0.18, 0.18, len(y)), mk, color=col, ms=3.6, mec="white", mew=0.4, alpha=0.9)
    ax.axvspan(-2, 2, color=GRID, alpha=0.6, lw=0)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=7.5)
    ax.set_xlabel("(estimate − truth) / cluster-robust standard error", fontsize=8.5, color=INK2)
    ax.set_title("(f) All fits: 5 campaigns, full design, seed levels;\nsquares: a second synthetic world",
                 fontsize=9, loc="left", color=INK)
    ax.set_xlim(-5, 5)
    ax.tick_params(labelsize=8, colors=INK2)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.suptitle("Kinetic landscape recovered from the measured furnace runs (forward model v2 as truth)\n"
                 "(a-d) rate constants relative to the truth over the design range; activation energies in the titles",
                 fontsize=10.5, color=INK, x=0.06, ha="left", y=0.985)
    fig.savefig("results/tio2/inverse.png", dpi=160)
    print("wrote results/tio2/inverse.png")


if __name__ == "__main__":
    main()
