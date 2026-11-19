# Paper plan: Machine Learning: Science and Technology

Target: MLST research paper, at most 8500 words in the main text. Theory stays light in the main text; derivations, formal statements and proofs go to the appendix and supporting information (SI). Every statistical step is attributed to its source.

## 1. Thesis and framing

**Framing.** The paper provides guaranteed, distribution-free safety margins on what a skipped measurement asserts. It argues neither speed nor superiority. Autonomous measurement decisions need accountability: a recorded reason for every skip and a checkable statement of how often skips are wrong. The paper offers one way to provide it, with guarantees that are precise and checked against truth. Other ways exist and are welcome; the record, the forms of guarantee and the acceptance check are built so that they can be compared on the same footing. The paper makes no priority or optimality claims.

**Thesis.** A scanning experiment can skip measurements and still state, for every level of a hierarchical design, a finite-sample bound on the rate of wrong skips. The bound comes from a uniform calibration draw. It holds for any interpolator, any scoring rule and any acquisition protocol that respects the order of operations: fit, freeze, draw, calibrate, decide.

**What the paper is about.** It is about which guarantees can be made, and at what cost in measurements. Every result is reported as a pair: the statement (wrong-skip rate ≤ ε at confidence c) and the number of measurements needed to make it. Protocols are exchangeable parts that show the guarantee survives a change of machinery. Protocols are never ranked by accuracy, and the paper claims no optimality for any interpolator, score or design.

**Guarantees come in forms.** Each guarantee is precise, and different needs call for different statements. A bound per reason for skipping tells how often "not interesting" failed and how often "predictable" failed. A bound on the shared event tells how often any skip failed, and spends the whole budget on that question. A bound on a conditional rate tells how often a skip of a given kind failed. The paper reports three forms side by side (per-claim budgets with a union bound, one budget along a quantile path, one budget along a priority path) and presents them as instances of one recipe: frozen scores, a uniform audit draw, and a decision rule fixed before the audit labels are seen. Readers build their own forms from the same recipe; the SI gives the contract a new form must keep and the Monte Carlo acceptance check it must pass. No form is presented as the right one.

**Ground rules for the text**

1. No "optimal", "best", "outperforms" or "state of the art" applied to a protocol. Comparisons read as cost per statement ("at R_E ≤ 0.10 with confidence 0.75, protocol A measured 269 of 949 sites and protocol B 321").
2. A protocol that measures more is reported as the price of that protocol's statement. It is not called worse.
3. Each guarantee is stated once, in one form, with its scope: design sites of one level, the predictor frozen at that level, probability over the calibration draw.
4. The statistical machinery is cited. Original content is limited to: the shared wrong-skip event for two certificates, the use of hierarchical levels to keep calibration exchangeable inside an adaptive campaign, and the empirical study.
5. Code, module and file names stay out of the main text; they go in the SI, referenced by section.
6. Every form of guarantee is reported on every dataset at the same nominal statement on the shared event. A form that cannot make the statement at m = 40 (the per-claim split on IR) is reported with its cost: every site measured.

**Working titles**

- Accountable skipping: finite-sample guarantees for measurements left out of scanning experiments
- Certified skips: distribution-free guarantees for adaptive scanning measurements
- What can be asserted about a measurement that was never made

## 2. Claims and their evidence

