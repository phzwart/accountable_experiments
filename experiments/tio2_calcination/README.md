# Dry-run: 4-D calcination campaign on doped TiO₂ (simulated)

A pilot for an autonomous solid-state synthesis platform (A-Lab type: powder dosing, box furnaces, powder XRD). The simulator stands in for the robot so that the accountable workflow can be dry-run with known truth before any furnace time is spent.

## Recipe space (unit 4-cube)

| Axis | Range | Mapping |
| --- | --- | --- |
| u0 calcination temperature | 500–1000 °C | linear |
| u1 dwell time | 1–16 h | log₂ |
| u2 inhibiting dopant (cation fraction) | 0–0.10 | linear |
| u3 rutile seed in the precursor (mass fraction) | 0–0.05 | linear |

## Design

Scrambled Sobol sequence (scipy, seed 42), 1024 recipes, cut into consecutive power-of-two blocks used as levels: 16, 16, 32, 64, 128, 256, 512. Each block starting at a multiple of its length is a (t, m, s)-net, so every level is balanced on its own. Levels 0–2 (64 recipes) are the seed.

## Forward model (`forward.py`)

- Anatase → rutile: Avrami kinetics, n = 1.5, Arrhenius rate with 165.6 kJ/mol (Zhang & Banfield, Am. Mineral. 84, 528, 1999), calibrated to half conversion after 4 h at 750 °C for undoped, unseeded nanocrystalline anatase.
- Inhibiting dopant: activation energy raised by 30 c/(c + 0.03) kJ/mol (saturating), following the inhibitor/promoter picture of Hanaor & Sorrell (J. Mater. Sci. 46, 855, 2011). At 10 % dopant the transition moves to about 900 °C.
- Rutile seeds bypass nucleation: a growth term proportional to s^(2/3), 120 kJ/mol, half conversion after 4 h at 680 °C for 5 % seed.
- Crystallite growth D³ − D₀³ = K t exp(−Q/RT): anatase 12 → 40 nm after 4 h at 750 °C (dopant slows growth); rutile 30 → 80 nm after 4 h at 800 °C.
- Pattern: Cu Kα₁, 2θ 20–60° in 0.02° steps. Reflections and intensities per unit mass from anatase (I4₁/amd) and rutile (P4₂/mnm) structures with pymatgen (`reflections.json`; the ratio of strongest reflections per unit mass is 1.375, cf. the Spurr–Myers factor 1.265). Pseudo-Voigt peaks broadened by Scherrer size, microstrain (annealing out with temperature) and a 0.05° instrumental width; smooth background; Poisson counts.
- Synthesis scatter: lognormal jitter (s.d. 0.15) on each rate constant per recipe and a furnace temperature offset (s.d. 4 °C). With `furnace="split"`, recipes whose temperature (25 °C steps) and dwell (powers of two) round to the same setting share one furnace run and its offset.

The truth of a dry-run is one realisation per recipe (seed 0), fixed before any campaign.

## Claims

- Interest: mixed phase, rutile mass fraction estimated from the pattern between 0.10 and 0.90 (anatase (101) and rutile (110) areas above 5σ, σ the counting noise in the reflection-free window 30–34°). About 35 % of recipes.
- Interpolation, `size`: the anatase (101) width within 0.08° 2θ, after Savitzky–Golay smoothing (11 bins), with agreement on the presence of the line. The noise floor of the width is about 0.03° (90th percentile).
- Interpolation, `pattern`: the whole pattern within 10 % + 2σ, averaged over channels with predicted counts above 600.

Tolerances are set so that about 20 % of last-level recipes fail prediction from the coarser levels under either claim (matched difficulty).

## Protocols

- Delaunay: barycentric weights on the 4-D Delaunay triangulation of the measured recipes (piecewise-linear interpolation of whole patterns), logistic score on neighbour disagreement and position.
- GP: isotropic squared-exponential kernel on the unit cube, length scale from the design spacing, posterior standard deviation as score.
- Random: independent uniform scores for both certificates.

Guarantee: R_E ≤ 0.20 at confidence 0.80 per level, quantile path, 40 calibration recipes per level.

## Commands

    python -m experiments.tio2_calcination.dryrun run --rows size_delaunay,pattern_delaunay --seeds 0-99
    python -m experiments.tio2_calcination.dryrun report
    python -m experiments.tio2_calcination.placement
