# SI 1. Interpolators (draft 1)

## SI 1.1 Natural-neighbour interpolation

A prediction at an unmeasured site must depend on positions only, so that one set of weights serves every channel and every derived quantity. Natural-neighbour (Sibson) coordinates meet that need [Sibson1981]. Inserting the query site $x$ into the Voronoi diagram of the measured sites gives it a cell $V(x)$, and the weight of measured site $i$ is the share of that cell taken from the cell $V_i$ of site $i$,

$$
w_i(x) = |V(x) \cap V_i| \, / \, |V(x)|
$$

The weights are nonnegative, sum to one, reproduce linear functions and vary continuously with $x$ [Sibson1981]. The prediction of a spectrum is $\hat y(x) = \sum_i w_i(x) \, y_i$, and a derived quantity is taken from that predicted spectrum.

**Construction.** The natural neighbours of $x$ are the measured sites whose Delaunay triangles have circumcircles containing $x$ [Watson1992]. The cell $V(x)$ is the intersection of the half-planes bounded by the perpendicular bisectors between $x$ and its natural neighbours, and each stolen area $|V(x) \cap V_i|$ is the area of a convex polygon obtained by clipping $V(x)$ with the bisectors of site $i$. Every step is a convex clip, so the result does not depend on the orientation in which the triangulation library returns its cells. On a hull edge the cell is unbounded; there the weights take their limiting values, linear between the two boundary sites that bracket the query. Outside the hull of the measured set, inverse-distance weights over the five nearest measured sites are used. On the synthetic map, mirror images of the measured sites across the three walls of the composition triangle, and across the origin, join the point set with the spectra of their preimages, so that sites near a wall have neighbours on all sides.

**Checks.** On random point sets the weights agree with stolen areas computed by brute-force Monte Carlo integration to Monte Carlo precision; linear functions are reproduced to rounding; predictions on a raster change continuously under small perturbations of the positions; and along a hull edge they are linear. A perturbation of $10^{-9}$ of the NaCl raster positions changes predictions by at most $3 \times 10^{-7}$ and flips no failure label (SI 4).

**An earlier implementation.** The routine used in the original analyses of the IR map and the NaCl scan clipped polygons on the assumption of counter-clockwise orientation. Cells returned clockwise clipped to nothing, and the routine fell back silently to barycentric weights on the enclosing Delaunay triangle. On 200 random sites, 134 of 300 queries took that fallback, and a perturbation of $10^{-9}$ of the NaCl positions flipped 22 of 271 failure labels at level 5 and 33 of 521 at level 6. The switch depended on the build of the triangulation library, which explains why archived numbers drifted from reruns after the first guaranteed levels. A guarantee concerns the predictor actually used, so the archived bounds remain valid for that predictor; every number in this paper uses the exact construction.

## SI 1.2 Gaussian-process interpolation on the design

The Gaussian-process protocols use an isotropic squared-exponential kernel on the coordinates of the hierarchical design: the unit square for the two scattering maps, and micrometres divided by 41 µm for the IR map, an isotropic rescaling of the physical raster [RasmussenWilliams2006]. With measured positions $X$, measured spectra $Y$ (one row per site), their column mean $\bar y$, kernel matrix $K$ and nugget $\nu$ relative to unit output scale, the prediction at a design site $x$ is

$$
\hat y(x) = \bar y + k(x)^\top (K + \nu I)^{-1} (Y - \bar y)
$$

and the interpolation score is the posterior standard deviation at unit output scale,

$$
\sigma(x)^2 = k(x, x) - k(x)^\top (K + \nu I)^{-1} k(x)
$$

One set of weights serves every channel of the spectrum, so the fit costs one Cholesky factorisation per level. The score depends on positions, length scale and nugget only. The interest claim keeps its natural-neighbour score.

**Length-scale rules.**

