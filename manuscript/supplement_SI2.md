# SI 2. Dataset processing (draft 1)

## SI 2.1 Infrared map

**Data.** The map covers 29 × 42 pixels at a pitch of 1 µm, with 1738 channels between 650 and 4000 cm⁻¹ in apparent absorbance. The claim window is 1500–1850 cm⁻¹. It holds the amide and ester bands, where scattering distortions are strongest next to the absorption bands.

**Scattering correction.** Particles of a few micrometres scatter infrared light resonantly. The result is broad oscillations and dispersive swings at band edges, superimposed on the absorbance. Each spectrum is corrected by extended multiplicative signal correction with a resonant Mie basis [MartensStark1991; Kohler2005; Bassan2010; Solheim2019]. The measured apparent absorbance is modelled as a scaled chemical spectrum plus a scattering background:

$$ A(\nu) = b\,A_{\mathrm{c}}(\nu) + B(\nu) $$

The background is a combination of seven signed principal components of a family of scattering-only extinction curves in the van de Hulst approximation [vandeHulst1957]. The family spans sphere radii of 2–8 µm, real refractive indices of 1.1–1.5 and imaginary indices peaking at 0.02–0.12, shaped by the current chemical estimate, with the dispersion obtained through the Kramers–Kronig relation. Absorption by the particles belongs to the chemical term and is left out of the basis. The fit has the following constraints:

- the background lies between zero and the measured spectrum;
- b is at least 0.05;
- the slope of the chemical spectrum is flat in 2100–2300 and 2390–2800 cm⁻¹;
- its level is pulled towards zero in 2390–2800 and 3850–4000 cm⁻¹;
- the background stays above the chord between these anchor windows across 2800–3850 cm⁻¹.

The chemical estimate is refined self-consistently. Each pixel starts from its own apparent absorbance, and after each of six iterations its estimate is replaced by its own corrected spectrum. No information passes between pixels, so the correction is a fixed transformation of each spectrum and can be applied to a site as soon as it is measured.

The corrected spectrum used throughout is the apparent absorbance minus the fitted background, clipped at zero; the scale b is not divided out. A site is of interest when any channel in the claim window reaches absorbance 0.1. That holds for 37 % of the pixels.

**Sensitivity to the starting estimate.** The iteration converges to the same corrected spectrum for most pixels, whatever the starting estimate. Starting from the median spectrum of the map instead of each pixel's own spectrum changes the corrected window by a median of 0.001. For about 5 % of the pixels it changes it by more than 0.05, and 20 of 1218 pixels change their interest label. The guarantees of the main text concern the target as defined by the per-pixel correction. Any fixed per-spectrum transformation defines a valid target.

**Design.** The hierarchical Poisson-disk design is drawn on the physical rectangle, 41 × 28 µm between the centres of the corner pixels. The radii run from 6.8 µm down to 0.85 µm in seven levels, each a factor $\sqrt{2}$ below the previous one, with the four corners forced into the coarsest level. Sites are snapped to the nearest pixel, and the coarsest level is kept when two sites share a pixel. Of 1064 sites, 959 remain, with 23, 13, 37, 71, 142, 245 and 428 sites on levels 0–6. Distances for the interpolators are taken in micrometres, divided by 41 µm for numerical convenience. This rescaling is isotropic and leaves the geometry unchanged.

## SI 2.2 NaCl microdiffraction scan

The scan was recorded at beamline 7.3.3 of the Advanced Light Source and is used as deposited: azimuthally integrated profiles on a raster of 3249 sites with a stage step of 0.25 mm, each with 1000 bins between 0.589 and 38.94 nm⁻¹ [ALSNaCl]. Stage coordinates are rescaled to the unit square for the design and kept in millimetres for display. A hierarchical Poisson-disk design on the unit square, with radii from 0.2 to 0.025 over seven levels, is snapped to the nearest raster site; a raster site claimed by several design points keeps the coarsest level. The design holds 1071 sites, with 21, 19, 36, 65, 138, 271 and 521 sites on levels 0 to 6.

**The (200) line.** The (200) reflection of rock salt lies at $q = 4\pi / a$ with $a = 5.6402$ Å, or 22.28 nm⁻¹. Its descriptors are taken in the window 22.28 ± 0.40 nm⁻¹: the position of the tallest local maximum, refined by a parabola through the logarithms of intensity and $q$, its height above a local baseline (the higher of the two flanking minima), and its full width at the level midway between baseline and peak.

**Noise and presence.** The noise in the window is estimated once from all design sites. Each profile is reduced to residuals from a straight baseline across the window. The 30 % of profiles with the smallest largest residual are taken as off the ring, and the noise is 1.4826 times the median absolute deviation of their residuals: $\sigma = 0.117$ in the units of the deposit. A line is present when its height above baseline exceeds $5\sigma$; on that criterion 64 % of the design sites hold the line, and these are the sites of interest.

