"""
The price of an unreliable error rate. For a cost ratio r (cost of one wrong skip over cost of one
measurement), every agent picks its operating point by the cost it believes, measurements + r x (wrong skips
it states), and pays measurements + r x (true wrong skips). Certified campaigns state their bound, eps times
the sites of the certified levels; uncertified campaigns state the sum of their own probabilities of a wrong
skip. Measuring every site is always available. The excess cost of an agent is what it pays over the cheapest
operating point among all options at that r.

    python -m experiments.price_of_uncertainty
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

D = Path("results/uncertified")
RATIOS = np.logspace(-1, 3, 41)
KEYS = ("ir", "nacl", "syn")


def families(key):
    unc = json.loads((D / f"{key}.json").read_text())
    cert = json.loads((D / f"certified_{key}.json").read_text())
    n_total = unc[0]["n_total"]
    fam = {}
    for c in cert:
        name = "certified, natural neighbour" if c["predictor"] == "sibson" else "certified, GP"
        fam.setdefault(name, []).append(dict(M=c["measured"], W=c["wrong"], S=c["eps"] * c["n_cert"], op=c["eps"]))
    for kind, label in (("latent", "GP, latent sd"), ("predictive", "GP, predictive sd"), ("loo", "GP, recalibrated")):
        fam["uncertified " + label] = [dict(M=r["measured"], W=r["wrong"], S=r["stated"], op=r["alpha"])
                                       for r in unc if r["kind"] == kind]
    everything = dict(M=n_total, W=0.0, S=0.0, op="all")
    return fam, everything, n_total


def analyse(key):
    fam, everything, n_total = families(key)
    allpts = [p for pts in fam.values() for p in pts] + [everything]
    out = dict(ratios=RATIOS.tolist(), n_total=n_total, curves={}, choices={})
    for name, pts in fam.items():
        pts = pts + [everything]
        excess, chosen, surprise = [], [], []
        for r in RATIOS:
            best = min(p["M"] + r * p["W"] for p in allpts)
            p = min(pts, key=lambda q: q["M"] + r * q["S"])
            paid = p["M"] + r * p["W"]
            believed = p["M"] + r * p["S"]
            excess.append(paid / best - 1)
            surprise.append(paid / believed - 1)
            chosen.append(p["op"])
        out["curves"][name] = dict(excess=excess, surprise=surprise)
        out["choices"][name] = chosen
    out["points"] = {name: pts for name, pts in fam.items()}
    return out


def main():
    res = {k: analyse(k) for k in KEYS}
    (D / "price.json").write_text(json.dumps(res, indent=1))
    for k in KEYS:
        print(k)
        for name, c in res[k]["curves"].items():
            ex = np.array(c["excess"]); su = np.array(c["surprise"])
            idx = [np.argmin(np.abs(np.array(res[k]["ratios"]) - r)) for r in (1, 10, 100)]
            print(f"  {name:38s} excess at r=1,10,100: " + ", ".join(f"{100 * ex[i]:6.0f}%" for i in idx)
                  + "   surprise: " + ", ".join(f"{100 * su[i]:6.0f}%" for i in idx))


if __name__ == "__main__":
    main()
