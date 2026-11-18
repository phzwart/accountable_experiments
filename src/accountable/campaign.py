"""
The campaign loop.

Seed, then for every finer level: fit and freeze the scores on the
measured set, draw the calibration sample, label it, let the policy set
thresholds, skip covered remainder sites and measure the rest. Every
decision is recorded with its reason. See docs/theory.md.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

import numpy as np

from .criteria import AccuracyCriterion, slice_desc
from .dataset import Dataset
from .policies import LevelData, Policy
from .predictors import Predictor
from .scores import MeasuredSet, Score
from .tails import clopper_pearson_upper, eps_min, expected_random_skip

INTEREST = "interest"
INTERP = "interp"


@dataclass
class Certificate:
    """A certificate: which label it excludes, how sites are ordered, an optional cap."""

    name: str                  # "interest" or "interp"
    score: Score
    cap: Optional[float] = None


@dataclass
class CampaignConfig:
    criterion: AccuracyCriterion
    predictor: Predictor
    certificates: List[Certificate]
    policy: Policy
    interest: Optional[Callable] = None     # truth -> bool, required for an interest certificate
    seed_level: int = 2
    final_level: Optional[int] = None
    cal_size: int = 40
    rng_seed: int = 0
    k_fallback: int = 5
    nn_method: str = "legacy"               # "legacy" reproduces; "watson" is exact Sibson
    map_confidence: Optional[float] = None
    post_labels: bool = True                # remainder labels from the end-of-level measured set
    final_labels: bool = True               # skipped-site labels from the final measured set

    def describe(self) -> dict:
        return dict(
            criterion=self.criterion.label(),
            predictor=getattr(self.predictor, "name", type(self.predictor).__name__),
            certificates=[dict(name=c.name, score=getattr(c.score, "name", ""), cap=c.cap)
                          for c in self.certificates],
            policy=self.policy.describe(),
            nn_method=self.nn_method,
            seed_level=self.seed_level, final_level=self.final_level,
            cal_size=self.cal_size, rng_seed=self.rng_seed,
        )


@dataclass
class CampaignResult:
    dataset: str
    config: dict
    measured: np.ndarray
    is_seed: np.ndarray
    is_cal: np.ndarray
    skipped: np.ndarray
    reason: np.ndarray
    scores: Dict[str, np.ndarray]
    thresholds: Dict[str, np.ndarray]
    interesting: np.ndarray
    fail_prior: np.ndarray
    fail_known: np.ndarray
    per_level: List[dict]
    map_certificates: List[dict]
    final: List[dict] = field(default_factory=list)

    @property
    def n_measured(self) -> int:
        return int(self.measured.sum())

    def summary(self) -> dict:
        rem = sum(r["n_rem"] for r in self.per_level)
        wrong = sum(r["rem"]["E_count"] for r in self.per_level)
        return dict(
            dataset=self.dataset,
            n_design=int(len(self.measured)),
            n_measured=self.n_measured,
            n_seed=int(self.is_seed.sum()),
            n_cal=int(self.is_cal.sum()),
            n_skipped=int(self.skipped.sum()),
            n_remainder=int(rem),
            wrong_skips_prior=int(wrong),
            reasons={str(k): int(v) for k, v in zip(*np.unique(self.reason, return_counts=True))},
        )

    def save(self, out_dir):
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            out / "sites.npz",
            measured=self.measured, is_seed=self.is_seed, is_cal=self.is_cal,
            skipped=self.skipped, reason=self.reason.astype(str),
            interesting=self.interesting, fail_prior=self.fail_prior,
            fail_known=self.fail_known,
            **{f"score_{k}": v for k, v in self.scores.items()},
            **{f"tau_{k}": v for k, v in self.thresholds.items()},
        )
        doc = dict(summary=self.summary(), config=self.config, per_level=self.per_level,
                   map_certificates=self.map_certificates)
        (out / "result.json").write_text(json.dumps(doc, indent=1, default=_json_default))
        return out


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def reason_from_covers(cover: Dict[str, bool]) -> str:
    a = bool(cover.get(INTEREST, False))
    b = bool(cover.get(INTERP, False))
    if a and b:
        return "not_interesting+interpolable"
    if a:
        return "not_interesting"
    if b:
        return "interpolable"
    return "no_certificate"


def _rate(mask, n):
    return float(mask.sum() / n) if n else float("nan")


def run_campaign(ds: Dataset, cfg: CampaignConfig, log: Callable = None) -> CampaignResult:
    log = log or (lambda *_: None)
    crit = cfg.criterion
    names = [c.name for c in cfg.certificates]
    for nm in names:
        if nm not in (INTEREST, INTERP):
            raise ValueError(f"certificate name must be {INTEREST!r} or {INTERP!r}, not {nm!r}")
    if INTEREST in names and cfg.interest is None:
        raise ValueError("an interest certificate needs an interest predicate")

    if getattr(cfg.predictor, "nn_method", cfg.nn_method) != cfg.nn_method:
        cfg.predictor.nn_method = cfg.nn_method
    n = ds.n
    P = ds.points
    levels = ds.levels
    all_idx = np.arange(n)
    # Retrospective truth: the stored spectra. Only measured rows feed decisions.
    truth = ds.oracle.truth(all_idx) if ds.oracle.retrospective else None
    I_known = np.full((n, len(ds.axis)), np.nan)
    desc_all = crit.descriptors(truth) if truth is not None else None

    final_level = int(levels.max()) if cfg.final_level is None else int(cfg.final_level)
    rng = np.random.default_rng(cfg.rng_seed)

    measured = (levels <= cfg.seed_level) & ds.candidate
    I_known[measured] = ds.oracle.measure(np.flatnonzero(measured))
    is_seed = measured.copy()
    is_cal = np.zeros(n, bool)
    skipped = np.zeros(n, bool)
    reason = np.array(["unassigned"] * n, dtype=object)
    reason[measured] = "seed"
    scores = {nm: np.full(n, np.nan) for nm in names}
    taus = {nm: np.full(n, np.nan) for nm in names}
    fail_prior = np.zeros(n, bool)
    fail_known = np.zeros(n, bool)
    if cfg.interest is not None and truth is not None:
        interesting = np.asarray(cfg.interest(truth, ds.axis), bool).ravel()
    else:
        interesting = np.zeros(n, bool)

    def desc_of(mask):
        if desc_all is not None:
            return slice_desc(desc_all, mask)
        return crit.descriptors(I_known[mask])

    def labels(src_mask, query_idx):
        query_idx = np.asarray(query_idx, int)
        if len(query_idx) == 0:
            return np.zeros(0), np.zeros(0, bool)
        I_true = I_known[query_idx] if truth is None else truth[query_idx]
        return cfg.predictor.label(
            P[src_mask], I_known[src_mask], P[query_idx], I_true,
            desc_true=slice_desc(desc_all, query_idx) if desc_all is not None else None,
        )

    per_level, map_rows = [], []
    map_conf = cfg.map_confidence
    if map_conf is None:
        map_conf = getattr(cfg.policy, "confidence", None)

    for L in range(int(cfg.seed_level) + 1, final_level + 1):
        idx = np.flatnonzero((levels == L) & ds.candidate)
        n_level = len(idx)
        if n_level == 0 or int(measured.sum()) < 2:
            per_level.append(dict(L=L, n_level=n_level, n_cal=0, n_rem=0, n_skip=0, empty=True,
                                  rem=dict(E_count=0)))
            continue
        prior = measured.copy()
        ms = MeasuredSet(P[prior], I_known[prior], desc_of(prior), ds.axis, crit,
                         images=ds.images, k_fallback=cfg.k_fallback, nn_method=cfg.nn_method)
        # Fit and freeze every score before the draw.
        for c in cfg.certificates:
            c.score.fit(ms)
        for c in cfg.certificates:
            c.score.bind_level(P[idx])
        level_scores = {c.name: np.asarray(c.score.score(P[idx]), float).ravel()
                        for c in cfg.certificates}
        score_info = {c.name: c.score.fit_info() for c in cfg.certificates
                      if hasattr(c.score, "fit_info")}

        m = max(1, min(int(cfg.cal_size), n_level))
        local = np.sort(rng.choice(n_level, size=m, replace=False))
        cal_idx = idx[local]
        rem_local = np.setdiff1d(np.arange(n_level), local)
        rem_idx = idx[rem_local]

        # Calibration sites are measured; their labels come from the frozen predictor.
        I_known[cal_idx] = ds.oracle.measure(cal_idx)
        s_cal, f_cal = labels(prior, cal_idx)
        bad = {}
        if INTERP in names:
            bad[INTERP] = np.asarray(f_cal, bool)
        if INTEREST in names:
            bad[INTEREST] = np.asarray(cfg.interest(I_known[cal_idx], ds.axis), bool).ravel()

        decision = cfg.policy.decide(LevelData(
            n_level=n_level, scores=level_scores, cal=local, bad=bad,
            caps={c.name: c.cap for c in cfg.certificates},
        ))

        cover_any = np.zeros(n_level, bool)
        for nm in names:
            cover_any |= decision.covers[nm]
        skip_local = np.zeros(n_level, bool)
        skip_local[rem_local] = cover_any[rem_local]

        # Retrospective labels on the remainder, from the frozen predictor.
        if truth is not None and len(rem_idx):
            _, f_rem = labels(prior, rem_idx)
        else:
            f_rem = np.zeros(len(rem_idx), bool)

        is_cal[cal_idx] = True
        measured[cal_idx] = True
        reason[cal_idx] = "calibration"
        fail_prior[cal_idx] = f_cal
        fail_known[cal_idx] = True
        for nm in names:
            scores[nm][idx] = level_scores[nm]
            taus[nm][idx] = decision.thresholds.get(nm, np.nan)
        for j, li in enumerate(rem_local):
            gi = idx[li]
            why = reason_from_covers({nm: decision.covers[nm][li] for nm in names})
            reason[gi] = why
            fail_prior[gi] = bool(f_rem[j]) if len(f_rem) else False
            fail_known[gi] = truth is not None
            if why == "no_certificate":
                measured[gi] = True
            else:
                skipped[gi] = True
        new_meas = rem_idx[~skip_local[rem_local]]
        if len(new_meas):
            I_known[new_meas] = ds.oracle.measure(new_meas)

        # ---- bookkeeping on the level and on the remainder
        fail_lvl = np.zeros(n_level, bool)
        fail_lvl[local] = f_cal
        fail_lvl[rem_local] = f_rem
        int_lvl = interesting[idx]
        bad_lvl = {INTERP: fail_lvl, INTEREST: int_lvl}
        E_lvl = np.zeros(n_level, bool)
        for nm in names:
            E_lvl |= decision.covers[nm] & bad_lvl[nm]
        rem_mask = np.zeros(n_level, bool)
        rem_mask[rem_local] = True
        n_rem = int(rem_mask.sum())
        cert_rows = {}
        for nm in names:
            cov = decision.covers[nm]
            hit = cov & bad_lvl[nm]
            cert_rows[nm] = dict(
                tau=decision.thresholds.get(nm), k=decision.k.get(nm),
                cal_bad=int(bad[nm].sum()), cal_covered=int(cov[local].sum()),
                rem_covered=int((cov & rem_mask).sum()),
                level_joint=_rate(hit, n_level),
                rem_joint=_rate(hit & rem_mask, n_rem),
                rem_conditional=float((hit & rem_mask).sum() / max((cov & rem_mask).sum(), 1)),
                expected_random_skip=expected_random_skip(
                    decision.k.get(nm, -1), m, int(bad[nm].sum())),
                tails=decision.tails.get(nm, decision.tails.get("E")),
                note=decision.notes.get(nm, ""),
            )
        rec = dict(
            L=int(L), n_level=n_level, n_cal=m, n_rem=n_rem,
            n_skip=int(skip_local.sum()), n_measured_rem=int(n_rem - skip_local.sum()),
            cal_overhead=m / n_level, eps_min=eps_min(map_conf, m) if map_conf else None,
            certificates=cert_rows,
            guarantees=[g.as_dict() for g in decision.guarantees],
            policy_notes=decision.notes,
            score_info=score_info,
            level=dict(E_rate=_rate(E_lvl, n_level)),
            rem=dict(
                E_count=int((E_lvl & rem_mask).sum()),
                E_rate=_rate(E_lvl & rem_mask, n_rem),
                skip_bad_both=_rate(skip_local & int_lvl & fail_lvl, n_rem),
            ),
            reasons={r: int(v) for r, v in zip(*np.unique(reason[rem_idx].astype(str), return_counts=True))}
            if n_rem else {},
        )

        if cfg.post_labels and truth is not None and n_rem:
            _, f_post = labels(measured, rem_idx)
            f_post = np.asarray(f_post, bool)
            dmg = np.zeros(n_rem, bool)
            covs = {nm: decision.covers[nm][rem_local] for nm in names}
            if INTEREST in names:
                dmg |= covs[INTEREST] & int_lvl[rem_local]
            if INTERP in names:
                dmg |= covs[INTERP] & f_post
            rec["post"] = dict(E_count=int(dmg.sum()), E_rate=float(dmg.mean()),
                               interp_fail_on_skips=int((skip_local[rem_local] & f_post).sum()))

        if map_conf is not None and int(L) - 1 >= int(cfg.seed_level) and INTERP in names:
            f = int(np.asarray(f_cal, bool).sum())
            inter_cal = interesting[cal_idx]
            m_int = int(inter_cal.sum())
            f_int = int((np.asarray(f_cal, bool) & inter_cal).sum())
            frac = float(fail_lvl.mean()) if truth is not None else float("nan")
            up = clopper_pearson_upper(f, m, map_conf)
            row = dict(map_level=int(L) - 1, from_level=int(L), m=m, failures=f, upper=up,
                       confidence=float(map_conf), level_fail_fraction=frac,
                       covers=bool(up + 1e-12 >= frac) if truth is not None else None,
                       m_interesting=m_int, failures_interesting=f_int,
                       upper_interesting=clopper_pearson_upper(f_int, m_int, map_conf) if m_int else None)
            map_rows.append(row)
            rec["map_certificate"] = row
        per_level.append(rec)
        log(f"L{L}: level {n_level}, cal {m}, skip {rec['n_skip']}, measured so far {int(measured.sum())}")

    final = []
    if cfg.final_labels and truth is not None:
        sk = np.flatnonzero(skipped)
        if len(sk) and int(measured.sum()) >= 2:
            s_f, y_f = labels(measured, sk)
            final = [dict(index=int(i), level=int(levels[i]), s=float(s), outside=bool(y))
                     for i, s, y in zip(sk, s_f, y_f)]

    return CampaignResult(
        dataset=ds.name, config=cfg.describe(), measured=measured, is_seed=is_seed,
        is_cal=is_cal, skipped=skipped, reason=reason, scores=scores, thresholds=taus,
        interesting=interesting, fail_prior=fail_prior, fail_known=fail_known,
        per_level=per_level, map_certificates=map_rows, final=final,
    )
