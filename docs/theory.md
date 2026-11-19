# Theory of the accountable campaign

An accountable campaign spends measurements only where the data cannot vouch for a site. Every skipped site carries a stated risk, and that risk is controlled by a random calibration draw rather than by the model that proposed the skip. This document fixes the mathematics shared by every experiment in this package. The experiments differ in data, design and predictor. They do not differ in what is claimed.

## 1. Objects

A campaign runs on a finite design $D$ partitioned into levels $D_0, D_1, \dots, D_{L_{\max}}$. Every site at level $L_s$ or coarser is the seed and is measured. Each finer level $L$ is processed once, in order.

Before level $L$ is touched, the measured set is $M_{<L}$. Everything used to decide level $L$ is a function of $M_{<L}$ and of randomness independent of the level's labels:

- a predictor $\hat y_L$, giving a prediction at any site from $M_{<L}$ alone;
- one score $S_{j,L}(x)$ per certificate $j$, larger meaning less safe to skip.

A site carries a truth $y(x)$, either the full spectrum or a quantity derived from it by a target map $\varphi$. Two bad-event labels are defined on the truth:

$$
Z(x) = \mathbb{1}\{\text{the site is interesting}\}
$$

$$
F_L(x) = \mathbb{1}\{ s(\varphi(y(x)), \hat y_L(x)) > 1 \}
$$

The acceptance score $s$ is normalised so that $s \le 1$ means the prediction meets the campaign tolerance. The interest certificate claims $Z = 0$ on the sites it covers. The interpolation certificate claims $F_L = 0$ on the sites it covers. Scores only order sites. A poor score spends measurements and leaves the guarantee intact.

## 2. One certificate

For certificate $j$ with bad label $B_j \in \{Z, F_L\}$, the population joint rate on level $L$ at threshold $\tau$ is

$$
R_j(\tau) = \frac{1}{N_L} \sum_{x \in D_L} \mathbb{1}\{S_j(x) \le \tau,\ B_j(x) = 1\}
$$

with $N_L = |D_L|$. $R_j$ is nondecreasing in $\tau$.

A calibration sample $C \subset D_L$ of size $m$ is drawn uniformly without replacement after the scores are frozen. Its sites are measured, so their labels are known. Let $k$ be the largest integer with

$$
P(\mathrm{Bin}(m, \varepsilon) \le k) \le \delta
$$

and let $b$ be the $(k+1)$-th smallest score among calibration sites with $B_j = 1$. Every site with $S_j < b$ is covered ("boundary placement", the default). The earlier rule stopped at the largest calibration score below $b$ ("calibration placement"); it is valid too and leaves the sites between that score and $b$ measured. When the sample holds at most $k$ bad sites, every site is covered. When no $k \ge 0$ satisfies the inequality, nothing is covered and the level is measured.

**Claim.** With probability at least $1 - \delta$ over the calibration draw, $R_j(\hat\tau) \le \varepsilon$.

The argument is the one-sided tolerance bound of Wilks (1941) in the form used for risk control by Bates et al. (2021) and Angelopoulos et al. (2021): let $\tau^\ast$ be the smallest score at which $R_j$ exceeds $\varepsilon$. The event $R_j(\hat\tau) > \varepsilon$ requires $\hat\tau \ge \tau^\ast$, hence at most $k$ calibration sites among the bad covered sites at $\tau^\ast$. That count is hypergeometric with a success fraction above $\varepsilon$. Appendix A gives the steps and the finite-population tail.

The claim concerns the level population, calibration sites included. The rate on the remainder (the non-calibration sites) is a check, not the guarantee.

**Finite population.** The calibration sample is drawn without replacement from $N_L$ sites, so the exact tail is hypergeometric on $N_L$ sites with $\lfloor \varepsilon N_L \rfloor + 1$ bad sites. The default $k$ is the largest integer with

$$
P\big(\mathrm{Hyp}(N_L, \lfloor \varepsilon N_L \rfloor + 1, m) \le k\big) \le \delta
$$

