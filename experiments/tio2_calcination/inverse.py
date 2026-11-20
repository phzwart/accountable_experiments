"""
Inverse problem: recover the kinetic parameters of forward model v2 from the patterns a
campaign measured.

    python -m experiments.tio2_calcination.inverse

1. Observables per crucible, as an analyst would take them from the pattern: rutile mass
   fraction from the areas of anatase (101) and rutile (110), and crystallite sizes from their
   widths through a Scherrer lookup calibrated on simulated single-phase patterns with the
   instrument function (the analogue of an instrument standard). Widths at the instrument
   limit (sizes above about 120 nm) are dropped.
2. Model: forward v2 with the nominal recipe (the analyst knows temperature, dwell, alumina
   and P25 fraction, not the furnace offsets, dosing errors or crucible jitter).
3. Fitted: rate and activation energy of surface nucleation and of anatase-rutile contact
   growth, the alumina inhibition constant, and the coarsening constants and activation
   energies of anatase and rutile (9 parameters). Rates are parameterised at a reference
   temperature inside the data, which removes most of the rate / activation-energy correlation.
   Held at their literature values: interface nucleation, the size dependence beta of the
   activation energy, the precursor size distribution and the P25 contact efficiency.
4. Uncertainty: Laplace approximation, s^2 (J^T J)^-1 at the optimum.

Data sets: every run of the 64-run design measured; the runs measured by accountable
campaigns (size claim, several calibration seeds); the seed levels alone.
"""
from __future__ import annotations

import dataclasses
import json
import time
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.signal import savgol_filter

from accountable import run_campaign
from accountable.criteria import peak_descriptors_window

from . import adapter as A
from . import forward_v2 as V
from . import furnace as FU

OUT = Path("results/tio2/inverse")
R = V.R_GAS
T_NUC, T_AR = 1023.15, 973.15
NAMES = ["ln k_SN(750 °C)", "E_SN", "ln k_AR(700 °C)", "E_AR", "ln c_n", "ln K_A(690 °C)", "E_KA",
         "ln K_R(900 °C)", "E_R", "rutile microstrain"]
UNITS = ["ln h⁻¹", "kJ/mol", "ln h⁻¹", "kJ/mol", "ln(mass fraction)", "ln nm³ h⁻¹", "kJ/mol", "ln nm³ h⁻¹", "kJ/mol",
         "10⁻⁴"]


def theta_of(p):
    return np.array([
        p.lnA_SN - p.E_SN / (R * T_NUC), p.E_SN,
        p.lnA_AR - p.E_AR / (R * T_AR), p.E_AR,
        np.log(p.c_n), np.log(p.K_A_690), p.E_KA, np.log(p.K_R_900), p.E_R, p.strain_R * 1e4,
    ])


def params_of(th, base=V.P):
    return dataclasses.replace(
        base, lnA_SN=th[0] + th[1] / (R * T_NUC), E_SN=th[1],
        lnA_AR=th[2] + th[3] / (R * T_AR), E_AR=th[3], c_n=float(np.exp(th[4])),
        K_A_690=float(np.exp(th[5])), E_KA=th[6], K_R_900=float(np.exp(th[7])), E_R=th[8],
        strain_R=float(th[9]) * 1e-4)


# ------------------------------------------------------------------ observables
EPS = np.array([0.0, 2.5, 5.0, 7.5, 10.0, 15.0])     # rutile microstrain grid, 10^-4
R101, R101_HALF = 36.079, 0.6                          # second rutile reflection; anatase (103) is 0.9° away
D_MAX = 70.0        # nm; a one-reflection Scherrer size is reliable below this (anatase, strain-free)
W_LOD = 0.03        # rutile (or anatase) mass fraction below which the phase is not detected
LOOK = None


def _lookup():
    """Width tables from simulated single-phase patterns with the instrument function: anatase (101)
    at zero strain, rutile (110) and (101) over a grid of microstrain (the analogue of a size-strain
    standard)."""
    Ds = np.geomspace(6, 400, 60)
    x = V.axis()
    n = len(Ds)
    out = {}
    for name, frac, refl, eps in (("A", 0.0, [(V.A101, 1.5)], [0.0]),
                                  ("R", 1.0, [(V.R110, A.R_HALF), (R101, R101_HALF)], EPS)):
        tab = []
        for e in eps:
            p0 = dataclasses.replace(V.P, strain_A0=0.0, strain_R=e * 1e-4)
            st = dict(a=np.full(n, 1 - frac), f_R=np.full(n, frac), D_A=Ds, D_R=Ds, T=np.full(n, 500.0),
                      c=np.zeros(n))
            I = savgol_filter(V.pattern(st, None, p0, noise=False), A.SMOOTH, 2, axis=1)
            tab.append([peak_descriptors_window(I, x, c, h)["fwhm"] for c, h in refl])
        out[name] = (Ds, np.array(tab))          # (strain, reflection, size)
    return out


