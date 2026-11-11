# Stage 11B — initial full gate in the re-quantized coupler basis

Date: 2026-11-11  
Status: initial nominal full-model rebuild and 120/240/480 gate convergence completed; robust retuning and physical qualification remain open.

## What was rebuilt

The Stage-10 shifted operating point was retained, but the local SQUID coupler was explicitly diagonalized at the shifted DC flux 0.25934367625232047 Phi_0. The A and B data-transmon local bases were reconstructed from the same Stage-3 circuit assumptions. The full A–coupler–B product Hamiltonian was then assembled again, including all three capacitive number-number interactions, in the new local product basis.

Nominal truncation: charge cutoff 10 and five retained eigenlevels per mode, giving a 125-dimensional product Hilbert space. Four dressed logical states were independently re-tracked from the bare ground, A-excited, B-excited, and A+B-excited product states. The minimum corresponding bare-product overlap is 0.9942737558.

The time-dependent SQUID Hamiltonian was projected using the newly diagonalized coupler's charge-basis eigenvectors. The drive term is referenced to the new DC bias and vanishes at that bias. This is a genuine rebuild in the re-quantized local basis; it is not a basis relabeling of the old Stage-10 matrices.

## Rebuilt static point

| Quantity | Result |
|---|---:|
| A local f01 | 5500.000000 MHz |
| Coupler local f01 | 5075.910813 MHz |
| B local f01 | 4515.000000 MHz |
| Dressed A transition | 5501.502906 MHz |
| Dressed B transition | 4513.829671 MHz |
| Dressed A–B detuning | 987.673235016 MHz |
| Static ZZ | -0.000767706456 MHz |
| Stage-10 pump | 987.609221499 MHz |
| Pump offset from rebuilt detuning | -64.013517 kHz |

## Full four-state gate calculation

The Stage-10 pulse was applied unchanged to the rebuilt model: bias 0.25934367625232047 Phi_0, amplitude 0.020000 Phi_0, frequency 987.609221499 MHz, requested duration 1.081 microseconds, common represented duration 1.081002799582 microseconds, and an eight-period raised-cosine ramp.

| Steps per period | Time steps | A→B | B→A | Process overlap after local-Z fit | Conditional phase |
|---:|---:|---:|---:|---:|---:|
| 120 | 128113 | 0.999985106193 | 0.999985105601 | 0.999992244079 | 0.002207380856 rad |
| 240 | 256226 | 0.999984387013 | 0.999984386317 | 0.999991882154 | 0.002214743614 rad |
| 480 | 512452 | 0.999984205861 | 0.999984205140 | 0.999991791082 | 0.002216577957 rad |

Second-order Richardson estimate of the conditional phase: 0.002217189404 rad.

Full 4x4 complex logical matrices and local-Z-corrected matrices are saved in results/stage11b_requantized_gate_matrices.npz; scalar diagnostics are in the companion JSON. Adjacent-grid phase-aligned Frobenius differences are 1.3021273e-4 (120→240) and 3.2385586e-5 (240→480), a factor of approximately four reduction, consistent with second-order time-discretization convergence.

At 480 steps per period, the maximum sampled norm drift is 9.37e-10 and the projected logical unitarity defect is approximately 1.81e-8. The largest sampled coupler-excited population among the four logical inputs is 0.006032513; the largest sampled logical leakage is 0.000330154.

## Numerical method and reproducibility

The static half-step / local 5x5 coupler drive / static half-step symmetric Strang split matches the structure of Stage 5. The 120- and 240-grid results used scipy.linalg.expm for the 5x5 drive propagator. To complete the 480-grid run within the execution limit, its small anti-Hermitian drive exponent was evaluated with a sixth-order Taylor matrix polynomial. Across 301 sampled pulse times the maximum absolute difference from scipy.linalg.expm was 1.12e-16; a separate 2,000-step state comparison differed by 3.75e-15. The committed runner uses the existing scipy.linalg.expm path.

Reproduce from the repository root after installing the prototype package:

    python -m pip install -e 'engineering/physical_prototype[test]'
    python engineering/physical_prototype/scripts/run_stage11b_requantized_gate.py

## Boundaries and remaining work

This completes the first nominal full-model rebuild and a 120/240/480 time-grid convergence check. It does not complete all of Stage 11B or hardware validation:

1. Re-optimize bias, frequency, amplitude and duration in the re-quantized model; run robust parameter sweeps and uncertainty maps.
2. Check convergence of the full three-mode driven gate against charge cutoff and retained-level choices, not only the 10/5 baseline.
3. Add measured/target flux-line transfer functions, distortion, delay, pump phase noise and crosstalk.
4. Add open-system T1/T2, thermal population, relaxation, dephasing and spectator channels.
5. Replace nominal capacitances/Josephson parameters with layout-extracted values and independent EM/circuit-QED review.
6. Resolve the graph-wide nine-tone collision warnings before simultaneous operation or tape-out.
7. Obtain fabrication, packaging, readout, calibration and independent hardware review.

These are closed-system projected numerical results, not measured gate fidelity. The hardware remains pre-experimental and is not fabrication- or tape-out-ready.
