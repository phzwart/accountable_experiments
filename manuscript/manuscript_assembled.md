# Abstract

*Working title: Accountable experiments: autonomy under contract*

Autonomous experiments decide where to measure, and every site they leave out enters the result as a prediction. An accountable experiment certifies every action, the decision on each level of which sites to measure and which to skip under a stated claim. The campaign runs under a contract fixed before it starts: a plan of sites at the finest resolution sought, the claims that justify a skip, a tolerance, an error budget and a confidence. A skip is made under one of two claims: the site holds nothing of interest, or its signal, or a quantity derived from it, can be predicted within tolerance from coarser measurements. Each level of the plan is set before its calibration draw, and a uniform draw from the level, taken after the model is frozen, bounds at the stated confidence the share of the level's sites skipped under a false claim, whatever the model. The statistics are standard; the contribution is posing the experiment so that they apply inside a closed loop. On three fully measured datasets, an infrared map, a NaCl microdiffraction scan and a synthetic scattering phase map, levels exceeded their budget no more often than the stated confidence permits; plans certified for all levels together kept their budget on every level in at least 90 % of campaigns, at 13 % to 41 % more measurements than plans certified level by level. A held-out audit after the last level bounds the error of the finished map for any campaign, and a bound conditional on interest cut the sites of interest lost from 35 % to 9 % where such sites were rare. Trusting its own uncertainty, a Gaussian process skipped no site of the synthetic map under a full-profile claim, where the certified plan skipped more than half under a bound that held, and a rate it stated could be right or too low with nothing in the run to tell which. The model and its scores set only the cost of a guarantee, and every decision can be replayed from the record.


# 1 Introduction

Autonomous decision engines are becoming routine in experimentation. At synchrotron beamlines, Gaussian-process surrogates choose the next sample position or composition, and measurement, analysis and decision run as one closed loop [Noack2019; Noack2020; Yager2023]. Self-driving laboratories search formulation and composition spaces in the same way [Burger2020; Nazeri2026], and an autonomous laboratory synthesised 41 of 58 target inorganic compounds in 17 days [Szymanski2023]. Probabilistic models recommend which strains to build next [Radivojevic2020], and laboratory automation keeps lowering the cost of handing experimental choices to machines [Tom2024].

Each decision to measure is also a decision to leave something unmeasured. Beam time, dose, reagents and sample lifetime are limited, and the sites left out of a map still enter it, as predictions. A closed-loop scattering study recently mapped the phases of a ternary polymer blend from 65 of 5151 grid compositions, so that 98.7 % of the map is prediction [Upreti2026]. As such decisions move from people to models, accountability becomes a requirement. Guidance on AI risk asks for traceable decisions and documented responsibility [NIST2023], regulation of high-risk systems requires automatic records of their operation [EU2024, Art. 12], and audit frameworks ask for evidence that can be checked against stated expectations [Raji2020]. For a measurement campaign the consequential decision is the skip, and the expectation to check is how often skips are wrong.

A surrogate model offers a rate of its own: its uncertainty states how likely each skip is to be wrong. The statement is the model's about itself, and only the measurements it avoids could check it. Figure 1 follows a campaign guided by Gaussian-process uncertainty on a fully measured synthetic phase map, with a claim on the full scattering profile. Skipping a site only when its own probability of a wrong skip was at most 0.10, the process judged no site safe and measured all 2118; a certified plan measured 932 on average and kept its budget of 0.10 per level. Rescaled to its leave-one-out residuals, the process skipped some sites and stated a smaller share wrong than it realised (Fig. 1c). Only sites the model did not choose could show which statement held.

**Figure 1.** Two campaigns on one fully measured synthetic phase map, 2118 design sites, with the claim that the full scattering profile at a site can be predicted within 0.5 % + 0.005 on average over its 240 points. (a) A plan of average cost certified level by level: at most 10 % of each level skipped wrongly, with confidence 0.80 for that level. (b) A campaign guided by the Gaussian process of Section 4.3, refitted after each level, skipping a site when its own probability of a wrong skip is at most α = 0.10, from the predictive standard deviation (SI 7); it judged no site safe to skip. Crosses mark wrong skips, found afterwards against the full map; lines mark the phase boundaries of the forward model. (c) Share of the certified-level sites skipped wrongly: stated in advance (bar) and realised (dot), with sites measured. For the Gaussian process the statement is its own probability of a wrong skip summed over its skips, at three values of α, rescaled to its leave-one-out residuals at α = 0.10, and on the NaCl scan of Section 5.2; for the certified plans it is the bound, with the mean and 5–95 % range of 250 campaigns. File: `figures/fig_hook_three.png`.

A rate that can be checked needs claims that a measurement would settle. Two reasons justify a skip: the site holds nothing of interest, or its signal, or a quantity derived from it, can be predicted within tolerance from the sites already measured. Each reason is a claim about the site, and a wrong skip is a site covered by a false claim. Posed this way, skips come within reach of distribution-free risk control, which bounds the population rate of a chosen loss from a held-out sample for any predictor, with exchangeability of the calibration data as the only assumption [Vovk2005; Bates2021; Angelopoulos2023; Angelopoulos2025]. Related constructions appear in imaging and power-grid screening (Section 2). A campaign strains that assumption, since every decision changes the data that calibrate the next.

This paper builds an accountable experiment for mapping campaigns, one that certifies every action. Any experiment declares in advance the most it will measure and the finest detail it seeks. The plan turns both into sites: those the experiment would measure if none could be skipped, at the finest spacing sought, and with them the sites for which every action is accounted. The campaign runs under a contract fixed before it starts: the claims, the tolerance that makes a prediction correct, an error budget ε and a confidence c. The plan is divided into levels, and the coarsest levels are measured in full. At each finer level, a model fitted to the measured sites proposes which sites to skip, a uniform random sample of the level is measured for calibration, and its labels set how far the skips may go. The decision on a level is one action, taken after its draw for all of its sites at once: these are measured, these are skipped, each under its claim. The plan is certified to keep the budget, at most a fraction ε of every level skipped under a false claim, with probability at least c over its calibration draws. It holds for any predictor and any score that respect the order fit, freeze, draw, calibrate, decide; the model decides only how many measurements the guarantee costs. A plan may also be drawn up level by level within the declared limit, each level set from what was measured before its draw; this study declares the plan in full. A nested, space-filling design [Bridson2007] declared at the start serves image formation at every resolution.

The contributions are three. The first poses a mapping campaign as an accountable experiment: skips as claims a measurement would settle, a contract fixed in advance, a record from which every decision can be replayed, and guarantees of three forms built from existing risk-control results [Angelopoulos2025; LauferGoldshtein2023]. The statistics are standard; the contribution is posing the experiment so that they apply. The second states the conditions that keep the guarantee valid inside the closed loop, a plan whose levels are set before their draws and an order of operations that forbids anticipation, and tests what breaking them does. The third is evidence on three fully measured datasets, an infrared map of a bioreef sample, a NaCl microdiffraction scan [ALSNaCl] and a synthetic small-angle scattering phase map: levels exceeded their budgets no more often than the confidence permits, the model set the cost, the claim decided where measurements and wrong skips fell, and the same model trusted on its own uncertainty stated a rate that was sometimes right and sometimes three to ten times too low.



