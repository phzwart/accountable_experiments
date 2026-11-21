"""
Uncertified campaigns on all three maps, with the same Gaussian process as the certified GP campaigns
(maximum-likelihood hyperparameters, shared kernel over the spectrum) and the claims of each dataset.

At every level after the seed, the GP is fitted to the sites measured so far. For each site of the level it
states, from its own posterior, the probability that the site is of interest and the probability that its
posterior-mean prediction fails the accuracy criterion: K spectra are drawn from the posterior (along the
principal directions of the measured spectra, clipped at zero) and the dataset's interest predicate and criterion are applied to them.
A site is skipped under each claim whose stated failure probability is at most alpha, and measured otherwise.
Three versions of the posterior standard deviation are used:

    latent      sd of the latent function (unit-scale posterior sd times the channel's prior scale)
    predictive  latent plus the fitted nugget
    loo         predictive, rescaled so that 68 % of the standardised leave-one-out residuals of the
                measured set fall within one sd (a recalibration on the data at hand)

The campaign records, per site, its action, the probability it stated for a wrong skip, and whether the
skip was wrong against the full scan. Nothing is calibrated on a random draw, so no rate is guaranteed.

    python -m experiments.uncertified_all [nacl|ir|syn ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from experiments.record import build

ROWS = {"nacl": "nacl_fwhm_nested_gp_mle", "ir": "ir_nested_gp_mle", "syn": "syn_peak_2cert_nested_gp_mle"}
ALPHAS = (0.01, 0.05, 0.10, 0.20, 0.32)
KINDS = ("latent", "predictive", "loo")
K = 64
OUT = Path("results/uncertified")


def loo_kappa(eng, Y_src, sigma_c):
    """Scale that puts 68 % of the standardised leave-one-out residuals within one predictive sd."""
    import torch
    Ainv = torch.cholesky_inverse(eng._L).cpu().numpy()
    Yc = Y_src - Y_src.mean(0)
    d = np.diag(Ainv)
    r = (Ainv @ Yc) / d[:, None]
    s = np.sqrt(1.0 / d)[:, None] * sigma_c[None, :]
    ok = sigma_c > 1e-12 * sigma_c.max()
    z = np.abs(r[:, ok] / s[:, ok])
    return float(np.quantile(z, 0.6827))


def pc_basis(Y_src, frac=0.99, q_max=20):
    """Principal directions of the measured spectra that carry ``frac`` of their variance, with score sds."""
    Yc = Y_src - Y_src.mean(0)
    U, S, Vt = np.linalg.svd(Yc, full_matrices=False)
    var = S ** 2
    q = int(min(q_max, np.searchsorted(np.cumsum(var) / var.sum(), frac) + 1))
    return Vt[:q], S[:q] / np.sqrt(len(Y_src))


def stated_probabilities(cfg, ds, mean, scale, V, s_pc, rng):
    """Posterior probabilities that the site is of interest and that the mean prediction fails. Posterior
    spectra are drawn along the principal directions of the measured spectra (the basis on which the GP's
    hyperparameters were fitted), each with its score sd times the site's posterior sd at unit scale."""
    crit = cfg.criterion
    n = mean.shape[0]
    p_int = np.zeros(n)
    p_fail = np.zeros(n)
    for _ in range(K):
        Z = rng.standard_normal((n, len(s_pc))) * s_pc[None, :] * scale[:, None]
        Y = np.maximum(mean + Z @ V, 0.0)
        if cfg.interest is not None:
            p_int += np.asarray(cfg.interest(Y, ds.axis), bool).ravel()
        p_fail += np.asarray(crit.stats(Y, mean)["outside_mean"], bool)
    return p_int / K, p_fail / K


