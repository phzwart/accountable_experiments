"""
An uncertified campaign on the NaCl (200)-width map, for comparison with the certified campaign of Fig. 1.
Same hierarchical design and seed sites. At each level from 3 on, a GP is fitted to every site measured so
far (log width where the line is present; the 0/1 presence indicator on all sites; RBF plus white noise,
maximum likelihood). A site is skipped as having no line when the presence GP is below p_lo, and skipped as
predictable when the presence GP exceeds p_hi and the z-interval of the width lies within the tolerance
(0.02 nm^-1); every other site is measured. The width interval uses either the latent standard deviation
or the predictive one (latent plus noise). Nothing is calibrated, so no error rate is stated.

Wrong skips are counted exactly as for the certified campaign: a no-line skip is wrong where the line is
present; a predictable skip is wrong where presence disagrees or the width misses by more than the tolerance.

    python -m experiments.uncertified_gp
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C, WhiteKernel

from experiments.record import OUT as REC, REASONS, build

ROW, TOL = "nacl_fwhm_nested_watson", 0.02
OUT = Path("results/hook/uncertified.json")


def site_truth():
    import sys
    sys.path.insert(0, "manuscript/figures")
    from fig_datasets import nacl_fwhm
    z = np.load(REC / ROW / "sites.npz")
    ds, _, _ = build(ROW, 44, {})
    xy = np.asarray(ds.meta["xy_mm"], float)[z["site_index"]]
    img, pres, (xs, ys), _, _ = nacl_fwhm()
    ix = np.searchsorted(xs, xy[:, 0].round(4).clip(xs[0], xs[-1]))
    iy = np.searchsorted(ys, xy[:, 1].round(4).clip(ys[0], ys[-1]))
    return z, xy, img[iy, ix], pres[iy, ix]


def fit(X, y, noise=True):
    k = C(1.0) * RBF(1.0, (0.05, 20.0)) + WhiteKernel(0.1, (1e-4, 10.0))
    mu, sd = y.mean(), y.std()
    g = GaussianProcessRegressor(k, alpha=1e-8, n_restarts_optimizer=2, random_state=0).fit(X, (y - mu) / sd)
    return g, mu, sd


def predict(g, mu, sd, Xq, latent):
    m, s = g.predict(Xq, return_std=True)
    if latent:  # remove the fitted white-noise variance from the predictive variance
        nv = g.kernel_.k2.noise_level
        s = np.sqrt(np.maximum(s ** 2 - nv, 0.0))
    return m * sd + mu, s * sd


def campaign(xy, w, p, lv, z, latent, p_lo=0.1, p_hi=0.9):
    measured = lv <= 2
    action = np.array(["seed" if m else "" for m in measured], dtype=object)
    wrong = np.zeros(len(lv), bool)
    implied = np.zeros(len(lv))  # the model's own probability that the skip is wrong
    for L in range(3, int(lv.max()) + 1):
        idx = np.flatnonzero(lv == L)
        M = measured
        gp_, mp, sp = fit(xy[M], p[M].astype(float))
        ph, _ = predict(gp_, mp, sp, xy[idx], latent=False)
        ok = M & p & np.isfinite(w)
        gw, mw, sw = fit(xy[ok], np.log(w[ok]))
        lm, ls = predict(gw, mw, sw, xy[idx], latent=latent)
        wh = np.exp(lm)
        half = np.maximum(np.exp(lm + z * ls) - wh, wh - np.exp(lm - z * ls))
        no_line = ph < p_lo
        pred = (ph > p_hi) & (half <= TOL)
        for j, gi in enumerate(idx):
            pc = float(np.clip(ph[j], 0.0, 1.0))
            if no_line[j]:
                action[gi] = "no_line"
                wrong[gi] = p[gi]
                implied[gi] = pc
            elif pred[j]:
                action[gi] = "predictable"
                wrong[gi] = (not p[gi]) or (abs(wh[j] - w[gi]) > TOL)
                lo, hi = np.log(max(wh[j] - TOL, 1e-12)), np.log(wh[j] + TOL)
                p_in = norm.cdf((hi - lm[j]) / ls[j]) - norm.cdf((lo - lm[j]) / ls[j]) if ls[j] > 0 else 1.0
                implied[gi] = 1.0 - pc * p_in
            else:
                action[gi] = "measured"
                measured[gi] = True
    return measured.copy(), action, wrong, implied


def main():
    z, xy, w, p = site_truth()
    lv = np.asarray(z["levels"])
    cert = lv >= 3
    rows = []
    for latent in (True, False):
        for zz in (1.0, 1.64, 1.96, 2.58):
            m, a, wr, imp = campaign(xy, w, p, lv, zz, latent)
            per = {int(L): float(wr[lv == L].mean()) for L in range(3, int(lv.max()) + 1)}
            rows.append(dict(sd="latent" if latent else "predictive", z=zz, nominal=float(2 * (1 - __import__("scipy").stats.norm.cdf(zz))),
                             measured=int(m.sum()), wrong_rate=float(wr[cert].mean()), stated_rate=float(imp[cert].sum() / cert.sum()),
                             stated_per_level={int(L): float(imp[lv == L].sum() / (lv == L).sum()) for L in range(3, int(lv.max()) + 1)},
                             n_skip_pred=int((a == "predictable").sum()), n_skip_noline=int((a == "no_line").sum()),
                             wrong_pred=float(wr[a == "predictable"].mean()) if (a == "predictable").any() else None,
                             per_level=per))
            print(rows[-1])
            np.savez_compressed(OUT.parent / f"uncertified_{rows[-1]['sd']}_z{zz:.2f}.npz", measured=m,
                                action=a.astype(str), wrong=wr, implied=imp)
    # the certified campaigns, same metric
    S = z["skipped"].astype(bool)
    R = np.array(REASONS)[z["reason"]]
    A = np.isin(R, ["not_interesting", "not_interesting+interpolable"])
    B = np.isin(R, ["interpolable", "not_interesting+interpolable"])
    W = S & ((A & z["interesting"].astype(bool)) | (B & z["fail_prior"].astype(bool)))
    certified = dict(measured=z["measured"].sum(1).tolist(), wrong_rate=W[:, cert].mean(1).tolist(),
                     seeds=z["seeds"].tolist())
    OUT.write_text(json.dumps(dict(uncertified=rows, certified=certified), indent=1))
    print("certified: measured mean", np.mean(certified["measured"]), "wrong rate mean",
          np.mean(certified["wrong_rate"]), "max", np.max(certified["wrong_rate"]))


if __name__ == "__main__":
    main()
