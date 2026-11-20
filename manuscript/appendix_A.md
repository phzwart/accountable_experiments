# Appendix A. Exchangeability by design and the single-certificate bound (draft 1)

## A.1 Conditions

A campaign processes the levels $L = L_s + 1, L_s + 2, \dots$ of a hierarchical design in order. Write $\mathcal{F}_{L-1}$ for everything known before the calibration draw of level $L$: the design, the sites measured so far and their spectra, all earlier calibration draws, and any auxiliary randomness used by the scores. The truth $y(x)$ at every design site is fixed; for a live experiment, $y(x)$ is the outcome a measurement of $x$ would return.

The order of operations of Section 3.1 amounts to six conditions.

- **(A1) Fixed population.** The level population $D_L$, of size $N_L$, is determined by $\mathcal{F}_{L-1}$. In this work it is fixed by the design before the experiment.
- **(A2) Frozen scores and predictor.** The scores $S_j$ and the predictor $\hat y_L$ on $D_L$ are determined by $\mathcal{F}_{L-1}$.
- **(A3) Labels.** Each bad label $B_j(x)$, $x \in D_L$, is a fixed function of the truth and of $\hat y_L$, so the labels of the whole level are determined given $\mathcal{F}_{L-1}$, whether or not a site is drawn.
- **(A4) Fixed rule.** The family of covers searched (thresholds on one score, a path, a split of the budget), the budget $\varepsilon$, the failure probability $\delta$, the sample size $m$ and the allowed number of failures $k$ are determined by $\mathcal{F}_{L-1}$.
- **(A5) Uniform draw.** Given $\mathcal{F}_{L-1}$, the calibration sample $C_L$ is uniform over the $m$-subsets of $D_L$.
- **(A6) No interference.** Measuring a site of $C_L$ leaves the truth at every other site unchanged.

Under (A1)–(A6), the level population with its scores and labels is a fixed finite population given $\mathcal{F}_{L-1}$, and $C_L$ is a simple random sample from it. Exchangeability of the calibration sites with the population is then a property of the draw [Vovk2005], and the bound below is a design-based statement [Neyman1934; Cochran1977]: its only probability is that of the draw. The scores may depend on anything in $\mathcal{F}_{L-1}$, including the truth itself through an oracle; such a score changes the cost and leaves the bound intact.

## A.2 The bound

Fix a level and a certificate with score $S$ and bad label $B$, and drop the indices. The joint rate at threshold $\tau$ is

$$
R(\tau) = N^{-1} \, \lvert \{x \in D : S(x) \le \tau,\ B(x) = 1\} \rvert
$$

which is nondecreasing and right-continuous in $\tau$. Let $H$ be hypergeometric with population $N$, $\lfloor \varepsilon N \rfloor + 1$ marked sites and $m$ draws, and let $k$ be the largest integer with $P(H \le k) \le \delta$. Let $b$ be the $(k+1)$-th smallest score among the calibration sites with $B = 1$. The rule covers every site with $S < b$; every site when $C$ holds at most $k$ bad sites; no site when $k < 0$.

**Proposition A.1.** Under (A1)–(A6),

$$
P\big(R(\hat\tau) > \varepsilon \mid \mathcal{F}_{L-1}\big) \le \delta_L = P(H \le k) \le \delta
$$

where $\hat\tau$ is any threshold below $b$ that covers the same sites.

*Proof.* Condition on $\mathcal{F}_{L-1}$; by (A1)–(A4) the population, scores, labels and $k$ are fixed. Let $\tau^\ast = \inf\{\tau : R(\tau) > \varepsilon\}$ and $K = \{x : S(x) \le \tau^\ast,\ B(x) = 1\}$. By right-continuity $|K| \ge \lfloor \varepsilon N \rfloor + 1$, and $K$ does not depend on the draw. If $R(\hat\tau) > \varepsilon$, then $\hat\tau \ge \tau^\ast$, so every site of $K$ has a score below $b$. By construction at most $k$ bad calibration sites have a score below $b$, hence $|C \cap K| \le k$. By (A5) and (A6), $|C \cap K|$ is hypergeometric with $|K|$ marked sites, and its lower tail decreases in $|K|$:

$$
P\big(R(\hat\tau) > \varepsilon \mid \mathcal{F}_{L-1}\big) \le P\big(|C \cap K| \le k\big) \le P(H \le k)
$$

$\square$

The argument is the one-sided tolerance bound of Wilks (1941) in the form used for risk control [Bates2021; Angelopoulos2025], with the exact finite-population tail in place of its binomial approximation. The binomial $k$, the largest with $P(\mathrm{Bin}(m, \varepsilon) \le k) \le \delta$, is never larger and gives a valid, more conservative rule.

**The picked level.** $\delta_L = P(H \le k)$ takes values on a grid indexed by $k$ and set by $m$, $N_L$ and $\varepsilon$. The rule picks the largest grid point at or below $\delta$, and $\delta_L$ is the failure probability the level asserts. Equality in Proposition A.1 holds when exactly $\lfloor \varepsilon N \rfloor + 1$ bad sites lie at or below $\tau^\ast$; Appendix B.5 describes the randomised rule that reaches $\delta$ itself.

**Several levels.** Taking expectations over $\mathcal{F}_{L-1}$ gives the unconditional bound on each level. For a statement about all certified levels at once, $P(\exists L : R_L > \varepsilon) \le \sum_L \delta_L$.

## A.3 What breaks the conditions

Each of the following lets the draw of a level shape the rule it is meant to test.

- *Refitting on calibration labels* (breaks A2, A4). Scores updated with the calibration labels after the draw and then thresholded on the same labels. In the Monte Carlo of Section 5.1 the bound was exceeded in every draw.
- *Choosing the calibration sites* (breaks A5). Calibrating where the scores are least sure, as an active learner would, makes the sample unrepresentative of the sites it speaks for.
- *Keeping the most favourable of several draws* (breaks A5). The retained sample is selected by its outcome.
- *Measurement-induced change* (breaks A6). Damage or drift caused by measuring the calibration sites alters the truth at their neighbours.

The sequential rule of Section 5.2 breaks (A4) in a subtler way: its second threshold is searched over a family that depends on the labels the first threshold left uncovered.

---

## Notes for revision (not part of the text)

- (A6) is a no-interference condition in the sense of causal inference. Beam damage is the realistic threat for the scattering experiments; one sentence in the Discussion should say how to check it (re-measure a few sites at the end).
- The conditional statement makes the guarantee robust to any adaptivity across levels. This is the property that lets the campaign be adaptive and still certified; it may deserve a sentence in the Introduction.
- References: [Neyman1934], [Cochran1977], [Vovk2005] to verify.