# 2 Related work

**Adaptive mapping.** Scanning instruments spend most of their time on sites that add little to the final map, and adaptive acquisition puts that time where the map is uncertain or interesting. Gaussian-process regression drives autonomous small-angle scattering and diffraction mapping at synchrotron and neutron facilities [Noack2019; Noack2020; Noack2021], and steers robotic formulation of polymer blends through their scattering peak ratios [Upreti2026]. Bayesian active learning maps phase diagrams of composition spreads on the fly at the beamline [Kusne2020]. Dynamic sampling selects each new pixel of a point-wise image by the expected reduction in distortion and stops once an estimated distortion is reached [Godaliyadda2018]. Scanning probe and electron microscopes run comparable loops of measurement, model update and choice of the next location [Kalinin2021; Ziatdinov2022]. These methods judge the sites they leave out through the model that chose them.

**Distribution-free risk control.** Distribution-free inference attaches finite-sample statements to the output of an arbitrary predictor, with exchangeability of the calibration data as the only assumption [Vovk2005; Angelopoulos2023]. Risk-controlling prediction sets bound the population rate of a chosen loss from a held-out sample [Bates2021], Learn-then-Test extends the bound to any family of decision rules searched in a fixed order or with a multiple-testing correction [Angelopoulos2025], and conformal risk control bounds an expected loss [Angelopoulos2024]. Several risks can be controlled at once, and a path through a family of rules can be learned on part of the data [LauferGoldshtein2023]. Conformal selection controls the false-discovery rate among the items a model selects [Jin2023], a statement close in spirit to a bound on wrong skips among the skipped sites, and selective classification certifies, with high probability, the risk of the predictions a model chooses to make [Geifman2017]. The bound on a level is, at its core, acceptance sampling, which accepts a lot from a sample of fixed size with an allowed number of defects [DodgeRomig1959]; risk-limiting audits apply the same logic to the count of an election [LindemanStark2012]. The present work poses a skip as a claim about a site, so that the claims of a mapping campaign become the losses these methods control.

**Exchangeability in space.** Spatial data are dependent, and a calibration sample drawn from a map is exchangeable with the rest of the map only under conditions. Spatial conformal prediction obtains exact or approximate exchangeability from properties of the spatial process, for instance local approximate exchangeability around a prediction location for a broad class of processes [Mao2024]. Design-based inference takes the opposite route and places the randomness in the sampling plan, so that statements about a finite population hold whatever the values in it [Neyman1934; Cochran1977]; in model-assisted estimation a model improves precision while the design alone carries validity [Sarndal1992], and conformal prediction has been carried into this setting [Vovk2013; Wieczorek2023]. Active inference uses a model to choose which items to label and keeps valid inference through known sampling probabilities [ZrnicCandes2024], a route that could let measured sites serve calibration as well. The campaign here follows the second route: a plan fixed level by level before each draw gives every level its population, and a uniform draw makes the calibration sample exchangeable with it, whatever the campaign did before, with no model of the spatial dependence.

**Adaptive sensing with guarantees.** Two recent lines of work bring calibrated uncertainty into the acquisition loop itself. Conformal intervals decide which pixels to re-scan in photon-limited scanning microscopy [Ye2025] and when enough has been acquired in rate-adaptive sensing [YangZhang2026], both calibrated on data collected outside the running acquisition. Power-system security screening offers the closest construction outside imaging: a label-independent audit drawn from the current operating window certifies the violation rate among contingencies that a cheap surrogate lets the operator skip, and the surrogate affects the cost of the guarantee and leaves its validity untouched [Manoharan2026]. The present work certifies each skip of a running scan by a claim, takes its calibration sample from the scan through the design, and checks every guarantee against fully measured truth.




# 3 Framework

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

**Further forms.** Any rule built from scores frozen before the draw, a uniform calibration draw and a family of thresholds fixed before the labels are known inherits a finite-sample guarantee, including a bound on a conditional rate (Appendix C). A label-conditional statement protects the sites of interest: given their number, the calibration sites of interest are a uniform draw from those of the level, and the rule of Section 3.3, with the worst case over their unknown total, limits the share skipped under the no-interest claim [Vovk2005; Sadinle2019]; a cover so restricted keeps every bound on a rate counted over the level. Table 1 summarises the forms; SI 4 gives the Monte Carlo acceptance check every form here passes.

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

## 3.6 An audit of the finished map

A campaign ends with a map, and the map deserves a statement of its own. After the last level, an audit sample drawn uniformly from the skipped sites is measured and kept out of the map, as the free set of reflections is kept out of crystallographic refinement [Brunger1992]. Its failures bound, through the exact hypergeometric limit of SI 9, how many skipped sites the map predicts outside tolerance. The bound covers every skipped site of the run at one confidence, provided the map, its interpolator and any strata are fixed before the draw; measured sites are taken as correct, so drift carried by the measurements escapes it.



# 4 Experiments

## 4.1 Datasets

Every guarantee in this study can be checked, because each dataset is measured at every design site. Three datasets cover a simulation with known phase structure, a diffraction scan and a spectroscopic map.

*Synthetic small-angle scattering map.* A forward model of a surfactant–oil–water formulation maps a composition in the triangle $x + y \le 1$ to a scattering curve on 240 logarithmically spaced points between 0.005 and 0.32 Å⁻¹. The model has a micellar phase, an ordered cubic phase, a hexagonal phase and an oil-rich emulsion, with smoothed transitions. A hierarchical Poisson-disk design on the unit square with nine levels, restricted to the triangle, gives 2118 sites. The interpolant uses mirror images across the walls of the triangle.

*NaCl microdiffraction scan.* A raster of 3249 sites on a 0.25 mm stage grid, with curves of 1000 bins between 0.59 and 38.9 nm⁻¹ [ALSNaCl]. A seven-level design, snapped to the raster, gives 1071 sites.

*Infrared map.* A bioreef sample mapped on 29 × 42 pixels of 1 µm, with 1738 channels between 650 and 4000 cm⁻¹. Each spectrum is corrected for resonant Mie scattering pixel by pixel, and the window 1500–1850 cm⁻¹, which holds the amide and ester bands, is used. A seven-level design drawn on the physical rectangle and snapped to pixels gives 959 sites. SI 2 describes the correction and the design.

Figure 3 shows each dataset as a map, with a site its claim accepts and one it rejects.

**Figure 3.** The three datasets and how their claims judge a prediction; rows: IR map, NaCl scan, synthetic map. Left column, the quantity the claims test: (a) amide-I absorbance, maximum over 1620–1690 cm⁻¹ after scattering correction, 1 µm pixels; (d) height of the (200) line where it stands five times the noise above its baseline, grey where absent, the width varying from pixel to pixel by more than the tolerance of the width claim; (g) position of the dominant peak where its prominence reaches 5, grey elsewhere, white lines: phase boundaries of the forward model. Middle and right columns: one site of a certified level that the claim accepts and one it rejects, predicted from the measured sites of the coarser levels by natural-neighbour weights (grey: neighbours, line width by weight; orange: prediction; black: measurement; shaded: tolerance). IR envelope claim: within 10 % + 0.10 absorbance on average over channels above 0.02. NaCl width claim: widths at half maximum (bars) within 0.02 nm⁻¹. Synthetic profile claim, drawn as the deviation of each channel in units of the envelope 0.005 × intensity + 0.005 (shaded: ±1; inset: the measured profile on log–log axes); the claim holds when the mean over channels is at most one, so a few channels near a peak may lie outside. File: `figures/fig_datasets_claims.png`.