| # | Claim | Evidence | Leans on |
| --- | --- | --- | --- |
| C1 | At each level the population rate of wrong skips is at most ε with probability at least c over the calibration draw, whatever the score and interpolator. | Theory (appendix A); Monte Carlo coverage on finite populations; seed replication on the three datasets | Wilks 1941; Bates et al. 2021; Angelopoulos et al. 2025 (LTT) |
| C2 | "Not interesting" and "predictable" are two claims about a site with one shared wrong-skip event. Guarantees on that event come in several precise forms, each built from frozen scores, a uniform draw and a rule fixed before the labels: per-claim budgets with a union bound, one budget along a quantile path, one budget along a priority path. Further forms slot in under the same contract. | Theory (appendix B); MC acceptance check of every form; all three forms on all three datasets over 20 seeds; a sequential two-stage rule that breaks the contract fails its nominal rate, and its priority-path counterpart keeps it | Angelopoulos et al. 2025 (multiple risks, multi-dimensional λ); Laufer-Goldshtein et al. 2023 (Pareto Testing); Jin & Candès 2023; Bonferroni |
| C3 | Exchangeability is created by design: a predetermined hierarchical design gives each level a fixed population, and a uniform draw under non-anticipation (fit, freeze, draw, calibrate, decide; no interference) makes the calibration sample exchangeable with it, conditionally on the campaign history. Breaking the order breaks the guarantee. | Protocol description (§3.1, Appendix A); random-score runs keep the guarantee; order-of-operations Monte Carlo: refitting on calibration labels, active-learning calibration and best-of-five draws break it | Bridson 2007 / hierarchical Poisson-disk sampling; exchangeability as in Vovk et al. 2005; design-based inference (Neyman 1934; Cochran 1977) |
| C4 | The guarantee survives a change of protocol: interpolator (natural neighbour on spectra, on scalars, Gaussian process), score (random, neighbour disagreement, logistic, GP standard deviation) and budget scheme. Only the cost changes. | Protocol matrix (§5), coverage counts per protocol, measurements per statement | Sibson 1981; Rasmussen & Williams 2006; Noack et al. 2019 |
| C5 | Every skip carries a stated safety margin, and the record shows each margin met at its picked level; the price of a margin is reported as measurements spent, never as a ranking. | Run record (SI 5); maps with reasons (Fig. 5) | Noack et al. 2019, 2020; Ye et al. 2025 |

The paper rests on these five claims. Any figure that supports none of them goes to the SI.

## 3. Outline and word budget

| Section | Words | Content |
| --- | --- | --- |
| Abstract | 200 | Need, statement, three datasets, cost per statement, scope of the claim |
| 1 Introduction | 900 | See below |
| 2 Related work | 700 | Autonomous experimentation; distribution-free risk control; adaptive sensing with guarantees |
| 3 Framework | 1300 | Light; formal material in appendix |
| 4 Experiments | 1000 | Data, targets, tolerances, protocols |
| 5 Results | 2800 | Five subsections, one per claim |
| 6 Discussion | 1000 | Scope, limitations, use at an instrument |
| 7 Conclusion | 200 | |
| Total | 8100 | Leaves 400 words of margin |

### 1 Introduction (≈900 words, five paragraphs)

1. **Need.** Beam time, dose and sample lifetime limit how many sites of a map can be measured. Adaptive and autonomous protocols decide where to measure (Noack et al. 2019; Kusne et al. 2020). A skipped site enters the map as a prediction.
2. **Opportunity.** Distribution-free risk control attaches finite-sample statements to the outputs of black-box predictors (Vovk et al. 2005; Angelopoulos & Bates 2023; Bates et al. 2021; Angelopoulos et al. 2025). It applies to a skip decision once the skip is posed as a claim about a site.
3. **What a skip claims.** Two claims cover the cases met in practice: the site holds nothing of interest, or its spectrum (or a quantity derived from it) is predictable within tolerance from coarser measurements. A skip is wrong when a claim that covers it is false.
4. **What this paper provides.** A protocol that asserts, level by level, a bound on the wrong-skip rate. The guarantee is separated from the choice of interpolator, score and acquisition order, so that any of them can change without changing what is claimed.
5. **Contributions and scope.** (i) The shared wrong-skip event and guarantees on it in several forms, built from existing risk-control results, with a contract for adding more; (ii) hierarchical designs as the source of exchangeable calibration in an adaptive campaign; (iii) a study on synthetic SAXS, a NaCl microdiffraction scan and an IR map across protocols, reporting what is asserted and what it costs. One explicit sentence: optimality of the underlying algorithms is outside the scope.

### 2 Related work (≈700 words)

