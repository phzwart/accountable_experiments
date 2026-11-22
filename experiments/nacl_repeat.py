"""
How often would a second measurement of the same NaCl site fail the width claim against the first? Two
replicates of every design site are made by adding independent Gaussian noise of the estimated window noise
sigma to the measured profile; the second is judged against the first with the claim's metric.

    python -m experiments.nacl_repeat
"""
import json
from pathlib import Path

import numpy as np

from experiments.record import build


def main():
    ds, cfg, _ = build("nacl_fwhm_nested_watson", 0, {})
    from experiments.nacl_saxs.adapter import noise_sigma
    sig = noise_sigma(ds)
    I = ds.oracle.truth(np.arange(ds.n))[ds.candidate]
    rng = np.random.default_rng(2026)
    shares = []
    for _ in range(20):
        a = np.clip(I + rng.normal(0, sig, I.shape), 0, None)
        b = np.clip(I + rng.normal(0, sig, I.shape), 0, None)
        fail = np.asarray(cfg.criterion.stats(a, b)["outside_mean"], bool)
        shares.append(fail.mean())
    out = dict(sigma=sig, share_mean=float(np.mean(shares)), share_sd=float(np.std(shares, ddof=1)), n_sites=int(I.shape[0]))
    print(out)
    Path("results/nacl_repeat.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
