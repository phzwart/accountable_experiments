# Appendix C. A bound on the conditional rate (draft 1)

The rate bounded in Appendices A and B counts wrong skips among all sites of a level. A reader of the map may instead need the rate among the sites one claim covers. Learn then Test gives that bound for a family of thresholds fixed before the labels are seen [Angelopoulos2021].

Keep the notation of Appendix B for one certificate with frozen score $S$ and bad label $B$. The family of thresholds is a grid of quantiles of the frozen scores over the whole level,

$$
\tau_i = Q_S(q_i), \quad q_i = q_0 + 0.05\,(i - 1), \quad i = 1, \dots, I
$$

ending at $q_I = 1$. Both the grid and $q_0$ depend on the scores and on settings fixed in advance, and on no label. Threshold $\tau_i$ covers the set $D_i = \{x \in D : S(x) \le \tau_i\}$ of $N_i$ sites, and its conditional rate is

$$
R_i = N_i^{-1} \, \#\{x \in D_i : B(x) = 1\}
$$

For each $i$, the null hypothesis $H_i : R_i > \alpha$ is tested on the calibration sites in $D_i$. Their number $n_i = |C \cap D_i|$ is random; given $n_i$, they form a uniform sample without replacement from $D_i$, since $C$ is uniform on $D$ and $D_i$ is fixed before the draw. The number $f_i$ of bad labels among them is then hypergeometric, and

$$
p_i = P(H_i^\ast \le f_i)
$$

with $H_i^\ast$ hypergeometric on $N_i$ sites, $\lfloor \alpha N_i \rfloor + 1$ of them bad and $n_i$ draws, is a valid p-value for $H_i$ conditional on $n_i$, hence also unconditionally. The binomial tail $P(\mathrm{Bin}(n_i, \alpha) \le f_i)$ approximates it closely at the sizes of this study and is the one recorded.

The rates $R_i$ need not increase with $i$, so the hypotheses are tested in a fixed order: $H_1, H_2, \dots$, each at level $\delta$, stopping at the first that is not rejected. Fixed-sequence testing controls the family-wise error at $\delta$ [Bauer1991], so with probability at least $1 - \delta$ every rejected hypothesis is false. The rule covers $D_{i^\ast}$, where $i^\ast$ is the last rejection, and covers nothing when $H_1$ is not rejected. With probability at least $1 - \delta$,

$$
R_{i^\ast} \le \alpha
$$

**Minimum calibration size and starting quantile.** A hypothesis can be rejected only if its calibration sites can show a small enough tail even with no bad label, which requires $(1 - \alpha)^{n_i} \le \delta$, or

$$
n_i \ge n_{\min} = \lceil \log \delta / \log (1 - \alpha) \rceil
$$

The first threshold therefore covers at least the share $n_{\min}/m$ of the level, and $q_0$ is that share rounded up to a multiple of 0.05. With $\alpha = \delta = 0.10$, $n_{\min} = 22$, and at $m = 40$ the grid starts at the 0.55 quantile: the rule certifies nothing or more than half of the level. A useful conditional bound thus calls for calibration samples several times larger than the rate bounds of Appendices A and B need, which is why the main text reports those.

## Notes for revision (not part of the text)

- References to add: [Angelopoulos2021] Angelopoulos, Bates, Candès, Jordan, Lei (2021), Learn then Test: calibrating predictive algorithms to achieve risk control, arXiv:2110.01052 (Ann. Appl. Stat. 2025, check); [Bauer1991] Bauer (1991), Multiple testing in clinical trials, Stat. Med. 10(6), 871–890 (fixed-sequence procedure; check).
- The record uses the binomial p-value (the hypergeometric option exists in the software, SI 4); the binomial is not dominated by the hypergeometric in every case, so if the conditional rate is ever reported in Results, rerun with the exact p-value.
- Table 3 example uses α = δ = 0.10; check it matches the setting used anywhere the conditional rate is quoted.
