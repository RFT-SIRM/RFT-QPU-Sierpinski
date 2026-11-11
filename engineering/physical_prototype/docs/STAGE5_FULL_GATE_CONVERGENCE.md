# Stage 5 — full logical-gate convergence audit

## Purpose

Stage 4 recorded high process overlap after local-Z correction, but the raw
logical matrices at 240 and 480 steps per pump period differed substantially.
Stage 5 reconstructs the fixed-DC-basis Strang propagator from the committed
Stage-3 charge-basis model and stores the unrounded complex 4x4 matrices.

## Reconstructed calculation

- Charge cutoff 10; five local levels per mode; product dimension 125.
- Three-node A–asymmetric-SQUID-C–B circuit from `circuit_quantization.py`.
- DC coupler flux is solved against the declared 5007.5 MHz local target.
- Logical dressed states are assigned by bare-product overlap; indices are
  expected to be `[0, 3, 1, 7]`.
- Fixed DC local eigenbasis; static Hamiltonian half-steps and exact projected
  5x5 flux-dependent coupler exponential at the Strang midpoint.
- Raised-cosine ramps of eight pump periods.

## Command

From the repository root:

```bash
PYTHONPATH=engineering/physical_prototype/src \
  /tmp/rft-qpu-clean/bin/python \
  engineering/physical_prototype/scripts/run_stage5_gate_convergence.py \
  --steps-per-period 120 240 480
```

Use `--steps-per-period 120 240 480 960` for the extended run. The 960-grid
run is more computationally expensive. All full matrices are saved without
rounding in an NPZ archive; JSON and Markdown summaries are written alongside.

## Phase conventions

The iSWAP nonlocal invariant is

`wrap(arg(U00) + arg(U33) - arg(U21) - arg(U12) + pi)`.

It is invariant under independent input/output local Z rotations and a global
phase. Full-matrix convergence is assessed by fitting those phase freedoms
between grids and then comparing every complex matrix element. Transfer
probabilities alone are not used as proof of matrix convergence.

## Evidence boundary

This is closed-system numerical simulation using a nominal assumed circuit.
It is not a measured gate fidelity or hardware qualification. Dissipation,
T1/T2, thermal population, flux-line transfer/crosstalk, calibration error,
fabrication disorder, layout-extracted capacitances, and spectator channels
remain outside the model. Sampled maximum leakage/coupler population depends
on the sampling stride; it should be checked at higher tracking density when
qualifying a final pulse.

## Coarse three-parameter sweep

The companion `run_stage5_full_gate_sweep.py` scans frequency, flux amplitude
and pulse duration against the full 4x4 logical operation. Its default 27-point
box is a coarse search around the improved frequency candidate; the runner
ranks feasible points by process overlap after local-Z optimization and
reports worst sampled values across the box. Do not treat the coarse grid as a
final optimum. Every selected candidate must be rerun at 120/240/480 or finer
and checked with measured flux-line calibration before hardware decisions.