## 4.2 Claims and tolerances

The IR map and the NaCl scan each carry one interest claim and one interpolation claim, fixed before any run. On the synthetic map every site is of interest, and the interpolation claim alone is made, on the full profile.

**Table 2.** Claims, fixed before any run.

| Dataset | Interest: a site holds | Interpolation: the prediction from coarser levels meets |
| --- | --- | --- |
| Synthetic map | every site (no interest claim) | every point of the profile within 0.5 % + 0.005, on average over the 240 points |
| NaCl scan | the (200) line at 22.28 nm⁻¹, at least five times the noise above its local baseline | the (200) width within 0.02 nm⁻¹, about half a detector bin |
| IR map | absorbance of 0.1 or more in some channel of the window | every channel within 10 % + 0.10 absorbance, on average over channels above 0.02 |

A second setting of the IR map tightens the envelope to 10 % + 0.01, with interest at 0.02 and channels counted above 0.005. Under it, interpolation rather than interest decides the cost. The choice of claim shapes the campaign as much as the budget does; Section 5.5 and SI 6 compare six metrics on the three datasets.


## 4.3 Protocols

A protocol pairs a predictor with the scores it supplies, so a difference in cost between protocols reflects both.

**Natural-neighbour protocol.** Natural-neighbour (Sibson) coordinates [Sibson1981] predict the spectrum at a site as a weighted mean of the measured spectra around it. One set of weights per site serves every channel and every derived quantity. The weights are non-negative and sum to one, so a prediction from non-negative spectra is non-negative. The coordinates are computed exactly by clipping Voronoi cells (SI 1); outside the hull of the measured set, inverse-distance weights over the five nearest measured sites take over.

Both scores are probabilities from logistic regressions fitted on the measured set, the interpolation score on the disagreement between natural neighbours and on position, the interest score on the predicted signal and its spread among the nearest measured sites; on the IR map the interest score is the predicted maximum in the window, capped below the interest level (SI 1). The random scorer of Section 5.4 assigns every site an independent uniform weight.

**Gaussian-process protocols.** Gaussian-process regression is the interpolator of choice for autonomous scattering experiments [Noack2019; Noack2020], and it offers a reason for every measurement: the posterior standard deviation is large where the measured set is far away in units of the length scale. The GP protocols place an isotropic squared-exponential kernel on the coordinates of the hierarchical design and evaluate the process only at design sites [RasmussenWilliams2006]. The posterior mean, clipped at zero because every spectrum here is non-negative, predicts the full spectrum at a site, and the posterior standard deviation at unit output scale orders the sites for the interpolation claim. Both depend on the measured set through one set of linear weights, so the spectrum and any quantity derived from it come from the same fit, as with natural-neighbour coordinates. The interest claim keeps its score from the natural-neighbour protocol, which isolates the change of interpolator.

The length scale is set in three ways, each fixed before the calibration draw of a level: by maximum marginal likelihood on the leading principal-component scores of the measured spectra [Balandat2020], by the median nearest-neighbour spacing of the design through the finest level measured, or locally, through a Gibbs kernel whose length scale is the distance to the third-nearest measured site [Gibbs1997; PaciorekSchervish2004]. SI 1 gives the details.

**Common settings.** Levels up to the second form the seed and are measured in full. Every finer level is calibrated on $m = 40$ sites, or on the whole level when it is smaller. The guarantee on the shared wrong-skip rate is $R_E \le 0.10$ at confidence 0.75 on the IR map, $R_E \le 0.20$ at confidence 0.80 on the NaCl scan and $R_E \le 0.10$ at confidence 0.80 on the synthetic map. The per-claim form gives each claim half the budget at half the failure probability, so the union bound returns the same statement; with the one claim of the synthetic map the three forms coincide. Every rule uses the exact finite-population tail, and the threshold is placed at the score of the first calibration failure beyond those allowed.

**Table 3.** Exchangeable parts of a campaign.

| Part | Options used |
| --- | --- |
| Design | Hierarchical Poisson-disk design; seed of levels 0–2; 7 (NaCl, IR) or 9 (synthetic) levels |
| Interpolator | Natural-neighbour coordinates; Gaussian process with length scale by maximum likelihood, by design spacing or by local spacing |
| Interest score | Predicted maximum (IR); logistic on predicted peak height (NaCl); random; none on the synthetic map |
| Interpolation score | Logistic on neighbour disagreement; GP posterior standard deviation; random |
| Form of guarantee | Per-claim budgets; quantile path; priority path |
| Calibration | 40 sites per level, uniform without replacement, exact hypergeometric tail |

## 4.4 Evaluation

A guarantee about a probability needs repetition to be checked. Each of 32 configurations was run as 250 campaigns, 20 for the three Gaussian-process configurations of the synthetic map, that differ only in their calibration draws and, for the random scorer, in the score stream. Every certified level of every campaign gives one level check against the budget, and the checks over budget are compared with the number expected under the picked failure probabilities (Section 3.3). For the first 20 campaigns of each configuration, the calibration draw was also repeated 1000 times on the recorded level populations, which isolates the randomness of the draw (SI 4, SI 5). Four studies extend the record (SI 10): a label-conditional bound, drift, an audit of finished maps and the cost of a plan against its calibration size and confidence.



# 5 Results

*All numbers below come from the run record: 32 configurations and nine comparisons, run as 250 campaigns with independent calibration draws, 20 for the three Gaussian-process configurations of the synthetic map (SI 5).*


## 5.1 The guarantee holds

Checking a probability bound needs repeated campaigns against a known truth. Every certified level of every campaign was therefore checked against the fully measured truth (SI 5).

The picked failure probabilities $\delta_L$ (Section 3.3) averaged 0.19 against a nominal 0.25 for the IR map, 0.12 against 0.20 for the NaCl scan and 0.10 against 0.20 for the synthetic map. The observed exceedances are to be compared with $\delta_L$, and the four levels of a NaCl campaign hold together with probability at least about one half.

The record agrees with the guarantee at the picked failure probabilities: over the 25 statements of 250 campaigns whose budget can be exceeded on every level, observed exceedances lay between 0.88 and 1.11 times the number expected, between 0.70 and 1.14 for the three Gaussian-process rows of 20 campaigns on the synthetic map, and none exceeded it beyond chance (SI 5, Table S5.3). On the IR map at its original tolerance, three of the four levels hold too few failing sites for the budget to be reached. Repeating the calibration draw on the recorded level populations gives the same picture (Table S5.2). Against a fixed truth these counts check the rule and its implementation (Section 6).

