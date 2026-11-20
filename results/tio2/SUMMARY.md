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