- **Autonomous and adaptive experimentation.** GP-driven X-ray scattering (Noack et al. 2019, 2020), closed-loop materials discovery (Kusne et al. 2020), dynamic sampling (SLADS; Godaly et al. 2018 for crystal positioning). These choose measurements. The present work attaches a statement to the measurements left out.
- **Distribution-free risk control.** Conformal prediction (Vovk et al. 2005; Lei et al. 2018), risk-controlling prediction sets (Bates et al. 2021), Learn-then-Test and multiple risks (Angelopoulos et al. 2025), conformal risk control (Angelopoulos et al. 2024), Pareto Testing (Laufer-Goldshtein et al. 2023), conformal selection with false-discovery control (Jin & Candès 2023).
- **Adaptive sensing with guarantees.** Pixel-wise conformal intervals driving re-scans in microscopy (Ye et al. 2025); conformal stopping for acquisition rate (CoRAS; Yang & Zhang 2026). Differences stated as scope: per-site skip certificates, two certificates at once, a hierarchical design that keeps calibration exchangeable, and real instruments with retrospective truth.

### 3 Framework (≈1300 words, light)

- **3.1 Design and order of operations.** Hierarchical design; seed; per level: fit and freeze scores on the measured set, draw calibration, measure it, decide. One schematic figure (Fig. 1).
- **3.2 Labels and certificates.** Interest label and failure label defined on the truth; target map (full spectrum or derived scalar) and acceptance score. Scores order sites and nothing else.
- **3.3 The statement.** Joint rate of wrong skips on a level; the order-statistic threshold; confidence over the draw. One displayed equation for the rate, one for the allowed failure count. Citation: Wilks 1941; Bates et al. 2021. Proof → appendix A.
- **3.4 Forms of guarantee.** Shared wrong-skip event. Three forms, each one paragraph: per-claim budgets with a union bound (a statement per reason and one on the shared event); one budget along a quantile path fixed before labels (an instance of LTT with a one-dimensional fixed sequence; Angelopoulos et al. 2025); one budget along a priority path that admits the claims in a set order. Table 3 states what each form asserts and what it gives up. One closing paragraph: the recipe (frozen scores, uniform draw, rule fixed before labels) admits further forms, with pointers to Pareto Testing (Laufer-Goldshtein et al. 2023), conformal selection (Jin & Candès 2023) and the conditional rate (appendix C); the contract and acceptance check are in SI 4. Proof → appendix B.
- **3.5 What is claimed and what is checked.** Claims: design sites of a level, frozen predictor. Checks: remainder rates, map bound (Clopper & Pearson 1934), off-design audit, final map. Joint rate as the controlled quantity; conditional rate reported as an outcome, with the reason (a conditional claim at m = 40 needs LTT and certifies nothing or more than half a level; appendix C).

### 4 Experiments (≈1000 words)

- **4.1 Datasets.** Synthetic SAXS mixture (forward model, composition triangle with mirror images); NaCl microdiffraction scan (Dryad doi:10.5061/dryad.p2ngf1w4t); IR map of a bioreef sample (29 × 42 pixels of 1 µm) after a per-pixel resonant Mie correction (stage-1 ME-EMSC, each pixel seeded with its own spectrum; SI 2); design drawn in micrometres.
- **4.2 Targets and tolerances.** Each tolerance justified by physics or noise: NaCl (200) width against 0.02 nm⁻¹ with presence at 5σ; full-profile envelope; IR envelope in 1500–1850 cm⁻¹ with interest at absorbance 0.1. The 9.492 nm⁻¹ peak-q tolerance is dropped, or kept only as a labelled stress case.
- **4.3 Protocols.** Table of exchangeable parts (Table 1): interpolator × score × budget scheme × design. Calibration size, budgets and confidences fixed before any run.
- **4.4 Evaluation.** Statement held fixed per dataset. Outputs: measurements, skips by reason, level and remainder wrong-skip rates, coverage over 20 calibration seeds, audit.

### 5 Results (≈2800 words; one subsection per claim)

