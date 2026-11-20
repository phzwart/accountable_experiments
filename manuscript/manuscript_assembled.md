# Abstract

*Working title: What can be guaranteed about a measurement that was never made*

Autonomous experiments decide where to measure, and every site left out enters the final map as a prediction. Accountability for such decisions calls for a statement, checkable against measurements, of how often a skip is wrong. A skip is posed here as one of two claims: the site holds nothing of interest, or its spectrum, or a quantity derived from it, is predictable within tolerance from coarser measurements. A hierarchical design and a uniform calibration draw, taken after predictor and scores are frozen, make the calibration sites exchangeable with each level. Existing risk-control results then give a finite-sample bound on the share of the level skipped under a false claim, in three forms. On a synthetic small-angle scattering map, a NaCl microdiffraction scan and an infrared map, each fully measured, observed exceedances lay between 0.88 and 1.11 times those allowed wherever the budget could be reached. Under a bound of 0.10 at confidence 0.75, the infrared map needed 295 of 959 measurements with informed scores and 716 with random ones: the guarantee comes from the draw, and the score sets its cost. The certified claim decides the rest. Across six acceptance metrics the bound held for each, while the metric decided where measurements were taken and where wrong skips gathered.


# 1 Introduction

Autonomous decision engines are becoming routine in large-scale experimentation. At synchrotron beamlines, Gaussian-process surrogates decide which sample position or composition to measure next, and measurement, analysis and decision run as one closed loop [Noack2019; Noack2020; Yager2023]. Self-driving laboratories search formulation and composition spaces in the same way [Burger2020; Nazeri2026]; an autonomous laboratory synthesised 41 of 58 target inorganic compounds in 17 days [Szymanski2023]. In synthetic biology, probabilistic models recommend which strains to build next [Radivojevic2020]. Laboratory automation, cloud laboratories and maturing decision software keep lowering the cost of handing experimental choices to machines [Tom2024].

Every such engine decides what to measure and, with the same decision, what to leave unmeasured. Beam time, dose, reagents and sample lifetime limit how much can be measured, and a decision engine spends that budget where its model is least certain or most promising. In a scanning or mapping experiment the sites left out still enter the final map, as predictions.

Moving these decisions from people to models makes accountability a design requirement. Guidance on AI risk asks for traceable decisions and documented responsibility across the life of a system [NIST2023], regulation of high-risk systems requires automatic records of their operation [EU2024, Art. 12], and audit frameworks for machine learning ask for evidence that can be checked against stated expectations [Raji2020]. For a measurement campaign the consequential decision is whether to measure a site. An accountable instrument records why each site was skipped and states, in a form that can be checked, how often such skips are wrong.

A short principle underlies every adaptive scan: measure what must be measured, skip what can be skipped. Two conditions justify a skip. Either the site holds nothing of interest, or its spectrum, or a quantity derived from it, can be predicted within tolerance from the sites already measured. Each condition is a claim about the site, and a measurement would settle it. A wrong skip is a site covered by a false claim.

Distribution-free risk control offers one route to that statement. Conformal prediction and its extensions attach finite-sample guarantees to the output of an arbitrary predictor, with exchangeability of the calibration data as the only assumption [Vovk2005; Angelopoulos2023]. Risk-controlling prediction sets and Learn-then-Test bound the population rate of a chosen loss from a held-out sample [Bates2021; Angelopoulos2025], and several risks can be controlled at once [Angelopoulos2025; LauferGoldshtein2023]. Related constructions already steer re-scanning in microscopy [Ye2025], set the acquisition rate in imaging [YangZhang2026] and certify the contingencies that power-grid operators leave unchecked [Manoharan2026], a sign that the need for checkable statements about automated decisions extends well beyond one field. Posing a skip as a claim brings scanning experiments within reach of these results.

This paper offers one way to make a mapping campaign accountable: a workflow that states, for every level of a hierarchical design, a guarantee on the rate of wrong skips. A coarse, space-filling level is measured first. At each finer level, a model fitted to the measured sites proposes which sites to skip, a uniform random sample of the level is measured for calibration, and its labels set the thresholds under which a skip is allowed. The guarantee reads: the fraction of the level skipped under a false claim is at most ε, with probability at least c over the calibration draw. Hierarchical Poisson-disk designs [Bridson2007] provide the fresh, exchangeable population that each calibration draw requires inside an adaptive campaign. Every site leaves the campaign with a recorded reason: measured in the seed, for calibration or for want of a covering claim, or skipped under a named claim and its bound.

The emphasis lies on what can be guaranteed, and at what cost in measurements. The bound holds for any interpolator, scoring rule or acquisition order that respects the sequence fit, freeze, draw, calibrate, decide. Model quality sets the number of measurements a guarantee costs. Optimality of the underlying algorithms lies outside the scope of this work, and protocols are compared by the measurements they spend per guarantee. The same guarantees are therefore made with natural-neighbour and Gaussian-process interpolation and with learned and random scores. The form of the guarantee is a choice as well, and follows from the question an experimenter needs answered.

A guarantee delivers exactly the claim it is given, which raises a second question: what does a guarantee buy? The acceptance metric that defines a predictable site, a peak position and width or the whole curve, decides which sites fail prediction, and with them where a campaign measures and where its wrong skips fall. A rate over a level leaves the location of wrong skips free, and it counts them over all sites of the level, of which the sites of interest may be a small part. Which claim to certify is therefore a scientific choice with a price in measurements, and this study reports that price next to every guarantee.

The workflow is one answer to the need for accountability, built from interchangeable parts so that other answers can share its record and its checks. The contributions are fourfold. Skipping is posed as two claims with one shared wrong-skip event, and guarantees of three forms are built on it from existing risk-control results: separate budgets combined by a union bound, and a single budget along a threshold path fixed before the calibration labels are seen, with the path either matching quantiles of the two scores or admitting the claims in a set order [Angelopoulos2025; LauferGoldshtein2023]. All three follow one recipe, and a contract with a Monte Carlo acceptance check lets further forms be added. Exchangeability of the calibration samples is created by design: a predetermined hierarchical design fixes the population of every level, and an order of operations that forbids anticipation keeps each level's guarantee valid whatever the campaign did before. The workflow is tested on a synthetic small-angle scattering phase map of a three-component surfactant–oil–water formulation, a NaCl microdiffraction scan [ALSNaCl] and an infrared map of a bioreef sample, and every bound is checked against the fully measured truth. Finally, six acceptance metrics compared on the same data show how the certified claim, under a guarantee that holds for each, decides where measurements are taken and where wrong skips gather. Sections 2 to 6 cover related work, the workflow, the experiments, the results, and the scope of the guarantee and its use at an instrument.