A plan can be certified for all levels together by dividing its failure probability among its levels when it is declared. Certified level by level, the plans exceeded the budget on at least one level in 20 %, 38 % and 46 % of campaigns on the IR, NaCl and synthetic maps. Certified for all levels together, at confidence 0.75 for IR and 0.80 for the other two, they measured 415 ± 82, 694 ± 58 and 1189 ± 286 sites, 41 %, 13 % and 28 % more, and exceeded it in 1, 24 and 16 of 250 campaigns, within the 25 % and 20 % the contracts allow (SI 5.3). Their 1, 27 and 16 level checks over budget compare with 30, 28 and 13 expected under the picked failure probabilities.

Conformal risk control on the same draw bounds only the expected share of a level skipped wrongly [Angelopoulos2024]. It measured 260, 542 and 673 sites. Its mean share of a level skipped wrongly, 5.7 %, 18.8 % and 8.8 %, stayed below the budget, as promised; single levels exceeded it in 5 %, 35 % and 32 % of checks, and campaigns on at least one level in 20 %, 81 % and 90 % (SI 5.3).

Table 4 gives one configuration per map: what was measured, why each site was skipped, and how the record compares with the guarantee. The guarantee bounds wrong skips as a share of all sites of a level; among the skipped sites alone the share is larger, up to 26.7 % on the NaCl scan.

**Table 4.** One guarantee per dataset: quantile path, natural-neighbour interpolation, 250 campaigns; counts are means per campaign. Wrong skips are given as a share of the sites on certified levels, the quantity the guarantee bounds, and as a share of the skipped sites. Expected exceedances are the sums of the picked failure probabilities over the level checks.

| Dataset | Guarantee | Sites | Measured: seed / calibration / no claim | Skipped: not of interest / predictable / both | Wrong skips: count (share of sites / of skips) | Exceedances: observed / expected |
| --- | --- | --- | --- | --- | --- | --- |
| IR map | $R_E \le 0.10$ at 0.75 | 959 | 73 / 160 / 62 | 37 / 228 / 399 | 34 (3.8 % / 5.1 %) | 49 / 190; reachable levels 49 / 56 |
| IR map, tight tolerance | $R_E \le 0.10$ at 0.75 | 959 | 73 / 160 / 388 | 8 / 257 / 73 | 54 (6.1 % / 15.9 %) | 193 / 190 |
| NaCl scan | $R_E \le 0.20$ at 0.80 | 1071 | 76 / 160 / 378 | 157 / 156 / 144 | 122 (12.3 % / 26.7 %) | 112 / 120 |
| Synthetic map | $R_E \le 0.10$ at 0.80 | 2118 | 39 / 233 / 660 | – / 1186 / – | 98 (4.7 % / 8.2 %) | 147 / 143 |

Breaking the order of operations breaks the guarantee (Section 3.1). On a simulated level of 399 sites with a budget of 0.10 and a picked failure probability of 0.206, the calibration draw was repeated 4000 times under several rules (SI 5.2). Scores frozen before a uniform draw exceeded the budget in 20.5 % of draws, as did a score that knew the true labels: what the score knows changes the cost and leaves the guarantee intact. Rules that use the draw broke it, in every draw when the scores of failing calibration sites were raised afterwards, in 63 % when calibration sites were taken where the scores were least sure, as an active learner would, and in 69 % when the best of five draws was kept. Setting one threshold on the calibration sites the other left uncovered exceeded the budget in 28.8 % of draws, where the priority path, which fixes the same preference in advance, stayed at 20.5 %. Every form of Table 1 kept its guarantee, and none was the least expensive on all three maps (Fig. S3; Table S3.1).

## 5.2 A model's own error rate is checked only against the full scan

Decisions resting on a model's stated error rate need that rate to hold. On the NaCl scan, a Gaussian process refitted after each level of the same fixed design skipped a site when it was sure the line was absent, or when its 68 % interval on the width, from the predictive standard deviation, lay within the tolerance (SI 7). Its statement, the model's own probability of a wrong skip summed over its skips, can be set against the realised share of the level, the quantity the guarantee bounds. The fitted noise took about three quarters of the variance of the width, the site-to-site scatter of the sample, so no interval fell within the tolerance; every skip was for want of a line, and the process stated 0.4 % and realised 0.3 %, at 922 measurements. The certified plans measured 614 ± 56 sites with natural-neighbour interpolation and 745 to 777 with the Gaussian process as predictor, and their bound held at the stated confidence (Fig. S7). Certifying the Gaussian process thus saved about 150 measurements against trusting its intervals.

The comparison was repeated on all three maps with the Gaussian process of the certified campaigns in Section 5.4, which predicts the whole profile. A site was skipped under a claim when the posterior probability of a wrong skip was at most α, for α from 0.01 to 0.32, with the predictive standard deviation or with that deviation rescaled to the leave-one-out residuals of the measured sites (SI 7). On the synthetic map, under the profile claim, the process judged every site too uncertain to skip at every α and measured all 2118, where the certified plan measured 932 ± 223 (Fig. 1). Rescaled to the leave-one-out residuals, it measured 1506 to 1792 sites, stated 0 % to 1.8 % and realised 0.3 % to 2.1 %; the scale fell to between 0.06 and 0.23 of its value, because the sites the process chose to measure were easier for it to predict than those it left out, the bias a uniform draw removes. On IR the stated shares stayed below 10 % and the realised ones below 5 %, with 73 to 398 of 959 sites measured. On NaCl the process judged almost every site too uncertain to skip and measured 959 to 1070 of 1071 (Fig. 4).

A rate stated by the model can thus be right, too low, or so cautious that nothing is skipped, and only sites the model did not choose show which (Section 5.6). The certified campaigns at budgets from 0.05 to 0.30 realised on average less than their bound on every map; certified points pair a bound with a mean, uncertified points a stated expectation with a realisation.

**Figure 4.** What an agent states about its wrong skips, and what happens. Stated against realised share of certified-level sites skipped wrongly, for certified campaigns with natural-neighbour (blue) and Gaussian-process (purple) prediction at budgets 0.05 to 0.30 (the bound against the mean over 20, or 8 for the Gaussian process, 4 on the synthetic map) and for uncertified Gaussian-process campaigns at α from 0.01 to 0.32 with predictive or rescaled standard deviation; shares below 10⁻³ are drawn at 10⁻³; grey: equality. File: `figures/fig_stated.png`.

## 5.3 Every action certified

An instrument record becomes useful once every site of a map carries its reason. Figure 5 shows one campaign of average cost per dataset under the quantile path with natural-neighbour interpolation, with every design site marked by the reason recorded for it and every wrong skip found against the fully measured truth.

In the campaigns shown, the wrong skips were 3.8 % of the sites on certified levels of the IR map, against a budget of 0.10 per level, 11.8 % on NaCl, against 0.20, and 5.3 % on the synthetic map, against 0.10. The wrong skips of the synthetic map gather along the phase boundaries and the walls of the composition triangle; the guarantee bounds their rate on each level and leaves their location open (Section 5.5; SI 6).