- **5.1 The statement holds (C1).** Fig. 2: exceedance frequency against nominal failure probability for every protocol and dataset (seed replication), with the MC finite-population panel. Random-score arm: realised skip fraction against the expected value.
- **5.2 Forms of guarantee (C2).** Fig. 3: for each dataset, the three forms at the same nominal statement on the shared event, with measurements spent and exceedances over 20 seeds; per-claim rates for the union-bound form. The IR per-claim split admits no threshold at m = 40 and measures every site, reported as the price of a statement per reason at that calibration size. The sequential two-stage rule exceeds its nominal rate on an uninformative population; the priority path expresses the same preference and holds its rate. The text reads as cost per statement, with no winner declared.
- **5.3 The cost of a guarantee across protocols (C4).** Fig. 4: measurements needed per statement across the protocol matrix for each dataset. Same coverage across rows. Natural neighbour, scalar route and GP all appear.
- **5.4 Maps (C5).** Fig. 5: one map per dataset with the reason for every site (measured, audited, skipped as uninteresting, skipped as interpolable) and the map bound. (Matched-budget study dropped: the paper argues safety margins, not speed or accuracy.)

### 6 Discussion (≈1000 words)

- **Scope of the claim.** Per level, design sites, frozen predictor, probability over the draw. Simultaneous statements over levels by Bonferroni. The final map is audited.
- **Calibration overhead.** Calibration takes 40 of 65 sites at the coarsest certified level. Options: pooled or growing calibration (Barber et al. 2023 for weighted and non-exchangeable variants) and larger budgets at coarse levels.
- **Building other guarantees.** The forms in this paper answer three questions about wrong skips. Other needs (a bound on false skips among the skipped set, unequal budgets for the two claims, a path learned on part of the draw) call for other forms. Each is built from the same recipe and accepted by the same check (SI 4).
- **Conditional rates.** Reported as outcomes. Link to conformal selection (Jin & Candès 2023) as the route to conditional control at larger calibration sizes.
- **Use at an instrument.** The protocol needs only the measured set, a score and a random draw per level; a prospective run is the next step.
- **Numerical reproducibility of the interpolant** (one paragraph, details in SI).

## 4. Figures and tables

| Item | Content | Claim |
| --- | --- | --- |
| Fig. 1 | Schematic: hierarchical levels; fit → freeze → draw → calibrate → decide; the two certificates and the shared event | — |
| Fig. 2 | Informed against random scores (random scorer: independent uniform weights): cost and exceedances, quantile path, 250 campaigns per configuration (drafted: figures/fig2_random.png); coverage over all configurations in SI 5 | C1, C3 |
| Fig. 3 | Forms of guarantee: sites measured and level wrong-skip rates for three forms on three datasets; Monte Carlo panel with the sequential rule against the two paths (drafted: figures/fig3_forms.png) | C2 |
| Fig. 4 | Cost per statement across the protocol matrix (drafted for natural neighbour and three GP rules: figures/fig4_protocols.png) | C4 |
| Fig. 5 | Maps with reasons and map bound, one per dataset | C1, C5 |
| Table 1 | Protocol components (interpolator, score, budget scheme, design) and settings | C4 |
| Table 2 | Per dataset: statement, measurements, skips by reason, coverage over seeds | C1, C4 |
| Table 3 | Forms of guarantee: what each asserts, what it gives up, when it suits; contract shared by all | C2 |

## 5. Appendix and supporting information

