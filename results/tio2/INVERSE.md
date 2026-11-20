# Recovering the kinetic landscape from campaign data

Question: given only the patterns an accountable campaign measured (plus the nominal recipes), can the
kinetic and energy landscape of the forward model be estimated back, and how well?

Short answer: yes. From the 44–50 furnace runs a size-claim campaign measures, the four activation
energies come back within 4–8 % of the truth, with honest (cluster-robust) error bars, and the
temperature for half conversion within about 5 °C over 1–16 h. The campaign's measured subset
does as well as measuring all 64 runs. The seed levels alone (16 runs) give the same centres with
bands about 1.5–2× wider on contact growth and anatase coarsening.

Code: `experiments/tio2_calcination/inverse.py` (fit), `inverse_figure.py` (figure).
Numbers: `results/tio2/inverse/fits.json`. Figure: `results/tio2/inverse.png`.

## Pipeline (what an analyst would do)

1. **Phase fraction.** A two-phase pseudo-Voigt doublet fit (Cu Kα₁/Kα₂, quadratic background) of
   anatase (101) and rutile (110) over 23.5–29.5°. The integrated areas, with the per-mass intensity
   ratio, give the rutile mass fraction to ±0.003 (rms 0.003–0.007 over 512 crucibles).
2. **Anatase size.** Width of (101) through a Scherrer lookup calibrated on simulated strain-free
   single-phase patterns with the instrument function (the analogue of a LaB₆ standard). Used below
   70 nm only.
3. **Rutile size and strain.** Widths of (110) and (101) are forward-modelled from (size, microstrain)
   tables. Microstrain is one global fitted parameter, so this is a Williamson–Hall analysis carried
   out inside the fit.
4. **Kinetic model.** Forward model v2 integrated at the nominal recipe. The analyst does not see
   furnace offsets, the tray gradient, dosing errors or rate jitter. P25 blends are integrated as two
   powders.
5. **Fitted parameters (10).**
   - Surface nucleation: rate at 750 °C and E.
   - Contact growth: rate at 700 °C and E.
   - Alumina inhibition constant.
   - Anatase coarsening: rate at 690 °C and E.
   - Rutile coarsening: rate at 900 °C and E.
   - Rutile microstrain.

   Rates are parameterised at reference temperatures inside the data, which removes most of the
   rate–energy correlation.
6. **Held at literature values.** Interface nucleation, the size dependence β of the activation
   energy, the precursor size distribution and the P25 contact efficiency.
7. **Uncertainty.** Sandwich covariance clustered by furnace run, since the eight crucibles of a firing
   share its temperature offset. Naive per-crucible standard errors are too small by 1.0–1.9× for the
   transformation energies and 2.5–4.6× for rutile coarsening.

## Results (world A, truth seed 0; world B, truth seed 11)

Activation energies, kJ/mol (estimate ± cluster-robust s.e.):

| Data | Runs | E nucleation | E contact growth | E anatase coarsening | E rutile coarsening |
| --- | --- | --- | --- | --- | --- |
| truth | | 478 | 231 | 250 | 300 |
| A, full design | 64 | 468 ± 12 | 248 ± 10 | 234 ± 20 | 283 ± 8 |
| A, campaigns 0–4 | 44–50 | 457–469 (±12–13) | 238–254 (±10–14) | 219–239 (±20–25) | 277–283 (±7–8) |
| A, seed levels | 16 | 469 ± 14 | 256 ± 21 | 213 ± 23 | 279 ± 9 |
| B, full design | 64 | 490 ± 18 | 261 ± 11 | 289 ± 28 | 291 ± 9 |
| B, campaigns 0–1 | 47–48 | 495–498 (±21) | 259–260 (±13–14) | 300–301 (±30) | 295–296 (±9) |

Over 11 fits × 10 parameters, almost all estimates lie within 2.5 s.e. of the truth. Two exceptions
remain:
- The alumina inhibition constant is persistently high (z ≈ +2 to +4).
- One campaign gives the rutile coarsening energy at z = −3.4.

On the transformation map (native powder, 1–16 h), the half-conversion temperature is estimated about
5 °C high without alumina and about 3 °C high at 5 % alumina. The 90 % parameter band does not cover
the first. That is a systematic floor of about one furnace standard deviation.

Rate constants are pinned at 750–850 °C, where the transformation data are. Extrapolated to
500–600 °C they carry ±1 in ln k, or ±2 for anatase coarsening, whose low-temperature end is barely
observed.

## Four traps, each larger than the noise

Each was found by fitting idealised data (model-exact observables, no synthesis scatter, native-only
crucibles) and removing one cause at a time.

1. **Detection limit.** Rutile at 0.5–3 % reads as zero. Treating that as a measured zero delays the
   apparent onset and biases E nucleation by +70 kJ/mol. The fix is to treat fractions below 3 % as
   censored (a one-sided residual).
