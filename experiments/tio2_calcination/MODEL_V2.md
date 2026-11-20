# Forward model v2: calcination of nano-anatase with alumina and P25, measured by lab XRD

v1 used one Avrami law with hand-set anchors. v2 replaces it with the nucleation kinetics of nanocrystalline anatase from the literature, a size distribution, an additive mechanism with a published magnitude, an intimately mixed rutile source with a published anchor, the actual furnace programme, and a laboratory diffractometer. Everything that is not taken from a source is marked as an assumption. Calibration and checks: `results/tio2/model_v2_calibration.json`, figure `results/tio2/model_v2.png`.

## Recipe space

| Axis | Range | Physical meaning |
| --- | --- | --- |
| Temperature | 500–1000 °C | hold temperature of the furnace run |
| Dwell | 1–16 h (pilot: 1–4 h) | hold time |
| Alumina | 0–10 wt% of the sample | γ-Al₂O₃ nanopowder dispersed among the anatase |
| P25 blend | 0–50 % of the TiO₂ | P25 (about 25 nm anatase with 17 % rutile in intimate contact) mixed with the nano-anatase precursor |

A rutile-seed axis (mechanically mixed rutile) is still available (`FOURTH = "seed"`), but with the contact efficiency assumed for mechanical mixing it has almost no effect; the P25 blend carries an anchored, strong effect instead.

## Kinetics

State per crucible: anatase mass in seven equal-mass size classes (lognormal precursor, median 20 nm, σ_ln = 0.35, assumption), their crystallite sizes, rutile fraction and rutile crystallite size. Integrated in 1-min steps over the whole furnace programme (A-Lab methods: 2 °C/min to 300 °C, 15 °C/min to the hold, hold, natural cooling with a 1.8 h time constant, assumption).

$$
\frac{da_k}{dt} = -k_{SN}(T, D_k)\, a_k - k_{IN}(T, D_k) \left(\frac{8\,\mathrm{nm}}{D_k}\right)^3 a_k\, a - \phi\, k_{AR}(T)\, a_k\, r \left(\frac{30\,\mathrm{nm}}{D_R}\right)\left(\frac{25\,\mathrm{nm}}{D_k}\right)
$$

$$
k_X(T, D) = A_X \exp\!\left(-\frac{E_X + \beta \ln(D / 8\,\mathrm{nm})}{RT}\right)
$$

| Term | Source | Values |
| --- | --- | --- |
| Interface nucleation (second order in anatase particle number) and surface nucleation | Zhang & Banfield, Am. Mineral. 84, 528 (1999); J. Mater. Res. 15, 437 (2000); combined model and tabulated constants for 8-nm anatase at 620–690 °C as given by Shakibania, Chem. Biochem. Eng. Q. 31, 353 (2017) | E_IN = 211.4, E_SN = 478.2 kJ/mol (Arrhenius fits to the table); ln A fitted (below) |
| Size-dependent activation energy | Zhang & Banfield 2000 ("the activation energy of nucleation is size dependent"); thermodynamic crossover near 14 nm (Zhang & Banfield, J. Mater. Chem. 8, 2073, 1998) | β fitted |
| Growth of rutile into anatase at anatase–rutile contacts | rutile nanocrystals act as seeds and bypass nucleation (Patras study of commercial anatase vs anatase–rutile mixtures, OSTI 22573958) | A_AR, E_AR fitted to P25; contact efficiency φ = 1 for P25, 0.1 for mechanically mixed rutile (assumption) |
| Anatase coarsening | coarsening constant of the same 8-nm data at 690 °C, D/D₀ − 1 = 0.51 h^-1/3 t^1/3 | d(D³)/dt = 67.9 nm³/h at 690 °C, E = 250 kJ/mol (assumption) |
| Rutile coarsening | 114 nm after 2 h at 900 °C (Int. J. Nanomed. 10 (Suppl 1), 31, 2015, Table 1) | d(D³)/dt = 7.3 × 10⁵ nm³/h at 900 °C, E = 300 kJ/mol (assumption) |
| Alumina additive | dispersed alumina reduces interface nucleation at all temperatures; rate constants of alumina-containing anatase are 7–24× lower at 640–680 °C (Zhang & Banfield 2000 via Shakibania 2017) | factor exp(−c/0.022) on nucleation and contact growth (5 wt% assumed for the published samples), exp(−c/0.05) on coarsening (assumption) |

### Calibration (least squares on the logit of the rutile fraction)