# 2 Related work

**Adaptive mapping.** Scanning instruments spend most of their time on sites that add little to the final map, and adaptive acquisition puts that time where the map is uncertain or interesting. Gaussian-process regression drives autonomous small-angle scattering and diffraction mapping at synchrotron and neutron facilities [Noack2019; Noack2020; Noack2021]. Bayesian active learning maps phase diagrams of composition spreads on the fly at the beamline [Kusne2020]. Dynamic sampling selects each new pixel of a point-wise image by the expected reduction in distortion and stops once an estimated distortion is reached [Godaliyadda2018]. Scanning probe and electron microscopes run comparable loops of measurement, model update and choice of the next location [Kalinin2021; Ziatdinov2022]. These methods decide where to measure and judge the result through the model that made the decision. The sites left out enter the final map as predictions, and their error is estimated by that same model.

**Distribution-free risk control.** Distribution-free inference attaches finite-sample statements to the output of an arbitrary predictor, with exchangeability of the calibration data as the only assumption [Vovk2005; Angelopoulos2023]. Risk-controlling prediction sets bound the population rate of a chosen loss from a held-out sample [Bates2021], Learn-then-Test extends the bound to any family of decision rules searched in a fixed order or with a multiple-testing correction [Angelopoulos2025], and conformal risk control bounds an expected loss [Angelopoulos2024]. Several risks can be controlled at once, and a path through a family of rules can be learned on part of the data [LauferGoldshtein2023]. Conformal selection controls the false-discovery rate among the items a model selects [Jin2023], a statement close in spirit to a bound on wrong skips among the skipped sites. In imaging, risk-controlling prediction sets give per-pixel intervals for image-to-image regression, calibrated on held-out images [Angelopoulos2022]. The present work uses these results as they stand. Its contribution on this side is to pose a skip as a claim about a site, so that the claims of a mapping campaign become the losses these methods control.

**Exchangeability in space.** Spatial data are dependent, and a calibration sample drawn from a map is exchangeable with the rest of the map only under conditions. Spatial conformal prediction obtains exact or approximate exchangeability from properties of the spatial process, for instance local approximate exchangeability around a prediction location for a broad class of processes [Mao2024]. Design-based inference takes the opposite route and places the randomness in the sampling plan, so that statements about a finite population hold whatever the values in it [Neyman1934; Cochran1977]. The campaign here follows the second route. A predetermined hierarchical design [Bridson2007] fixes the population of every level, and a uniform audit draw makes the calibration sample exchangeable with that population, conditionally on everything the campaign did before. The statement then concerns the design sites of a level, and needs no model of the spatial dependence.

**Adaptive sensing with guarantees.** Two recent lines of work bring calibrated uncertainty into the acquisition loop itself. In photon-limited scanning microscopy, pixel-wise conformal intervals decide which pixels to re-scan [Ye2025]. In rate-adaptive sensing, a conformal criterion decides when enough has been acquired [YangZhang2026]. Both calibrate on data collected outside the running acquisition. Power-system security screening offers the closest construction outside imaging: a label-independent audit drawn from the current operating window certifies the violation rate among contingencies that a cheap surrogate lets the operator skip, and the surrogate affects the cost of the certificate and leaves its validity untouched [Manoharan2026]. These works and the present one answer the same need for checkable statements about automated decisions, each for its own setting. The present work adds one answer for mapping: it certifies each skipped site of a running scan by one of two claims with a shared wrong-skip event, takes its calibration sample from the scan itself through the design, offers several forms of guarantee on that event, and checks every statement against fully measured truth on three instruments.




# 3 Framework

*Notation: level $L$ with $N_L$ design sites, frozen score $S_j$ per certificate $j$, calibration draw of $m$ sites.*

## 3.1 Design and order of operations

A finite-sample guarantee about skipped sites needs a calibration sample that is exchangeable with the sites it speaks for [Vovk2005]. Here the design creates that exchangeability. The population of every level is fixed before the experiment, and a uniform random draw from that population is the only source of randomness the guarantee relies on, as in design-based survey inference [Neyman1934; Cochran1977]. The guarantee needs no model of the spatial field or of the noise.

A hierarchical Poisson-disk design [Bridson2007] partitions the scan into nested levels of increasing density. The coarsest levels form the seed and are measured in full. Each finer level is then processed once, in order, in five steps (Fig. 1):

1. *Fit.* The predictor and the scores are fitted on the sites measured so far.
2. *Freeze.* Scores and predictor are fixed for every site of the level, and so is the decision rule: the family of thresholds, the budget and its split, and the number of calibration failures the level may allow.
3. *Draw.* A calibration sample of $m$ sites is drawn uniformly without replacement from the level, with randomness independent of everything else.
4. *Calibrate.* The calibration sites are measured, their labels are evaluated against the frozen predictor, and the rule turns the labels into thresholds.
5. *Decide.* Covered sites of the remainder are skipped and the others measured; every measured site joins the measured set for the next level.

**Figure 1.** The workflow. (a) Hierarchical design of the IR map: levels 0–2 form the seed, and each finer level fills the gaps of the coarser ones. (b) The five steps on one level; the calibration draw is the only random element of the guarantee, and its labels are unseen until the rule is frozen. (c) The two claims: a skipped site is covered as not of interest ($A$), as predictable ($B$) or both, and the skip is wrong when a covering claim is false. The guarantee bounds the share of level-$L$ sites at which the shared event $E$ occurs. File: `figures/fig1_schematic.png`.

