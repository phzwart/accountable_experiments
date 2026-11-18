# Reproduction and harmonised comparison

A shared core is only useful if it reproduces what the three experiments already did, and if it then lets them be compared on one statement. This document records both. Numbers come from `python -m experiments.study` and `python -m experiments.aggregate` (`runs/study/summary.md`).

## 1. Decision-by-decision reproduction

The original scripts (`_forge_accountable_experiments`, commit f3af0d8) were run in this environment (Python 3.13, numpy 2.5.3, scipy 1.18.1, scikit-learn 1.9.1). The core, with `nn_method="legacy"`, reproduces every site's decision and reason. `tests/test_reproduce.py` checks this against the packed references.

| Case | Original (here) | Core | Site mismatches | Archived |
| --- | --- | --- | --- | --- |
| NaCl (200) width, two certificates, 0.90 | 684 | 684 | 0 | 671 |
| NaCl (200) width, interpolation only, 0.90 | 839 | 839 | 0 | 846 |
| NaCl peak q at 9.492 nm⁻¹, two certificates, 0.90 | 631 | 631 | 0 | 631 |
| NaCl (200) width, random scores, 0.90 | 957 | 957 | 0 | — |
| IR interest gate, original sequential rule | 285 (32 wrong) | 285 (32 wrong) | 0 | 278 (33 wrong) |
| Synthetic mixture, envelope, interpolation only | 511 | 511 | 0 | superseded |
| Synthetic mixture, peak, interpolation only | 448 | 448 | 0 | superseded |

The archived synthetic seed sequence used the earlier protocol, which passed the confidence in as a failure probability and targeted the conditional rate. The current code refuses that target, so the synthetic references use the joint target at confidence 0.90 with ε = 0.10.

## 2. Environment sensitivity of the legacy interpolant

The archived NaCl and IR numbers agree with the rerun through the first two certified levels and then drift. The cause is in the legacy natural-neighbour routine. Its polygon clip assumes a counter-clockwise clip polygon, and Qhull returns the query's Voronoi cell in either orientation. A clockwise cell clips to nothing, and the routine drops silently to barycentric weights on the enclosing Delaunay triangle. The legacy predictor is therefore Sibson at some sites and triangle-linear at others, with the switch set by vertex ordering:

- on 200 random sites, 134 of 300 queries take the triangle fallback;
- on the NaCl raster, a 10⁻⁹ perturbation of the positions flips 22 of 271 failure labels at L5 and 33 of 521 at L6;
- a different scipy or Qhull build changes the ordering, which accounts for the archived differences.

The guarantee is unaffected: each certificate controls the failure rate of the predictor that was actually used. The predictor is just not the one the write-ups name.

`nn_method="watson"` computes exact Sibson coordinates. Natural neighbours come from a circumcircle test, the query's cell is an intersection of half-planes, and each stolen area is a convex clip. A query on a hull edge gets the limiting weights, linear between the boundary sites that bracket it. On random sites these weights match brute-force stolen areas to Monte Carlo precision. On the NaCl raster the same perturbation changes predictions by at most 3 × 10⁻⁷ and flips no label. The method is about five times faster than the legacy routine.

## 3. Policies on one statement

Every row below states a bound on the shared wrong-skip rate R_E of each level (theory §3). Two-certificate NaCl and synthetic rows compare `separate` (0.10 per certificate at 0.90, hence R_E ≤ 0.20 at 0.80) with `nested_path` (R_E ≤ 0.20 at 0.80 directly). IR rows hold the statement of the original run, R_E ≤ 0.10 at 0.75.