In hindsight, the record shows which measurements every claim would have skipped wrongly (SI 8): 43 % of the sites measured for want of a claim on the synthetic map, against 40 % of sites drawn at random, where the tight tolerance fails at most sites, and 47 % against 35 % on NaCl, where the width scatters from site to site by about the tolerance.

**Figure 5.** Maps with reasons, one campaign of average cost per dataset (quantile path, natural-neighbour interpolation; NaCl: random state 44; the same campaigns as SI 8). Measured sites: seed (black diamonds), calibration (dark grey squares) and sites without a claim (light grey squares). Skipped sites: not of interest (yellow), predictable (green) and both (blue). Crosses: wrong skips against the fully measured truth. IR in micrometres, NaCl in stage millimetres, synthetic map in composition fractions. File: `figures/fig5_maps.png`.

## 5.4 The model sets the cost

Freedom in the choice of model has a price, paid in measurements. The quantile path was run with four interpolation protocols on each dataset at the nominal guarantees of Section 5.1: natural-neighbour interpolation with the logistic score, and Gaussian-process interpolation with the posterior standard deviation as score and three rules for the length scale (Section 4.3). At the original IR tolerance almost every site is interpolable and the interest claim alone sets the cost; at the tight tolerance interpolation decides.

A score that carries no information still yields a valid guarantee, at a price. A random scorer, an independent uniform weight per site and claim, exceeded the budget no more often than expected on every map and cost 1.4 to 2.4 times as many measurements as informed scores, 716 ± 71 against 295 ± 53 of 959 sites on IR (Fig. 6). The guarantee comes from the calibration draw; the score decides what it costs.

Every guarantee held, with exceedance counts on each map close to those expected under the picked failure probabilities and none beyond chance (Fig. 6; Table S5.3).

The cost depends on the protocol and on the data (Fig. 6; Table S3.2). At the original IR tolerance the four protocols measured 273 ± 31 to 295 ± 53 of 959 sites with skipped sets overlapping by about 90 %; at the tight tolerance they measured 621 ± 70 to 799 ± 40, and the Gaussian-process protocols shared a quarter to a third of their skips with natural-neighbour interpolation. On NaCl, the Gaussian-process protocols measured 745 to 777 of 1071 sites, against 614 ± 56. On the synthetic map they measured between 1946 ± 50 and 2027 ± 39 of 2118 sites over 20 campaigns each, against 932 ± 223 with natural-neighbour interpolation and 1578 ± 248 with random scores; their score, the posterior standard deviation at unit output scale, depends on the positions of the measured sites and the length scale only. The difference arises in the calibration draws: more failing calibration sites admit fewer skips at the same budget, and the guarantee is unchanged.

A certified plan has to earn its place against a uniform sample of the same size. With every other site predicted from all measured sites, such a sample left 0.5 ± 0.2 %, 22.0 ± 1.0 % and 10.4 ± 0.7 % of the certified-level sites outside tolerance on the IR, NaCl and synthetic maps; the final maps of the certified plans, predicted in the same way, left 0.4 ± 0.3 %, 18.0 ± 3.8 % and 3.6 ± 1.8 % (SI 5.3). The contract sets the rest: on the IR map at confidence 0.80, calibration samples of 20, 40 and 80 sites per level cost 340 ± 90, 337 ± 63 and 393 ± 22 measurements, and at 0.95 a sample of 20 certified no level (SI 10.4).

**Figure 6.** What a guarantee costs under different models: sites measured (mean ± s.d. over 250 campaigns, quantile path) with random scores and with four interpolation protocols, against the number of design sites (dashed). Under each bar: level checks over budget on the shared rate, observed against expected under the picked failure probabilities. GP: Gaussian process with isotropic squared-exponential kernel; length scale by maximum likelihood, by design spacing, or by local spacing of measured sites. File: `figures/fig_cost.png`.

## 5.5 The claim decides what is protected

Each claim protects what it states, so its choice deserves a record. Six acceptance metrics were compared on the three maps with the interpolation claim alone (SI 6). Every metric kept its guarantee, and the metric set the cost: at tolerances a practitioner might pick, the IR map needed between 233 and 810 measurements. At tolerances matched to equal difficulty the metric still decided where measurements went, with the peak claim on the synthetic map measuring where the peak drifts with composition and the profile claim along the phase boundaries (Fig. S6), and it decided where wrong skips fell. The rate counts wrong skips over all sites of a level. On a variant of the synthetic map that adds an interest claim, a dominant peak at least five times its baseline, to a claim on the peak position and width at a budget of 0.20, a third of the sites are of interest, and 35 % of them on certified levels were skipped in error while every level met its budget (SI 6.2).

The label-conditional statement of Section 3.4 closes that gap. On that variant, at a share of 0.20 and confidence 0.80, calibrated on 12 to 20 sites of interest per level, the plan lost 8.5 ± 4.4 % of the interesting sites, against 34.7 ± 8.5 %, at 359 ± 26 measurements against 334 ± 26; 4.9 % of level checks exceeded the share, against 58.7 % without it. On NaCl, where two thirds of the sites hold the line, the shared budget already spared them, and the statement changed the share lost from 9.2 % to 8.1 % at 16 more measurements (SI 10.1).

## 5.6 Checks on the finished map

An audit of 100 skipped sites after the last level (Section 3.6) bounded, at confidence 0.80, the share of certified-level sites that the final map predicts outside tolerance at 1.5 %, 19.8 % and 5.1 % on the IR, NaCl and synthetic maps, against 0.4 %, 18.0 % and 3.6 %, and held in 100 %, 83 % and 86 % of audit draws (SI 10.3). A campaign steered by its own model meets a budget only when the model's statement holds. On the NaCl scan a Gaussian process measured, batch by batch, the sites at which it judged a skip most likely to be wrong, and stopped once its stated share of certified-level sites predicted wrongly reached 0.20 (SI 10.3). In 30 runs it stopped after 451 to 501 measurements with 14.6 ± 0.6 % of the sites wrong, fewer measurements than the certified plan needed, because its fitted noise made the statement conservative on this scan; the same statement fell short by factors of 3 to 10 on the synthetic map (Section 5.2). An audit of 100 sites at the stopping point confirmed the budget in 89 % of draws.

Drift was simulated as a slow swelling of the synthetic sample, its $q$ scale stretched in proportion to the number of sites measured before, by 5 % to 20 % over the mean cost of the plan (SI 10.2). Under the profile claim the bound broke: at a stretch of 5 % the levels exceeded their budget in 24 % of checks against 9.5 % expected, the plan measured 1687 ± 76 sites against 966 ± 247, and 88 % of the measurements lay outside tolerance of the sample at the start, where no claim applies. Five seed sites measured again after each level flagged every drifted campaign from the fourth level on, and none without drift.


# 6 Discussion

## The value of a stated rate