Non-anticipation ties the steps together: nothing that shapes the guarantee on a level may depend on that level's draw, except through the rule fixed in step 2. Three practices that look harmless break it, and Section 5.1 shows each failing: refitting the scores on the calibration labels before the threshold is set, taking the calibration sample where the model is least sure, and keeping the most favourable of several draws. The condition concerns the draw and the rule. A score may use anything known before the draw, including physical models, other datasets or prior beliefs; a poor score costs measurements and leaves the guarantee intact.

Measuring one site must also leave the outcome of every other site unchanged. Radiation damage that spreads beyond the probed spot, or sample drift triggered by the measurement order, would let the draw alter the population it is meant to sample.

Given everything that precedes the draw of a level, its population, scores, labels and rule are fixed, so the guarantee holds conditionally on the history of the campaign and adaptivity across levels leaves it intact. Statements about several levels follow from the union bound; Appendix A states the conditions formally.

## 3.2 Labels and certificates

A skip is useful only if it says something that a measurement could contradict. Two claims serve that purpose. The interest certificate claims that a site holds nothing of interest; its label $Z(x) = 1$ marks a site whose measured spectrum meets the interest criterion of the dataset, such as a diffraction line standing clear of the noise. The interpolation certificate claims that a site is predictable; its label $F(x) = 1$ marks a site where the prediction from the coarser levels misses the acceptance metric. The metric fixes what predictable means: agreement of the full spectrum within an envelope, or agreement of a quantity derived from it, such as a peak position or width, within a tolerance. Both labels are functions of the true spectrum and of the frozen predictor. In a campaign they are known only at measured sites, and for this study they are known everywhere.

A certificate is the mechanism, and a claim is what it states about a site. Each certificate carries a score that orders the sites of a level from most to least safe to skip. The score has no other role: any function of the data available before the draw may serve, and its quality decides the number of measurements spent. The choice of metric decides more, since it sets where predictions fail and therefore where the campaign measures (Section 5.5).

## 3.3 The guarantee

A skip deserves a statement that a measurement could check. At level $L$, certificate $j$ covers the sites whose frozen score lies at or below a threshold $\tau_j$. A covered site is a wrong skip when the claim of the certificate fails there, marked by $B_j(x) = 1$. The controlled quantity is the rate of wrong skips over the level population:

$$
R_j(\tau_j) = N_L^{-1} \, \#\{x \in D_L : S_j(x) \le \tau_j,\ B_j(x) = 1\}
$$

The threshold comes from $m$ sites drawn uniformly, without replacement, from the level after the scores are frozen and then measured. Let $H$ count the failing sites in such a draw from a level in which $\lfloor \varepsilon N_L \rfloor + 1$ sites fail. With $k$ the largest integer for which

$$
P(H \le k) \le \delta
$$

every site scored below the $(k+1)$-th failing calibration site is covered. The guarantee

$$
P\big(R_j(\hat\tau_j) \le \varepsilon\big) \ge 1 - \delta
$$

holds over the draw, for any score and any predictor [Wilks1941; Bates2021; Angelopoulos2025]. The argument needs only a rate that grows with the threshold and a uniform draw; Appendix A gives it. Allowing no failure in the draw gives, in the binomial approximation, the smallest budget that $m$ sites can certify, $\varepsilon_{\min} = 1 - \delta^{1/m}$.

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

alongside a separate guarantee for each claim. The split leaves each certificate a smaller budget at a higher confidence. Once $\varepsilon_j$ falls below $\varepsilon_{\min}$, no threshold exists and the level is measured in full.

**One budget along a path.** A single budget spends all of $\varepsilon$ and $\delta$ on $R_E$. Two thresholds cannot be read off one draw by an order statistic, and Learn-then-Test supplies the remedy: search a family of thresholds fixed before any label is seen [Angelopoulos2025]. Here the family is a path $\lambda \mapsto (\tau_a(\lambda), \tau_b(\lambda))$, built from the frozen scores alone, along which both thresholds rise. The wrong-skip sets along such a path are nested, $R_E(\lambda)$ grows with $\lambda$, and the rule of Section 3.3 applies with $\lambda$ in place of the threshold (Appendix B). Two paths are used. The quantile path moves both thresholds through matching quantiles of their scores on the level. The priority path admits the claims in a set order: the first claim sweeps its quantiles before the second moves. A preference, for instance to skip a site as uninteresting before relying on interpolation, thereby enters the decision with the guarantee intact, because the order is fixed in advance.

**Further forms.** The forms above share one recipe: scores frozen before the draw, a uniform calibration draw from the level, and a decision rule whose family of thresholds is fixed before the calibration labels are known. Any rule built this way inherits a finite-sample guarantee (Section 6), including a bound on a conditional rate (Appendix C). Table 3 summarises the forms; SI 4 lists the conditions a new form must meet and a Monte Carlo acceptance check that every form here passes.

**Table 3.** Forms of guarantee on the wrong-skip event of one level. Every form uses the same frozen scores and the same calibration draw.

| Form | Guarantee, with probability at least the stated confidence | Budget | Given up | Suited to |
| --- | --- | --- | --- | --- |
| Per-claim budgets | $R_a \le \varepsilon_a$ and $R_b \le \varepsilon_b$; hence $R_E \le \varepsilon_a + \varepsilon_b$ at $1 - \delta_a - \delta_b$ | Split between the claims | Budget per claim; no threshold once $\varepsilon_j < \varepsilon_{\min}$ | Reporting how often each reason for skipping fails |
| Quantile path | $R_E \le \varepsilon$ at $1 - \delta$ | Whole budget on $R_E$ | Guarantee per claim; path shape set in advance | Bounding how often any skip fails |
| Priority path | $R_E \le \varepsilon$ at $1 - \delta$ | Whole budget on $R_E$, spent on the claims in order | Guarantee per claim; a later claim may receive no budget | A set preference between the claims |
| Conditional rate (Appendix C) | Failure rate among sites skipped by one claim $\le \alpha$ at $1 - \delta$ | One claim | Coverage at small $m$: at $m = 40$ it certifies nothing or more than half a level | Large calibration samples |