- **Appendix A.** Order-statistic bound for one certificate; finite-population (hypergeometric) worst case and the check that the binomial k is conservative. Cite Wilks 1941; Bates et al. 2021.
- **Appendix B.** Shared wrong-skip event; union-bound statement; nested path as a one-dimensional fixed sequence in LTT; proof of monotonicity of the shared rate along the path.
- **Appendix C.** Conditional rate by fixed-sequence LTT; the minimum calibration size and the starting quantile.
- **Appendix D.** Map bound (Clopper–Pearson) and its confidence when shared with the decision draw.
- **SI 1.** Natural-neighbour coordinates: exact construction by half-plane clipping, hull-edge limit, check against brute-force stolen areas, continuity under perturbation; the defect in the earlier implementation and its effect.
- **SI 2.** Dataset processing: IR correction and design drafted; NaCl and synthetic parts to draft.
- **SI 3.** Full tables per dataset, level and protocol.
- **SI 4.** Software: functionality, tests, reproduction procedure. The contract a new form of guarantee keeps (inputs it may use, family fixed before labels, guarantee stated or declared absent) and the Monte Carlo acceptance check, with the priority path as a worked example and a plug-in rule as a counterexample that the check flags.
- **Data availability.** NaCl scan (Dryad, doi:10.5061/dryad.p2ngf1w4t); IR map, campaign records (250-campaign record and audits), synthetic forward model and a software snapshot deposited on Zenodo, with the DOI reserved before submission. Listed by function.

## 6. Work needed before drafting

1. Make exact natural-neighbour weights the default; re-run every row.
2. ~~Add a Gaussian-process predictor and a GP-standard-deviation score.~~ Done: isotropic kernel on the design (BoTorch), three length-scale rules (maximum likelihood, design spacing, local spacing by Gibbs kernel), quantile path, 20 seeds on all three datasets; every guarantee held.
3. Add the scalar route to the protocol matrix (NaCl width, IR window maximum).
4. ~~Fix the protocol matrix and settings in advance; replicate each row.~~ Done: 36 configurations × 250 campaigns, logged in results/record; exact finite-population tail and boundary placement are the defaults.
5. ~~Matched-budget study.~~ Dropped (framing: safety margins, no speed or accuracy claims).
6. Off-design audit for NaCl (raster) and IR (non-design pixels): optional, computational only. No new instrument experiments for this paper.
7. ~~Settle the IR data release~~ Decided: Zenodo (reserve the DOI before submission). Mie correction decided: the per-pixel stage-1 ME-EMSC engine, seeded with each pixel's own spectrum, described in SI 2 and deposited with the code; IR design redrawn in micrometres; all IR rows rerun (19 Nov 2026).
8. ~~Decide the headline budget scheme.~~ Decided: no headline scheme. All forms are reported on all datasets; the abstract states that guarantees come in several precise forms and names the shared-event statement as the one common to all.
9. ~~Replicate the three forms on all three datasets over 20 seeds.~~ Done; every stated rate holds (results/study_summary.md).

## 7. Draft status

| Part | File | State |
| --- | --- | --- |
| 1 Introduction | introduction.md | Draft 1, complete |
| 2 Related work | related_work.md | Draft 1, complete (about 650 words) |
| 3 Framework | framework.md | 3.1 (exchangeability by design, non-anticipation), 3.3 and 3.4 with Table 3 drafted; 3.2, 3.5 to draft |
| 4 Experiments | experiments.md | 4.3 Gaussian-process protocols drafted |
| 5 Results | results.md | 5.1 (coverage, attainment, random scores) with Fig. 2, 5.2 with Fig. 3 and 5.3 with Fig. 4 drafted from the 250-campaign record; others wait for section 6 items 3–6 |
| 6 Discussion | discussion.md | "Building other guarantees" drafted |
| Appendix A | appendix_A.md | Draft 1: conditions (A1)–(A6), bound, what breaks it |
| Appendix B | appendix_B.md | Draft 1, complete |
| SI 1 | supplement_SI1.md | GP part with Table S1.1 and Fig. S1 drafted; natural-neighbour part to come |
| SI 3 | supplement_SI3.md | Tables S3.1 (cost per form) and S3.2 (cost per protocol) drafted; full per-level tables to come |
| SI 5 | supplement_SI5.md | Run record: description, Table S5.1 (exceedances of every configuration), Table S5.2 (attainment audit) |
| SI 4 | supplement_SI4.md | Contract, acceptance check (Table S4.1), worked example drafted |
| Fig. 3 | figures/fig3_forms.png, figures/fig_forms.py | Draft |

