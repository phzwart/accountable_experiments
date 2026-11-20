"""
Forward model of a doped-TiO2 calcination campaign (dry-run simulator).

A recipe is a point u in the unit 4-cube, mapped to
    calcination temperature T = 500 + 500 u0   (degC)
    dwell time            t = 2 ** (4 u1)      (h, 1 to 16 h)
    inhibiting dopant     c = 0.10 u2          (cation fraction)
    rutile seed           s = 0.05 u3          (mass fraction of rutile in the precursor)

Physics (literature-anchored, simplified; see README.md):
- Anatase -> rutile by Avrami (JMAK) kinetics with Arrhenius rate, n = 1.5, activation
  energy 165.6 kJ/mol for undoped nanocrystalline anatase (Zhang & Banfield 1999),
  calibrated so that undoped, unseeded anatase is half transformed after 4 h at 750 degC.
- An inhibiting dopant raises the activation energy, saturating with content
  (Hanaor & Sorrell 2011): dE = 30 c / (c + 0.03) kJ/mol.
- Rutile seeds bypass nucleation and grow into the anatase (growth term ~ s^(2/3),
  E = 120 kJ/mol), calibrated so that 5 % seed gives half conversion after 4 h at 680 degC.
- Crystallite growth D^3 - D0^3 = K t exp(-Q/RT) for anatase (D0 = 12 nm, 40 nm after
  4 h at 750 degC; the dopant also slows growth) and rutile (D0 = 30 nm, 80 nm after
  4 h at 800 degC).
- Powder pattern, Cu K-alpha1, 2theta 20-60 deg in 0.02 deg steps: reflections from
  pymatgen for anatase and rutile (reflections.json), scaled per unit mass, pseudo-Voigt
  peaks broadened by size (Scherrer), microstrain and the instrument; smooth background;
  Poisson counting noise.
- Synthesis scatter: each recipe realisation draws lognormal jitter on the rate constants
  and a furnace temperature offset; recipes sharing a furnace run share the offset.

Every realisation is reproducible from (recipe index, seed).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

R_GAS = 8.314462618e-3  # kJ / mol / K
LAMBDA_NM = 0.1540562
_REF = json.loads((Path(__file__).with_name("reflections.json")).read_text())
A101, R110 = 25.31, 27.44


@dataclass
class Params:
    # transformation
    n_avrami: float = 1.5
    E_nuc: float = 165.6
    T50_nuc: float = 750.0
    E_seed: float = 120.0
    T50_seed: float = 680.0
    s_ref: float = 0.05
    dE_max: float = 30.0
    c_half: float = 0.03
    # growth
    D0_A: float = 12.0
    D_A_ref: float = 40.0
    T_A_ref: float = 750.0
    Q_A: float = 150.0
    dQ_max: float = 40.0
    D0_R: float = 30.0
    D_R_ref: float = 80.0
    T_R_ref: float = 800.0
    Q_R: float = 180.0
    t_ref_h: float = 4.0
    # pattern
    tth_min: float = 20.0
    tth_max: float = 60.0
    step: float = 0.02
    inst_fwhm: float = 0.05
    eta: float = 0.5
    strain0: float = 2e-3
    area_scale: float = 3000.0    # counts * deg of the strongest reflection of a pure phase (mass-weighted)
    bg0: float = 300.0
    bg1: float = 150.0
    # scatter
    jitter_sd: float = 0.15
    furnace_sd: float = 4.0


P = Params()


def recipe(u: np.ndarray):
    u = np.atleast_2d(np.asarray(u, float))
    return dict(T=500.0 + 500.0 * u[:, 0], t=2.0 ** (4.0 * u[:, 1]), c=0.10 * u[:, 2], s=0.05 * u[:, 3])


def axis(p: Params = P) -> np.ndarray:
    n = int(round((p.tth_max - p.tth_min) / p.step)) + 1
    return np.linspace(p.tth_min, p.tth_max, n)


def _arr(E, T_K, T50_K):
    return np.exp(-E / R_GAS * (1.0 / T_K - 1.0 / T50_K))


def state(u, jitter=None, dT=None, p: Params = P):
    """Rutile mass fraction and crystallite sizes (nm) for recipes u (n, 4)."""
    r = recipe(u)
    n = len(r["T"])
    jit = np.ones((n, 4)) if jitter is None else np.asarray(jitter, float)
    T_K = r["T"] + 273.15 + (0.0 if dT is None else np.asarray(dT, float))
    tr = r["t"] / p.t_ref_h
    dE = p.dE_max * r["c"] / (r["c"] + p.c_half)
    # nucleation term (k t)^n with k t = (ln 2)^(1/n) at the reference point
    kt = np.log(2.0) ** (1.0 / p.n_avrami) * tr * _arr(p.E_nuc, T_K, p.T50_nuc + 273.15) \
        * np.exp(-dE / (R_GAS * T_K)) * jit[:, 0]
    # seed-growth term
    G = np.log(2.0) * (r["s"] / p.s_ref) ** (2.0 / 3.0) * tr * _arr(p.E_seed, T_K, p.T50_seed + 273.15) \
        * np.exp(-dE / (R_GAS * T_K)) * jit[:, 1]
    X = 1.0 - np.exp(-(kt ** p.n_avrami + G))
    f_R = r["s"] + (1.0 - r["s"]) * X
    dQ = p.dQ_max * r["c"] / (r["c"] + p.c_half)
    KA = (p.D_A_ref ** 3 - p.D0_A ** 3)
    D_A = (p.D0_A ** 3 + KA * tr * _arr(p.Q_A, T_K, p.T_A_ref + 273.15) * np.exp(-dQ / (R_GAS * T_K)) * jit[:, 2]) ** (1 / 3)
    KR = (p.D_R_ref ** 3 - p.D0_R ** 3)
    D_R = (p.D0_R ** 3 + KR * tr * _arr(p.Q_R, T_K, p.T_R_ref + 273.15) * jit[:, 3]) ** (1 / 3)
    strain = p.strain0 * np.exp(-(r["T"] - 500.0) / 150.0)
    return dict(f_R=f_R, X=X, D_A=D_A, D_R=D_R, strain=strain, **r)


def _fwhm_deg(tth, D_nm, strain, p: Params):
    th = np.radians(tth / 2.0)
    size = np.degrees(0.9 * LAMBDA_NM / (D_nm * np.cos(th)))
    st = np.degrees(4.0 * strain * np.tan(th))
    return np.sqrt(size ** 2 + st ** 2 + p.inst_fwhm ** 2)


def _pv(x, x0, fwhm, eta):
    g = np.sqrt(4 * np.log(2) / np.pi) / fwhm * np.exp(-4 * np.log(2) * ((x - x0) / fwhm) ** 2)
    lor = (2 / np.pi) * fwhm / (4 * (x - x0) ** 2 + fwhm ** 2)
    return eta * lor + (1 - eta) * g     # unit area


def pattern(st: dict, rng=None, p: Params = P, noise: bool = True) -> np.ndarray:
    """Counts on axis(p) for each state; Poisson noise if rng is given and noise=True."""
    x = axis(p)
    n = len(st["f_R"])
    out = np.empty((n, len(x)))
    bg = p.bg0 + p.bg1 * np.exp(-(x - p.tth_min) / 10.0)
    for i in range(n):
        y = bg.copy()
        for phase, w, D in (("anatase", 1.0 - st["f_R"][i], st["D_A"][i]), ("rutile", st["f_R"][i], st["D_R"][i])):
            if w <= 0:
                continue
            for tth, rel in _REF[phase]["peaks"]:
                y += p.area_scale * w * rel * _pv(x, tth, _fwhm_deg(tth, D, st["strain"][i], p), p.eta)
        out[i] = y
    if noise and rng is not None:
        out = rng.poisson(out).astype(float)
    return out


def realise(u, seed: int = 0, furnace_key=None, p: Params = P, noise: bool = True):
    """
    One synthesis realisation per recipe: jitter on rates, furnace offset (shared by
    recipes with the same furnace_key), Poisson counts. Returns (patterns, state).
    """
    u = np.atleast_2d(np.asarray(u, float))
    n = len(u)
    rng = np.random.default_rng(seed)
    jitter = np.exp(p.jitter_sd * rng.standard_normal((n, 4)))
    if furnace_key is None:
        dT = p.furnace_sd * rng.standard_normal(n)
    else:
        keys = np.asarray(furnace_key)
        uniq, inv = np.unique(keys, return_inverse=True, axis=0 if keys.ndim > 1 else None)
        off = p.furnace_sd * rng.standard_normal(len(uniq))
        dT = off[np.asarray(inv).ravel()]
    st = state(u, jitter, dT, p)
    st["dT"] = dT
    return pattern(st, rng, p, noise), st
