# 1 Introduction (draft 1)

Autonomous decision engines are becoming routine in large-scale experimentation, and early results show great promise. At synchrotron beamlines, Gaussian-process surrogates decide which sample position or composition to measure next, and the measurement, the analysis and the decision run as one closed loop [Noack2019; Noack2020; Yager2023]. Self-driving laboratories search formulation and composition spaces in the same way: a mobile robot carried out 688 experiments over eight days in a ten-variable photocatalyst formulation space [Burger2020], closed-loop platforms tune surfactant formulations against measured interfacial properties [Nazeri2026], and an autonomous laboratory synthesised 41 of 58 target inorganic compounds in 17 days [Szymanski2023]. In synthetic biology, probabilistic machine learning recommends which strains to build in the next design–build–test–learn cycle [Radivojevic2020]. The momentum is growing: laboratory automation, remotely operated cloud laboratories and maturing decision software lower the cost of handing experimental choices to machines, and adoption is spreading across disciplines [Tom2024].

Every such engine decides what to measure and, with the same decision, what to leave unmeasured. Beam time, dose, reagents and sample lifetime limit how much can be measured, and a decision engine spends that budget where its model is least certain or most promising. In a scanning or mapping experiment the sites left out still enter the final map, as predictions.

Moving these decisions from people to models makes accountability a design requirement. Guidance on AI risk asks for traceable decisions and documented responsibility across the life of a system [NIST2023], regulation of high-risk systems requires automatic records of their operation [EU2024, Art. 12], and audit frameworks for machine learning ask for evidence that can be checked against stated expectations [Raji2020]. For a measurement campaign the consequential decision is whether to measure a site. An accountable instrument records why each site was skipped and states, in a form that can be checked, how often such skips are wrong.

A short principle underlies every adaptive scan: measure what must be measured, skip what can be skipped. Two conditions justify a skip. Either the site holds nothing of interest, or its spectrum, or a quantity derived from it, can be predicted within tolerance from the sites already measured. Each condition is a claim about the site, and a measurement would settle it. A wrong skip is a site covered by a false claim.

Distribution-free risk control supplies the missing statement. Conformal prediction and its extensions attach finite-sample guarantees to the output of an arbitrary predictor, with exchangeability of the calibration data as the only assumption [Vovk2005; Angelopoulos2023]. Risk-controlling prediction sets and Learn-then-Test bound the population rate of a chosen loss from a held-out sample [Bates2021; Angelopoulos2025], and several risks can be controlled at once [Angelopoulos2025; LauferGoldshtein2023]. Related constructions already steer re-scanning in microscopy [Ye2025] and the choice of an acquisition rate in imaging [YangZhang2026]. Posing a skip as a claim brings scanning experiments within reach of these results.

This paper describes a workflow that asserts, for every level of a hierarchical design, a bound on the rate of wrong skips. A coarse, space-filling layer is measured first. At each finer layer, a model fitted to the measured sites proposes which sites to skip, a uniform random sample of the layer is measured as an audit, and the audit sets the thresholds under which a skip is allowed. The assertion reads: the fraction of the layer skipped under a false claim is at most ε, with probability at least c over the audit draw. Hierarchical Poisson-disk designs [Bridson2007] provide the fresh, exchangeable population that each audit requires inside an adaptive campaign. Every site leaves the campaign with a recorded reason: measured, audited, or skipped under a named claim and its bound.

The emphasis lies on what can be asserted, and at what cost in measurements. The bound holds for any interpolator, scoring rule or acquisition order that respects the sequence fit, freeze, audit, decide. Model quality changes the number of measurements needed to make an assertion; the assertion stays fixed. Optimality of the underlying algorithms lies outside the scope of this work, and protocols are compared by the measurements they spend per assertion. The same assertions are therefore made with natural-neighbour interpolation of full spectra and of derived quantities, and with learned and random scoring rules. The form of the guarantee is a choice as well. A bound per claim reports how often each reason for skipping failed; a single bound on the shared event spends the whole budget on how often any skip failed; a priority between the claims can be built into the path along which thresholds advance. Each form is a valid finite-sample bound for its own statement, and the choice among them follows from the question an experimenter needs answered.

The contributions are threefold. Skipping is posed as two claims with one shared wrong-skip event, and guarantees of three forms are built on it from existing risk-control results: separate budgets combined by a union bound, and a single budget along a threshold path fixed before the audit labels are seen, with the path either matching quantiles of the two scores or admitting the claims in a set order [Angelopoulos2025; LauferGoldshtein2023]. All three follow one recipe, and a contract with a Monte Carlo acceptance check lets further forms be added. Exchangeability of the audit samples is created by design: a predetermined hierarchical design fixes the population of every level, and an order of operations that forbids anticipation keeps each level's assertion valid whatever the campaign did before. The workflow is tested on a synthetic small-angle scattering phase map of a three-component surfactant–oil–water formulation, a NaCl microdiffraction scan [ALSNaCl] and an infrared map of a bioreef sample, and every bound is checked against the fully measured truth. Section 2 places the work among autonomous experimentation and risk control, Section 3 describes the workflow, Section 4 the experiments and Section 5 the results.

---

## Notes for revision (not part of the text)

**Paragraph map.** Each paragraph opens on a need or an opportunity.