## 3.5 What is claimed and what is checked

A guarantee is only as useful as its scope is clear. Each guarantee of Sections 3.3 and 3.4 concerns the design sites of one level and the predictor frozen for that level. Its probability is taken over the calibration draw of that level. It bounds how many skips fail, and the location of the failures is left open. It says nothing about points between design sites, nor about the final map, which draws on measurements made after the level was decided.

Two further statements accompany each level. The rate of wrong skips among the sites left after calibration, the remainder, follows from the same draw. The map bound states, from the calibration labels of a level, an upper confidence limit on the share of that level's sites that the map built from the coarser levels predicts outside tolerance [ClopperPearson1934]; Appendix D gives its confidence when the draw also serves the decision.



# 4 Experiments

## 4.1 Datasets

Every guarantee in this study can be checked, because each dataset is measured at every design site. Three datasets cover a simulation with known phase structure, a diffraction scan and a spectroscopic map.

*Synthetic small-angle scattering map.* A forward model of a surfactant–oil–water formulation maps a composition in the triangle $x + y \le 1$ to a scattering curve on 240 logarithmically spaced points between 0.005 and 0.32 Å⁻¹. The model has a micellar phase, an ordered cubic phase, a hexagonal phase and an oil-rich emulsion, with smoothed transitions. A hierarchical Poisson-disk design on the unit square with nine levels, restricted to the triangle, gives 2118 sites. The interpolant uses mirror images across the walls of the triangle.

*NaCl microdiffraction scan.* A raster of 3249 sites on a 0.25 mm stage grid, with curves of 1000 bins between 0.59 and 38.9 nm⁻¹ [ALSNaCl]. A seven-level design, snapped to the raster, gives 1071 sites.

*Infrared map.* A bioreef sample mapped on 29 × 42 pixels of 1 µm, with 1738 channels between 650 and 4000 cm⁻¹. Each spectrum is corrected for resonant Mie scattering pixel by pixel, and the window 1500–1850 cm⁻¹, which holds the amide and ester bands, is used. A seven-level design drawn on the physical rectangle and snapped to pixels gives 959 sites. SI 2 describes the correction and the design.

## 4.2 Claims and tolerances

Each dataset carries one interest claim and one interpolation claim, fixed before any run.

| Dataset | Interest: a site holds | Interpolation: the prediction from coarser levels meets |
| --- | --- | --- |
| Synthetic map | a dominant peak rising above its local baseline by at least five times that baseline | the dominant-peak position within 0.005 Å⁻¹ and its width within 0.001 Å⁻¹ |
| NaCl scan | the (200) line at 22.28 nm⁻¹, at least five noise levels above its local baseline | the (200) width within 0.02 nm⁻¹, about half a detector bin |
| IR map | absorbance of 0.1 or more in some channel of the window | every channel within 10 % + 0.10 absorbance, on average over channels above 0.02 |

A second setting of the IR map tightens the envelope to 10 % + 0.01, with interest at 0.02 and channels counted above 0.005. Under it, interpolation rather than interest decides the cost. The choice of claim shapes the campaign as much as the budget does; Section 5.5 and SI 6 compare six metrics on the three datasets.

## 4.3 Protocols

**Natural-neighbour protocol.** Natural-neighbour (Sibson) coordinates [Sibson1981] predict the spectrum at a site as a weighted mean of the measured spectra around it. One set of weights per site serves every channel and every derived quantity. The coordinates are computed exactly by clipping Voronoi cells (SI 1); outside the hull of the measured set, inverse-distance weights over the five nearest measured sites take over.

The interpolation score is one minus the probability of acceptance from a logistic regression. The regression is fitted by leave-one-out on the measured set (at most 120 sites), on the disagreement between natural neighbours in units of the acceptance metric and on the position. The interest score depends on the dataset. On the IR map it is the predicted maximum in the window, capped below the interest level, so that a site predicted to be of interest is never covered. On the two scattering datasets it is the probability of interest from a logistic regression on the predicted peak height above its baseline, the spread of that height over the five nearest measured sites and the distance to the nearest of them. The random scorer of Section 5.1 assigns every site an independent uniform weight.

**Gaussian-process protocols.** Gaussian-process regression is the interpolator of choice for autonomous scattering experiments [Noack2019; Noack2020], and it offers a reason for every measurement: the posterior standard deviation is large where the measured set is far away in units of the length scale. The GP protocols place an isotropic squared-exponential kernel on the coordinates of the hierarchical design and evaluate the process only at design sites [RasmussenWilliams2006]. The posterior mean predicts the full spectrum at a site; the posterior standard deviation at unit output scale orders the sites for the interpolation certificate. Both depend on the measured set through one set of linear weights, so the spectrum and any quantity derived from it come from the same fit, as with natural-neighbour coordinates. The interest certificate keeps its score from the natural-neighbour protocol, which isolates the change of interpolator.

The length scale is set in three ways, each fixed before the calibration draw of a level. In the first, it maximises the marginal likelihood of the leading three principal-component scores of the measured spectra, with one length scale shared by the components [Balandat2020]. In the second, it equals the median nearest-neighbour spacing of the design through the finest level already measured, a quantity known before the experiment starts. In the third, the length scale varies across the sample: a Gibbs kernel [Gibbs1997; PaciorekSchervish2004] takes as local length scale the distance to the third-nearest measured site. Measurements guided by the interest certificate cluster where the sample holds something of interest and thin out elsewhere, so the local length scale is short in the first regions and long in the second. Details, including the nugget and the bounds on the length scale, are in SI 1.

**Common settings.** Levels up to the second form the seed and are measured in full. Every finer level is calibrated on $m = 40$ sites, or on the whole level when it is smaller. The guarantee on the shared wrong-skip rate is $R_E \le 0.10$ at confidence 0.75 on the IR map and $R_E \le 0.20$ at confidence 0.80 on the NaCl and synthetic maps. The per-claim form splits it as in Section 5.2. Every rule uses the exact finite-population tail, and the threshold is placed at the score of the first calibration failure beyond those allowed.

