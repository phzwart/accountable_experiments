# Dry-run: 4-D calcination campaign on doped TiO₂ (simulated)

Simulator, design and claims: `experiments/tio2_calcination/README.md`. 1024 recipes in a scrambled Sobol design over temperature, dwell, dopant and rutile seed; levels are power-of-two blocks (16, 16, 32, 64, 128, 256, 512), levels 0–2 the seed. Guarantee R_E ≤ 0.20 at confidence 0.80 per level, quantile path, 40 calibration recipes per level, 100 campaigns per row (calibration seeds 0–99) on one fixed truth realisation.

## Results

| Row | Measured of 1024 (mean ± s.d.) | Of which for want of a claim | Exceedances / allowed (400 level checks) | P(≥ observed) | Wrong skips | Mixed-phase recipes lost |
| --- | --- | --- | --- | --- | --- | --- |
| Size claim, Delaunay | 321 ± 41 | 97 | 39 / 52.8 | 0.99 | 117 | 19 % |
| Pattern claim, Delaunay | 397 ± 35 | 173 | 51 / 52.8 | 0.63 | 123 | 27 % |
| Size claim, random scores | 684 ± 74 | 460 | 48 / 52.8 | 0.78 | 116 | 22 % |
| Pattern claim, random scores | 659 ± 85 | 435 | 63 / 52.8 | 0.08 | 118 | 28 % |
| Size claim, GP (design spacing) | 338 ± 35 | 114 | 50 / 52.8 | 0.68 | 118 | 13 % |
| Size claim, Delaunay, furnace grid | 335 ± 45 | 111 | 55 / 52.8 | 0.40 | 119 | 21 % |

1. **The guarantee holds in 4-D.** Every row stays within its allowance. The largest ratio, 1.19 for the pattern claim with random scores, has a one-sided probability of 0.08 under the picked levels. Nothing in the construction depends on the dimension: the design fixes each level's recipes, and the draw is uniform within the level.
2. **The score sets the cost.** Informed scores measured 321–397 of 1024 recipes; random scores 659–684, with the same guarantee.
3. **The claim sets the cost and the loss.** At matched difficulty (about 20 % of last-level recipes fail prediction under either claim), the whole-pattern claim measured 76 more recipes than the size claim and lost more of the mixed-phase recipes (27 % against 19 %).
4. **Where measurements go.** Both claims concentrate on the anatase→rutile front (0.1 < rutile fraction < 0.9, 36 % of recipes): 80 % of the pattern claim's measurements for want of a claim, 63 % of the size claim's. The size claim puts more of them where anatase coarsens fastest (41 % against 30 %, on 25 % of recipes) and along the edge where anatase vanishes at high temperature. The two claims share 43 % of these measurements. The contrast is weaker than on the synthetic scattering map because in this chemistry coarsening and transformation are both driven by temperature. (`placement.png`, `placement.json`.)
5. **The denominator matters again.** About 117 wrong skips per campaign (12 % of certified-level recipes, budget 20 % per level) cost 13–28 % of the mixed-phase recipes. A guarantee that protects the mixed-phase window needs the label-conditional form.
6. **Shared furnace runs leave the guarantee intact in the dry-run** (55 / 52.8). The truth is one realisation of the whole design, shared offsets included, fixed before any draw.

## What the dry-run says about a real pilot

- **Furnace runs, not samples, set the time.** On the furnace grid (21 temperatures × 5 dwell times), a campaign measured about 340 recipes but needed about 100 distinct furnace settings, 16–80 per level, and each level needs its calibration recipes fired before the rest are decided. With 8 furnaces and up to 16 h dwells, that is weeks, not days. A split-plot design, with temperature and dwell fixed at the coarse levels and dopant and seed varied per crucible, is the next step.
- **Noise floor.** The width of anatase (101) carries a counting-noise error of about 0.01° (median) and 0.03° (90th percentile) after smoothing; the size tolerance of 0.08° sits above it. In the lab, replicate syntheses at about 30 recipes set this floor, including synthesis scatter.
- **Interpolation in 4-D** works with barycentric weights on a Delaunay triangulation and with a GP; exact natural-neighbour coordinates are 2-D only.

## Not modelled

Dopant solubility limits and secondary phases, amorphous content, preferred orientation, sample-height error, failed or contaminated crucibles, drift of the diffractometer. Kinetic parameters are literature anchors, not fits to one material; the dopant effect is a saturating shift of the activation energy.


---

# Few-days pilot: the furnace run as the unit (`furnace.py`)

