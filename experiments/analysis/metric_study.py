"""
What the certified metric does to a campaign. Interpolation certificate only, quantile path,
natural-neighbour interpolation; budgets as in the record (IR 0.10 at 0.75; NaCl and synthetic
0.20 at 0.80); 100 campaigns per metric. Only the acceptance criterion changes between rows.

Basis metrics: the spectra of the seed sites (levels <= 2, known before any decision) define a
frozen basis. 'plain': SVD of all seed spectra. 'dedup': SVD of seed spectra after near-duplicates
are merged (greedy; cosine distance below a tenth of the median pairwise distance counts as a
duplicate), so a shape counts once whatever its abundance. Components to 99 % of the variance
(at most 10); each coefficient is divided by its spread over the spectra the basis was built from;
a prediction is accepted when the RMS over components is at most 0.1.

    python -m experiments.analysis.metric_study 100
"""
from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from accountable import AccuracyCriterion, SpectrumRoute, make_policy, run_campaign
from accountable.campaign import INTERP
from accountable.tails import worst_case_tail
from experiments.record_picked import poisson_binomial_sf
from experiments.study import _load

OUTD = Path("results/analysis/metric_study")
BUDGET = {"synthetic_saxs": (0.20, 0.80), "nacl_saxs": (0.20, 0.80), "ir_bioreef": (0.10, 0.75)}


def seed_idx(ds):
    cand = np.asarray(ds.candidate, bool) if ds.candidate is not None else np.ones(len(ds.points), bool)
    return np.flatnonzero(cand & (np.asarray(ds.levels) <= 2))


def seed_basis(ds, dedup, log_floor=None, var=0.99, rmax=10):
    idx = seed_idx(ds)
    X = np.asarray(ds.oracle.truth(idx), float)
    if log_floor is not None:
        X = np.log10(np.maximum(X, log_floor))
    if dedup:
        U = X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-30)
        D = 1.0 - U @ U.T
        d0 = 0.1 * np.median(D[np.triu_indices(len(U), 1)])
        keep = []
        for i in range(len(U)):
            if all(D[i, j] > d0 for j in keep):
                keep.append(i)
        X = X[keep]
    Xc = X - X.mean(0)
    _, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    cum = np.cumsum(S ** 2) / np.sum(S ** 2)
    r = int(min(rmax, np.searchsorted(cum, var) + 1, len(S)))
    return Vt[:r], S[:r] / np.sqrt(len(X)), len(X)


def criteria(exp, ds, A):
    q = ds.axis
    if exp == "synthetic_saxs":
        out = {
            "peak, absolute (Δq 0.005, ΔFWHM 0.001 Å⁻¹)": AccuracyCriterion(kind="peak", q=q, peak_eps=0.005, fwhm_eps=0.001),
            "peak, relative (Δq 5 %, ΔFWHM 10 %)": AccuracyCriterion(kind="peak", q=q, peak_eps=0.05, fwhm_eps=0.10, tol_mode="relative"),
            "profile, 0.01 + 1 %": AccuracyCriterion(kind="envelope", rtol=0.01, atol=0.01),
            "profile, relative 5 %": AccuracyCriterion(kind="envelope", rtol=0.05, atol=1e-9),
        }
    elif exp == "nacl_saxs":
        sigma = A.noise_sigma(ds)
        base = dict(kind="peak", q=q, q_center=A.Q200, q_halfwidth=A.Q200_HALF, include_position=False,
                    include_width=True, presence_sigma=sigma, presence_multiple=A.PRESENCE_C, q_unit="nm^-1")
        out = {
            "(200) FWHM, absolute (0.02 nm⁻¹)": AccuracyCriterion(fwhm_eps=0.02, tol_mode="absolute", **base),
            "(200) FWHM, relative (10 %)": AccuracyCriterion(fwhm_eps=0.10, tol_mode="relative", **base),
            "profile, 0.01 + 1 %": AccuracyCriterion(kind="envelope", rtol=0.01, atol=0.01, q_unit="nm^-1"),
            "profile, relative 5 %": AccuracyCriterion(kind="envelope", rtol=0.05, atol=1e-9, q_unit="nm^-1"),
        }
    else:
        out = {
            "window profile, 0.10 + 10 % (record)": AccuracyCriterion(kind="envelope", rtol=0.10, atol=0.10, signal_min=0.02),
            "window profile, relative 10 %": AccuracyCriterion(kind="envelope", rtol=0.10, atol=1e-9, signal_min=0.02),
        }
    floor = None
    if exp != "ir_bioreef":
        X = np.asarray(ds.oracle.truth(seed_idx(ds)), float)
        floor = 1e-3 * float(np.median(X[X > 0]))
    lg = "log-intensity " if floor is not None else ""
    for dedup, name in [(False, f"{lg}basis, plain SVD"), (True, f"{lg}basis, de-duplicated SVD")]:
        B, s, n = seed_basis(ds, dedup, log_floor=floor)
        out[f"{name} ({len(s)} comp. from {n} spectra)"] = AccuracyCriterion(
            kind="basis", basis=B, basis_scale=s, basis_tol=0.1, basis_log_floor=floor)
    res = {f"default | {k}": c for k, c in out.items()}
    for k, c in out.items():
        res[f"matched | {short(k)}"] = matched(ds, c)
    return res


