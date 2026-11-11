# Validation Plan

## Current baseline

The repository contains a closed/internal engineering pre-release candidate v0.4-rc1. Stages 1–10 record the circuit-derived coupler and full logical-gate numerical study; Stage 11A adds a separate local SQUID-coupler re-quantization audit. The local release-preparation run used Python 3.14.2 and recorded **75 passed in 1.33s**. The release-candidate pull request must also pass GitHub Actions on Python 3.11 before merge.

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

## Gate 2C — Circuit-derived driven-coupler numerical pre-release

**Status: Stage 10 full-gate candidate converged in the Stage-5 fixed local coupler basis; Stage 11A local coupler re-quantization audit complete; Stage 11B full-gate integration open.**

Stage 10 reference at 480 steps/period:

- DC flux: `0.259343676252 Phi0`.
- Pump frequency: `987.609221499 MHz`.
- Flux amplitude: `0.020000 Phi0`.
- Common duration: `1.081002799582 us`.
- A→B / B→A: `0.999983152623` / `0.999983152074`.
- Projected process overlap after local-Z fitting: `0.999991271648`.
- Conditional iSWAP phase: `0.0021957288 rad`.

These are closed-system projected metrics, not measured gate fidelity. Stages 5–10 use the retained Stage-5 local coupler basis while the flux-dependent coupler Hamiltonian is projected into it.

Stage 11A explicitly re-diagonalizes the local SQUID Hamiltonian at the shifted DC flux and tracks local eigenstates/operator matrices across charge cutoffs `[8, 10, 12]` and retained levels `[3, 4, 5]`. At charge cutoff 12 with five retained local levels, the coupler f01 changes from 5007.500000 MHz to 5075.910813 MHz (Δ +68.410813 MHz); the minimum matched-state overlap probability is 0.9989682 and the minimum retained-subspace singular value is 0.9995692. This is a local-basis audit, not a new full driven-gate result.

Required before this gate can be considered circuit-qualified:

- [ ] Rebuild the complete three-mode Hamiltonian and driven four-state gate using the Stage-11A re-quantized coupler basis.
- [ ] Re-run common-duration 120/240/480 convergence of the full logical matrices.
- [ ] Repeat robust bias/frequency/amplitude/duration sweeps in the rebuilt model.
- [ ] Add flux-line transfer, pump phase noise, crosstalk and open-system T1/T2/thermal effects.

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