def _tables():
    global LOOK
    if LOOK is None:
        LOOK = _lookup()
    return LOOK


def rutile_widths(D, eps):
    """Predicted rutile (110) and (101) widths for sizes D at microstrain eps (10^-4):
    log-linear in size, linear in strain between table rows."""
    Ds, tab = _tables()["R"]
    j = int(np.clip(np.searchsorted(EPS, eps) - 1, 0, len(EPS) - 2))
    t = (eps - EPS[j]) / (EPS[j + 1] - EPS[j])
    f = (1 - t) * tab[j] + t * tab[j + 1]
    lD = np.log(np.clip(D, Ds[0], Ds[-1]))
    return [np.exp(np.interp(lD, np.log(Ds), np.log(f[k]))) for k in range(f.shape[0])]


def size_from_fwhm(fw, which="A", d_max=D_MAX):
    Ds, f = _tables()[which]
    f = f[0, 0]
    fmin = f[Ds <= d_max].min()                    # strain and instrument dominate the width beyond this
    ok = np.isfinite(fw) & (fw > fmin)
    D = np.full(len(fw), np.nan)
    D[ok] = np.exp(np.interp(np.log(fw[ok]), np.log(f[::-1]), np.log(Ds[::-1])))
    return D


def _pv(x, c, fw, eta):
    g = np.exp(-4 * np.log(2) * ((x - c) / fw) ** 2) * (2 * np.sqrt(np.log(2) / np.pi) / fw)
    l = (2 / np.pi / fw) / (1 + 4 * ((x - c) / fw) ** 2)
    return eta * l + (1 - eta) * g


def _doublet(x, c1, fw, eta):
    """Unit-area Cu Kalpha1/Kalpha2 doublet (2:1) at Kalpha1 position c1."""
    c2 = 2 * np.degrees(np.arcsin(np.sin(np.radians(c1 / 2)) * V.LAMBDA2 / V.LAMBDA1))
    return (2 * _pv(x, c1, fw, eta) + _pv(x, c2, fw, eta)) / 3


def profile_areas(I, sigma, lo=23.5, hi=29.5):
    """Integrated areas of anatase (101) and rutile (110) from a two-phase pseudo-Voigt doublet fit
    with a quadratic background over lo-hi. Areas of peaks below the presence threshold are zero."""
    x = V.axis()
    m = (x >= lo) & (x <= hi)
    xs = x[m] - 0.5 * (lo + hi)
    xx = x[m]
    out = np.zeros((len(I), 2))
    sig = np.broadcast_to(np.asarray(sigma, float), (len(I),))
    for i, y in enumerate(np.asarray(I, float)[:, m]):
        base = np.median(np.r_[y[:15], y[-15:]])

        def model(t):
            b0, b1, b2, sh, aA, fA, eA, aR, fR, eR = t
            return (b0 + b1 * xs + b2 * xs ** 2 + aA * _doublet(xx, V.A101 + sh, fA, eA)
                    + aR * _doublet(xx, V.R110 + sh, fR, eR))

        hA = max(y[np.abs(xx - V.A101) < 0.3].max() - base, 0)
        hR = max(y[np.abs(xx - V.R110) < 0.3].max() - base, 0)
        t0 = [base, 0, 0, 0, hA * 0.4 + 1, 0.4, 0.5, hR * 0.3 + 1, 0.3, 0.5]
        r = least_squares(lambda t: model(t) - y, t0, method="trf",
                          bounds=([-np.inf, -np.inf, -np.inf, -0.3, 0, 0.08, 0, 0, 0.08, 0],
                                  [np.inf, np.inf, np.inf, 0.3, np.inf, 3, 1, np.inf, 3, 1]))
        _, _, _, _, aA, fA, eA, aR, fR, eR = r.x
        # peak height of the fitted doublet against the noise: presence test
        pA = aA * _doublet(np.array([V.A101 + r.x[3]]), V.A101 + r.x[3], fA, eA)[0]
        pR = aR * _doublet(np.array([V.R110 + r.x[3]]), V.R110 + r.x[3], fR, eR)[0]
        out[i] = [aA if pA > A.PRESENCE_C * sig[i] else 0.0, aR if pR > A.PRESENCE_C * sig[i] else 0.0]
    return out


I_REL_R110 = 1 / 1.375          # rutile (110) to anatase (101) integrated intensity per unit mass


