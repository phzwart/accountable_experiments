"""
Harmonised comparison across the three experiments.

Each row is one campaign. Rows are grouped so that every comparison holds
the shared statement fixed: the wrong-skip rate R_E on a level, at a
stated budget and confidence (docs/theory.md §3–4).

    python -m experiments.study            # seed 0, all rows
    python -m experiments.study --replicate 20 --rows nacl_fwhm_nested_watson ir_nested_watson
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from accountable import run_campaign

ROWS = {
    # NaCl: separate at 0.10 + 0.10, confidence 0.90 each -> R_E <= 0.20 at 0.80.
    # nested_path and priority_path state R_E <= 0.20 at 0.80 directly (one budget).
    "nacl_fwhm_separate_legacy": ("nacl_saxs", dict(target="fwhm", mode="2cert", confidence=0.90, nn_method="legacy")),
    "nacl_fwhm_separate_watson": ("nacl_saxs", dict(target="fwhm", mode="2cert", confidence=0.90, nn_method="watson")),
    "nacl_fwhm_nested_legacy": ("nacl_saxs", dict(target="fwhm", mode="2cert", policy="nested_path", eps=0.20, confidence=0.80, nn_method="legacy")),
    "nacl_fwhm_nested_watson": ("nacl_saxs", dict(target="fwhm", mode="2cert", policy="nested_path", eps=0.20, confidence=0.80, nn_method="watson")),
    "nacl_fwhm_priority_watson": ("nacl_saxs", dict(target="fwhm", mode="2cert", policy="priority_path", eps=0.20, confidence=0.80, nn_method="watson")),
    "nacl_qpeak_separate_legacy": ("nacl_saxs", dict(target="qpeak", mode="2cert", confidence=0.90, peak_eps=9.492458504457112, nn_method="legacy")),
    "nacl_qpeak_separate_watson": ("nacl_saxs", dict(target="qpeak", mode="2cert", confidence=0.90, peak_eps=9.492458504457112, nn_method="watson")),
    "nacl_qpeak_nested_watson": ("nacl_saxs", dict(target="qpeak", mode="2cert", policy="nested_path", eps=0.20, confidence=0.80, peak_eps=9.492458504457112, nn_method="watson")),
    "nacl_envelope_separate_watson": ("nacl_saxs", dict(target="envelope", mode="2cert", confidence=0.90, nn_method="watson")),
    # IR: one budget 0.10 at confidence 0.75 on R_E.
    "ir_legacy_sequential": ("ir_bioreef", dict(policy="legacy_sequential", nn_method="legacy")),
    "ir_nested_legacy": ("ir_bioreef", dict(policy="nested_path", nn_method="legacy")),
    "ir_nested_watson": ("ir_bioreef", dict(policy="nested_path", nn_method="watson")),
    "ir_separate_split_watson": ("ir_bioreef", dict(policy="separate", nn_method="watson")),
    "ir_priority_watson": ("ir_bioreef", dict(policy="priority_path", nn_method="watson")),
    # Synthetic: interpolation only, then both certificates.
    "syn_envelope_interp_legacy": ("synthetic_saxs", dict(target="envelope", mode="interp", nn_method="legacy")),
    "syn_envelope_interp_watson": ("synthetic_saxs", dict(target="envelope", mode="interp", nn_method="watson")),
    "syn_peak_interp_watson": ("synthetic_saxs", dict(target="peak", mode="interp", nn_method="watson")),
    "syn_peak_2cert_separate_watson": ("synthetic_saxs", dict(target="peak", mode="2cert", confidence=0.90, nn_method="watson")),
    "syn_peak_2cert_nested_watson": ("synthetic_saxs", dict(target="peak", mode="2cert", policy="nested_path", eps=0.20, confidence=0.80, nn_method="watson")),
    "syn_peak_2cert_priority_watson": ("synthetic_saxs", dict(target="peak", mode="2cert", policy="priority_path", eps=0.20, confidence=0.80, nn_method="watson")),
    # Gaussian-process protocols: isotropic kernel on the design, three length-scale rules.
    "ir_nested_gp_mle": ("ir_bioreef", dict(policy="nested_path", nn_method="watson", interp_model="gp_mle")),
    "nacl_fwhm_nested_gp_mle": ("nacl_saxs", dict(target="fwhm", mode="2cert", policy="nested_path", eps=0.20, confidence=0.80, nn_method="watson", interp_model="gp_mle")),
    "syn_peak_2cert_nested_gp_mle": ("synthetic_saxs", dict(target="peak", mode="2cert", policy="nested_path", eps=0.20, confidence=0.80, nn_method="watson", interp_model="gp_mle")),
    "ir_nested_gp_design": ("ir_bioreef", dict(policy="nested_path", nn_method="watson", interp_model="gp_design")),
    "nacl_fwhm_nested_gp_design": ("nacl_saxs", dict(target="fwhm", mode="2cert", policy="nested_path", eps=0.20, confidence=0.80, nn_method="watson", interp_model="gp_design")),
    "syn_peak_2cert_nested_gp_design": ("synthetic_saxs", dict(target="peak", mode="2cert", policy="nested_path", eps=0.20, confidence=0.80, nn_method="watson", interp_model="gp_design")),
    "ir_nested_gp_nonstationary": ("ir_bioreef", dict(policy="nested_path", nn_method="watson", interp_model="gp_nonstationary")),
    "nacl_fwhm_nested_gp_nonstationary": ("nacl_saxs", dict(target="fwhm", mode="2cert", policy="nested_path", eps=0.20, confidence=0.80, nn_method="watson", interp_model="gp_nonstationary")),
    "syn_peak_2cert_nested_gp_nonstationary": ("synthetic_saxs", dict(target="peak", mode="2cert", policy="nested_path", eps=0.20, confidence=0.80, nn_method="watson", interp_model="gp_nonstationary")),
    # Random scores for every certificate ("stock-picking chicken"): the order
    # of skips carries no information, and the guarantee must still hold.
    "ir_separate_random": ("ir_bioreef", dict(policy="separate", score="random", nn_method="watson")),
    "ir_nested_random": ("ir_bioreef", dict(policy="nested_path", score="random", nn_method="watson")),
    "ir_priority_random": ("ir_bioreef", dict(policy="priority_path", score="random", nn_method="watson")),
    "nacl_fwhm_separate_random": ("nacl_saxs", dict(target="fwhm", mode="2cert", confidence=0.90, score="random", nn_method="watson")),
    "nacl_fwhm_nested_random": ("nacl_saxs", dict(target="fwhm", mode="2cert", policy="nested_path", eps=0.20, confidence=0.80, score="random", nn_method="watson")),
    "nacl_fwhm_priority_random": ("nacl_saxs", dict(target="fwhm", mode="2cert", policy="priority_path", eps=0.20, confidence=0.80, score="random", nn_method="watson")),
    "syn_peak_2cert_separate_random": ("synthetic_saxs", dict(target="peak", mode="2cert", confidence=0.90, score="random", nn_method="watson")),
    "syn_peak_2cert_nested_random": ("synthetic_saxs", dict(target="peak", mode="2cert", policy="nested_path", eps=0.20, confidence=0.80, score="random", nn_method="watson")),
    "syn_peak_2cert_priority_random": ("synthetic_saxs", dict(target="peak", mode="2cert", policy="priority_path", eps=0.20, confidence=0.80, score="random", nn_method="watson")),
    # Synthetic SAXS, round 3: every site of interest, so the interpolation claim alone, on the full profile at
    # rtol = atol = 0.005; budget 0.10 at confidence 0.80. With one claim the forms of guarantee coincide.
    "syn_env_nested_watson": ("synthetic_saxs", dict(target="envelope", mode="interp", policy="nested_path", eps=0.10, confidence=0.80, nn_method="watson", tol=0.005)),
    "syn_env_nested_random": ("synthetic_saxs", dict(target="envelope", mode="interp", policy="nested_path", eps=0.10, confidence=0.80, score="random", nn_method="watson", tol=0.005)),
    "syn_env_nested_gp_mle": ("synthetic_saxs", dict(target="envelope", mode="interp", policy="nested_path", eps=0.10, confidence=0.80, nn_method="watson", interp_model="gp_mle", tol=0.005)),
    "syn_env_nested_gp_design": ("synthetic_saxs", dict(target="envelope", mode="interp", policy="nested_path", eps=0.10, confidence=0.80, nn_method="watson", interp_model="gp_design", tol=0.005)),
    "syn_env_nested_gp_nonstationary": ("synthetic_saxs", dict(target="envelope", mode="interp", policy="nested_path", eps=0.10, confidence=0.80, nn_method="watson", interp_model="gp_nonstationary", tol=0.005)),
}


def _load(exp):
    if exp == "nacl_saxs":
        from .nacl_saxs import adapter as A
        return A, A.load()[0]
    if exp == "ir_bioreef":
        from .ir_bioreef import adapter as A
        return A, A.load()
    from .synthetic_saxs import adapter as A
    return A, A.load()


def summarise(res) -> dict:
    lv = [r for r in res.per_level if not r.get("empty")]
    g = lv[0]["guarantees"] if lv else []
    shared = [x for x in g if x["event"] == "R_E"]
    final_out = [f["outside"] for f in res.final]
    vouched = np.isin(res.reason[[f["index"] for f in res.final]].astype(str),
                      ["interpolable", "not_interesting+interpolable"]) if res.final else np.zeros(0, bool)
    return dict(
        n_design=int(res.measured.sum() + res.skipped.sum()),
        n_measured=res.n_measured,
        n_skipped=int(res.skipped.sum()),
        reasons=res.summary()["reasons"],
        guarantee_RE=shared[0] if shared else None,
        guarantees=g,
        level_E=[round(r["level"]["E_rate"], 4) for r in lv],
        level_cert={nm: [round(r["certificates"][nm]["level_joint"], 4) for r in lv]
                    for nm in (lv[0]["certificates"] if lv else {})},
        rem_E=[round(r["rem"]["E_rate"], 4) for r in lv],
        n_skip_by_level=[r["n_skip"] for r in lv],
        map_covers=[m["covers"] for m in res.map_certificates],
        score_info=[r.get("score_info", {}) for r in lv],
        final_outside_vouched=float(np.mean(np.asarray(final_out)[vouched])) if vouched.any() else None,
    )


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", nargs="*", default=list(ROWS))
    ap.add_argument("--replicate", type=int, default=0, help="number of calibration seeds")
    ap.add_argument("--out", default="runs/study")
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    seeds = list(range(args.replicate)) if args.replicate else [0]
    cache = {}
    for name in args.rows:
        exp, kw = ROWS[name]
        if exp not in cache:
            cache[exp] = _load(exp)
        A, ds = cache[exp]
        for seed in seeds:
            path = out / (f"{name}.json" if not args.replicate else f"rep/{name}_s{seed:02d}.json")
            if path.exists():
                continue
            t0 = time.time()
            res = run_campaign(ds, A.config(ds, seed=seed, **kw))
            row = dict(name=name, experiment=exp, seed=seed, kwargs=kw, config=res.config,
                       seconds=round(time.time() - t0, 1), **summarise(res))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(row, indent=1, default=str))
            print(f"{name} s{seed}: measured {row['n_measured']}  rem_E {row['rem_E']}  ({row['seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
