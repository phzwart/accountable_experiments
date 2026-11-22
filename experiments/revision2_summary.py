"""
Summary of the round-2 studies: results/revision2/summary.json.

    python -m experiments.revision2_summary
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from experiments.record import OUT as REC, REASONS

OUT = Path("results/revision2")


def jl(f):
    return [json.loads(l) for l in Path(f).open()] if Path(f).exists() else []


def ms(x):
    x = np.asarray(x, float)
    return dict(mean=float(x.mean()), sd=float(x.std(ddof=1)) if len(x) > 1 else 0.0, n=int(len(x)))


def record_recall(row="syn_peak_2cert_nested_watson", eps_r=0.20):
    z = np.load(REC / row / "sites.npz")
    R = np.array(REASONS)[z["reason"]]
    I = z["interesting"].astype(bool)
    lv = z["levels"]
    A = np.isin(R, ["not_interesting", "not_interesting+interpolable"])
    rates, over = [], []
    for L in range(3, int(lv.max()) + 1):
        m = lv == L
        ni = I[:, m].sum(1)
        r = (A & I)[:, m].sum(1) / np.maximum(ni, 1)
        rates.append(r); over.append(r > eps_r + 1e-12)
    overall = (A & I)[:, lv > 2].sum(1) / I[:, lv > 2].sum(1)
    return dict(n=int(len(z["seeds"])), measured=ms(z["measured"].sum(1)), lost_overall=ms(overall),
                level_recall_over=float(np.mean(over)),
                lost_per_level=[float(np.mean(r)) for r in rates])


def recall(eps=0.20):
    rr = jl(OUT / "recall_syn.jsonl")
    if not rr:
        return None
    eps_r = rr[0]["eps_r"]
    lv = [l for r in rr for l in r["levels"]]
    rec = [v for r in rr for v in r["recall"].values() if v["rate"] is not None]
    overall = [sum(v["lost"] for v in r["recall"].values()) / sum(v["n_interest"] for v in r["recall"].values())
               for r in rr]
    Ls = sorted({int(k) for r in rr for k in r["recall"]})
    return dict(n=len(rr), measured=ms([r["measured"] for r in rr]),
                level_over=float(np.mean([l["exceeded"] for l in lv])),
                level_expected=float(np.mean([l["picked"] for l in lv])),
                recall_over=float(np.mean([v["rate"] > eps_r + 1e-12 for v in rec])),
                lost_overall=ms(overall),
                lost_per_level=[float(np.mean([r["recall"][str(L)]["rate"] for r in rr
                                               if r["recall"][str(L)]["rate"] is not None])) for L in Ls],
                record=record_recall(eps_r=eps_r))


def drift(eps=0.20):
    out = {}
    for f in sorted(OUT.glob("drift_syn_*.jsonl")):
        rr = jl(f)
        sw = rr[0]["swell"]
        lv = [l for r in rr for l in r["levels"]]
        over = [l["E_rate"] > eps + 1e-12 for l in lv]
        flag = [l["check_fail"] > 0 for l in lv]
        camp_over = [any(l["E_rate"] > eps + 1e-12 for l in r["levels"]) for r in rr]
        camp_flag = [any(l["check_fail"] > 0 for l in r["levels"]) for r in rr]
        # an exceedance is caught when the check of its level, or of an earlier level, failed
        caught = []
        for r in rr:
            seen = False
            for l in r["levels"]:
                seen = seen or l["check_fail"] > 0
                if l["E_rate"] > eps + 1e-12:
                    caught.append(seen)
        by_level = {}
        for L in sorted({l["L"] for l in lv}):
            xs = [l for l in lv if l["L"] == L]
            by_level[int(L)] = dict(rate=float(np.mean([x["E_rate"] for x in xs])),
                                    over=float(np.mean([x["E_rate"] > eps + 1e-12 for x in xs])),
                                    flagged=float(np.mean([x["check_fail"] > 0 for x in xs])),
                                    swell_at_end=float(sw * np.mean([x["clock"] for x in xs]) / 334.0))
        out[f"{sw:.2f}"] = dict(n=len(rr), measured=ms([r["measured"] for r in rr]),
                                level_over=float(np.mean(over)), level_expected=float(np.mean([l["picked"] for l in lv])),
                                mean_rate=float(np.mean([l["E_rate"] for l in lv])),
                                level_flagged=float(np.mean(flag)), campaign_over=float(np.mean(camp_over)),
                                campaign_flagged=float(np.mean(camp_flag)),
                                caught=float(np.mean(caught)) if caught else None, n_over=int(sum(over)),
                                by_level=by_level)
    return out


def costgrid():
    out = {}
    for f in sorted(OUT.glob("cost_ir_*.jsonl")):
        rr = jl(f)
        if not rr:
            continue
        lv = [l for r in rr for l in r["levels"]]
        out[f.stem] = dict(m=rr[0]["m"], c=rr[0]["c"], n=len(rr), measured=ms([r["measured"] for r in rr]),
                           level_over=float(np.mean([l["exceeded"] for l in lv])),
                           level_expected=float(np.mean([l["picked"] for l in lv])),
                           k=sorted({l["k"] for l in lv}))
    return out


def main():
    s = dict(recall=recall(), drift=drift(), costgrid=costgrid())
    for name in ("audit.json", "gpacq_nacl.json"):
        if (OUT / name).exists():
            s[name.split(".")[0]] = json.loads((OUT / name).read_text())
    (OUT / "summary.json").write_text(json.dumps(s, indent=1))
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    main()