A stated rate is worth most where decisions rest on it: a budget chosen in advance holds at its confidence, and a model's own statement may be right or several times too low (Section 5.2). Accountability costs measurements: certifying the Gaussian process on the NaCl scan took about 100 more, and certifying a plan for all levels together rather than level by level 13 % to 41 % more, each in exchange for a budget fixed in advance and kept. A model steering its own campaign can be cheaper, and it meets a budget when its fitted noise happens to cover its misfit, as on the NaCl scan (Section 5.6); the contract meets the budget whatever the variance, at the price of its calibration draws, and the audit reports afterwards what any finished map delivered. The record adds a second value in failure. A level over budget is either chance at the stated rate or a sign that a condition of Section 3.1 failed, through drift, beam damage or a draw that was not uniform, and drift also corrupts the measurements themselves, where no bound reaches (Section 5.6); seed sites measured again after each level expose it. An uncertified agent leaves its errors unapportioned between model, data and chance.

A better kernel may make a Gaussian process honest on a given map, and whether it did can be checked only on sites the model did not choose. A coherent Bayesian model expects its own forecasts to prove well calibrated, whatever its prior [Dawid1982], so calibration is checked outside the model. In a closed loop the sites of that check have to be drawn uniformly from the level before the decision: cross-validation on the measured sites inherits their selection, and on the synthetic map rescaling to leave-one-out residuals shrank the stated uncertainty, because the measured sites were easier to predict than the skipped ones (Section 5.2). A uniform held-out sample turns the check into a bound at no further cost, through the order statistic of Section 3.3, and that sample is the calibration step of the plan. Cross-validation estimates the error of a model; the calibration draw bounds the error of a decision, for any model and inside the loop the model steers. Any kernel then enters as a score, and its quality returns as fewer measurements.

## Scope of the guarantee

A map built under a guarantee serves its reader to the extent that the reader knows what the bound covers. The bound concerns the share of wrong skips among all design sites of a level, with probability over the calibration draw. Section 5.5 and SI 6 show the two consequences: wrong skips gather in space, and when signal is rare a budget met on every level can still cost a large share of the sites of interest. A label-conditional statement bounds the share of interesting sites lost (Section 5.5); it rests on the calibration sites of interest alone, so a rare signal calls for a larger draw. Calibration carries a fixed cost of 40 sites per certified level, up to a sixth of the IR map, a share that falls as maps grow, since the budget and the confidence alone set the sample size. Labels compare with one measurement (Section 3.5). On the NaCl scan the width scatters from site to site by about the tolerance, and about half of all predictions fail whatever the model, while counting noise alone makes a second measurement fail against the first at 1.1 % of sites (SI 2); the scatter lies in the sample, or in variation the counting noise leaves out, and repeated measurements would set the tolerance. Fully measured data check the rule against a fixed truth. Simulated drift broke the bound and moved most of the error into the measurements, where repeated seed sites found it (Section 5.6). A drift so found can be modelled from the repeated sites and removed, or the calibration sites weighted by age at a bounded loss of coverage [Barber2023]; a measurement that disturbs its neighbours remains a question for a live campaign.

## What is certified shapes the campaign

A guarantee is stated for one acceptance metric, and the metric deserves the same care as the budget. The bound holds for any metric fixed before the calibration draw, and the metric decides the rest: which sites fail prediction, where measurements are taken and where wrong skips gather (Section 5.5). The same holds for any autonomous experiment: the quantity a model predicts, and the error its acquisition anticipates, decide where measurements are taken [Noack2019; Noack2020]. The guarantee delivers the claim as specified, and features outside that claim carry no protection. The metric is therefore best fixed from the scientific question before beam time, stated with the guarantee, and checked on a pilot scan for the cost it implies.

## Extensions

An audit sits over any campaign, whatever its rule, at the cost of its sample (Section 5.6). Certification of each level sits over any campaign that fixes its proposals for a level before its draw: the proposals of an acquisition-driven Gaussian process enter as a frozen score, and within an action the remaining sites can follow the shortest path of the instrument. Costs here are counted in sites; at an instrument each level adds a second pass, the calibration sample measured and reduced before the rest is decided, and a fast raster of the whole plan may compete with scattered single measurements. Any rate that counts sites can be bounded, and ratios such as the share of skips that are wrong are controlled through conformal p-values [Jin2023]. Two conditions carry every such statement: the calibration sites are an exchangeable draw from the population the statement concerns, a Mondrian category fixed before the draw taking the place of the level [Vovk2005], and the rule is non-anticipating (Section 3.1). For a bounded loss graded by the size of an error, confidence sequences for sampling without replacement [WaudbySmith2020] give a bound of the same kind and would let calibration stop as soon as the bound is settled. Optimisation is the natural next case; reweighting by the known selection mechanism [Tibshirani2019; Fannjiang2022; Barber2023], online control of a long-run rate [Gibbs2021] and level sets, each a mapping problem with a threshold fixed before its draw [CerouGuyader2007; Gotovos2013], offer routes to a bound.

## Accountable experiments

An accountable experiment certifies every action, one decision per level of the plan, and gives every site its reason. The workflow leaves both in its record. Each site carries its level, scores and reason; each level carries its calibration draw, picked failure probability, thresholds and bound. The guarantee rests on the order of operations, so the record suffices: predictor and scores are frozen and recorded before each draw, the draw is reproduced from its recorded random state, and every decision can be replayed, every bound recomputed (SI 5) and every measurement checked in hindsight (SI 8). The guarantee bounds, at the stated confidence, the share of each level skipped under a false claim. Claims, tolerances and budgets form the contract and remain the experimenter's choice; the record shows that the contract was kept.

---



# 7 Conclusion

An experiment that leaves sites unmeasured can certify every action. On each level of the plan one decision is taken, after a uniform draw from a level fixed before it: each skipped site falls under a claim, the share of the level skipped under a false claim is bounded, and each measured site carries the reason it was measured; the order fit, freeze, draw, calibrate, decide keeps each draw exchangeable with its level whatever came before. On three fully measured datasets the record matched the guarantees, with informed and random scores, natural-neighbour and Gaussian-process interpolation and three forms of guarantee. The model set the cost of a guarantee; trusted on its own uncertainty, the same model stated a rate that was sometimes right, sometimes too low, and under a tight claim so cautious that it skipped nothing. The certified claim decided what a guarantee bought: where measurements were taken, where wrong skips gathered and which sites were protected. The claim therefore belongs to the scientific question and enters the contract with it, before the experiment. A held-out audit certified the finished map of any campaign, and a label-conditional bound protected the sites of interest. Optimisation through level sets, scores that rank sites by the information they add to a process model, a model of beam time, and deployment at autonomous instruments, beginning with a synthesis campaign, are natural next steps. Each skipped site leaves the campaign with a reason and a claim, each level with a bound, and the record allows every decision to be replayed.


# Appendix A. Exchangeability by design and the single-claim bound

## A.1 Conditions

A campaign processes the levels $L = L_s + 1, L_s + 2, \dots$ of a hierarchical design in order. Write $\mathcal{F}_{L-1}$ for everything known before the calibration draw of level $L$: the design, the sites measured so far and their spectra, all earlier calibration draws, and any auxiliary randomness used by the scores. The truth $y(x)$ at every design site is fixed; for a live experiment, $y(x)$ is the outcome a measurement of $x$ would return.

The order of operations of Section 3.1 amounts to six conditions.

