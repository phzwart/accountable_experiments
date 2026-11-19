"""
The run record: every campaign of the study, repeated over calibration
seeds, logged in full.

    python -m experiments.record run --rows ir_nested_watson,ir_priority_watson --seeds 0-249
    python -m experiments.record pack
    python -m experiments.record summary > results/record/SUMMARY.md

``run`` writes one file per campaign to runs/record/<row>/ (resumable).
``pack`` gathers them into results/record/<row>/:

- runs.jsonl.gz: one line per seed with the configuration, the summary,
  every per-level record (thresholds, k with both tails, guarantees,
  calibration counts, level and remainder rates, map certificate), the
  wall time and the package versions;
- sites.npz: per seed and design site (candidate sites only, in the
  order of ``site_index``): decision reason code, measured, skipped,
  calibration, interest and interpolation labels, and the frozen score of
  each certificate.
"""
from __future__ import annotations

import argparse
import gzip
import json
import platform
import subprocess
import time
from pathlib import Path

import numpy as np

from accountable import make_policy, run_campaign
from experiments.study import ROWS as STUDY_ROWS
from experiments.study import _load, summarise

RUNS = Path("runs/record")
OUT = Path("results/record")
REASONS = ["unassigned", "seed", "calibration", "no_certificate", "not_interesting",
           "interpolable", "not_interesting+interpolable"]

# Rows of the paper: three forms of guarantee and three GP protocols per
# dataset, and the IR protocol comparison at a tight tolerance.
PAPER_ROWS = [
    "ir_separate_split_watson", "ir_nested_watson", "ir_priority_watson",
    "ir_nested_gp_mle", "ir_nested_gp_design", "ir_nested_gp_nonstationary",
    "nacl_fwhm_separate_watson", "nacl_fwhm_nested_watson", "nacl_fwhm_priority_watson",
    "nacl_fwhm_nested_gp_mle", "nacl_fwhm_nested_gp_design", "nacl_fwhm_nested_gp_nonstationary",
    "syn_peak_2cert_separate_watson", "syn_peak_2cert_nested_watson", "syn_peak_2cert_priority_watson",
    "syn_peak_2cert_nested_gp_mle", "syn_peak_2cert_nested_gp_design", "syn_peak_2cert_nested_gp_nonstationary",
] + [f"ir_tight{v}_{p}" for v in ("", "_interp") for p in ("sibson", "gp_mle", "gp_design", "gp_nonstationary")]

# Random scores for every certificate: the "stock-picking chicken".
CHICKEN_ROWS = [f"{d}_{f}_random" for d in ("ir", "nacl_fwhm", "syn_peak_2cert")
                for f in ("separate", "nested", "priority")] + ["ir_tight_random"]
PAPER_ROWS = PAPER_ROWS + CHICKEN_ROWS


