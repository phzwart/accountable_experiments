# SI 1. Interpolators (draft 1: Gaussian-process part)

*The natural-neighbour part (exact construction, hull-edge limit, check against brute-force stolen areas, the defect in the earlier implementation) is still to be drafted.*

## SI 1.x Gaussian-process interpolation on the design

The Gaussian-process protocols use an isotropic squared-exponential kernel on the coordinates of the hierarchical design, the unit square on which the design was drawn [RasmussenWilliams2006]. With measured positions $X$, measured spectra $Y$ (one row per site), their column mean $\bar y$, kernel matrix $K$ and nugget $\nu$ relative to unit output scale, the prediction at a design site $x$ is

$$
\hat y(x) = \bar y + k(x)^\top (K + \nu I)^{-1} (Y - \bar y)
$$

and the interpolation score is the posterior standard deviation at unit output scale,

$$
\sigma(x)^2 = k(x, x) - k(x)^\top (K + \nu I)^{-1} k(x)
$$

One set of weights serves every channel of the spectrum, so the fit costs one Cholesky factorisation per level. The score depends on positions, length scale and nugget only. The interest certificate keeps its natural-neighbour score.

**Length-scale rules.**

1. *Maximum likelihood.* The leading three principal-component scores of the centred measured spectra are modelled as independent outputs that share one length scale and one output scale, each with its own noise variance. The marginal likelihood is maximised with L-BFGS-B over all outputs jointly, with the length scale bounded below by a quarter of the smallest nearest-neighbour distance in the measured set and above by 2 (BoTorch 0.18, GPyTorch 1.15 [Balandat2020; Gardner2018]). The nugget used for prediction is the median fitted noise-to-signal ratio over the three components.
2. *Design spacing.* The length scale equals the median nearest-neighbour distance among design sites up to the finest level present in the measured set; $\nu = 10^{-3}$.
3. *Local spacing.* A Gibbs kernel [Gibbs1997; PaciorekSchervish2004],

$$
k(x, x') = \frac{2 \ell(x) \ell(x')}{\ell(x)^2 + \ell(x')^2} \exp\left(-\frac{\lVert x - x' \rVert^2}{\ell(x)^2 + \ell(x')^2}\right)
$$

with $\ell(x)$ the distance from $x$ to its third-nearest measured site, clipped to the interval from the finest design spacing to $\sqrt{2}/2$; $\nu = 10^{-3}$. The kernel is positive semidefinite for any positive $\ell$ and reduces to the isotropic kernel for constant $\ell$.

In every rule, the length scale of a level is fixed from the measured set before the calibration draw, so the score is frozen in the sense of Section 3.1.

**Table S1.1.** Length scales and nuggets over all certified levels and 20 seeds (quantile path), in design units (the unit square). Median, with the range in parentheses. For the local-spacing rule the entry is the median local length scale over measured sites.

| Dataset | Max. likelihood: $\ell$ | Max. likelihood: $\nu$ | Design spacing: $\ell$ | Local spacing: median $\ell$ |
| --- | --- | --- | --- | --- |
| IR map | 0.077 (0.057–0.095) | 0.12 (0.007–0.61) | 0.058 (0.036–0.104) | 0.078 (0.043–0.118) |
| NaCl scan | 0.072 (0.029–0.120) | 1.47 (0.007–5.04) | 0.064 (0.036–0.107) | 0.077 (0.040–0.113) |
| Synthetic map | 0.150 (0.070–0.296) | 0.083 (0.018–0.27) | 0.045 (0.019–0.109) | 0.051 (0.021–0.118) |

**Figure S1.** Posterior standard deviation on the IR map before level 5 (seed 0, local-spacing campaign; 185 measured sites, dots) under the three length-scale rules, evaluated on the full 42 × 29 µm raster, and the local length scale of the third rule. Length scales are converted to micrometres along the 42 µm axis; the design coordinates scale the 29 µm axis by a factor 0.69 relative to it. File: `figures/figS1_gp_std.png`.

**Checks.** Unit tests confirm that the weights reproduce the BoTorch posterior mean and variance for fixed hyperparameters, that the design rule follows the finest measured level, that the Gibbs kernel is positive semidefinite and reduces to the isotropic kernel for constant $\ell$, and that the local length scale is long where measured sites are sparse.

---

*Reference to add: [Gardner2018] Gardner, Pleiss, Bindel, Weinberger, Wilson (2018). GPyTorch. NeurIPS 31.*