| ¶ | Opens on | Job | Feeds claim |
| --- | --- | --- | --- |
| 1 | Opportunity: autonomy is routine and promising | Beamlines, formulation and synthesis labs, synthetic biology; momentum from automation and cloud labs | — |
| 1b | Need: every decision to measure is also a decision to skip | Scarce budget; skipped sites enter the map as predictions | — |
| 2 | Need: accountability | A skip is the consequential decision; accountable = recorded reason + checkable error rate | C1, C5 |
| 3 | Principle | Measure what you must, skip what you can; two claims; wrong skip defined | C2 |
| 4 | Opportunity: risk control | Cited machinery; nothing derived | C1, C2 |
| 5 | What the paper provides | Workflow, the assertion, design as the audit population, per-site record | C1, C3 |
| 6 | Framing | Guarantees, cost per assertion, protocols as interchangeable parts; the form of the guarantee as a choice tied to the question asked | C2, C4 |
| 7 | Contributions | Three contributions, datasets, roadmap | C2, C3, C5 |

**Word budget.** About 950 words, about 50 over the 900 in the plan. If space is needed, ¶3 and ¶5 can each lose a sentence.

**Choices to make**

- *A-Lab.* Its headline success rate drew a published critique of its phase identification (Leeman et al. 2024, PRX Energy; check). Cited only for autonomous operation over 17 days, it is safe, but it can be swapped for MacLeod et al. (2020, Sci. Adv.) if you prefer.
- *Kusne2020* was dropped from ¶1 to make room; it can return in Related work.
- *EU AI Act.* Scientific instruments are not high-risk systems under the Act. The citation is used for the principle of automatic records. If a reviewer pushes on this, soften it to "regulation of AI systems asks for".
- *"Assertion" against "statement".* "Assertion" is used throughout for the bound, to avoid echoing "statement". Check that it suits your voice.
- *Forms of guarantee.* ¶6 and ¶7 now name three forms and say more can be built. If space is short, the priority path can move from ¶7 to Section 3.
- *¶6 last sentence.* It previews the protocol matrix. If the GP predictor makes it into the study, add "and Gaussian-process regression".

**References used here.** Those marked ✓ were verified this session; the others need a check before the reference list is built.

- ✓ [Tom2024] Tom, Schmid, Baird et al. (2024). Self-driving laboratories for chemistry and materials science. Chem. Rev. 124(16), 9633–9732. doi:10.1021/acs.chemrev.4c00055.
- ✓ [NIST2023] Tabassi, E. (2023). Artificial Intelligence Risk Management Framework (AI RMF 1.0). NIST AI 100-1. doi:10.6028/NIST.AI.100-1.
- ✓ [EU2024] Regulation (EU) 2024/1689 (Artificial Intelligence Act), OJ L 2024/1689, 12.7.2024, Article 12.
- ✓ [Raji2020] Raji, Smart, White, Mitchell, Gebru, Hutchinson, Smith-Loud, Theron, Barnes (2020). Closing the AI accountability gap: defining an end-to-end framework for internal algorithmic auditing. FAT* '20. doi:10.1145/3351095.3372873.
- ✓ [Yager2023] Yager, Majewski, Noack, Fukuto (2023). Autonomous x-ray scattering. Nanotechnology 34. PMID 37141868 (check volume and article number).
- ✓ [Burger2020] Burger et al. (2020). A mobile robotic chemist. Nature 583, 237–241. doi:10.1038/s41586-020-2442-2.
- ✓ [Nazeri2026] Nazeri, Mei, Watchorn et al. (2026). RAISE: a self-driving laboratory for interfacial property formulation discovery. Digital Discovery. doi:10.1039/D5DD00531K.
- ✓ [Szymanski2023] Szymanski et al. (2023). An autonomous laboratory for the accelerated synthesis of novel materials. Nature 624, 86–91. doi:10.1038/s41586-023-06734-w.
- ✓ [Radivojevic2020] Radivojević, Costello, Workman, Garcia Martin (2020). A machine learning Automated Recommendation Tool for synthetic biology. Nat. Commun. 11, 4879. doi:10.1038/s41467-020-18008-4.
- ✓ [Noack2019] Noack, Yager, Fukuto, Doerk, Li, Sethian (2019). Sci. Rep. 9. doi:10.1038/s41598-019-48114-3.
- ✓ [Noack2020] Noack, Doerk, Li, Fukuto, Yager (2020). Sci. Rep. 10, 1325. doi:10.1038/s41598-020-57887-x.
- ✓ [Angelopoulos2025] Angelopoulos, Bates, Candès, Jordan, Lei (2025). Learn then Test. Ann. Appl. Stat. doi:10.1214/24-AOAS1998.
- ✓ [LauferGoldshtein2023] Efficiently controlling multiple risks with Pareto Testing. arXiv:2210.07913 (ICLR 2023).
- ✓ [Ye2025] Ye et al. (2025). Opt. Express 33(6). doi:10.1364/OE.542640.
- ✓ [YangZhang2026] Yang, Zhang (2026). Conformalized rate-adaptive sensing. arXiv:2607.26887.
- [Kusne2020] Kusne et al. (2020). On-the-fly closed-loop materials discovery via Bayesian active learning. Nat. Commun. 11.
- [Vovk2005] Vovk, Gammerman, Shafer (2005). Algorithmic Learning in a Random World. Springer.
- [Angelopoulos2023] Angelopoulos, Bates. A gentle introduction to conformal prediction and distribution-free uncertainty quantification. arXiv:2107.07511 (check the journal version).
- [Bates2021] Bates, Angelopoulos, Lei, Malik, Jordan (2021). Distribution-free, risk-controlling prediction sets. J. ACM 68(6).
- [Bridson2007] Bridson (2007). Fast Poisson disk sampling in arbitrary dimensions. SIGGRAPH sketches.
- [ALSNaCl] Dryad dataset doi:10.5061/dryad.p2ngf1w4t (check the authors and the citation the depositors request).
