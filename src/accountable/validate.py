"""
Monte Carlo acceptance check for a budget policy's stated guarantees.

A new policy is accepted for claims once every guarantee it states holds
on fixed finite populations, where the calibration draw is the only
randomness. For each stated guarantee ``rate <= budget`` at
``confidence``, the frequency of draws in which the population rate
exceeds the budget must not exceed ``1 - confidence`` beyond Monte Carlo
error. Uninformative scores are the hard case: the covered bad rate grows
with the threshold as fast as it can.

See docs/architecture.md, "Adding a scheme".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from .policies import LevelData, Policy


def population(N: int, bad_rates: Dict[str, float], informative: bool = False,
               seed: int = 0) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
    """
    Scores uniform on [0, 1] and bad labels per certificate.

    Uninformative: labels independent of scores at the given rate.
    Informative: bad probability rises linearly with the score, with the
    same mean.
    """
    rng = np.random.default_rng(seed)
    scores, labels = {}, {}
    for name, r in bad_rates.items():
        s = rng.random(N)
        p = 2.0 * r * s if informative else np.full(N, r)
        scores[name] = s
        labels[name] = rng.random(N) < np.clip(p, 0.0, 1.0)
    return scores, labels


def population_rate(event: str, covers: Dict[str, np.ndarray],
                    labels: Dict[str, np.ndarray]) -> Optional[float]:
    """Rate of ``R_E`` (any wrong skip) or ``R_<certificate>`` on the full population."""
    if event == "R_E":
        wrong = np.zeros(len(next(iter(labels.values()))), bool)
        for n, c in covers.items():
            wrong |= c & labels[n]
        return float(wrong.mean())
    if event.startswith("R_") and event[2:] in covers:
        n = event[2:]
        return float((covers[n] & labels[n]).mean())
    return None


@dataclass
class CoverageRow:
    event: str
    budget: float
    confidence: float
    stated: int = 0
    exceeded: int = 0
    tolerance: float = 0.0

    @property
    def allowed(self) -> float:
        return 1.0 - self.confidence

    @property
    def observed(self) -> float:
        return self.exceeded / self.stated if self.stated else float("nan")

    @property
    def passed(self) -> bool:
        return self.stated > 0 and self.observed <= self.allowed + self.tolerance


@dataclass
class CoverageReport:
    policy: dict
    draws: int
    rows: List[CoverageRow] = field(default_factory=list)
    unchecked: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.rows)

    def __str__(self) -> str:
        head = f"{self.policy.get('policy', '?')}: {self.draws} draws"
        if not self.rows:
            return head + ", no guarantee stated"
        lines = [head]
        for r in self.rows:
            lines.append(
                f"  {r.event} <= {r.budget:.3f} at {r.confidence:.3f}: "
                f"exceeded {r.observed:.3f} (allowed {r.allowed:.3f} + {r.tolerance:.3f}) "
                f"{'pass' if r.passed else 'FAIL'}"
            )
        for u in self.unchecked:
            lines.append(f"  unchecked event {u}")
        return "\n".join(lines)


def check_coverage(policy: Policy, scores: Dict[str, np.ndarray], labels: Dict[str, np.ndarray],
                   m: int = 40, draws: int = 2000, seed: int = 0,
                   caps: Optional[Dict[str, float]] = None, z: float = 3.0) -> CoverageReport:
    """
    Run ``policy.decide`` on ``draws`` uniform calibration draws of size
    ``m`` from one fixed population and count, per stated guarantee, the
    draws in which the population rate exceeds the budget.
    """
    N = len(next(iter(scores.values())))
    caps = dict(caps or {})
    rng = np.random.default_rng(seed)
    rows: Dict[tuple, CoverageRow] = {}
    unchecked = set()
    for _ in range(draws):
        cal = np.sort(rng.choice(N, m, replace=False))
        level = LevelData(N, scores, cal, {n: labels[n][cal] for n in scores}, caps=caps)
        d = policy.decide(level)
        for g in d.guarantees:
            rate = population_rate(g.event, d.covers, labels)
            if rate is None:
                unchecked.add(g.event)
                continue
            key = (g.event, round(g.budget, 12), round(g.confidence, 12))
            row = rows.setdefault(key, CoverageRow(g.event, g.budget, g.confidence))
            row.stated += 1
            row.exceeded += rate > g.budget
    for r in rows.values():
        a = r.allowed
        r.tolerance = z * np.sqrt(max(a * (1 - a), 1e-12) / max(r.stated, 1)) + 1e-3
    return CoverageReport(policy.describe(), draws, list(rows.values()), sorted(unchecked))