def rutile_fraction_profile(I, sigma):
    a = profile_areas(I, sigma)
    tot = a[:, 1] + a[:, 0] * I_REL_R110
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(tot > 0, a[:, 1] / tot, np.nan)


def observables(I, sigma):
    """Per crucible: rutile fraction w, anatase size, rutile (110) and (101) widths (NaN where not
    measurable). Rutile widths stay widths: size and strain are separated inside the fit."""
    x = V.axis()
    w = rutile_fraction_profile(I, sigma)
    Is = savgol_filter(I, A.SMOOTH, 2, axis=1)
    dA = peak_descriptors_window(Is, x, V.A101, 1.5)
    d110 = peak_descriptors_window(Is, x, V.R110, A.R_HALF)
    d101 = peak_descriptors_window(Is, x, R101, R101_HALF)
    DA = size_from_fwhm(np.where(np.isfinite(w) & (w < 0.9), dA["fwhm"], np.nan))
    f110 = np.where(np.isfinite(w) & (w > 0.1), d110["fwhm"], np.nan)
    f101 = np.where(np.isfinite(w) & (w > 0.3), d101["fwhm"], np.nan)
    return w, DA, f110, f101


# ------------------------------------------------------------------ model
def predict(p, rec):
    """Nominal-recipe predictions of w, D_A (mass-weighted over both powders), D_R."""
    st = V.integrate(rec["T"], rec["t"], rec["c"], 0.0, None, p)
    w = st["f_R"].copy()
    DA, DR = st["D_A"].copy(), st["D_R"].copy()
    b = rec["b"]
    m = b > 0
    if m.any():
        q = dataclasses.replace(p, D0_A=25.0, D_seed=40.0, r_impurity=0.17, phi_contact=1.0)
        sp = V.integrate(rec["T"][m], rec["t"][m], rec["c"][m], 0.0, None, q)
        an_n, an_p = (1 - b[m]) * st["a"][m], b[m] * sp["a"]
        ru_n, ru_p = (1 - b[m]) * st["f_R"][m], b[m] * sp["f_R"]
        w[m] = ru_n + ru_p
        DA[m] = (an_n * st["D_A"][m] + an_p * sp["D_A"]) / np.maximum(an_n + an_p, 1e-12)
        DR[m] = (ru_n * st["D_R"][m] + ru_p * sp["D_R"]) / np.maximum(ru_n + ru_p, 1e-12)
    return w, DA, DR


def logit(v):
    v = np.clip(v, 0.005, 0.995)
    return np.log(v / (1 - v))


SIG_W, SIG_D, SIG_F = 0.35, 0.12, 0.015         # residual scales: logit fraction, ln size, ln width


def residuals(th, rec, obs, censor=True):
    w_o, DA_o, f110_o, f101_o = obs
    w, DA, DR = predict(params_of(th), rec)
    if censor:
        # below the detection limit only "less than W_LOD" is known: one-sided residual
        lo, hi = w_o < W_LOD, w_o > 1 - W_LOD
        mid = ~(lo | hi)
        r = [(logit(w[mid]) - logit(w_o[mid])) / SIG_W,
             np.maximum(logit(w[lo]) - logit(W_LOD), 0) / SIG_W,
             np.minimum(logit(w[hi]) - logit(1 - W_LOD), 0) / SIG_W]
    else:
        r = [(logit(w) - logit(w_o)) / SIG_W]
    mA = np.isfinite(DA_o)
    r.append((np.log(DA[mA]) - np.log(DA_o[mA])) / SIG_D)
    f110, f101 = rutile_widths(DR, th[9])
    for f, fo in ((f110, f110_o), (f101, f101_o)):
        m = np.isfinite(fo)
        r.append((np.log(f[m]) - np.log(fo[m])) / SIG_F)
    return np.concatenate(r)


def residual_groups(rec, obs):
    """Furnace run of each residual, in the order residuals() returns them."""
    w_o, DA_o, f110_o, f101_o = obs
    g = rec["run"]
    lo, hi = w_o < W_LOD, w_o > 1 - W_LOD
    mid = ~(lo | hi)
    return np.concatenate([g[mid], g[lo], g[hi], g[np.isfinite(DA_o)], g[np.isfinite(f110_o)],
                           g[np.isfinite(f101_o)]])


