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

Step 5 is the action of the level: one decision, taken after the draw, on which of its sites are measured and which are skipped, and under which claim. The decision covers every site of the level at once, so the order in which the sites are then measured is free. The plan, together with the rule that decides each of its levels, is guaranteed to keep the budget of the specification on every level, at most a fraction ε of the sites skipped under a false claim, with probability at least c over its calibration draws; the failure probability 1 − c is divided among the levels when the plan is declared. Each action has its bound, and the record gives every site its reason.

**Figure 2.** The workflow. (a) Hierarchical design of the IR map: levels 0–2 form the seed, and each finer level fills the gaps of the coarser ones. (b) The five steps on one level; the calibration draw is the only random element of the guarantee, and its labels are unseen until the rule is frozen. (c) The two claims: a skipped site is covered as not of interest ($A$), as predictable ($B$) or both, and the skip is wrong when a covering claim is false. The guarantee bounds the share of level-$L$ sites at which the shared event $E$ occurs. File: `figures/fig1_schematic.png`.

Non-anticipation ties the steps together: nothing that shapes the guarantee on a level may depend on that level's draw, except through the rule fixed in step 2. Three practices that look harmless break it, and Section 5.1 shows each failing: refitting the scores on the calibration labels before the threshold is set, taking the calibration sample where the model is least sure, and keeping the most favourable of several draws. The condition concerns the draw and the rule. A score may use anything known before the draw, including physical models, other datasets or prior beliefs; a poor score costs measurements and leaves the guarantee intact.

Measuring one site must also leave the outcome of every other site unchanged. Radiation damage that spreads beyond the probed spot, or sample drift triggered by the measurement order, would let the draw alter the population it is meant to sample.

Given everything that precedes the draw of a level, its population, scores, labels and rule are fixed, so the guarantee holds conditionally on the history of the campaign and adaptivity across levels leaves it intact. Statements about several levels follow from the union bound; Appendix A states the conditions formally.

## 3.2 Claims and labels

A skip is useful only if it says something that a measurement could contradict. Two claims serve that purpose. The interest claim states that a site holds nothing of interest; its label $Z(x) = 1$ marks a site whose measured spectrum meets the interest criterion of the dataset, such as a diffraction line standing clear of the noise. The interpolation claim states that a site is predictable; its label $F(x) = 1$ marks a site where the prediction from the coarser levels misses the acceptance metric. The metric fixes what predictable means: agreement of the full spectrum within an envelope, or agreement of a quantity derived from it, such as a peak position or width, within a tolerance. Both labels are functions of the true spectrum, the one a single measurement returns, and of the frozen predictor. In a campaign they are known only at measured sites, and for this study they are known everywhere.

Each claim carries a score that orders the sites of a level from most to least safe to skip. The score has no other role: any function of the data available before the draw may serve, and its quality decides the number of measurements spent. The choice of metric decides more, since it sets where predictions fail and therefore where the campaign measures (Section 5.5).

## 3.3 The guarantee

A skip deserves a statement that a measurement could check. At level $L$, claim $j$ covers the sites whose frozen score lies at or below a threshold $\tau_j$. A covered site is a skip error when the claim fails there, marked by $B_j(x) = 1$. The controlled quantity is the rate of skip errors over the level population:

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

holds over the draw, for any score and any predictor [Wilks1941; Bates2021; Angelopoulos2025]. In words, the share of the level skipped in error is at most ε at least a fraction 1 − δ of the time, over repeated calibration draws on the same frozen model: a PAC guarantee [Valiant1984; Park2020], and training-conditional in the terms of [VovkCond2013], since it concerns the share realised after the draw actually taken. The argument needs only a rate that grows with the threshold and a uniform draw; Appendix A gives it. The attained value $\delta_L = P(H \le k)$, at most $\delta$, is the failure probability the level carries, its picked failure probability. On a level of 399 sites with $m = 40$ and $\varepsilon = 0.10$, a level just over budget holds 40 failing sites; at $\delta = 0.25$ the rule allows $k = 2$ failing calibration sites, stops at the third, and carries $\delta_L = 0.206$. The statement concerns one level; all guaranteed levels of a campaign hold together with probability at least $1 - \sum_L \delta_L$, the sum running over every guaranteed level (Appendix A). A plan guaranteed at campaign confidence $c$ therefore sets $\delta = (1 - c)/n$ on each of its $n$ guaranteed levels. Allowing no failure in the draw gives, in the binomial approximation, the smallest budget that $m$ sites can support, $\varepsilon_{\min} = 1 - \delta^{1/m}$.

## 3.4 Forms of guarantee

Two claims can share one budget in several ways, and all rest on the shared skip-error event, a skip under a claim that fails at the site. With covers $A_Z$ and $A_F$ for the interest and interpolation claims,