| Anchor | Conditions | Rutile fraction, literature | Model |
| --- | --- | --- | --- |
| A1 coarse commercial anatase (9.7 m²/g, about 160 nm; 4 % rutile) | 3 °C/min, 6 h at 900 / 925 / 950 / 975 / 1000 °C | 0.085 / 0.23 / 0.51 / 0.80 / 0.98 | 0.14 / 0.28 / 0.56 / 0.84 / 0.96 |
| A2 P25 | 5 °C/min, 3 h at 700 / 750 °C (Ishigaki et al.) | 0.68 / 0.98 | 0.50 / 0.98 |
| A3 pure commercial nano-anatase (20 nm assumed) | 8 h at 700 °C: only textural changes (Patras study) | ≤ 0.05 | 0.04 |
| A4 8-nm anatase | 2 h at 620–690 °C, combined nucleation model with the tabulated constants | 0.04 / 0.07 / 0.20 / 0.56 / 0.68 | 0.04 / 0.12 / 0.24 / 0.40 / 0.49 |

Fitted: β = 57.4 kJ/mol per e-fold of size; ln A_IN = 18.85 and ln A_SN = 58.39 (h⁻¹; the table fits give 26.85 and 59.8); ln A_AR = 28.05, E_AR = 231.4 kJ/mol. The largest misfits are the steep high-temperature end of the 8-nm data (A4) and the P25 point at 700 °C.

### Checks

- Rutile crystallite size after 2 h at 900 °C: 115 nm (anchor 114 nm).
- Alumina, 8-nm anatase, 4 h at 660 °C: rutile 0.31 without, 0.08 with 5 wt%.
- On the pilot programme (4 h), nano-anatase is half transformed near 760 °C; 10 wt% alumina moves this to about 900 °C; 30 % P25 broadens the mixed-phase window towards lower temperature.
- Not reproduced: faster heating at fixed soak giving more rutile at 620–700 °C (Processing and Application of Ceramics 10, 235, 2016). The model has no mechanism for it at these temperatures.

## Diffraction

| Element | Model | Source or assumption |
| --- | --- | --- |
| Reflections, intensities per unit mass | pymatgen from anatase (I4₁/amd), rutile (P4₂/mnm), γ-Al₂O₃ as a defect spinel (Fd-3m, a = 7.911 Å, Al₂.₆₇O₄) | strongest anatase/rutile ratio per mass 1.375 (Spurr–Myers factor 1.265) |
| Wavelengths | Cu Kα₁ 1.540562 Å, Kα₂ 1.544390 Å, ratio 2:1 | standard |
| Instrument width | Caglioti U = 0.004, V = −0.002, W = 0.002 deg² (about 0.045° at 25°) | typical Bragg–Brentano (assumption) |
| Sample broadening | Scherrer (K = 0.94) Lorentzian, microstrain Gaussian (anatase 2 × 10⁻³ annealing out with temperature, rutile 5 × 10⁻⁴), Thompson–Cox–Hastings pseudo-Voigt | strain values assumed |
| γ-Al₂O₃ | 5 nm crystallites: broad (311), (400), (440) | assumption |
| Sample displacement | s ~ N(0, 50 µm), shift −2s cos θ / R, R = 200 mm | powders flattened by an acrylic disc (A-Lab); magnitude assumed |
| Intensity scale | lognormal, s.d. 8 % (packing, amount) | assumption |
| Background | air and holder, low-angle rise, Ti fluorescence under Cu radiation (partly suppressed by detector discrimination) | magnitudes assumed |
| Counting | Poisson; strongest anatase reflection of a pure sample about 3000 counts·deg | scan 20–60° in 0.02° steps, about 4 min at the A-Lab scan rate (8 min for 10–100°) |

## Synthesis scatter

Dosing error 3 % relative on alumina and P25; furnace offset s.d. 5 °C per run; tray gradient 0.8 °C per slot from the centre; crucible-to-crucible jitter s.d. 10 % on rate constants; failed crucible (low, weak pattern) with probability 0.5 %. All assumed.

## Not modelled

Brookite; cross-contacts between the nano-anatase and the P25 powders; alumina incorporation into TiO₂ and Al₂TiO₅ (forms above about 1280 °C, outside the range); δ/θ-alumina transitions near 1000 °C; preferred orientation; axial-divergence asymmetry; amorphous content; agglomeration and its effect on contacts (the likely origin of the heating-rate effect).
