"""
Map bound with the exact hypergeometric upper limit: the largest share K'/N of failing sites that the observed
number f of failures in m calibration draws does not reject at confidence 1 - delta_map. Recomputed from the
run record for the three main configurations, against the Clopper-Pearson limit the record stores.

    python -m experiments.map_bound_exact
"""
import gzip
import json
from pathlib import Path

import numpy as np
from scipy.stats import hypergeom

from experiments.record import OUT as REC, build

ROWS = {"ir": "ir_nested_watson", "nacl": "nacl_fwhm_nested_watson", "syn": "syn_peak_2cert_nested_watson"}


def upper_hyp(f, m, N, conf):
    d = 1.0 - conf
    Ks = np.arange(0, N + 1)
    ok = hypergeom.cdf(f, N, Ks, m) > d  # K' not rejected
    return Ks[ok].max() / N


def main():
    out = {}
    for key, row in ROWS.items():
        ds, cfg, _ = build(row, 0, {})
        sizes = {int(L): int(((ds.levels == L) & ds.candidate).sum()) for L in np.unique(ds.levels)}
        cov_cp, cov_h, wid_cp, wid_h, n = 0, 0, [], [], 0
        for line in gzip.open(REC / row / "runs.jsonl.gz", "rt"):
            r = json.loads(line)
            for mc in r.get("map_certificates", []):
                N = sizes[mc["from_level"]]
                K = mc["level_fail_fraction"]
                uh = upper_hyp(mc["failures"], mc["m"], N, mc["confidence"])
                cov_cp += mc["upper"] >= K - 1e-12
                cov_h += uh >= K - 1e-12
                wid_cp.append(mc["upper"]); wid_h.append(uh); n += 1
        out[key] = dict(n=n, coverage_cp=cov_cp / n, coverage_hyp=cov_h / n,
                        mean_upper_cp=float(np.mean(wid_cp)), mean_upper_hyp=float(np.mean(wid_h)))
        print(key, out[key], flush=True)
    Path("results/map_bound_exact.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