**Table 1.** Exchangeable parts of a campaign.

| Part | Options used |
| --- | --- |
| Design | Hierarchical Poisson-disk design; seed of levels 0–2; 7 (NaCl, IR) or 9 (synthetic) levels |
| Interpolator | Natural-neighbour coordinates; Gaussian process with length scale by maximum likelihood, by design spacing or by local spacing |
| Interest score | Predicted maximum (IR); logistic on predicted peak height (NaCl, synthetic); random |
| Interpolation score | Logistic on neighbour disagreement; GP posterior standard deviation; random |
| Form of guarantee | Per-claim budgets; quantile path; priority path |
| Calibration | 40 sites per level, uniform without replacement, exact hypergeometric tail |

## 4.4 Evaluation

A guarantee about a probability needs repetition to be checked. Each of 36 configurations was run as 250 campaigns that differ only in their calibration draws and, for the random scorer, in the score stream. Every certified level of every campaign gives one level check: the realised wrong-skip rate, computed against the truth, is compared with the budget. The number of checks over budget is compared with the number allowed by the failure probability the rule picked on each level (Section 5.1). For the first five campaigns of each configuration, the calibration draw was also repeated 500 times on the recorded level populations, which isolates the randomness of the draw. The record, its format and the code are described in SI 4 and SI 5.



# 5 Results

*All numbers below come from the run record: 36 configurations, each run as 250 independent campaigns with their own calibration draws (SI 5).*

## 5.1 The guarantee holds

A guarantee is worth only as much as its record of being kept. Every configuration in this study was therefore run 250 times, and every certified level of every campaign was checked against the fully measured truth (SI 5).

The failure probability a level actually carries is set by the calibration sample. The rule allows $k$ failing calibration sites, and the worst-case probability of exceeding the budget at that $k$ takes only a few values: with 40 calibration sites and a budget of 0.10 on a level of 428 sites, allowing 2 failures gives 0.206 and allowing 3 gives 0.410. The rule picks the largest of these values at or below the nominal $\delta$, and that picked value $\delta_L$ is the failure probability the level guarantees. On the levels of this study, $\delta_L$ averaged 0.19 against a nominal 0.25 for the IR map and 0.11 to 0.12 against 0.20 for the NaCl and synthetic maps. The observed exceedances are to be compared with $\delta_L$.

Measured against the picked levels, the record agrees with the guarantee. For the 32 stated rates (configuration and statement) whose budget can be exceeded on every level, union-bound statements excluded, the observed number of exceedances lay between 0.88 and 1.11 times the number the picked levels allow, and none exceeded it beyond chance: the smallest one-sided probability of the observed count under the picked levels was 0.13 (SI 5, Table S5.3). The IR map at its tight tolerance, for instance, allowed 190 exceedances in 1000 level checks and showed 193 with natural-neighbour interpolation and 179 to 191 with the Gaussian-process protocols. On the IR map at its original tolerance, three of the four levels hold too few failing sites for the budget to be reached: skipping every site that a certificate may cover leaves the wrong-skip rate below 0.10, so no exceedance is possible there and the record shows none. The union-bound statement of the per-claim form is exceeded far less often than its picked level allows, since two claims seldom approach their budgets on the same level. Repeating the calibration draw on the recorded level populations gives the same picture level by level: the attained exceedance probability lay between 0.90 and 1.06 times $\delta_L$ wherever the budget could be exceeded (SI 5, Table S5.2).

Table 2 gives one configuration per dataset: what was measured, why each skipped site was skipped, and how the record compares with the guarantee.

**Table 2.** One guarantee per dataset: quantile path, natural-neighbour interpolation, 250 campaigns; counts are means per campaign. Wrong skips are given as a share of the sites on certified levels. Allowed exceedances are the sums of the picked failure probabilities over the level checks.

| Dataset | Guarantee | Sites | Measured: seed / calibration / no claim | Skipped: not of interest / predictable / both | Wrong skips | Exceedances: observed / allowed |
| --- | --- | --- | --- | --- | --- | --- |
| IR map | $R_E \le 0.10$ at 0.75 | 959 | 73 / 160 / 62 | 37 / 228 / 399 | 34 (3.8 %) | 49 / 190 (56 on reachable levels) |
| IR map, tight tolerance | $R_E \le 0.10$ at 0.75 | 959 | 73 / 160 / 388 | 8 / 257 / 73 | 54 (6.1 %) | 193 / 190 |
| NaCl scan | $R_E \le 0.20$ at 0.80 | 1071 | 76 / 160 / 378 | 157 / 156 / 144 | 122 (12.3 %) | 112 / 120 |
| Synthetic map | $R_E \le 0.20$ at 0.80 | 2118 | 39 / 233 / 62 | 321 / 319 / 1144 | 270 (13.0 %) | 161 / 170 |

A score that carries no information leaves the guarantee intact. In a further set of configurations, a random scorer ordered the sites for every certificate: each site received an independent uniform weight, unrelated to any measurement. The shared rate exceeded its budget in 168 of 1000 level checks on IR, 194 of 1000 on IR at the tight tolerance, 127 of 1000 on NaCl and 161 of 1500 on the synthetic map, against 25 %, 25 %, 20 % and 20 % allowed (Fig. 2, lower row). The random order cost measurements: 716 ± 71 of 959 sites on IR against 295 ± 53 with informed scores, 871 ± 31 against 621 ± 70 at the tight tolerance, 861 ± 50 of 1071 against 614 ± 56 on NaCl, and 1076 ± 187 of 2118 against 334 ± 26 on the synthetic map (Fig. 2, upper row). The guarantee comes from the calibration draw; the score decides what it costs.

Breaking the order of operations breaks the guarantee (Section 3.1). On a level of 399 sites with informative scores, a budget of 0.10 and a picked failure probability of 0.206, the calibration draw was repeated 4000 times under five rules. With scores frozen before a uniform draw, the budget was exceeded in 822 draws (0.205). A score that knew the true labels but was frozen before the draw gave 819 (0.205): what the score knows changes the cost and leaves the guarantee intact. Raising the scores of the failing calibration sites after the draw and thresholding on the same labels exceeded the budget in every draw. Taking the calibration sample from the half of the level the scores rank as least safe, as an active learner would, gave 2502 exceedances (0.63), and keeping the most favourable of five draws gave 2771 (0.69).