def fit(rec, obs, th0, censor=True):
    lo = th0 - np.array([4, 150, 4, 150, 2, 4, 150, 4, 150, 0])
    hi = th0 + np.array([4, 150, 4, 150, 2, 4, 150, 4, 150, 0])
    lo[[1, 3, 6, 8]] = np.maximum(lo[[1, 3, 6, 8]], 40)
    lo[9], hi[9] = 0.0, 14.9
    t0 = time.time()
    res = least_squares(residuals, th0, args=(rec, obs, censor), bounds=(lo, hi),
                        x_scale=np.array([1, 30, 1, 30, 0.5, 1, 30, 1, 30, 2]), diff_step=1e-3, max_nfev=200)
    J = res.jac
    dof = max(len(res.fun) - len(th0), 1)
    s2 = float(2 * res.cost / dof)
    Hinv = np.linalg.pinv(J.T @ J)
    cov_naive = s2 * Hinv
    # crucibles of one furnace run share its temperature offset: cluster-robust (sandwich) covariance
    g = residual_groups(rec, obs)
    U = np.array([J[g == k].T @ res.fun[g == k] for k in np.unique(g)])
    G = len(U)
    cov = Hinv @ (U.T @ U) @ Hinv * G / max(G - 1, 1)
    return dict(theta=res.x, se=np.sqrt(np.clip(np.diag(cov), 0, None)), cov=cov,
                se_naive=np.sqrt(np.clip(np.diag(cov_naive), 0, None)), s2=s2, n=len(res.fun),
                seconds=time.time() - t0, nfev=res.nfev)


def crucibles(ds, runs):
    """Nominal recipes and patterns of every crucible in the given runs."""
    C = ds.meta["n_channels"]
    u = ds.meta["recipes"]
    idx = (np.asarray(runs)[:, None] * FU.N_SLOTS + np.arange(FU.N_SLOTS)[None, :]).ravel()
    rec = V.recipe(u[idx])
    rec["run"] = idx // FU.N_SLOTS
    I = FU.blocks(ds.oracle.truth(np.asarray(runs)), C).reshape(-1, C)
    return rec, I, idx


def main(n_campaigns=5):
    OUT.mkdir(parents=True, exist_ok=True)
    truth = theta_of(V.P)
    th0 = truth + np.array([1.5, -60, -1.5, 60, 0.5, 1.0, -50, -1.0, 50, 0.0])   # deliberately poor start
    th0[9] = 2.0
    out = dict(truth=truth.tolist(), names=NAMES, units=UNITS, start=th0.tolist(), fits={})
    worlds = {"world A": FU.load(blocks_=(8, 8, 16, 32), model="v2"),
              "world B": FU.load(truth_seed=11, blocks_=(8, 8, 16, 32), model="v2")}
    for wname, ds in worlds.items():
        sigma = FU.noise_sigma(ds)
        sets = {"full design": np.arange(ds.n), "seed levels": np.flatnonzero(ds.levels <= 1)}
        for s_ in range(n_campaigns if wname == "world A" else 2):
            res = run_campaign(ds, FU.config(ds, target="size", seed=s_))
            sets[f"campaign {s_}"] = np.flatnonzero(res.measured)
        rec, I, idx = crucibles(ds, np.arange(ds.n))
        obs_all = observables(I, sigma)
        st = ds.meta["state"]
        ok = np.isfinite(obs_all[0])
        out.setdefault("observable_check", {})[wname] = dict(
            w_rmse=float(np.sqrt(np.mean((obs_all[0][ok] - st["f_R"][idx][ok]) ** 2))),
            DA_used=int(np.isfinite(obs_all[1]).sum()), R110_used=int(np.isfinite(obs_all[2]).sum()),
            R101_used=int(np.isfinite(obs_all[3]).sum()), n=len(idx))
        for name, runs in sets.items():
            sel = (np.asarray(runs)[:, None] * FU.N_SLOTS + np.arange(FU.N_SLOTS)[None, :]).ravel()
            r_ = {k: v[sel] for k, v in rec.items()}
            o_ = tuple(o[sel] for o in obs_all)
            f = fit(r_, o_, th0)
            z = (f["theta"] - truth) / np.maximum(f["se"], 1e-12)
            key = f"{wname} | {name}"
            out["fits"][key] = dict(runs=len(runs), theta=f["theta"].tolist(), se=f["se"].tolist(), z=z.tolist(),
                                    se_naive=f["se_naive"].tolist(),
                                    s2=f["s2"], n_resid=f["n"], seconds=f["seconds"],
                                    corr=(f["cov"] / np.outer(f["se"] + 1e-30, f["se"] + 1e-30)).tolist())
            print(f"{key:28s} {len(runs):3d} runs", " ".join(f"{zz:+5.1f}" for zz in z),
                  "| E", *[f"{f['theta'][k]:.0f}±{f['se'][k]:.0f}" for k in (1, 3, 6, 8)], flush=True)
            (OUT / "fits.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    main()
