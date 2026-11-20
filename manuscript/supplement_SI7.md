# SI 7. Simulated calcination campaign and kinetic recovery (draft 1)

An autonomous synthesis laboratory fires powders in box furnaces and reads each crucible by powder diffraction [Szymanski2023]. The anatase-to-rutile transformation of nanocrystalline titania offers a test in which both the map and the physics behind it are known: its kinetics have been measured and modelled in detail [ZhangBanfield1999; ZhangBanfield2000; HanaorSorrell2011]. This section describes the forward model, the campaign, the observations taken from the patterns, the kinetic fit and the comparison of the four arms of Section 5.6.

## SI 7.1 Forward model

**Kinetics.** Each crucible holds nanocrystalline anatase as seven lognormal size classes (median 20 nm, logarithmic standard deviation 0.35), optionally blended with a commercial anatase–rutile powder (P25) and with dispersed alumina. Rutile forms by three routes: nucleation at contacts between anatase particles (interface nucleation), nucleation at free surfaces (surface nucleation) and growth of existing rutile into anatase at anatase–rutile contacts (contact growth). The first two follow the combined interface and surface nucleation model [ZhangBanfield2000]. For a size class $k$ with anatase fraction $a_k$, size $D_k$ and total anatase fraction $a$, rutile fraction $r$ and rutile size $D_R$:

$$
\frac{da_k}{dt} = - k_{SN}(T, D_k)\, a_k - k_{IN}(T, D_k) \left(\frac{8\,\mathrm{nm}}{D_k}\right)^3 a_k\, a - \phi\, k_{AR}(T)\, a_k\, r \left(\frac{30\,\mathrm{nm}}{D_R}\right) \left(\frac{25\,\mathrm{nm}}{D_k}\right)
$$

The activation energies of nucleation depend on size [ZhangBanfield2000]:

$$
k_X(T, D) = A_X \exp\left(-\frac{E_X + \beta \ln(D / 8\,\mathrm{nm})}{R T}\right)
$$

Anatase and rutile coarsen by cubic laws, $d(D^3)/dt = K \exp(-E/RT)$, anchored at 690 °C for anatase and 900 °C for rutile. Alumina lowers the rates of nucleation and contact growth by the factor $\exp(-c/0.022)$ at mass fraction $c$, and those of coarsening by $\exp(-c/0.05)$. The furnace programme follows the A-Lab methods: 2 °C/min to 300 °C, 15 °C/min to the set temperature, hold, and Newtonian cooling [Szymanski2023].

**Calibration to the literature.** The activation energies of nucleation for 8-nm anatase come from Arrhenius fits to tabulated rate constants at 620–690 °C [ZhangBanfield2000]. The prefactors, the size coefficient $\beta$ and the constants of contact growth were fitted to four sets of published transformation data: coarse commercial anatase at 900–1000 °C, P25 at 700 and 750 °C, 20-nm anatase at 700 °C and 8-nm anatase at 620–690 °C. Table S7.1 lists the values used as truth.

**Table S7.1.** Kinetic parameters of the forward model (truth for Section 5.6).

| Process | Rate at reference temperature | Activation energy (kJ/mol) | Origin |
| --- | --- | --- | --- |
| Interface nucleation | ln A = 18.85 (h⁻¹) | 211.4 | literature table; held fixed in the fit |
| Surface nucleation | ln k = 2.17 h⁻¹ at 750 °C | 478.2 | literature table, prefactor fitted |
| Size coefficient β | – | 57.4 per e-fold of size | fitted; held fixed in the fit |
| Contact growth | ln k = −0.55 h⁻¹ at 700 °C | 231.4 | fitted to P25 data |
| Alumina inhibition | c₀ = 0.022 | – | literature magnitude |
| Anatase coarsening | 67.9 nm³ h⁻¹ at 690 °C | 250 | literature at 690 °C; energy assumed |
| Rutile coarsening | 7.3 × 10⁵ nm³ h⁻¹ at 900 °C | 300 | literature anchor; energy assumed |

