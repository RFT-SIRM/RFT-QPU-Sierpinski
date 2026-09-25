# Validation Plan

## Gate 0 — Mathematical reproducibility

- reproduce the companion fourth-moment formula;
- reproduce gauge-invariance tests;
- record software versions and numerical tolerances.

## Gate 1 — Full graph solver

Implement the actual SG(m) graph and SU(2) connection rather than relying on the minimal two-site core.

## Gate 2 — Qubit isolation

For each refinement and physical normalization, report:

- the two selected eigenvalues;
- their splitting;
- the nearest leakage eigenvalue;
- the leakage gap;
- eigenvector stability under perturbations.

## Gate 3 — Control

Construct projected `X_L`, `Y_L`, and `Z_L`. Quantify:

- operator norms;
- linear independence;
- commutators;
- pulse synthesis;
- leakage during pulses.

## Gate 4 — Noise

Separate gauge-equivalent perturbations from physical non-gauge perturbations. Test disorder, drift, thermal effects, control noise and coupling errors.

## Gate 5 — Hardware demonstrator

Specify the physical Hamiltonian, fabrication tolerances, control lines, readout, calibration and measurement protocol.

## Gate 6 — Experimental protection claim

Only after measured data are available should claims concerning robustness, protection, fidelity or scalability be made.