It is never smaller than the binomial $k$, and larger on small levels (at $m = 40$, $\varepsilon = 0.10$, $\delta = 0.25$: $k = 3$ on 65 sites against the binomial 2). Each run records both. With boundary placement the exceedance probability on a fixed population reaches this worst case (confidence audit, `experiments/confidence_audit.py`); the remaining gap to $\delta$ is the integer step in $k$. A randomised choice between $k$ and $k + 1$ would close it at the price of a random element in the decision; it is not implemented.

**Smallest certifiable budget.** With zero calibration failures allowed,

$$
\varepsilon_{\min} = 1 - \delta^{1/m}
$$

so $m = 40$ cannot certify $\varepsilon = 0.02$ at any confidence above 0.56.

## 3. Two certificates: the shared error event

A skip is wrong when any claim that covers it is false. With covers $A(x) = \mathbb{1}\{S_a(x) \le \tau_a\}$ and $B(x) = \mathbb{1}\{S_b(x) \le \tau_b\}$, the wrong-skip event is

$$
E(x) = (A(x) \wedge Z(x)) \vee (B(x) \wedge F_L(x))
$$

and its population rate is $R_E = N_L^{-1} \sum_{x \in D_L} E(x)$. Every budget policy in this package is stated as a bound on $R_E$, on the individual $R_a$ and $R_b$, or on both. That shared statement is what makes the experiments comparable.

$E$ is the conservative event. A site covered by both certificates counts as wrong when either claim fails, even if the other claim holds. The alternative, wrong only when every covering claim fails, is not monotone in the thresholds and has no order-statistic bound.

## 4. Budget policies

A policy turns frozen scores and calibration labels into thresholds and states its guarantee. New policies register under a name and must state their guarantee in the same terms, or declare that they have none.

### 4.1 `separate` (default)

Each certificate is calibrated on its own label by section 2, with budget $\varepsilon_j$ and failure probability $\delta_j$, on one shared draw. By the union bound, with probability at least $1 - \delta_a - \delta_b$:

$$
R_a(\hat\tau_a) \le \varepsilon_a \ \text{and} \ R_b(\hat\tau_b) \le \varepsilon_b
$$

Since $R_E \le R_a + R_b$, the same event gives $R_E \le \varepsilon_a + \varepsilon_b$. The rate of a skip that violates both labels is at most $\min(\varepsilon_a, \varepsilon_b)$. This is the NaCl scheme.

### 4.2 `nested_path`: one budget on the shared event

A single budget on $R_E$ needs a one-parameter family of threshold pairs fixed before any calibration label is seen. A nondecreasing path $\lambda \mapsto (\tau_a(\lambda), \tau_b(\lambda))$ on $\lambda \in [0, 1]$ is built from the frozen scores of the whole level. The default path matches quantiles:

$$
\tau_j(\lambda) = Q_j(w_j \lambda)
$$

where $Q_j$ is the empirical quantile function of $S_j$ over $D_L$ and $w_j \in (0, 1]$ tilts the path toward one certificate. No label enters the path.

Each site gets an entry time per certificate, $\lambda_j(x) = \inf\{\lambda : S_j(x) \le \tau_j(\lambda)\}$. The site is covered at $\lambda$ when $\lambda_{\mathrm{cov}}(x) = \min_j \lambda_j(x) \le \lambda$. It is a wrong skip at $\lambda$ when $\lambda_E(x) \le \lambda$, with

$$
\lambda_E(x) = \min(\lambda_a(x) \text{ if } Z(x),\ \lambda_b(x) \text{ if } F_L(x))
$$

and $\lambda_E = +\infty$ when neither label is bad. A site is a wrong skip at $\lambda$ exactly when $\lambda_E(x) \le \lambda$, so

$$
R_E(\lambda) = N_L^{-1} \, \#\{x \in D_L : \lambda_E(x) \le \lambda\}
$$

is nondecreasing in $\lambda$, and the argument of section 2 applies with $\lambda_E$ in place of the bad-site scores. With $b$ the $(k+1)$-th smallest finite calibration $\lambda_E$, every site with $\lambda_{\mathrm{cov}} < b$ is covered (boundary placement); calibration placement stops at the largest calibration value of $\lambda_{\mathrm{cov}}$ below $b$.

