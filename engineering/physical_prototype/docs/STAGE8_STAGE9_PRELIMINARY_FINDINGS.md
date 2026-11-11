# Stage 8–9 preliminary findings

Status: exploratory closed-system control optimization. These findings do not constitute hardware qualification or a physical pre-release design.

## Stage 8 — chirp and asymmetric ramp

The weak second-harmonic candidate from Stage 7 did not outperform Stage 6 after common-duration 120/240/480 convergence. Stage 8 therefore screened two other controls while retaining the fundamental-only waveform:

- a linear carrier chirp, with the instantaneous pump frequency swept symmetrically around `f0`;
- independently chosen raised-cosine input and output ramp lengths.

At 24 steps/period, changing the chirp by ±4 kHz while keeping 8/8-period ramps changed process overlap by less than `9e-10`; it is effectively neutral at that resolution. A 6/8-period ramp seemed slightly better than 8/8 at 24 steps/period, but the ordering reversed at 40 steps/period. At 40 steps/period:

| Ramp in/out | A→B | B→A | Process overlap | Conditional phase (rad) |
|---|---:|---:|---:|---:|
| 6/8 | 0.999998634851 | 0.999998684627 | 0.999980300371 | 0.01743820003 |
| 8/8 | 0.999999838499 | 0.999999857887 | 0.999980898349 | 0.01744372405 |

The 6/8 ramp reduced conditional phase by about `5.52e-6 rad`, but lowered process overlap by about `5.98e-7` and transfer by about `1.2e-6`. This is not accepted as a better pulse. Retain Stage-6 8/8 ramps as the reference.

## Stage 9 — DC bias shift

A bias shift changes static ZZ and the dressed A–B detuning. The model therefore adds the flux-dependent SQUID Hamiltonian offset to the retained fixed 5-level coupler basis, rediagonalizes the complete 125-dimensional static Hamiltonian, re-tracks the logical dressed states, and re-zeroes the time-dependent drive about the shifted bias. This is not a fresh local charge-basis quantization at every bias; the fixed-basis truncation is a remaining model limitation.

At bias offset `-0.0075 Phi0`:

- absolute DC flux: `0.259343676252321 Phi0`;
- dressed A–B detuning: `987.673221499198 MHz`;
- static ZZ: `-0.000766699942 MHz`;
- minimum tracked bare overlap: `0.994244823`.

The 40-step/period preliminary pulse candidate used a pump 63 kHz below the shifted dressed A–B detuning, amplitude `0.020 Phi0`, duration `1.081 us`, and 8-period ramps:

- process overlap after local Z: `0.999986758065`;
- A→B: `0.999974080305`;
- B→A: `0.999974080540`;
- conditional phase: `+0.00210689215 rad` (about `0.121°`);
- maximum final logical leakage: `1.86e-8`;
- sampled maximum coupler excited probability: `0.00592564`.

The common-duration high-resolution check has so far completed 120 and 240 steps/period at `T=1.081001705017489 us`:

| Grid | A→B | Process overlap | Conditional phase (rad) |
|---:|---:|---:|---:|
| 120 | 0.999962532445 | 0.999980964563 | 0.00218670266 |
| 240 | 0.999961399918 | 0.999980396068 | 0.00219394345 |

The 480 grid remains pending. The provisional two-grid second-order extrapolations are `Fproc≈0.999980206569` and `phi≈0.00219635705 rad`; do not treat them as final without the third grid.

The Stage-9 candidate has a much smaller conditional phase than Stage 6, but at 240 steps its process overlap is lower than the Stage-6 value (`0.999980776281`) and its transfer is also lower. It is a trade-off, not yet an accepted improvement. The archive contains the two completed complex matrices and resumable checkpoint for the remaining 480 grid.

## Required next work

1. Resume and complete the 480-grid calculation using the supplied checkpoint.
2. Compare the full complex matrices after independent input/output local-Z frame alignment; retain the nonlocal conditional-phase invariant separately.
3. Refine pump offset and duration around the Stage-9 point at a common high-resolution grid. Amplitude sensitivity must also be mapped.
4. Re-quantize the local coupler basis at the shifted bias and compare against the fixed-basis projection.
5. Add measured flux-line transfer, bandwidth, delay, distortion and crosstalk, then T1/T2, thermal population and fabrication variations.

The nominal capacitances and Josephson parameters remain assumptions rather than layout-extracted values. No hardware readiness, fabrication approval, or experimental gate fidelity is claimed.