| Row | Measured | Statement on R_E |
| --- | --- | --- |
| IR, original sequential rule (legacy geometry) | 285 / 949 | none |
| IR, nested path (legacy geometry) | 321 / 949 | ≤ 0.10 at 0.75 |
| IR, nested path (exact Sibson) | 269 / 949 | ≤ 0.10 at 0.75 |
| IR, separate, 0.05 per certificate at 0.875 | 949 / 949 | ≤ 0.10 at 0.75 |
| NaCl width, separate (legacy) | 684 / 1071 | ≤ 0.20 at 0.80 |
| NaCl width, separate (exact) | 762 / 1071 | ≤ 0.20 at 0.80 |
| NaCl width, nested path (legacy) | 578 / 1071 | ≤ 0.20 at 0.80 |
| NaCl width, nested path (exact) | 631 / 1071 | ≤ 0.20 at 0.80 |
| NaCl peak q 9.492, separate (legacy) | 631 / 1071 | ≤ 0.20 at 0.80 |
| NaCl peak q 9.492, separate (exact) | 630 / 1071 | ≤ 0.20 at 0.80 |
| NaCl peak q 9.492, nested path (exact) | 588 / 1071 | ≤ 0.20 at 0.80 |
| NaCl envelope, separate (exact) | 800 / 1071 | ≤ 0.20 at 0.80 |
| Synthetic envelope, interpolation (legacy) | 511 / 2118 | ≤ 0.10 at 0.90 |
| Synthetic envelope, interpolation (exact) | 637 / 2118 | ≤ 0.10 at 0.90 |
| Synthetic peak, interpolation (exact) | 503 / 2118 | ≤ 0.10 at 0.90 |
| Synthetic peak, separate (exact) | 358 / 2118 | ≤ 0.20 at 0.80 |
| Synthetic peak, nested path (exact) | 440 / 2118 | ≤ 0.20 at 0.80 |

Seed 0 only. Three readings follow.

The original IR rule has no finite-sample claim, and it can fail the claim it intended. On a population with uninformative scores, its shared rate exceeds 0.10 in 28.7% of calibration draws against a nominal 25%, about four standard errors over (`tests/test_coverage_mc.py`). The nested path states R_E ≤ 0.10 at 0.75 validly and, with exact Sibson, measures fewer sites than the original rule. Splitting the IR budget across two separate certificates is infeasible at m = 40: ε = 0.05 at confidence 0.875 lies below the zero-failure floor of 0.051, so every level is measured.

Neither policy dominates. The nested path is cheaper on NaCl and dearer on the synthetic peak. It spends one budget where the failures fall, and `separate` keeps each certificate's own statement. Both are valid, and the choice is a design decision for each campaign.

Exact Sibson costs measurements on the spectrum route for targets that blur under averaging. Averaging more neighbours' spectra broadens a predicted peak. Over 20 calibration seeds, the NaCl width campaign measures 766 sites with exact weights against 743 with the legacy mixture. The seed-0 gap (762 against 684) overstates it.

## 4. Replication over calibration seeds

Twenty calibration seeds per row. Each count is the number of level-rate trials (4 levels × 20 seeds) above the budget. The nominal value is the failure probability that the statement allows.

| Row | Mean measured | Event | Budget | Nominal | Exceedances | 95% interval |
| --- | --- | --- | --- | --- | --- | --- |
| IR, original rule | 282 | R_E (intended) | 0.10 | 0.25 | 0/80 | 0.000–0.045 |
| IR, nested path (exact) | 282 | R_E | 0.10 | 0.25 | 0/80 | 0.000–0.045 |
| NaCl width, nested path (exact) | 651 | R_E | 0.20 | 0.20 | 6/80 | 0.028–0.156 |
| NaCl width, separate (legacy) | 743 | R_interest | 0.10 | 0.10 | 2/80 | 0.003–0.087 |
| | | R_interp | 0.10 | 0.10 | 2/80 | 0.003–0.087 |
| | | R_E | 0.20 | 0.20 | 0/80 | 0.000–0.045 |
| NaCl width, separate (exact) | 766 | R_interest | 0.10 | 0.10 | 3/80 | 0.008–0.106 |
| | | R_interp | 0.10 | 0.10 | 0/80 | 0.000–0.045 |
| | | R_E | 0.20 | 0.20 | 0/80 | 0.000–0.045 |
| NaCl peak q 9.492, nested path (exact) | 581 | R_E | 0.20 | 0.20 | 5/80 | 0.021–0.140 |

Every observed exceedance rate is at or below its nominal failure probability. On these data the original IR rule did not exceed its intended rate; its failure shows on populations with uninformative scores. Levels within one seed share a calibration stream and a measured set, so the 80 trials of a row are not independent.

## 5. Reproducing this document

```bash
python -m experiments.study
python -m experiments.study --replicate 20 --rows nacl_fwhm_separate_watson nacl_fwhm_nested_watson \
    ir_nested_watson ir_legacy_sequential nacl_qpeak_nested_watson nacl_fwhm_separate_legacy
python -m experiments.aggregate > runs/study/summary.md
ACCOUNTABLE_SLOW=1 pytest tests/test_reproduce.py
```
