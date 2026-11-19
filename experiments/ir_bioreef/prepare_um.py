"""
Prepare the IR map for the record: per-pixel Mie correction and a design in micrometres.

    python -m experiments.ir_bioreef.prepare_um

Writes <data root>/IR_data/interest_gate_um/prepared.npz.

Correction. Stage-1 resonant Mie EMSC (scattering-only van de Hulst basis, 7 signed principal
components, flat-slope and level windows, chord lower envelope, 0 <= background <= A, b >= 0.05),
self-consistent per pixel: every pixel starts from its own apparent absorbance and its reference
is replaced by its own corrected spectrum at each of 6 iterations. No information passes between
pixels, so the correction is a fixed per-spectrum transformation. Corrected spectrum = apparent
absorbance minus the fitted background, clipped at 0; the scale b is not divided out. Float64.

Design. Hierarchical Poisson-disk design drawn on the physical rectangle, pixel centres at 1 um
(x 0-41 um, y 0-28 um), radii 6.8 um down to 0.85 um by 1/sqrt(2) (seven levels), seed 42, the
four corners forced. Sites are snapped to the nearest pixel; on a collision the coarsest level is
kept. Points are stored in micrometres and, for the interpolators, divided by 41 um (an isotropic
rescaling, so distances keep their physical proportions).
"""
from __future__ import annotations

import numpy as np

from .._paths import data_root

PITCH_UM = 1.0
SCALE_UM = 41.0
R_MAX_UM, N_LEVELS, SEED = 6.8, 7, 42
CHECK = (1500.0, 1850.0)
DISPLAY = (900.0, 1850.0)


def load_map(path):
    z = np.load(path)
    cube = np.asarray(z["data_cube"], np.float64)          # (n_chan, ny, nx), apparent absorbance
    wn = np.asarray(z["wavenumbers"], np.float64)
    n_chan, ny, nx = cube.shape
    return np.moveaxis(cube, 0, -1).reshape(-1, n_chan), wn, ny, nx


def correct(spectra, wn, n_iter=6):
    import torch

    from .mie_correction_torch import me_emsc_batch
    own = np.clip(spectra, 0.0, None)                       # each pixel seeds itself
    fit = me_emsc_batch(spectra, wn, own, n_iter=n_iter, device="cpu", dtype=torch.float64)
    return np.clip(spectra - fit["background"], 0.0, None), fit


def design(ny, nx):
    from hiposa import PoissonDiskSamplerWithExisting
    rng = np.random.default_rng(SEED)
    np.random.seed(int(rng.integers(0, 2 ** 31 - 1)))
    W, H = (nx - 1) * PITCH_UM, (ny - 1) * PITCH_UM
    radii = R_MAX_UM / np.sqrt(2.0) ** np.arange(N_LEVELS)
    points = np.array([[0.0, 0.0], [W, 0.0], [0.0, H], [W, H]])
    labels = np.zeros(4, np.int32)
    for lev, r in enumerate(radii):
        s = PoissonDiskSamplerWithExisting(domain=[(0.0, W), (0.0, H)], r=float(r), existing_points=points,
                                           existing_labels=labels, symmetry_operators=None, wrap=False)
        new, lab = s.sample(new_label=int(lev), return_new_only=True)
        if len(new):
            points = np.vstack([points, new])
            labels = np.concatenate([labels, lab])
    col = np.clip(np.rint(points[:, 0] / PITCH_UM).astype(int), 0, nx - 1)
    row = np.clip(np.rint(points[:, 1] / PITCH_UM).astype(int), 0, ny - 1)
    pix = row * nx + col
    order = np.lexsort((np.arange(len(pix)), labels))
    _, first = np.unique(pix[order], return_index=True)
    keep = np.sort(order[first])
    return pix[keep], labels[keep], radii, len(points)


def main():
    root = data_root()
    spectra, wn, ny, nx = load_map(root / "IR_data" / "BP-area.npz")
    corr, fit = correct(spectra, wn)
    pix, levels, radii, n_raw = design(ny, nx)
    rows, cols = np.divmod(np.arange(ny * nx), nx)
    points_um = np.column_stack([cols * PITCH_UM, rows * PITCH_UM]).astype(float)
    check = (wn >= CHECK[0]) & (wn <= CHECK[1])
    display = (wn >= DISPLAY[0]) & (wn <= DISPLAY[1])
    out = root / "IR_data" / "interest_gate_um"
    out.mkdir(parents=True, exist_ok=True)
    np.savez(out / "prepared.npz", points_um=points_um, points=points_um / SCALE_UM, scale_um=SCALE_UM,
             rows=rows, cols=cols, ny=ny, nx=nx, wavenumbers=wn, pix=pix, levels=levels,
             spectra=corr[:, check][pix], wn_check=wn[check], corr_display=corr[:, display],
             raw_display=spectra[:, display], wn_display=wn[display], emsc_b=fit["b"],
             radii_um=radii, n_raw=n_raw, n_dropped=n_raw - len(pix))
    lv, cnt = np.unique(levels, return_counts=True)
    print(f"{len(pix)} unique sites of {n_raw}; levels {dict(zip(lv.tolist(), cnt.tolist()))}")
    win = corr[:, check]
    print(f"interest share (any channel >= 0.1): {np.mean(win.max(1) >= 0.1):.3f}")


if __name__ == "__main__":
    main()
