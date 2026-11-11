# RFT-QPU-Sierpinski — closed engineering pre-release candidate v0.4-rc1

**Release channel:** closed/internal engineering pre-release candidate. This is a reproducible numerical and circuit-model checkpoint, not a fabricated device, foundry package, tape-out release, or experimental hardware result.

## Scope

This package includes the level-1 Sierpiński SU(2) graph model and proposed 12-transmon mapping, the two-cell projected-interaction study, the graph-wide Floquet collision audit, the circuit-derived three-mode SQUID coupler work (Stages 1–4), and the subsequent full logical-gate exploration (Stages 5–11B baseline).

## Reproduce the complete test suite

From the repository root:

```bash
python -m pip install -e 'engineering/physical_prototype[test]'
python -m pytest -q tests engineering/physical_prototype/tests
```

Local pre-release preparation used Python 3.14.2 and recorded **75 passed in 1.33s**. The release-candidate PR must also pass the repository's GitHub Actions workflow (Python 3.11).

## Stage map and evidence

| Stage | Contents | Status |
|---|---|---|
| 1 | Effective three-mode nonlinear coupler stress model | Recorded; exploratory |
| 2 | Static and dynamic parameter sweeps | Recorded; assumed effective-model parameters |
| 3 | Three-node charge-basis circuit model | Recorded; declared capacitance/Josephson assumptions |
| 4 | Full four-state driven-gate checkpoint | Recorded; closed-system model |
| 5–6 | Full logical matrices, phase alignment, fixed-duration convergence | Recorded; retained Stage-5 coupler basis |
| 7–8 | Harmonic/chirp/envelope control exploration | Recorded; no coarse-grid-only candidate promoted |
| 9–10 | Shifted-bias candidate refinement and 120/240/480 convergence | Recorded; retained Stage-5 fixed local coupler basis |
| 11A | Local coupler re-quantization at shifted DC flux | Recorded; local audit only |
| 11B | Full three-mode rebuild and four-state gate rerun in the re-quantized basis on 120/240/480 grids | Initial nominal baseline complete; robust retuning and truncation convergence open |

## Current Stage 10 reference point

- Bias: `0.259343676252 Φ₀`.
- Pump: `987.609221499 MHz` (`-64.000 kHz` relative to shifted static detuning).
- Flux amplitude: `0.020000 Φ₀`.
- Pulse duration: `1.081002799582 μs`; raised-cosine ramp `8.0` periods.
- At 480 steps/period: A→B `0.999983152623`, B→A `0.999983152074`, projected process overlap after local-Z fitting `0.999991271648`, conditional phase `0.0021957288 rad`.

These are closed-system projected calculations, not measured gate fidelity.

## Important model boundary

Stages 5–10 use the Stage-5 fixed-DC local coupler basis. Stage 11A independently diagonalizes the local SQUID at the shifted bias; the first Stage 11B baseline then rebuilds the full three-mode Hamiltonian and driven four-state gate in that new local basis, with 120/240/480 time-grid convergence. Stage 10 remains the fixed-basis reference and must not be mislabeled as the re-quantized gate. Robust retuning and full-gate truncation convergence remain open.

## Output layout

- `src/rft_qpu/` — model implementations for Stages 5–11A.
- `scripts/` — reproducible sweep, convergence and audit runners.
- `tests/` — regression tests.
- `docs/` — stage reports and release/validation boundaries.
- `results/` — JSON/CSV summaries and NPZ complex matrices/checkpoints.
- `hardware/level1/` — proposed level-1 coefficient/channel tables; not a foundry netlist.

## Open requirements before physical design release

1. Robustly re-optimize bias, frequency, amplitude and duration in the re-quantized model; build parameter maps and uncertainty budgets.
2. Check full-gate convergence against charge cutoff and retained-level choices.
3. Flux-line bandwidth/delay/distortion/phase-noise/crosstalk characterization.
4. Open-system T1/T2, thermal, leakage and spectator modeling.
5. Layout-extracted capacitances/parasitics and independent EM/circuit-QED review.
6. Resolution of graph-wide pump-collision warnings and simultaneous-tone feasibility.
7. Fabrication, packaging, readout, calibration and independent hardware qualification.

The existing graph-wide screen reports 73 primary pump/sideband warnings within 10 MHz and 653 conditional harmonic/intermodulation warnings. Simultaneous nine-tone operation is not cleared.

**The package is suitable as a closed, reproducible engineering research baseline. It is not suitable as a fabrication-ready or experimentally qualified design.**
