"""
Round-2 studies.

    python -m experiments.revision2 recall     # sites of interest protected by a label-conditional bound (synthetic)
    python -m experiments.revision2 drift      # slow swelling of the synthetic sample during the campaign
    python -m experiments.revision2 costgrid   # cost against calibration size and confidence (IR)
    python -m experiments.revision2 finalmap   # final-map labels of the record's campaigns, for the audit
    python -m experiments.revision2 audit      # held-out audit after the last level (all three maps)
    python -m experiments.revision2 gpacq      # GP acquisition campaign on NaCl, with the audit on top

Results go to results/revision2/. Every study is resumable by campaign.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import hypergeom

from accountable import make_policy
from accountable.campaign import run_campaign
from accountable.dataset import Oracle
from accountable.policies import RecallNestedPathPolicy
from experiments.record import OUT as REC, REASONS, build
from experiments.record_picked import worst_case_tail

OUT = Path("results/revision2")
ROWS = {"ir": "ir_nested_watson", "nacl": "nacl_fwhm_nested_watson", "syn": "syn_env_nested_watson"}
EPS = {"ir": 0.10, "nacl": 0.20, "syn": 0.10}
NOT_INT = ("not_interesting", "not_interesting+interpolable")


def _resume(f):
    return {json.loads(l)["seed"] for l in f.open()} if f.exists() else set()


def _levels(r, eps):
    out = []
    for lv in r.per_level:
        if lv.get("empty"):
            continue
        name = next(iter(lv["certificates"]))
        k = lv["certificates"][name]["k"]
        out.append(dict(L=lv["L"], n_level=lv["n_level"], n_cal=lv["n_cal"], k=k,
                        picked=worst_case_tail(k, eps, lv["n_cal"], lv["n_level"], "hypergeometric"),
                        E_rate=lv["level"]["E_rate"], rem_rate=lv["rem"]["E_rate"],
                        exceeded=bool(lv["level"]["E_rate"] > eps + 1e-12),
                        measured_rem=lv["n_measured_rem"], notes=lv.get("policy_notes", {})))
    return out


def _recall_rates(ds, r, lv_min):
    R = np.asarray(r.reason).astype(str)
    lost = np.isin(R, NOT_INT) & r.interesting
    out = {}
    for L in range(lv_min, int(ds.levels.max()) + 1):
        lvl = (ds.levels == L) & ds.candidate
        ni = int((r.interesting & lvl).sum())
        out[int(L)] = dict(n_interest=ni, lost=int((lost & lvl).sum()),
                           rate=float((lost & lvl).sum() / ni) if ni else None)
    return out


# ------------------------------------------------------------------ recall
def recall(n=250, eps_r=0.20, conf_r=0.80, key="syn"):
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / f"recall_{key}.jsonl"
    done = _resume(f)
    row, eps = ROWS[key], EPS[key]
    with f.open("a") as fh:
        for s in range(n):
            if s in done:
                continue
            ds, cfg, _ = build(row, s, {})
            cfg.policy = RecallNestedPathPolicy(budget=eps, confidence=cfg.policy.confidence,
                                                recall_budget=eps_r, recall_confidence=conf_r)
            t0 = time.time()
            r = run_campaign(ds, cfg)
            rec = dict(seed=s, measured=int(r.measured[ds.candidate].sum()), levels=_levels(r, eps),
                       recall=_recall_rates(ds, r, cfg.seed_level + 1), eps_r=eps_r, conf_r=conf_r,
                       seconds=time.time() - t0)
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            if s % 25 == 0:
                print("recall", s, rec["measured"], flush=True)


# ------------------------------------------------------------------ drift
class SwellingOracle(Oracle):
    """The sample swells during the campaign: a measurement at clock t returns the pristine profile with q
    scaled by 1 + rate * t (every peak moves to lower q), t counting the sites measured before it. Truth is
    the sample as it was when the plan was declared."""

    retrospective = True

    def __init__(self, spectra, q, rate):
        self.spectra = np.asarray(spectra, float)
        self.lq = np.log(np.asarray(q, float))
        self.rate = float(rate)
        self.t = 0
        self.t_of = {}

    def shifted(self, i, t):
        s = 1.0 + self.rate * t
        return np.interp(self.lq + np.log(s), self.lq, self.spectra[i])

    def measure(self, idx):
        out = []
        for i in np.asarray(idx, int):
            self.t_of[int(i)] = self.t
            out.append(self.shifted(int(i), self.t))
            self.t += 1
        return np.array(out).reshape(len(out), -1)

    def truth(self, idx):
        return self.spectra[np.asarray(idx, int)]


def drift(n=50, swell=(0.0, 0.05, 0.10, 0.20), n_check=5, cost=None):
    """swell: total change of the q scale over the mean cost of the plan (`cost` sites, from the record)."""
    OUT.mkdir(parents=True, exist_ok=True)
    row = ROWS["syn"]
    if cost is None:
        import gzip
        cost = float(np.mean([json.loads(l)["summary"]["n_measured"] for l in gzip.open(REC / row / "runs.jsonl.gz", "rt")]))
    for sw in swell:
        f = OUT / f"drift_syn_{sw:.2f}.jsonl"
        done = _resume(f)
        with f.open("a") as fh:
            for s in range(n):
                if s in done:
                    continue
                ds, cfg, _ = build(row, s, {})
                orc = SwellingOracle(ds.oracle.spectra, ds.axis, sw / cost)
                ds.oracle = orc
                cfg.cal_from_measurement = True
                t0 = time.time()
                r = run_campaign(ds, cfg)
                lv = _levels(r, EPS["syn"])
                # Re-measure n_check seed sites at the end of every level and compare with their first
                # measurement under the claim's metric.
                seeds = np.flatnonzero(r.is_seed)
                chk = np.random.default_rng(5000 + s).choice(seeds, size=n_check, replace=False)
                first = np.array([orc.shifted(int(i), orc.t_of[int(i)]) for i in chk])
                clock = int(r.is_seed.sum())
                for x in lv:
                    clock += x["n_cal"] + x["measured_rem"]
                    again = np.array([orc.shifted(int(i), clock) for i in chk])
                    fail = np.asarray(cfg.criterion.stats(again, first)["outside_mean"], bool)
                    x["clock"] = clock
                    x["check_fail"] = int(fail.sum())
                # Measured sites of the certified levels whose recorded measurement lies outside tolerance of
                # the sample as it was when the plan was declared.
                cert = ds.candidate & (ds.levels > cfg.seed_level)
                mi = np.flatnonzero(r.measured & cert)
                got = np.array([orc.shifted(int(i), orc.t_of[int(i)]) for i in mi])
                bad = np.asarray(cfg.criterion.stats(orc.spectra[mi], got)["outside_mean"], bool)
                R = np.asarray(r.reason).astype(str)
                A = np.isin(R, NOT_INT); B = np.isin(R, ("interpolable", "not_interesting+interpolable"))
                W = r.skipped & cert & ((A & r.interesting) | (B & r.fail_prior))
                rec = dict(seed=s, swell=sw, cost=cost, measured=int(r.measured[ds.candidate].sum()), levels=lv,
                           n_cert=int(cert.sum()), measured_off=int(bad.sum()), wrong_skips=int(W.sum()),
                           seconds=time.time() - t0)
                fh.write(json.dumps(rec) + "\n"); fh.flush()
                if s % 10 == 0:
                    print("drift", sw, s, rec["measured"], [x["exceeded"] for x in lv],
                          [x["check_fail"] for x in lv], flush=True)


# ------------------------------------------------------------------ cost grid
def costgrid(n=100, ms=(20, 40, 80), confs=(0.80, 0.90, 0.95)):
    OUT.mkdir(parents=True, exist_ok=True)
    row, eps = ROWS["ir"], EPS["ir"]
    for m in ms:
        for c in confs:
            f = OUT / f"cost_ir_m{m}_c{c:.2f}.jsonl"
            done = _resume(f)
            with f.open("a") as fh:
                for s in range(n):
                    if s in done:
                        continue
                    ds, cfg, _ = build(row, s, {})
                    cfg.cal_size = m
                    cfg.policy = make_policy("nested_path", budget=eps, confidence=c)
                    r = run_campaign(ds, cfg)
                    rec = dict(seed=s, m=m, c=c, measured=int(r.measured[ds.candidate].sum()),
                               levels=_levels(r, eps))
                    fh.write(json.dumps(rec) + "\n"); fh.flush()
            print("cost", m, c, flush=True)


# ------------------------------------------------------------------ final map of the record, then the audit
def finalmap():
    """Per campaign of the record: the skipped sites whose prediction from all measured sites fails the
    claim's metric (the final map), on the candidate sites in the order of the record."""
    OUT.mkdir(parents=True, exist_ok=True)
    for key, row in ROWS.items():
        f = OUT / f"finalmap_{key}.npz"
        if f.exists():
            continue
        z = np.load(REC / row / "sites.npz")
        site = z["site_index"]
        wrong = np.zeros(z["measured"].shape, bool)
        for j, s in enumerate(z["seeds"]):
            ds, cfg, _ = build(row, int(s), {})
            truth = ds.oracle.truth(np.arange(ds.n))
            meas = np.zeros(ds.n, bool); meas[site[z["measured"][j].astype(bool)]] = True
            qg = site[z["skipped"][j].astype(bool)]
            mean = cfg.predictor.predict(ds.points[meas], truth[meas], ds.points[qg])
            fail = np.asarray(cfg.criterion.stats(truth[qg], mean)["outside_mean"], bool)
            wrong[j, np.flatnonzero(z["skipped"][j].astype(bool))] = fail
        np.savez_compressed(f, wrong=wrong, seeds=z["seeds"])
        print("finalmap", key, wrong.sum(1).mean(), flush=True)