2. **Areas as height × width.** The Lorentzian-heavy small anatase and the Gaussian, instrument-limited
   large rutile differ in shape, so height × width biases the fraction by up to +0.07 at mid
   conversion. The fix is integrated areas from a profile fit.
3. **Strain read as size.** Rutile microstrain (5×10⁻⁴) makes one-reflection Scherrer sizes read
   3–16 % low above 70 nm. That flattens coarsening and biases E rutile coarsening by −50 kJ/mol. With
   one reflection the strain cannot be fitted (it goes to zero). With (110) and (101) it comes back at
   4.2 ± 0.5 against a true 5.
4. **Furnace-run clustering.** The eight crucibles share a furnace offset, so the effective sample
   size is the number of runs. Ignoring this gives bands that look precise and miss the truth by up to
   7.5 s.e.

The kinetic predictor itself is exact: model-generated observables return the truth to 0.0 s.e.

## What it means for the pilot

- The campaign's own measured runs are enough to map the energy landscape; no runs need to be added
  for kinetics. The runs the campaign skips are those its neighbours predict, and they add little:
  44–50 runs give the same bands as 64.
- The analysis plan should be fixed in advance:
  - profile-fit phase fractions;
  - two rutile reflections;
  - censoring at the detection limit;
  - errors clustered by furnace run.
- A thermocouple log per firing would remove the largest unmodelled term. Per-run offsets could then
  enter the fit as known values instead of a random effect.
- Interface nucleation and the size dependence β were held at literature values. A precursor-size
  axis in the design would be needed to identify β.

## Against uniform points (matched budgets)

Script: `experiments/tio2_calcination/inverse_uniform.py`. Numbers: `results/tio2/inverse/uniform.json`.
Arms:
- **campaign:** runs the size-claim campaign measured, 5 calibration seeds.
- **random-sub:** uniformly random subsets of the 64-run Sobol design (10 draws).
- **iid-uniform:** fresh designs of iid uniform (temperature, dwell) runs (6 designs). Each design has
  its own synthesis realisation, so its errors also carry world-to-world variation; compare the
  standard errors first.

Values are activation energies, kJ/mol, in the order nucleation / contact growth / anatase coarsening /
rutile coarsening. T50 is the error in the temperature for 50 % rutile over 1–4 h dwell, native powder.

| Arm | Runs | Median s.e. | Spread across replicates (s.d.) | RMSE vs truth | T50 error, median / max (°C) |
| --- | --- | --- | --- | --- | --- |
| full design (Sobol) | 64 | 12 / 10 / 20 / 8 | – | 10 / 17 / 16 / 17 | 6.6 |
| campaign | 44–50 | 12 / 11 / 22 / 8 | 5 / 5 / 7 / 2 | 15 / 16 / 24 / 19 | 6.7 / 7.2 |
| random subset of Sobol | 47 | 14 / 11 / 20 / 9 | 6 / 8 / 17 / 3 | 10 / 18 / 26 / 17 | 7.1 / 8.9 |
| iid uniform | 47 | 17 / 10 / 28 / 7 | 18 / 14 / 24 / 7 | 19 / 29 / 31 / 16 | 5.3 / 9.3 |
| seed levels (Sobol) | 16 | 14 / 21 / 23 / 9 | – | 10 / 24 / 37 / 21 | 7.0 |
| random subset of Sobol | 16 | 25 / 19 / 42 / 14 | 22 / 22 / 51 / 17 | 22 / 34 / 55 / 23 | 3.9 / 11.7 |
| iid uniform | 16 | 32 / 14 / 48 / 12 | 36 / 19 / 33 / 10 | 37 / 25 / 40 / 19 | 8.5 / 9.9 |

Reading:
- **At about 47 runs, run selection barely matters among Sobol-based arms.** The campaign, a random 47
  of the Sobol runs and the full design give the same standard errors. The spread across campaign seeds
  is smaller, but campaigns share most of their runs.
- **iid uniform runs cost precision.** Nucleation and anatase-coarsening energies are about 30–40 %
  less precise, with 2–3× the spread across designs. Clumps and holes in an iid design leave parts of
  the transformation front unsampled.
- **At 16 runs, the design is what matters.** The Sobol seed levels give standard errors of
  14 / 21 / 23 / 9. A random 16 of the same runs, or 16 iid uniform runs, roughly double the errors on
  nucleation and anatase coarsening, and individual draws miss the anatase-coarsening energy by up to
  100 kJ/mol.
- **T50 sits on the systematic floor (5–9 °C) in every arm.** Precision gains in the energies do not
  move it, because the floor comes from the observation model and synthesis scatter.
- **Bands are least honest for iid uniform designs at 47 runs:** 20 % of parameter estimates lie beyond
  2.5 s.e., against 10–16 % in the Sobol arms.
