# Evidence and Disclosure Boundary

This file separates established mathematical results, numerical model outputs, proposed hardware design and experimental evidence.

| Item | Status | Evidence class |
|---|---|---|
| Sierpiński graph construction and finite-level counts | Implemented for levels 1–5 | Numerical/computable |
| Fourth spectral-moment closed form | Documented in companion project | Analytic + numerical reference |
| \(I_\infty(\pi/2)=-8/9\) | Consequence of the stated normalization | Analytic |
| Gauge spectral invariance | Numerically validated in companion work | Numerical |
| General operator-level Lean proof of TraceDefectIdentity | Still open in the current companion repository status | Formalization boundary |
| Level-1 12-mode SU(2) Hamiltonian | Implemented and regression-tested | Numerical |
| Level-1 candidate doublet and gap | Splitting \(1.61\times10^{-15}J\); gap \(1.3937126931J\) | Floating-point numerical result |
| Level-1 best local projected-control coefficient | \(g_{\mathrm{eff}}=0.1770433\), vertex 5 | Model-dependent numerical result |
| Level-5 reference control coefficient | \(g_{\mathrm{eff}}\approx0.015085\) | Different refinement/model point |
| 12-transmon level-1 mapping and 22 exchange channels | Coefficient export exists; complex-Z realization unresolved | Proposed engineering |
| Two-cell projected interaction | \(0.00783608327\chi\); ideal estimate 6.38074 μs at assumed \(\chi/(2\pi)=10\) MHz | Static numerical projection |
| Physical QPU fabrication or measurement | Not demonstrated | Not claimed |
| Arbitrary-noise immunity or fault tolerance | Not established | Not claimed |
| \(-8/9\) as a universal energy gap | **Not claimed** | — |

## Interpretation rules

1. The near-zero level-1 doublet splitting is at floating-point roundoff scale; it is not, by itself, a proof of exact degeneracy.
2. The value \(g_{\mathrm{eff}}=0.1770433\) belongs to the level-1 local-control calculation at vertex 5. The value \(0.015085\) is a level-5 reference result. Neither is a universal constant.
3. The \(-8/9\) quantity is a normalized fourth spectral-moment invariant, not an energy gap, a leakage suppression factor or a measure of noise protection.
4. Gauge covariance is a model symmetry property. It does not imply immunity to arbitrary non-gauge laboratory noise.
5. The 12-transmon and 24-transmon configurations are proposed hardware embodiments. No physical device, calibrated gate, or measured fidelity is claimed.
6. The resonant complex-Z link is an open pre-tape-out blocker. The coefficient CSV is not a foundry-ready netlist.

The detailed hardware acceptance criteria are maintained in [Validation Plan](VALIDATION_PLAN.md) and [Physical Realization](../engineering/physical_prototype/docs/PHYSICAL_REALIZATION.md).