A furnace run is one temperature and one dwell and carries a tray of eight crucibles (the A-Lab methods: four box furnaces, up to eight samples per alumina tray; 2 °C/min to 300 °C, 15 °C/min to the hold, natural cooling; XRD 8 min per scan). Recipes that share a furnace setting share its cost, so a skip saves a furnace run only when every crucible of the run is skipped. The pilot therefore decides at run level:

- Design over the two furnace variables only: scrambled Sobol in temperature (500–1000 °C) × dwell (1–4 h, log scale), 128 runs in levels of 8, 8, 16, 32, 64 (or 64 runs: 8, 8, 16, 32); levels 0–1 are the seed.
- The tray is the same in every run. v1: dopant {0, 2, 5, 10 %} × rutile seed {0, 3 %}. v2: alumina {0, 2, 5, 10 wt%} × P25 blend {0, 30 %}. Every tray slot is a 2-D map over (temperature, dwell), so the exact natural-neighbour interpolant of the paper applies.
- Claims at run level: interest = some crucible is mixed phase; size = every crucible's anatase (101) width within 0.12°; pattern = every crucible's pattern within tolerance. R_E ≤ 0.20 at confidence 0.80, quantile path, 12 calibration runs per level.
- Schedule: waves of furnace runs packed onto 4 or 8 furnaces. Pipelined: every level's calibration runs are fired with the seed (the draws are uniform and need nothing measured), and their patterns stay unread until that level's predictor and scores are frozen; only the runs measured for want of a claim wait for the previous level. Cycle time = ramp + dwell + natural cooling to 100 °C (time constant 1.8 h, an assumption to be measured) + 0.5 h handling.

| Row | Model | Runs measured | Exceedances / allowed (P) | Runs with a mixed-phase crucible lost | Days: 4 furnaces, sequential, slow ramp | 4 furnaces, pipelined, fast ramp | 8 furnaces, pipelined, fast ramp |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 128 runs, size claim | v1 | 94 ± 6 of 128 | 22 / 23.6 (0.67) | 7 % | 10.1 | 8.0 | 4.5 |
| 128 runs, pattern claim | v1 | 102 ± 7 | 16 / 23.6 (0.97) | 7 % | 10.8 | 8.5 | 4.7 |
| 128 runs, random scores | v1 | 113 ± 9 | 30 / 23.6 (0.10) | 8 % | 11.8 | 9.2 | 5.1 |
| 64 runs, size claim | v1 | 53 ± 2 of 64 | 14 / 18.8 (0.91) | 6 % | 5.7 | 4.5 | 2.6 |
| 128 runs, size claim | v2 | 80 ± 6 of 128 | 21 / 23.6 (0.75) | 11 % | 8.7 | 6.8 | 3.9 |
| 128 runs, pattern claim | v2 | 83 ± 10 | 18 / 23.6 (0.92) | 9 % | 9.0 | 7.1 | 4.0 |
| 128 runs, random scores | v2 | 110 ± 10 | 27 / 23.6 (0.26) | 11 % | 11.5 | 9.0 | 5.0 |
| 64 runs, size claim | v2 | 48 ± 3 of 64 | 13 / 18.8 (0.95) | 10 % | 5.3 | 4.2 | 2.4 |

Findings:
1. **The guarantee holds at run level** in every row, including random scores.
2. **What fits in a few days:** 64 furnace runs (512 crucibles) in about 2.5 days on eight furnaces, or about 4–5 days on four. 128 runs take about 4 days on eight furnaces.
3. **Skipping saves 25–40 % of furnace runs** with informed scores (v2: 80 of 128), against 10–15 % with random scores. The saving is smaller than per recipe because a run is skipped only when all eight crucibles are covered; a claim that tolerates one failing crucible of eight would save more and is a choice to make before the pilot.
4. **The schedule is set by furnace cycles.** Removing the slow ramp to 300 °C (not needed for oxide powders) saves about 20 %; pipelining the calibration draws matters on eight furnaces, little on four. Cooling time is the largest single assumption and should be measured on the furnaces before the pilot.
5. **The realistic model makes interpolation easier and the whole-pattern claim harder.** In v2 the transformation front is broader (size distribution, alumina, P25 blend), so more runs are predictable; sample-to-sample intensity scale (8 %), displacement and the Kα₂ doublet raise the whole-pattern failure rate, so its tolerance was set at 25 % + 4σ to keep about 30 % of last-level runs failing.

Model v2 and its calibration: `experiments/tio2_calcination/MODEL_V2.md`, `model_v2.png`, `model_v2_calibration.json`.
