"""
Summary of measured sites over the recorded campaigns (levels with a certificate), and of the replayed campaign
of average cost per dataset (results/measurement_record). Writes results/measurement_record/SUMMARY.json.

    python -m experiments.measurement_summary
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from experiments.measurement_record import ROWS, OUT
from experiments.record import OUT as REC, REASONS


def pooled(row):
    z = np.load(REC / row / "sites.npz")
    lv = np.asarray(z["levels"])
    c = np.broadcast_to(lv >= 3, z["measured"].shape)
    R = np.array(REASONS)[z["reason"]]
    F, I = z["fail_prior"].astype(bool), z["interesting"].astype(bool)
    groups = dict(calibration=(R == "calibration") & c, chosen=(R == "no_certificate") & c,
                  skipped_pred=np.isin(R, ["interpolable", "not_interesting+interpolable"]) & c,
                  skipped_noint=np.isin(R, ["not_interesting", "not_interesting+interpolable"]) & c)
    n = len(z["seeds"])
    out = dict(campaigns=n, per_campaign={k: float(m.sum() / n) for k, m in groups.items()},
               seed_sites=float((R == "seed").sum() / n), certified_sites=int((lv >= 3).sum()))
    for k, m in groups.items():
        out[k] = dict(fail=float(F[m].mean()), interesting=float(I[m].mean()), needed=float((F & I)[m].mean()))
    out["lift_needed"] = out["chosen"]["needed"] / out["calibration"]["needed"]
    return out


def replayed(row):
    d = np.load(OUT / f"{row}.npz")
    c = d["level"] >= 3
    ch = (d["reason"] == "no_certificate") & c
    cal = d["is_cal"] & c
    r, p = d["residual"], d["p_resid"]
    return dict(seed=int(d["seed"]), chosen=int(ch.sum()), calibration=int(cal.sum()),
                median_resid_cal=float(np.median(r[cal])), median_resid_chosen=float(np.median(r[ch])),
                p_below_02_chosen=float(np.mean(p[ch] < 0.2)), p_below_05_chosen=float(np.mean(p[ch] < 0.5)),
                chosen_needed=float(np.mean((d["fail"] & d["interesting"])[ch])))


def main():
    S = {row: dict(name=name, pooled=pooled(row), replay=replayed(row)) for row, name in ROWS.items()}
    (OUT / "SUMMARY.json").write_text(json.dumps(S, indent=1))
    for row, v in S.items():
        P, Rp = v["pooled"], v["replay"]
        print(f"\n{v['name']}  ({P['campaigns']} campaigns; certified-level sites {P['certified_sites']})")
        print("  per campaign:", {k: round(x, 1) for k, x in P["per_campaign"].items()}, "seed", P["seed_sites"])
        for k in ("calibration", "chosen", "skipped_pred", "skipped_noint"):
            print(f"  {k:14s} fail {P[k]['fail']:.3f}  interesting {P[k]['interesting']:.3f}  needed {P[k]['needed']:.3f}")
        print(f"  lift needed chosen/cal {P['lift_needed']:.2f}")
        print("  replay:", {k: (round(x, 3) if isinstance(x, float) else x) for k, x in Rp.items()})


if __name__ == "__main__":
    main()