**Diffraction.** Patterns cover 20–60° 2θ in steps of 0.02° with Cu Kα₁ and Kα₂ in the ratio 2:1. Reflection positions and intensities per unit mass come from the crystal structures of anatase, rutile and γ-alumina. Peak profiles are Thompson–Cox–Hastings pseudo-Voigt functions [Thompson1987] that combine the instrument function, Scherrer broadening and microstrain (anatase 2 × 10⁻³ annealing out with temperature, rutile 5 × 10⁻⁴). Sample displacement, intensity scale, a background with titanium fluorescence and Poisson counting complete the pattern.

**Synthesis scatter.** Every furnace run carries a temperature offset (standard deviation 5 °C) shared by its eight crucibles and a gradient of 0.8 °C per tray slot. Every crucible carries dosing errors of 3 % on alumina and P25, scatter of 10 % on its rate constants, and a failure probability of 0.5 %. A world is one draw of all scatter and noise; the truth seed selects it.

## SI 7.2 Campaign

The unit of decision is a furnace run. Each run fires a tray of eight crucibles at one temperature and dwell: alumina at 0, 2, 5 and 10 wt%, each without and with 30 % P25. The design places 64 runs in (temperature, log dwell) over 500–1000 °C and 1–4 h as a scrambled Sobol sequence [Owen1995] cut into nested blocks of 8, 8, 16 and 32 runs. Each block of $2^m$ points of a scrambled Sobol sequence is a randomised net with the uniform distribution on the square, so every level of the design is a fixed population known before the campaign starts, as with the hierarchical Poisson-disk designs of the other datasets. The two blocks of 8 form the seed.

The measurement of a run is its eight patterns. A claim on a run holds when it holds for each crucible. The interest claim asks whether some crucible holds both phases, with a rutile fraction between 0.1 and 0.9 estimated from the areas of anatase (101) and rutile (110). The size claim asks the width of anatase (101), wherever the reflection is present, to lie within 0.12° of the width predicted by natural-neighbour interpolation from coarser levels. The pattern claim asks every channel within 25 % + 4σ, on average over channels with predicted signal above 600 counts. Scores and interpolator follow the natural-neighbour protocol of Section 4.3, applied to the run coordinates. Each certified level is calibrated on 12 runs, and the guarantee is $R_E \le 0.20$ at confidence 0.80 along the quantile path. The calibration seed of each campaign equals the truth seed of its world.

## SI 7.3 Observations from the patterns

The kinetic fit uses three observations per crucible, taken as an analyst would take them from a pattern.

1. **Rutile mass fraction.** A two-phase fit of anatase (101) and rutile (110) over 23.5–29.5°, each a pseudo-Voigt Kα₁/Kα₂ doublet on a quadratic background, gives integrated areas. Their ratio, with the intensity ratio per unit mass from the crystal structures, gives the rutile fraction [SpurrMyers1957]. On noiseless mixtures the error is below 0.002 at every combination of sizes; on the simulated campaign the root-mean-square error is 0.003–0.007.
2. **Anatase size.** The width of anatase (101) is converted to a size through a lookup calibrated on simulated strain-free single-phase patterns with the instrument function, the analogue of a measured instrument standard. Sizes above 70 nm, where the width approaches the instrument limit, are not used.
3. **Rutile widths.** The widths of rutile (110) and (101) are kept as widths. They are predicted from the rutile size and a global microstrain, which is fitted with the kinetic parameters; two reflections at different angles separate size from strain [WilliamsonHall1953].

A fraction below 0.03 is below the detection limit and enters the fit as "less than 0.03" (one-sided residual), and likewise above 0.97.

Each of these choices removed a bias larger than the statistical error (Table S7.2). The bias was traced by fitting idealised data and removing one cause at a time: observations computed from the model itself return the truth exactly, so the remaining error lies in the observations or in the synthesis scatter.

