"""
Summary of the revision runs: campaign-level contracts, conformal risk control on the same draw, and uniform
subsampling at equal cost, against the per-level certified plans of the record.

    python -m experiments.revision_summary
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

import numpy as np

REC = Path("results/record")
ROWS = {"ir": "ir_nested_watson", "nacl": "nacl_fwhm_nested_watson", "syn": "syn_env_nested_watson"}


def jl(f):
    return [json.loads(l) for l in Path(f).open()] if Path(f).exists() else []


def per_level_record(row):
    rs = [json.loads(l) for l in gzip.open(REC / row / "runs.jsonl.gz", "rt")]
    picked = [p for p in json.loads((REC / "PICKED.json").read_text()) if p["row"] == row and p["event"] == "R_E"]
    by_seed = {}
    for p in picked:
        by_seed.setdefault(p["seed"], []).append(p["exceeded"])
    camp = np.mean([any(v) for v in by_seed.values()])
    return dict(n=len(rs), measured=np.mean([r["summary"]["n_measured"] for r in rs]),
                measured_sd=np.std([r["summary"]["n_measured"] for r in rs], ddof=1),
                level_exceed=np.mean([p["exceeded"] for p in picked]), campaign_exceed=camp,
                mean_picked=np.mean([p["picked"] for p in picked]))


def main():
    out = {}
    uni = json.loads(Path("results/uniform_baseline.json").read_text()) if Path("results/uniform_baseline.json").exists() else {}
    for key, row in ROWS.items():
        d = dict(per_level=per_level_record(row))
        cc = jl(f"results/campaign_contract/{key}.jsonl")
        if cc:
            lv = [l for r in cc for l in r["levels"]]
            d["campaign"] = dict(n=len(cc), measured=np.mean([r["measured"] for r in cc]),
                                 measured_sd=np.std([r["measured"] for r in cc], ddof=1),
                                 campaign_exceed=np.mean([r["campaign_exceeded"] for r in cc]),
                                 level_exceed=np.mean([l["exceeded"] for l in lv]),
                                 mean_picked=np.mean([l["picked"] for l in lv]),
                                 sum_picked=np.mean([sum(l["picked"] for l in r["levels"]) for r in cc]),
                                 wrong_share=np.mean([r["wrong"] / r["n_cert"] for r in cc]),
                                 level_confidence=cc[0]["level_confidence"], campaign_confidence=cc[0]["campaign_confidence"])
        crc = jl(f"results/crc_baseline/{key}.jsonl")
        if crc:
            d["crc"] = dict(n=len(crc), measured=np.mean([r["measured"] for r in crc]),
                            level_exceed=np.mean([e for r in crc for e in r["exceeded"]]),
                            campaign_exceed=np.mean([any(r["exceeded"]) for r in crc]),
                            wrong_share=np.mean([r["wrong"] / r["n_cert"] for r in crc]),
                            mean_level_rate=np.mean([l["E_rate"] for r in crc for l in r["levels"]]),
                            k=sorted({l["k"] for r in crc for l in r["levels"]}))
        if key in uni:
            d["uniform"] = dict(measured=uni[key]["measured"], share=uni[key]["share_mean"],
                                sd=uni[key].get("share_sd"), range=uni[key]["share_range"], n=uni[key].get("n"))
        if "certified_final" in uni and key in uni["certified_final"]:
            d["certified_final"] = uni["certified_final"][key]
        out[key] = d
        print(f"== {key}")
        for k, v in d.items():
            print(" ", k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items()})
    Path("results/revision_summary.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