**Figure 2.** Informed against random scores, quantile path, 250 campaigns per configuration. Upper row: sites measured, mean ± s.d., with the design size dashed. Lower row: realised wrong-skip rate on every certified level of every campaign, with the budget as a solid line; tick labels give the number of exceedances. File: `figures/fig2_random.png`.

## 5.2 Forms of guarantee

A choice between forms of guarantee needs their costs on real data. Each form of Table 3 was run on all three datasets at one nominal guarantee on the shared event: $R_E \le 0.10$ at confidence 0.75 for the IR map, $R_E \le 0.20$ at confidence 0.80 for the NaCl scan and the synthetic map. The per-claim form reached that guarantee through a split, 0.10 at confidence 0.90 per claim for NaCl and the synthetic map, 0.05 at confidence 0.875 for IR. All runs used exact natural-neighbour interpolation and the logistic scores of Section 4.

Every stated rate held (Fig. 3, lower row). The shared rate exceeded its budget in 0, 49 and 49 of 1000 level checks for the three IR forms, in 9, 112 and 123 of 1000 for NaCl, and in 5, 161 and 156 of 1500 for the synthetic map. The per-claim guarantees of the split form exceeded their budgets in 37 and 0 of 1000 checks on IR (12.5 % allowed), 64 and 57 of 1000 on NaCl and 73 and 67 of 1500 on the synthetic map (10 % allowed). The shared guarantee of the split form, obtained through the union bound, was almost never exceeded: two claims seldom approach their budgets on the same level.

The forms differ in cost, and the ordering changes between datasets (Fig. 3, upper row; Table S3.1). On IR the per-claim form measured 262 ± 28 of 959 sites, the quantile path 295 ± 53 and the priority path 327 ± 80. The per-claim split is feasible on IR only through the exact finite-population tail: on levels of 71 to 428 sites, a draw of 40 without replacement admits zero failures at a budget of 0.05 and confidence 0.875, where the binomial approximation admits none. On NaCl, the quantile path was the least expensive form (614 ± 56 of 1071 sites, against 719 ± 60 and 678 ± 39). On the synthetic map, the per-claim form and the quantile path cost the same within their spread (338 ± 26 and 334 ± 26 of 2118), and the priority path almost twice as much (628 ± 61). No form is the least expensive on all three datasets.

The priority path admitted the interest claim first, and the order shows in the reasons recorded for each skip. On NaCl and on the synthetic map, the interest claim took the whole budget: in every campaign, every skipped site was skipped as uninteresting. On IR, the interest claim applies only below an intensity cap, so its sweep ends early and interpolation receives the rest of the budget.

A rule that breaks the recipe loses its guarantee. The sequential rule of the original IR analysis chooses the interest threshold on the calibration draw and then the interpolation threshold on the calibration sites left uncovered, from the remaining budget. On a population with uninformative scores (399 sites; interest and failure labels at rates 0.5 and 0.1), it exceeded $R_E = 0.10$ in 1150 of 4000 draws, a frequency of 0.288 against 0.25 allowed (Monte Carlo standard error 0.007). The priority path expresses the same preference with the order fixed in advance and exceeded the bound in 819 of 4000 draws; the quantile path did so in 832 (Fig. 3, right).

**Figure 3.** Forms of guarantee, 250 campaigns per configuration. Upper row: sites measured per form, mean ± s.d., with the design size dashed. Lower row: realised wrong-skip rate on every certified level of every campaign, with the budget as a solid line; tick labels give the number of exceedances. Right: fraction of 4000 calibration draws in which $R_E$ exceeded 0.10 on a population with uninformative scores, for the sequential rule and the two single-budget paths; the band marks ±2 Monte Carlo standard errors around the allowed 0.25. File: `figures/fig3_forms.png`.

## 5.3 The cost of a guarantee across protocols

A guarantee is of use only if it holds whichever interpolator proposes the skips. The quantile path was therefore run with four interpolation protocols on each dataset, at the nominal guarantees of Section 5.2: natural-neighbour interpolation with the logistic score, and Gaussian-process interpolation with the posterior standard deviation as score and the length scale set by maximum likelihood, by the design spacing or by the local spacing of measured sites (Section 4.3). The IR map was run at two tolerances. At its original tolerance of ±(10 % + 0.10) absorbance almost every site is interpolable by any method, and the interest claim alone sets the cost; at ±(10 % + 0.01), with interest at 0.02, interpolation decides.

Every guarantee held (Fig. 4, lower row). In the order listed, the shared rate exceeded its budget in 49, 49, 50 and 2 of 1000 level checks on IR at the original tolerance, in 193, 179, 190 and 191 of 1000 at the tight tolerance (25 % allowed), in 112, 119, 110 and 119 of 1000 on NaCl, and in 161, 160, 184 and 161 of 1500 on the synthetic map (20 % allowed).

The cost depends on the protocol and on the data (Fig. 4, upper row; Table S3.2). At the original IR tolerance the four protocols measured 295 ± 53, 273 ± 31, 283 ± 34 and 295 ± 42 of 959 sites, and their skipped sets overlapped by about 90 % (Jaccard index 0.89 to 0.92). At the tight tolerance they measured 621 ± 70, 750 ± 55, 757 ± 53 and 804 ± 37, and the Gaussian-process protocols shared a quarter to a third of their skips with natural-neighbour interpolation (Jaccard index 0.26 to 0.33). On NaCl, the Gaussian-process protocols measured 745 to 778 of 1071 sites, against 614 ± 56. On the synthetic map they measured between 1042 ± 201 and 1447 ± 134 of 2118 sites, against 334 ± 26. In every case the difference arises in the calibration draws: the Gaussian-process predictions missed the tolerance at more calibration sites, and more failures among the calibration sites admit fewer skips at the same budget. The guarantee itself is unchanged.

