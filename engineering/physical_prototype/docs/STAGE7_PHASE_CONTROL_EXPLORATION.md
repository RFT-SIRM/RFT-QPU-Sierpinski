# Stage 7 — conditional-phase control exploration

**Status:** exploratory closed-system numerical study. No hardware-ready or
experimentally measured gate claim is made.

## Stage-6 convergence baseline

The user-run fixed-duration Stage-6 calculation used the same physical pulse
duration, `1.0625675587737073 us`, on all three grids. It reported:

| Steps per pump period | A→B transfer | Projected process overlap | Conditional phase (rad) |
|---:|---:|---:|---:|
| 120 | 0.999999766284 | 0.999980795546 | 0.01746968975 |
| 240 | 0.999999743124 | 0.999980776281 | 0.01747204798 |
| 480 | 0.999999736342 | 0.999980770807 | 0.01747263555 |

The process-overlap change from 120 to 480 is `2.47e-8`; the conditional
phase approaches `0.01747264 rad` (about one degree). This confirms numerical
convergence of the scalar gate metrics at the tested resolution, but the
nonlocal phase remains a real gate error relative to ideal iSWAP.

## Attempt A — static-ZZ compensation excursion (rejected)

A full 125-dimensional static diagonalization in the fixed-DC basis found a
positive static conditional ZZ near a temporary flux bias of `0.250 Phi0`:

- `ZZ_static = +0.03561535 MHz`;
- a naive phase-area estimate for cancellation suggested a hold of about
  `78.067 ns`.

The full dynamic model was then used for a gate followed by a raised-cosine
flux excursion to `0.250 Phi0`, a hold, and a return ramp. The phase did not
follow the static hold-only estimate because the ramps and state mixing also
contribute. With a 25 ns ramp and the naive 78.067 ns hold:

- conditional phase after compensation: `-0.00228894 rad` (overshoot);
- projected process overlap: `0.99980985`, below the uncorrected Stage-6
  baseline near `0.99998077`;
- maximum final logical leakage: `7.59e-4`;
- sampled transient logical leakage: `2.90e-3`;
- sampled coupler excited probability: `1.02e-2`.

A 10 ns ramp was worse (`Fproc = 0.99962885`, transient leakage
`3.69e-3`). This simple idle-ZZ excursion is **not accepted**. Any future
compensation experiment must optimize the complete ramp/hold/return waveform
using the full propagator, not only the static ZZ phase-area estimate.

## Attempt B — second-harmonic flux shaping

The tested waveform was

`Phi(t) = Phi_DC + env(t) * [A1 cos(w t) + A2c cos(2 w t) + A2s sin(2 w t)]`.

A coarse 3×3 quadrature screen at 24 steps per period completed 9/9
candidates, all passing only the preliminary numerical screen. A separate
40-step-per-period comparison tested the baseline and two cosine amplitudes:

| A2c (Phi0) | A2s (Phi0) | A→B transfer | Process overlap | Conditional phase (rad) |
|---:|---:|---:|---:|---:|
| 0 | 0 | 0.999999838499 | 0.999980898349 | 0.01744372405 |
| +0.0002 | 0 | 0.999999860810 | 0.999980916066 | 0.01744073493 |
| +0.0002 | -0.0002 | 0.999999860022 | 0.999980915585 | 0.01744078199 |
| +0.0020 | 0 | 0.999958760292 | 0.999960414050 | 0.01741807030 |

The very small second harmonic changes process overlap by only
`+1.77e-8` and conditional phase by `-2.99e-6 rad` at this coarse grid. The
nearby quadrature candidate `(A2c,A2s)=(+0.0002,-0.0002) Phi0` gives almost
the same result (`Fproc=0.999980915585`, phase `0.01744078199 rad`). The
larger `0.002 Phi0` component reduces the phase by `2.57e-5 rad`, but lowers
process overlap by about `2.05e-5` and transfer to about `99.9959%`.

The small apparent improvement is comparable to the temporal-discretization
uncertainty and is **not yet a design improvement**. The candidate must be
re-run on common-duration 120/240/480 grids before any selection. The real
flux-line bandwidth and ability to deliver a calibrated 2w component are
also unknown.

## Current decision

1. Keep the Stage-6 fundamental-only pulse as the control baseline.
2. Do not use the static-ZZ excursion in its current form.
3. Do not promote a second-harmonic candidate based on the 24/40-grid screen.
4. Run the Stage-7 common-duration convergence runner on the weak 2w candidate
   and compare its phase-aligned full matrices with the Stage-6 baseline.
5. If no statistically meaningful gain survives refinement, stop tuning 2w
   and move to a more expressive smooth envelope / phase-modulated pulse
   optimization with explicit flux-line bandwidth constraints.

## Evidence boundary

The model still uses nominal assumed capacitances, Josephson energies and
SQUID asymmetry. It omits measured flux-line transfer, filtering, latency,
nonlinearity, crosstalk, T1/T2, thermal population, fabrication variation and
layout-extracted parasitics. Numerical success here is not hardware release
signoff or permission to fabricate from the assumed circuit values.
