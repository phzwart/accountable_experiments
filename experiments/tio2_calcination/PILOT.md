# An accountable calcination campaign: pilot design for an autonomous synthesis laboratory

Draft, 20 November 2026. Technical detail: `PILOT_technical_appendix.md` (forward model, observation
model, fit, statistics). Dry-run records: `results/tio2/` (SUMMARY.md, INVERSE.md, kinetics_worlds/).

## Aim

An autonomous synthesis campaign decides which furnace runs to fire. The pilot tests two things on a
real campaign:

1. **Every action is certified.** A run is skipped because a stated claim covers it, with a bound on
   how often such skips are wrong; a run is fired because the seed, the calibration draw or the absence
   of a covering claim required it. The bound is checked afterwards by firing the skipped runs.
2. **The fired runs still teach the process.** The activation energies of the anatase-to-rutile
   transformation, fitted to the fired runs alone, agree with those fitted to all runs, and carry more
   information than a random set of the same size.

The statistical machinery and its checks on three fully measured datasets are in the companion
manuscript (accountable experiments); this pilot is its first test on a synthesis instrument.

## System

Nanocrystalline anatase calcined in air; rutile forms by interface and surface nucleation and grows
at anatase–rutile contacts [Zhang & Banfield 1999, 2000; Hanaor & Sorrell 2011]. Each crucible is read
by powder diffraction: rutile fraction from a two-phase profile fit of anatase (101) and rutile (110),
crystallite sizes from peak widths.

## Design

- **Unit of decision:** a furnace run (one temperature, one dwell, one tray of eight crucibles).
- **Tray:** alumina at 0, 2, 5 and 10 wt%, each without and with 30 % P25 (an anatase–rutile powder that
  seeds contact growth).
- **Design space:** temperature 500–1000 °C, dwell 1–4 h (log scale).
- **Design:** 64 runs as a scrambled Sobol sequence cut into nested blocks of 8, 8, 16 and 32 runs. The
  levels are fixed before the campaign, which is all the guarantee requires; the nesting and the even
  spread serve the map.
- **Seed:** the first 16 runs, fired in full.
- **Per certified level (16 and 32 runs):** fit and freeze the predictor (natural-neighbour weights in
  temperature × log dwell) and the scores; draw 12 runs uniformly for calibration; fire and read them;
  set the thresholds; skip covered runs, fire the rest.
- **Claims:**
  - interest: some crucible holds both phases (rutile fraction 0.1–0.9);
  - size: the width of anatase (101) is predicted within 0.12° in every crucible where the line is present.
- **Guarantee:** wrong-skip rate at most 0.20 of a level's runs, at confidence 0.80.
- **Audit:** after the campaign, every skipped run is fired, so every bound can be checked.

## Predictions from the dry run

The dry run uses a forward model calibrated to published kinetics, an A-Lab-like furnace programme and
a laboratory diffractometer, with furnace offsets (5 °C per run), dosing errors and counting noise.
Over 30 simulated worlds:

| Quantity | Prediction |
| --- | --- |
| Runs fired | about 48 of 64 |
| Guarantee | 6 exceedances in 60 level checks against 5.6 allowed (one-sided probability 0.50) |
| Information in the fired runs (D-efficiency relative to all 64) | median 0.85; random subsets of the same size 0.74; higher than the paired random subset in 27 of 30 worlds |
| Information lost by skipping | less than for 98 % of random drops of the same size |
| Errors of the activation energies, surface nucleation / contact growth / anatase coarsening / rutile coarsening | 14 / 26 / 29 / 14 kJ/mol from the fired runs; 15 / 28 / 28 / 14 from all runs; 18 / 29 / 34 / 15 from random subsets |
| Temperature of half conversion, 1–4 h | within about 6 °C |
| Time | about 2.5 days on eight furnaces, 4–5 days on four (64 runs, pipelined calibration, fast ramp) |

In the dry run every rejection under the size claim at the certified levels came from anatase predicted
but absent, or the reverse: failures sit on the transformation front.

## Analysis plan, fixed before the campaign

Each element removed a bias larger than the statistical error in the dry run (technical appendix,
Table S7.2):

1. Rutile fraction from integrated areas of a two-phase profile fit (height × width biases it by up to 0.07).
2. Fractions below 0.03 treated as below the detection limit (one-sided residuals).
3. Rutile size and microstrain separated with two reflections, (110) and (101).
4. Standard errors clustered by furnace run, whose crucibles share a temperature offset.
5. Kinetic model: interface and surface nucleation with size-dependent activation energy, contact
   growth, alumina inhibition, coarsening of both phases; interface nucleation and the size coefficient
   held at literature values.

## What is needed from the laboratory

- Four to eight box furnaces for about one week, alumina trays of eight crucibles, the standard
  programme with the slow ramp removed (oxide precursors).
- Powder XRD of every crucible, 20–60° 2θ.
- A thermocouple log of every firing: it removes the largest unmodelled term (the run offset) from the
  kinetic fit.
- A measured cooling curve of the furnaces: the largest assumption in the schedule.
- 64 + 16 runs in total: the campaign, plus firing the skipped runs for the audit.

## Risks

- Real kinetics may differ from the forward model (heating-rate effects, agglomeration, brookite).
  The guarantee is unaffected; the kinetic comparison is relative between sets of runs.
- A crucible failure (spill, weak pattern) affects a whole run's claim; a claim that tolerates one
  failing crucible of eight is an option to decide before the campaign.
- The forward model generates and fits its own data in the dry run, so the predicted errors are
  optimistic in absolute terms; the comparison between fired, all and random runs is the prediction.

## Second candidate

The same design applies to closed-loop SAXS phase mapping of polymer blends (Upreti et al., ChemRxiv
2026, doi:10.26434/chemrxiv.15012310): a nested design over the composition grid fixed in advance,
part of each batch drawn uniformly for calibration, and the ordering label and peak-ratio prediction
as the two claims.
