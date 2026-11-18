"""
Pack decisions produced by the original scripts into tests/data/legacy_refs.npz.

The dumps come from running the original code (_forge_accountable_experiments
at commit f3af0d8) in the same environment as the tests. See
docs/reproduction.md for the commands and the environment.
"""
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy
import sklearn

REASONS = ["unassigned", "seed", "calibration", "no_certificate", "interpolable",
           "not_interesting", "not_interesting+interpolable"]
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/legacy_ref")
OUT = Path(__file__).resolve().parents[1] / "tests" / "data"

CASES = {
    "nacl_fwhm_2cert_c90_s0_logistic": dict(experiment="nacl_saxs", kw=dict(target="fwhm", mode="2cert", confidence=0.9, seed=0)),
    "nacl_fwhm_interp_c90_s0_logistic": dict(experiment="nacl_saxs", kw=dict(target="fwhm", mode="interp", confidence=0.9, seed=0)),
    "nacl_qpeak_2cert_c90_s0_logistic_pe": dict(experiment="nacl_saxs", kw=dict(target="qpeak", mode="2cert", confidence=0.9, seed=0, peak_eps=9.492458504457112)),
    "nacl_fwhm_2cert_c90_s0_random": dict(experiment="nacl_saxs", kw=dict(target="fwhm", mode="2cert", confidence=0.9, seed=0, score="random")),
    "syn_envelope": dict(experiment="synthetic_saxs", kw=dict(target="envelope", mode="interp", confidence=0.9, seed=0)),
    "syn_peak": dict(experiment="synthetic_saxs", kw=dict(target="peak", mode="interp", confidence=0.9, seed=0)),
    "ir_legacy": dict(experiment="ir_bioreef", kw=dict(policy="legacy_sequential")),
}

arrays, meta = {}, {}
for name, spec in CASES.items():
    f = SRC / f"{name}.npz"
    if not f.exists():
        print("missing", f)
        continue
    z = np.load(f, allow_pickle=True)
    arrays[f"{name}__measured"] = np.asarray(z["measured"], bool)
    if "reason" in z.files:
        arrays[f"{name}__reason"] = np.array([REASONS.index(str(r)) for r in z["reason"]], np.int8)
    meta[name] = spec
for spec in meta.values():
    spec["kw"]["nn_method"] = "legacy"
meta["_reasons"] = REASONS
meta["_environment"] = dict(python=platform.python_version(), numpy=np.__version__,
                            scipy=scipy.__version__, sklearn=sklearn.__version__,
                            legacy_commit="f3af0d8")
OUT.mkdir(parents=True, exist_ok=True)
np.savez_compressed(OUT / "legacy_refs.npz", **arrays)
(OUT / "legacy_refs.json").write_text(json.dumps(meta, indent=1))
print("packed", sorted(meta))
