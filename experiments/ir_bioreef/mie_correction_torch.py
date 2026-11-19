"""
mie_correction_torch.py — GPU-batched stage-1 resonant Mie EMSC
================================================================

PyTorch port of the stage-1 correction engine of `mie_correction.py`,
processing ALL pixels of a map as one batch per outer iteration. Same model,
same constraint set, same defaults; numerically FP32-safe by construction
(batched QR least squares via torch.linalg.lstsq; PCA via 90x90 Gram
eigendecomposition — identical span to the SVD of the reference code).

Targets: CUDA (incl. aarch64 / DGX Spark GB10), MPS, or CPU. FP64 is
available via dtype=torch.float64 but is not required and is slow on
consumer/Blackwell-class FP64 units.

Differences from the numpy engine (all verified small, see equivalence test):
  * fixed n_iter outer iterations for the whole batch (no per-pixel early
    exit) — deterministic batching;
  * Savitzky-Golay smoothing uses replicate padding at the array edges
    (scipy uses polynomial edge interpolation; affects only the 10 edge
    channels of the k-shape, which are tapered anyway);
  * hinge and b>=b_min handling are algebraically identical (weighted-row
    block; exact two-branch active set for the single bound).

Stage 2 (population fit) remains in `mie_correction.py` (scipy NNLS; it is
not the bottleneck).

Usage:
    from mie_correction_torch import me_emsc_batch, correct_map_torch
    out = correct_map_torch('in.h5', 'out.h5', device='cuda')
"""
import numpy as np
import torch
from scipy.signal import savgol_coeffs

# ----------------------------------------------------------------------
# defaults — mirror mie_correction.py
# ----------------------------------------------------------------------
B_MIN = 0.05
LAM_HINGE = 30.0
LAM_FLAT = 1e4
MU_LEVEL = 0.3
FLAT_WINDOWS = ((2100, 2300), (2390, 2800), (3850, 4000))
LEVEL_WINDOWS = ((2390, 2800), (3850, 4000))
CHORD_WINDOW = (2800, 3850)
CHORD_ANCHORS = ((2390, 2800), (3850, 4000))
K_CUTOFF, K_TAPER = 2300.0, 40.0
A_UM = (2.0, 8.0, 6)
N0_GRID = (1.1, 1.5, 5)
KMAX = (0.02, 0.12, 3)
N_COMP = 7


