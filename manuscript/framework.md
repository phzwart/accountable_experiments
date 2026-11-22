# 3 Framework (draft 1)

*Notation: level $L$ with $N_L$ design sites, frozen score $S_j$ per claim $j$, calibration draw of $m$ sites.*

## 3.1 Design and order of operations

An experiment declares before it starts the most it will measure and the finest detail it seeks. The plan, the design sites it would measure if none could be skipped, carries both: its finest spacing sets the resolution of the final map, and its sites bound the measurements. The same plan serves the guarantee. A finite-sample guarantee about skipped sites needs a calibration sample that is exchangeable with the sites it speaks for [Vovk2005]. Here the design creates that exchangeability. The population of every level is fixed before its calibration draw, and a uniform random draw from that population is the only source of randomness the guarantee relies on, as in design-based survey inference [Neyman1934; Cochran1977]. The guarantee needs no model of the spatial field or of the noise.

Here a hierarchical Poisson-disk design [Bridson2007] lays out the plan in nested levels of increasing density. Any plan whose levels are fixed before their draws would serve the guarantee equally: a grid, independent uniform points, or a level drawn up from the sites already measured, such as the neighbourhood of sites found interesting. The hierarchy serves image formation: the sites up to any depth contain every coarser depth and form an evenly spread design at that resolution, so each map builds on the coarser maps and interpolation has well-placed support. Nesting and spread set the cost of a guarantee and play no part in its validity. Each completed level also yields a map at the spacing of its sites, in which every site is measured or predicted under a claim bounded on its level; a display map can be drawn afterwards with any interpolator. The coarsest levels form the seed and are measured in full. Each finer level is then processed once, in order, in five steps (Fig. 2):

1. *Fit.* The predictor and the scores are fitted on the sites measured so far.
2. *Freeze.* Scores and predictor are fixed for every site of the level, and so is the decision rule: the family of thresholds, the budget and its split, and the number of calibration failures the level may allow.
3. *Draw.* A calibration sample of $m$ sites is drawn uniformly without replacement from the level, with randomness independent of everything else.
4. *Calibrate.* The calibration sites are measured, their labels are evaluated against the frozen predictor, and the rule turns the labels into thresholds.
5. *Decide.* Covered sites of the remainder are skipped and the others measured; every measured site joins the measured set for the next level.

Step 5 is the action of the level: one decision, taken after the draw, on which of its sites are measured and which are skipped, and under which claim. The decision covers every site of the level at once, so the order in which the sites are then measured is free. The plan, together with the rule that decides each of its levels, is certified to keep the budget of the contract on every level, at most a fraction ε of the sites skipped under a false claim, with probability at least c over its calibration draws; the failure probability 1 − c is divided among the levels when the plan is declared. Each action has its bound, and the record gives every site its reason.

**Figure 2.** The workflow. (a) Hierarchical design of the IR map: levels 0–2 form the seed, and each finer level fills the gaps of the coarser ones. (b) The five steps on one level; the calibration draw is the only random element of the guarantee, and its labels are unseen until the rule is frozen. (c) The two claims: a skipped site is covered as not of interest ($A$), as predictable ($B$) or both, and the skip is wrong when a covering claim is false. The guarantee bounds the share of level-$L$ sites at which the shared event $E$ occurs. File: `figures/fig1_schematic.png`.

Non-anticipation ties the steps together: nothing that shapes the guarantee on a level may depend on that level's draw, except through the rule fixed in step 2. Three practices that look harmless break it, and Section 5.1 shows each failing: refitting the scores on the calibration labels before the threshold is set, taking the calibration sample where the model is least sure, and keeping the most favourable of several draws. The condition concerns the draw and the rule. A score may use anything known before the draw, including physical models, other datasets or prior beliefs; a poor score costs measurements and leaves the guarantee intact.

Measuring one site must also leave the outcome of every other site unchanged. Radiation damage that spreads beyond the probed spot, or sample drift triggered by the measurement order, would let the draw alter the population it is meant to sample.

Given everything that precedes the draw of a level, its population, scores, labels and rule are fixed, so the guarantee holds conditionally on the history of the campaign and adaptivity across levels leaves it intact. Statements about several levels follow from the union bound; Appendix A states the conditions formally.

## 3.2 Claims and labels