**Table S7.2.** Effect of the choices in the observation model on the full 64-run design of one world.

| Choice | Effect when omitted |
| --- | --- |
| Censoring below the detection limit | rutile at 0.5–3 % reads as zero; surface-nucleation energy biased by about +70 kJ/mol |
| Integrated areas from a profile fit | areas as height × width bias the rutile fraction by up to +0.07 at mid conversion, since small anatase and large rutile differ in profile shape |
| Two rutile reflections with fitted microstrain | one reflection reads strain as size, 3–16 % low above 70 nm; rutile-coarsening energy biased by about −50 kJ/mol; with one reflection the fitted strain goes to zero |
| Errors clustered by furnace run | crucibles of one run share its temperature offset; per-crucible errors are too small by 1.0–1.9× on the transformation energies and 2.5–4.6× on rutile coarsening |

## SI 7.4 Kinetic fit

The model is the forward model of SI 7.1 integrated at the nominal recipe of each crucible: furnace offsets, tray gradient, dosing errors and rate scatter are unknown to the fit. Ten parameters are fitted: rate and activation energy of surface nucleation, of contact growth and of the coarsening of each phase, the alumina inhibition constant and the rutile microstrain. Rates are stated at reference temperatures inside the data (750 °C for nucleation, 700 °C for contact growth, 690 °C and 900 °C for coarsening), which removes most of the correlation between rate and activation energy. Interface nucleation, the size coefficient β, the precursor size distribution and the contact efficiency of P25 are held at their values in Table S7.1.

Residuals are the logit of the rutile fraction (scale 0.35), the logarithm of the anatase size (scale 0.12) and the logarithms of the two rutile widths (scale 0.015, the width noise found on the data). The parameters minimise the sum of squared scaled residuals, from a starting point displaced from the truth by 50–60 kJ/mol in every activation energy. Crucibles of one furnace run share its temperature offset, so the covariance of the estimate is the cluster-robust sandwich over runs [LiangZeger1986]. With $J$ the Jacobian of the residuals at the estimate, $J_g$ and $r_g$ its rows and the residuals of run $g$, and $G$ the number of runs:

$$
H = J^{\top} J
$$

$$
\widehat{V} = \frac{G}{G-1}\, H^{-1} \left( \sum_{g} J_g^{\top} r_g\, r_g^{\top} J_g \right) H^{-1}
$$

## SI 7.5 Arms and statistics

In each of 30 worlds, the same fit is applied to the runs of five arms: the full design, the runs measured by the size-claim campaign, those measured by the pattern-claim campaign, a uniformly random subset of the design of the size campaign's size, and a subset of the same size chosen for the kinetics. The last arm starts from the seed levels and adds, one at a time, the run that most increases the determinant of the Fisher information at the true parameters, the D-optimality criterion [Atkinson2007]. Knowing the truth, it bounds the precision any choice of runs could reach.

The information a subset $S$ carries is summarised by its D-efficiency relative to the full design, with $\mathcal{I}_S$ the Fisher information of the runs in $S$ at the true parameters and $p = 10$:

$$
D_{\mathrm{eff}}(S) = \left( \det \mathcal{I}_S \,/\, \det \mathcal{I}_{\mathrm{full}} \right)^{1/p}
$$

A D-efficiency of 0.84 means that the full design would reach the same determinant with 84 % of its runs if information were spread evenly. Each arm is also scored by the standard errors and errors of the four activation energies, by the share of all ten parameters lying within two standard errors of the truth, and by the largest error, over dwells of 1–4 h, of the temperature at which half the anatase of the native powder has transformed. The same forward model generates the data and serves in the fit, so absolute accuracy is favourable to every arm alike; the comparison between arms is the result.

## SI 7.6 Further results

**Table S7.3.** Kinetic recovery over 30 worlds (median runs; activation energies in kJ/mol, ordered surface nucleation / contact growth / anatase coarsening / rutile coarsening).

