# Mock referee reports, round 3 (2026-11-21)

All three: minor revision. Full reports were returned to the session; key points condensed here.

## Referee 1 (statistics)
- Label-conditional bound and audit verified valid against the code; coverages (83 %, 85 % at 0.80; 100 % on IR) consistent with a conservative discrete limit.
- "keeps every bound it carried" too broad: holds for rates counted over the level, not ratio rates (Appendix C); freed budget must not be re-spent on the same draw (B.3); joint statement per level only at 1 − δ_L − 0.20.
- Audit scope: covers skipped sites only, measured sites assumed correct (drift escapes it); needs A6 until the audit is measured; map, interpolator, strata fixed before the draw; re-auditing after refitting needs a multiplicity correction; mention Bonferroni in main text.
- Contradictions: §3.5 ("nothing is claimed for a display map") and SI 9 scope vs §3.6; SI 9 cites "Section 6" for the label-conditional statement.
- SI 10.3 interest-loss bound uses a separate 100-site draw; say so.
- Cite Tong, Feng & Li (2018) Neyman–Pearson umbrella; a finite-population reference for the audit.
- Minor: say audit numbers are mean bounds; exact coverage for deterministic GP run; drift result depends on drift direction; Dawid stated precisely (asymptotic, prior probability one of own calibration); CV sentence partly rhetorical, "at no further cost" → beyond calibration; §5.4 random-score sentence ambiguous; abstract 9 % vs 8.5 %.
- Cuts proposed ≈ 780 words.

## Referee 2 (beamline)
- Drift study favours the bound by construction (truth at t=0, monotone drift, calibration measured after predictors); state conditions in §5.6 (no noise, re-measurement not charged, 16 % flagged at s = 0.05, flags late at s = 0.10, 79 % of measurements off at s = 0.20).
- Wants damage models: dose-driven decay with spatial kernel (makes interest labels optimistic), flux steps, stage translation — with Poisson noise. With NaCl repeat-failure 1.1 %, 5 sentinels × 6 levels false-flag ≈ 28 % of drift-free campaigns; fresh sentinels; contract should state what a flag triggers.
- Audit: sizing rule (zero failures: 1 − (1 − c)^{1/n_a} ≈ 1.6 % at 100, 0.80); A6 must hold until audit; skipped sites only; run audit under drift. R-free analogy: exact finite-population bound immune to neighbour correlation; re-audit needs fresh sample and split confidence; may audit sites enter the delivered map?
- GP acquisition result understated: halving at equal cost; qualify (different predictors, one deterministic run, missing like-for-like: certified plan with GP predictor final map). Discussion: what per-level certification buys over acquire-then-audit (bound before irreversible decisions, reason per skip); for static mounted samples acquire+audit may be the better default.
- Label-conditional: share not location; per level at 0.80; shown only on synthetic; show NaCl and cost for a rare feature.
- Minor: beam-time model deferred three times (one SI table would do); Conclusion "audit certified the finished map" overstates; 330 vs 334 in SI 10.2.
- Cuts proposed ≈ 690 words.

## Referee 3 (ML/GP)
- GP acquisition changes the message; outdated statements: abstract "three to ten times too low", §1 "Nothing in either run could show which statement held", §5.2 "nothing in a run shows which", SI 7 "acquisition-driven campaigns not tested". Discussion must state what per-level certification buys (statement at decision time, reason per claim, protection of interest, no terminal sample) and costs (map quality at equal cost; certified 18.0 % vs uniform 22.0 %).
- "Any kernel then enters as a score, and its quality returns as fewer measurements" contradicted by runs (GP protocols cost more; positional SD score). Run certified plan on NaCl with the GP posterior failure probability as frozen score, or withdraw. Latent SD is a misuse for single-measurement claims; presence model is regression on 0/1, not a classifier; use the Gibbs kernel in S7.2.
- Dawid supports "external", not "uniform"; "only on sites the model did not choose" contradicts §2 (known selection probabilities, ZrnicCandes2024); cite jackknife+/CV+ (Barber et al. 2021) and Fannjiang et al. 2022 for the CV objection; "at no further cost" overstated.
- Audit references: Stehman & Czaplewski 1998; Olofsson et al. 2014; Kossen et al. 2021 (active testing); Sawade et al. 2010; Farquhar et al. 2021; Angelopoulos et al. 2023 (PPI). Audit is terminal; "covers the whole run" overstates; Bonferroni wastes confidence.
- Label-conditional: position as PAC / NP umbrella (Tong et al. 2018; Park et al. 2020); report attained δ_Z; joint confidence ≈ 0.6; 58.7 % is not an exceedance of a stated guarantee.
- Minor: repeat GP run with jitter; Table S10.4 label stated (expectation) vs bound; SI 1 leftover draft notes; refs.bib surname-only entries, incomplete references in main.pdf; qualify Szymanski2023 (Leeman et al. 2024).
- Cuts proposed ≈ 736 words (net ≈ 650 after ≈ 80 words of additions).

## Cuts on which all three agree
§1 "Any experiment declares…/The plan turns both…"; §1 "A plan may also be drawn up…/A nested, space-filling…"; §1 "The statistics are standard…"; §3.5 last paragraph to one sentence; §5.1 "Checking a probability bound…"; §5.1 "Breaking the order of operations…" (keep three rates, rest to SI 5.2); §5.2 "The certified campaigns at budgets…" (to Fig. 4 caption); §5.4 "Every guarantee held…/The guarantee comes from…"; §6 Scope repeats ("The bound concerns…", "Section 5.5 and SI 6 show…", "Simulated drift left…"); §7 compress. Two of three: §1 "The third is evidence…"; §3.1 "Each completed level also yields…"; §4.3 GP-protocol sentences to SI 1.