## 8. Reviewer questions to answer in the text

- *Is this new statistics?* Partly not, and the paper says so: the bounds are cited. The contribution is posing skips as claims, the shared event, exchangeable calibration from the design, and the evidence across protocols.
- *Why the joint rate?* It is the quantity a calibration draw of 40 sites can bound. The conditional rate is reported, and its control at this size is shown to be powerless (appendix C).
- *Does the final map carry the guarantee?* No. It is audited, and the text says which quantity carries which statement.
- *Which form should a user pick?* The one whose statement answers the user's question; Table 3 maps questions to forms. The paper declines to rank them.
- *Are these the only valid forms?* No. They are three instances of one recipe, and SI 4 shows how to build and check another.
- *Is the GP worse?* The comparison reports the cost of a statement under each protocol. No ranking is drawn.
- *Retrospective only?* Yes; truth is needed to check coverage. The protocol itself needs no truth at the remainder.

## 9. Reference map

Verified while planning:

- Angelopoulos, Bates, Candès, Jordan, Lei (2025). Learn then Test: calibrating predictive algorithms to achieve risk control. *Ann. Appl. Stat.* doi:10.1214/24-AOAS1998.
- Jin, Candès (2023). Selection by prediction with conformal p-values. *JMLR* 24(244), 1–41.
- Noack, Yager, Fukuto, Doerk, Li, Sethian (2019). A kriging-based approach to autonomous experimentation with applications to X-ray scattering. *Sci. Rep.* 9. doi:10.1038/s41598-019-48114-3.
- Noack, Doerk, Li, Fukuto, Yager (2020). Advances in kriging-based autonomous X-ray scattering experiments. *Sci. Rep.* 10, 1325. doi:10.1038/s41598-020-57887-x.
- Ye, Han, Liu, Angelopoulos, Griffith, Monakhova, You (2025). Learned, uncertainty-driven adaptive acquisition for photon-efficient scanning microscopy. *Opt. Express* 33(6). doi:10.1364/OE.542640.
- Yang, Zhang (2026). Conformalized rate-adaptive sensing. arXiv:2607.26887.
- Laufer-Goldshtein et al. (2023). Efficiently controlling multiple risks with Pareto Testing. arXiv:2210.07913 (ICLR 2023).
- Angelopoulos, Bates (2021/2023). A gentle introduction to conformal prediction and distribution-free uncertainty quantification. arXiv:2107.07511.

To verify before citing (bibliographic details from memory):

- Wilks (1941), *Ann. Math. Stat.* 12, 91–96.
- Clopper, Pearson (1934), *Biometrika* 26, 404–413.
- Bates, Angelopoulos, Lei, Malik, Jordan (2021), Distribution-free, risk-controlling prediction sets, *J. ACM* 68(6).
- Angelopoulos, Bates, Fisch, Lei, Schuster (2024), Conformal risk control, ICLR.
- Vovk, Gammerman, Shafer (2005), *Algorithmic Learning in a Random World*.
- Lei, G'Sell, Rinaldo, Tibshirani, Wasserman (2018), *JASA* 113, 1094–1111.
- Barber, Candès, Ramdas, Tibshirani (2023), Conformal prediction beyond exchangeability, *Ann. Stat.*
- Kusne et al. (2020), On-the-fly closed-loop materials discovery via Bayesian active learning, *Nat. Commun.* 11.
- Godaly et al. (2018), SLADS for protein crystal positioning, *J. Synchrotron Rad.* (check authors and year).
- Sibson (1981), A brief description of natural neighbour interpolation.
- Bridson (2007), Fast Poisson disk sampling in arbitrary dimensions; plus the HiPoSa software reference.
- Rasmussen, Williams (2006), *Gaussian Processes for Machine Learning*.
- Solheim et al. (2019), open-source ME-EMSC, *J. Biophotonics* (or the reference the IR processing actually used).
- Hoeffding (1963), *JASA* 58 (hypergeometric against binomial).
