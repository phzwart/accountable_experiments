# 3 Framework (draft 1: sections 3.3 and 3.4)

*Sections 3.1, 3.2 and 3.5 follow the outline in the plan and are still to be drafted. Notation used below: level $L$ with $N_L$ design sites, frozen score $S_j$ per certificate $j$, calibration draw of $m$ sites.*

## 3.1 Design and order of operations

*To draft.* Hierarchical design and seed. Per level: fit and freeze the scores on the measured set, draw the calibration sites, measure them, then decide. Fig. 1.

## 3.2 Labels and certificates

*To draft.* Interest label $Z$ and failure label $F$ defined on the truth. Target map (full spectrum or derived scalar) and acceptance score. Scores order sites and carry no other role.

## 3.3 The assertion

A skip deserves a statement that a measurement could check. At level $L$, certificate $j$ covers the sites whose frozen score lies at or below a threshold $\tau_j$. A covered site is a wrong skip when the claim of the certificate fails there, marked by $B_j(x) = 1$. The controlled quantity is the rate of wrong skips over the level population:

$$
R_j(\tau_j) = N_L^{-1} \, \#\{x \in D_L : S_j(x) \le \tau_j,\ B_j(x) = 1\}
$$

The threshold comes from $m$ sites drawn uniformly from the level after the scores are frozen and then measured. With $k$ the largest integer for which

$$
P(\mathrm{Bin}(m, \varepsilon) \le k) \le \delta
$$

the threshold $\hat\tau_j$ sits just below the $(k+1)$-th failing calibration site in score order. The assertion

$$
P\big(R_j(\hat\tau_j) \le \varepsilon\big) \ge 1 - \delta
$$

holds over the draw, for any score and any predictor [Wilks1941; Bates2021; Angelopoulos2025]. The argument needs only a rate that grows with the threshold and a uniform draw; Appendix A gives it together with the finite-population tail. Allowing no failure in the draw gives the smallest budget that $m$ sites can certify, $\varepsilon_{\min} = 1 - \delta^{1/m}$.

## 3.4 Forms of guarantee

Two claims justify a skip, and an experimenter may need to know how often each fails, how often any skip fails, or how often skips fail when one claim is preferred over the other. Each need calls for its own form of guarantee. All forms rest on the shared wrong-skip event. With covers $A$ and $B$ for the interest and interpolation certificates,

$$
E(x) = \big(A(x) \wedge Z(x)\big) \vee \big(B(x) \wedge F(x)\big)
$$

and $R_E$ is its rate over the level. A site covered by both certificates counts as wrong when either claim fails there.

**Per-claim budgets.** Each certificate is calibrated on its own claim, with budget $\varepsilon_j$ and failure probability $\delta_j$, on one shared draw. A wrong skip fails at least one claim, so $R_E \le R_a + R_b$, and the Bonferroni inequality gives

$$
P\big(R_E \le \varepsilon_a + \varepsilon_b\big) \ge 1 - \delta_a - \delta_b
$$

alongside a separate assertion for each claim. The split leaves each certificate a smaller budget at a higher confidence. Once $\varepsilon_j$ falls below $\varepsilon_{\min}$, no threshold exists and the level is measured in full.

**One budget along a path.** A single budget spends all of $\varepsilon$ and $\delta$ on $R_E$. Two thresholds cannot be read off one draw by an order statistic, and Learn-then-Test supplies the remedy: search a family of thresholds fixed before any label is seen [Angelopoulos2025]. Here the family is a path $\lambda \mapsto (\tau_a(\lambda), \tau_b(\lambda))$, built from the frozen scores alone, along which both thresholds rise. The wrong-skip sets along such a path are nested, $R_E(\lambda)$ grows with $\lambda$, and the rule of Section 3.3 applies with $\lambda$ in place of the threshold (Appendix B). Two paths are used. The quantile path moves both thresholds through matching quantiles of their scores on the level. The priority path admits the claims in a set order: the first claim sweeps its quantiles before the second moves. A preference, for instance to skip a site as uninteresting before relying on interpolation, thereby enters the decision with the assertion intact, because the order is fixed in advance. A rule that sets the second threshold from the labels the first one left over makes the path depend on the draw, and the argument fails; Section 5.2 shows such a rule exceeding its nominal failure rate.

**Further forms.** The forms above share one recipe: scores frozen before the draw, a uniform audit of the level, and a decision rule whose family of thresholds is fixed before the audit labels are known. Any rule built this way inherits a finite-sample assertion, and other needs suggest other rules: unequal budgets for the two claims, a path learned by Pareto Testing on part of the draw [LauferGoldshtein2023], control of the false-skip proportion among skipped sites by conformal selection [Jin2023], or a bound on a conditional rate (Appendix C). Table 3 summarises the forms used in this work. The Supplementary Information (SI 4) lists the conditions a new form must meet and a Monte Carlo acceptance check that every form here passes.

**Table 3.** Forms of guarantee on the wrong-skip event of one level. Every form uses the same frozen scores and the same calibration draw.

| Form | Assertion, with probability at least the stated confidence | Budget | Given up | Suited to |
| --- | --- | --- | --- | --- |
| Per-claim budgets | $R_a \le \varepsilon_a$ and $R_b \le \varepsilon_b$; hence $R_E \le \varepsilon_a + \varepsilon_b$ at $1 - \delta_a - \delta_b$ | Split between the claims | Budget per claim; no threshold once $\varepsilon_j < \varepsilon_{\min}$ | Reporting how often each reason for skipping fails |
| Quantile path | $R_E \le \varepsilon$ at $1 - \delta$ | Whole budget on $R_E$ | Assertion per claim; path shape set in advance | Bounding how often any skip fails |
| Priority path | $R_E \le \varepsilon$ at $1 - \delta$ | Whole budget on $R_E$, spent on the claims in order | Assertion per claim; a later claim may receive no budget | A set preference between the claims |
| Conditional rate (Appendix C) | Failure rate among sites skipped by one claim $\le \alpha$ at $1 - \delta$ | One claim | Coverage at small $m$: at $m = 40$ it certifies nothing or more than half a level | Large calibration samples |

## 3.5 What is claimed and what is checked

*To draft.* Claims: design sites of a level, frozen predictor, probability over the draw. Checks: remainder rates, map bound, off-design audit, final map.

---

## Notes for revision (not part of the text)

- Results from Section 5.2 stay out of this section; the IR infeasibility appears here only as a property of the split ($\varepsilon_j < \varepsilon_{\min}$).
- References added here: [Wilks1941], [Bates2021], [Jin2023]. Bibliographic details are in the plan's reference map; Wilks and Bates still need a check.
- "Certificate" and "claim" are used side by side: a certificate is the mechanism, a claim is what it asserts about a site. Check that the distinction holds in 3.2 when it is drafted.