**Claim.** With probability at least $1 - \delta$, $R_E(\hat\lambda) \le \varepsilon$.

The confidence is not split. With a single certificate the policy coincides with section 2. A unit test checks that identity.

Nothing in the argument depends on the quantile form of the path. Any family of threshold pairs that is nondecreasing in $\lambda$ and fixed without calibration labels gives nested wrong-skip sets and the same claim. `priority_path` uses a lexicographic path: the certificates enter in a fixed order, certificate $i$ sweeping its own quantiles over $\lambda \in [i, i+1]$:

$$
\lambda_j(x) = i_j + \hat F_j(S_j(x))
$$

where $i_j$ is the position of certificate $j$ in the order and $\hat F_j$ its empirical distribution function over $D_L$. The shape of the path changes the cost of the claim and leaves the claim itself unchanged.

### 4.3 `ltt_conditional`

Fixed-sequence Learn-then-Test on the conditional rate $P(B = 1 \mid S \le \tau)$, on a label-free grid of level-score quantiles (Angelopoulos et al., 2021). It controls the conditional rate of one certificate at family-wise error $\delta$. At $m = 40$ the grid starts at the 0.55 quantile, so the rule certifies nothing or at least 55% of a level.

### 4.4 Further forms

The three policies above state three different guarantees: one bound per certificate (and their union), one bound on the shared event, and a bound on a conditional rate. Others follow from the same ingredients, frozen scores, a uniform draw and a rule fixed before the labels are seen, and slot in by the contract in `docs/architecture.md`. Examples from the literature that fit the same contract include unequal splits of $\varepsilon$ and $\delta$ between certificates, Pareto Testing on a held-out part of the draw to learn the path [Laufer-Goldshtein et al. 2023], and false-discovery control over the skipped set by conformal selection [Jin & Candès 2023]. Each new form gets the Monte Carlo acceptance check of `accountable.validate` before it carries a claim.

### 4.5 `legacy_sequential` (no guarantee)

The rule of the original IR run: one SSBC-corrected budget, the interest threshold chosen first on the calibration sample, the interpolation threshold chosen on what remains of the same budget, on calibration sites the interest certificate did not cover. Both thresholds are selected from the same labels along a data-dependent route through the two-dimensional threshold plane. The argument of section 2 needs a family fixed in advance, so no claim follows. The policy exists to reproduce the original numbers and is reported with `guarantee = none`.

## 5. Confidence across levels and outputs

Each level is a separate statement at its own confidence, with its own calibration draw. A simultaneous statement over the $J$ certified levels uses Bonferroni,

$$
\delta_{\mathrm{level}} = \delta / J
$$

which can drive the allowed $k$ to $-1$ at small $m$.

**Map certificate.** The calibration labels at level $L+1$ are the errors of the map built through level $L$, so a Clopper–Pearson upper bound at confidence $1 - \delta_{\mathrm{map}}$ bounds the failing fraction of that map on $D_{L+1}$. It shares the draw with the decision at $L+1$; together they hold at confidence $1 - \delta_{\mathrm{map}} - \delta_{\mathrm{decision}}$.

**What is not claimed.** Claims concern the frozen predictor $\hat y_L$. The final map uses the calibration and gated measurements as well. Those depend on the draw, so the final map has no finite-sample claim; it is checked by audit.

## 6. Full spectra and scalar targets

The target map $\varphi$ and the acceptance score $s$ decide what a failure means. The predictor decides how the prediction is formed. Two routes share one set of natural-neighbour weights $W$, which depend only on site positions:

- spectrum route: $\hat y = \varphi(W I)$, interpolating spectra and extracting the target from the prediction;
- scalar route: $\hat y = W \varphi(I)$, interpolating the target directly.

A Gaussian process may replace $W$ as the predictor on either route. With an isotropic squared-exponential kernel $k$ on the design coordinates and a nugget $\nu$ relative to unit output scale, the posterior mean is again linear in the measured data,

$$
\hat y(x) = \bar y + k(x)^\top (K + \nu I)^{-1} (Y - \bar y)
$$

and the posterior standard deviation at unit output scale,