**Width tolerance.** A prediction fails when it disagrees with the truth on the presence of the line, or when both show the line and their widths differ by more than 0.02 nm⁻¹, about half the bin width of 0.038 nm⁻¹ at the (200) position. Sites without the line in truth and prediction pass. The same presence test is applied to the predicted profile, so a predicted line too weak to clear $5\sigma$ counts as absent.

## SI 2.3 Synthetic small-angle scattering map

**Forward model.** A composition $(x, y)$, with $x$ the oil and $y$ the surfactant weight fraction and $x + y \le 1$, maps to a noiseless scattering curve on 240 logarithmically spaced points between 0.005 and 0.32 Å⁻¹. Four phases are separated by straight boundaries in composition: a micellar phase (L1), modelled as polydisperse spheres whose radius swells with solubilised oil, with a Percus–Yevick hard-sphere structure factor; an ordered cubic phase (I1) with face-centred cubic Bragg peaks; a hexagonal phase (H1) with Bragg peaks of a two-dimensional hexagonal lattice and a cylinder form factor; and an oil-rich emulsion, in which excess oil adds Porod scattering. Sigmoids of fixed width smooth every transition, so the curves vary continuously with composition while the peak positions and widths change quickly near the boundaries. The model is carried over from an earlier study and is deposited with the data.

**Parameters.** Table S2.1 lists every parameter of the forward model; the curves carry no noise.

**Table S2.1.** Parameters of the synthetic forward model (compositions in weight fractions, lengths in Å, $q$ in Å⁻¹).

| Group | Parameter | Value |
| --- | --- | --- |
| Phase boundaries | emulsion: $x = 0.15 + 0.55\,y$; order–disorder: $y = 0.42 + 0.50\,x$; cubic–hexagonal: $y = 0.72 + 0.30\,x$ | sigmoid widths 0.012 |
| Micelles (L1) | dry radius $R_0$, cap on swollen radius, swelling strength | 60, 95, 1.2 |
| | polydispersity (Gaussian, relative), quadrature points | 0.08, 15 |
| | hard-sphere radius / micelle radius; volume fraction per surfactant fraction, range | 1.25; 0.9, 0.05–0.45 |
| Ordered phases | FCC (111) position at $(0, 0.5)$; resolution-limited width; extra width near the transition | 0.045, 0.0016, 0.004 |
| | FCC peak ratios and amplitudes | $\sqrt{3,4,8,11,12}/\sqrt{3}$; 30, 9, 5, 2.5, 1.5 |
| | hexagonal peak ratios and amplitudes; $q^\ast$ relative to FCC | $\sqrt{1,3,4,7}$; 40, 8, 5, 2; 1.25 |
| Emulsion and background | Porod amplitude per 0.1 excess oil; flat background | $4 \times 10^{-8}$; $5 \times 10^{-5}$ |
| Intensity | amplitude per surfactant fraction; floor | 2.0; 0.02 |

**Design.** A hierarchical Poisson-disk design on the unit square with nine levels, with the corners forced into the coarsest level, is restricted to the triangle $x + y \le 1$, which leaves 2118 sites. The natural-neighbour interpolant adds mirror images of the measured sites across $x = 0$, $y = 0$ and $x + y = 1$, and across the origin, each carrying the spectrum of its preimage (SI 1.1).

**Descriptors and claims.** The dominant peak is the tallest interior local maximum, its position refined below the grid spacing by a parabola in logarithmic coordinates; its width and height above baseline are measured as for the NaCl line. A site is of interest when its dominant peak rises above its local baseline by at least five times that baseline, which holds for most ordered compositions and for part of the micellar phase. A prediction fails when it disagrees on the presence of a dominant peak, or misses its position by more than 0.005 Å⁻¹ or its width by more than 0.001 Å⁻¹. Sites without a peak in truth and prediction pass.

---

## Notes for revision (not part of the text)

- The correction is the stage-1 engine developed for the BSISB maps. The constraint set and the decision log for rejected designs are documented with the code, which goes to Zenodo with the data.
- An earlier version of the record used the map median as the starting estimate and a design on the unit square. Both were replaced before submission. The old record is in the repository history.
- References to check: [MartensStark1991] Martens, Stark (1991), J. Pharm. Biomed. Anal. 9, 625–635. [Kohler2005] Kohler et al. (2005), Appl. Spectrosc. 59, 707–716. [Bassan2010] Bassan et al. (2010), Analyst 135, 268–277 (RMieS-EMSC). [Solheim2019] Solheim et al. (2019), J. Biophotonics 12, e201800415 (open-source ME-EMSC). [vandeHulst1957] van de Hulst (1957), Light Scattering by Small Particles, Wiley. Consider Konevskikh et al. on the identifiable size–refractive-index pair.
