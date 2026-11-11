# Stage 9 — static SQUID bias offset and full-gate retuning

**Status:** preliminary control-space candidate; no hardware qualification or pre-release acceptance.

## Motivation

Stage 7's weak second harmonic did not improve the converged full-gate process overlap. Stage 8's linear chirp was effectively neutral at the tested coarse temporal grid, and an asymmetric 6/8-period ramp traded a slightly lower conditional phase for a worse process overlap at 40 steps/period. The Stage-6 fundamental-only operating point therefore remained the stable reference.

A separate static diagonalization showed that a modest negative shift of the SQUID DC bias changes the dressed static ZZ while preserving unique tracking of the four logical dressed states. The pump frequency and pulse duration must be retuned at the shifted point; simply reusing the baseline pulse is not valid.

## Model implementation

`build_bias_shifted_model` adds the SQUID coupler's flux-dependent Hamiltonian offset to the Stage-5 full 125-dimensional Hamiltonian in the retained fixed local 5-level coupler basis, rediagonalizes it, and re-tracks the logical states by maximum overlap with their bare product states. The time-dependent drive is then re-zeroed about the new bias, avoiding double-counting the static offset.

The local coupler basis is **not re-quantized at each bias**. This is a controlled projection into the existing five-level basis and must be checked against a later independently re-quantized model before hardware use.

## Preliminary 40-step/period candidate

At offset `-0.0075 Phi0`:

- absolute DC flux: approximately `0.2593436763 Phi0`;
- static A-B dressed detuning: `987.673221499 MHz`;
- static ZZ: `-0.000766700 MHz`;
- minimum bare overlap among the four tracked logical states: `0.994244823`.

A preliminary 40-step/period point used a pump `63 kHz` below the shifted dressed A-B detuning, amplitude `0.020 Phi0`, ramp 8 periods, and duration `1.081 us`:

- A-to-B transfer: `0.9999740803`;
- B-to-A transfer: `0.9999740805`;
- process overlap after local Z: `0.9999867581`;
- conditional phase invariant: `+0.00210689 rad` (about `0.121°`);
- maximum final logical leakage: `1.86e-8`;
- sampled maximum coupler excited probability: approximately `0.005918`.

For comparison, the same 40-step internal calculation at the Stage-6 baseline gave process overlap `0.9999808984`, conditional phase `0.01744372 rad`, and transfer above `0.9999998`. This is promising at 40 steps/period, but it is not yet a like-for-like converged comparison. A common-duration 120/240 run was then completed for the same candidate (`T=1.081001705017489 us`):

| Grid | A→B | Process overlap | Conditional phase (rad) |
|---:|---:|---:|---:|
| 120 | 0.999962532445 | 0.999980964563 | 0.00218670266 |
| 240 | 0.999961399918 | 0.999980396068 | 0.00219394345 |

The two-grid second-order provisional extrapolations are `Fproc≈0.999980206569` and `phi≈0.00219635705 rad`. These are not final estimates because the 480 grid has not yet completed. Notably, the 240-grid process overlap is slightly below the Stage-6 baseline (`0.999980776281`) while the conditional phase is much smaller. The shifted-bias candidate therefore trades some transfer/process performance for reduced nonlocal phase; it is **not yet accepted**. The included checkpoint contains the full 120/240 complex matrices so the 480 grid can resume without repeating them.

## Required next checks

1. Sweep bias offset, pump detuning relative to the newly computed dressed transition, and duration together.
2. Select finalists on a common temporal grid; do not choose by phase alone.
3. Re-run finalists with the same physical pulse duration at 120/240/480 steps per period and compare full 4×4 matrices before and after independently fitted local-Z frame alignment.
4. Check sensitivity to bias error, pump-frequency error and amplitude error around the selected shifted operating point.
5. Re-quantize the local coupler basis at the shifted DC bias and compare the result with the fixed-basis projection.
6. Add measured flux-line response and open-system errors before any hardware design freeze.

## Evidence boundary

The capacitance and Josephson parameters remain declared assumptions, not layout-extracted values. The model is closed-system and omits T1/T2, thermal population, quasiparticles, flux-line transfer, bandwidth, distortion, latency, crosstalk, calibration errors and fabrication disorder. It is not a physical pre-release design or fabrication authorization.