def upper_count(N, n, f, delta):
    """Exact upper confidence limit on the number K of bad items among N, from f bad in a uniform sample of
    n without replacement: the largest K with P(Hyp(N, K, n) <= f) > delta."""
    if n == 0:
        return N
    K = np.arange(f, N - (n - f) + 1)
    ok = hypergeom.cdf(f, N, K, n) > delta
    return int(K[ok].max()) if ok.any() else int(f)


def audit(sizes=(50, 100, 200), confs=(0.80, 0.95), reps=200, keys=None):
    """The audit is drawn after the last level, uniformly from the skipped sites of the certified levels,
    measured, and used for nothing else. It bounds the number of skipped sites the final map gets wrong,
    hence the share of the certified-level sites, with the stated confidence. Coverage is over campaigns
    and over `reps` audit draws per campaign."""
    res = json.loads((OUT / "audit.json").read_text()) if (OUT / "audit.json").exists() else {}
    for key, row in ROWS.items():
        if keys and key not in keys:
            continue
        z = np.load(REC / row / "sites.npz")
        W = np.load(OUT / f"finalmap_{key}.npz")["wrong"]
        lv = z["levels"]; cert = lv > 2
        S = z["skipped"].astype(bool) & cert
        Rn = np.array(REASONS)[z["reason"]]
        n_cert = int(cert.sum())
        out = dict(n_cert=n_cert, true_share=float((W & S).sum(1).mean() / n_cert))
        for n_a in sizes:
            for c in confs:
                cov, bnd = [], []
                for j in range(len(z["seeds"])):
                    pop = np.flatnonzero(S[j]); N = len(pop); K = int((W[j] & S[j]).sum())
                    rng = np.random.default_rng(3000 + j)
                    for _ in range(reps):
                        pick = rng.choice(pop, size=min(n_a, N), replace=False)
                        u = upper_count(N, len(pick), int(W[j, pick].sum()), 1 - c)
                        cov.append(K <= u); bnd.append(u / n_cert)
                out[f"n{n_a}_c{c:.2f}"] = dict(coverage=float(np.mean(cov)), bound_mean=float(np.mean(bnd)),
                                               bound_sd=float(np.std(bnd)))
        if key == "syn" and ROWS["syn"].startswith("syn_peak_2cert"):
            # Stratified by the claim of the skip, half the audit in each stratum, Bonferroni over the two.
            # The no-interest stratum also bounds the share of the sites of interest skipped as holding none.
            I = z["interesting"].astype(bool)
            A = S & np.isin(Rn, NOT_INT)
            B = S & ~np.isin(Rn, NOT_INT)
            for c in confs:
                cov_m, bnd_m, cov_r, bnd_r, true_r = [], [], [], [], []
                for j in range(len(z["seeds"])):
                    rng = np.random.default_rng(4000 + j)
                    i_meas = int((I[j] & z["measured"][j].astype(bool) & cert).sum())
                    KA_int = int((I[j] & A[j]).sum())
                    tr = KA_int / int((I[j] & cert).sum())
                    for _ in range(reps):
                        u_tot, Kt = 0, 0
                        for St in (A[j], B[j]):
                            pop = np.flatnonzero(St); N = len(pop)
                            pick = rng.choice(pop, size=min(50, N), replace=False)
                            u_tot += upper_count(N, len(pick), int(W[j, pick].sum()), (1 - c) / 2)
                            Kt += int((W[j] & St).sum())
                        cov_m.append(Kt <= u_tot); bnd_m.append(u_tot / n_cert)
                        pop = np.flatnonzero(A[j]); N = len(pop)
                        pick = rng.choice(pop, size=min(100, N), replace=False)
                        uA = upper_count(N, len(pick), int(I[j, pick].sum()), 1 - c)
                        br = uA / (i_meas + uA) if (i_meas + uA) else 0.0
                        cov_r.append(tr <= br + 1e-12); bnd_r.append(br); true_r.append(tr)
                out[f"strat_c{c:.2f}"] = dict(coverage=float(np.mean(cov_m)), bound_mean=float(np.mean(bnd_m)))
                out[f"interest_lost_c{c:.2f}"] = dict(coverage=float(np.mean(cov_r)), bound_mean=float(np.mean(bnd_r)),
                                                      true_mean=float(np.mean(true_r)))
        out["reps"] = reps
        out.setdefault("reps", reps)
        res[key] = out
        print(key, json.dumps(out), flush=True)
        (OUT / "audit.json").write_text(json.dumps(res, indent=1))


