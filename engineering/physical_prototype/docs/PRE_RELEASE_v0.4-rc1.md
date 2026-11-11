# Closed engineering pre-release candidate v0.4-rc1

**Review update:** 11 November 2026  
**Original pre-release base commit:** d9b374c1dbd7e24050a33b13acf21f57858ff775  
**Current reviewed engineering baseline before this documentation update:** 39c55368d3b3f76ccf0e5116ced0bb0d66dcf9fd

## Release intent

This is a closed/internal engineering-software and numerical-model checkpoint. It is not a fabrication release, foundry package, tape-out authorization, or experimental hardware claim.

The current repository record includes Stages 1–11B. Stage 11B has an initial full three-mode rebuild in the shifted, re-quantized SQUID-coupler basis and a separate local pulse-retuning result. These must be kept distinct.

## Stage 10 fixed-basis reference

Stage 10 remains a useful historical reference, but it uses the Stage-5 fixed local coupler basis:

- DC flux: 0.259343676252320 Φ₀.
- Pump frequency: 987.609221499191 MHz.
- Pump offset: −64.000000 kHz.
- Flux amplitude: 0.02000000 Φ₀.
- Common duration: 1.081002799581705 μs.
- 480-grid A→B / B→A: 0.999983152623462 / 0.999983152073742.
- 480-grid projected process overlap after local-Z fitting: 0.999991271647941.
- 480-grid conditional phase: 0.002195728776 rad.

These are closed-system projected metrics, not experimental gate fidelity. Stage 10 must not be described as a gate evaluated in the re-quantized shifted-bias basis.

## Stage 11A — local coupler re-quantization

At charge cutoff 12 with five retained local levels, the coupler f01 changes from 5007.500000 MHz to 5075.910813 MHz (Δ +68.410813 MHz). The minimum matched-state overlap probability is 0.9989682 and the minimum retained-subspace singular value is 0.9995692.

The local study covers charge cutoffs 8/10/12 and retained levels 3/4/5. This stage is a local coupler-basis audit, not a full driven-gate result.

## Stage 11B — initial full re-quantized baseline

The complete A–coupler–B product Hamiltonian was rebuilt in the shifted local SQUID eigenbasis using charge cutoff 10 and five retained levels per mode (dimension 125). The unchanged Stage-10 pulse was propagated at 120/240/480 steps per period.

At 480 steps per period:

- A→B: 0.999984205861.
- B→A: 0.999984205140.
- Projected process overlap after local-Z fitting: 0.999991791082.
- Conditional phase: 0.002216577957 rad.
- Second-order Richardson phase: 0.002217189404 rad.

The full complex logical matrices and scalar diagnostics are stored in the tracked files:
- results/stage11b_requantized_gate_matrices.npz;
- results/stage11b_requantized_gate.json;
- docs/STAGE11B_REQUANTIZED_GATE.md.

The adjacent-grid phase-aligned matrix differences are 1.3021273×10⁻⁴ (120→240) and 3.2385586×10⁻⁵ (240→480), consistent with second-order time-discretization convergence.

## Stage 11B — later local pulse retune

A later local search in the re-quantized model selected:

- DC bias: 0.25884589447013934 Φ₀.
- Pump: 987.6171621707836 MHz.
- Flux amplitude: 0.0199946062 Φ₀.
- Requested duration: 1.081140796 μs.
- Raised-cosine ramp: 8 pump periods.

At 480 steps per period and five retained levels per mode (dimension 125), the reported projected process overlap after local-Z fitting is 0.9999999793763371 and the average logical-state fidelity including leakage is 0.9999999803654352. The A→B and B→A transfer probabilities are 0.9999999973549074 and 0.999999992602828. The conditional iSWAP phase is 0.00027739757232 rad. Maximum sampled logical leakage is 3.3115929888805073×10⁻⁴ and maximum sampled coupler-excited population is 6.089711727433299×10⁻³.

At the same point, the six-level 480-grid process overlap is 0.999999967757. The five-/six-level phase-aligned matrix Frobenius difference is 1.8981859×10⁻⁴. The seven-level calculation is only a 120-grid spot check; 240/480 propagation remains open.

**Archive limitation:** the raw FineRobustness and LocalPulseRetune JSON/NPZ files are not tracked in the repository. Their reported SHA-256 fingerprints and the local numerical details are recorded in docs/STAGE11B_LOCAL_RETUNE_NOTE.md. The hashes are not substitutes for the missing files.

## Validation record

- Historical local interpreter: Python 3.14.2.
- Historical local full test suite: 75 passed in 1.33 s.
- Merged Stage 11B PR #5: GitHub Actions run #23 (ID 42976933542) completed successfully on the reviewed PR head.
- The documentation-only branch created for this review requires its own CI run; it is not implied by the earlier PR result.

## Remaining engineering gates

1. Archive the raw local retune JSON/NPZ files, manifests, exact commands and source commit; verify the recorded SHA-256 fingerprints.
2. Complete seven-level 240/480 propagation and matched phase-aligned matrix comparisons.
3. Extend full driven-gate convergence across charge cutoffs and retained-level choices.
4. Turn local deterministic pulse searches into uncertainty budgets and worst-case parameter-tolerance maps.
5. Add measured/target flux-line transfer, delay, distortion, pump phase noise and crosstalk.
6. Add open-system T1/T2, thermal population, relaxation, dephasing, leakage and spectator dynamics.
7. Replace assumed capacitances/Josephson parameters with layout-extracted values and independent EM/circuit-QED review.
8. Resolve the resonant complex-Z link and the graph-wide nine-tone collision warnings before simultaneous operation.
9. Complete fabrication, packaging, readout, calibration and independent hardware review.

## Release decision and boundary

Retain v0.4-rc1 as a closed/internal software and numerical-model checkpoint. It is suitable as a research baseline for continued engineering work. Do not label it fabrication-ready, foundry-ready, experimentally validated, noise-protected or fault tolerant.