1. *Maximum likelihood.* The leading three principal-component scores of the centred measured spectra are modelled as independent outputs that share one length scale and one output scale, each with its own noise variance. The marginal likelihood is maximised with L-BFGS-B over all outputs jointly, with the length scale bounded below by a quarter of the smallest nearest-neighbour distance in the measured set and above by 2 (BoTorch 0.18, GPyTorch 1.15 [Balandat2020; Gardner2018]). The nugget used for prediction is the median fitted noise-to-signal ratio over the three components.
2. *Design spacing.* The length scale equals the median nearest-neighbour distance among design sites up to the finest level present in the measured set; $\nu = 10^{-3}$.
3. *Local spacing.* A Gibbs kernel [Gibbs1997; PaciorekSchervish2004],

$$
k(x, x') = \frac{2 \ell(x) \ell(x')}{\ell(x)^2 + \ell(x')^2} \exp\left(-\frac{\lVert x - x' \rVert^2}{\ell(x)^2 + \ell(x')^2}\right)
$$

with $\ell(x)$ the distance from $x$ to its third-nearest measured site, clipped to the interval from the finest design spacing to $\sqrt{2}/2$; $\nu = 10^{-3}$. The kernel is positive semidefinite for any positive $\ell$ and reduces to the isotropic kernel for constant $\ell$.

In every rule, the length scale of a level is fixed from the measured set before the calibration draw, so the score is frozen in the sense of Section 3.1.

**Table S1.1.** Length scales and nuggets over all guaranteed levels and 20 campaigns (matched-quantile rule), in design units (the unit square; for the IR map, micrometres divided by 41, so 0.024 corresponds to 1 µm). Median, with the range in parentheses. For the local-spacing rule the entry is the median local length scale over measured sites.

| Dataset | Max. likelihood: $\ell$ | Max. likelihood: $\nu$ | Design spacing: $\ell$ | Local spacing: median $\ell$ |
| --- | --- | --- | --- | --- |
| IR map | 0.069 (0.045–0.082) | 0.36 (0.038–0.82) | 0.045 (0.024–0.088) | 0.071 (0.049–0.101) |
| NaCl scan | 0.072 (0.029–0.120) | 1.47 (0.007–5.04) | 0.064 (0.036–0.107) | 0.077 (0.040–0.113) |
| Synthetic map | 0.147 (0.055–0.296) | 0.085 (0.009–0.27) | 0.045 (0.019–0.109) | 0.050 (0.020–0.118) |

The three rules give visibly different reasons for measuring a site (Fig. S1). The design-spacing rule gives the shortest length scale and the most structured standard deviation, high in every gap between measured sites. Maximum likelihood on the IR map assigned much of the variance to noise and returned a nearly uniform standard deviation. The local-spacing rule lengthens the kernel where measurements are sparse and lowers the standard deviation there.

**Figure S1.** Posterior standard deviation on the IR map before level 5 (first campaign of the record, local-spacing protocol; 167 measured sites, dots) under the three length-scale rules, evaluated on the full 42 × 29 µm raster, and the local length scale of the third rule. Length scales are given in micrometres. File: `figures/figS1_gp_std.png`.

**Checks.** Unit tests confirm that the weights reproduce the BoTorch posterior mean and variance for fixed hyperparameters, that the design rule follows the finest measured level, that the Gibbs kernel is positive semidefinite and reduces to the isotropic kernel for constant $\ell$, and that the local length scale is long where measured sites are sparse.

---


## SI 1.3 Scores of the natural-neighbour protocol

The interpolation score is one minus the probability of acceptance from a logistic regression, fitted by leave-one-out on the measured set (at most 120 sites) on the disagreement between natural neighbours in units of the acceptance metric and on the position. The interest score depends on the dataset. On the IR map it is the predicted maximum in the window, capped below the interest level, so that a site predicted to be of interest is never covered. On the two scattering datasets it is the probability of interest from a logistic regression on the predicted peak height above its baseline, the spread of that height over the five nearest measured sites and the distance to the nearest of them.

## Notes for revision (not part of the text)

- References to add: [Sibson1981] (see Section 4 notes); [Watson1992] Watson (1992), Contouring: A Guide to the Analysis and Display of Spatial Data, Pergamon (natural-neighbour construction; check).