The three length-scale rules lead to visibly different reasons for measuring a site, from a standard deviation high in every gap between measured sites to one that is nearly uniform (Fig. S1; SI 1).

**Figure 4.** The cost of one guarantee across interpolation protocols, quantile path, 250 campaigns per configuration. Columns: IR map at the original and at the tight tolerance, NaCl scan, synthetic map. Upper row: sites measured, mean ± s.d., with the design size dashed. Lower row: realised wrong-skip rate on every certified level of every campaign, with the budget; tick labels give the number of exceedances. GP: Gaussian process with isotropic squared-exponential kernel; length scale by maximum likelihood, by design spacing, or by local spacing of measured sites. File: `figures/fig4_protocols.png`.

## 5.4 Maps with reasons

A guarantee on rates becomes useful at an instrument once every site of a map carries its reason. Figure 5 shows one campaign per dataset under the quantile path with natural-neighbour interpolation (seed 0 of the record), with every design site marked by the reason recorded for it and every wrong skip found against the fully measured truth.

In the campaigns shown, the wrong skips were 2.3 % of the sites on certified levels of the IR map, against a budget of 0.10 per level, and 13.3 % on NaCl and 10.3 % on the synthetic map, against 0.20; the panel titles give the counts by reason. The wrong skips of the synthetic map gather in two compact regions of the composition triangle; the guarantee bounds their rate on each level and leaves their location open (Section 5.5).

The map bound states, from the calibration draw of a level, how many of its sites the map built from coarser levels predicts outside tolerance. For the last level of these campaigns it allowed at most 3.4 % on IR (0 of 40 calibration sites failed; actual 0.2 %), 47.9 % on NaCl (16 of 40; actual 49.9 %) and 16.2 % on the synthetic map (4 of 40; actual 10.1 %). The NaCl campaign shown is one in which the bound missed. Over the 250 campaigns of each configuration, the map bound held on 100 % of the certified levels for IR, 88.5 % for NaCl and 90.4 % for the synthetic map, against confidences of 0.75, 0.80 and 0.80. On NaCl, about half of the last-level sites lie outside tolerance of the map built from coarser levels; the skip guarantee is unaffected, since it concerns only the sites a certificate covers.

**Figure 5.** Maps with reasons, one campaign per dataset (quantile path, natural-neighbour interpolation, seed 0). Measured sites: seed (diamonds), calibration (orange squares) and sites without a claim (grey squares). Skipped sites: not of interest (yellow), predictable (aqua) and both (blue). Crosses: wrong skips against the fully measured truth. Panel titles give the guarantee, the counts and the wrong-skip share of the sites on certified levels; the text under each panel gives the map bound of the last level. IR in micrometres, NaCl in stage millimetres, synthetic map in composition fractions. File: `figures/fig5_maps.png`.


## 5.5 What the guarantee buys

A guarantee covers the claim it is given, so the choice of claim needs its own record. Six acceptance metrics were compared on the three datasets with the interpolation certificate alone and 50 campaigns per metric: peak or line descriptors with absolute or relative tolerance, two forms of profile envelope, and the error in a basis of the seed spectra, plain or with near-duplicate spectra merged (SI 6). Every metric kept its guarantee. Over 32 combinations of metric, dataset and tolerance, the largest ratio of observed to allowed exceedances was 1.37, with a one-sided probability of 0.04 under the picked levels; all other ratios were at most 1.08.

The metric set the cost. At tolerances a practitioner might pick, the share of certified-level sites that a prediction fails ranged from 1 % to 85 %, and the IR map needed between 233 and 810 measurements. Scaling every tolerance so that 15 % of the sites fail, a control that uses the truth, brought the costs close: 338–453 sites on IR, 287–367 on NaCl and 398–461 on the synthetic map.

At equal difficulty the metric still decided where measurements go (Fig. 6). On the synthetic map the peak claim measured where the peak position and width drift with composition, in the micellar phase and in a band of the emulsion. The profile claim measured along the phase boundaries: 45–46 % of its measurements fell on the 8.8 % of sites next to another phase, against 32 % for the peak claim. The two claims placed 31 % of their measurements on the same sites, and 16 % at the default tolerances.

The metric also decided where wrong skips fall. On IR, the metrics with an absolute term put 72–83 % of their wrong skips on sites with signal, which are 30 % of the skipped sites; the relative profile put them in proportion. On NaCl, the line-width claim put 6 % of its wrong skips on sites holding the (200) line, which are 66 % of the skipped sites: its failures sit where the line is weak or absent. Under every metric the wrong skips clustered, with another wrong skip among the six nearest neighbours 1.5 to 3.0 times as often as for wrong skips placed at random among the skipped sites. The rate also counts wrong skips over all sites of a level. On the synthetic map, where a third of the sites are of interest, 35 % of the interesting sites on certified levels were skipped in error while every level met its budget (SI 6.2). Merging near-duplicate seed spectra before building the basis changed cost and placement by a few per cent.

**Figure 6.** Where the certified claim sends the measurements: synthetic map, tolerances matched to equal difficulty, quantile path, 50 campaigns per claim. Colour gives the frequency with which a design site of a certified level was measured because no claim covered it, under the peak claim (a) and the profile claim (b); (c) gives their difference. Grey lines: phase boundaries of the forward model (L1 micellar, I1 cubic, H1 hexagonal, emulsion). File: `figures/fig6_metric.png`.


# 6 Discussion

## Scope of the guarantee

A map built under a guarantee serves its reader to the extent that the reader knows what the bound covers. The bound concerns the share of wrong skips among all design sites of a level, with probability over the calibration draw. Section 5.5 shows the two consequences: wrong skips gather in space, and when signal is rare a budget met on every level can still cost a large share of the sites of interest. A bound on the share of interesting sites lost calls for a label-conditional statement, calibrated on the calibration sites that hold signal [Vovk2005; Sadinle2019]. A uniform draw keeps those sites exchangeable with the interesting sites of the level, at the price of a calibration sample larger by the inverse of the share of interest; Appendix D gives the corresponding bound for the map. Calibration carries a fixed cost of 40 sites per certified level, up to a sixth of the IR map, a share that falls as maps grow, since the budget and the confidence alone set the sample size.