def _hilbert_imag(x, pad=512):
    """Imag part of the analytic signal, batched over leading dims."""
    xe = torch.cat([x[..., :1].expand(*x.shape[:-1], pad), x,
                    x[..., -1:].expand(*x.shape[:-1], pad)], dim=-1)
    n = xe.shape[-1]
    X = torch.fft.fft(xe, dim=-1)
    h = torch.zeros(n, dtype=X.dtype, device=x.device)
    if n % 2 == 0:
        h[0] = 1; h[n // 2] = 1; h[1:n // 2] = 2
    else:
        h[0] = 1; h[1:(n + 1) // 2] = 2
    a = torch.fft.ifft(X * h, dim=-1)
    return a.imag[..., pad:-pad]


def kk_dn(k, pad=512):
    """dn = -Im[hilbert(k)], batched. Sign per Lorentz-oscillator test."""
    return -_hilbert_imag(k, pad)


def _sg_filter(x, window=21, order=3):
    """Savitzky-Golay smoothing via conv1d, replicate edge padding."""
    c = torch.as_tensor(savgol_coeffs(window, order)[::-1].copy(),
                        dtype=x.dtype, device=x.device)
    B = x.shape[:-1]
    xf = x.reshape(-1, 1, x.shape[-1])
    xf = torch.nn.functional.pad(xf, (window // 2, window // 2),
                                 mode='replicate')
    y = torch.nn.functional.conv1d(xf, c.view(1, 1, -1))
    return y.reshape(*B, -1)


def _windows_mask(wn, windows):
    m = torch.zeros_like(wn, dtype=torch.bool)
    for lo, hi in windows:
        m |= (wn > lo) & (wn < hi)
    return m


def mie_basis_batch(wn, est, n_comp=N_COMP, a_um=A_UM, n0_grid=N0_GRID,
                    kmax=KMAX, k_cutoff=K_CUTOFF, k_taper=K_TAPER):
    """(B, n_comp, W) orthonormal scattering-only basis per pixel.

    PCA via Gram eigendecomposition of the mean-centred 90-curve family —
    identical span to the reference SVD.
    """
    Bn, W = est.shape
    r = torch.clamp(est, min=0.0)
    if k_cutoff is not None:
        r = r / (1.0 + torch.exp((wn - k_cutoff) / k_taper))
    s = r / wn
    s = torch.clamp(_sg_filter(s), min=0.0)
    s = s / torch.clamp(s.amax(dim=-1, keepdim=True), min=1e-12)

    Qs = []
    for km in np.linspace(*kmax):
        dn = kk_dn(km * s)                                # (B, W)
        for a in np.linspace(a_um[0], a_um[1], a_um[2]) * 1e-4:
            for n0 in np.linspace(n0_grid[0], n0_grid[1], n0_grid[2]):
                nm1 = torch.clamp(n0 - 1.0 + dn, min=1e-6)
                rho = torch.clamp(4 * np.pi * a * wn * nm1, min=1e-8)
                Qs.append(2 - (4 / rho) * torch.sin(rho)
                            + (4 / rho ** 2) * (1 - torch.cos(rho)))
    Q = torch.stack(Qs, dim=1)                            # (B, 90, W)
    Qc = Q - Q.mean(dim=1, keepdim=True)
    # Gram eigendecomposition SQUARES the family's conditioning; with
    # singular values spanning ~1e3 the 7th eigenvalue sits at ~1e-6 of
    # the top — below fp32 resolution, which destabilises the basis and
    # the self-consistent loop amplifies it. The 90x90 eigh is tiny, so
    # do the Gram + eigh in fp64 unconditionally and cast back.
    Qc64 = Qc.double()
    G = Qc64 @ Qc64.transpose(1, 2)                       # (B, 90, 90)
    evals, evecs = torch.linalg.eigh(G)                   # ascending
    top = evecs[..., -n_comp:]                            # (B, 90, n_comp)
    P = (top.transpose(1, 2) @ Qc64)
    P = P / torch.clamp(P.norm(dim=-1, keepdim=True), min=1e-12)
    return P.to(Qc.dtype)


def _lstsq64(M, y):
    """Least squares via fp64 normal equations with column equilibration.

    The design has column norms spanning ~40x and cond ~7e3; in fp32,
    eps*cond ~ 8e-4 makes the solve marginal, and the self-consistent
    loop amplifies the error into batch-dependent divergence. The normal
    matrix is only 11x11 per pixel, so forming and Cholesky-solving it in
    fp64 costs nothing next to the O(W) design assembly, and restores
    exact agreement with the scipy engine while the heavy work
    (basis, hinges, all O(W) tensors) stays in the working dtype.
    """
    M64 = M.double()
    y64 = y.double()
    scale = torch.clamp(M64.pow(2).sum(dim=1).sqrt(), min=1e-30)   # (B, C)
    Ms = M64 / scale.unsqueeze(1)
    G = Ms.transpose(1, 2) @ Ms
    rhs = Ms.transpose(1, 2) @ y64.unsqueeze(-1)
    ridge = 1e-12 * torch.eye(G.shape[-1], dtype=G.dtype,
                              device=G.device).expand_as(G)
    xs = torch.linalg.solve(G + ridge, rhs).squeeze(-1)
    return (xs / scale)


def _solve_bounded(M, y, ref_col_idx, b_min=B_MIN):
    """Batched least squares with the single bound x[ref_col] >= 0
    (b = b_min + x[ref_col]): exact two-branch active set."""
    x = _lstsq64(M, y)
    bad = x[:, ref_col_idx] < 0.0
    if bad.any():
        cols = [c for c in range(M.shape[-1]) if c != ref_col_idx]
        xr = _lstsq64(M[bad][..., cols], y[bad])
        xfix = torch.zeros_like(x[bad])
        xfix[:, cols] = xr
        x[bad] = xfix
    return x.to(M.dtype)


def emsc_fit_batch(A, wn, est, P, chord, flat_idx, level_idx,
                   lam_flat=LAM_FLAT, mu_level=MU_LEVEL,
                   lam_hinge=LAM_HINGE, b_min=B_MIN, n_pass=4):
    """One batched EMSC solve with all constraints. Shapes: A,est (B,W);
    P (B,7,W); chord (B,W) floor (zeros outside chord window)."""
    Bn, W = A.shape
    dt, dev = A.dtype, A.device
    u = (wn - wn.mean()) / (wn.max() - wn.min())
    ones = torch.ones(Bn, W, dtype=dt, device=dev)
    D = torch.cat([ones.unsqueeze(-1), (u * ones).unsqueeze(-1),
                   (u * u * ones).unsqueeze(-1), P.transpose(1, 2),
                   est.unsqueeze(-1)], dim=-1)            # (B, W, 11)
    ncol = D.shape[-1]
    # substitution b = b_min + beta: subtract b_min * est from the target
    y = A - b_min * est

    # fixed penalty blocks (b column zeroed)
    blocks_M = [D]
    blocks_y = [y]
    if len(flat_idx):
        i0 = flat_idx
        F = np.sqrt(lam_flat) * (D[:, i0 + 1, :] - D[:, i0, :])
        F = F.clone(); F[..., -1] = 0.0
        blocks_M.append(F)
        blocks_y.append(np.sqrt(lam_flat) * (A[:, i0 + 1] - A[:, i0]))
    if len(level_idx):
        L = np.sqrt(mu_level) * D[:, level_idx, :]
        L = L.clone(); L[..., -1] = 0.0
        blocks_M.append(L)
        blocks_y.append(np.sqrt(mu_level) * A[:, level_idx])
    # hinge block: full-width, weight set per pass (b column zeroed)
    Hrow = D.clone(); Hrow[..., -1] = 0.0

    wgt = torch.zeros(Bn, W, dtype=dt, device=dev)
    tgt = torch.zeros(Bn, W, dtype=dt, device=dev)
    # PER-PIXEL FREEZING. The scipy engine exits its hinge loop per
    # spectrum as soon as that spectrum satisfies the constraints; a
    # batch-wide loop would keep re-solving already-feasible pixels,
    # and further passes can walk them off their solution (observed:
    # a pixel driven onto the b lower bound purely by batch company).
    # Freeze each pixel's coefficients at its first feasible pass.
    x = None
    x_out = None
    frozen = torch.zeros(Bn, dtype=torch.bool, device=dev)
    for p in range(n_pass + 1):
        M = torch.cat(blocks_M + [Hrow * wgt.unsqueeze(-1)], dim=1)
        yy = torch.cat(blocks_y + [tgt * wgt], dim=1)
        x = _solve_bounded(M, yy, ref_col_idx=ncol - 1, b_min=b_min)
        if x_out is None:
            x_out = x.clone()
        else:
            x_out = torch.where(frozen.unsqueeze(-1), x_out, x)
        bg = torch.einsum('bwc,bc->bw', D[..., :-1], x_out[..., :-1])
        hi = bg > A
        lo = bg < chord
        feasible = ~(hi.any(dim=-1) | lo.any(dim=-1))
        frozen = frozen | feasible
        if bool(frozen.all()) or p == n_pass:
            break
        wgt = (hi | lo).to(dt) * np.sqrt(lam_hinge)
        tgt = torch.where(hi, A, chord)
        wgt = torch.where(frozen.unsqueeze(-1),
                          torch.zeros_like(wgt), wgt)
    x = x_out
    bg = torch.einsum('bwc,bc->bw', D[..., :-1], x[..., :-1])
    b = b_min + x[..., -1]
    pure = torch.clamp((A - bg) / b.unsqueeze(-1), min=0.0)
    return pure, bg, b


def me_emsc_batch(A_np, wn_np, ref0_np, n_iter=6, device=None,
                  dtype=torch.float32, chunk=None,
                  flat_windows=FLAT_WINDOWS, lam_flat=LAM_FLAT,
                  level_windows=LEVEL_WINDOWS, mu_level=MU_LEVEL,
                  chord_window=CHORD_WINDOW, chord_anchors=CHORD_ANCHORS,
                  verbose=False):
    """Batched stage-1 correction for a whole map.

    A_np (N, W) apparent absorbance, wn_np (W,), ref0_np (W,).
    Returns dict of numpy arrays: pure, background, b.
    """
    device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
    wn = torch.as_tensor(wn_np, dtype=dtype, device=device)
    N = len(A_np)
    chunk = chunk or N
    out_p = np.zeros_like(A_np, dtype=np.float32)
    out_g = np.zeros_like(A_np, dtype=np.float32)
    out_b = np.zeros(N, dtype=np.float32)

    fm = _windows_mask(wn, flat_windows)
    flat_idx = torch.where(fm[:-1] & fm[1:])[0]
    level_idx = torch.where(_windows_mask(wn, level_windows))[0]

    for s0 in range(0, N, chunk):
        sl = slice(s0, min(s0 + chunk, N))
        A = torch.as_tensor(A_np[sl], dtype=dtype, device=device)
        Bn = A.shape[0]
        # per-pixel chord floor from anchor means of A
        (a1l, a1h), (a2l, a2h) = chord_anchors
        m1 = (wn > a1l) & (wn < a1h)
        m2 = (wn > a2l) & (wn < a2h)
        x1, x2 = wn[m1].mean(), wn[m2].mean()
        y1, y2 = A[:, m1].mean(1), A[:, m2].mean(1)
        line = y1[:, None] + (y2 - y1)[:, None] * (wn - x1) / (x2 - x1)
        chord = torch.zeros_like(A)
        cw = (wn > chord_window[0]) & (wn < chord_window[1])
        chord[:, cw] = line[:, cw]

        est = torch.as_tensor(ref0_np, dtype=dtype,
                              device=device).expand(Bn, -1).contiguous()
        est = torch.clamp(est, min=0)
        est = est - est.amin(dim=-1, keepdim=True)
        for it in range(n_iter):
            P = mie_basis_batch(wn, est)
            pure, bg, b = emsc_fit_batch(A, wn, est, P, chord,
                                         flat_idx, level_idx,
                                         lam_flat=lam_flat,
                                         mu_level=mu_level)
            est = pure - pure.amin(dim=-1, keepdim=True)
            if verbose:
                print(f"  chunk {s0}: iter {it+1}/{n_iter}", flush=True)
        out_p[sl] = pure.float().cpu().numpy()
        out_g[sl] = bg.float().cpu().numpy()
        out_b[sl] = b.float().cpu().numpy()
    return dict(pure=out_p, background=out_g, b=out_b)


def correct_map_torch(in_h5, out_h5, device=None, dtype=torch.float32,
                      chunk=None, n0_assumed=1.3, verbose=True):
    """Full map driver: torch stage 1 + scipy stage 2 + h5 output
    (same schema as mie_correction.correct_map)."""
    import h5py, time
    import mie_correction as mc
    with h5py.File(in_h5, 'r') as f:
        grp = list(f.keys())[0]
        g = f[grp]
        wn = g['data/wavenumbers'][:].astype(float)
        S = g['data/spectra'][:].astype(float)
        mask = g['data/image/image_mask'][:]
        ind = g['data/image/ind_rc_map'][:]
        grid_param = g['data/image/image_grid_param'][:]
        xy = g['data/xy'][:]
    A = -np.log10(np.clip(S, 0.1, None) / 100.0)
    ref0 = mc.build_initial_reference(A, wn)
    t0 = time.time()
    r = me_emsc_batch(A, wn, ref0, device=device, dtype=dtype, chunk=chunk,
                      verbose=verbose)
    if verbose:
        print(f"stage 1 (torch, {device or 'auto'}): {time.time()-t0:.0f}s")
    pure, bg, b = r['pure'], r['background'], r['b']
    N = len(A)
    Wmat = None
    stats = np.zeros((N, 4))
    wig = np.zeros(N)
    for i in range(N):                       # stage 2 stays on CPU (scipy)
        p = mc.population_fit(bg[i].astype(float), wn,
                              np.clip(pure[i].astype(float), 0, None))
        if Wmat is None:
            Wmat = np.zeros((N, len(p['w'])), np.float32)
            par = p['par']
        Wmat[i] = p['w']
        stats[i] = [p['coverage'], p['alpha0_mean'],
                    p['gamma_mean'], p['alpha0_sd']]
        wig[i] = mc.lf_wiggle(pure[i].astype(float), wn)
    if verbose:
        print(f"stage 2 (scipy): {time.time()-t0:.0f}s total")
    ok = b > 0.2
    H, Wd = mask.shape
    cube_pure = np.full((H, Wd, len(wn)), np.nan, np.float32)
    cube_bg = np.full((H, Wd, len(wn)), np.nan, np.float32)
    cube_pure[ind[:, 1], ind[:, 2]] = pure
    cube_bg[ind[:, 1], ind[:, 2]] = bg
    import h5py
    with h5py.File(out_h5, 'w') as f:
        g = f.create_group(grp)
        d = g.create_group('data')
        d.create_dataset('wavenumbers', data=wn.astype(np.float32))
        d.create_dataset('xy', data=xy)
        d.create_dataset('spectra_pure', data=pure, compression='gzip')
        d.create_dataset('spectra_background', data=bg, compression='gzip')
        d.create_dataset('emsc_b', data=b)
        d.create_dataset('quality_ok', data=ok)
        d.create_dataset('audit_lf_wiggle', data=wig.astype(np.float32))
        im = d.create_group('image')
        im.create_dataset('image_cube_pure', data=cube_pure,
                          compression='gzip')
        im.create_dataset('image_cube_background', data=cube_bg,
                          compression='gzip')
        im.create_dataset('image_mask', data=mask)
        im.create_dataset('ind_rc_map', data=ind)
        im.create_dataset('image_grid_param', data=grid_param)
        p = g.create_group('population_model')
        p.create_dataset('weights', data=Wmat, compression='gzip')
        p.create_dataset('atoms_alpha0_gamma', data=par.astype(np.float32))
        p.create_dataset('coverage', data=stats[:, 0].astype(np.float32))
        p.create_dataset('alpha0_wmean', data=stats[:, 1].astype(np.float32))
        p.create_dataset('gamma_wmean', data=stats[:, 2].astype(np.float32))
        p.create_dataset('alpha0_wsd', data=stats[:, 3].astype(np.float32))
        p.create_dataset('a_eff_um', data=mc.a_eff_um(
            stats[:, 1], n0_assumed).astype(np.float32))
        g.attrs['correction'] = ('torch-batched signed-PC resonant EMSC '
                                 '(stage 1) + post-hoc population fit '
                                 '(stage 2); see mie_correction_methods.md')
    return dict(pure=pure, bg=bg, b=b, stats=stats)


# ======================================================================
# VERIFICATION
# ======================================================================

def verify(A_np, wn_np, ref0_np, n_px=30, device='cpu',
           dtype=torch.float32, seed=0, verbose=True):
    """Equivalence test against the scipy engine, plus batch invariance.

    Checks (thresholds calibrated on the development map):
      * max|dpure| vs mie_correction.me_emsc: median < 0.01, max < 0.05
        for pixels with b > 0.3 (low-b pixels sit near the b bound where
        the hinge path is genuinely ill-conditioned and both engines are
        equally arbitrary -- these are flagged by quality_ok anyway);
      * batch invariance: a pixel's result must not depend on which other
        pixels share its batch.
    """
    import mie_correction as mc
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(A_np), n_px, replace=False)
    rt = me_emsc_batch(A_np[idx], wn_np, ref0_np, device=device, dtype=dtype)
    d, db, bs = [], [], []
    for k, i in enumerate(idx):
        rn = mc.me_emsc(A_np[i], wn_np, ref0_np, n_iter=6, tol=0)
        d.append(np.max(np.abs(np.clip(rn['pure'], 0, None) - rt['pure'][k])))
        db.append(abs(rn['b'] - rt['b'][k]))
        bs.append(rn['b'])
    d, db, bs = np.array(d), np.array(db), np.array(bs)
    keep = bs > 0.3
    solo = me_emsc_batch(A_np[idx[:1]], wn_np, ref0_np, device=device,
                         dtype=dtype)
    inv = np.max(np.abs(solo['pure'][0] - rt['pure'][0]))
    out = dict(dpure_median=float(np.median(d)),
               dpure_max_goodb=float(d[keep].max() if keep.any() else 0.0),
               db_max_goodb=float(db[keep].max() if keep.any() else 0.0),
               batch_invariance=float(inv))
    if verbose:
        print(f"verify[{device}/{dtype}]: |dpure| median {out['dpure_median']:.4f}"
              f" max(b>0.3) {out['dpure_max_goodb']:.4f} | |db| max "
              f"{out['db_max_goodb']:.4f} | batch-invariance {inv:.2e}")
    assert out['dpure_median'] < 0.01, "torch engine diverges from reference"
    assert out['batch_invariance'] < 1e-4, "result depends on batch company"
    return out


if __name__ == '__main__':
    import sys
    import h5py
    import mie_correction as mc
    if len(sys.argv) >= 3:
        dev = sys.argv[3] if len(sys.argv) > 3 else None
        correct_map_torch(sys.argv[1], sys.argv[2], device=dev)
    else:
        print("usage: python mie_correction_torch.py in.h5 out.h5 [device]")