A skip is useful only if it says something that a measurement could contradict. Two claims serve that purpose. The interest claim states that a site holds nothing of interest; its label $Z(x) = 1$ marks a site whose measured spectrum meets the interest criterion of the dataset, such as a diffraction line standing clear of the noise. The interpolation claim states that a site is predictable; its label $F(x) = 1$ marks a site where the prediction from the coarser levels misses the acceptance metric. The metric fixes what predictable means: agreement of the full spectrum within an envelope, or agreement of a quantity derived from it, such as a peak position or width, within a tolerance. Both labels are functions of the true spectrum, the one a single measurement returns, and of the frozen predictor. In a campaign they are known only at measured sites, and for this study they are known everywhere.

Each claim carries a score that orders the sites of a level from most to least safe to skip. The score has no other role: any function of the data available before the draw may serve, and its quality decides the number of measurements spent. The choice of metric decides more, since it sets where predictions fail and therefore where the campaign measures (Section 5.5).

## 3.3 The guarantee

A skip deserves a statement that a measurement could check. At level $L$, claim $j$ covers the sites whose frozen score lies at or below a threshold $\tau_j$. A covered site is a wrong skip when the claim fails there, marked by $B_j(x) = 1$. The controlled quantity is the rate of wrong skips over the level population:

$$
R_j(\tau_j) = N_L^{-1} \, \lvert \{x \in D_L : S_j(x) \le \tau_j,\ B_j(x) = 1\} \rvert
$$

The threshold comes from $m$ sites drawn uniformly, without replacement, from the level after the scores are frozen and then measured. Let $H$ count the failing sites in such a draw from a level in which $\lfloor \varepsilon N_L \rfloor + 1$ sites fail. With $k$ the largest integer for which

$$
P(H \le k) \le \delta
$$

every site scored below the $(k+1)$-th failing calibration site is covered. The guarantee

$$
P\big(R_j(\hat\tau_j) \le \varepsilon\big) \ge 1 - \delta
$$

holds over the draw, for any score and any predictor [Wilks1941; Bates2021; Angelopoulos2025]. The argument needs only a rate that grows with the threshold and a uniform draw; Appendix A gives it. The attained value $\delta_L = P(H \le k)$, at most $\delta$, is the failure probability the level carries, its picked failure probability. On a level of 399 sites with $m = 40$ and $\varepsilon = 0.10$, a level just over budget holds 40 failing sites; at $\delta = 0.25$ the rule allows $k = 2$ failing calibration sites, stops at the third, and carries $\delta_L = 0.206$. The statement concerns one level; all certified levels of a campaign hold together with probability at least $1 - \sum_L \delta_L$, the sum running over every certified level (Appendix A). A plan certified at campaign confidence $c$ therefore sets $\delta = (1 - c)/n$ on each of its $n$ certified levels. Allowing no failure in the draw gives, in the binomial approximation, the smallest budget that $m$ sites can certify, $\varepsilon_{\min} = 1 - \delta^{1/m}$.

## 3.4 Forms of guarantee

The rate a campaign must control depends on the question: wrong skips per claim, wrong skips overall, or wrong skips with one claim preferred. All forms rest on the shared wrong-skip event. With covers $A_Z$ and $A_F$ for the interest and interpolation claims,

$$
E(x) = \big(A_Z(x) \wedge Z(x)\big) \vee \big(A_F(x) \wedge F(x)\big)
$$

and $R_E$ is its rate over the level. A site covered by both claims counts as wrong when either claim fails there.

**Per-claim budgets.** Each claim is calibrated on its own, with budget $\varepsilon_j$ and failure probability $\delta_j$, on one shared draw. A wrong skip fails at least one claim, so $R_E \le R_a + R_b$, and the Bonferroni inequality gives

$$
P\big(R_E \le \varepsilon_a + \varepsilon_b\big) \ge 1 - \delta_a - \delta_b
$$

alongside a separate guarantee for each claim. The split leaves each claim a smaller budget at a higher confidence. Once $\varepsilon_j$ falls below $\varepsilon_{\min}$, no threshold exists and the level is measured in full.

