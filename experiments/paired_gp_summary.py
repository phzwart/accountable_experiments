"""Summary of experiments/paired_gp.py: per kernel and driving trajectory, for both cuts on identical states."""
import json
import numpy as np
from scipy.stats import binomtest

rr = [json.loads(l) for l in open("results/revision2/paired_gp.jsonl")]
out = {}
for kernel in ("fitted", "nugget"):
    for driver in ("contract", "uq"):
        sub = [r for r in rr if r["kernel"] == kernel and r["driver"] == driver]
        if not sub:
            continue
        n = len(sub)
        tot = np.array([r["measured"] for r in sub])
        print(f"\n{kernel} kernel, trajectory driven by {driver}: {n} designs, measured {tot.mean():.0f} ± {tot.std():.0f}")
        for cut in ("uq", "contract"):
            N = np.array([[x["N"] for x in r["rounds"]] for r in sub]); cap = np.array([[x["cap"] for x in r["rounds"]] for r in sub])
            sk = np.array([[x[cut]["n_skip"] for x in r["rounds"]] for r in sub]); wr = np.array([[x[cut]["realised"] for x in r["rounds"]] for r in sub])
            st = np.array([[x[cut]["stated"] for x in r["rounds"]] for r in sub])
            d = wr / N - st; within = (d <= 1e-12).mean(0); over = (wr > cap).mean(0)
            pv = [binomtest(int((d[:, j] <= 1e-12).sum()), n, 0.8).pvalue for j in range(d.shape[1])]
            print(f"  {cut:8s} skipped {sk.mean(0).round(0)} (sd {sk.std(0).round(0)})  wrong {wr.mean(0).round(1)}  "
                  f"stated {st.mean(0).round(3)}  within own bound {within.round(3)} (p {['%.2g' % x for x in pv]})  "
                  f"over budget {over.round(3)}  q80 delta {np.quantile(d, .8, axis=0).round(3)}")
            out[f"{kernel}/{driver}/{cut}"] = dict(n=n, skipped=sk.mean(0).tolist(), wrong=wr.mean(0).tolist(), stated=st.mean(0).tolist(),
                                                  within=within.tolist(), p_within=pv, over=over.tolist(),
                                                  q80_delta=np.quantile(d, .8, axis=0).tolist(), measured_trajectory=float(tot.mean()))
json.dump(out, open("results/revision2/paired_gp_summary.json", "w"), indent=1)
