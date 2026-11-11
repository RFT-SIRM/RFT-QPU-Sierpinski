# Validation Plan

## Current baseline

The repository now contains the level-1 numerical and hardware-mapping prototype in `engineering/physical_prototype/`. Its package test suite reported 20 passing tests locally on 10 November 2026. The post-merge GitHub Actions run on `main` completed successfully and reproduced the configured level-1 calculation.

A green numerical test suite verifies the implemented model and code paths. It does not validate a fabricated device.

## Gate 0 — Mathematical reference

**Status: documented in the companion project.**

- reproduce the fourth spectral-moment formula and stated normalization;
- record the exact graph, face ordering, edge orientation and axis assignment;
- preserve the boundary between the graph-level Lean infrastructure and any still-open operator-level formalization.

## Gate 1 — Finite-level numerical model

**Status: implemented for SG levels 1–5.**

- construct the finite Sierpiński graph using the reference recursion;
- build the SU(2)-transport Hamiltonian;
- compute spectra, candidate doublets and leakage gaps;
- compute local/global projected controls;
- test graph, Hamiltonian, hardware mapping, disorder/thermal analysis and two-cell projection.

Acceptance for future changes: exact regression checks on graph counts, link assignments, Hermiticity, matrix dimensions and benchmark outputs.

## Gate 2 — Hardware coefficient export

**Status: generated; one critical phase-realization issue remains open.**

- export the 22 level-1 effective exchange channels;
- preserve complex amplitudes and the sign/orientation convention;
- validate endpoint frequency assumptions and detunings;
- resolve the resonant complex-Z link with a physical coupler topology;
- include parasitic ZZ, spectator interactions, pump sidebands and higher-level leakage.

**Tape-out blocker:** a single real static coupler does not reproduce the current complex Z-link amplitudes.

## Gate 2A — Isolated phase-conjugate Z-link screen

**Status: implemented in a reduced effective two-/four-qutrit model.** The concurrent block gives process overlap 0.999609. This is a reduced-block trace overlap, not an average two-qubit gate fidelity.

## Gate 2B — Nine-tone spectral collision screen

**Status: implemented; current frequency assignment fails.** The first-order primary-tone screen finds 0 MHz minimum margin and 73 warnings within 10 MHz. Conditional harmonics and pairwise intermodulation scenarios raise the count to 653. This is a resonance-candidate screen, not a full Floquet solution or measured device failure.

Do not approve simultaneous nine-tone operation until the frame plan is redesigned and actual channel isolation is measured.

## Gate 3 — Physical single-cell demonstrator

**Status: not fabricated or measured.**

Required evidence:

- 12-transmon chip and verified connectivity;
- calibrated frequencies, exchange amplitudes and pump phases;
- measured spectrum and reconstruction of the candidate doublet;
- measured separation from leakage states;
- state preparation, reset and readout calibration;
- projected-control tomography and pulse calibration;
- leakage, crosstalk, drift and non-gauge noise characterization.

No protection or fidelity claim should be made from the ideal Hamiltonian alone.

## Gate 4 — Two-cell entangling demonstrator

**Status: projected numerically; no physical gate demonstrated.**

- connect two calibrated level-1 cells (24 data transmons);
- implement the four cross-Kerr terms with the required \(+,-,-,+\) sign pattern;
- characterize static shifts, excitation conservation, residual interactions and leakage;
- calibrate the pulse and measure process fidelity, leakage, crosstalk and repeatability.

The quoted 6.38074 μs is an ideal projected estimate at the illustrative assumption \(\chi/(2\pi)=10\) MHz, not a measured gate time.

## Gate 5 — Modular scale-up

**Status: future work.**

Only after the single-cell and two-cell gates pass measured acceptance criteria:

1. replicate calibrated level-1 tiles;
2. begin with nearest-neighbour logical modules in a one-dimensional chain;
3. validate control/readout wiring and inter-tile crosstalk;
4. consider two-dimensional and fractal module connectivity only after routing and error data justify it.

## Evidence labels

- **Analytic/formal:** exact identities and machine-checked results within their stated assumptions.
- **Numerical:** outputs of the finite matrix and circuit-mapping models.
- **Proposed engineering:** circuit and control designs without fabrication evidence.
- **Experimental:** measured hardware data only.

These categories must remain separate in README, the website, partner material and future release notes.
