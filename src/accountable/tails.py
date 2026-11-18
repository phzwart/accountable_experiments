"""
Binomial and hypergeometric tails behind the allowed failure count k.

k is the largest integer with P(Bin(m, eps) <= k) <= delta. The exact
finite-population tail is hypergeometric on a level of N sites with
floor(eps N) + 1 bad sites. ``allowed_k`` returns the binomial k and, when
the level size is known, refuses a k that the hypergeometric tail would
not allow.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import beta, binom, hypergeom


def allowed_k_binomial(eps: float, m: int, delta: float) -> int:
    """Largest k with P(Bin(m, eps) <= k) <= delta; -1 if none."""
    m = int(m)
    if m < 1:
        return -1
    allowed = -1
    for k in range(0, m):
        # P(Beta(k+1, m-k) > eps) equals P(Bin(m, eps) <= k).
        tail = float(beta.sf(float(eps), k + 1, m - k))
        if tail <= float(delta) + 1e-15:
            allowed = k
        else:
            break
    return allowed


def allowed_k_hypergeometric(eps: float, m: int, delta: float, N: int) -> int:
    """Largest k with P(Hyp(N, floor(eps N)+1, m) <= k) <= delta; -1 if none."""
    m, N = int(m), int(N)
    if m < 1 or N < m:
        return -1
    K = min(int(np.floor(float(eps) * N)) + 1, N)
    allowed = -1
    for k in range(0, m):
        if float(hypergeom.cdf(k, N, K, m)) <= float(delta) + 1e-15:
            allowed = k
        else:
            break
    return allowed


@dataclass
class TailDecision:
    k: int
    k_binomial: int
    k_hypergeometric: int | None
    eps: float
    m: int
    delta: float
    N: int | None
    tail: str

    def as_dict(self):
        return dict(self.__dict__)


def allowed_k(eps: float, m: int, delta: float, N: int | None = None,
              tail: str = "binomial") -> TailDecision:
    """
    Allowed calibration failures for a joint budget ``eps`` at failure
    probability ``delta``. ``tail="binomial"`` (default) uses the binomial
    and, when N is given, checks that it is not looser than the exact
    hypergeometric tail. ``tail="hypergeometric"`` uses the exact tail.
    """
    kb = allowed_k_binomial(eps, m, delta)
    kh = allowed_k_hypergeometric(eps, m, delta, N) if N is not None and N >= m else None
    if tail == "binomial":
        if kh is not None and kb > kh:
            raise RuntimeError(
                f"binomial k={kb} exceeds the hypergeometric k={kh} "
                f"(eps={eps}, m={m}, delta={delta}, N={N}); use tail='hypergeometric'"
            )
        k = kb
    elif tail == "hypergeometric":
        if kh is None:
            raise ValueError("the hypergeometric tail needs the level size N >= m")
        k = kh
    else:
        raise ValueError(f"unknown tail {tail!r}")
    return TailDecision(k=k, k_binomial=kb, k_hypergeometric=kh, eps=float(eps),
                        m=int(m), delta=float(delta), N=N, tail=tail)


def clopper_pearson_upper(failures: int, m: int, confidence: float) -> float:
    """One-sided Clopper–Pearson upper bound on a binomial rate."""
    failures, m = int(failures), int(m)
    if m <= 0:
        return float("nan")
    if failures >= m:
        return 1.0
    failures = max(failures, 0)
    return float(beta.ppf(float(confidence), failures + 1, m - failures))


def clopper_pearson(k: int, n: int, level: float = 0.95):
    """Central Clopper–Pearson interval."""
    k, n = int(k), int(n)
    if n <= 0:
        return float("nan"), float("nan")
    a = 1.0 - float(level)
    lo = 0.0 if k <= 0 else float(beta.ppf(a / 2.0, k, n - k + 1))
    hi = 1.0 if k >= n else float(beta.ppf(1.0 - a / 2.0, k + 1, n - k))
    return lo, hi


def eps_min(confidence: float, m: int) -> float:
    """Smallest joint budget that zero calibration failures can certify."""
    return float(1.0 - (1.0 - float(confidence)) ** (1.0 / int(m))) if m > 0 else float("nan")


def expected_random_skip(k: int, m: int, f: int) -> float:
    """Expected skip fraction of a uniform score at (k, m, f)."""
    if m <= 0 or k < 0:
        return 0.0
    if f <= k:
        return 1.0
    return (1.0 / m) * (k + (k + 1) * (m - f) / (f + 1))


def binomial_lower_tail(k: int, m: int, p: float) -> float:
    return float(binom.cdf(int(k), int(m), float(p)))