# ------------------------------------------------------------------ GP acquisition campaign on NaCl
def gpacq(batch=25, checkpoints=(614, 694, 800), n_a=100, conf=0.80, reps=2000):
    """Acquisition by the GP's own probability that a skip would be wrong (presence and log-width GPs as
    in SI 7, predictive standard deviation), batches of `batch` sites, from the seed sites. At each
    checkpoint: the map's true share of wrong sites, the GP's stated share (latent and predictive), and the
    audit bound from n_a uniform held-out unmeasured sites."""
    from scipy.stats import norm
    from experiments.uncertified_gp import TOL, fit, predict, site_truth
    z, xy, w, p = site_truth()
    lv = np.asarray(z["levels"])
    cert = lv >= 3
    measured = lv <= 2
    rows = []

    def state(measured):
        U = np.flatnonzero(~measured)
        gp_, mp, sp = fit(xy[measured], p[measured].astype(float))
        ph, _ = predict(gp_, mp, sp, xy[U], latent=False)
        ph = np.clip(ph, 0.0, 1.0)
        ok = measured & p & np.isfinite(w)
        gw, mw, sw = fit(xy[ok], np.log(w[ok]))
        out = {}
        for latent in (False, True):
            lm, ls = predict(gw, mw, sw, xy[U], latent=latent)
            wh = np.exp(lm)
            lo, hi = np.log(np.maximum(wh - TOL, 1e-12)), np.log(wh + TOL)
            p_in = np.where(ls > 0, norm.cdf((hi - lm) / np.maximum(ls, 1e-12)) - norm.cdf((lo - lm) / np.maximum(ls, 1e-12)), 1.0)
            line = ph >= 0.5
            q = np.where(line, 1.0 - ph * p_in, ph)
            wrong = np.where(line, (~p[U]) | (np.abs(wh - np.nan_to_num(w[U], nan=1e9)) > TOL), p[U])
            out["latent" if latent else "predictive"] = (U, q, wrong.astype(bool))
        return out

    for cp in checkpoints:
        while measured.sum() < cp:
            U, q, _ = state(measured)["predictive"]
            take = min(batch, cp - int(measured.sum()))
            measured[U[np.argsort(-q)[:take]]] = True
            print("gpacq measured", int(measured.sum()), flush=True)
        st = state(measured)
        U, q, wrong = st["predictive"]
        _, q_lat, _ = st["latent"]
        n_cert = int(cert.sum())
        K = int(wrong.sum()); N = len(U)
        rng = np.random.default_rng(7)
        bnd, cov = [], []
        for _ in range(reps):
            pick = rng.choice(N, size=n_a, replace=False)
            u = upper_count(N, n_a, int(wrong[pick].sum()), 1 - conf)
            bnd.append(u / n_cert); cov.append(K <= u)
        rows.append(dict(measured=int(measured.sum()), true_share=K / n_cert,
                         stated_predictive=float(q.sum() / n_cert), stated_latent=float(q_lat.sum() / n_cert),
                         audit_n=n_a, audit_conf=conf, audit_bound_mean=float(np.mean(bnd)),
                         audit_bound_q=[float(x) for x in np.quantile(bnd, [0.1, 0.5, 0.9])],
                         audit_coverage=float(np.mean(cov))))
        print(rows[-1], flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gpacq_nacl.json").write_text(json.dumps(rows, indent=1))


# ------------------------------------------------------------------ GP campaign that stops on its own stated rate
def gpstop(n=30, eps=0.20, batch=25, frac=0.8, n_a=100, conf=0.80, start=0):
    """The GP acquisition campaign of gpacq, told to meet a budget: after every batch it states its own
    share of certified-level sites predicted wrongly (sum of per-site wrong-skip probabilities, latent or
    predictive standard deviation) and stops once that statement is at most eps. Acquisition uses the
    predictive probability; each batch is chosen among a random share `frac` of the unmeasured sites, so
    runs differ. The trajectory is followed until the predictive statement meets eps; the stopping point of
    the latent rule is read off the same trajectory."""
    from scipy.stats import norm
    from experiments.uncertified_gp import TOL, fit, predict, site_truth
    z, xy, w, p = site_truth()
    lv = np.asarray(z["levels"])
    n_cert = int((lv >= 3).sum())
    f = OUT / "gpstop_nacl.jsonl"
    done = _resume(f)
    for s in range(start, start + n):
        if s in done:
            continue
        rng = np.random.default_rng(9000 + s)
        measured = lv <= 2
        traj = []
        while True:
            U = np.flatnonzero(~measured)
            gp_, mp, sp = fit(xy[measured], p[measured].astype(float))
            ph, _ = predict(gp_, mp, sp, xy[U], latent=False)
            ph = np.clip(ph, 0.0, 1.0)
            ok = measured & p & np.isfinite(w)
            gw, mw, sw = fit(xy[ok], np.log(w[ok]))
            row = dict(measured=int(measured.sum()))
            qs = {}
            for latent in (False, True):
                lm, ls = predict(gw, mw, sw, xy[U], latent=latent)
                wh = np.exp(lm)
                lo, hi = np.log(np.maximum(wh - TOL, 1e-12)), np.log(wh + TOL)
                sd = np.maximum(ls, 1e-12)
                p_in = np.where(ls > 0, norm.cdf((hi - lm) / sd) - norm.cdf((lo - lm) / sd), 1.0)
                line = ph >= 0.5
                q = np.where(line, 1.0 - ph * p_in, ph)
                qs["latent" if latent else "predictive"] = q
                if not latent:
                    wrong = np.where(line, (~p[U]) | (np.abs(wh - np.nan_to_num(w[U], nan=1e9)) > TOL), p[U]).astype(bool)
            K, N = int(wrong.sum()), len(U)
            row.update(true_share=K / n_cert, stated_predictive=float(qs["predictive"].sum() / n_cert),
                       stated_latent=float(qs["latent"].sum() / n_cert))
            # an audit of n_a unmeasured sites at this point: share of draws whose bound meets eps, and coverage
            ok_n, cov_n = 0, 0
            for _ in range(200):
                pick = rng.choice(N, size=n_a, replace=False)
                u = upper_count(N, n_a, int(wrong[pick].sum()), 1 - conf)
                ok_n += (u / n_cert) <= eps; cov_n += K <= u
            row.update(audit_meets=ok_n / 200, audit_coverage=cov_n / 200)
            traj.append(row)
            if row["stated_predictive"] <= eps or N <= batch:
                break
            cand = rng.choice(len(U), size=max(batch, int(frac * len(U))), replace=False)
            take = cand[np.argsort(-qs["predictive"][cand])[:batch]]
            measured[U[take]] = True
        stops = {}
        for rule in ("latent", "predictive"):
            hit = next((r for r in traj if r[f"stated_{rule}"] <= eps), traj[-1])
            stops[rule] = dict(measured=hit["measured"], true_share=hit["true_share"], stated=hit[f"stated_{rule}"],
                               over=bool(hit["true_share"] > eps), audit_meets=hit["audit_meets"])
        with f.open("a") as fh:
            fh.write(json.dumps(dict(seed=s, eps=eps, stops=stops, trajectory=traj)) + "\n")
        print("gpstop", s, {k: (v["measured"], round(v["true_share"], 3)) for k, v in stops.items()}, flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "gpstop":
        gpstop(n=int(sys.argv[2]) if len(sys.argv) > 2 else 30, start=int(sys.argv[3]) if len(sys.argv) > 3 else 0)
    elif sys.argv[1] == "recall" and len(sys.argv) > 2:
        recall(key=sys.argv[2])
    elif sys.argv[1] == "audit" and len(sys.argv) > 2:
        audit(reps=int(sys.argv[3]) if len(sys.argv) > 3 else 200, keys=sys.argv[2].split(","))
    else:
        {"recall": recall, "drift": drift, "costgrid": costgrid, "finalmap": finalmap, "audit": audit,
         "gpacq": gpacq}[sys.argv[1]]()