$$
\sigma(x)^2 = k(x, x) - k(x)^\top (K + \nu I)^{-1} k(x)
$$

depends only on positions, length scale and nugget. As an interpolation score it says why a site is measured: it lies far, in units of the length scale, from the measured set. Three length-scale rules are implemented (`accountable.gp`): maximum marginal likelihood on the leading principal-component scores of the measured spectra, one length scale shared by all components (BoTorch); the median nearest-neighbour spacing of the design through the finest level in the measured set, fixed before any measurement; and a Gibbs kernel with local length scale $\ell(x)$ equal to the distance to the third-nearest measured site, clipped to $[s_{\min}, \sqrt{2}/2]$ with $s_{\min}$ the finest design spacing. An interest-driven campaign leaves uninteresting regions sparsely measured, so $\ell$ is long there and short where measurements cluster. The Gibbs kernel in two dimensions,

$$
k(x, x') = \frac{2 \ell(x) \ell(x')}{\ell(x)^2 + \ell(x')^2} \exp\left(-\frac{\lVert x - x' \rVert^2}{\ell(x)^2 + \ell(x')^2}\right)
$$

is positive semidefinite for any positive $\ell$ [Gibbs 1997; Paciorek & Schervish 2004] and reduces to the isotropic kernel for constant $\ell$. Whatever the route, the label is computed from the predictor that would be used at the site, and the guarantee is unchanged. Choosing between the routes affects how many sites are skipped. It does not affect what a skip claims.

## 7. What the design contributes

The hierarchical Poisson-disk design gives each level a covering radius and a minimum spacing. The certificate does not use them. They matter for efficiency: the predictor at level $L$ sees neighbours at distance about $r_{L-1}$, so a fine level is usually well predicted. Exchangeability needs only that calibration be a uniform draw from the level after the scores are frozen.

## Appendix A. The order-statistic bound

Fix a level and certificate, write $N = N_L$, and let $\tau^\ast = \inf\{\tau : R(\tau) > \varepsilon\}$. $R$ is a right-continuous step function, so $R(\tau^\ast) > \varepsilon$ and $K = N R(\tau^\ast) \ge \lfloor \varepsilon N \rfloor + 1$ sites are bad and covered at $\tau^\ast$. If $R(\hat\tau) > \varepsilon$ then $\hat\tau \ge \tau^\ast$. By construction, at most $k$ calibration sites are bad with score at most $\hat\tau$. Those $K$ sites therefore contribute at most $k$ calibration sites. The count $X$ of them in a uniform sample of size $m$ is hypergeometric:

$$
P(R(\hat\tau) > \varepsilon) \le P(X \le k)
$$

$P(X \le k)$ decreases as $K$ grows, so the worst case is $K = \lfloor \varepsilon N \rfloor + 1$. The run records the hypergeometric value at that $K$ next to the binomial value at $\varepsilon$ and checks that $k$ meets both.

## References

- Angelopoulos, Bates, Candès, Jordan, Lei (2021). Learn then Test: calibrating predictive algorithms to achieve risk control. arXiv:2110.01052.
- Bates, Angelopoulos, Lei, Malik, Jordan (2021). Distribution-free, risk-controlling prediction sets. J. ACM 68(6).
- Wilks (1941). Determination of sample sizes for setting tolerance limits. Ann. Math. Stat. 12, 91–96.
- Clopper, Pearson (1934). The use of confidence or fiducial limits illustrated in the case of the binomial. Biometrika 26, 404–413.
- Laufer-Goldshtein, Fisch, Barzilay, Jaakkola (2023). Efficiently controlling multiple risks with Pareto Testing. ICLR. arXiv:2210.07913.
- Jin, Candès (2023). Selection by prediction with conformal p-values. JMLR 24(244), 1–41.
- Gibbs (1997). Bayesian Gaussian processes for regression and classification. PhD thesis, University of Cambridge.
- Paciorek, Schervish (2004). Nonstationary covariance functions for Gaussian process regression. NeurIPS 16.
- Balandat et al. (2020). BoTorch: a framework for efficient Monte-Carlo Bayesian optimization. NeurIPS 33.
