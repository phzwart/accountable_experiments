import json, numpy as np
from accountable import make_policy
from accountable.campaign import run_campaign
from experiments.record import build
from experiments.confidence_audit import audit_level
out=[]
for s in range(4):
    ds, cfg, _ = build("syn_env_nested_watson", s, {})
    cfg.policy = make_policy("nested_path", budget=0.20, confidence=1 - 0.2/6)
    res = run_campaign(ds, cfg)
    rng = np.random.default_rng(77 + s)
    for L in range(4, 9):
        for r in audit_level(res, ds, cfg, L, 3000, rng):
            r.update(seed=s); out.append(r)
            print(s, L, r["N"], r["k"], "worst %.4f attained %.4f rate_max %.3f" % (r["worst_case"], r["attained"], r["rate_max"]), flush=True)
json.dump(out, open("results/campaign_contract/syn_audit.json","w"), indent=1)