- **(A1) Fixed population.** The level population $D_L$, of size $N_L$, is determined by $\mathcal{F}_{L-1}$. It may be declared before the experiment or drawn up from the sites measured so far; in this work the plan is declared in full before the experiment.
- **(A2) Frozen scores and predictor.** The scores $S_j$ and the predictor $\hat y_L$ on $D_L$ are determined by $\mathcal{F}_{L-1}$.
- **(A3) Labels.** Each bad label $B_j(x)$, $x \in D_L$, is a fixed function of the truth and of $\hat y_L$, so the labels of the whole level are determined given $\mathcal{F}_{L-1}$, whether or not a site is drawn.
- **(A4) Fixed rule.** The family of covers searched (thresholds on one score, a path, a split of the budget), the budget $\varepsilon$, the failure probability $\delta$, the sample size $m$ and the allowed number of failures $k$ are determined by $\mathcal{F}_{L-1}$.
- **(A5) Uniform draw.** Given $\mathcal{F}_{L-1}$, the calibration sample $C_L$ is uniform over the $m$-subsets of $D_L$.
- **(A6) Fixed truth.** The measurement a site of $D_L$ would return depends neither on which sites are drawn nor on the order or time at which they are measured: measuring a site of $C_L$ leaves the truth at every other site unchanged, and the sample does not drift during the level.

Under (A1)–(A6), the level population with its scores and labels is a fixed finite population given $\mathcal{F}_{L-1}$, and $C_L$ is a simple random sample from it. Exchangeability of the calibration sites with the population is then a property of the draw [Vovk2005], and the bound below is a design-based statement [Neyman1934; Cochran1977]: its only probability is that of the draw. The scores may depend on anything in $\mathcal{F}_{L-1}$, including the truth itself through an oracle; such a score changes the cost and leaves the bound intact.

## A.2 The bound

Fix a level and a claim with score $S$ and bad label $B$, and drop the indices. The joint rate at threshold $\tau$ is

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

The argument is the one-sided tolerance bound of Wilks (1941) in the form used for risk control [Bates2021; Angelopoulos2025], with the exact finite-population tail in place of its binomial approximation. The binomial $k$, the largest with $P(\mathrm{Bin}(m, \varepsilon) \le k) \le \delta$, was never larger in this study and then gives a valid, more conservative rule; the implementation checks the ordering on every level and refuses a binomial $k$ above the hypergeometric one, and a numerical check over level sizes from 41 to 1300, budgets from 0.05 to 0.30 and failure probabilities from 0.05 to 0.25 at $m = 40$ found no exception.

**The picked level.** $\delta_L = P(H \le k)$ takes values on a grid indexed by $k$ and set by $m$, $N_L$ and $\varepsilon$. The rule picks the largest grid point at or below $\delta$, and $\delta_L$ is the failure probability the level asserts. Equality in Proposition A.1 holds when exactly $\lfloor \varepsilon N \rfloor + 1$ bad sites lie at or below $\tau^\ast$; Appendix B.5 describes the randomised rule that reaches $\delta$ itself.

**Several levels.** Taking expectations over $\mathcal{F}_{L-1}$ gives the unconditional bound on each level. For a statement about all certified levels at once, $P(\exists L : R_L > \varepsilon) \le \sum_L \delta_L$, the sum running over every certified level. A level that holds too few failing sites for the budget to be reached cannot exceed it, but which levels these are is known only from the full truth, so the confidence a campaign can claim is the one its plan declares. A plan certified at campaign confidence $c$ divides $1 - c$ among its levels before the first draw. A plan drawn up level by level fixes in advance how the failure probability is spent, for example $\delta_\ell$ for the $\ell$-th level it produces with $\sum_\ell \delta_\ell \le 1 - c$; the number and sizes of the levels may then depend on the history, and each $\delta_\ell$ is fixed before its own draw.

## A.3 What breaks the conditions

Each of the following lets the draw of a level shape the rule it is meant to test.

- *Refitting on calibration labels* (breaks A2, A4). Scores changed with the calibration labels after the draw and then thresholded on the same labels. The Monte Carlo of Section 5.1 takes the extreme case, raising the scores of the failing calibration sites, and the bound was exceeded in every draw.
- *Choosing the calibration sites* (breaks A5). Calibrating where the scores are least sure, as an active learner would, makes the sample unrepresentative of the sites it speaks for.
- *Keeping the most favourable of several draws* (breaks A5). The retained sample is selected by its outcome.
- *Measurement-induced change and drift* (break A6). Damage caused by measuring the calibration sites alters the truth at their neighbours, and drift during a level changes the truth between the draw and the measurement of the remainder.

The sequential rule of Section 5.1 breaks (A4) in a subtler way: its second threshold is searched over a family that depends on the labels the first threshold left uncovered.



# Appendix B. Guarantees on the shared wrong-skip event

Fix a level with population $D$ of $N$ sites and a set $J$ of claims. Claim $j$ has a frozen score $S_j$ and a bad label $B_j$ ($Z$ for interest, $F$ for interpolation). A calibration sample $C \subset D$ of size $m$ is drawn uniformly without replacement after the scores are frozen; labels are known on $C$ only. Write $k(\varepsilon, \delta)$ for the largest integer with $P(H \le k) \le \delta$, where $H$ is hypergeometric with population $N$, $\lfloor \varepsilon N \rfloor + 1$ marked sites and $m$ draws, as in Appendix A. The binomial tail $P(\mathrm{Bin}(m, \varepsilon) \le k)$ gives a valid but smaller $k$.

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

On the same event, the rate of sites at which every covering claim fails is at most $\min_j \varepsilon_j$. No threshold exists for claim $j$ when $k(\varepsilon_j, \delta_j) < 0$, that is, when $\varepsilon_j < 1 - \delta_j^{1/m}$; the claim then covers nothing.

## B.2 One budget along a nested path

A path is given by entry times $\lambda_j(x) \in [0, \infty]$, one per claim and site, computed from the frozen scores of the whole level and from settings fixed in advance, and from no calibration label. Claim $j$ covers $x$ at path position $\lambda$ when $\lambda_j(x) \le \lambda$. Define the cover time and the failure time of a site,

$$
\lambda_{\mathrm{cov}}(x) = \min_{j \in J} \lambda_j(x)
$$

$$
\lambda_E(x) = \min \{\lambda_j(x) : j \in J,\ B_j(x) = 1\}
$$

with $\lambda_E(x) = \infty$ when no label is bad. A site is a wrong skip at $\lambda$ exactly when $\lambda_E(x) \le \lambda$, so

$$
R_E(\lambda) = N^{-1} \, \lvert \{x \in D : \lambda_E(x) \le \lambda\} \rvert
$$

is nondecreasing and right-continuous in $\lambda$. Let $k = k(\varepsilon, \delta)$. Let $b$ be the $(k+1)$-th smallest finite value of $\lambda_E$ on $C$. The rule covers every site with $\lambda_{\mathrm{cov}} < b$, every site when $C$ holds at most $k$ finite values of $\lambda_E$, and no site when $k < 0$. Write $\hat\lambda$ for any position below $b$ that covers the same sites.