def short(name):
    import re
    s = re.sub(r"\s*\((?!200\)).*?\)", "", name)
    s = re.sub(r"0\.\d+ \+ \d+ %", "absolute + relative", s)
    s = re.sub(r"relative \d+ %", "relative", s)
    return s


TARGET_FAIL = 0.15


def scaled(crit, f):
    """The same criterion with every tolerance multiplied by f (acceptance scores scale as 1/f)."""
    from dataclasses import replace
    return replace(crit, rtol=crit.rtol * f, atol=crit.atol * f, peak_eps=crit.peak_eps * f,
                   fwhm_eps=crit.fwhm_eps * f, basis_tol=crit.basis_tol * f)


def matched(ds, crit):
    """Difficulty-matched control: scale the tolerance so that 15 % of the sites on certified levels
    (3 and finer) fail when predicted from all design sites of the coarser levels. Uses the truth of
    the design, so it is a control for comparing metrics, not a campaign recipe."""
    from accountable.sibson import interpolate
    cand = np.asarray(ds.candidate, bool) if ds.candidate is not None else np.ones(len(ds.points), bool)
    lev = np.asarray(ds.levels)
    P = np.asarray(ds.points, float)
    scores = []
    for L in np.unique(lev[cand & (lev > 2)]):
        src = np.flatnonzero(cand & (lev < L))
        qi = np.flatnonzero(cand & (lev == L))
        Ih = interpolate(P[src], ds.oracle.truth(src), P[qi], images=getattr(ds, "images", None), method="watson")
        scores.append(np.asarray(crit.stats(ds.oracle.truth(qi), Ih)["score"], float))
    s = np.concatenate(scores)
    s = np.where(np.isfinite(s), s, 1e6)
    return scaled(crit, max(float(np.quantile(s, 1 - TARGET_FAIL)), 1e-9))


_C = {}


def setup(exp):
    if exp not in _C:
        A, ds = _load(exp)
        _C[exp] = (A, ds, criteria(exp, ds, A))
    return _C[exp]