## What is certified shapes the campaign

A guarantee is stated for one acceptance metric, and the metric deserves the same care as the budget. The bound holds for any metric fixed before the calibration draw, and the metric decides the rest: which sites fail prediction, where measurements are taken and where wrong skips gather (Section 5.5). The same holds for any autonomous experiment: the quantity a model predicts, and the error its acquisition anticipates, decide where measurements are taken [Noack2019; Noack2020]. The guarantee delivers the claim as specified, and features outside that claim carry no protection. The metric is therefore best fixed from the scientific question before beam time, stated with the guarantee, and checked on a pilot scan for the cost it implies.

## Building other guarantees

The forms reported here address three questions about wrong skips, and an instrument may face others, each calling for its own form: unequal budgets when one claim is riskier than the other, a bound on the proportion of false skips among the skipped sites [Jin2023], or a path learned on part of the calibration draw [LauferGoldshtein2023]. Each follows the recipe of Section 3.4 and is accepted by the same Monte Carlo check (SI 4). The cost of a form on a given dataset is hard to predict in advance; Section 5.2 shows that the ordering of three forms changes between datasets. Running candidate forms on a fully measured pilot scan, as done here retrospectively, gives that cost before beam time is committed.

## Optimisation

Optimisation is the natural next case, and it differs from mapping in its population. A Bayesian optimiser or a self-driving laboratory proposes its next experiments from the model it has just fitted, so calibration points from earlier rounds are no longer exchangeable with its proposals. When the selection mechanism is known, as it is to the optimiser, calibration points can be reweighted by the likelihood ratio between proposals and calibration points, with bounds that widen where the optimiser concentrates [Tibshirani2019; Fannjiang2022; Barber2023]; online methods control a long-run error rate and give up the finite-sample statement at each step [Gibbs2021]. The construction of this work suggests a further route through level sets. A search for the maximum becomes a sequence of mapping problems, each asking where the response exceeds a threshold, which is the claim the interest certificate already makes. The threshold is meaningful as a quantile of the whole response: when a fraction $s$ of the domain survives and contains the top set, the quantile $q$ of the whole response is the quantile $1 - (1 - q)/s$ of the surviving region, and the order statistics of a uniform draw from that region bound it [DavidNagaraja2003]. With threshold and population fixed before each stage's calibration draw, conditions (A1)–(A6) of Appendix A hold stage by stage, much as adaptive levels do in multilevel splitting [CerouGuyader2007] and thresholds in active level-set estimation [Gotovos2013]. Each stage then bounds the fraction of sites above its threshold that were eliminated in error. The location of the single maximum lies beyond a rate statement of this kind, since a bounded fraction of wrong eliminations may include it.

## Accountability at the instrument

An accountable instrument needs a reason for every site and a statement that a reviewer can check. The workflow leaves both in its record. Each site carries its level, its scores, and the claim that covered it or the reason it was measured; each level carries its calibration draw, its picked failure probability and its bound. The guarantee rests on the order of operations, so the record suffices: predictor and scores are frozen and recorded before each draw, the draw comes from a recorded seed, and every decision can be replayed and every bound recomputed (SI 5). Claims, metrics and budgets remain the experimenter's choice and enter the record as such. The guarantee then states, for each claim, how often a skip made under it was wrong.



# 7 Conclusion

A skip decision can carry a checkable guarantee once it is posed as a claim about a site and calibrated on a uniform draw from a population fixed in advance. Hierarchical designs supply such populations at every level of an adaptive campaign, and the order fit, freeze, draw, calibrate, decide keeps each draw exchangeable with its level whatever came before. On three fully measured datasets the record matched the guarantees with informed and random scores, natural-neighbour and Gaussian-process interpolation, and three forms of guarantee; model quality and the form of the guarantee set the cost. The certified claim decides what the guarantee buys: where measurements are taken, where wrong skips gather and which sites carry protection. The claim therefore belongs to the scientific question and is best fixed with it, before beam time. Label-conditional bounds that protect the sites of interest, and optimisation through level sets referred to the whole response, are natural next steps. Each skipped site leaves the campaign with a reason, a claim and a bound, and the record allows every decision to be replayed.


# Appendix A. Exchangeability by design and the single-certificate bound

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
R(\tau) = N^{-1} \, \#\{x \in D : S(x) \le \tau,\ B(x) = 1\}
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



# Appendix B. Guarantees on the shared wrong-skip event

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


# Appendix C. A bound on the conditional rate

The rate bounded in Appendices A and B counts wrong skips among all sites of a level. A reader of the map may instead need the rate among the sites one claim covers. Learn then Test gives that bound for a family of thresholds fixed before the labels are seen [Angelopoulos2025].

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

The rates $R_i$ need not increase with $i$, so the hypotheses are tested in a fixed order: $H_1, H_2, \dots$, each at level $\delta$, stopping at the first that is not rejected. Fixed-sequence testing controls the family-wise error at $\delta$ [WestfallKrishen2001], so with probability at least $1 - \delta$ every rejected hypothesis is false. The rule covers $D_{i^\ast}$, where $i^\ast$ is the last rejection, and covers nothing when $H_1$ is not rejected. With probability at least $1 - \delta$,

$$
R_{i^\ast} \le \alpha
$$

**Minimum calibration size and starting quantile.** A hypothesis can be rejected only if its calibration sites can show a small enough tail even with no bad label, which requires $(1 - \alpha)^{n_i} \le \delta$, or

$$
n_i \ge n_{\min} = \lceil \log \delta / \log (1 - \alpha) \rceil
$$

The first threshold therefore covers at least the share $n_{\min}/m$ of the level, and $q_0$ is that share rounded up to a multiple of 0.05. With $\alpha = \delta = 0.10$, $n_{\min} = 22$, and at $m = 40$ the grid starts at the 0.55 quantile: the rule certifies nothing or more than half of the level. A useful conditional bound thus calls for calibration samples several times larger than the rate bounds of Appendices A and B need, which is why the main text reports those.


# Appendix D. The map bound

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
