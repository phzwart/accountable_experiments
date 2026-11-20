"""
Forward model v2: calcination of nano-anatase with a gamma-alumina additive and rutile seeds,
measured by laboratory powder XRD. Literature-anchored; see MODEL_V2.md for sources,
calibration and validation.

Recipe (unit 4-cube, same axes as v1):
    T = 500 + 500 u0 (degC), dwell t = 2 ** (4 u1) h, alumina additive c = 0.10 u2 (mass
    fraction of the sample), and on the fourth axis either a rutile seed s = 0.05 u3 (mass
    fraction of the TiO2; mechanically mixed, contact efficiency 0.1) or, with
    ``fourth="p25"``, a P25 blend b = 0.5 u3 (mass fraction of the TiO2 supplied as P25:
    about 25 nm anatase with 17 % rutile in intimate contact, contact efficiency 1). The two
    TiO2 powders transform independently; cross-contacts are neglected.

Kinetics (state per crucible: anatase mass fraction a of the TiO2, anatase crystallite size
D_A, rutile fraction r = 1 - a, rutile crystallite size D_R), integrated over the full furnace
programme (A-Lab: optional 2 degC/min to 300 degC, 15 degC/min to T, hold, natural cooling):

    da/dt = - k_SN(T, D_A) a - k_IN(T, D_A) (8 nm / D_A)^3 a^2 - k_AR(T) a r (30 nm / D_R) (25 nm / D_A)

- k_IN, k_SN: interface and surface nucleation of rutile in anatase (Zhang & Banfield 1999,
  2000; combined model as in Shakibania 2017). Arrhenius fits to the tabulated 8-nm rate
  constants at 620-690 degC: E_IN = 211.4 kJ/mol, ln A_IN = 26.85 (h^-1); E_SN = 478.2 kJ/mol,
  ln A_SN = 59.8 (h^-1). The (8 nm / D_A)^3 factor is the particle-number dependence of
  interface nucleation (second order in the number of anatase particles).
- Size-dependent activation energy (Zhang & Banfield 2000: "the activation energy of
  nucleation is size dependent"): E(D) = E_8nm + beta ln(D / 8 nm), beta fitted.
- k_AR: growth of rutile into anatase at anatase-rutile contacts (rutile seeds or P25-like
  mixed powders bypass nucleation); prefactor and activation energy fitted.
- Anatase coarsening: d(D^3)/dt = K_A exp(-E_KA/RT), anchored at 690 degC to the coarsening
  constant of the same 8-nm data (D/D0 - 1 = k t^(1/3), k = 0.51 h^-1/3, so K = (8 nm k)^3);
  E_KA = 250 kJ/mol assumed (extrapolating the 620-690 degC fit, 3 x 175 kJ/mol, would grow
  anatase to micrometres at 1000 degC).
- Rutile coarsening: d(D_R^3)/dt = K_R exp(-E_R/RT), anchored to 114 nm after 2 h at 900 degC.
  New rutile enters at the anatase size (mass-weighted mean).
- Alumina additive: dispersed alumina particles reduce anatase-anatase contacts (Zhang &
  Banfield 2000) and pin anatase grain boundaries: factor exp(-c / c_n) on the nucleation and
  contact terms, exp(-c / c_g) on anatase coarsening. c_n is set so that 5 wt% gives the
  7-24x rate reduction reported for alumina-containing anatase at 640-680 degC (alumina
  content not given there; 5 wt% assumed).

XRD: Cu K-alpha1/K-alpha2 (ratio 0.5), Caglioti instrument width, Scherrer size broadening
(Lorentzian) and microstrain (Gaussian) combined by the Thompson-Cox-Hastings pseudo-Voigt,
sample displacement shift, overall intensity scale (packing, amount), background from air
and holder, Ti fluorescence under Cu radiation (partly suppressed by the detector), Poisson
counts. Reflections per unit mass from pymatgen structures (reflections_v2.json).

Synthesis scatter: dosing error on additive and seed, per-run furnace offset, temperature
gradient across the tray, crucible-to-crucible jitter on rates, rare failed crucibles.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

R_GAS = 8.314462618e-3
LAMBDA1, LAMBDA2 = 1.540562, 1.544390      # Angstrom
_REF = json.loads(Path(__file__).with_name("reflections_v2.json").read_text())
A101, R110 = 25.306, 27.435


@dataclass
class Params:
    # precursor
    D0_A: float = 20.0            # nm, nano-anatase precursor (median of the mass distribution)
    sigma_ln: float = 0.35        # lognormal width of the precursor size distribution (assumed)
    n_classes: int = 7
    D_seed: float = 60.0          # nm, rutile seed powder
    r_impurity: float = 0.0       # rutile already in the precursor
    # nucleation (8-nm reference, Arrhenius fits to Zhang & Banfield data)
    E_IN: float = 211.4
    lnA_IN: float = 18.85         # fitted (Arrhenius fit to the table: 26.85)
    E_SN: float = 478.2
    lnA_SN: float = 58.385        # fitted (Arrhenius fit to the table: 59.8)
    beta: float = 57.41           # kJ/mol per e-fold of D_A (fitted, see MODEL_V2.md)
    # anatase-rutile contact growth
    E_AR: float = 231.37          # fitted
    lnA_AR: float = 28.05         # fitted
    phi_contact: float = 0.1      # contact efficiency of rutile with anatase: 1 for intimate (P25-like),
                                  # 0.1 assumed for mechanically mixed seeds or separate impurity rutile
    # coarsening
    K_A_690: float = 67.9         # nm^3/h at 690 degC: (8 nm x 0.51 h^-1/3)^3 from the Zhang-Banfield table
    E_KA: float = 250.0           # kJ/mol for d(D^3)/dt; assumed (sintering range), anchored at 690 degC
    E_R: float = 300.0
    K_R_900: float = 7.3e5        # nm^3/h at 900 degC
    D_R_new_min: float = 25.0
    # alumina additive
    c_n: float = 0.022
    c_g: float = 0.05
    # furnace programme
    slow_ramp: bool = True
    ramp_fast: float = 15.0       # degC/min
    tau_cool: float = 1.8         # h
    dt_min: float = 1.0
    # XRD
    tth_min: float = 20.0
    tth_max: float = 60.0
    step: float = 0.02
    U: float = 0.0040
    V: float = -0.0020
    W: float = 0.0020
    K_scherrer: float = 0.94
    strain_A0: float = 2e-3
    strain_R: float = 5e-4
    D_gamma: float = 5.0          # nm, gamma-alumina crystallites
    R_gonio: float = 200.0        # mm
    displacement_sd: float = 0.05 # mm
    scale_sd: float = 0.08
    area_scale: float = 3000.0
    bg_air: float = 120.0
    bg_fluor: float = 250.0
    bg_low: float = 150.0
    # synthesis scatter
    dose_rel_sd: float = 0.03
    furnace_sd: float = 5.0
    tray_gradient: float = 0.8    # degC per slot from the tray centre
    rate_sd: float = 0.10
    p_fail: float = 0.005


P = Params()


FOURTH = "p25"        # "seed" or "p25"


def recipe(u, fourth=None):
    u = np.atleast_2d(np.asarray(u, float))
    f = fourth or FOURTH
    out = dict(T=500.0 + 500.0 * u[:, 0], t=2.0 ** (4.0 * u[:, 1]), c=0.10 * u[:, 2])
    if f == "p25":
        out["s"] = np.zeros(len(u))
        out["b"] = 0.5 * u[:, 3]
    else:
        out["s"] = 0.05 * u[:, 3]
        out["b"] = np.zeros(len(u))
    return out


def axis(p: Params = P):
    n = int(round((p.tth_max - p.tth_min) / p.step)) + 1
    return np.linspace(p.tth_min, p.tth_max, n)


def programme(T_set, dwell_h, p: Params = P):
    """Time grid (h) and temperature (degC) for each crucible; common grid, padded at room temperature."""
    T_set = np.atleast_1d(np.asarray(T_set, float))
    dwell_h = np.atleast_1d(np.asarray(dwell_h, float))
    if p.slow_ramp:
        t1 = (300.0 - 25.0) / 2.0 / 60.0
        t2 = t1 + np.maximum(T_set - 300.0, 0.0) / p.ramp_fast / 60.0
    else:
        t1 = 0.0
        t2 = (T_set - 25.0) / p.ramp_fast / 60.0
    t3 = t2 + dwell_h
    t_cool = p.tau_cool * np.log((T_set - 25.0) / 75.0)
    t_end = float(np.max(t3 + t_cool))
    dt = p.dt_min / 60.0
    tg = np.arange(0.0, t_end + dt, dt)
    TT = np.empty((len(T_set), len(tg)))
    for i in range(len(T_set)):
        if p.slow_ramp:
            Tt = np.where(tg < t1, 25.0 + tg / t1 * 275.0, 300.0 + (tg - t1) * 60.0 * p.ramp_fast)
        else:
            Tt = 25.0 + tg * 60.0 * p.ramp_fast
        Tt = np.where((tg >= t2[i]) & (tg < t3[i]), T_set[i], Tt)
        Tt = np.where(tg >= t3[i], 25.0 + (T_set[i] - 25.0) * np.exp(-(tg - t3[i]) / p.tau_cool), Tt)
        TT[i] = np.minimum(Tt, T_set[i])
    return tg, TT


def integrate(T_set, dwell_h, c, s, rate_jit=None, p: Params = P, r0=None):
    """
    Integrate the kinetics over the furnace programme; returns final state arrays.
    The precursor is a lognormal mass distribution of anatase sizes, split into
    ``n_classes`` equal-mass classes that transform and coarsen independently; rutile seeds
    and newly formed rutile are shared.
    """
    from scipy.stats import norm
    T_set = np.atleast_1d(np.asarray(T_set, float))
    n = len(T_set)
    K = int(p.n_classes)
    c = np.broadcast_to(np.asarray(c, float), (n,)).copy()
    s = np.broadcast_to(np.asarray(s, float), (n,)).copy()
    jit = np.ones((n, 3)) if rate_jit is None else np.asarray(rate_jit, float)
    tg, TT = programme(T_set, np.broadcast_to(np.asarray(dwell_h, float), (n,)), p)
    dt = tg[1] - tg[0]
    r_init = s + (1 - s) * p.r_impurity if r0 is None else np.asarray(r0, float)
    z = norm.ppf((np.arange(K) + 0.5) / K) if K > 1 else np.zeros(1)
    a = np.repeat(((1.0 - r_init) / K)[:, None], K, axis=1)           # anatase mass per class
    DA = p.D0_A * np.exp(p.sigma_ln * z)[None, :] * np.ones((n, 1))
    r = r_init.copy()
    DR = np.full(n, p.D_seed)
    inh_n = np.exp(-c / p.c_n)[:, None]
    inh_g = np.exp(-c / p.c_g)[:, None]
    for j in range(len(tg)):
        T = (TT[:, j] + 273.15)[:, None]
        hot = (TT[:, j] > 350.0)[:, None]
        if not hot.any():
            continue
        lnD = np.log(DA / 8.0)
        kIN = np.exp(p.lnA_IN - (p.E_IN + p.beta * lnD) / (R_GAS * T)) * inh_n * jit[:, :1]
        kSN = np.exp(p.lnA_SN - (p.E_SN + p.beta * lnD) / (R_GAS * T)) * inh_n * jit[:, 1:2]
        kAR = p.phi_contact * np.exp(p.lnA_AR - p.E_AR / (R_GAS * T)) * inh_n * jit[:, 2:3]
        atot = a.sum(axis=1, keepdims=True)
        # per-class mass rates; class mass a_k, interface term uses the class's own particle number
        rate = kSN * a + kIN * (8.0 / DA) ** 3 * a * atot + kAR * a * r[:, None] * (30.0 / DR[:, None]) * (25.0 / DA)
        da = np.minimum(rate * dt, a) * hot
        new = da.sum(axis=1)
        newD3 = (da * np.maximum(DA, p.D_R_new_min) ** 3).sum(axis=1) / np.maximum(new, 1e-15)
        DR3 = np.where(new > 0, (r * DR ** 3 + new * newD3) / np.maximum(r + new, 1e-12), DR ** 3)
        KR = p.K_R_900 * np.exp(-p.E_R / R_GAS * (1.0 / T[:, 0] - 1.0 / 1173.15))
        DR = np.cbrt(DR3 + KR * dt * hot[:, 0])
        KA = p.K_A_690 * np.exp(-p.E_KA / R_GAS * (1.0 / T - 1.0 / 963.15))
        DA = np.cbrt(DA ** 3 + KA * dt * inh_g * hot)
        a = a - da
        r = r + new
    atot = a.sum(axis=1)
    DA_mean = np.where(atot > 1e-9, (a * DA).sum(axis=1) / np.maximum(atot, 1e-12), DA.mean(axis=1))
    return dict(a=atot, f_R=1.0 - atot, D_A=DA_mean, D_R=DR, T=T_set, c=c, s=s)


def _tch(G, L):
    G5 = G ** 5
    Gam = (G5 + 2.69269 * G ** 4 * L + 2.42843 * G ** 3 * L ** 2 + 4.47163 * G ** 2 * L ** 3
           + 0.07842 * G * L ** 4 + L ** 5) ** 0.2
    q = L / Gam
    eta = 1.36603 * q - 0.47719 * q ** 2 + 0.11116 * q ** 3
    return Gam, np.clip(eta, 0.0, 1.0)


def _pv(x, x0, fwhm, eta):
    g = np.sqrt(4 * np.log(2) / np.pi) / fwhm * np.exp(-4 * np.log(2) * ((x - x0) / fwhm) ** 2)
    lor = (2 / np.pi) * fwhm / (4 * (x - x0) ** 2 + fwhm ** 2)
    return eta * lor + (1 - eta) * g


def components(st, p: Params = P):
    """Phase components (name, mass fraction of the sample, crystallite size, strain) per crucible."""
    out = []
    n = len(st["a"])
    for i in range(n):
        tio2 = 1.0 - st["c"][i]
        strainA = p.strain_A0 * np.exp(-(st["T"][i] - 500.0) / 150.0)
        comp = []
        for pre in ("", "p25_"):
            w = st.get(pre + "w", np.ones(n) if pre == "" else np.zeros(n))[i]
            if w <= 0:
                continue
            comp.append(("anatase", tio2 * w * st[pre + "a"][i], st[pre + "D_A"][i], strainA))
            comp.append(("rutile", tio2 * w * (1.0 - st[pre + "a"][i]), st[pre + "D_R"][i], p.strain_R))
        comp.append(("gamma_alumina", st["c"][i], p.D_gamma, 0.0))
        out.append(comp)
    return out


def pattern(st, rng=None, p: Params = P, noise=True, extras=None):
    """Counts on axis(p). ``extras`` holds per-crucible displacement, scale and failure flags."""
    x = axis(p)
    n = len(st["a"])
    ex = extras or {}
    disp = ex.get("disp", np.zeros(n))
    scale = ex.get("scale", np.ones(n))
    fail = ex.get("fail", np.zeros(n, bool))
    out = np.empty((n, len(x)))
    bg = p.bg_air + p.bg_low * np.exp(-(x - p.tth_min) / 8.0)
    comps = components(st, p)
    for i in range(n):
        y = bg + p.bg_fluor * (1.0 - st["c"][i])
        sig = 0.0 * x
        for ph, w, D, eps in comps[i]:
            if w <= 1e-6:
                continue
            for tth, rel, _ in _REF[ph]["peaks"]:
                for lam, frac in ((LAMBDA1, 2.0 / 3.0), (LAMBDA2, 1.0 / 3.0)):
                    sin_th = np.sin(np.radians(tth / 2.0)) * lam / LAMBDA1
                    if sin_th >= 1:
                        continue
                    th = np.arcsin(sin_th)
                    tth_l = np.degrees(2 * th)
                    shift = -np.degrees(2.0 * disp[i] * np.cos(th) / p.R_gonio)
                    L = np.degrees(p.K_scherrer * LAMBDA1 / 10.0 / (D * np.cos(th)))
                    G = np.sqrt(max(p.U * np.tan(th) ** 2 + p.V * np.tan(th) + p.W, 1e-6) + np.degrees(4 * eps * np.tan(th)) ** 2)
                    fw, eta = _tch(G, L)
                    sig = sig + p.area_scale * w * rel * frac * _pv(x, tth_l + shift, fw, eta)
        out[i] = y + sig * scale[i] * (0.15 if fail[i] else 1.0)
    if noise and rng is not None:
        out = rng.poisson(out).astype(float)
    return out


def realise(u, seed=0, furnace_key=None, slot=None, p: Params = P, noise=True):
    """One synthesis realisation per recipe. ``furnace_key`` groups crucibles of one run;
    ``slot`` (0-7) places a crucible on the tray for the temperature gradient."""
    u = np.atleast_2d(np.asarray(u, float))
    n = len(u)
    rng = np.random.default_rng(seed)
    r = recipe(u)
    c = r["c"] * np.exp(p.dose_rel_sd * rng.standard_normal(n))
    s = r["s"] * np.exp(p.dose_rel_sd * rng.standard_normal(n))
    if furnace_key is None:
        dT = p.furnace_sd * rng.standard_normal(n)
    else:
        keys = np.asarray(furnace_key)
        uniq, inv = np.unique(keys, return_inverse=True, axis=0 if keys.ndim > 1 else None)
        dT = (p.furnace_sd * rng.standard_normal(len(uniq)))[np.asarray(inv).ravel()]
    if slot is not None:
        dT = dT + p.tray_gradient * (np.asarray(slot, float) - 3.5)
    jit = np.exp(p.rate_sd * rng.standard_normal((n, 3)))
    b = r["b"] * np.exp(p.dose_rel_sd * rng.standard_normal(n))
    st = integrate(r["T"] + dT, r["t"], c, s, jit, p)
    st["w"] = 1.0 - b
    if np.any(b > 0):
        import dataclasses
        q = dataclasses.replace(p, D0_A=25.0, D_seed=40.0, r_impurity=0.17, phi_contact=1.0)
        sp = integrate(r["T"] + dT, r["t"], c, 0.0, jit, q)
        st.update({"p25_" + k: sp[k] for k in ("a", "D_A", "D_R")})
        st["p25_w"] = b
        st["f_R"] = (1.0 - b) * st["f_R"] + b * sp["f_R"]
    st["b"] = b
    st["T"] = r["T"] + dT
    st["dT"] = dT
    extras = dict(disp=p.displacement_sd * rng.standard_normal(n),
                  scale=np.exp(p.scale_sd * rng.standard_normal(n)),
                  fail=rng.random(n) < p.p_fail)
    st.update({f"x_{k}": v for k, v in extras.items()})
    return pattern(st, rng, p, noise, extras), st
