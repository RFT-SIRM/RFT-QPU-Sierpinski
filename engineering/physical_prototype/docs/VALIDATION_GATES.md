# Hardware and model validation gates

## Gate 0 — software/model integrity

- [x] Canonical Sierpiński graph recursion and level counts.
- [x] SU(2) edge transport and graph Hamiltonian construction.
- [x] Hermiticity, covariance and effective-symmetry regression checks.
- [x] Candidate doublet, leakage gap and projected-control analysis.
- [x] Level-1 coefficient export and two-cell static projection.
- [x] Stage 11B initial full three-mode re-quantized baseline with 120/240/480 matrix archive.
- [x] Historical local suite record: 75 passing tests.
- [x] Merged Stage 11B PR #5 CI run #23: successful.

A new documentation branch must pass its own CI check. Gate 0 validates the software/model record only.

## Gate 1 — circuit feasibility (before tape-out)

**Status: open.**

- [ ] Produce a physical coupler Hamiltonian for every complex exchange channel.
- [ ] Resolve the resonant complex Z edge; one real static coupler is insufficient.
- [ ] Validate the multi-path or auxiliary Floquet phase-engineering option.
- [ ] Redesign the graph-wide nine-tone allocation and clear the current 73 primary / 653 conditional warnings.
- [ ] Extract static/driven ZZ, residual exchange, Stark shifts, sidebands and spectator interactions.
- [ ] Simulate multi-level transmons and coupler dynamics.
- [ ] Add realistic open-system T1/T2 and thermal population.
- [ ] Close package, filtering, magnetic environment, flux-line and readout layout.
- [ ] Replace declared circuit assumptions with layout extraction and independent EM/circuit-QED review.

## Gate 2 — one-cell fabricated demonstrator

**Status: not fabricated or measured.**

- [ ] Fabricate one level-1 tile containing 12 data transmons.
- [ ] Spectroscopically identify all modes and the 22 effective exchange channels.
- [ ] Calibrate complex amplitudes and phases with uncertainty bars.
- [ ] Measure the effective Hamiltonian and compare it with the ideal 12×12 one-excitation matrix.
- [ ] Reconstruct the lowest two dressed states and the next leakage state(s).
- [ ] Measure doublet splitting and leakage gap across repeated cooldowns.
- [ ] Reconstruct projected X/Y/Z operators and verify rank three.
- [ ] Demonstrate state preparation, single-logical-qubit rotations and tomography.
- [ ] Measure leakage, coherence, thermal repopulation, drift, reset and readout assignment.

## Gate 3 — two-cell entangling demonstrator

**Status: static model projection only.**

- [ ] Couple two calibrated level-1 cells (24 data transmons).
- [ ] Implement the four cross-Kerr channels with the required (+, −, −, +) sign pattern.
- [ ] Calibrate the two-logical-qubit interaction and pulse envelope.
- [ ] Verify entanglement using process tomography or a suitable non-local invariant.
- [ ] Measure leakage, spectator effects, crosstalk and repeatability.
- [ ] Repeat over bias points and cooldowns.

The 6.38074 μs time estimate assumes χ/(2π)=10 MHz and is not a measured gate time.

## Gate 4 — modular processor tile

**Status: future work.**

- [ ] Replicate at least 5–10 logical cells.
- [ ] Validate simultaneous independent gates and readout.
- [ ] Measure inter-cell crosstalk and correlated errors.
- [ ] Demonstrate stable calibration and automated drift correction.
- [ ] Establish the logical compilation and runtime stack.

## Gate 5 — scalable processor and protection claims

**Status: future work.**

- [ ] Demonstrate a fault-tolerance-compatible logical gate set.
- [ ] Implement and measure a chosen error-correction or leakage-reduction protocol.
- [ ] Show logical error suppression with increasing code size or protection depth.
- [ ] Publish full hardware data, uncertainty budgets and independent reproduction instructions.

A passing software suite is Gate 0 only. A successful one-cell chip is Gate 2 only. Neither alone demonstrates a universal or fault-tolerant quantum computer.