**Proposition B.2.** With probability at least $1 - \delta$ over the draw, $R_E(\hat\lambda) \le \varepsilon$.

*Proof.* Let $\lambda^\ast = \inf\{\lambda : R_E(\lambda) > \varepsilon\}$. By right-continuity, the set $K = \{x : \lambda_E(x) \le \lambda^\ast\}$ has $|K| \ge \lfloor \varepsilon N \rfloor + 1$ sites. The set depends on the labels and the entry times, and on nothing drawn. If $R_E(\hat\lambda) > \varepsilon$, then $\hat\lambda \ge \lambda^\ast$, so every site of $K$ has $\lambda_E \le \hat\lambda$. Since $\hat\lambda < b$, at most $k$ calibration sites have $\lambda_E \le \hat\lambda$, hence $|C \cap K| \le k$. The count $|C \cap K|$ is hypergeometric, and the remainder of the argument is that of Appendix A:

$$
P\big(R_E(\hat\lambda) > \varepsilon\big) \le P\big(|C \cap K| \le k\big) \le \delta
$$

$\square$

Testing the hypotheses $R_E(\lambda) > \varepsilon$ in order of increasing $\lambda$ and stopping at the first that cannot be rejected is fixed-sequence testing in Learn-then-Test [Angelopoulos2025]; Proposition B.2 is the one-dimensional, monotone case. With a single claim, $\lambda_E$ and $\lambda_{\mathrm{cov}}$ coincide on bad sites and the rule reduces to Appendix A.

**Quantile path.** With $\hat F_j$ the empirical distribution function of $S_j$ over the level and weights $w_j \in (0, 1]$,

$$
\lambda_j(x) = \hat F_j(S_j(x)) / w_j
$$

**Priority path.** With $i_j \in \{0, 1, \dots\}$ the position of claim $j$ in a fixed order,

$$
\lambda_j(x) = i_j + \hat F_j(S_j(x))
$$

so that claim $j$ sweeps its own quantiles over $\lambda \in (i_j, i_j + 1]$ while earlier claims stay at their final coverage. In both paths, a claim restricted to sites below a cap on its score receives $\lambda_j(x) = \infty$ above the cap. Both are functions of frozen scores and fixed settings, and Proposition B.2 applies.

## B.3 The sequential rule

The rule of the original IR analysis first sets the interest threshold on $C$, then sets the interpolation threshold on the calibration sites the interest claim leaves uncovered, from the budget that remains. The second entry time then depends on calibration labels, $K$ in the proof of Proposition B.2 is no longer fixed before the draw, and the hypergeometric step fails. Section 5.1 reports the consequence on a simulated population with uninformative scores: the bound is exceeded in 0.288 of draws, against a picked failure probability of 0.206 and a nominal 0.25. The priority path keeps the same preference and the fixed-path condition.

## B.4 Other families

Proposition B.2 needs a family of covers fixed before the labels and nested in one parameter. A family without that order, such as a two-dimensional grid of threshold pairs, is handled by Learn-then-Test with a family-wise correction across the grid [Angelopoulos2025], or by learning a path on one part of the draw and testing it on the other [LauferGoldshtein2023]. Both give guarantees of the same kind at the cost of a smaller effective calibration sample.

## B.5 Attaining the nominal failure probability

On a fixed level population, the exceedance probability of the rule above equals $P(|C \cap K| \le k)$ when the wrong-skip rate crosses $\varepsilon$ at exactly $\lfloor \varepsilon N \rfloor + 1$ sites, and is smaller otherwise. With $k$ from the hypergeometric tail, the bound is therefore attained up to the integer step in $k$: at $m = 40$ and $\varepsilon = 0.10$, $k = 2$ gives at most 0.21 on 399 sites against $\delta = 0.25$. A randomised rule, which uses $k + 1$ with the probability that makes the mixture of the two tails equal to $\delta$, removes the step [Lehmann & Romano 2005, ch. 3]. It makes the decision depend on an extra coin and is not used here.


# Appendix C. A bound on the conditional rate

The rate bounded in Appendices A and B counts wrong skips among all sites of a level. A reader of the map may instead need the rate among the sites one claim covers. Learn then Test gives that bound for a family of thresholds fixed before the labels are seen [Angelopoulos2025].

Keep the notation of Appendix B for one claim with frozen score $S$ and bad label $B$. The family of thresholds is a grid of quantiles of the frozen scores over the whole level,

$$
\tau_i = Q_S(q_i), \quad q_i = q_0 + 0.05\,(i - 1), \quad i = 1, \dots, I
$$

ending at $q_I = 1$. Both the grid and $q_0$ depend on the scores and on settings fixed in advance, and on no label. Threshold $\tau_i$ covers the set $D_i = \{x \in D : S(x) \le \tau_i\}$ of $N_i$ sites, and its conditional rate is

$$
R_i = N_i^{-1} \, \lvert \{x \in D_i : B(x) = 1\} \rvert
$$

For each $i$, the null hypothesis $H_i : R_i > \alpha$ is tested on the calibration sites in $D_i$. Their number $n_i = |C \cap D_i|$ is random; given $n_i$, they form a uniform sample without replacement from $D_i$, since $C$ is uniform on $D$ and $D_i$ is fixed before the draw. The number $f_i$ of bad labels among them is then hypergeometric, and

$$
p_i = P(H_i^\ast \le f_i)
$$

with $H_i^\ast$ hypergeometric on $N_i$ sites, $\lfloor \alpha N_i \rfloor + 1$ of them bad and $n_i$ draws, is a valid p-value for $H_i$ conditional on $n_i$, hence also unconditionally. The binomial tail $P(\mathrm{Bin}(n_i, \alpha) \le f_i)$ is close to it at the sizes of this study but is not dominated by it in every case, so only the hypergeometric p-value carries the guarantee; no result of Section 5 rests on the conditional rate.

The rates $R_i$ need not increase with $i$, so the hypotheses are tested in a fixed order: $H_1, H_2, \dots$, each at level $\delta$, stopping at the first that is not rejected. Fixed-sequence testing controls the family-wise error at $\delta$ [WestfallKrishen2001], so with probability at least $1 - \delta$ every rejected hypothesis is false. The rule covers $D_{i^\ast}$, where $i^\ast$ is the last rejection, and covers nothing when $H_1$ is not rejected. With probability at least $1 - \delta$,

$$
R_{i^\ast} \le \alpha
$$

**Minimum calibration size and starting quantile.** A hypothesis can be rejected only if its calibration sites can show a small enough tail even with no bad label, which requires $(1 - \alpha)^{n_i} \le \delta$, or

$$
n_i \ge n_{\min} = \lceil \log \delta / \log (1 - \alpha) \rceil
$$

The first threshold therefore covers at least the share $n_{\min}/m$ of the level, and $q_0$ is that share rounded up to a multiple of 0.05. With $\alpha = \delta = 0.10$, $n_{\min} = 22$, and at $m = 40$ the grid starts at the 0.55 quantile: the rule certifies nothing or more than half of the level. A useful conditional bound thus calls for calibration samples several times larger than the rate bounds of Appendices A and B need, which is why the main text reports those.
