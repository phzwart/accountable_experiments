"""
What breaks the guarantee: three ways to let the calibration draw inform
the rule that it is supposed to test, against the rule that keeps the
order of operations.

On a fixed level population with informative scores (failure more likely at high score), the calibration
draw is repeated and the frequency with which the shared wrong-skip rate
exceeds its budget is compared with the picked failure probability.

- valid: scores frozen before a uniform draw; quantile path; exact tail.
- refit on calibration labels: after the draw, the score of each failing
  calibration site is raised to the top, then the same labels set the
  threshold (double use of the calibration sample).
- chosen calibration sites: the calibration sample is taken from the
  half of the level the scores rank as least safe, the sites an active
  learner would measure first, instead of uniformly.
- best of five draws: five calibration samples are drawn and the one
  that allows the most skips is kept.
- oracle score: the score sees the true labels but is frozen before the
  draw; the guarantee still holds, since non-anticipation concerns the
  draw and the rule, not what the score knows.

    python -m experiments.anticipation_demo
"""
import json
from pathlib import Path

import numpy as np

from accountable.policies import LevelData, NestedPathPolicy

N, M, EPS, CONF, T = 399, 40, 0.10, 0.75, 4000


def population(seed=7):
    rng = np.random.default_rng(seed)
    s = {"interest": rng.random(N), "interp": rng.random(N)}
    # Informative scores: a site fails more often the higher its score.
    y = {"interest": rng.random(N) < 0.60 * s["interest"], "interp": rng.random(N) < 0.70 * s["interp"]}
    return s, y


def shared_rate(cov, y):
    return float(np.mean((cov["interest"] & y["interest"]) | (cov["interp"] & y["interp"])))


def run(variant, s, y, rng):
    pol = NestedPathPolicy(EPS, CONF)
    sc = {n: v.copy() for n, v in s.items()}
    if variant == "oracle":
        sc = {n: np.where(y[n], 0.5 + 0.5 * s[n], 0.5 * s[n]) for n in s}
    if variant == "chosen":
        # Calibrate where the scores are least sure, as an active learner would.
        high = np.argsort(sc["interest"] + sc["interp"])[N // 2:]
        cal = np.sort(rng.choice(high, M, replace=False))
    else:
        cal = np.sort(rng.choice(N, M, replace=False))
    if variant == "redraw":
        # Keep the most favourable of five draws: the one that skips most.
        best, best_n = cal, -1
        for _ in range(5):
            c = np.sort(rng.choice(N, M, replace=False))
            d = pol.decide(LevelData(N, sc, c, {n: y[n][c] for n in sc}))
            n_cov = int(np.sum(d.covers["interest"] | d.covers["interp"]))
            if n_cov > best_n:
                best, best_n = c, n_cov
        cal = best
    if variant == "refit":
        for n in sc:
            sc[n] = sc[n].copy()
            sc[n][cal[y[n][cal]]] = 2.0     # failing calibration sites pushed to the top
    d = pol.decide(LevelData(N, sc, cal, {n: y[n][cal] for n in sc}))
    return shared_rate(d.covers, y) > EPS + 1e-12


def main():
    s, y = population()
    pick = NestedPathPolicy(EPS, CONF).decide(
        LevelData(N, s, np.arange(M), {n: y[n][:M] for n in s})).tails["E"]["delta_picked"]
    out = {}
    for v in ("valid", "oracle", "refit", "chosen", "redraw"):
        rng = np.random.default_rng(1)
        ex = sum(run(v, s, y, rng) for _ in range(T))
        out[v] = dict(exceeded=int(ex), draws=T, frequency=ex / T)
        print(f"{v:8s} {ex}/{T} = {ex / T:.3f}  (picked level {pick:.3f}, nominal {1 - CONF:.2f})", flush=True)
    out["_picked"] = pick
    Path("results").mkdir(exist_ok=True)
    Path("results/anticipation_demo.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
