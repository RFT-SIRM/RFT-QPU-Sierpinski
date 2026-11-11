# Hardware validation gates

## Gate 0 — model/software integrity

- [x] Canonical Sierpinski graph recursion and face/edge ordering in a reproducible package.
- [x] SU(2) edge transport and full Hamiltonian construction.
- [x] Hermiticity and local gauge covariance regression tests.
- [x] Effective time-reversal/Kramers-like symmetry check.
- [x] Projected-control rank and singular-value analysis.
- [x] Level-1 transmon coefficient/netlist export.
- [x] Initial disorder and thermal-scale diagnostics.

## Gate 1 — circuit feasibility (before tape-out)

- [ ] Produce a circuit-level coupler Hamiltonian for every complex channel.
- [ ] Verify all pump frequencies and avoid harmful frequency collisions.
- [ ] Resolve the resonant complex Z-edge channel with a concrete multi-path/static-flux or Floquet coupler design; demonstrate its phase experimentally.
- [ ] Extract static and driven ZZ, residual exchange, Stark shifts and higher sidebands.
- [ ] Simulate at least the first three transmon levels per mode and coupler dynamics.
- [ ] Run a full 12-transmon open-system simulation with measured/target T1, T2, thermal occupation and pump noise.
- [ ] Close package, filtering, magnetic environment, flux-line and readout layout.
- [ ] Obtain independent circuit-QED/fabrication review.

## Gate 2 — one-cell fabricated demonstrator

- [ ] Spectroscopically identify 12 modes and the 22 inter-site exchange channels.
- [ ] Calibrate all complex amplitudes and phases with uncertainty bars.
- [ ] Measure effective Hamiltonian and compare to the ideal 12x12 one-excitation matrix.
- [ ] Reconstruct the lowest two dressed states and next leakage doublet.
- [ ] Measure ground-doublet splitting and leakage gap across repeated cooldowns.
- [ ] Reconstruct projected X/Y/Z operators and verify rank three.
- [ ] Demonstrate state preparation, single-logical-qubit rotations and tomography.
- [ ] Measure leakage, coherence, thermal repopulation and drift.

## Gate 3 — two-cell universal-gate test

- [ ] Couple two level-1 cells (24 transmons).
- [ ] Derive and calibrate a number-conserving inter-cell interaction.
- [ ] Verify that the projected interaction is entangling (nonlocal invariant / process tomography).
- [ ] Measure two-logical-qubit gate fidelity, leakage and spectator effects.
- [ ] Repeat at multiple coupler biases and cooldowns.

## Gate 4 — processor tile

- [ ] Replicate at least 5–10 logical cells.
- [ ] Validate simultaneous independent gates and simultaneous readout.
- [ ] Measure crosstalk and correlated errors between cells.
- [ ] Demonstrate stable calibration and automated drift correction.
- [ ] Produce a first logical compilation and runtime stack.

## Gate 5 — scalable processor / protection claim

- [ ] Demonstrate a fault-tolerance-compatible logical gate set.
- [ ] Implement and measure a chosen error-correction or leakage-reduction protocol.
- [ ] Show logical error suppression with increasing code size or protection depth.
- [ ] Publish full hardware data, uncertainty budgets and independent reproduction instructions.

A green numerical test suite is Gate 0 only. A successful one-cell chip is Gate 2 only. Neither is, by itself, a universal or fault-tolerant quantum computer.

## Closed engineering pre-release candidate v0.4-rc1

This is a **software/model release checkpoint**, not a hardware validation gate. It can be closed independently while the following physical gates remain open.

- [x] Stages 1–10 source, reports, tests and numerical outputs consolidated.
- [x] Stage 10 full logical matrix calculated at 120/240/480 steps per period with a common physical pulse duration.
- [x] Stage 11A local SQUID coupler re-quantization audit executed for charge cutoffs [8, 10, 12] and retained levels [3, 4, 5].
- [x] Local compile and full test suite recorded as **75 passed in 1.33s** on Python 3.14.2.
- [ ] Release-candidate GitHub Actions run on Python 3.11 must pass before merge.
- [ ] Stage 11B: rebuild the complete three-mode Hamiltonian and driven gate using the re-quantized coupler basis; reconverge full matrices at 120/240/480.
- [ ] Re-run robust bias/frequency/amplitude/duration sweeps with the Stage 11B model.
- [ ] Add flux-line transfer, phase noise, crosstalk and open-system T1/T2/thermal models.
- [ ] Replace declared circuit assumptions with layout-extracted parameters and independent circuit-QED/EM review.

**Interpretation:** passing the software pre-release gate does not close Gate 1 circuit feasibility, Gate 2 fabrication, Gate 3 two-cell gate, or any fault-tolerance/scaling gate above.