def one(args):
    exp, metric, seed = args
    A, ds, crits = setup(exp)
    eps, conf = BUDGET[exp]
    crit = crits[metric]
    if exp == "ir_bioreef":
        cfg = A.config(ds, policy="nested_path", eps=eps, confidence=conf, seed=seed, nn_method="watson")
        cfg.certificates = [c for c in cfg.certificates if c.name == INTERP]
        cfg.policy = make_policy("nested_path", budget=eps, confidence=conf)
    else:
        cfg = A.config(ds, target="envelope", mode="interp", policy="nested_path", eps=eps, confidence=conf,
                       seed=seed, nn_method="watson")
    images = getattr(cfg.predictor, "images", None)
    cfg.criterion = crit
    cfg.predictor = SpectrumRoute(crit, images=images, nn_method="watson")
    cfg.final_labels = False
    cfg.post_labels = False
    res = run_campaign(ds, cfg)
    cand = np.asarray(ds.candidate, bool) if ds.candidate is not None else np.ones(len(ds.points), bool)
    lev = np.asarray(ds.levels)
    fail = np.asarray(res.fail_prior, bool)
    sk = np.asarray(res.skipped, bool)
    reason = np.asarray(res.reason).astype(str)
    inter = np.asarray(res.interesting, bool)
    wrong = sk & (reason == "interpolable") & fail
    checks = []
    for lv in res.per_level:
        if lv.get("empty"):
            continue
        k = lv["certificates"][INTERP]["k"]
        checks.append(dict(L=int(lv["L"]), picked=float(worst_case_tail(k, eps, lv["n_cal"], lv["n_level"], "hypergeometric")),
                           rate=float(lv["level"]["E_rate"]), exceeded=bool(lv["level"]["E_rate"] > eps + 1e-12)))
    certified = cand & (lev > 2)
    # Clumping: share of wrong skips with another wrong skip among the 6 nearest candidate sites,
    # against random placement of the same number among the skipped sites.
    ci = np.flatnonzero(cand)
    P = np.asarray(ds.points, float)[ci]
    _, nn = cKDTree(P).query(P, k=7)
    w = wrong[ci]
    s = sk[ci]

    def neigh_share(mask):
        if mask.sum() == 0:
            return np.nan
        return float(np.mean(mask[nn[mask, 1:]].any(1)))
    obs = neigh_share(w)
    rng = np.random.default_rng(seed)
    exp_ = np.nanmean([neigh_share(np.isin(np.arange(len(w)), rng.choice(np.flatnonzero(s), w.sum(), replace=False)))
                       for _ in range(20)]) if w.sum() and s.sum() >= w.sum() else np.nan
    return dict(exp=exp, metric=metric, seed=seed, measured=int(np.asarray(res.measured)[cand].sum()),
                n=int(cand.sum()), fail_share=float(fail[certified].mean()), wrong=int(wrong.sum()),
                wrong_share=float(wrong.sum() / certified.sum()),
                wrong_on_signal=float(inter[wrong].mean()) if wrong.any() else np.nan,
                signal_share_skipped=float(inter[sk & certified].mean()) if (sk & certified).any() else np.nan,
                clump=float(obs / exp_) if np.isfinite(obs) and np.isfinite(exp_) and exp_ > 0 else np.nan,
                checks=checks)


def summarise(rows):
    out = []
    for key in dict.fromkeys((r["exp"], r["metric"]) for r in rows):
        rs = [r for r in rows if (r["exp"], r["metric"]) == key]
        ch = [c for r in rs for c in r["checks"]]
        p = np.array([c["picked"] for c in ch])
        x = int(sum(c["exceeded"] for c in ch))
        a = lambda k: float(np.nanmean([r[k] for r in rs]))  # noqa: E731
        out.append(dict(exp=key[0], metric=key[1], campaigns=len(rs), n=rs[0]["n"],
                        measured=a("measured"), measured_sd=float(np.std([r["measured"] for r in rs])),
                        fail_share=a("fail_share"), wrong_share=a("wrong_share"),
                        mean_level_rate=float(np.mean([c["rate"] for c in ch])),
                        exceeded=x, checks=len(ch), allowed=float(p.sum()),
                        p_value=poisson_binomial_sf(p, x), wrong_on_signal=a("wrong_on_signal"),
                        signal_share_skipped=a("signal_share_skipped"), clump=a("clump")))
    return out


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    exps = sys.argv[2].split(",") if len(sys.argv) > 2 else ["ir_bioreef", "nacl_saxs", "synthetic_saxs"]
    OUTD.mkdir(parents=True, exist_ok=True)
    jobs = []
    for exp in exps:
        _, _, crits = setup(exp)
        jobs += [(exp, m, s) for m in crits for s in range(n)]
    with Pool(2) as pool:
        rows = list(pool.imap_unordered(one, jobs, chunksize=4))
    tag = "_".join(exps)
    (OUTD / f"runs_{tag}_n{n}.json").write_text(json.dumps(rows))
    summ = summarise(rows)
    (OUTD / f"summary_{tag}_n{n}.json").write_text(json.dumps(summ, indent=1))
    for s in summ:
        print(f"{s['exp'][:6]} | {s['metric'][:52]:52s} | meas {s['measured']:6.0f} | fail {s['fail_share']:.2f} | "
              f"rate {s['mean_level_rate']:.3f} | exc {s['exceeded']}/{s['checks']} vs {s['allowed']:.1f} | "
              f"signal {s['wrong_on_signal']:.2f}/{s['signal_share_skipped']:.2f} | clump {s['clump']:.2f}")
