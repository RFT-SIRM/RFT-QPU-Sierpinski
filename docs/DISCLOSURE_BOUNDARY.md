# Evidence and disclosure boundary

**Review date:** 11 November 2026. This file separates mathematical-model results, numerical outputs, proposed hardware, local reports without tracked raw artifacts and experimental evidence.

## Evidence ledger

| Item | Current status | Evidence class |
|---|---|---|
| Sierpiński graph and finite-level counts | Implemented for levels 1–5 | Numerical/computable |
| Fourth spectral-moment formula and normalized −8/9 value | Referenced in the project README as the mathematical anchor and attributed to the companion mathematical work | Mathematical statement; not an energy gap |
| Gauge spectral invariance | Described in the project record | Mathematical/model property |
| General operator-level Lean proof | Not established by this repository alone | Do not claim complete formal proof from this repository |
| Level-1 12-mode SU(2) Hamiltonian | Implemented and regression-tested | Numerical |
| Level-1 candidate doublet | Near-degenerate to floating-point roundoff | Ideal-model numerical result |
| Level-1 leakage gap | 1.3937127 J | Ideal finite graph Hamiltonian |
| Level-1 local projected-control coefficient | g_eff = 0.1770433, vertex 5 | Model-dependent numerical result |
| Level-5 local projected-control coefficient | g_eff ≈ 0.015085 | Different finite graph/model point |
| Level-1 transmon mapping | 12 modes and 22 exchange channels | Proposed hardware design |
| Resonant complex Z edge | Requires non-real diagonal hopping phases; a single real static coupler is insufficient | Open circuit-feasibility blocker |
| Nine-tone plan | 73 primary warnings and 653 conditional warnings; 0 MHz minimum margin | Not cleared; first-order resonance screen |
| Two-cell interaction | 0.00783608327 χ; 6.38074 μs ideal estimate at assumed χ/(2π)=10 MHz | Static model projection |
| Stage 11B initial full-gate baseline | Tracked JSON/NPZ; 120/240/480 convergence | Closed-system three-mode numerical evidence |
| Stage 11B local retune | 480-grid five-level metrics; six-level 480-grid spot check; seven-level 120-grid spot check | Local run reported in README; raw retune JSON/NPZ not tracked |
| Physical chip or measured gate | None recorded in this repository | Not demonstrated |
| T1/T2/open-system gate performance | Not recorded | Not demonstrated |
| Arbitrary-noise immunity or fault tolerance | Not established | Not claimed |

## Interpretation rules

1. The −8/9 value is a normalized fourth spectral-moment invariant. It is not an energy gap, leakage suppression factor or noise metric.
2. The near-zero ideal doublet splitting is at floating-point roundoff. It is not a manufactured-device splitting measurement or proof of exact device degeneracy.
3. The values g_eff = 0.1770433 (level 1) and 0.015085 (level 5) belong to different finite graphs and are not universal constants.
4. Gauge covariance is a mathematical symmetry property. It does not imply immunity to arbitrary laboratory noise.
5. The Stage 11B gate is a three-mode A–coupler–B calculation. It is not a complete driven simulation of the 12-mode level-1 tile.
6. A process overlap computed from a closed-system projected matrix is not experimental gate fidelity.
7. Transmon and two-cell configurations are proposed embodiments. No chip or calibrated multi-logical-qubit gate is demonstrated.
8. The level-1 coefficient CSV is not a foundry-ready netlist. Complex phases, parasitic couplings, frequency collisions and fabrication geometry still need circuit-level implementation and validation.
9. The fine-retune hashes identify user-side artifacts but cannot substitute for the absent JSON/NPZ files.
10. A passing software test suite validates code/model integrity only.

## Disclosure handling

The repository metadata indicates that the GitHub repository is private. This alone does not prove that the information has never been disclosed elsewhere. Check older repositories, mirrors, sites, talks, preprints, emails, demonstrations and partner discussions before drawing a patent novelty conclusion.

The current patent-oriented disclosure is a private working document for counsel review. No filing number or date is recorded in this repository. See [IP and Licensing](../IP_AND_LICENSING.md) and [Disclosure Log](DISCLOSURE_LOG_TEMPLATE.md).

The Stage 11B outputs are distinguished in [the tracked baseline report](../engineering/physical_prototype/docs/STAGE11B_REQUANTIZED_GATE.md) and [the local retune note](../engineering/physical_prototype/docs/STAGE11B_LOCAL_RETUNE_NOTE.md).