**One budget along a path.** A single budget spends all of $\varepsilon$ and $\delta$ on $R_E$. Two thresholds cannot be read off one draw by an order statistic, and Learn-then-Test supplies the remedy: search a family of thresholds fixed before any label is seen [Angelopoulos2025]. Here the family is a path $\lambda \mapsto (\tau_a(\lambda), \tau_b(\lambda))$, built from the frozen scores alone, along which both thresholds rise. The wrong-skip sets along such a path are nested, $R_E(\lambda)$ grows with $\lambda$, and the rule of Section 3.3 applies with $\lambda$ in place of the threshold (Appendix B). Two paths are used. The quantile path moves both thresholds through matching quantiles of their scores on the level. The priority path admits the claims in a set order: the first claim sweeps its quantiles before the second moves. A preference between the claims thereby enters the decision with the guarantee intact.

**Further forms.** Any rule built from scores frozen before the draw, a uniform calibration draw and a family of thresholds fixed before the labels are known inherits a finite-sample guarantee, including a bound on a conditional rate (Appendix C). Table 1 summarises the forms; SI 4 gives the Monte Carlo acceptance check every form here passes.

**Table 1.** Forms of guarantee on the wrong-skip event of one level. Every form uses the same frozen scores and the same calibration draw.

| Form | Guarantee, with probability at least the stated confidence | Budget | Given up | Suited to |
| --- | --- | --- | --- | --- |
| Per-claim budgets | $R_a \le \varepsilon_a$ and $R_b \le \varepsilon_b$; hence $R_E \le \varepsilon_a + \varepsilon_b$ at $1 - \delta_a - \delta_b$ | Split between the claims | Budget per claim; no threshold once $\varepsilon_j < \varepsilon_{\min}$ | Reporting how often each reason for skipping fails |
| Quantile path | $R_E \le \varepsilon$ at $1 - \delta$ | Whole budget on $R_E$ | Guarantee per claim; path shape set in advance | Bounding how often any skip fails |
| Priority path | $R_E \le \varepsilon$ at $1 - \delta$ | Whole budget on $R_E$, spent on the claims in order | Guarantee per claim; a later claim may receive no budget | A set preference between the claims |
| Conditional rate (Appendix C) | Failure rate among sites skipped by one claim $\le \alpha$ at $1 - \delta$ | One claim | Coverage at small $m$: at $m = 40$ it certifies nothing or more than half a level | Large calibration samples |

## 3.5 What is claimed and what is checked

A reader of the record needs to know what each guarantee covers:

- **Per level, and per plan.** Each bound concerns the design sites of one level and holds with probability $1 - \delta_L$ over that level's draw; a plan certified for all levels together keeps the budget on every level with the confidence of the contract.
- **Share of the level.** The share counts every site of the level, measured or skipped; the share of skipped sites that are wrong is larger and is reported beside it (Table 4).
- **Count, not place.** The bound limits how many skips fail and leaves their location open; wrong skips can gather, and when sites of interest are rare a level can meet its budget while losing many of them (Section 5.5).
- **Design sites only.** Nothing is claimed between design sites or for a display map drawn afterwards from all measurements.
- **One measurement as truth.** A label compares the prediction with what a single measurement returns, noise included, so a tolerance close to the measurement scatter makes many predictions fail whatever the model.

Two further statements accompany each level. The rate of wrong skips among the sites left after calibration, the remainder, follows from the same draw (Appendix C), and the calibration labels also bound the share of the level that the map from coarser levels predicts outside tolerance (SI 9).

Each site of an action carries its reason. A site was measured because the plan placed it in the seed, the draw placed it in the calibration sample, or no claim covered it under the thresholds frozen for its level, and it was skipped under the claim that covered it. The reasons are exact, fixed at the time of decision and replayable; a measured site that hindsight finds predictable counts as a cost of the guarantee.

---

## Notes for revision (not part of the text)

- Results from Section 5.2 stay out of this section; the IR infeasibility appears here only as a property of the split ($\varepsilon_j < \varepsilon_{\min}$).
- References added here: [Wilks1941], [Bates2021], [Jin2023], [Neyman1934] (Neyman 1934, J. R. Stat. Soc. 97, 558–625, on the representative method; check), [Cochran1977] (Cochran, Sampling Techniques, 3rd ed., Wiley; check).
- Fig. 1 drawn (figures/fig1_schematic.png). Bibliographic details are in the plan's reference map; Wilks and Bates still need a check.
- "Certificate" and "claim": distinction stated in 3.2.
- Reference to add: [ClopperPearson1934] Clopper, Pearson (1934), Biometrika 26, 404–413.