def versions():
    out = dict(python=platform.python_version(), platform=platform.platform())
    for mod in ("numpy", "scipy", "sklearn", "torch", "gpytorch", "botorch"):
        try:
            out[mod] = __import__(mod).__version__
        except Exception:
            out[mod] = None
    try:
        out["git_commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        out["git_dirty"] = bool(subprocess.check_output(["git", "status", "--porcelain", "src", "experiments"], text=True).strip())
    except Exception:
        out["git_commit"] = None
    return out


def build(row, seed, cache):
    """Dataset and campaign configuration of one row and seed."""
    if row.startswith("ir_tight"):
        from experiments.ir_bioreef import adapter as A
        interp_only = row.startswith("ir_tight_interp_")
        proto = row.split("_", 3)[-1] if interp_only else row[len("ir_tight_"):]
        score = "logistic"
        if proto == "random":
            proto, score = "sibson", "random"
        if "ir" not in cache:
            cache["ir"] = A.load()
        ds = cache["ir"]
        saved = (A.RTOL, A.ATOL, A.FLOOR)
        A.RTOL, A.ATOL, A.FLOOR = 0.10, 0.01, 0.005
        try:
            cfg = A.config(ds, policy="nested_path", eps=0.10, confidence=0.75, seed=seed,
                           interp_model=proto, score=score)
        finally:
            A.RTOL, A.ATOL, A.FLOOR = saved
        if interp_only:
            cfg.certificates = [c for c in cfg.certificates if c.name == "interp"]
            cfg.policy = make_policy("nested_path", budget=0.10, confidence=0.75)
        else:
            cfg.certificates[0].cap = 0.02 if score != "random" else None
            cfg.interest = A.interest_predicate(0.02)
        spec = dict(experiment="ir_bioreef", tolerance="rtol 0.10, atol 0.01, floor 0.005",
                    interest=None if interp_only else 0.02, interp_model=proto, score=score,
                    policy="nested_path", eps=0.10, confidence=0.75)
        return ds, cfg, spec
    exp, kw = STUDY_ROWS[row]
    if exp not in cache:
        cache[exp] = _load(exp)
    A, ds = cache[exp]
    return ds, A.config(ds, seed=seed, **kw), dict(experiment=exp, **kw)


def _final_labels_off(row):
    """
    Final-map labels and end-of-level ("post") remainder labels refit the
    predictor on the measured set after the level. For maximum-likelihood
    GP rows those refits dominate the run time (about 50 s on the
    synthetic map) and change no decision, so they are skipped there and
    recorded as skipped in each run's spec.
    """
    return "gp_mle" in row


def run(rows, seeds):
    cache = {}
    env = versions()
    for row in rows:
        d = RUNS / row
        d.mkdir(parents=True, exist_ok=True)
        for s in seeds:
            fj = d / f"s{s:03d}.json"
            if fj.exists():
                continue
            ds, cfg, spec = build(row, s, cache)
            if _final_labels_off(row):
                cfg.final_labels = False
                cfg.post_labels = False
                spec = dict(spec, final_labels=False, post_labels=False)
            t0 = time.time()
            res = run_campaign(ds, cfg)
            secs = time.time() - t0
            cand = np.flatnonzero(ds.candidate)
            code = {r: i for i, r in enumerate(REASONS)}
            arrays = dict(
                reason=np.array([code[str(r)] for r in res.reason[cand]], np.uint8),
                measured=res.measured[cand], skipped=res.skipped[cand], is_cal=res.is_cal[cand],
                interesting=res.interesting[cand], fail_prior=res.fail_prior[cand],
                **{f"score_{k}": v[cand].astype(np.float32) for k, v in res.scores.items()},
            )
            np.savez_compressed(d / f"s{s:03d}.npz", **arrays)
            rec = dict(row=row, seed=s, spec=spec, config=res.config, seconds=round(secs, 2),
                       summary=res.summary(), study=summarise(res), per_level=res.per_level,
                       map_certificates=res.map_certificates, env=env)
            fj.write_text(json.dumps(rec, default=_default))
            print(f"{row} s{s:03d} measured {res.n_measured} ({secs:.1f}s)", flush=True)


def _default(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def pack():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = dict(rows={}, reasons=REASONS, packed=time.strftime("%Y-%m-%d %H:%M:%S %Z"))
    cache = {}
    for d in sorted(p for p in RUNS.iterdir() if p.is_dir()):
        row = d.name
        js = sorted(d.glob("s*.json"))
        if not js:
            continue
        o = OUT / row
        o.mkdir(parents=True, exist_ok=True)
        recs = [json.loads(p.read_text()) for p in js]
        with gzip.open(o / "runs.jsonl.gz", "wt") as fh:
            for r in recs:
                fh.write(json.dumps(r) + "\n")
        arrs = [dict(np.load(p.with_suffix(".npz"))) for p in js]
        ds, _, spec = build(row, 0, cache)
        stacked = {k: np.stack([a[k] for a in arrs]) for k in arrs[0]}
        np.savez_compressed(o / "sites.npz", seeds=np.array([r["seed"] for r in recs]),
                            site_index=np.flatnonzero(ds.candidate),
                            levels=ds.levels[ds.candidate], **stacked)
        manifest["rows"][row] = dict(spec=spec, n_runs=len(recs), seeds=[recs[0]["seed"], recs[-1]["seed"]],
                                     seconds_total=round(sum(r["seconds"] for r in recs), 1),
                                     env=recs[0]["env"], config=recs[0]["config"])
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=1, default=_default))


def load_row(row):
    with gzip.open(OUT / row / "runs.jsonl.gz", "rt") as fh:
        return [json.loads(line) for line in fh]


def summary():
    from accountable.tails import clopper_pearson
    print("| Row | Runs | Measured (mean ± s.d.) | Event | Budget | Allowed failure | Exceedances / level checks | Rate | 95 % interval |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in PAPER_ROWS:
        if not (OUT / row / "runs.jsonl.gz").exists():
            continue
        recs = load_row(row)
        meas = np.array([r["summary"]["n_measured"] for r in recs])
        first = recs[0]["per_level"]
        events = []
        for lv in first:
            for g in lv.get("guarantees", []):
                if g["event"] not in [e[0] for e in events]:
                    events.append((g["event"], g["budget"], 1 - g["confidence"]))
        for ev, b, fail in events:
            vals = []
            for r in recs:
                for lv in r["per_level"]:
                    if lv.get("empty"):
                        continue
                    if ev == "R_E":
                        vals.append(lv["level"]["E_rate"])
                    else:
                        vals.append(lv["certificates"][ev[2:]]["level_joint"])
            vals = np.asarray(vals, float)
            vals = vals[np.isfinite(vals)]
            k = int(np.sum(vals > b + 1e-12))
            lo, hi = clopper_pearson(k, len(vals), 0.95)
            print(f"| {row} | {len(recs)} | {meas.mean():.0f} ± {meas.std(ddof=1):.0f} | {ev} | {b:.2f} | {fail:.3f} | "
                  f"{k}/{len(vals)} | {k / max(len(vals), 1):.3f} | {lo:.3f}–{hi:.3f} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run", "pack", "summary"))
    ap.add_argument("--rows", default=",".join(PAPER_ROWS))
    ap.add_argument("--seeds", default="0-249")
    a = ap.parse_args()
    if a.cmd == "run":
        lo, hi = (int(x) for x in a.seeds.split("-"))
        run(a.rows.split(","), range(lo, hi + 1))
    elif a.cmd == "pack":
        pack()
    else:
        summary()


if __name__ == "__main__":
    main()
