"""
Calibrate and validate forward model v2 against published anchors.

    python -m experiments.tio2_calcination.calibrate_v2

Fitted: beta (size dependence of the nucleation activation energy), ln A_AR and E_AR
(anatase-rutile contact growth, for intimate contact as in P25; mechanically mixed seeds and
separate impurity rutile get a contact efficiency of 0.1, an assumption). Anchors (rutile mass fraction):
  A1 coarse commercial anatase (~160 nm from 9.7 m2/g, 4 % rutile), 3 degC/min, 6 h:
     8.5 / 23 / 51 / 80 / 98 % at 900 / 925 / 950 / 975 / 1000 degC (Naresuan 2015 study)
  A2 P25 (about 17 % rutile, about 25 nm anatase), 5 degC/min, 3 h:
     68 % at 700 degC, 98 % at 750 degC (Ishigaki et al.)
  A3 pure commercial nano-anatase (20 nm assumed): only textural changes up to 700 degC, 8 h
     (target <= 5 % rutile; Patras study)
  A4 Zhang-Banfield 8-nm anatase, 2 h isothermal at 620-690 degC: alpha from their combined
     nucleation model with the tabulated constants (4 / 7 / 20 / 56 / 68 %)
Also fitted: offsets of ln A_IN and ln A_SN from the Arrhenius fits to the tabulated rates.
Checks (not fitted): heating-rate effect at fixed soak
(faster heating gives more rutile, 620-700 degC); alumina inhibition; rutile size at 900 degC.
"""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

from . import forward_v2 as V

OUT = Path("results/tio2")


def run(p, T, dwell, D0, r_imp, ramp, c=0.0, s=0.0, D_seed=None, slow=False, phi=None):
    q = dataclasses.replace(p, D0_A=D0, r_impurity=r_imp, ramp_fast=ramp, slow_ramp=slow,
                            D_seed=D_seed if D_seed is not None else p.D_seed,
                            phi_contact=phi if phi is not None else p.phi_contact)
    return V.integrate(np.asarray(T, float), dwell, c, s, None, q)


ANCHORS = [
    ("A1", dict(T=[900, 925, 950, 975, 1000], dwell=6.0, D0=160.0, r_imp=0.04, ramp=3.0, D_seed=160.0, phi=0.1),
     [0.085, 0.2308, 0.5063, 0.80, 0.9783]),
    ("A2", dict(T=[700, 750], dwell=3.0, D0=25.0, r_imp=0.17, ramp=5.0, D_seed=40.0, phi=1.0), [0.68, 0.98]),
    # A4: Zhang-Banfield 8-nm anatase, 2 h isothermal: the combined interface+surface nucleation
    # curves with their tabulated constants (as re-fitted by Shakibania 2017)
    ("A4", dict(T=[620, 640, 660, 680, 690], dwell=2.0, D0=8.0, r_imp=0.0, ramp=100.0), [0.040, 0.072, 0.202, 0.555, 0.678]),
]


def logit(x):
    x = np.clip(x, 1e-3, 1 - 1e-3)
    return np.log(x / (1 - x))


def params(theta, p0):
    beta, lnA_AR, E_AR, d_IN, d_SN = theta
    return dataclasses.replace(p0, beta=beta, lnA_AR=lnA_AR, E_AR=E_AR,
                               lnA_IN=26.85 + d_IN, lnA_SN=59.8 + d_SN)


def residuals(theta, p0):
    p = params(theta, p0)
    res = []
    for _, kw, tgt in ANCHORS:
        f = run(p, **kw)["f_R"]
        res.extend(logit(f) - logit(np.asarray(tgt)))
    f3 = run(p, [700.0], 8.0, 20.0, 0.0, 5.0)["f_R"][0]
    res.append(max(0.0, logit(f3) - logit(0.03)))
    return np.asarray(res)


def main():
    p0 = V.P
    fit = least_squares(residuals, x0=[60.0, 25.0, 200.0, 0.0, 0.0], args=(p0,),
                        bounds=([0.0, 0.0, 60.0, -8.0, -8.0], [250.0, 80.0, 500.0, 8.0, 8.0]))
    p = params(fit.x, p0)
    rep = dict(beta=p.beta, lnA_AR=p.lnA_AR, E_AR=p.E_AR, lnA_IN=p.lnA_IN, lnA_SN=p.lnA_SN,
               cost=float(fit.cost))
    for name, kw, tgt in ANCHORS:
        rep[name] = dict(T=kw["T"], target=tgt, model=[round(float(v), 3) for v in run(p, **kw)["f_R"]])
    rep["A3_700C_8h_20nm"] = round(float(run(p, [700.0], 8.0, 20.0, 0.0, 5.0)["f_R"][0]), 3)
    # checks
    T = [620.0, 660.0, 700.0]
    slow = run(p, T, 2.0, 20.0, 0.0, 50 / 60.0)["f_R"]
    fast = run(p, T, 2.0, 20.0, 0.0, 300 / 60.0)["f_R"]
    rep["heating_rate_check_20nm_2h"] = dict(T=T, rate_50_per_h=[round(float(v), 3) for v in slow],
                                             rate_300_per_h=[round(float(v), 3) for v in fast])
    zb = run(p, [620, 640, 660, 680, 690], 4.0, 8.0, 0.0, 15.0)["f_R"]
    rep["zhang_banfield_8nm_4h"] = [round(float(v), 3) for v in zb]
    al0 = run(p, [660.0], 4.0, 8.0, 0.0, 15.0, c=0.0)["f_R"][0]
    al5 = run(p, [660.0], 4.0, 8.0, 0.0, 15.0, c=0.05)["f_R"][0]
    rep["alumina_check_8nm_660C_4h"] = dict(c0=round(float(al0), 3), c5=round(float(al5), 3))
    r900 = run(p, [900.0], 2.0, 20.0, 0.0, 15.0)
    rep["rutile_size_900C_2h_nm"] = round(float(r900["D_R"][0]), 1)
    grid = {}
    for c in (0.0, 0.05, 0.10):
        for s in (0.0, 0.03):
            st = run(p, np.arange(500, 1001, 50), 4.0, 20.0, 0.0, 15.0, c=c, s=s, slow=True)
            grid[f"c{c}_s{s}"] = dict(f_R=[round(float(v), 2) for v in st["f_R"]], D_A=[round(float(v)) for v in st["D_A"]],
                                      D_R=[round(float(v)) for v in st["D_R"]])
    rep["A-Lab_programme_4h_T500-1000"] = grid
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "model_v2_calibration.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
