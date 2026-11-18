"""
Spectral descriptors and acceptance criteria.

A criterion turns a true spectrum and a predicted spectrum into a score s
with the convention s <= 1 accepts. Three kinds are provided: the
full-profile rtol/atol envelope, the dominant-peak descriptors (position,
width, presence) and the integrated intensity. The functions are carried
over unchanged from the original experiments so labels reproduce.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

def envelope_violation_stats(
    I_true: np.ndarray,
    I_hat: np.ndarray,
    rtol: float = 0.02,
    atol: float = 0.1,
    signal_min: float = None,
):
    """
    Per-spectrum accounting vs the rtol/atol envelope.

    If ``signal_min`` is set, the mean is taken only over channels where the
    measured spectrum is at least that large. A spectrum with no such channel
    scores 0: there is no signal the interpolant is required to match.

    Returns
    -------
    score : (n,) mean ρ over the channels that count
    outside_mean : (n,) bool — score > 1 (mean envelope breach)
    outside_any : (n,) bool — any counted channel with ρ > 1
    frac_q_out : (n,) fraction of counted channels with ρ > 1
    rho_max : (n,) max ρ over counted channels
    """
    I_true = np.asarray(I_true, float)
    I_hat = np.asarray(I_hat, float)
    denom = rtol * np.abs(I_true) + atol
    rho = np.abs(I_hat - I_true) / np.maximum(denom, 1e-30)
    if signal_min is None:
        use = np.ones(rho.shape, dtype=bool)
    else:
        use = I_true >= float(signal_min)
    counts = use.sum(axis=-1)
    rho_used = np.where(use, rho, 0.0)
    score = np.zeros(rho.shape[0], float)
    np.divide(rho_used.sum(axis=-1), counts, out=score, where=counts > 0)
    breach = (rho > 1.0) & use
    outside_any = np.any(breach, axis=-1)
    frac_q_out = np.zeros(rho.shape[0], float)
    np.divide(breach.sum(axis=-1), counts, out=frac_q_out, where=counts > 0)
    rho_max = np.max(np.where(use, rho, 0.0), axis=-1)
    return dict(
        score=score,
        outside_mean=score > 1.0,
        outside_any=outside_any,
        frac_q_out=frac_q_out,
        rho_max=rho_max,
    )


# ----------------------------------------------------------------------
# Peak-feature acceptance criterion (q of dominant peak + its FWHM)
# ----------------------------------------------------------------------
def peak_descriptors(
    I: np.ndarray,
    q: np.ndarray,
    min_prominence: float = 0.0,
    q_center: float = None,
    q_halfwidth: float = None,
):
    """
    Locate the dominant peak of each spectrum and measure its width.

    The dominant peak is the tallest interior local maximum of I(q).
    If ``q_center`` is set, only maxima inside
    ``[q_center − q_halfwidth, q_center + q_halfwidth]`` compete, so a
    chosen reflection can be tracked while it wobbles. Its
    position is refined below the grid spacing by a parabolic fit to
    log I vs log q (the q grid is log-spaced, and at ``default_q(240)`` one
    bin is already ~1.7% in q, so raw ``argmax`` cannot resolve a 1% test).

    Width is the full width at half maximum taken *above a local baseline*:
    the baseline is the higher of the two local minima flanking the peak, and
    the half level is midway between that baseline and the peak. This keeps
    the width meaningful for a Bragg peak riding on a Porod or structure-factor
    background. FWHM is NaN when the flanks never fall to the half level.

    Returns a dict of per-spectrum arrays: ``q_peak``, ``fwhm``, ``height``,
    ``prominence`` ((I_peak - baseline)/baseline) and ``has_peak``.
    """
    I = np.asarray(I, float)
    I2 = np.atleast_2d(I)
    q = np.asarray(q, float)
    lq = np.log(q)
    n, nb = I2.shape

    q_peak = np.full(n, np.nan)
    fwhm = np.full(n, np.nan)
    height = np.full(n, np.nan)
    height_above_base = np.full(n, np.nan)
    prominence = np.full(n, np.nan)
    has_peak = np.zeros(n, bool)
    if nb < 3:
        out = dict(q_peak=q_peak, fwhm=fwhm, height=height,
                   height_above_base=height_above_base,
                   prominence=prominence, has_peak=has_peak)
        return out

    core = I2[:, 1:-1]
    is_max = np.zeros((n, nb), bool)
    is_max[:, 1:-1] = (core > I2[:, :-2]) & (core > I2[:, 2:])
    is_min = np.zeros((n, nb), bool)
    is_min[:, 1:-1] = (core <= I2[:, :-2]) & (core < I2[:, 2:])
    finite = np.all(np.isfinite(I2), axis=1)

    for r in range(n):
        if not finite[r]:
            continue
        loc = np.flatnonzero(is_max[r])
        if q_center is not None:
            half = 0.5 if q_halfwidth is None else float(q_halfwidth)
            loc = loc[(q[loc] >= float(q_center) - half) & (q[loc] <= float(q_center) + half)]
        if loc.size == 0:
            continue
        y = I2[r]
        i = int(loc[np.argmax(y[loc])])

        # Flanking local minima bracket the peak; y is monotone on each side.
        mins = np.flatnonzero(is_min[r])
        left = mins[mins < i]
        right = mins[mins > i]
        lo = int(left[-1]) if left.size else 0
        hi = int(right[0]) if right.size else nb - 1

        base = max(y[lo], y[hi])
        peak = y[i]
        if peak <= base:
            continue
        prom = (peak - base) / max(abs(base), 1e-30)
        prominence[r] = prom
        if prom < min_prominence:
            continue

        has_peak[r] = True
        height[r] = peak
        height_above_base[r] = float(peak - base)

        # sub-bin peak position: parabola through log I vs log q
        shift = 0.0
        if 0 < i < nb - 1:
            ly = np.log(np.maximum(y[i - 1:i + 2], 1e-300))
            denom = ly[0] - 2.0 * ly[1] + ly[2]
            if denom != 0.0:
                shift = float(np.clip(0.5 * (ly[0] - ly[2]) / denom, -1.0, 1.0))
        step = lq[i + 1] - lq[i] if i < nb - 1 else lq[i] - lq[i - 1]
        q_peak[r] = float(np.exp(lq[i] + shift * step))

        # FWHM above the local baseline, crossings interpolated in log q
        half = 0.5 * (peak + base)
        left_arm = y[lo:i + 1]                      # increasing
        right_arm = y[i:hi + 1][::-1]               # increasing
        if left_arm[0] > half or right_arm[0] > half:
            continue
        jl = lo + int(np.searchsorted(left_arm, half)) - 1
        jr = hi - int(np.searchsorted(right_arm, half)) + 1
        if jl < lo or jr > hi or jl + 1 > i or jr - 1 < i:
            continue
        q_lo = np.interp(half, [y[jl], y[jl + 1]], [lq[jl], lq[jl + 1]])
        q_hi = np.interp(half, [y[jr], y[jr - 1]], [lq[jr], lq[jr - 1]])
        fwhm[r] = float(np.exp(q_hi) - np.exp(q_lo))

    return dict(q_peak=q_peak, fwhm=fwhm, height=height,
                height_above_base=height_above_base,
                prominence=prominence, has_peak=has_peak)


def estimate_window_noise(
    I: np.ndarray,
    q: np.ndarray,
    q_center: float,
    q_halfwidth: float,
    off_ring_quantile: float = 0.30,
) -> dict:
    """
    Robust noise of I(q) inside ``[q_center ± q_halfwidth]``.

    Each spectrum is residualised against a straight baseline fit in the
    window. Spectra whose tallest residual sits at or below
    ``off_ring_quantile`` of that height distribution are treated as
    off-ring, and the noise is 1.4826 times the MAD of their residuals.
    The split is fixed by the height distribution; it is not a
    certification outcome.
    """
    I2 = np.atleast_2d(np.asarray(I, float))
    qq_all = np.asarray(q, float)
    lo = float(q_center) - float(q_halfwidth)
    hi = float(q_center) + float(q_halfwidth)
    sl = (qq_all >= lo) & (qq_all <= hi)
    qq = qq_all[sl]
    block = I2[:, sl]
    heights = np.full(len(block), np.nan)
    if len(qq) < 3:
        return dict(sigma=np.nan, heights=heights, n_off_ring=0, cutoff=np.nan)
    for r in range(len(block)):
        y = block[r]
        if not np.isfinite(y).all():
            continue
        base = np.polyval(np.polyfit(qq, y, 1), qq)
        heights[r] = float(np.max(y - base))
    finite = heights[np.isfinite(heights)]
    if len(finite) == 0:
        return dict(sigma=np.nan, heights=heights, n_off_ring=0, cutoff=np.nan)
    cutoff = float(np.quantile(finite, off_ring_quantile))
    off = np.flatnonzero(np.isfinite(heights) & (heights <= cutoff))
    chunks = []
    for r in off:
        y = block[r]
        base = np.polyval(np.polyfit(qq, y, 1), qq)
        chunks.append(y - base)
    resid = np.concatenate(chunks) if chunks else np.zeros(1)
    med = float(np.median(resid))
    mad = float(np.median(np.abs(resid - med)))
    return dict(
        sigma=float(1.4826 * mad),
        heights=heights,
        n_off_ring=int(len(off)),
        cutoff=cutoff,
    )


def unresolved_width_count(fwhm: np.ndarray, q: np.ndarray, n_bins: float = 1.5) -> int:
    """How many finite widths are narrower than ``n_bins`` detector bins."""
    dq = float(np.median(np.diff(np.asarray(q, float))))
    w = np.asarray(fwhm, float)
    return int(np.sum(np.isfinite(w) & (w < n_bins * dq)))


def peak_violation_stats(
    I_true: np.ndarray,
    I_hat: np.ndarray,
    q: np.ndarray,
    peak_eps: float = 0.005,
    fwhm_eps: float = 0.001,
    min_prominence: float = 0.0,
    tol_mode: str = "absolute",
    include_width: bool = True,
    include_position: bool = True,
    q_center: float = None,
    q_halfwidth: float = None,
    desc_true: dict = None,
    desc_hat: dict = None,
):
    """
    Per-spectrum accounting against the peak-position / FWHM criterion.

    With ``tol_mode="absolute"`` the tolerances are in inverse angstroms:

        s_q    = |q̂_peak − q_peak| / peak_eps
        s_w    = |FŴHM   − FWHM|   / fwhm_eps
        s      = max(s_q, s_w)

    With ``tol_mode="relative"`` each denominator is scaled by the true value
    (``peak_eps · q_peak`` and ``fwhm_eps · FWHM``).

    Either way ``s ≤ 1`` means the interpolated spectrum reproduces the
    dominant peak position to within ``peak_eps`` and its width to within
    ``fwhm_eps`` — the same "accept iff s ≤ 1" convention the envelope
    criterion uses, so the conformal machinery downstream is unchanged.

    Peak presence is part of the test. If true and interpolated spectra agree
    that there is no peak (the Porod-dominated emulsion region), the site
    passes with s = 0. If they disagree, s = inf. A width test that is
    undefined for both (flanks never reach half maximum) is skipped rather
    than failed.
    """
    if tol_mode not in ("absolute", "relative"):
        raise ValueError(f"unknown tol_mode={tol_mode!r}")
    I_true = np.asarray(I_true, float)
    I_hat = np.asarray(I_hat, float)
    if desc_true is None:
        desc_true = peak_descriptors(
            I_true, q, min_prominence=min_prominence,
            q_center=q_center, q_halfwidth=q_halfwidth,
        )
    if desc_hat is None:
        desc_hat = peak_descriptors(
            I_hat, q, min_prominence=min_prominence,
            q_center=q_center, q_halfwidth=q_halfwidth,
        )

    hp_t, hp_h = desc_true["has_peak"], desc_hat["has_peak"]
    qt, qh = desc_true["q_peak"], desc_hat["q_peak"]
    wt, wh = desc_true["fwhm"], desc_hat["fwhm"]
    n = len(hp_t)
    relative = tol_mode == "relative"

    mismatch = hp_t != hp_h
    both = hp_t & hp_h

    s_q = np.zeros(n)
    den_q = peak_eps * np.abs(qt[both]) if relative else peak_eps
    s_q[both] = np.abs(qh[both] - qt[both]) / np.maximum(den_q, 1e-30)

    have_w = both & np.isfinite(wt) & np.isfinite(wh) if include_width else np.zeros(n, bool)
    only_one_w = (
        both & (np.isfinite(wt) != np.isfinite(wh)) if include_width else np.zeros(n, bool)
    )
    s_w = np.zeros(n)
    if include_width and np.any(have_w):
        den_w = fwhm_eps * np.abs(wt[have_w]) if relative else fwhm_eps
        s_w[have_w] = np.abs(wh[have_w] - wt[have_w]) / np.maximum(den_w, 1e-30)
        s_w[only_one_w] = np.inf

    score = s_w if not include_position else np.maximum(s_q, s_w)
    score[mismatch] = np.inf

    n_active = np.where(mismatch, 1, 1 + have_w.astype(int))
    n_fail = ((s_q > 1.0) & ~mismatch).astype(int) + (s_w > 1.0).astype(int)
    n_fail = np.where(mismatch, 1, n_fail)

    return dict(
        score=score,
        outside_mean=score > 1.0,
        outside_any=score > 1.0,
        frac_q_out=n_fail / np.maximum(n_active, 1),
        rho_max=score,
        s_q=s_q,
        s_fwhm=s_w,
        dq_rel=np.where(both, np.abs(qh - qt) / np.maximum(np.abs(qt), 1e-30),
                        np.nan),
        dfwhm_rel=np.where(have_w,
                           np.abs(wh - wt) / np.maximum(np.abs(wt), 1e-30),
                           np.nan),
        q_peak_true=qt, q_peak_hat=qh,
        fwhm_true=wt, fwhm_hat=wh,
        has_peak_true=hp_t, has_peak_hat=hp_h,
        peak_mismatch=mismatch,
    )


def integral_violation_stats(
    I_true: np.ndarray,
    I_hat: np.ndarray,
    q: np.ndarray,
    rtol: float = 0.01,
    atol: float = 0.01,
):
    """
    Per-spectrum score for the integrated intensity only.

    ``s = |T̂ − T| / (rtol |T| + atol)`` with ``T = ∫ I(q) dq``. Channel
    errors that cancel inside the integral do not count. ``s ≤ 1`` is the
    same accept convention as the full-curve envelope.
    """
    I_true = np.atleast_2d(np.asarray(I_true, float))
    I_hat = np.atleast_2d(np.asarray(I_hat, float))
    q = np.asarray(q, float)
    total = np.trapezoid(I_true, q, axis=-1)
    total_hat = np.trapezoid(I_hat, q, axis=-1)
    score = np.abs(total_hat - total) / np.maximum(rtol * np.abs(total) + atol, 1e-30)
    outside = score > 1.0
    return dict(
        score=score,
        outside_mean=outside,
        outside_any=outside,
        frac_q_out=outside.astype(float),
        rho_max=score,
        total=total,
        total_hat=total_hat,
    )


@dataclass
class AccuracyCriterion:
    """
    What counts as "good enough to interpolate", in one object.

    ``kind="envelope"`` is the full-profile rtol/atol test; ``kind="peak"``
    tests only the dominant peak's position and width; ``kind="integral"``
    tests only the integrated intensity. All three expose the same ``s ≤ 1``
    accept convention via :meth:`stats`, so the SSBC chain, the conformal
    thresholds and the plots do not care which one is in use.
    """
    kind: str = "envelope"
    rtol: float = 0.01
    atol: float = 0.01
    q: np.ndarray = None
    peak_eps: float = 0.005
    fwhm_eps: float = 0.001
    tol_mode: str = "absolute"
    min_prominence: float = 0.0
    signal_min: float = None
    include_width: bool = True
    include_position: bool = True
    q_center: float = None
    q_halfwidth: float = None
    # Absolute intensity noise in the analysis window, and the multiple of
    # that noise a peak must clear before it counts as present. None leaves
    # every local maximum marked present.
    presence_sigma: float = None
    presence_multiple: float = 5.0
    # Display unit for labels. Synthetic SAXS stays in Å⁻¹; ALS passes nm^-1.
    q_unit: str = "A^-1"

    def __post_init__(self):
        if self.kind not in ("envelope", "peak", "integral"):
            raise ValueError(f"unknown criterion kind={self.kind!r}")
        if self.tol_mode not in ("absolute", "relative"):
            raise ValueError(f"unknown tol_mode={self.tol_mode!r}")
        if self.kind in ("peak", "integral") and self.q is None:
            raise ValueError(f"criterion kind={self.kind!r} requires the q grid")

    @property
    def is_peak(self) -> bool:
        return self.kind == "peak"

    def _unit_tex(self) -> str:
        if str(self.q_unit).replace("⁻", "-") in ("nm^-1", "1/nm"):
            return r"\mathrm{nm^{-1}}"
        return r"\mathrm{\AA^{-1}}"

    def descriptors(self, I):
        """Peak descriptors for a spectrum block (peak criterion only)."""
        if not self.is_peak:
            return None
        d = peak_descriptors(
            I, self.q, min_prominence=self.min_prominence,
            q_center=self.q_center, q_halfwidth=self.q_halfwidth,
        )
        return self.apply_presence(d)

    def apply_presence(self, desc):
        """
        Drop a local maximum that does not clear ``presence_multiple`` times
        ``presence_sigma`` above its local baseline. Both the measured
        spectrum and a prediction pass through this, so a presence mismatch
        is a real disagreement about whether the line is there.
        """
        if desc is None or self.presence_sigma is None:
            return desc
        hab = np.asarray(desc["height_above_base"], float)
        present = (
            np.asarray(desc["has_peak"], bool)
            & np.isfinite(hab)
            & (hab > float(self.presence_multiple) * float(self.presence_sigma))
        )
        out = dict(desc)
        out["has_peak"] = present
        out["fwhm"] = np.where(present, desc["fwhm"], np.nan)
        out["q_peak"] = np.where(present, desc["q_peak"], np.nan)
        return out

    def stats(self, I_true, I_hat, desc_true=None, desc_hat=None):
        if self.is_peak:
            if desc_true is None:
                desc_true = self.descriptors(I_true)
            if desc_hat is None:
                desc_hat = self.descriptors(I_hat)
            return peak_violation_stats(
                I_true, I_hat, self.q,
                peak_eps=self.peak_eps, fwhm_eps=self.fwhm_eps,
                min_prominence=self.min_prominence, tol_mode=self.tol_mode,
                include_width=self.include_width,
                include_position=self.include_position,
                q_center=self.q_center, q_halfwidth=self.q_halfwidth,
                desc_true=desc_true, desc_hat=desc_hat,
            )
        if self.kind == "integral":
            return integral_violation_stats(
                I_true, I_hat, self.q, rtol=self.rtol, atol=self.atol,
            )
        return envelope_violation_stats(
            I_true, I_hat, rtol=self.rtol, atol=self.atol,
            signal_min=self.signal_min,
        )

    def denominators(self, q_true, fwhm_true):
        """Tolerance half-widths in q units, for plotting the accept band."""
        if self.tol_mode == "relative":
            return self.peak_eps * np.abs(q_true), self.fwhm_eps * np.abs(fwhm_true)
        return (np.full_like(np.asarray(q_true, float), self.peak_eps),
                np.full_like(np.asarray(fwhm_true, float), self.fwhm_eps))

    def label(self) -> str:
        """Short human-readable tag for figure titles."""
        unit_tex = self._unit_tex()
        if self.is_peak and self.q_center is not None and not self.include_position:
            return (
                rf"FWHM of the peak near ${self.q_center:.3f}\,{unit_tex}$: "
                rf"$|\Delta\mathrm{{FWHM}}|\leq{self.fwhm_eps:g}\,{unit_tex}$"
            )
        if self.is_peak and not self.include_width:
            unit = rf"\ {unit_tex}" if self.tol_mode == "absolute" else ""
            return rf"strongest-peak $q$: $|\Delta q|\leq{self.peak_eps:g}{unit}$"
        if self.is_peak:
            unit = rf"\ {unit_tex}" if self.tol_mode == "absolute" else ""
            tag = "abs" if self.tol_mode == "absolute" else "rel"
            return (rf"peak ({tag}): $\Delta q_{{\rm pk}}\leq{self.peak_eps:g}"
                    rf"{unit}$, $\Delta$FWHM$\leq{self.fwhm_eps:g}{unit}$")
        if self.kind == "integral":
            return rf"total intensity: rtol={self.rtol:g}, atol={self.atol:g}"
        return rf"envelope: rtol={self.rtol:g}, atol={self.atol:g}"


def as_criterion(criterion, rtol: float = 0.01, atol: float = 0.01):
    """Normalize a criterion argument, defaulting to the rtol/atol envelope."""
    if criterion is None:
        return AccuracyCriterion(kind="envelope", rtol=rtol, atol=atol)
    if isinstance(criterion, AccuracyCriterion):
        return criterion
    raise TypeError(f"criterion must be AccuracyCriterion or None, got {criterion!r}")




def slice_desc(desc, mask):
    """Row-subset a descriptor dict, or pass None through."""
    if desc is None:
        return None
    return {k: v[mask] for k, v in desc.items()}
