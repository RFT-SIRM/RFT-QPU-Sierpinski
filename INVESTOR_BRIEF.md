# RFT-QPU-Sierpinski — Investor / Strategic Partner Brief

## The thesis

RFT-QPU-Sierpinski investigates whether quantum hardware can be designed around a mathematically structured, self-similar connectivity architecture rather than treating device geometry as a secondary implementation detail.

## The technical anchor

The companion Evgeny's Theorem repository reports an exact fourth spectral-moment defect for a noncommutative SU(2) connection on the Sierpiński gasket:

`Δ_m(H⁴,θ) = −16(3^(m−1)+1) sin²(θ/2)`.

At the nominal point `θ = π/2`, the normalized invariant approaches `−8/9`.

## The product hypothesis

The proposed hardware program is to combine:

**self-similar geometry + SU(2) transport + low-dimensional spectral encoding + projected control**

into a physical quantum-processing element.

## Development path

1. Complete the numerical architecture solver.
2. Identify and characterize the two-dimensional logical subspace.
3. Quantify leakage and control matrices.
4. Map the effective Hamiltonian onto a physical platform.
5. Fabricate a small demonstrator.
6. Measure spectra, control fidelity, leakage and disorder sensitivity.
7. Scale from one logical element to coupled elements.

## Investment-relevant milestones

| Milestone | Evidence required |
|---|---|
| Mathematical foundation | Reproducible theorem repository and formalization artifacts |
| Numerical qubit | Reproducible spectral isolation and projected-control results |
| Device mapping | Hamiltonian-to-hardware derivation |
| Prototype | Fabricated test structure and measured spectrum |
| Gate demonstration | Calibrated single-/multi-qubit operations |
| Protection claim | Experimental noise and leakage measurements |

## IP

The architecture is being documented as a technical disclosure for patent-counsel review. See `PATENT_SPEC.md` and `LICENSE.md`.

## Critical diligence point

This project should be evaluated on reproducible mathematical, numerical and experimental milestones. The repository does not claim that a fault-tolerant physical QPU has already been demonstrated.
