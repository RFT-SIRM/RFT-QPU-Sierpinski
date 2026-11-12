# Validation plan — current state and acceptance gates

**Review date:** 12 November 2026  
**Engineering checkpoint:** v0.4-rc1 public research baseline; numerical model only, not a hardware release.

## Current baseline

Stages 1–11B are recorded in this repository. Stage 11B has:
- an initial full three-mode rebuild in the re-quantized coupler basis;
- 120/240/480 temporal-grid convergence for the initial baseline, with archived complex matrices;
- a later local pulse retune with reported five-level 480-grid metrics and five-/six-level comparisons;
- only a seven-level 120-grid spot check for the retuned point.

The local retune raw JSON/NPZ artifacts are not tracked. The selected point is recorded in the root README and in the Stage 11B local-retune note. It must be archived with a reproducing runner before it is treated as a fully reproducible numerical release artifact.

A passing numerical test suite verifies the code and mathematical model represented by the tests. It does not validate a fabricated device. Public release invites independent scrutiny; it does not imply that the remaining engineering gates have passed.

## Gate 0 — software/model integrity

**Status: completed for the recorded pre-release checkpoint.**

- [x] Canonical finite graph construction and level counts.
- [x] SU(2) edge-transport Hamiltonian.
- [x] Hermiticity, covariance and effective-symmetry regression tests.
- [x] Candidate spectrum, leakage gap and projected-control analysis.
- [x] Coefficient export and two-cell static projection.
- [x] Circuit-model and Stage 11B baseline regression tests.
- [x] Historical local test record: 75 passed.
- [x] Merged Stage 11B PR #5 CI: run #23 succeeded on its reviewed head.

The public-release documentation commit requires its own CI result; earlier successful runs do not certify this commit.

## Gate 1 — finite graph and proposed hardware coefficient map

**Status: implemented numerically; physical phase-realization issue remains open.**

The level-1 tile has 6 graph sites, 9 graph edges, 3 non-commuting face links, 12 transmon modes and 22 effective exchange channels.

Required before circuit qualification:
- [ ] Preserve edge orientation and all complex amplitudes in a device-level netlist.
- [ ] Resolve the resonant complex Z edge using a multi-path/static-flux or auxiliary Floquet embodiment, or revise the frame/frequency plan.
- [ ] Derive the physical coupler Hamiltonian for each channel.
- [ ] Include residual ZZ, static exchange, spectator terms and higher transmon levels.
- [ ] Verify rotating-wave and parametric-drive approximations against the proposed device.

## Gate 2 — graph-wide multitone feasibility

**Status: not cleared.**

The existing first-order screen reports:
- 73 primary-tone warnings within 10 MHz;
- 653 conditional harmonic/intermodulation warnings;
- 0 MHz minimum primary margin.

These are resonance candidates, not measured error rates or a full Floquet/Sambe solution.

Required:
- [ ] Redesign the six frame offsets and frequency assignment.
- [ ] Measure or extract the complex 22×22 channel-transfer matrix.
- [ ] Include actual coupler and pump response.
- [ ] Run multitone Floquet/circuit simulation and open-system validation.
- [ ] Demonstrate simultaneous operation experimentally before enabling the full nine-tone schedule.

## Gate 3 — Stage 11B re-quantized three-mode gate model

**Status: initial baseline and local nominal retune recorded; full convergence and uncertainty qualification remain open.**

The initial baseline was rebuilt at shifted DC flux in the new local SQUID eigenbasis. The tracked baseline covers charge cutoff 10, five retained levels per mode, a 125-dimensional product Hilbert space, and 120/240/480 time grids.

The later selected local retune is:
- bias 0.25884589447013934 Φ₀;
- pump 987.6171621707836 MHz;
- amplitude 0.0199946062 Φ₀;
- requested duration 1.081140796 μs;
- raised-cosine ramp of 8 pump periods.

At five retained levels and 480 steps per period, the local README record gives projected process overlap 0.9999999793763371 after local-Z fitting and average logical-state fidelity including leakage 0.9999999803654352. The six-level 480-grid process overlap is 0.999999967757. The seven-level 240/480 propagation remains incomplete.

Required:
- [ ] Add the raw fine-retune JSON/NPZ files to the repository with their original manifests and hashes.
- [ ] Add an exact runner/configuration that reproduces the selected local point.
- [ ] Complete seven-level 240/480 temporal propagation.
- [ ] Compare phase-aligned full matrices across five, six and seven retained levels.
- [ ] Extend the full driven charge-cutoff study.
- [ ] Turn local deterministic searches into uncertainty and worst-case tolerance maps.

All Stage 11B process results are closed-system model projections, not measured gate fidelity.

## Gate 4 — circuit/noise qualification

**Status: not started as a measured-device programme.**

- [ ] Replace Stage-3 nominal capacitances/Josephson parameters with layout-extracted values.
- [ ] Obtain independent EM/circuit-QED review.
- [ ] Measure or specify a realistic flux-line transfer function, bandwidth, delay and distortion.
- [ ] Characterise pump phase noise, amplitude noise and cross-channel crosstalk.
- [ ] Add T1/T2, thermal occupation, relaxation, dephasing, leakage and spectator dynamics.
- [ ] Include fabrication variation and repeated-cooldown drift.
- [ ] Resolve packaging, filtering, magnetic environment and readout architecture.

## Gate 5 — one-cell fabricated demonstrator

**Status: not fabricated or measured.**

Acceptance requires a 12-transmon tile, spectroscopy of all modes, calibration of all complex hopping amplitudes/phases, reconstruction of the candidate doublet and leakage gap, projected X/Y/Z control tomography, reset/readout calibration, measured leakage and coherence, and repeatability across cooldowns.

A single successful cell demonstrates one logical element only; it does not demonstrate a universal processor.

## Gate 6 — two-cell entangling demonstrator

**Status: static numerical projection only.**

The model's two-cell interaction coefficient is 0.00783608327 χ. The ideal 6.38074 μs time estimate assumes χ/(2π) = 10 MHz.

Acceptance requires:
- [ ] Two calibrated level-1 cells (24 data transmons).
- [ ] Four cross-Kerr channels with the required sign pattern.
- [ ] Calibrated pulse and measured non-local gate invariant/process tomography.
- [ ] Leakage, spectator effects, crosstalk and repeatability measurements.

## Gate 7 — modular scale-up and protection claims

**Status: future work.**

Only after single-cell and two-cell hardware acceptance:
1. replicate calibrated level-1 cells;
2. start with nearest-neighbour modules and measured inter-cell coupling;
3. validate simultaneous controls, readout and correlated errors;
4. consider larger or fractal module-level connectivity from measured data;
5. make protection or fault-tolerance claims only after a measured logical-error suppression experiment.

## Evidence vocabulary

- **Analytic / formal:** identities or proofs within stated assumptions.
- **Numerical:** output from a specified finite matrix or circuit model.
- **Proposed engineering:** coefficient maps and device designs without fabrication evidence.
- **Experimental:** measured hardware results only.

Keep these labels consistent across the README, partner material, validation reports and any later public release.
