# RFT-QPU-Sierpinski — engineering model package v0.4-rc1

**Channel:** closed/internal engineering pre-release candidate. This package is a reproducible numerical and circuit-model baseline, not a fabricated device, foundry package, tape-out release or experimental hardware result.

## Scope

The package contains the level-1 Sierpiński SU(2) graph model and proposed 12-transmon mapping, two-cell projected-interaction study, graph-wide Floquet collision audit, circuit-derived three-mode SQUID-coupler work (Stages 1–4), and the subsequent logical-gate exploration (Stages 5–11B).

## Reproduce the complete test suite

From the repository root:

    python -m pip install -e 'engineering/physical_prototype[test]'
    python -m pytest -q tests engineering/physical_prototype/tests

Historical local pre-release preparation used Python 3.14.2 and recorded 75 passing tests. The merged Stage 11B pull request has a successful GitHub Actions run #23 on its reviewed head. A new documentation branch still needs its own CI run.

## Stage map

| Stage | Work recorded | Evidence boundary |
|---|---|---|
| 1 | Effective three-mode nonlinear coupler stress model | Exploratory reduced model |
| 2 | Static and dynamic parameter sweeps | Declared effective-model assumptions |
| 3 | Three-node charge-basis circuit model | Nominal capacitance/Josephson assumptions; not layout extraction |
| 4 | Full four-state driven-gate checkpoint | Closed-system calculation |
| 5–6 | Full logical matrices, phase alignment and fixed-duration convergence | Retained Stage-5 local coupler basis |
| 7–8 | Harmonic, chirp and envelope exploration | Exploratory controls |
| 9–10 | Shifted-bias pulse refinement and 120/240/480 convergence | Retained Stage-5 local coupler basis |
| 11A | Local SQUID re-quantization at shifted DC flux | Local-basis audit |
| 11B baseline | Full three-mode rebuild and 120/240/480 gate convergence in the re-quantized basis | Tracked nominal closed-system result |
| 11B local retune | Bias/frequency and amplitude/duration local search; five-/six-level check | Reported in README; raw fine-retune JSON/NPZ not tracked |

## Stage 11B evidence distinction

The initial baseline is stored in:
- docs/STAGE11B_REQUANTIZED_GATE.md;
- results/stage11b_requantized_gate.json;
- results/stage11b_requantized_gate_matrices.npz.

The later selected local operating point and its SHA-256 fingerprints are described in docs/STAGE11B_LOCAL_RETUNE_NOTE.md. The original retune matrices and JSON files are not stored here, so the retune must not be described as fully reproducible from the tracked artifacts.

The A–coupler–B model is a three-mode gate subsystem. It is not the full 12-mode level-1 graph Hamiltonian.

## Current physical blockers

1. The resonant complex Z link requires complex diagonal hopping amplitudes; one real static coupler does not implement them.
2. The current graph-wide nine-tone plan has 73 primary and 653 conditional warnings and is not cleared for simultaneous operation.
3. The gate model remains closed-system and omits measured/target T1/T2, thermal population, pump phase noise, flux-line transfer, delay, distortion and crosstalk.
4. Nominal capacitances and Josephson parameters have not been replaced by layout-extracted values.
5. The project has no fabricated or measured device and no independent hardware qualification.

## Output map

- src/rft_qpu/ — graph, Hamiltonian, hardware, control, coupler and gate models.
- scripts/ — reproducible model, sweep and audit runners.
- tests/ — regression tests.
- docs/ — engineering stage reports, validation gates and risk register.
- results/ — JSON/CSV outputs and tracked NPZ archives.
- hardware/level1/ — proposed coefficient and channel tables; not a foundry-ready netlist.

## Before circuit design release

- [ ] Archive the Stage 11B local-retune JSON/NPZ outputs and add exact reproduction configuration.
- [ ] Complete seven-level 240/480 propagation and matched matrix convergence.
- [ ] Extend driven-gate truncation and charge-cutoff checks.
- [ ] Derive worst-case parameter maps and uncertainty budgets.
- [ ] Resolve complex Z-link implementation.
- [ ] Clear multitone pump allocation.
- [ ] Add open-system, thermal, flux-line, phase-noise and crosstalk models.
- [ ] Replace assumed parameters with layout extraction and independent EM/circuit-QED review.

A passing software workflow is Gate 0 model integrity only. It is not physical feasibility, fabrication readiness, tape-out authorization or experimental gate qualification.
