# accountable

Accountable measurement campaigns. A site is skipped only when a certificate covers it, and every certificate carries a finite-sample bound on the rate of wrong skips. Two certificates share one footing:

- **interest**: the site is not interesting (for example, a diffraction line is absent, or no channel reaches an absorbance level);
- **interpolation**: the prediction from coarser measurements meets the tolerance, for the full spectrum or for a scalar derived from it (peak position, width, integrated intensity).

Scores only order the sites. The guarantee comes from a uniform calibration draw at each level of a hierarchical design. The mathematics is in [`docs/theory.md`](docs/theory.md) and the code layout in [`docs/architecture.md`](docs/architecture.md).

## Install

```bash
pip install -e .            # numpy, scipy, scikit-learn
pip install -e ".[legacy]"  # ssbc, only for the legacy_sequential policy
```

## Run

The three experiments read their data from a checkout of `_forge_accountable_experiments`. Set `ACCOUNTABLE_DATA` to its path; by default it is looked for next to this repository.

```bash
python -m experiments.run nacl_saxs --target fwhm --mode 2cert --confidence 0.9
python -m experiments.run ir_bioreef --policy nested_path --nn-method watson
python -m experiments.run synthetic_saxs --target peak --mode 2cert --policy nested_path --eps 0.2 --confidence 0.8
python -m experiments.study                      # the harmonised comparison
```

Each run writes `sites.npz` (per-site decision, reason, scores, thresholds, labels) and `result.json` (per-level records, guarantees, map certificate).

## Budget policies

| Policy | Statement | Use |
| --- | --- | --- |
| `separate` (default) | each certificate's joint rate ≤ its budget at its confidence; the shared wrong-skip rate ≤ the sum, at 1 − Σδ | the NaCl scheme |
| `nested_path` | the shared wrong-skip rate ≤ one budget at one confidence, along a label-free path | one budget for both certificates |
| `ltt_conditional` | conditional rate of one certificate, fixed-sequence Learn-then-Test | conditional claims, large calibration |
| `legacy_sequential` | none | reproduces the original IR run only |

New schemes register with `@accountable.register("name")` and must state their guarantee in the same terms, or state none.

## Natural-neighbour method

`--nn-method legacy` reproduces the original scripts decision for decision. `--nn-method watson` computes exact Sibson coordinates. It is continuous in the site positions and about five times faster. The legacy routine falls back to triangle-linear weights whenever Qhull returns a cell in clockwise order, which makes its predictions depend on vertex ordering. See `docs/reproduction.md`.

## Tests

```bash
pytest                                   # unit, geometry, Monte Carlo coverage, small campaigns
ACCOUNTABLE_SLOW=1 pytest tests/test_reproduce.py   # decision-by-decision match with the original scripts
```
