# Stage 4 — circuit-derived parametric gate checkpoint

Status: reproducible numerical checkpoint in a closed, three-mode circuit model.
This is not measured hardware performance, a fabrication-ready design, or a
noise-inclusive gate qualification.

## Model and static operating point

- Circuit: capacitively coupled data transmon A — asymmetric SQUID coupler C —
  data transmon B.
- Charge cutoff: 10.
- Local levels retained: 5 per mode.
- DC flux: 0.266843676252319 Phi0.
- Target isolated frequencies: A = 5500 MHz, C = 5007.5 MHz, B = 4515 MHz.
- Extracted local anharmonicities: -277.880373851, -344.279217886,
  -286.427299933 MHz.
- Charge-basis-derived exchange estimates:
  g_AC = 25.562032613 MHz,
  g_CB = 24.802753207 MHz,
  g_AB(direct) = 1.208300190 MHz.
- Residual static ZZ: approximately -0.003286850 MHz.
- Charge-cutoff convergence was checked at 8, 10, 12 and local truncations
  3, 4, 5. All nine configurations were finite, the four tracked dressed
  states were uniquely assigned, and all bare-product overlaps exceeded 99%.

## Drive calibration

- Static dressed A-B transition difference: 987.575679799 MHz.
- Refined dynamic pump candidate: 987.515679799 MHz.
- Flux amplitude: 0.020 Phi0.
- Raised-cosine ramp: 8 pump periods, approximately 0.008101137 us.
- Selected full pulse duration: 1.062565407 us.
- Propagation: fixed DC eigenbasis, exact local coupler exponential at the
  Strang midpoint, symmetric static half-steps.
- Closed-system evolution only.

## Full-pulse transfer

A frequency refinement located the best sampled pump candidate at
987.515679799 MHz. The completed-pulse scan selected 1.062565407 us.

At 240 steps per pump period:
- A-to-B transfer probability: 0.9999784434.
- Final logical leakage, inputs |00>, |10>, |01>, |11>:
  1.6370e-10, 7.8233e-8, 2.1730e-8, 1.2298e-7.
- Maximum leakage during the pulse for those inputs:
  0.0002588, 0.0003309, 0.0003314, 0.0003391.
- Maximum coupler population:
  0.0002713, 0.0051632, 0.0051592, 0.0055895.
- Norm error: 4.2037e-10 in the earlier 240-grid pulse run.

## Four-state gate projection

The four logical inputs |00>, |10>, |01>, |11> were propagated.

At 480 steps per pump period:
- A-to-B transfer: 0.9999783706.
- B-to-A transfer: 0.9999784273.
- Conditional phase: 0.0174726384 rad (about 1.001 degrees).
- Logical-block unitarity defect: 1.5888e-7.
- Norm error: 8.2644e-10.
- Time-dependent Hamiltonian Hermiticity error: 0.

A local-Z phase optimization against iSWAP reported:
- input Z_A: 175.6243166 degrees;
- input Z_B: -144.9682271 degrees;
- output Z_A: -67.5779667 degrees;
- output Z_B: -136.1691689 degrees;
- projected process overlap: 0.9999700882;
- average logical state fidelity including leakage, using the reported
  projected-matrix formula: 0.9999760594.

The phase-corrected matrix from that optimization is recorded in the
companion JSON. These are projected closed-system model metrics, not
experimental gate fidelity.

## Important unresolved numerical issue

The raw logical matrices at 240 and 480 steps had a Frobenius difference
of 0.0468079 (maximum element difference 0.0234900), despite close agreement
in transfer probability and conditional phase. The conditional-phase
difference was only 5.88e-7 rad.

Therefore raw full-matrix phase convergence is NOT closed. A phase-aligned
matrix comparison and a refinement of the local-Z optimization must be done
before treating the process-overlap estimate as final.

## Evidence boundary and remaining work

This model does not include:
- dissipation, T1/T2, thermal bath coupling or quasiparticles;
- measured flux-line transfer function, filtering, delay, distortion or crosstalk;
- calibration uncertainty, flux noise or fabrication disorder;
- a measured capacitance matrix or extracted layout parasitics;
- a graph-wide simultaneous nine-tone drive simulation.

The previously reported graph-wide Floquet screen still has primary and
conditional harmonic/intermodulation warnings. The nine-tone schedule is
not cleared for simultaneous operation.

Next: resolve full logical-matrix phase convergence, optimize amplitude,
frequency and pulse envelope against the full four-state operation, then add
open-system and flux-line models. Only afterward consider a 12-transmon block.

No claim of fabricated or experimentally demonstrated hardware is made.
