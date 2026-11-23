# SI 9. The map bound

The calibration draw of a level serves a second purpose. Its interpolation labels are the errors, at the sites of the new level, of the map built from all coarser measurements. They therefore measure how well that map predicts at the density of the new level.

Let level $L + 1$ have $N$ sites, of which $K$ lie outside tolerance of the map frozen before its draw. The $m$ calibration sites are a uniform sample without replacement, so the number $f$ of failures among them is hypergeometric. The map bound is the exact upper limit for a draw without replacement: the largest share $K'/N$ for which the observed $f$ is not rejected at level $\delta_{\mathrm{map}}$,

$$
u(f) = \max \{ K'/N : P(H_{N, K', m} \le f) > \delta_{\mathrm{map}} \}
$$

with $H_{N, K', m}$ hypergeometric, $N$ sites of which $K'$ fail and $m$ draws. It holds with probability at least $1 - \delta_{\mathrm{map}}$ for every $K$, by the same inversion of the tail as Proposition A.1. The record also stores the Clopper–Pearson limit [ClopperPearson1934], $\mathrm{Beta}^{-1}(1 - \delta_{\mathrm{map}};\ f + 1,\ m - f)$, which is exact for a binomial count, wider at the sizes of this study, and can fall short by a few per cent when the failing share is close to one.

**Sharing the draw with the decision.** The same draw sets the thresholds of level $L + 1$. The decision fails with probability at most $\delta_{L+1}$ and the map bound with probability at most $\delta_{\mathrm{map}}$, so by the union bound both hold together with probability at least

$$
1 - \delta_{L+1} - \delta_{\mathrm{map}}
$$

No independence between the two statements is needed.

**Sites of interest.** Given the number $m_Z$ of calibration sites of interest, those sites are a uniform sample without replacement from the sites of interest of the level. The same limit, applied to their failures, bounds the failing share among the sites of interest. This is the label-conditional statement of Section 3.4, at the cost of a smaller sample.

**Scope.** The bound concerns the map frozen before the draw, at the sites of the new level. The final map also uses the calibration sites and every site measured because no claim covered it. Those depend on the draw, so the plan gives the final map no finite-sample statement; the audit of Section 3.6 gives it one, and here it is also checked against the truth (Section 5.4).

**Record.** The map bound states, from the calibration draw of a level, how many of its sites the map built from coarser levels predicts outside tolerance. Recomputed with the exact limit from the 250 campaigns of each main configuration, it held on 95.8 % of the guaranteed levels for IR, 84.4 % for NaCl and 87.2 % for the synthetic map, against confidences of 0.75, 0.80 and 0.80; the Clopper–Pearson limit held on 100 %, 88.5 % and 90.9 %, at mean upper limits 0.052, 0.593 and 0.483 against 0.042, 0.579 and 0.463 for the exact one. On NaCl about half of the last-level sites lie outside that tolerance; the skip guarantee concerns only the sites a claim covers.
