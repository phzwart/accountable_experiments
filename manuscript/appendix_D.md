# Appendix D. The map bound (draft 1)

The calibration draw of a level serves a second purpose. Its interpolation labels are the errors, at the sites of the new level, of the map built from all coarser measurements. They therefore measure how well that map predicts at the density of the new level.

Let level $L + 1$ have $N$ sites, of which $K$ lie outside tolerance of the map frozen before its draw. The $m$ calibration sites are a uniform sample without replacement, so the number $f$ of failures among them is hypergeometric. The map bound is the Clopper–Pearson upper limit [ClopperPearson1934] at confidence $1 - \delta_{\mathrm{map}}$,

$$
u(f) = \mathrm{Beta}^{-1}(1 - \delta_{\mathrm{map}};\ f + 1,\ m - f)
$$

with $u(m) = 1$. The limit is exact for a binomial count. For a draw without replacement it was checked numerically: at $m = 40$, for every level size $N$ from 41 to 1200 and every failing share $K/N \le 0.6$, the probability that $u(f) \ge K/N$ was at least 0.754, 0.804 and 0.904 at confidences 0.75, 0.80 and 0.90. At failing shares close to one, the binomial limit can fall short by a few per cent; the hypergeometric limit, found by inverting the hypergeometric tail in $K$, removes that gap.

**Sharing the draw with the decision.** The same draw sets the thresholds of level $L + 1$. The decision fails with probability at most $\delta_{L+1}$ and the map bound with probability at most $\delta_{\mathrm{map}}$, so by the union bound both hold together with probability at least

$$
1 - \delta_{L+1} - \delta_{\mathrm{map}}
$$

No independence between the two statements is needed.

**Sites of interest.** Given the number $m_Z$ of calibration sites of interest, those sites are a uniform sample without replacement from the sites of interest of the level. The same limit, applied to their failures, bounds the failing share among the sites of interest. This is the label-conditional statement of Section 6, at the cost of a smaller sample.

**Scope.** The bound concerns the map frozen before the draw, at the sites of the new level. The final map also uses the calibration sites and every site measured because no claim covered it. Those depend on the draw, so the final map carries no finite-sample statement and is checked against the truth (Section 5.4).
