"""
Site-by-site reproduction of the original scripts (slow; needs the data).

References in tests/data were produced by the original code in the
environment recorded in legacy_refs.json. Natural-neighbour weights from
the legacy method depend on Qhull's vertex ordering, so a different
scipy build can change a few decisions; see docs/reproduction.md.
"""
import json
import os
from pathlib import Path

import numpy as np
import pytest

from accountable import run_campaign

DATA = Path(__file__).parent / "data"
REFS = json.loads((DATA / "legacy_refs.json").read_text()) if (DATA / "legacy_refs.json").exists() else {}
ARR = np.load(DATA / "legacy_refs.npz") if (DATA / "legacy_refs.npz").exists() else None

try:
    from experiments._paths import data_root
    data_root()
    HAVE_DATA = True
except Exception:
    HAVE_DATA = False

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(not HAVE_DATA or ARR is None, reason="experiment data or references missing"),
    pytest.mark.skipif(os.environ.get("ACCOUNTABLE_SLOW") != "1", reason="set ACCOUNTABLE_SLOW=1"),
]

CASES = [k for k in REFS if not k.startswith("_")]


def _build(spec):
    exp, kw = spec["experiment"], dict(spec["kw"])
    if exp == "nacl_saxs":
        from experiments.nacl_saxs import adapter as A
        ds, _ = A.load()
    elif exp == "ir_bioreef":
        from experiments.ir_bioreef import adapter as A
        ds = A.load()
    else:
        from experiments.synthetic_saxs import adapter as A
        ds = A.load()
    if kw.get("policy", "separate") != "legacy_sequential":
        # The original scripts used the binomial tail and stopped at a calibration score.
        pk = dict(tail="binomial", placement="calibration")
        kw["policy_kwargs"] = pk
    return ds, A.config(ds, **kw)


@pytest.mark.parametrize("case", CASES)
def test_decisions_match_original(case):
    ds, cfg = _build(REFS[case])
    res = run_campaign(ds, cfg)
    assert np.array_equal(res.measured, ARR[f"{case}__measured"])
    key = f"{case}__reason"
    if key in ARR.files:
        names = REFS["_reasons"]
        ref = np.array([names[i] for i in ARR[key]])
        assert np.array_equal(res.reason.astype(str), ref)