| Set of runs | Runs | D-efficiency, median | Median standard error | RMS error over worlds | Parameters within 2 s.e. | Half-conversion temperature error, median (°C) |
| --- | --- | --- | --- | --- | --- | --- |
| Full design | 64 | 1.00 | 13 / 11 / 22 / 6 | 15 / 28 / 28 / 14 | 67 % | 6.5 |
| Size-claim campaign | 47.9 | 0.85 | 15 / 12 / 23 / 7 | 14 / 26 / 29 / 14 | 74 % | 6.1 |
| Pattern-claim campaign | 49.6 | 0.88 | 15 / 12 / 22 / 7 | 16 / 27 / 29 / 14 | 74 % | 5.9 |
| Random subset | 47.9 | 0.74 | 15 / 12 / 24 / 7 | 18 / 29 / 34 / 15 | 70 % | 6.3 |
| Kinetics-optimal subset | 47.9 | 1.00 | 14 / 11 / 22 / 6 | 15 / 28 / 27 / 14 | 67 % | 6.4 |
| Seed levels | 16 | 0.23 | 22 / 14 / 29 / 10 | 27 / 25 / 44 / 17 | 79 % | 4.2 |

In 27 of the 30 worlds the size campaign's runs had a higher D-efficiency than the paired random subset, by a median of 0.11. Removing the 16 runs a campaign skipped lost less information than removing a random set of the same size in a median 98 % of 200 draws per world. Every set of runs places fewer parameters within two standard errors of the truth than the nominal 95 %: the fit integrates the nominal recipe, and the furnace offsets, tray gradient and rate scatter it leaves out bias the estimate, most for contact growth. The standard errors of a single fit are themselves uncertain with about 48 clusters, and a random subset can show a smaller standard error than the full design; the errors over worlds and the D-efficiency are the measures relied on in Section 5.6. The guarantee was checked on 60 certified levels per claim: 6 exceedances against 5.6 allowed by the picked levels under the size claim (one-sided probability 0.50) and 8 under the pattern claim (0.20).

**Uniform designs.** Designs of independent uniform runs were compared at matched budgets in one world (Table S7.4). At 47 runs, a random subset of the Sobol design matched the campaign, and independent uniform runs lost 30–40 % in precision on the surface-nucleation and anatase-coarsening energies. At 16 runs, the seed levels kept standard errors of 14, 21, 23 and 9 kJ/mol on the four energies, while random or independent uniform runs roughly doubled the errors on surface nucleation and anatase coarsening, with single draws off by up to 100 kJ/mol. The nested Sobol design keeps its small levels evenly spread, which the kinetics need when runs are few.

**Table S7.4.** Median standard errors of the activation energies (kJ/mol; surface nucleation / contact growth / anatase coarsening / rutile coarsening), one world, matched budgets.

| Runs | Sobol levels or campaign | Random subset of the Sobol design | Independent uniform runs |
| --- | --- | --- | --- |
| about 47 | campaign: 12 / 11 / 22 / 8 | 14 / 11 / 20 / 9 | 17 / 10 / 28 / 7 |
| 16 | seed levels: 14 / 21 / 23 / 9 | 25 / 19 / 42 / 14 | 32 / 14 / 48 / 12 |

## Notes for revision (not part of the text)

- Code: experiments/tio2_calcination (forward_v2.py, furnace.py, inverse.py, kinetics_worlds.py, inverse_uniform.py); model documentation in MODEL_V2.md; records in results/tio2/.
- The literature table of rate constants for 8-nm anatase was read from Shakibania (2017), Chem. Biochem. Eng. Q. 31, 353, which reproduces the Zhang–Banfield constants; confirm against the original before citing only Zhang & Banfield.
- Anchor sources (P25 at 700/750 °C, coarse anatase at 900–1000 °C, rutile size after 2 h at 900 °C) to be added as references; see MODEL_V2.md.
- Heating-rate effect at 620–700 °C is not reproduced by the model (MODEL_V2.md); it does not enter the 1–4 h hold design.
