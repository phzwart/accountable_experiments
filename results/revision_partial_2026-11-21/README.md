# Partial revision runs, 2026-11-21 (snapshot before completion to 250 campaigns)

These are the runs reported in the first revision (response to the mock review panel, round 1).
They were stopped by hand when compute time ran short on a two-core machine, after a fixed number of
seeds in seed order (0, 1, 2, ...); the stopping did not depend on outcomes. Counts:

| run | IR | NaCl | synthetic |
|---|---|---|---|
| plans certified for all levels together (campaign_contract) | 105 | 128 | 60 |
| conformal risk control on the same draw (crc_baseline) | 100 | 100 | 42 |
| uniform sample of the same size (uniform_baseline.json) | 20 | 20 | 20 |
| certified final maps (uniform_baseline.json, certified_final) | 20 | 20 | 20 |

`campaign_contract/syn_audit.json`: attainment audit, 3000 draws on 20 recorded synthetic levels (four campaigns,
levels 4 to 8), campaign-level confidence. `revision_summary.json`: the summary the revised text quoted.
The completed runs (seeds 0 to 249) extend these files in `results/campaign_contract/`, `results/crc_baseline/`
and `results/uniform_baseline.json`; this directory is kept unchanged as the record of the partial runs.
