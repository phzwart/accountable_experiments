"""
Forward model of the synthetic SAXS mixture (F127 / hexanes / water).

Composition (x, y) in the triangle x + y <= 1 maps to a SAXS curve: a
micellar L1 phase, an ordered FCC (I1) phase, a hexagonal (H1) phase and an
oil-rich two-phase emulsion, with sigmoid-smoothed transitions. Carried
over unchanged from the original experiment so that spectra reproduce.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Params:
    # phase boundaries (linear, in wt fractions)
    emu_intercept: float = 0.15   # x_emulsion(y) = a + b*y
    emu_slope: float = 0.55
    odt_intercept: float = 0.42   # y_order(x) = a + b*x
    odt_slope: float = 0.50
    hex_intercept: float = 0.72   # y_hex(x) = a + b*x
    hex_slope: float = 0.30
    # micelle geometry
    R0: float = 60.0              # dry-micelle radius, Angstrom
    Rmax: float = 95.0            # cap on oil-swollen radius
    swell: float = 1.2            # core swelling strength (volume-based)
    pd: float = 0.08              # relative polydispersity (Gaussian)
    n_pd: int = 15                # quadrature points for polydispersity
    hs_ratio: float = 1.25        # hard-sphere radius / micelle radius
    # thermodynamic-ish knobs
    eta_per_y: float = 0.9        # HS volume fraction per F127 wt frac
    eta_min: float = 0.05
    eta_max: float = 0.45
    odt_width: float = 0.012      # sigmoid width of the ODT (wt frac)
    hex_width: float = 0.012      # sigmoid width of the I1->H1 transition
    # diffraction
    qstar0: float = 0.045         # FCC(111) position at (x, y) = (0, 0.5)
    peak_w0: float = 0.0016       # resolution-limited Bragg width, A^-1
    peak_w_broad: float = 0.004   # extra broadening approaching the ODT
    fcc_ratios: tuple = tuple(np.sqrt(np.array([3, 4, 8, 11, 12]) / 3.0))
    fcc_amps: tuple = (30, 9, 5, 2.5, 1.5)
    hex_ratios: tuple = tuple(np.sqrt(np.array([1, 3, 4, 7])))
    hex_amps: tuple = (40, 8, 5, 2)
    hex_qstar_factor: float = 1.25  # H1 q* relative to FCC q*
    # incoherent-ish extras
    porod_K: float = 4e-8         # Porod amplitude per 0.1 excess oil
    bkg: float = 5e-5             # flat background
    amp_per_y: float = 2.0        # scattering amplitude per F127 wt frac
    amp_floor: float = 0.02


DEFAULTS = Params()


def default_q(n: int = 400) -> np.ndarray:
    """q grid ~0.005 to 0.32 A^-1 (typical lab/synchrotron SAXS window)."""
    return np.logspace(-2.3, -0.5, n)


# ----------------------------------------------------------------------
# Phase boundaries and classification
# ----------------------------------------------------------------------
def x_emulsion(y, p: Params = DEFAULTS):
    return p.emu_intercept + p.emu_slope * np.asarray(y)


def y_order(x, p: Params = DEFAULTS):
    return p.odt_intercept + p.odt_slope * np.asarray(x)


def y_hex(x, p: Params = DEFAULTS):
    return p.hex_intercept + p.hex_slope * np.asarray(x)


def classify(x, y, p: Params = DEFAULTS):
    """Hard phase labels: -1 infeasible, 0 L1, 1 I1, 2 H1, 3 2phi."""
    x, y = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float))
    lab = np.full(x.shape, -1, dtype=int)
    feas = (x >= 0) & (y >= 0) & (x + y <= 1)
    lab[feas] = 0
    lab[feas & (x > x_emulsion(y, p))] = 3
    ordered = feas & (x <= x_emulsion(y, p)) & (y > y_order(x, p))
    lab[ordered] = 1
    lab[ordered & (y > y_hex(x, p))] = 2
    return lab


# ----------------------------------------------------------------------
# Scattering building blocks (broadcast over arbitrary grid shape)
# All take/return arrays shaped (*grid, Nq).
# ----------------------------------------------------------------------
def _sphere_ff(q, R, p: Params):
    """Polydisperse (Gaussian) sphere form factor, peak-normalized."""
    offsets = np.linspace(-3 * p.pd, 3 * p.pd, p.n_pd)
    w = np.exp(-0.5 * (offsets / p.pd) ** 2)
    w /= w.sum()
    P = 0.0
    for d, wi in zip(offsets, w):
        Ri = (R * (1 + d))[..., None]
        xq = q * Ri
        f = 3 * (np.sin(xq) - xq * np.cos(xq)) / xq**3
        P = P + wi * Ri**6 * f**2
    return P / P.max(axis=-1, keepdims=True)


def _s_py(q, Rhs, eta):
    """Percus-Yevick hard-sphere structure factor."""
    x = np.maximum(2 * q * Rhs[..., None], 1e-6)
    e = eta[..., None]
    a = (1 + 2 * e) ** 2 / (1 - e) ** 4
    b = -6 * e * (1 + e / 2) ** 2 / (1 - e) ** 4
    c = e * a / 2
    sx, cx = np.sin(x), np.cos(x)
    G = (a / x**2 * (sx - x * cx)
         + b / x**3 * (2 * x * sx - (x**2 - 2) * cx - 2)
         + c / x**5 * (-x**4 * cx + 4 * ((3 * x**2 - 6) * cx
                       + (x**3 - 6 * x) * sx + 6)))
    return 1.0 / (1.0 + 24 * e * G / x)


def _bragg(q, qstar, width, ratios, amps):
    """Gaussian Bragg comb at q = qstar * ratios."""
    out = 0.0
    qs = qstar[..., None]
    wd = width[..., None]
    for r, A in zip(ratios, amps):
        out = out + A * np.exp(-0.5 * ((q - r * qs) / wd) ** 2)
    return out


def _cyl_envelope(q, R):
    """Crude q^-1 cylinder envelope with a Guinier-like rollover."""
    env = (q * R[..., None]) ** -1 * np.exp(-(q * 12.0) ** 2 / 2)
    return env / env.max(axis=-1, keepdims=True)


# ----------------------------------------------------------------------
# The forward model
# ----------------------------------------------------------------------
def saxs(x, y, q=None, p: Params = DEFAULTS):
    """
    Simulated SAXS intensity for compositions (x, y).

    Parameters
    ----------
    x, y : scalar or array-like (broadcastable to a common shape)
        Hexanes and F127 weight fractions.
    q : 1D array, optional
        Scattering vector grid (A^-1). Defaults to default_q().
    p : Params
        Model parameters.

    Returns
    -------
    I : ndarray, shape (*broadcast(x, y).shape, len(q))
        Intensity (a.u.). NaN where x < 0 or y < 0. Defined on the full
        unit square (including x+y>1) so HiPoSa designs need not be filtered;
        axis/diagonal mirrors are for interpolation only.
    """
    if q is None:
        q = default_q()
    q = np.asarray(q, float)
    x, y = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float))

    sig = lambda z: 1.0 / (1.0 + np.exp(-z))

    oil_in = np.minimum(x, x_emulsion(y, p))        # solubilized oil
    excess = np.clip(x - x_emulsion(y, p), 0, None)  # emulsified oil

    R = np.clip(p.R0 * (1 + p.swell * oil_in / (y + 0.05)) ** (1 / 3),
                None, p.Rmax)
    eta = np.clip(p.eta_per_y * y, p.eta_min, p.eta_max)

    m_odt = y - y_order(x, p)
    A_B = sig(m_odt / p.odt_width)                  # Bragg order parameter
    width = p.peak_w0 + p.peak_w_broad * np.exp(
        -np.clip(m_odt, 0, None) / 0.015)
    A_H = sig((y - y_hex(x, p)) / p.hex_width)      # hexagonal weight

    qstar = p.qstar0 * (p.R0 / R) * (eta / p.eta_max) ** (1 / 3)
    amp = p.amp_per_y * y + p.amp_floor

    P = _sphere_ff(q, R, p)
    S = _s_py(q, p.hs_ratio * R, eta)
    B = ((1 - A_H[..., None])
         * _bragg(q, qstar, width, p.fcc_ratios, p.fcc_amps)
         + A_H[..., None]
         * _bragg(q, qstar * p.hex_qstar_factor, width,
                  p.hex_ratios, p.hex_amps))
    FF = (1 - A_H[..., None]) * P + A_H[..., None] * _cyl_envelope(q, R)

    I = amp[..., None] * FF * ((1 - 0.7 * A_B[..., None]) * S
                               + A_B[..., None] * B)
    I = I + p.porod_K * (excess[..., None] / 0.1) * q ** -4 + p.bkg

    # Keep algebraic continuation on the unit square (x+y>1 allowed).
    # Axis / diagonal mirrors are used only for interpolation, not here.
    outside = (x < 0) | (y < 0)
    I[outside] = np.nan
    return I


# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------
def log_normalize(I, axis=-1):
    """Log10 each spectrum and min-max scale so the peak equals 1."""
    logI = np.log10(np.maximum(I, 1e-30))
    with np.errstate(all="ignore"):
        lo = np.nanmin(logI, axis=axis, keepdims=True)
        hi = np.nanmax(logI, axis=axis, keepdims=True)
    span = np.maximum(hi - lo, 1e-12)
    out = (logI - lo) / span
    out[~np.isfinite(I).any(axis=axis)] = np.nan
    return out


