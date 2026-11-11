# Stage 6 — robustness map and fixed-duration convergence

## Purpose

Stage 6 tightens two numerical controls that matter before a pre-release
engineering decision:

1. Every convergence grid must simulate the *same physical pulse duration*.
   The earlier Stage-5 runner rounded the requested duration separately on
   each grid. Stage 6 snaps once to the common time lattice defined by the
   GCD of the requested steps-per-period values.
2. A parameter sweep must report no feasible candidate when none passes the
   screening constraints. It must not silently select the best infeasible
   point and label it feasible.

Local-Z phases are also written in the canonical interval `(-pi, pi]` so
that reports do not show equivalent phases shifted by hundreds of full turns.
This does not change the corrected matrix or its fidelity metrics.

## Reconstructed 3 x 3 x 3 screening result

An internal coarse sweep used the Stage-5 circuit-derived propagator at
40 steps per pump period, with:

- pump offsets: -1, 0, +1 kHz around 987.5136797993163 MHz;
- flux amplitudes: 0.0199, 0.0200, 0.0201 Phi0;
- duration offsets: -1, 0, +1 coarse integration step;
- eight-period raised-cosine ramps.

All 27 candidates passed the *preliminary numerical screening constraints*
(transfer in each direction >= 0.999, final logical leakage <= 1e-3, sampled
coupler excited probability <= 0.02). These are not hardware acceptance limits.

| Coarse-screen metric | Result |
|---|---:|
| Candidate count | 27 / 27 |
| Minimum process overlap in sampled box | 0.9999424704 |
| Minimum A-to-B transfer | 0.9999231759 |
| Maximum final logical leakage | 4.5966e-8 |
| Maximum sampled coupler excited probability | 0.00563574 |

Best sampled coarse candidate:

- frequency: 987.513679799 MHz;
- flux amplitude: 0.0200 Phi0;
- duration: 1.062592874879 us (40-step grid snapped duration);
- A-to-B transfer: 0.9999998620;
- B-to-A transfer: 0.9999998819;
- process overlap after local-Z fit: 0.9999809091;
- conditional phase invariant: 0.0174441421 rad.

The improvement over the central coarse point is only about 1.1e-8 in process
overlap. It is below what should be treated as a meaningful design improvement
until the point is reconfirmed at higher temporal resolution and at a shared
physical duration. Do not replace the Stage-5 nominal candidate on this coarse
result alone.

The flux-amplitude sensitivity dominates the small frequency variation in
this box. At the centre duration and frequency, the coarse process overlap is
about 0.99994768 at 0.0199 Phi0, 0.99998090 at 0.0200 Phi0, and 0.99995342 at
0.0201 Phi0. The frequency offsets of +/-1 kHz around the centre amplitude
reduce process overlap by about 2.2e-6 relative to the centre point.

## Correct shared-duration calculation

For a frequency `f` in MHz and a set of grids `N_i` steps per pump period,
let `g = gcd(N_i)`. Stage 6 chooses the nearest duration on the shared lattice
`1 / (f*g)` microseconds, then derives the exact integer step count on every
requested grid. For [120, 240, 480], the selected common-duration counts are
`n`, `2n`, and `4n`; all grids therefore evolve for identical physical time.

The corrected convergence runner saves raw complex 4x4 matrices and
independently phase-aligned matrix comparisons. The conditional phase
invariant is kept separate because local Z phases cannot alter it.


## Why the common-duration runner is required

The just-completed Stage-5 local run reported the following requested-duration
case at 987.5136797993163 MHz. The propagator rounded the duration separately
on each grid:

| Grid | Actual pulse duration (us) |
|---:|---:|
| 120 | 1.0625675587737073 |
| 240 | 1.0625633394228750 |
| 480 | 1.0625654490982912 |

The spread is only a few picoseconds, but it means the old grid comparison
changed both integration step and pulse duration. The Stage-6 shared-duration
runner snaps once to 1.0625675587737073 us for this request, then uses step
counts 125916, 251832 and 503664 on 120/240/480 respectively. This isolates
the integration-step refinement more cleanly.

## Evidence boundary

Everything here is a closed-system calculation using declared nominal
capacitances, Josephson energy and SQUID asymmetry. No T1/T2, thermal bath,
flux-line transfer function, crosstalk, fabrication disorder, calibration
uncertainty or layout-extracted circuit data is included. This is not a
hardware-release signoff.
