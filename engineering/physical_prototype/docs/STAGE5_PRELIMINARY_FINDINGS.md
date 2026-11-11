# Stage 5 — preliminary internal numerical findings

These values were independently reconstructed from the committed circuit model
and the Stage-4 pulse convention. The package runner is supplied to reproduce
them locally and to save the full matrices without rounding.

## 1. Full-matrix phase convergence at the Stage-4 pulse

Pulse: 987.5156797993163 MHz, 0.020 Phi0, 1.0625654067723154 us,
eight-period raised-cosine ramps.

| Steps per period | A→B transfer | iSWAP process overlap after local Z | iSWAP phase invariant (rad) |
|---:|---:|---:|---:|
| 120 | 0.999978736975 | 0.999970281077 | 0.017469692196 |
| 240 | 0.999978443247 | 0.999970126573 | 0.017472050408 |
| 480 | 0.999978369903 | 0.999970087677 | 0.017472637978 |

Full complex matrix comparison:

| Grid pair | Raw Frobenius difference | After independent input/output Z and global phase fit |
|---|---:|---:|
| 120 → 240 | 0.1879774338 | 4.47498258e-5 |
| 240 → 480 | 0.04680791294 | 1.11200014e-5 |

The raw difference decreases by approximately 4x when the step size is halved,
and the phase-aligned residual also decreases by approximately 4x. This is
consistent with second-order Strang splitting. The 240→480 conditional-phase
difference is 5.87570646e-7 rad. Richardson estimates from the three grids are:

- iSWAP phase invariant: 0.017472833835 rad;
- process overlap after local Z: 0.999970074712;
- average logical-state fidelity including leakage: 0.999976048440.

Thus the former 0.0468 raw matrix discrepancy is overwhelmingly local/global
phase gauge. Full matrix convergence is not literally zero at finite step size,
but the phase-aligned residual is about 1.1e-5 on the 240→480 pair and shows the
expected second-order trend.

## 2. Better sampled frequency point for the full operation

A local frequency refinement around Stage 4 found a better sampled candidate:

- pump frequency: 987.5136797993163 MHz;
- flux amplitude: 0.020 Phi0;
- requested duration: 1.0625654067723154 us;
- actual duration is snapped to the nearest complete time step on each grid.

| Steps per period | A→B transfer | Process overlap after local Z | iSWAP phase invariant (rad) |
|---:|---:|---:|---:|
| 120 | 0.999999766376 | 0.999980795611 | 0.017469689798 |
| 240 | 0.999999742462 | 0.999980776137 | 0.017471978363 |
| 480 | 0.999999736943 | 0.999980771258 | 0.017472600751 |

At 480 steps per period, B→A transfer is 0.999999793177, final maximum
logical leakage over the four inputs is 1.22545e-7, the logical unitarity defect
is 1.59744e-7, and norm error is 2.57086e-10.

Compared with the Stage-4 480-grid baseline, the sampled candidate improves
A→B transfer from 0.999978370609 to 0.999999736943 and process overlap from
0.999970087677 to 0.999980771258. This is a local sampled improvement, not a
global optimum.

## 3. Local robustness observations

Around the new frequency point, a 120-step-per-period scan found:

- frequency ±0.5 kHz changes process overlap by roughly 1e-6 or less;
- amplitude ±0.0001 Phi0 (±0.5%) reduces process overlap to approximately
  0.9999501–0.9999507, versus 0.9999808 nominal.

This nominal point is materially more sensitive to flux-amplitude calibration
than to a ±0.5 kHz pump-frequency error in this local scan. The amplitude
sensitivity needs a denser scan and a real flux-line calibration model before
setting hardware tolerances.

## 4. Unresolved nonlocal phase

The iSWAP-invariant phase remains approximately 0.0174726 rad, or about 1.001°.
Local Z rotations cannot change this invariant. Frequency refinement improved
transfer but did not remove the nonlocal phase. A one-tone pulse with only
frequency, amplitude and duration may not have enough independent control to
remove both exchange-angle error and conditional phase. Further work should add
at least one physical pulse-shape/compensation degree of freedom and optimize it
against the full four-state operator.

## 5. Remaining evidence boundary

All metrics are closed-system numerical results with assumed capacitances,
Josephson energy and SQUID asymmetry. They are not measured gate fidelity or a
hardware-release signoff. T1/T2, thermal occupation, quasiparticles, flux-line
transfer/distortion/crosstalk, calibration uncertainty, fabrication disorder,
layout-extracted circuit parameters and spectator channels remain outstanding.
