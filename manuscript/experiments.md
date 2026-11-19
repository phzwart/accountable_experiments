# 4 Experiments (draft 1: section 4.3, Gaussian-process protocols)

*Sections 4.1, 4.2 and 4.4 and the natural-neighbour part of 4.3 follow the plan and are still to be drafted.*

## 4.3 Protocols

*Natural-neighbour protocol: to draft (Sibson coordinates on full spectra and on derived scalars, logistic scores).*

**Gaussian-process protocols.** Gaussian-process regression is the interpolator of choice for autonomous scattering experiments [Noack2019; Noack2020], and it offers a reason for every measurement: the posterior standard deviation is large where the measured set is far away in units of the length scale. The GP protocols place an isotropic squared-exponential kernel on the coordinates of the hierarchical design and evaluate the process only at design sites [RasmussenWilliams2006]. The posterior mean predicts the full spectrum at a site; the posterior standard deviation at unit output scale orders the sites for the interpolation certificate. Both depend on the measured set through one set of linear weights, so the spectrum and any quantity derived from it come from the same fit, as with natural-neighbour coordinates. The interest certificate keeps its score from the natural-neighbour protocol, which isolates the change of interpolator.

The length scale is set in three ways, each fixed before the calibration draw of a level. In the first, it maximises the marginal likelihood of the leading three principal-component scores of the measured spectra, with one length scale shared by the components [Balandat2020]. In the second, it equals the median nearest-neighbour spacing of the design through the finest level already measured, a quantity known before the experiment starts. In the third, the length scale varies across the sample: a Gibbs kernel [Gibbs1997; PaciorekSchervish2004] takes as local length scale the distance to the third-nearest measured site. Measurements guided by the interest certificate cluster where the sample holds something of interest and thin out elsewhere, so the local length scale is short in the first regions and long in the second. Details, including the nugget and the bounds on the length scale, are in SI 1.

---

## Notes for revision (not part of the text)

- *Isotropy.* Decided: physical coordinates in micrometres for IR (needs the IR design redrawn on the physical rectangle and the IR rows rerun). Previous state: the kernel is isotropic in design coordinates, the unit square on which the hierarchical design was drawn. The IR raster (42 × 29 µm) maps onto that square with different scales along the two axes, so the kernel is mildly anisotropic in physical units for IR. The natural-neighbour weights use the same coordinates. Decide whether to keep design coordinates for both (current choice) or move both to physical coordinates.
- *Interest score.* Kept from the natural-neighbour protocol on purpose; only the interpolator and the interpolation score change. If a reviewer asks for a fully GP protocol, a GP-predicted maximum is a small addition.
- *Mirror images.* The synthetic map uses mirror images at the composition walls for natural-neighbour interpolation. The GP protocols use none.
- References to add: [RasmussenWilliams2006] Rasmussen, Williams (2006), Gaussian Processes for Machine Learning, MIT Press. [Balandat2020] Balandat et al. (2020), BoTorch, NeurIPS 33. [Gibbs1997] Gibbs (1997), PhD thesis, Cambridge. [PaciorekSchervish2004] Paciorek, Schervish (2004), NeurIPS 16. Consider Noack & Sethian (2022) on non-stationary kernels for autonomous experiments (check details).