$$
E(x) = \big(A_Z(x) \wedge Z(x)\big) \vee \big(A_F(x) \wedge F(x)\big)
$$

and $R_E$ is its rate over the level; a site covered by both claims counts as wrong when either claim fails there. The campaigns of Section 5 spend the whole budget on $R_E$ along the matched-quantile rule, which raises both thresholds through matching quantiles of their scores on the level. Two thresholds cannot be read off one draw by an order statistic, so the path is built from the frozen scores before any label is seen and searched as in Learn-then-Test [Angelopoulos2025]; the skip-error sets along it are nested, and the rule of Section 3.3 applies (Appendix B). Budgets per claim, a set priority between the claims and a bound on a conditional rate follow from the same ingredients (SI 4.5; Appendix C). A label-conditional statement protects the sites of interest: the calibration sites of interest are a uniform draw from those of the level, and the rule of Section 3.3, with the worst case over their unknown total, limits the share of them skipped under the no-interest claim [Vovk2005; Sadinle2019; Tong2018]. It bounds a share, per level, and holds together with the shared bound on the same draw with probability at least $1 - \delta_L - \delta_Z$ (Appendix B.3).

## 3.5 What is claimed and what is checked

A reader of the record needs to know what each guarantee covers:

- **Per level, and per plan.** Each bound concerns the design sites of one level and holds with probability $1 - \delta_L$ over that level's draw; a plan guaranteed for all levels together keeps the budget on every level with the confidence of the specification.
- **Share of the level.** The share counts every site of the level, measured or skipped; the share of skipped sites that are wrong is larger and is reported beside it (Table 3).
- **Count, not place.** The bound limits how many skips fail and leaves their location open; skip errors can gather, and when sites of interest are rare a level can meet its budget while losing many of them (Section 5.5).
- **Design sites only.** Nothing is claimed between design sites, and a map drawn afterwards from all measurements carries a statement only through the audit of Section 3.6.
- **One measurement as truth.** A label compares the prediction with what a single measurement returns, noise included, so a tolerance has to lie above the precision of the measured quantity; a tolerance close to the variation between neighbouring sites makes many predictions fail whatever the model.

Two further statements accompany each level. The rate of skip errors among the sites left after calibration, the remainder, follows from the same draw (Appendix C), and the calibration labels also bound the share of the level that the map from coarser levels predicts outside tolerance (SI 9).

Each site of an action carries its reason. A site was measured because the plan placed it in the seed, the draw placed it in the calibration sample, or no claim covered it under the thresholds frozen for its level, and it was skipped under the claim that covered it. The reasons are exact, fixed at the time of decision and replayable; a measured site that hindsight finds predictable counts as a cost of the guarantee.

## 3.6 An audit of the finished map

A campaign ends with a map, and the map needs a statement of its own. After the last level, an audit sample drawn uniformly from the skipped sites is measured and kept out of the map. Its failures bound, through the exact hypergeometric limit of SI 9, how many skipped sites the map predicts outside tolerance. The bound covers every skipped site of the run at one confidence, provided the map, its interpolator and any strata are fixed before the draw; measured sites are taken as correct, so drift carried by the measurements escapes it, and the absence of drift has to hold until the audit is measured. Strata fixed before the draw give one bound each, combined by splitting the confidence among them. With no failure among $n_a$ audit sites the bound on the share is about $1 - (1 - c)^{1/n_a}$, 1.6 % for 100 sites at confidence 0.80. The audit is terminal: measuring more and auditing again needs a fresh sample and a split confidence, or a sequential bound [WaudbySmith2020]. Audit sites may join the delivered map afterwards, and the bound then refers to the map without them. Design-based accuracy assessment of land-cover maps rests on the same probability sample [Olofsson2014]; weighting the audit by a model's predicted failures, as in active testing [Kossen2021] or prediction-powered inference [AngelopoulosPPI2023], could tighten the bound.

---

## Notes for revision (not part of the text)

- Results from Section 5.2 stay out of this section; the IR infeasibility appears here only as a property of the split ($\varepsilon_j < \varepsilon_{\min}$).
- References added here: [Wilks1941], [Bates2021], [Jin2023], [Neyman1934] (Neyman 1934, J. R. Stat. Soc. 97, 558–625, on the representative method; check), [Cochran1977] (Cochran, Sampling Techniques, 3rd ed., Wiley; check).
- Fig. 1 drawn (figures/fig1_schematic.png). Bibliographic details are in the plan's reference map; Wilks and Bates still need a check.
- "Certificate" and "claim": distinction stated in 3.2.
- Reference to add: [ClopperPearson1934] Clopper, Pearson (1934), Biometrika 26, 404–413.
