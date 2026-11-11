# Stage 8 — linear chirp and asymmetric envelope exploration

**Status:** new exploratory control-space stage. The pulse candidates are idealized closed-system waveforms, not calibrated flux-line commands or hardware-qualified controls.

## Why this stage

Stage 6 established a stable fundamental-only reference. Stage 7's weak second-harmonic candidate changed the conditional phase slightly but reduced the converged process overlap relative to the Stage-6 baseline. The current Stage-6 waveform therefore remains the baseline; no second-harmonic control is accepted.

Stage 8 examines two control degrees that preserve a single fundamental flux tone:

1. independent raised-cosine input and output ramp durations;
2. a linear frequency chirp across the pulse, integrated continuously in phase.

The instantaneous pump frequency is

`f(t) = f0 + Delta_f * (t/T - 1/2)`,

so `chirp_span_kHz` is the full start-to-end frequency change. The phase is the time integral of this frequency, not an instantaneous-frequency substitution into `cos(2*pi*f*t)`.

The flux waveform is

`Phi(t) = Phi_DC + env_asym(t) * A1 * cos(theta(t))`.

Stage 8 can retain second-harmonic quadratures for controlled follow-up, but the default sweep is fundamental-only.

## Local validation included

- envelope endpoints and plateau are tested;
- the integral of a zero chirp is tested against a constant-frequency carrier;
- the linear chirp derivative is checked at both pulse endpoints;
- overlapping rise/fall ramps are rejected;
- zero-chirp, symmetric-ramp propagation is compared directly against the Stage-5 propagator to catch sign, time-unit, and Strang-splitting drift.

## Preliminary internal 24/40-grid screen

At 24 steps/period, a ±4 kHz symmetric linear chirp with 8/8-period ramps changed process overlap by less than `9e-10` and was effectively neutral. A 6/8-period ramp pair appeared slightly better at 24 steps/period (`Fproc=0.9999802922`) than 8/8 (`0.9999802272`), but at 40 steps/period the ordering reversed: 6/8 gave `0.9999803004`, while 8/8 gave `0.9999808983`. This is not a stable improvement; equal-duration higher-resolution finalist checks are required.

## Screening protocol

The coarse sweep records the complete 4×4 logical matrix, process overlap after numerical local-Z correction, bidirectional transfer, conditional phase, final logical leakage, sampled transient leakage, and sampled coupler population. It is checkpointed after each candidate and supports resume. The sweep thresholds are numerical filters only, not hardware acceptance limits.

A finalist must then be rerun on at least 120/240/480 steps per nominal pump period with one common physical duration across all grids. Full matrices must be compared both raw and after independently fitted input/output local-Z frame alignment. The conditional-phase invariant remains an independent nonlocal diagnostic and must not be hidden by local-Z fitting.

## Evidence boundary

No measured flux-line bandwidth, transfer, delay, distortion or crosstalk is included. The capacitance/Josephson values remain nominal assumptions. There is no dissipation, T1/T2, thermal population, quasiparticle model, calibration uncertainty or fabrication disorder. A candidate that wins this idealized screen is not a physical pre-release design.
