# 1 Introduction (draft 1)

Autonomous decision engines are becoming routine in experimentation. At synchrotron beamlines, Gaussian-process surrogates choose the next sample position or composition, and measurement, analysis and decision run as one closed loop [Noack2019; Noack2020; Yager2023]. Self-driving laboratories search formulation and composition spaces in the same way [Burger2020; Nazeri2026], and an autonomous laboratory synthesised 41 of 58 target inorganic compounds in 17 days [Szymanski2023]. Probabilistic models recommend which strains to build next [Radivojevic2020], and laboratory automation keeps lowering the cost of handing experimental choices to machines [Tom2024].

Each decision to measure is also a decision to leave something unmeasured. Beam time, dose, reagents and sample lifetime are limited, and the sites left out of a map still enter it, as predictions. A closed-loop scattering study recently mapped the phases of a ternary polymer blend from 65 of 5151 grid compositions, so that 98.7 % of the map is prediction [Upreti2026]. Moving such decisions from people to models makes accountability a requirement. Guidance on AI risk asks for traceable decisions and documented responsibility [NIST2023], regulation of high-risk systems requires automatic records of their operation [EU2024, Art. 12], and audit frameworks ask for evidence that can be checked against stated expectations [Raji2020]. For a measurement campaign the consequential decision is the skip. An accountable experiment certifies every action. A site is skipped because a stated claim covers it, with a bound, checkable by measurement, on how often such skips are wrong; a site is measured because it was needed when the decision was made. Figure 1 shows one on a diffraction scan: every site carries its action, and the share of wrong skips stays within a stated bound that the full scan confirms.

**Figure 1.** A guarantee on what was not measured: one campaign of average cost on a fully measured NaCl microdiffraction scan, certified on the width of the (200) line; 612 of 1071 design sites were measured, against a mean of 614 over 250 campaigns. (a) The true (200) line height, known everywhere because the scan was measured in full, with the sites the campaign measured. (b) The certified action of every design site, filled over the scan: measured for the seed, for the calibration draw or because no claim covered it (greys); skipped as not of interest, as predictable or both (colours). Crosses: wrong skips, found afterwards against the full scan. (c) The share of 250 campaigns in which each site was skipped wrongly. (d) The guarantee on each certified level, at most 20 % of the level skipped wrongly with confidence 0.80: realised rates in 250 campaigns (dots) and in this campaign (diamonds); numbers give the levels over budget against the number the guarantee allows. File: `figures/fig_hook.png`.

Two reasons justify a skip. Either the site holds nothing of interest, or its signal, or a quantity derived from it, can be predicted within tolerance from the sites already measured. Each reason is a claim about the site that a measurement would settle, and a wrong skip is a site covered by a false claim. Posed this way, skips come within reach of distribution-free risk control, which bounds the population rate of a chosen loss from a held-out sample for any predictor, with exchangeability of the calibration data as the only assumption [Vovk2005; Bates2021; Angelopoulos2023; Angelopoulos2025]. Related constructions already steer re-scanning in microscopy [Ye2025], set the acquisition rate in imaging [YangZhang2026] and certify the contingency checks skipped in power grids [Manoharan2026].

This paper builds an accountable experiment for mapping campaigns. The design sites are divided into levels fixed before the campaign. The coarsest levels are measured in full. At each finer level, a model fitted to the measured sites proposes which sites to skip, a uniform random sample of the level is measured for calibration, and its labels set how far the skips may go. The guarantee reads: at most a fraction ε of the level is skipped under a false claim, with probability at least c over the calibration draw. It holds for any predictor and any score that respect the order fit, freeze, draw, calibrate, decide; the model decides only how many measurements the guarantee costs, and protocols are compared by that cost. A nested, space-filling design [Bridson2007] serves image formation at every resolution, while the guarantee needs only that the levels are fixed in advance. Every site leaves the campaign with a certified action: measured for the seed, for calibration or because no claim covered it, or skipped under a named claim and its bound.

A guarantee delivers the claim it is given, so the choice of claim decides what the guarantee buys. The acceptance metric that defines a predictable site, a peak width or the whole curve, decides where predictions fail, and with them where a campaign measures and where its wrong skips fall.

The contributions are three. Skipping is posed as two claims with a shared wrong-skip event, and guarantees of three forms are built on it from existing risk-control results: separate budgets under a union bound, and one budget along a threshold path fixed before the calibration labels are seen [Angelopoulos2025; LauferGoldshtein2023]; a contract with a Monte Carlo acceptance check admits further forms. Exchangeable calibration inside an adaptive campaign is created by design: levels fixed in advance give each draw its population, and an order of operations that forbids anticipation keeps each level's guarantee valid whatever came before. Every bound is checked against fully measured truth on three datasets, an infrared map of a bioreef sample, a NaCl microdiffraction scan [ALSNaCl] and a synthetic small-angle scattering phase map, together with what each guarantee costs in measurements and where it sends them.

---

## Notes for revision (not part of the text)

- Rewritten 20 Nov 2026 around the accountable experiment: need (skips enter the map) → definition (reason + checkable rate) → two claims → what the paper builds → what a guarantee buys → three contributions. The paragraph map below predates the rewrite.

**Paragraph map.** Each paragraph opens on a need or an opportunity.

| ¶ | Opens on | Job | Feeds claim |
| --- | --- | --- | --- |
| 1 | Opportunity: autonomy is routine and promising | Beamlines, formulation and synthesis labs, synthetic biology; momentum from automation and cloud labs | — |
| 1b | Need: every decision to measure is also a decision to skip | Scarce budget; skipped sites enter the map as predictions | — |
| 2 | Need: accountability | A skip is the consequential decision; accountable = recorded reason + checkable error rate | C1, C5 |
| 3 | Principle | Measure what you must, skip what you can; two claims; wrong skip defined | C2 |
| 4 | Opportunity: risk control | Cited machinery; nothing derived | C1, C2 |
| 5 | What the paper provides | Workflow, the guarantee, design as the audit population, per-site record | C1, C3 |
| 6 | Framing | Guarantees, cost per guarantee, protocols as interchangeable parts; the form of the guarantee as a choice tied to the question asked | C2, C4 |
| 7 | Contributions | Three contributions, datasets, roadmap | C2, C3, C5 |

**Word budget.** About 950 words, about 50 over the 900 in the plan. If space is needed, ¶3 and ¶5 can each lose a sentence.

**Choices to make**

- *A-Lab.* Decided: keep A-Lab. Its headline success rate drew a published critique of its phase identification (Leeman et al. 2024, PRX Energy; check). Cited only for autonomous operation over 17 days, it is safe, but it can be swapped for MacLeod et al. (2020, Sci. Adv.) if you prefer.
- *Kusne2020* was dropped from ¶1 to make room; it can return in Related work.
- *EU AI Act.* Scientific instruments are not high-risk systems under the Act. The citation is used for the principle of automatic records. If a reviewer pushes on this, soften it to "regulation of AI systems asks for".
- *"Guarantee" against "statement".* "Guarantee" is used throughout for the bound, to avoid echoing "statement". Check that it suits your voice.
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