def campaign(key, kind, alpha, seed=0):
    ds, cfg, _ = build(ROWS[key], seed, {})
    eng, pred, crit = cfg.predictor.engine, cfg.predictor, cfg.criterion
    names = [c.name for c in cfg.certificates]
    P, lv, cand = ds.points, ds.levels, ds.candidate
    truth = ds.oracle.truth(np.arange(ds.n))
    interesting = np.asarray(cfg.interest(truth, ds.axis), bool).ravel() if cfg.interest else np.zeros(ds.n, bool)
    measured = (lv <= cfg.seed_level) & cand
    action = np.where(measured, "seed", "").astype(object)
    p_stated = np.full(ds.n, np.nan)
    wrong = np.zeros(ds.n, bool)
    rng = np.random.default_rng(1234)
    kappas = {}
    for L in range(cfg.seed_level + 1, int(lv.max()) + 1):
        idx = np.flatnonzero((lv == L) & cand)
        if len(idx) == 0:
            continue
        Ps, Ys = P[measured], truth[measured]
        mean = pred.predict(Ps, Ys, P[idx])
        su = eng.std(P[idx])
        V, s_pc = pc_basis(Ys)
        if kind == "latent":
            scale = su
        else:
            scale = np.sqrt(su ** 2 + eng._nu)
            if kind == "loo":
                kap = loo_kappa(eng, Ys, Ys.std(0))
                kappas[L] = kap
                scale = kap * scale
        p_int, p_fail = stated_probabilities(cfg, ds, mean, scale, V, s_pc, rng)
        cover_A = ("interest" in names) & (p_int <= alpha)
        cover_B = ("interp" in names) & (p_fail <= alpha)
        skip = cover_A | cover_B
        true_fail = np.asarray(crit.stats(truth[idx], mean)["outside_mean"], bool)
        for j, gi in enumerate(idx):
            if skip[j]:
                action[gi] = ("not_interesting+interpolable" if cover_A[j] and cover_B[j]
                              else "not_interesting" if cover_A[j] else "interpolable")
                pa = p_int[j] if cover_A[j] else 0.0
                pb = p_fail[j] if cover_B[j] else 0.0
                p_stated[gi] = 1 - (1 - pa) * (1 - pb)
                wrong[gi] = (cover_A[j] and interesting[gi]) or (cover_B[j] and true_fail[j])
            else:
                action[gi] = "measured"
                measured[gi] = True
    c = cand & (lv > cfg.seed_level)
    sk = c & np.isin(action, ["not_interesting", "interpolable", "not_interesting+interpolable"])
    per_level = {int(L): dict(n=int(((lv == L) & cand).sum()),
                              wrong=int((wrong & (lv == L) & cand).sum()),
                              stated=float(np.nansum(p_stated[(lv == L) & cand & sk])))
                 for L in range(cfg.seed_level + 1, int(lv.max()) + 1)}
    return dict(dataset=key, kind=kind, alpha=alpha, n_cert=int(c.sum()), n_total=int(cand.sum()),
                measured=int((measured & cand).sum()), skipped=int(sk.sum()),
                wrong=int((wrong & c).sum()), stated=float(np.nansum(p_stated[sk])),
                wrong_rate=float((wrong & c).sum() / c.sum()), stated_rate=float(np.nansum(p_stated[sk]) / c.sum()),
                per_level=per_level, kappa=kappas), dict(action=action[cand].astype(str), wrong=wrong[cand],
                                                          p_stated=p_stated[cand])


def main():
    keys = [k for k in sys.argv[1:] if k in ROWS] or list(ROWS)
    OUT.mkdir(parents=True, exist_ok=True)
    for key in keys:
        rows = []
        for kind in KINDS:
            for a in ALPHAS:
                r, arr = campaign(key, kind, a)
                rows.append(r)
                np.savez_compressed(OUT / f"{key}_{kind}_a{a:.2f}.npz", **arr)
                print(f"{key} {kind:10s} alpha {a:.2f}: measured {r['measured']:5d}/{r['n_total']}, "
                      f"wrong {r['wrong']:4d} ({100 * r['wrong_rate']:.1f} %), stated {r['stated']:.1f} "
                      f"({100 * r['stated_rate']:.1f} %)", flush=True)
        (OUT / f"{key}.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
