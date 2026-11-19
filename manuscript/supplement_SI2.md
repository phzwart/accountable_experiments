# SI 2. Dataset processing (draft 1: infrared map)

## SI 2.1 Infrared map

**Data.** The map covers 29 × 42 pixels at a pitch of 1 µm, with 1738 channels between 650 and 4000 cm⁻¹ in apparent absorbance. The certificate window is 1500–1850 cm⁻¹. It holds the amide and ester bands, where scattering distortions are strongest next to the absorption bands.

**Scattering correction.** Particles of a few micrometres scatter infrared light resonantly. The result is broad oscillations and dispersive swings at band edges, superimposed on the absorbance. Each spectrum is corrected by extended multiplicative signal correction with a resonant Mie basis [MartensStark1991; Kohler2005; Bassan2010; Solheim2019]. The measured apparent absorbance is modelled as a scaled chemical spectrum plus a scattering background:

$$ A(\nu) = b\,A_{\mathrm{c}}(\nu) + B(\nu) $$

The background is a combination of seven signed principal components of a family of scattering-only extinction curves in the van de Hulst approximation [vandeHulst1957]. The family spans sphere radii of 2–8 µm, real refractive indices of 1.1–1.5 and imaginary indices peaking at 0.02–0.12, shaped by the current chemical estimate, with the dispersion obtained through the Kramers–Kronig relation. Absorption by the particles belongs to the chemical term and is left out of the basis. The fit has the following constraints:

- the background lies between zero and the measured spectrum;
- b is at least 0.05;
- the slope of the chemical spectrum is flat in 2100–2300 and 2390–2800 cm⁻¹;
- its level is pulled towards zero in 2390–2800 and 3850–4000 cm⁻¹;
- the background stays above the chord between these anchor windows across 2800–3850 cm⁻¹.

The chemical estimate is refined self-consistently. Each pixel starts from its own apparent absorbance, and after each of six iterations its estimate is replaced by its own corrected spectrum. No information passes between pixels, so the correction is a fixed transformation of each spectrum and can be applied to a site as soon as it is measured.

The corrected spectrum used throughout is the apparent absorbance minus the fitted background, clipped at zero; the scale b is not divided out. A site is of interest when any channel in the certificate window reaches absorbance 0.1. That holds for 37 % of the pixels.

**Sensitivity to the starting estimate.** The iteration converges to the same corrected spectrum for most pixels, whatever the starting estimate. Starting from the median spectrum of the map instead of each pixel's own spectrum changes the corrected window by a median of 0.001. For about 5 % of the pixels it changes it by more than 0.05, and 20 of 1218 pixels change their interest label. The guarantees of the main text concern the target as defined by the per-pixel correction. Any fixed per-spectrum transformation defines a valid target.

**Design.** The hierarchical Poisson-disk design is drawn on the physical rectangle, 41 × 28 µm between the centres of the corner pixels. The radii run from 6.8 µm down to 0.85 µm in seven levels, each a factor $\sqrt{2}$ below the previous one, with the four corners forced into the coarsest level. Sites are snapped to the nearest pixel, and the coarsest level is kept when two sites share a pixel. Of 1064 sites, 959 remain, with 23, 13, 37, 71, 142, 245 and 428 sites on levels 0–6. Distances for the interpolators are taken in micrometres, divided by 41 µm for numerical convenience. This rescaling is isotropic and leaves the geometry unchanged.

## SI 2.2 NaCl microdiffraction scan

*To draft: integration, presence test at 5σ, (200) width and its tolerance of 0.02 nm⁻¹.*

## SI 2.3 Synthetic small-angle scattering map

*To draft: forward model, composition triangle, mirror images for the natural-neighbour interpolant.*

---

## Notes for revision (not part of the text)

- The correction is the stage-1 engine developed for the BSISB maps. The constraint set and the decision log for rejected designs are documented with the code, which goes to Zenodo with the data.
- An earlier version of the record used the map median as the starting estimate and a design on the unit square. Both were replaced before submission. The old record is in the repository history.
- References to check: [MartensStark1991] Martens, Stark (1991), J. Pharm. Biomed. Anal. 9, 625–635. [Kohler2005] Kohler et al. (2005), Appl. Spectrosc. 59, 707–716. [Bassan2010] Bassan et al. (2010), Analyst 135, 268–277 (RMieS-EMSC). [Solheim2019] Solheim et al. (2019), J. Biophotonics 12, e201800415 (open-source ME-EMSC). [vandeHulst1957] van de Hulst (1957), Light Scattering by Small Particles, Wiley. Consider Konevskikh et al. on the identifiable size–refractive-index pair.
