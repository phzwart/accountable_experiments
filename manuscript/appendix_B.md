# Appendix B. Guarantees on the shared wrong-skip event (draft 1)

Fix a level with population $D$ of $N$ sites and a set $J$ of certificates. Certificate $j$ has a frozen score $S_j$ and a bad label $B_j$ ($Z$ for interest, $F$ for interpolation). A calibration sample $C \subset D$ of size $m$ is drawn uniformly without replacement after the scores are frozen; labels are known on $C$ only. Write $k(\varepsilon, \delta)$ for the largest integer with $P(H \le k) \le \delta$, where $H$ is hypergeometric with population $N$, $\lfloor \varepsilon N \rfloor + 1$ marked sites and $m$ draws, as in Appendix A. The binomial tail $P(\mathrm{Bin}(m, \varepsilon) \le k)$ gives a valid but smaller $k$.

The shared wrong-skip event of a site under covers $\{A_j\}$ is

$$
E(x) = \bigvee_{j \in J} \big(A_j(x) \wedge B_j(x)\big)
$$

and $R_E = N^{-1} \sum_{x \in D} E(x)$.

## B.1 Per-claim budgets

**Proposition B.1.** Let each $\hat\tau_j$ be set by the rule of Appendix A with budget $\varepsilon_j$ and failure probability $\delta_j$, all on the same draw $C$. Then, with probability at least $1 - \sum_j \delta_j$,

$$
R_j(\hat\tau_j) \le \varepsilon_j \ \text{for every} \ j \in J
$$

and on the same event

$$
R_E \le \sum_{j \in J} \varepsilon_j
$$

*Proof.* Appendix A bounds the probability of $R_j(\hat\tau_j) > \varepsilon_j$ by $\delta_j$ for each $j$; the union bound over $j$ gives the first statement. Since $E(x) \le \sum_j A_j(x) B_j(x)$ for every site, $R_E \le \sum_j R_j$. $\square$

On the same event, the rate of sites at which every covering claim fails is at most $\min_j \varepsilon_j$. No threshold exists for certificate $j$ when $k(\varepsilon_j, \delta_j) < 0$, that is, when $\varepsilon_j < 1 - \delta_j^{1/m}$; the certificate then covers nothing.

## B.2 One budget along a nested path

A path is given by entry times $\lambda_j(x) \in [0, \infty]$, one per certificate and site, computed from the frozen scores of the whole level and from settings fixed in advance, and from no calibration label. Certificate $j$ covers $x$ at path position $\lambda$ when $\lambda_j(x) \le \lambda$. Define the cover time and the failure time of a site,

$$
\lambda_{\mathrm{cov}}(x) = \min_{j \in J} \lambda_j(x)
$$

$$
\lambda_E(x) = \min \{\lambda_j(x) : j \in J,\ B_j(x) = 1\}
$$

with $\lambda_E(x) = \infty$ when no label is bad. A site is a wrong skip at $\lambda$ exactly when $\lambda_E(x) \le \lambda$, so

$$
R_E(\lambda) = N^{-1} \, \#\{x \in D : \lambda_E(x) \le \lambda\}
$$

is nondecreasing and right-continuous in $\lambda$. Let $k = k(\varepsilon, \delta)$. Let $b$ be the $(k+1)$-th smallest finite value of $\lambda_E$ on $C$. The rule covers every site with $\lambda_{\mathrm{cov}} < b$, every site when $C$ holds at most $k$ finite values of $\lambda_E$, and no site when $k < 0$. Write $\hat\lambda$ for any position below $b$ that covers the same sites.

**Proposition B.2.** With probability at least $1 - \delta$ over the draw, $R_E(\hat\lambda) \le \varepsilon$.

*Proof.* Let $\lambda^\ast = \inf\{\lambda : R_E(\lambda) > \varepsilon\}$. By right-continuity, the set $K = \{x : \lambda_E(x) \le \lambda^\ast\}$ has $|K| \ge \lfloor \varepsilon N \rfloor + 1$ sites. The set depends on the labels and the entry times, and on nothing drawn. If $R_E(\hat\lambda) > \varepsilon$, then $\hat\lambda \ge \lambda^\ast$, so every site of $K$ has $\lambda_E \le \hat\lambda$. Since $\hat\lambda < b$, at most $k$ calibration sites have $\lambda_E \le \hat\lambda$, hence $|C \cap K| \le k$. The count $|C \cap K|$ is hypergeometric, and the remainder of the argument is that of Appendix A:

$$
P\big(R_E(\hat\lambda) > \varepsilon\big) \le P\big(|C \cap K| \le k\big) \le \delta
$$

$\square$

Testing the hypotheses $R_E(\lambda) > \varepsilon$ in order of increasing $\lambda$ and stopping at the first that cannot be rejected is fixed-sequence testing in Learn-then-Test [Angelopoulos2025]; Proposition B.2 is the one-dimensional, monotone case. With a single certificate, $\lambda_E$ and $\lambda_{\mathrm{cov}}$ coincide on bad sites and the rule reduces to Appendix A.

**Quantile path.** With $\hat F_j$ the empirical distribution function of $S_j$ over the level and weights $w_j \in (0, 1]$,

$$
\lambda_j(x) = \hat F_j(S_j(x)) / w_j
$$

**Priority path.** With $i_j \in \{0, 1, \dots\}$ the position of certificate $j$ in a fixed order,

$$
\lambda_j(x) = i_j + \hat F_j(S_j(x))
$$

so that certificate $j$ sweeps its own quantiles over $\lambda \in (i_j, i_j + 1]$ while earlier certificates stay at their final coverage. In both paths, a certificate restricted to sites below a cap on its score receives $\lambda_j(x) = \infty$ above the cap. Both are functions of frozen scores and fixed settings, and Proposition B.2 applies.

## B.3 The sequential rule

The rule of the original IR analysis first sets the interest threshold on $C$, then sets the interpolation threshold on the calibration sites the interest certificate leaves uncovered, from the budget that remains. The second entry time then depends on calibration labels, $K$ in the proof of Proposition B.2 is no longer fixed before the draw, and the hypergeometric step fails. Section 5.2 reports the consequence on a population with uninformative scores: the bound is exceeded in 0.288 of draws against 0.25 allowed. The priority path keeps the same preference and the fixed-path condition.

## B.4 Other families

Proposition B.2 needs a family of covers fixed before the labels and nested in one parameter. A family without that order, such as a two-dimensional grid of threshold pairs, is handled by Learn-then-Test with a family-wise correction across the grid [Angelopoulos2025], or by learning a path on one part of the draw and testing it on the other [LauferGoldshtein2023]. Both give guarantees of the same kind at the cost of a smaller effective calibration sample.

## B.5 Attaining the nominal failure probability

On a fixed level population, the exceedance probability of the rule above equals $P(|C \cap K| \le k)$ when the wrong-skip rate crosses $\varepsilon$ at exactly $\lfloor \varepsilon N \rfloor + 1$ sites, and is smaller otherwise. With $k$ from the hypergeometric tail, the bound is therefore attained up to the integer step in $k$: at $m = 40$ and $\varepsilon = 0.10$, $k = 2$ gives at most 0.21 on 399 sites against $\delta = 0.25$. A randomised rule, which uses $k + 1$ with the probability that makes the mixture of the two tails equal to $\delta$, removes the step [Lehmann & Romano 2005, ch. 3]. It makes the decision depend on an extra coin and is not used here.
